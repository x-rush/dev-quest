#!/bin/bash
# 智能重试处理器 - Smart Retry Handler
# 用于处理Claude Code执行过程中的异常恢复和智能重试

# 配置参数
MAX_TOTAL_RETRIES=10                  # 全局最大重试次数
MAX_RETRY_PER_TASK=3                   # 单个任务最大重试次数
RETRY_DELAY_BASE=30                    # 基础重试延迟(秒)
RETRY_DELAY_MAX=1800                   # 最大重试延迟(30分钟)
ERROR_LOG_FILE="ERROR_REPORT.md"       # 错误日志文件
STATUS_FILE="EXECUTION_STATUS.json"    # 执行状态文件
RETRY_LOG_FILE="RETRY_LOG.md"          # 重试日志文件

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$RETRY_LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$RETRY_LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$RETRY_LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$RETRY_LOG_FILE"
}

# 检查依赖
check_dependencies() {
    local deps=("jq" "claude")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "缺少依赖工具: $dep"
            return 1
        fi
    done
    return 0
}

# 读取执行状态
read_execution_status() {
    if [[ ! -f "$STATUS_FILE" ]]; then
        log_error "执行状态文件不存在: $STATUS_FILE"
        return 1
    fi

    local status=$(jq -r '.execution_info.status' "$STATUS_FILE" 2>/dev/null)
    echo "$status"
}

# 读取当前任务
read_current_task() {
    if [[ ! -f "$STATUS_FILE" ]]; then
        echo ""
        return 1
    fi

    local current_task=$(jq -r '.execution_info.current_task' "$STATUS_FILE" 2>/dev/null)
    echo "$current_task"
}

# 读取重试计数
read_retry_count() {
    local task_id="$1"

    if [[ ! -f "$STATUS_FILE" ]]; then
        echo "0"
        return 1
    fi

    local count=$(jq -r ".retry_info.task_retries.\"$task_id\" // 0" "$STATUS_FILE" 2>/dev/null)
    echo "$count"
}

# 更新重试计数
update_retry_count() {
    local task_id="$1"

    # 创建重试信息结构如果不存在
    jq --arg task_id "$task_id" '
        if .retry_info == null then
            .retry_info = {total_retries: 0, task_retries: {}}
        else
            .
        end |
        .retry_info.total_retries += 1 |
        .retry_info.task_retries[$task_id] += 1
    ' "$STATUS_FILE" > temp_status.json && mv temp_status.json "$STATUS_FILE"

    log_info "更新任务 $task_id 重试计数"
}

# 检查是否应该重试
should_retry() {
    local task_id="$1"
    local error_type="$2"

    # 检查全局重试限制
    local total_retries=$(jq -r '.retry_info.total_retries // 0' "$STATUS_FILE" 2>/dev/null)
    if [[ $total_retries -ge $MAX_TOTAL_RETRIES ]]; then
        log_error "已达到全局最大重试次数 ($MAX_TOTAL_RETRIES)"
        return 1
    fi

    # 检查单任务重试限制
    local task_retries=$(read_retry_count "$task_id")
    if [[ $task_retries -ge $MAX_RETRY_PER_TASK ]]; then
        log_error "任务 $task_id 已达到最大重试次数 ($MAX_RETRY_PER_TASK)"
        return 1
    fi

    # 检查错误类型是否可重试
    case "$error_type" in
        "API_ERROR"|"TIMEOUT"|"NETWORK_ERROR"|"TEMPORARY_FAILURE")
            return 0
            ;;
        "PERMISSION_DENIED"|"INVALID_INPUT"|"CONFIGURATION_ERROR")
            log_warn "错误类型 $error_type 不适合自动重试"
            return 1
            ;;
        *)
            log_warn "未知错误类型 $error_type，默认允许重试"
            return 0
            ;;
    esac
}

# 计算重试延迟 (指数退避)
calculate_retry_delay() {
    local task_id="$1"
    local retry_count=$(read_retry_count "$task_id")

    # 指数退避: base_delay * (2 ^ retry_count)
    local delay=$((RETRY_DELAY_BASE * (2 ** retry_count)))

    # 限制最大延迟
    if [[ $delay -gt $RETRY_DELAY_MAX ]]; then
        delay=$RETRY_DELAY_MAX
    fi

    echo "$delay"
}

