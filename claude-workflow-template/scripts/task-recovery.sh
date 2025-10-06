#!/bin/bash
# 任务恢复器 - Task Recovery Manager
# 专门用于从各种异常情况中恢复Claude Code任务执行

# 配置参数
RECOVERY_MODES=("auto" "manual" "interactive")
DEFAULT_RECOVERY_MODE="interactive"
STATUS_FILE="EXECUTION_STATUS.json"
RECOVERY_LOG_FILE="RECOVERY_LOG.md"
BACKUP_DIR="RECOVERY_POINTS"
MAX_BACKUPS=20

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 日志函数
log_recovery() {
    echo -e "${CYAN}[RECOVERY]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$RECOVERY_LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$RECOVERY_LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$RECOVERY_LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$RECOVERY_LOG_FILE"
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

# 获取执行状态
get_execution_status() {
    if [[ ! -f "$STATUS_FILE" ]]; then
        echo "NO_STATUS_FILE"
        return 1
    fi

    local status=$(jq -r '.execution_info.status' "$STATUS_FILE" 2>/dev/null)
    echo "$status"
}

# 获取当前任务
get_current_task() {
    if [[ ! -f "$STATUS_FILE" ]]; then
        echo ""
        return 1
    fi

    local current_task=$(jq -r '.execution_info.current_task' "$STATUS_FILE" 2>/dev/null)
    echo "$current_task"
}

# 列出可用的恢复点
list_recovery_points() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        log_info "没有恢复点目录"
        return 1
    fi

    log_info "可用的恢复点:"
    local count=0

    for recovery_point in $(ls -t "$BACKUP_DIR" | grep "recovery_point_.*_status.json" | head -10); do
        local recovery_id=$(echo "$recovery_point" | sed 's/_status.json//')
        local info_file="$BACKUP_DIR/${recovery_id}_info.md"

        if [[ -f "$info_file" ]]; then
            local task_id=$(grep "任务ID:" "$info_file" | awk '{print $3}')
            local create_time=$(grep "创建时间:" "$info_file" | awk '{print $2" "$3}')

            echo "  $((++count)). $recovery_id"
            echo "     任务ID: $task_id"
            echo "     创建时间: $create_time"
            echo ""
        fi
    done

    if [[ $count -eq 0 ]]; then
        log_info "没有找到可用的恢复点"
        return 1
    fi

    return 0
}

# 从恢复点恢复状态
recover_from_point() {
    local recovery_point="$1"

    if [[ -z "$recovery_point" ]]; then
        log_error "请指定恢复点ID"
        return 1
    fi

    local status_backup="$BACKUP_DIR/${recovery_point}_status.json"
    local info_file="$BACKUP_DIR/${recovery_point}_info.md"

    if [[ ! -f "$status_backup" ]]; then
        log_error "恢复点状态文件不存在: $status_backup"
        return 1
    fi

    log_info "从恢复点恢复状态: $recovery_point"

    # 备份当前状态
    if [[ -f "$STATUS_FILE" ]]; then
        local current_backup="backup_before_recovery_$(date +%Y%m%d_%H%M%S).json"
        cp "$STATUS_FILE" "BACKUPS/$current_backup"
        log_info "当前状态已备份到: $current_backup"
    fi

    # 恢复状态
    cp "$status_backup" "$STATUS_FILE"

    # 更新恢复时间戳
    jq --arg recovery_time "$(date -Iseconds)" '.execution_info.last_recovery = $recovery_time' "$STATUS_FILE" > temp.json && mv temp.json "$STATUS_FILE"

    log_success "状态恢复完成"

    # 显示恢复点信息
    if [[ -f "$info_file" ]]; then
        log_info "恢复点信息:"
        cat "$info_file"
    fi

    return 0
}

# 智能状态恢复
smart_state_recovery() {
    log_info "开始智能状态恢复"

    # 检查状态文件
    if [[ ! -f "$STATUS_FILE" ]]; then
        log_error "执行状态文件不存在，无法进行智能恢复"
        return 1
    fi

    # 检查状态文件是否损坏
    if ! jq . "$STATUS_FILE" &>/dev/null; then
        log_error "执行状态文件损坏，尝试从备份恢复"

        # 尝试从最新的恢复点恢复
        local latest_recovery=$(ls -t "$BACKUP_DIR" | grep "recovery_point_.*_status.json" | head -1)
        if [[ -n "$latest_recovery" ]]; then
            local recovery_id=$(echo "$latest_recovery" | sed 's/_status.json//')
            recover_from_point "$recovery_id"
            return $?
        else
            log_error "没有可用的恢复点，智能恢复失败"
            return 1
        fi
    fi

    # 检查任务状态一致性
    local status=$(get_execution_status)
    local current_task=$(get_current_task)

    log_info "当前状态: $status, 当前任务: $current_task"

    # 如果状态为空或无效，尝试修复
    if [[ "$status" == "null" || -z "$status" ]]; then
        log_info "检测到无效状态，尝试修复"

        # 设置默认状态
        jq '.execution_info.status = "RECOVERING"' "$STATUS_FILE" > temp.json && mv temp.json "$STATUS_FILE"

        log_success "状态修复完成"
    fi

    # 检查任务一致性
    if [[ -n "$current_task" && "$current_task" != "null" ]]; then
        # 检查任务是否在tasks列表中
        local task_exists=$(jq -r ".tasks.\"$current_task\" // null" "$STATUS_FILE")
        if [[ "$task_exists" == "null" ]]; then
            log_warn "当前任务 $current_task 在任务列表中不存在，尝试重置"

            # 重置当前任务为null
            jq '.execution_info.current_task = null' "$STATUS_FILE" > temp.json && mv temp.json "$STATUS_FILE"

            log_success "当前任务已重置"
        fi
    fi

    return 0
}

# 任务完整性验证
verify_task_integrity() {
    local task_id="$1"

    if [[ -z "$task_id" ]]; then
        log_error "请指定任务ID"
        return 1
    fi

    log_info "验证任务 $task_id 的完整性"

    # 检查任务状态
    local task_status=$(jq -r ".tasks.\"$task_id\".status // null" "$STATUS_FILE" 2>/dev/null)
    if [[ "$task_status" == "null" ]]; then
        log_error "任务 $task_id 不存在或状态无效"
        return 1
    fi

    # 检查任务的输出文件
    local expected_files=$(jq -r ".tasks.\"$task_id\".expected_files[]? // empty" "$STATUS_FILE" 2>/dev/null)
    local missing_files=0

    for file in $expected_files; do
        if [[ ! -f "$file" ]]; then
            log_warn "预期输出文件缺失: $file"
            ((missing_files++))
        fi
    done

    if [[ $missing_files -gt 0 ]]; then
        log_info "任务 $task_id 有 $missing_files 个文件缺失，可能需要重新执行"
        return 1
    fi

    log_success "任务 $task_id 完整性验证通过"
    return 0
}

# 继续执行中断的任务
continue_interrupted_task() {
    local task_id="$1"

    if [[ -z "$task_id" ]]; then
        task_id=$(get_current_task)
        if [[ -z "$task_id" ]]; then
            log_error "无法确定当前任务，请手动指定任务ID"
            return 1
        fi
    fi

    log_info "继续执行中断的任务: $task_id"

    # 验证任务完整性
    if ! verify_task_integrity "$task_id"; then
        log_info "任务完整性验证失败，准备重新执行"

        # 重置任务状态
        jq --arg task_id "$task_id" '
            .tasks[$task_id].status = "PENDING" |
            .tasks[$task_id].start_time = null |
            .tasks[$task_id].end_time = null |
            .execution_info.current_task = $task_id |
            .execution_info.status = "RECOVERING"
        ' "$STATUS_FILE" > temp.json && mv temp.json "$STATUS_FILE"

        log_info "任务 $task_id 状态已重置，可以重新执行"
    else
        log_info "任务 $task_id 完整性验证通过，继续下一个任务"

        # 标记当前任务为完成
        jq --arg task_id "$task_id" '
            .tasks[$task_id].status = "COMPLETED" |
            .tasks[$task_id].end_time = now |
            .execution_info.completed_tasks += 1 |
            .execution_info.status = "CONTINUING"
        ' "$STATUS_FILE" > temp.json && mv temp.json "$STATUS_FILE"
    fi

    # 生成恢复报告
    generate_recovery_report "$task_id" "task_continuation"

    return 0
}

# 生成恢复报告
generate_recovery_report() {
    local task_id="$1"
    local recovery_type="$2"

    local report_file="RECOVERY_REPORT_$(date +%Y%m%d_%H%M%S).md"

    cat > "$report_file" << EOF
# 任务恢复报告

**恢复时间**: $(date '+%Y-%m-%d %H:%M:%S')
**任务ID**: $task_id
**恢复类型**: $recovery_type

## 恢复前状态

- **执行状态**: $(get_execution_status)
- **当前任务**: $(get_current_task)
- **已完成任务**: $(jq -r '.execution_info.completed_tasks // 0' "$STATUS_FILE")
- **失败任务**: $(jq -r '.execution_info.failed_tasks // 0' "$STATUS_FILE")

## 恢复操作

EOF

    case "$recovery_type" in
        "smart_recovery")
            cat >> "$report_file" << EOF
1. 检查状态文件完整性
2. 修复无效状态信息
3. 验证任务一致性
4. 重置必要的状态字段

EOF
            ;;
        "task_continuation")
            cat >> "$report_file" << EOF
1. 验证任务输出完整性
2. 检查预期文件是否存在
3. 根据验证结果决定继续或重新执行
4. 更新任务状态和进度

EOF
            ;;
        "manual_recovery")
            cat >> "$report_file" << EOF
1. 用户手动指定恢复点
2. 从指定恢复点恢复状态
3. 验证恢复后的状态一致性
4. 准备继续执行

EOF
            ;;
    esac

    cat >> "$report_file" << EOF
## 恢复后状态

- **执行状态**: $(get_execution_status)
- **当前任务**: $(get_current_task)
- **总任务数**: $(jq -r '.execution_info.total_tasks // 0' "$STATUS_FILE")
- **进度百分比**: $(jq -r '.execution_info.progress_percentage // 0' "$STATUS_FILE")

## 下一步操作

建议执行以下命令继续任务执行:

\`\`\`bash
claude "任务恢复完成，当前任务: $(get_current_task)。请检查执行状态，然后继续执行任务。如果发现问题，请报告并等待进一步指示。"
\`\`\`

EOF

    log_recovery "恢复报告已生成: $report_file"
}

# 交互式恢复模式
interactive_recovery() {
    log_info "启动交互式恢复模式"

    echo -e "${CYAN}=== Claude Code 任务恢复工具 ===${NC}"
    echo ""

    # 显示当前状态
    local status=$(get_execution_status)
    local current_task=$(get_current_task)

    echo -e "${BLUE}当前执行状态:${NC} $status"
    echo -e "${BLUE}当前任务:${NC} $current_task"
    echo ""

    # 显示恢复选项
    echo -e "${YELLOW}请选择恢复操作:${NC}"
    echo "1. 智能状态恢复 (自动修复状态问题)"
    echo "2. 继续中断的任务"
    echo "3. 从恢复点恢复"
    echo "4. 验证任务完整性"
    echo "5. 生成恢复报告"
    echo "0. 退出"

    read -p "请输入选项 (0-5): " choice

    case $choice in
        1)
            smart_state_recovery
            ;;
        2)
            read -p "请输入任务ID (留空使用当前任务): " task_id
            continue_interrupted_task "$task_id"
            ;;
        3)
            list_recovery_points
            read -p "请输入恢复点ID: " recovery_point
            recover_from_point "$recovery_point"
            ;;
        4)
            read -p "请输入任务ID: " task_id
            verify_task_integrity "$task_id"
            ;;
        5)
            read -p "请输入任务ID (可选): " task_id
            generate_recovery_report "$task_id" "manual_recovery"
            ;;
        0)
            log_info "退出交互式恢复模式"
            ;;
        *)
            log_error "无效选项: $choice"
            ;;
    esac
}

# 自动恢复模式
auto_recovery() {
    log_info "启动自动恢复模式"

    # 1. 智能状态恢复
    if ! smart_state_recovery; then
        log_error "智能状态恢复失败"
        return 1
    fi

    # 2. 检查当前任务状态
    local current_task=$(get_current_task)
    if [[ -n "$current_task" ]]; then
        log_info "检测到当前任务: $current_task"

        # 3. 尝试继续任务
        if ! continue_interrupted_task "$current_task"; then
            log_error "继续任务失败"
            return 1
        fi
    fi

    log_success "自动恢复完成"
    return 0
}

# 清理旧的恢复点
cleanup_old_recovery_points() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        return 0
    fi

    local recovery_count=$(ls "$BACKUP_DIR" | grep recovery_point | wc -l)

    if [[ $recovery_count -gt $MAX_BACKUPS ]]; then
        log_info "清理旧恢复点，保留最新 $MAX_BACKUPS 个"

        # 删除最旧的恢复点
        ls -t "$BACKUP_DIR" | grep recovery_point | tail -n +$((MAX_BACKUPS + 1)) | xargs -I {} rm -f "$BACKUP_DIR/{}"

        log_success "清理完成"
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
任务恢复器 v1.0

用法: $0 [选项] [参数]

选项:
    --auto                     自动恢复模式
    --interactive              交互式恢复模式
    --smart-recovery           智能状态恢复
    --continue [task_id]       继续执行中断的任务
    --recover-point <point_id> 从指定恢复点恢复
    --verify <task_id>         验证任务完整性
    --list-points              列出可用恢复点
    --report [task_id]         生成恢复报告
    --cleanup                  清理旧恢复点
    --help                     显示此帮助信息

示例:
    $0 --auto                  # 自动恢复
    $0 --interactive           # 交互式恢复
    $0 --continue T001-002     # 继续指定任务
    $0 --recover-point rp_20251006_120000 # 从恢复点恢复
    $0 --verify T001-002       # 验证任务完整性
    $0 --list-points           # 列出恢复点

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
    mkdir -p "$BACKUP_DIR" BACKUPS LOGS REPORTS

    # 初始化恢复日志
    echo "# 任务恢复日志" > "$RECOVERY_LOG_FILE"
    echo "启动时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$RECOVERY_LOG_FILE"
    echo "" >> "$RECOVERY_LOG_FILE"

    case "$1" in
        "--auto")
            auto_recovery
            ;;
        "--interactive")
            interactive_recovery
            ;;
        "--smart-recovery")
            smart_state_recovery
            ;;
        "--continue")
            continue_interrupted_task "$2"
            ;;
        "--recover-point")
            recover_from_point "$2"
            ;;
        "--verify")
            verify_task_integrity "$2"
            ;;
        "--list-points")
            list_recovery_points
            ;;
        "--report")
            generate_recovery_report "$2" "manual_recovery"
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