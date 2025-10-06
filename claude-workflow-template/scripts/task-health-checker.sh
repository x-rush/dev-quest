#!/bin/bash
# 任务健康检查器 - Task Health Checker
# 专门用于检测Claude Code任务执行状态，识别需要干预的情况

# 配置参数
HEALTH_CHECK_INTERVAL=60            # 健康检查间隔(秒)
TASK_TIMEOUT_THRESHOLD=1800         # 任务超时阈值(30分钟)
API_ERROR_THRESHOLD=5               # API错误阈值
NETWORK_ERROR_THRESHOLD=3          # 网络错误阈值
STATUS_FILE="EXECUTION_STATUS.json" # 执行状态文件
HEALTH_LOG_FILE="HEALTH_CHECK_LOG.md"  # 健康检查日志
ALERT_LOG_FILE="ALERT_LOG.md"       # 告警日志

# 颜色输出
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_health() {
    echo -e "${BLUE}[HEALTH]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$HEALTH_LOG_FILE"
}

log_alert() {
    echo -e "${RED}[ALERT]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$ALERT_LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$HEALTH_LOG_FILE"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$HEALTH_LOG_FILE"
}

# 检查文件是否存在
check_file() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        log_alert "文件不存在: $file"
        return 1
    fi
    return 0
}

# 获取JSON字段的值
get_json_value() {
    local file="$1"
    local key="$2"
    local default="$3"

    if [[ ! -f "$file" ]]; then
        echo "$default"
        return 1
    fi

    jq -r "$key // \"$default\"" "$file" 2>/dev/null
}

# 检查任务执行时间
check_task_duration() {
    local task_id="$1"
    local current_time=$(date +%s)

    # 从状态文件获取任务开始时间
    local start_time=$(get_json_value "$STATUS_FILE" ".tasks.\"$task_id\".start_time" "0")
    if [[ "$start_time" == "0" ]]; then
        return 1
    fi

    # 转换时间戳
    local start_timestamp=$(date -d "$start_time" +%s 2>/dev/null || echo 0)
    local duration=$((current_time - start_timestamp))

    echo "$duration"
}

# 检查任务是否超时
check_task_timeout() {
    local task_id="$1"
    local duration=$(check_task_duration "$task_id")

    if [[ $duration -gt $TASK_TIMEOUT_THRESHOLD ]]; then
        log_alert "任务 $task_id 执行时间过长: ${duration}秒 (阈值: ${TASK_TIMEOUT_THRESHOLD}秒)"
        return 0
    fi

    return 1
}

# 检查API错误计数
check_api_errors() {
    local api_error_count=0

    # 检查错误日志中的API错误
    if [[ -f "ERROR_REPORT.md" ]]; then
        api_error_count=$(grep -c "API\|rate.limit\|quota\|timeout" "ERROR_REPORT.md" 2>/dev/null || echo 0)
    fi

    if [[ $api_error_count -gt $API_ERROR_THRESHOLD ]]; then
        log_alert "检测到过多的API错误: $api_error_count 次"
        return 0
    fi

    return 1
}

# 检查网络连接
check_network_connectivity() {
    local network_issues=0

    # 测试基本网络连接
    if ! ping -c 1 google.com &>/dev/null; then
        ((network_issues++))
    fi

    # 测试Claude API连接
    if ! curl -s -I https://api.openai.com &>/dev/null; then
        ((network_issues++))
    fi

    if [[ $network_issues -gt 0 ]]; then
        log_alert "检测到网络连接问题: $network_issues 个连接失败"
        return 0
    fi

    return 1
}

# 检查系统资源
check_system_resources() {
    local resource_issues=0

    # 检查磁盘空间
    local disk_usage=$(df . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        log_warn "磁盘空间使用率过高: ${disk_usage}%"
        ((resource_issues++))
    fi

    # 检查内存使用 (Linux)
    if command -v free &>/dev/null; then
        local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3/$2*100}')
        if [[ $memory_usage -gt 90 ]]; then
            log_warn "内存使用率过高: ${memory_usage}%"
            ((resource_issues++))
        fi
    fi

    # 检查CPU负载 (Linux)
    if command -v uptime &>/dev/null; then
        local load_avg=$(uptime | awk -F'[a-z]:' '{ print $2 }' | awk '{print $1}' | sed 's/,//')
        local cpu_cores=$(nproc 2>/dev/null || echo 1)
        local load_per_cpu=$(echo "$load_avg / $cpu_cores" | bc -l 2>/dev/null || echo 0)

        if (( $(echo "$load_per_cpu > 2.0" | bc -l) )); then
            log_warn "CPU负载过高: $load_avg (每个核心: $load_per_cpu)"
            ((resource_issues++))
        fi
    fi

    if [[ $resource_issues -gt 0 ]]; then
        log_alert "检测到系统资源问题: $resource_issues 个资源告警"
        return 0
    fi

    return 1
}