# 分析错误类型
analyze_error() {
    local error_message="$1"

    if [[ "$error_message" =~ API|rate.limit|quota.exceeded ]]; then
        echo "API_ERROR"
    elif [[ "$error_message" =~ timeout|time.out ]]; then
        echo "TIMEOUT"
    elif [[ "$error_message" =~ network|connection|dns ]]; then
        echo "NETWORK_ERROR"
    elif [[ "$error_message" =~ permission|denied|unauthorized ]]; then
        echo "PERMISSION_DENIED"
    elif [[ "$error_message" =~ invalid|syntax|format ]]; then
        echo "INVALID_INPUT"
    elif [[ "$error_message" =~ config|configuration ]]; then
        echo "CONFIGURATION_ERROR"
    else
        echo "UNKNOWN_ERROR"
    fi
}

# 创建恢复点
create_recovery_point() {
    local task_id="$1"
    local recovery_point="recovery_point_$(date +%Y%m%d_%H%M%S)"

    mkdir -p "RECOVERY_POINTS"

    # 备份当前状态
    cp "$STATUS_FILE" "RECOVERY_POINTS/${recovery_point}_status.json"

    # 记录恢复点信息
    cat > "RECOVERY_POINTS/${recovery_point}_info.md" << EOF
# 恢复点信息

**恢复点ID**: $recovery_point
**任务ID**: $task_id
**创建时间**: $(date '+%Y-%m-%d %H:%M:%S')
**重试次数**: $(read_retry_count "$task_id")

**上下文信息**:
- 执行状态: $(read_execution_status)
- 当前任务: $(read_current_task)
- 错误原因: 需要手动检查错误日志

**恢复操作**:
```bash
# 从此恢复点恢复
./task-recovery.sh --recovery-point $recovery_point
```
EOF

    log_info "创建恢复点: $recovery_point"
    echo "$recovery_point"
}

# 智能重试执行
smart_retry() {
    local task_id="$1"
    local error_message="$2"

    local error_type=$(analyze_error "$error_message")

    log_info "分析到错误类型: $error_type"

    # 检查是否应该重试
    if ! should_retry "$task_id" "$error_type"; then
        log_error "任务 $task_id 不适合或无法继续重试"
        return 1
    fi

    # 更新重试计数
    update_retry_count "$task_id"

    # 创建恢复点
    local recovery_point=$(create_recovery_point "$task_id")

    # 计算重试延迟
    local retry_delay=$(calculate_retry_delay "$task_id")
    log_info "任务 $task_id 将在 $retry_delay 秒后重试"

    # 等待重试延迟
    for ((i=retry_delay; i>0; i--)); do
        echo -ne "\r${BLUE}等待重试: ${NC}${i}秒 "
        sleep 1
    done
    echo ""

    # 执行重试
    log_info "开始重试任务: $task_id"

    # 重新核实任务目标和进度
    local retry_command="claude \"任务 $task_id 在执行过程中遇到错误，需要重新核实。请检查 EXECUTION_STATUS.json 中的当前进度，确认任务目标是否仍然有效，然后从错误点继续执行或重新开始有问题的地方。错误信息: $error_message\""

    log_info "执行重试命令: $retry_command"
    eval "$retry_command"

    local retry_result=$?

    if [[ $retry_result -eq 0 ]]; then
        log_success "任务 $task_id 重试成功"
        return 0
    else
        log_error "任务 $task_id 重试失败"
        return 1
    fi
}

# 监控任务执行状态
monitor_execution() {
    log_info "开始监控Claude Code执行状态"

    local last_check_time=$(date +%s)
    local check_interval=300  # 5分钟检查一次

    while true; do
        local current_time=$(date +%s)
        local time_since_last_check=$((current_time - last_check_time))

        # 检查执行状态文件是否存在和更新
        if [[ ! -f "$STATUS_FILE" ]]; then
            log_warn "执行状态文件不存在，可能需要启动新的执行"
            sleep $check_interval
            continue
        fi

        local status=$(read_execution_status)
        local current_task=$(read_current_task)

        log_info "当前状态: $status, 当前任务: $current_task"

        # 检查状态文件最后更新时间
        local last_update=$(stat -c %Y "$STATUS_FILE" 2>/dev/null || echo 0)
        local time_since_update=$((current_time - last_update))

        # 如果超过15分钟没有更新，可能卡住了
        if [[ $time_since_update -gt 900 ]]; then
            log_warn "执行状态超过15分钟未更新，任务可能卡住"

            # 尝试分析问题
            if [[ -n "$current_task" ]]; then
                smart_retry "$current_task" "任务长时间无响应，疑似超时"
            fi
        fi

        # 检查是否有错误报告
        if [[ -f "$ERROR_LOG_FILE" ]]; then
            local recent_errors=$(tail -10 "$ERROR_LOG_FILE" | grep -c "ERROR")
            if [[ $recent_errors -gt 0 ]]; then
                log_warn "检测到最近有 $recent_errors 个错误"

                # 分析最新错误
                local latest_error=$(tail -1 "$ERROR_LOG_FILE")
                if [[ -n "$current_task" ]]; then
                    smart_retry "$current_task" "$latest_error"
                fi
            fi
        fi

        last_check_time=$current_time
        sleep $check_interval
    done
}

