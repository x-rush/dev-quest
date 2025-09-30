# Dev Quest 24小时不间断自动化操作指南

## 🎯 概述

本指南详细介绍如何使用Claude Code CLI模式切换器和Master Control系统实现24小时不间断的Dev Quest项目自动化执行。

## 📋 系统组件

### 已有基础设施
- **Claude模式切换器**: `~/.local/bin/claude-mode-switcher.sh`
- **主控制系统**: `CLAUDE_CODE_MASTER_CONTROL.md`
- **全局任务列表**: `GLOBAL_TODO_LIST_UPDATED.md`
- **任务状态文档**: `MASTER_CONTROL_README.md`

## 🚀 完整操作流程

### 步骤1: 启动自动化环境

```bash
# 1. 打开终端，导航到项目目录
cd /home/x_rush/project/www/dev-quest

# 2. 加载Claude模式切换器
source ~/.local/bin/claude-mode-switcher.sh

# 3. 查看可用命令（可选）
claude-mode-help

# 4. 检查当前模式（应该显示确认模式）
claude-mode-status
```

### 步骤2: 启用自动化模式

```bash
# 5. 切换到自动化模式
claude-auto

# 6. 验证模式切换成功
claude-mode-status
# 应该显示：当前模式: 自动化模式
```

### 步骤3: 加载项目上下文

```bash
# 7. 查看当前项目状态
ls -la

# 8. 检查最新的任务进度
cat GLOBAL_TODO_LIST_UPDATED.md | head -20

# 9. 查看主控制系统状态
cat MASTER_CONTROL_README.md | head -30
```

### 步骤4: 启动24小时自动化执行

```bash
# 10. 启动Claude Code并加载主控制指令
claude "根据CLAUDE_CODE_MASTER_CONTROL.md开始执行24小时不间断的Dev Quest项目自动化任务"

# 或者更具体的指令：
claude "根据GLOBAL_TODO_LIST_UPDATED.md中的任务队列，从任务2.1.1开始执行：为01-go-backend创建标准化目录结构"
```

### 步骤5: 监控执行进度

```bash
# 在另一个终端窗口中监控进度（新终端需要重新加载切换器）

# 终端A（主执行终端）:
# 保持开启，Claude会自动执行所有任务

# 终端B（监控终端）:
cd /home/x_rush/project/www/dev-quest
source ~/.local/bin/claude-mode-switcher.sh

# 检查任务状态
cat MASTER_CONTROL_README.md | grep -A 10 "任务队列"

# 查看文件变化
watch -n 5 'find . -name "*.md" -newer GLOBAL_TODO_LIST_UPDATED.md | head -10'

# 检查git状态（如果有git仓库）
git status
git log --oneline -5
```

## 🔧 详细操作说明

### 自动化模式特性

**自动确认的内容：**
- 文件编辑确认
- 工具使用确认
- 计划执行确认
- 继续执行确认

**自动确认序列：**
```bash
y          # 确认文件编辑
yes        # 确认工具使用
continue   # 继续执行
proceed    # 确认计划执行
yes        # 再次确认
continue   # 继续下一步
y          # 简单确认
proceed    # 最终确认
yes        # 开始执行
```

### 任务执行预期流程

1. **任务开始**: Claude读取GLOBAL_TODO_LIST_UPDATED.md
2. **状态更新**: 使用TodoWrite更新任务为"in_progress"
3. **执行任务**: 自动确认并执行具体操作
4. **质量检查**: 自我验证完成质量
5. **状态更新**: 使用TodoWrite更新任务为"completed"
6. **下一个任务**: 自动开始队列中的下一个任务

### 监控命令

```bash
# 实时监控文件变化
watch -n 3 'ls -la --time-style=full-iso'

# 监控特定目录变化
watch -n 5 'tree 01-go-backend 2>/dev/null || echo "目录尚未创建"'

# 检查任务状态变化
grep -A 5 -B 5 "in_progress\|completed" MASTER_CONTROL_README.md

# 查看最新修改的文件
find . -name "*.md" -mmin -10 | sort
```

## ⚠️ 重要注意事项

### 执行前检查清单

- [ ] 确认有足够的磁盘空间
- [ ] 确认网络连接稳定
- [ ] 确认电源稳定（笔记本建议连接电源）
- [ ] 关闭终端休眠设置
- [ ] 备份重要数据（可选但推荐）

### 执行期间建议

1. **保持终端开启**: 自动化任务执行期间不要关闭主终端
2. **定期检查**: 每隔一段时间检查执行进度
3. **监控资源**: 关注系统资源使用情况
4. **网络稳定**: 确保网络连接稳定，避免中断

### 异常处理

**如果任务意外中断：**
```bash
# 重新加载环境
source ~/.local/bin/claude-mode-switcher.sh
claude-auto

# 检查中断时的状态
cat MASTER_CONTROL_README.md | grep -A 15 "任务队列"

# 继续执行
claude "从上次中断的地方继续执行Dev Quest任务"
```

**如果出现错误：**
```bash
# 切换到确认模式进行手动处理
claude-confirm

# 处理完错误后切换回自动化模式
claude-auto
claude "继续执行Dev Quest自动化任务"
```

## 🎯 预期执行效果

### 短期目标（几小时内）
- 完成01-go-backend的标准化目录结构
- 开始02-nextjs-frontend的目录结构完善
- 执行03-12模块的详细文档生成

### 中期目标（24-48小时）
- 完成所有模块的目录结构创建
- 生成大量详细的技术文档
- 建立完整的知识体系

### 长期目标（持续运行）
- 自动维护和更新文档
- 响应技术发展趋势
- 建立自我完善的学习体系

## 📊 成功指标

### 执行成功标志
- ✅ 任务状态从"pending"变为"in_progress"再到"completed"
- ✅ 新的目录和文件按预期创建
- ✅ 文档内容质量符合标准
- ✅ 自动执行过程无需人工干预

### 质量检查标准
- 📄 文档结构完整性和一致性
- 🔧 技术内容的准确性和前沿性
- 📚 学习路径的逻辑性和实用性
- 🎯 与整体项目架构的协调性

## 🚀 立即开始

```bash
# 复制以下命令序列到终端执行：

cd /home/x_rush/project/www/dev-quest
source ~/.local/bin/claude-mode-switcher.sh
claude-auto
claude "根据CLAUDE_CODE_MASTER_CONTROL.md开始执行24小时不间断的Dev Quest项目自动化任务"
```

---

**祝你的Dev Quest项目24小时自动化执行成功！** 🎉

*最后更新: 2025-09-30*