# 检查执行进度
check_execution_progress() {
    local current_time=$(date +%s)
    local last_update=$(stat -c %Y "$STATUS_FILE" 2>/dev/null || echo 0)
    local time_since_update=$((current_time - last_update))

    # 检查状态文件是否长时间未更新
    if [[ $time_since_update -gt $TASK_TIMEOUT_THRESHOLD ]]; then
        log_alert "执行状态长时间未更新: ${time_since_update}秒"
        return 0
    fi

    return 1
}

# 检查任务完成率
check_task_completion_rate() {
    local total_tasks=$(get_json_value "$STATUS_FILE" ".execution_info.total_tasks" "0")
    local completed_tasks=$(get_json_value "$STATUS_FILE" ".execution_info.completed_tasks" "0")

    if [[ "$total_tasks" == "0" ]]; then
        return 1
    fi

    local completion_rate=$((completed_tasks * 100 / total_tasks))

    # 如果任务开始很久但完成率很低
    local start_time=$(get_json_value "$STATUS_FILE" ".execution_info.start_time" "0")
    if [[ "$start_time" != "0" ]]; then
        local start_timestamp=$(date -d "$start_time" +%s 2>/dev/null || echo 0)
        local elapsed_time=$((current_time - start_timestamp))

        # 如果执行超过2小时但完成率低于20%
        if [[ $elapsed_time -gt 7200 && $completion_rate -lt 20 ]]; then
            log_alert "执行进度缓慢: 完成 ${completion_rate}%，耗时 ${elapsed_time}秒"
            return 0
        fi
    fi

    return 1
}

# 检查错误模式
check_error_patterns() {
    local critical_patterns=0

    if [[ -f "ERROR_REPORT.md" ]]; then
        # 检查严重错误模式
        local patterns=("segmentation.fault" "core.dumped" "permission.denied" "file.not.found" "command.not.found")

        for pattern in "${patterns[@]}"; do
            if grep -q "$pattern" "ERROR_REPORT.md" 2>/dev/null; then
                ((critical_patterns++))
            fi
        done
    fi

    if [[ $critical_patterns -gt 0 ]]; then
        log_alert "检测到 $critical_patterns 个严重错误模式"
        return 0
    fi

    return 1
}

# 生成健康检查报告
generate_health_report() {
    local report_file="HEALTH_REPORT_$(date +%Y%m%d_%H%M%S).md"

    cat > "$report_file" << EOF
# 任务健康检查报告

**检查时间**: $(date '+%Y-%m-%d %H:%M:%S')
**检查器版本**: 1.0

## 系统状态

### 资源使用
- **磁盘空间**: $(df . | awk 'NR==2 {print $5}')
- **内存使用**: $(free -h | awk 'NR==2{print $3"/"$2}')
- **CPU负载**: $(uptime | awk -F'[a-z]:' '{ print $2 }')
- **网络连接**: $(ping -c 1 google.com &>/dev/null && echo "正常" || echo "异常")

### 执行状态
- **总任务数**: $(get_json_value "$STATUS_FILE" ".execution_info.total_tasks" "未知")
- **已完成任务**: $(get_json_value "$STATUS_FILE" ".execution_info.completed_tasks" "未知")
- **失败任务**: $(get_json_value "$STATUS_FILE" ".execution_info.failed_tasks" "未知")
- **当前任务**: $(get_json_value "$STATUS_FILE" ".execution_info.current_task" "无")

## 健康检查结果

EOF

    # 添加具体的检查结果
    local current_task=$(get_json_value "$STATUS_FILE" ".execution_info.current_task" "")

    if [[ -n "$current_task" ]]; then
        cat >> "$report_file" << EOF
### 当前任务状态
- **任务ID**: $current_task
- **执行时间**: $(check_task_duration "$current_task") 秒
- **是否超时**: $(check_task_timeout "$current_task" && echo "是" || echo "否")

EOF
    fi

    cat >> "$report_file" << EOF
### 系统检查
- **网络连接**: $(check_network_connectivity && echo "异常" || echo "正常")
- **系统资源**: $(check_system_resources && echo "异常" || echo "正常")
- **执行进度**: $(check_execution_progress && echo "异常" || echo "正常")
- **错误模式**: $(check_error_patterns && echo "异常" || echo "正常")
- **API错误**: $(check_api_errors && echo "异常" || echo "正常")

## 建议

EOF

    # 生成建议
    if check_task_timeout "$current_task" 2>/dev/null; then
        cat >> "$report_file" << EOF
1. **任务超时**: 当前任务执行时间过长，建议检查是否有问题或需要人工干预
EOF
    fi

    if check_api_errors 2>/dev/null; then
        cat >> "$report_file" << EOF
2. **API错误**: 检测到API错误，建议检查API配额和网络连接
EOF
    fi

    if check_system_resources 2>/dev/null; then
        cat >> "$report_file" << EOF
3. **资源问题**: 系统资源使用率过高，建议释放资源或优化任务
EOF
    fi

    log_health "健康检查报告已生成: $report_file"
}

