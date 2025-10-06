#!/bin/bash
# Claude Code 执行监控器 - 综合监控和告警系统
# 整合所有监控功能，提供统一的任务执行监控界面

# 配置参数
MONITOR_INTERVAL=60                    # 监控间隔(秒)
ALERT_COOLDOWN=300                    # 告警冷却时间(秒)
LOG_ROTATION_SIZE=10M                  # 日志轮转大小
MAX_LOG_FILES=5                        # 最大日志文件数

# 文件路径
STATUS_FILE="EXECUTION_STATUS.json"
MONITOR_LOG_FILE="MONITOR_LOG.md"
ALERT_HISTORY_FILE="ALERT_HISTORY.md"
DASHBOARD_FILE="MONITOR_DASHBOARD.md"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m'

# 全局变量
LAST_ALERT_TIME=0
MONITOR_START_TIME=$(date +%s)

# 日志函数
log_monitor() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$level" in
        "INFO")
            echo -e "${BLUE}[MONITOR]${NC} $timestamp - $message" | tee -a "$MONITOR_LOG_FILE"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} $timestamp - $message" | tee -a "$MONITOR_LOG_FILE"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $timestamp - $message" | tee -a "$MONITOR_LOG_FILE"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $timestamp - $message" | tee -a "$MONITOR_LOG_FILE"
            ;;
        "ALERT")
            echo -e "${MAGENTA}[ALERT]${NC} $timestamp - $message" | tee -a "$MONITOR_LOG_FILE"
            # 记录到告警历史
            echo "[$timestamp] $message" >> "$ALERT_HISTORY_FILE"
            ;;
    esac
}

# 获取JSON字段值
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

# 计算执行时间
calculate_execution_time() {
    local start_time="$1"
    local current_time=$(date +%s)

    if [[ -z "$start_time" || "$start_time" == "null" ]]; then
        echo "0"
        return 1
    fi

    local start_timestamp=$(date -d "$start_time" +%s 2>/dev/null || echo 0)
    local duration=$((current_time - start_timestamp))

    echo "$duration"
}

# 格式化时间显示
format_duration() {
    local seconds="$1"
    local hours=$((seconds / 3600))
    local minutes=$(((seconds % 3600) / 60))
    local secs=$((seconds % 60))

    if [[ $hours -gt 0 ]]; then
        printf "%dh %dm %ds" $hours $minutes $secs
    elif [[ $minutes -gt 0 ]]; then
        printf "%dm %ds" $minutes $secs
    else
        printf "%ds" $secs
    fi
}

# 检查系统状态
check_system_status() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//' 2>/dev/null || echo "0")
    local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3/$2*100}' 2>/dev/null || echo "0")
    local disk_usage=$(df . | awk 'NR==2 {print $5}' | sed 's/%//' 2>/dev/null || echo "0")
    local load_avg=$(uptime | awk -F'[a-z]:' '{ print $2 }' | awk '{print $1}' | sed 's/,//' 2>/dev/null || echo "0")

    echo "CPU:${cpu_usage}% MEM:${memory_usage}% DISK:${disk_usage}% LOAD:${load_avg}"
}

# 检查网络状态
check_network_status() {
    local ping_result="FAIL"
    local api_result="FAIL"

    if ping -c 1 google.com &>/dev/null; then
        ping_result="OK"
    fi

    if curl -s --max-time 5 https://api.openai.com &>/dev/null; then
        api_result="OK"
    fi

    echo "PING:${ping_result} API:${api_result}"
}

# 获取任务状态摘要
get_task_summary() {
    if [[ ! -f "$STATUS_FILE" ]]; then
        echo "状态文件不存在"
        return 1
    fi

    local status=$(get_json_value "$STATUS_FILE" ".execution_info.status" "UNKNOWN")
    local current_task=$(get_json_value "$STATUS_FILE" ".execution_info.current_task" "NONE")
    local total_tasks=$(get_json_value "$STATUS_FILE" ".execution_info.total_tasks" "0")
    local completed_tasks=$(get_json_value "$STATUS_FILE" ".execution_info.completed_tasks" "0")
    local failed_tasks=$(get_json_value "$STATUS_FILE" ".execution_info.failed_tasks" "0")

    if [[ "$total_tasks" != "0" ]]; then
        local progress=$((completed_tasks * 100 / total_tasks))
        echo "状态:$status 进度:$progress%($completed_tasks/$total_tasks) 失败:$failed_tasks 当前:$current_task"
    else
        echo "状态:$status 当前:$current_task"
    fi
}