# 手动触发重试
manual_retry() {
    local task_id="$1"

    if [[ -z "$task_id" ]]; then
        log_error "请指定任务ID"
        return 1
    fi

    log_info "手动触发任务 $task_id 重试"

    # 检查任务状态
    local status=$(read_execution_status)
    local current_task=$(read_current_task)

    if [[ "$status" == "COMPLETED" ]]; then
        log_warn "任务已完成，无需重试"
        return 0
    fi

    # 执行手动重试
    local retry_command="claude \"手动重试任务 $task_id。请检查当前执行状态，确认任务进度，然后继续执行或重新开始有问题的地方\""

    log_info "执行手动重试: $retry_command"
    eval "$retry_command"
}

# 显示重试统计
show_retry_stats() {
    echo "=== 重试统计信息 ==="
    echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    if [[ -f "$STATUS_FILE" ]]; then
        local total_retries=$(jq -r '.retry_info.total_retries // 0' "$STATUS_FILE" 2>/dev/null)
        echo "全局重试次数: $total_retries / $MAX_TOTAL_RETRIES"

        echo ""
        echo "各任务重试次数:"
        jq -r '.retry_info.task_retries | to_entries[] | "  \(.key): \(.value)次"' "$STATUS_FILE" 2>/dev/null
    else
        echo "执行状态文件不存在"
    fi

    echo ""
    echo "最近的恢复点:"
    if [[ -d "RECOVERY_POINTS" ]]; then
        ls -la RECOVERY_POINTS/ | grep recovery_point | tail -5
    else
        echo "无恢复点"
    fi
}

# 清理旧的恢复点
cleanup_old_recovery_points() {
    local max_recovery_points=10

    if [[ ! -d "RECOVERY_POINTS" ]]; then
        return 0
    fi

    local recovery_point_count=$(ls RECOVERY_POINTS/ | grep recovery_point | wc -l)

    if [[ $recovery_point_count -gt $max_recovery_points ]]; then
        log_info "清理旧的恢复点，保留最新 $max_recovery_points 个"

        # 删除最旧的恢复点
        ls -t RECOVERY_POINTS/ | grep recovery_point | tail -n +$((max_recovery_points + 1)) | xargs -I {} rm -f "RECOVERY_POINTS/{}"

        log_info "清理完成"
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
Claude Code 智能重试处理器 v1.0

用法: $0 [选项] [参数]

选项:
    --monitor                   启动执行状态监控
    --retry <task_id>          手动重试指定任务
    --stats                    显示重试统计信息
    --cleanup                  清理旧的恢复点
    --help                     显示此帮助信息

示例:
    $0 --monitor               # 启动监控模式
    $0 --retry T001-002        # 重试任务 T001-002
    $0 --stats                 # 显示统计信息
    $0 --cleanup               # 清理旧恢复点

配置参数:
    MAX_TOTAL_RETRIES=$MAX_TOTAL_RETRIES
    MAX_RETRY_PER_TASK=$MAX_RETRY_PER_TASK
    RETRY_DELAY_BASE=$RETRY_DELAY_BASE 秒
    RETRY_DELAY_MAX=$RETRY_DELAY_MAX 秒

EOF
}

# 主函数
main() {
    # 检查依赖
    if ! check_dependencies; then
        log_error "依赖检查失败，请安装必要的工具"
        exit 1
    fi

    # 创建必要的目录
    mkdir -p RECOVERY_POINTS LOGS

    # 初始化重试日志
    echo "# 智能重试日志" > "$RETRY_LOG_FILE"
    echo "启动时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$RETRY_LOG_FILE"
    echo "" >> "$RETRY_LOG_FILE"

    case "$1" in
        "--monitor")
            log_info "启动智能重试监控模式"
            monitor_execution
            ;;
        "--retry")
            manual_retry "$2"
            ;;
        "--stats")
            show_retry_stats
            ;;
        "--cleanup")
            cleanup_old_recovery_points
            ;;
        "--help"|"")
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi