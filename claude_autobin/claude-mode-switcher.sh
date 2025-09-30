#!/bin/bash

# Claude Code CLI 工作模式切换器
#
# 功能：在当前终端会话中快速切换Claude Code的工作模式
# 特点：
# - 一键切换：确认模式 ↔ 自动化模式
# - 会话隔离：只在当前终端会话生效
# - 无需配置：不修改系统配置，无后台进程
# - 完全控制：用户完全掌控工作模式
#
# 使用方法：
#   source claude-mode-switcher.sh    # 加载模式切换器
#   claude-auto                      # 切换到自动化模式
#   claude-confirm                   # 切换到确认模式
#   run-auto-claude <command>        # 直接运行自动化任务
#   claude-mode-help                 # 显示帮助信息

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 自动确认输入流
AUTO_CONFIRM_INPUT="y\nyes\ncontinue\nproceed\nyes\ncontinue\ny\nproceed\nyes"

# 检查是否已加载
if [[ "$CLAUDE_MODE_SWITCHER_LOADED" == "true" ]]; then
    echo -e "${YELLOW}⚠️  Claude模式切换器已经加载过了${NC}"
    return 0
fi

# 自动化模式
claude-auto() {
    # 设置自动化模式标志
    export CLAUDE_AUTO_MODE=true

    # 创建自动化包装函数
    claude() {
        echo -e "$AUTO_CONFIRM_INPUT" | command claude "$@"
    }

    export -f claude

    echo -e "${GREEN}✅ Claude Code 自动化模式已启用${NC}"
    echo -e "${BLUE}📝 现在所有Claude命令都将自动确认${NC}"
    echo -e "${YELLOW}💡 使用 'claude-confirm' 切换回确认模式${NC}"
}

# 确认模式
claude-confirm() {
    # 清除自动化模式标志
    unset CLAUDE_AUTO_MODE

    # 移除包装函数，恢复原始命令
    unset -f claude 2>/dev/null || true

    # 确保claude命令可用
    if ! command -v claude &> /dev/null; then
        echo -e "${RED}❌ Claude CLI 未找到，请确保已正确安装${NC}"
        return 1
    fi

    echo -e "${GREEN}✅ Claude Code 确认模式已启用${NC}"
    echo -e "${BLUE}📝 现在所有Claude命令都需要手动确认${NC}"
    echo -e "${YELLOW}💡 使用 'claude-auto' 切换到自动化模式${NC}"
}

# 直接运行自动化任务
run-auto-claude() {
    if [[ $# -eq 0 ]]; then
        echo -e "${RED}❌ 请指定要运行的Claude命令${NC}"
        echo -e "${YELLOW}用法: run-auto-claude <claude-command-and-args>${NC}"
        return 1
    fi

    echo -e "${BLUE}🚀 启动自动化Claude Code任务...${NC}"
    echo -e "${YELLOW}命令: claude $*${NC}"

    # 直接执行自动化任务
    echo -e "$AUTO_CONFIRM_INPUT" | command claude "$@"
}

# 显示当前模式
claude-mode-status() {
    if [[ "$CLAUDE_AUTO_MODE" == "true" ]]; then
        echo -e "${GREEN}当前模式: 自动化模式${NC}"
        echo -e "${BLUE}📝 Claude命令将自动确认${NC}"
    else
        echo -e "${YELLOW}当前模式: 确认模式${NC}"
        echo -e "${BLUE}📝 Claude命令需要手动确认${NC}"
    fi

    # 显示会话信息
    echo -e "${BLUE}🔧 会话PID: $$${NC}"
    echo -e "${BLUE}⏰ 加载时间: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
}

# 显示帮助信息
claude-mode-help() {
    echo -e "${BLUE}Claude Code CLI 模式切换器使用说明:${NC}"
    echo ""
    echo -e "${GREEN}命令列表:${NC}"
    echo -e "  ${YELLOW}claude-auto${NC}         - 启用自动化模式（长时任务）"
    echo -e "  ${YELLOW}claude-confirm${NC}      - 启用确认模式（短时任务）"
    echo -e "  ${YELLOW}claude-mode-status${NC}  - 显示当前模式状态"
    echo -e "  ${YELLOW}run-auto-claude${NC}     - 直接运行自动化任务"
    echo -e "  ${YELLOW}claude-mode-help${NC}    - 显示此帮助信息"
    echo ""
    echo -e "${BLUE}使用示例:${NC}"
    echo -e "  ${YELLOW}source claude-mode-switcher.sh${NC}     # 加载切换器"
    echo -e "  ${YELLOW}claude-auto${NC}                           # 启用自动化模式"
    echo -e "  ${YELLOW}claude long-task-command${NC}             # 自动执行长时任务"
    echo -e "  ${YELLOW}claude-confirm${NC}                        # 切换回确认模式"
    echo -e "  ${YELLOW}claude short-task-command${NC}            # 手动确认短时任务"
    echo -e "  ${YELLOW}run-auto-claude dev-quest-control.md${NC}  # 直接执行自动化任务"
    echo ""
    echo -e "${BLUE}特点:${NC}"
    echo -e "  ✅ 只在当前终端会话生效"
    echo -e "  ✅ 不修改系统配置"
    echo -e "  ✅ 无后台进程"
    echo -e "  ✅ 完全用户控制"
    echo -e "  ✅ 一键切换模式"
    echo ""
    echo -e "${YELLOW}注意:${NC}"
    echo -e "  - 每次新开终端会话都需要重新加载切换器"
    echo -e "  - 终端会话结束后所有设置自动清除"
    echo -e "  - 自动化模式请谨慎使用，确保任务正确性"
}

# 清理函数（会话结束时自动调用）
claude-mode-cleanup() {
    echo -e "${BLUE}🧹 正在清理Claude模式切换器...${NC}"
    unset CLAUDE_AUTO_MODE
    unset CLAUDE_MODE_SWITCHER_LOADED
    unset -f claude 2>/dev/null || true
    unset -f claude-auto
    unset -f claude-confirm
    unset -f claude-mode-status
    unset -f claude-mode-help
    unset -f run-auto-claude
    unset -f claude-mode-cleanup
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 注册清理函数
trap claude-mode-cleanup EXIT

# 标记已加载
export CLAUDE_MODE_SWITCHER_LOADED=true

# 默认启动确认模式
claude-confirm

# 显示欢迎信息
echo -e "${GREEN}🎉 Claude Code CLI 模式切换器已加载！${NC}"
echo -e "${BLUE}💡 使用 'claude-mode-help' 查看使用说明${NC}"
echo -e "${YELLOW}📝 当前模式: 确认模式（默认）${NC}"

# 设置快捷别名（可选）
alias auto='claude-auto'
alias confirm='claude-confirm'
alias status='claude-mode-status'
alias help='claude-mode-help'
alias run='run-auto-claude'

echo -e "${BLUE}🔧 快捷别名: auto, confirm, status, help, run${NC}"