# 检查异常情况
check_anomalies() {
    local anomalies=0

    # 检查任务超时
    local current_task=$(get_json_value "$STATUS_FILE" ".execution_info.current_task" "")
    if [[ -n "$current_task" && "$current_task" != "null" ]]; then
        local start_time=$(get_json_value "$STATUS_FILE" ".tasks.\"$current_task\".start_time" "")
        if [[ -n "$start_time" && "$start_time" != "null" ]]; then
            local duration=$(calculate_execution_time "$start_time")
            if [[ $duration -gt 1800 ]]; then  # 30分钟超时
                log_monitor "ALERT" "任务 $current_task 执行时间过长: $(format_duration $duration)"
                ((anomalies++))
            fi
        fi
    fi

    # 检查状态文件更新时间
    if [[ -f "$STATUS_FILE" ]]; then
        local last_update=$(stat -c %Y "$STATUS_FILE" 2>/dev/null)
        local current_time=$(date +%s)
        local time_diff=$((current_time - last_update))

        if [[ $time_diff -gt 900 ]]; then  # 15分钟未更新
            log_monitor "ALERT" "执行状态长时间未更新: $(format_duration $time_diff)"
            ((anomalies++))
        fi
    fi

    # 检查错误日志
    if [[ -f "ERROR_REPORT.md" ]]; then
        local recent_errors=$(tail -10 "ERROR_REPORT.md" | grep -c "ERROR" 2>/dev/null || echo 0)
        if [[ $recent_errors -gt 3 ]]; then
            log_monitor "ALERT" "检测到 $recent_errors 个最近错误"
            ((anomalies++))
        fi
    fi

    return $anomalies
}

# 生成监控仪表板
generate_dashboard() {
    local dashboard_content="# Claude Code 执行监控仪表板\n\n"
    dashboard_content+="**更新时间**: $(date '+%Y-%m-%d %H:%M:%S')\n"
    dashboard_content+="**监控启动时间**: $(date -d "@$MONITOR_START_TIME" '+%Y-%m-%d %H:%M:%S')\n"
    dashboard_content+="**监控时长**: $(format_duration $(($(date +%s) - MONITOR_START_TIME)))\n\n"

    # 系统状态
    dashboard_content+="## 🖥️ 系统状态\n\n"
    local system_status=$(check_system_status)
    dashboard_content+="\`\`\`\n$system_status\n\`\`\`\n\n"

    # 网络状态
    dashboard_content+="## 🌐 网络状态\n\n"
    local network_status=$(check_network_status)
    dashboard_content+="\`\`\`\n$network_status\n\`\`\`\n\n"

    # 任务执行状态
    dashboard_content+="## 📊 任务执行状态\n\n"
    local task_summary=$(get_task_summary)
    dashboard_content+="**执行摘要**: $task_summary\n\n"

    if [[ -f "$STATUS_FILE" ]]; then
        local start_time=$(get_json_value "$STATUS_FILE" ".execution_info.start_time" "")
        if [[ -n "$start_time" && "$start_time" != "null" ]]; then
            local execution_time=$(calculate_execution_time "$start_time")
            dashboard_content+="**执行时间**: $(format_duration $execution_time)\n\n"
        fi

        # 质量指标
        local quality_score=$(get_json_value "$STATUS_FILE" ".quality_metrics.overall_score" "N/A")
        local pass_rate=$(get_json_value "$STATUS_FILE" ".quality_metrics.validation_pass_rate" "N/A")
        dashboard_content+="**质量指标**:\n"
        dashboard_content+="- 总体评分: $quality_score/10\n"
        dashboard_content+="- 验证通过率: $pass_rate\n\n"
    fi

    # 最近活动
    dashboard_content+="## 📝 最近活动\n\n"
    if [[ -f "EXECUTION_LOG.md" ]]; then
        dashboard_content+="\`\`\`\n$(tail -10 "EXECUTION_LOG.md")\n\`\`\`\n\n"
    else
        dashboard_content+="暂无执行日志\n\n"
    fi

    # 异常和告警
    dashboard_content+="## ⚠️ 异常和告警\n\n"
    if [[ -f "$ALERT_HISTORY_FILE" ]]; then
        dashboard_content+="\`\`\`\n$(tail -5 "$ALERT_HISTORY_FILE")\n\`\`\`\n\n"
    else
        dashboard_content+="暂无告警记录\n\n"
    fi

    # 监控统计
    dashboard_content+="## 📈 监控统计\n\n"
    local total_alerts=$(wc -l < "$ALERT_HISTORY_FILE" 2>/dev/null || echo 0)
    local log_entries=$(wc -l < "$MONITOR_LOG_FILE" 2>/dev/null || echo 0)
    dashboard_content+="- 总告警数: $total_alerts\n"
    dashboard_content+="- 日志条目: $log_entries\n"
    dashboard_content+="- 监控检查次数: $((log_entries / 2))\n\n"

    # 快速操作
    dashboard_content+="## 🚀 快速操作\n\n"
    dashboard_content+="\`\`\`bash\n"
    dashboard_content+="# 查看详细状态\n"
    dashboard_content+="cat EXECUTION_STATUS.json | jq .\n\n"
    dashboard_content+="# 手动重试任务\n"
    dashboard_content+="./smart-retry-handler.sh --retry <task_id>\n\n"
    dashboard_content+="# 执行健康检查\n"
    dashboard_content+="./task-health-checker.sh --check\n\n"
    dashboard_content+="# 任务恢复\n"
    dashboard_content+="./task-recovery.sh --interactive\n"
    dashboard_content+="\`\`\`\n"

    # 写入仪表板文件
    echo -e "$dashboard_content" > "$DASHBOARD_FILE"
}