# 执行健康检查
perform_health_check() {
    log_health "开始执行任务健康检查"

    local issues_found=0
    local current_task=$(get_json_value "$STATUS_FILE" ".execution_info.current_task" "")

    # 检查执行状态文件
    if ! check_file "$STATUS_FILE"; then
        log_alert "执行状态文件不存在，可能需要重新启动任务"
        return 1
    fi

    # 检查当前任务状态
    if [[ -n "$current_task" ]]; then
        if check_task_timeout "$current_task"; then
            ((issues_found++))
        fi
    fi

    # 检查系统级问题
    if check_network_connectivity; then
        ((issues_found++))
    fi

    if check_system_resources; then
        ((issues_found++))
    fi

    if check_execution_progress; then
        ((issues_found++))
    fi

    if check_error_patterns; then
        ((issues_found++))
    fi

    if check_api_errors; then
        ((issues_found++))
    fi

    if check_task_completion_rate; then
        ((issues_found++))
    fi

    # 输出检查结果
    if [[ $issues_found -gt 0 ]]; then
        log_alert "健康检查发现 $issues_found 个问题需要关注"

        # 如果发现问题，生成详细报告
        generate_health_report

        # 返回有问题的状态
        return $issues_found
    else
        log_info "任务执行状态健康"
        return 0
    fi
}

# 持续监控模式
monitor_health() {
    log_health "启动持续健康监控模式"
    log_health "检查间隔: ${HEALTH_CHECK_INTERVAL}秒"

    while true; do
        perform_health_check
        local check_result=$?

        if [[ $check_result -gt 0 ]]; then
            log_alert "检测到健康问题，可能需要人工干预"

            # 可以在这里添加自动恢复逻辑
            # 例如: ./smart-retry-handler.sh --monitor
        fi

        log_health "下次健康检查将在 ${HEALTH_CHECK_INTERVAL} 秒后进行"
        sleep "$HEALTH_CHECK_INTERVAL"
    done
}

# 显示帮助信息
show_help() {
    cat << EOF
任务健康检查器 v1.0

用法: $0 [选项]

选项:
    --check              执行单次健康检查
    --monitor            启动持续健康监控
    --report             生成健康检查报告
    --help               显示此帮助信息

示例:
    $0 --check           # 执行单次检查
    $0 --monitor         # 启动持续监控
    $0 --report          # 生成报告

配置参数:
    HEALTH_CHECK_INTERVAL=${HEALTH_CHECK_INTERVAL}秒
    TASK_TIMEOUT_THRESHOLD=${TASK_TIMEOUT_THRESHOLD}秒
    API_ERROR_THRESHOLD=${API_ERROR_THRESHOLD}次
    NETWORK_ERROR_THRESHOLD=${NETWORK_ERROR_THRESHOLD}次

EOF
}

# 主函数
main() {
    # 创建必要的目录
    mkdir -p LOGS REPORTS

    # 初始化日志文件
    echo "# 任务健康检查日志" > "$HEALTH_LOG_FILE"
    echo "启动时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$HEALTH_LOG_FILE"
    echo "" >> "$HEALTH_LOG_FILE"

    echo "# 告警日志" > "$ALERT_LOG_FILE"
    echo "启动时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$ALERT_LOG_FILE"
    echo "" >> "$ALERT_LOG_FILE"

    case "$1" in
        "--check")
            perform_health_check
            ;;
        "--monitor")
            monitor_health
            ;;
        "--report")
            generate_health_report
            ;;
        "--help"|"")
            show_help
            ;;
        *)
            log_alert "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi