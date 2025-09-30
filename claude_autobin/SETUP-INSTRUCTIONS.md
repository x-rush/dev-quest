# Claude Code CLI 模式切换器 - 安装和使用说明

## 📁 文件位置

Claude模式切换器文件已移动到：
- 脚本：`~/.local/bin/claude-mode-switcher.sh`
- 说明：`~/.local/bin/CLAUDE-MODE-USAGE.md`

## 🚀 快速使用

### 方法1：直接加载（推荐）
```bash
# 加载切换器
source ~/.local/bin/claude-mode-switcher.sh

# 查看帮助
claude-mode-help

# 切换模式
claude-auto    # 自动化模式
claude-confirm # 确认模式
```

### 方法2：添加到bashrc（已配置）
你的 `~/.bashrc` 已添加：
```bash
export PATH="$HOME/.local/bin:$PATH"
alias claude-mode="source ~/.local/bin/claude-mode-switcher.sh"
```

使用方法：
```bash
# 重新加载bashrc（或重新开终端）
source ~/.bashrc

# 使用别名加载切换器
claude-mode

# 现在可以使用所有命令
claude-auto
claude-confirm
claude-mode-help
```

## 🔧 故障排除

如果别名不工作，请使用方法1直接加载。

## 📖 详细说明
查看完整使用说明：`~/.local/bin/CLAUDE-MODE-USAGE.md`