# 显示实时监控界面
show_monitor_interface() {
    clear
    echo -e "${WHITE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${WHITE}║                Claude Code 执行监控器                    ║${NC}"
    echo -e "${WHITE}║                     实时监控界面                        ║${NC}"
    echo -e "${WHITE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    while true; do
        # 清屏并显示标题
        clear
        echo -e "${WHITE}╔══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${WHITE}║                Claude Code 执行监控器                    ║${NC}"
        echo -e "${WHITE}║                     $(date '+%Y-%m-%d %H:%M:%S')                        ║${NC}"
        echo -e "${WHITE}╚══════════════════════════════════════════════════════════════╝${NC}"
        echo ""

        # 系统状态
        echo -e "${CYAN}🖥️  系统状态${NC}"
        local system_status=$(check_system_status)
        echo "   $system_status"
        echo ""

        # 网络状态
        echo -e "${CYAN}🌐 网络状态${NC}"
        local network_status=$(check_network_status)
        echo "   $network_status"
        echo ""

        # 任务状态
        echo -e "${CYAN}📊 任务执行状态${NC}"
        local task_summary=$(get_task_summary)
        echo "   $task_summary"
        echo ""

        # 执行时间
        if [[ -f "$STATUS_FILE" ]]; then
            local start_time=$(get_json_value "$STATUS_FILE" ".execution_info.start_time" "")
            if [[ -n "$start_time" && "$start_time" != "null" ]]; then
                local execution_time=$(calculate_execution_time "$start_time")
                echo -e "${CYAN}⏱️  执行时间${NC}"
                echo "   $(format_duration $execution_time)"
                echo ""
            fi
        fi

        # 最近告警
        if [[ -f "$ALERT_HISTORY_FILE" ]]; then
            local recent_alerts=$(tail -3 "$ALERT_HISTORY_FILE" 2>/dev/null)
            if [[ -n "$recent_alerts" ]]; then
                echo -e "${YELLOW}⚠️  最近告警${NC}"
                echo "$recent_alerts" | while read line; do
                    echo "   $line"
                done
                echo ""
            fi
        fi

        # 监控统计
        local total_alerts=$(wc -l < "$ALERT_HISTORY_FILE" 2>/dev/null || echo 0)
        local log_entries=$(wc -l < "$MONITOR_LOG_FILE" 2>/dev/null || echo 0)
        echo -e "${CYAN}📈 监控统计${NC}"
        echo "   总告警: $total_alerts  |  日志条目: $log_entries  |  监控时长: $(format_duration $(($(date +%s) - MONITOR_START_TIME)))"
        echo ""

        echo -e "${BLUE}按 Ctrl+C 退出监控 | 仪表板文件: $DASHBOARD_FILE${NC}"
        echo ""

        # 执行异常检查
        check_anomalies

        # 生成仪表板
        generate_dashboard

        # 等待下次检查
        sleep "$MONITOR_INTERVAL"
    done
}

# 后台监控模式
background_monitor() {
    log_monitor "INFO" "启动后台监控模式，监控间隔: ${MONITOR_INTERVAL}秒"

    while true; do
        # 检查系统状态
        local system_status=$(check_system_status)
        log_monitor "INFO" "系统状态: $system_status"

        # 检查网络状态
        local network_status=$(check_network_status)
        log_monitor "INFO" "网络状态: $network_status"

        # 检查任务状态
        local task_summary=$(get_task_summary)
        log_monitor "INFO" "任务状态: $task_summary"

        # 检查异常
        check_anomalies
        local anomaly_count=$?

        if [[ $anomaly_count -gt 0 ]]; then
            log_monitor "WARN" "检测到 $anomaly_count 个异常"
        fi

        # 生成仪表板
        generate_dashboard

        sleep "$MONITOR_INTERVAL"
    done
}

# 一次性检查
single_check() {
    log_monitor "INFO" "执行一次性监控检查"

    echo -e "${WHITE}=== Claude Code 执行状态检查 ===${NC}"
    echo ""

    # 系统状态
    echo -e "${CYAN}🖥️  系统状态:${NC}"
    local system_status=$(check_system_status)
    echo "   $system_status"
    echo ""

    # 网络状态
    echo -e "${CYAN}🌐 网络状态:${NC}"
    local network_status=$(check_network_status)
    echo "   $network_status"
    echo ""

    # 任务状态
    echo -e "${CYAN}📊 任务执行状态:${NC}"
    local task_summary=$(get_task_summary)
    echo "   $task_summary"
    echo ""

    # 异常检查
    echo -e "${CYAN}⚠️  异常检查:${NC}"
    check_anomalies
    local anomaly_count=$?
    if [[ $anomaly_count -eq 0 ]]; then
        echo -e "${GREEN}   ✓ 未检测到异常${NC}"
    else
        echo -e "${YELLOW}   ⚠ 检测到 $anomaly_count 个异常${NC}"
    fi
    echo ""

    # 生成仪表板
    generate_dashboard
    echo -e "${GREEN}✓ 监控仪表板已更新: $DASHBOARD_FILE${NC}"
}

# 清理日志
cleanup_logs() {
    log_monitor "INFO" "开始清理日志文件"

    # 检查并轮转监控日志
    if [[ -f "$MONITOR_LOG_FILE" ]]; then
        local log_size=$(stat -c%s "$MONITOR_LOG_FILE" 2>/dev/null || echo 0)
        local max_size=$((10 * 1024 * 1024))  # 10MB

        if [[ $log_size -gt $max_size ]]; then
            mv "$MONITOR_LOG_FILE" "${MONITOR_LOG_FILE}.old"
            log_monitor "INFO" "监控日志已轮转"
        fi
    fi

    # 清理旧的仪表板文件
    find . -name "MONITOR_DASHBOARD_*.md" -mtime +7 -delete 2>/dev/null

    # 清理旧的告警历史
    if [[ -f "$ALERT_HISTORY_FILE" ]]; then
        local alert_lines=$(wc -l < "$ALERT_HISTORY_FILE" 2>/dev/null || echo 0)
        if [[ $alert_lines -gt 1000 ]]; then
            tail -500 "$ALERT_HISTORY_FILE" > "${ALERT_HISTORY_FILE}.tmp"
            mv "${ALERT_HISTORY_FILE}.tmp" "$ALERT_HISTORY_FILE"
            log_monitor "INFO" "告警历史已清理"
        fi
    fi

    log_monitor "INFO" "日志清理完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
Claude Code 执行监控器 v1.0

用法: $0 [选项]

选项:
    --interface         显示实时监控界面
    --background        启动后台监控模式
    --check             执行一次性状态检查
    --dashboard         生成监控仪表板
    --cleanup           清理日志文件
    --help              显示此帮助信息

示例:
    $0 --interface      # 启动实时监控界面
    $0 --background     # 后台监控模式
    $0 --check          # 一次性状态检查
    $0 --dashboard      # 生成仪表板

配置参数:
    MONITOR_INTERVAL=${MONITOR_INTERVAL}秒
    ALERT_COOLDOWN=${ALERT_COOLDOWN}秒
    LOG_ROTATION_SIZE=${LOG_ROTATION_SIZE}
    MAX_LOG_FILES=${MAX_LOG_FILES}

输出文件:
    - $MONITOR_LOG_FILE: 监控日志
    - $ALERT_HISTORY_FILE: 告警历史
    - $DASHBOARD_FILE: 监控仪表板

EOF
}

# 初始化监控环境
init_monitoring() {
    # 创建必要目录
    mkdir -p LOGS REPORTS MONITOR_DATA

    # 初始化日志文件
    echo "# Claude Code 执行监控日志" > "$MONITOR_LOG_FILE"
    echo "启动时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$MONITOR_LOG_FILE"
    echo "" >> "$MONITOR_LOG_FILE"

    echo "# 告警历史记录" > "$ALERT_HISTORY_FILE"
    echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$ALERT_HISTORY_FILE"
    echo "" >> "$ALERT_HISTORY_FILE"

    log_monitor "INFO" "监控环境初始化完成"
}

# 主函数
main() {
    # 检查依赖
    local deps=("jq")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            echo -e "${RED}错误: 缺少依赖工具 $dep${NC}" >&2
            exit 1
        fi
    done

    # 初始化监控环境
    init_monitoring

    case "$1" in
        "--interface")
            show_monitor_interface
            ;;
        "--background")
            background_monitor
            ;;
        "--check")
            single_check
            ;;
        "--dashboard")
            generate_dashboard
            echo -e "${GREEN}仪表板已生成: $DASHBOARD_FILE${NC}"
            ;;
        "--cleanup")
            cleanup_logs
            ;;
        "--help"|"")
            show_help
            ;;
        *)
            echo -e "${RED}错误: 未知选项 $1${NC}" >&2
            show_help
            exit 1
            ;;
    esac
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi