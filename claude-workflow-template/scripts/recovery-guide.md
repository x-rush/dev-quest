# 恢复指南

> **使用说明**: 当Claude Code执行中断或出现异常时，如何恢复执行状态。

## 🔍 中断类型识别

### 常见中断情况
1. **网络连接问题** - Claude Code API连接中断
2. **系统资源不足** - 内存或磁盘空间耗尽
3. **会话超时** - 长时间无操作导致会话失效
4. **程序异常** - Claude Code内部错误
5. **手动中断** - 用户主动停止执行

### 判断中断类型
```bash
# 检查系统状态
echo "=== 系统状态检查 ==="
echo "磁盘使用: $(df -h . | tail -1)"
echo "内存使用: $(free -h | grep Mem)"
echo "网络连接: $(ping -c 1 google.com &>/dev/null && echo '正常' || echo '异常')"

# 检查执行状态
if [ -f "EXECUTION_STATUS.json" ]; then
    echo "执行状态文件存在"
    echo "最后更新: $(stat -c %y EXECUTION_STATUS.json)"
else
    echo "执行状态文件不存在"
fi
```

## 🔄 恢复执行步骤

### 步骤1: 环境检查
```bash
# 1. 检查项目目录
pwd
ls -la *.md *.json 2>/dev/null || echo "无状态文件"

# 2. 检查Claude Code可用性
claude --version 2>/dev/null && echo "Claude Code正常" || echo "Claude Code异常"

# 3. 检查权限
test -w . && echo "写入权限正常" || echo "写入权限异常"
```

### 步骤2: 状态分析
```bash
# 分析执行状态
analyze_status() {
    if [ -f "EXECUTION_STATUS.json" ]; then
        echo "=== 执行状态分析 ==="
        current_task=$(jq -r '.execution_info.current_task' EXECUTION_STATUS.json 2>/dev/null)
        completed=$(jq -r '.execution_info.completed_tasks' EXECUTION_STATUS.json 2>/dev/null)
        total=$(jq -r '.execution_info.total_tasks' EXECUTION_STATUS.json 2>/dev/null)

        echo "当前任务: $current_task"
        echo "已完成: $completed/$total"

        # 检查未完成的任务
        echo "=== 未完成任务 ==="
        jq -r 'to_entries[] | select(.value.status != "COMPLETED") | "\(.key): \(.value.status)"' EXECUTION_STATUS.json
    else
        echo "无执行状态，需要重新开始"
    fi
}
```

### 步骤3: 选择恢复策略
```bash
# 根据状态选择恢复方式
choose_recovery_strategy() {
    if [ -f "EXECUTION_STATUS.json" ]; then
        completed=$(jq -r '.execution_info.completed_tasks' EXECUTION_STATUS.json 2>/dev/null)
        total=$(jq -r '.execution_info.total_tasks' EXECUTION_STATUS.json 2>/dev/null)

        if [ "$completed" = "null" ] || [ "$completed" = "0" ]; then
            echo "建议: 重新开始执行"
            return 1
        else
            echo "建议: 从中断点继续执行"
            return 0
        fi
    else
        echo "建议: 重新开始执行"
        return 1
    fi
}
```

## 🛠️ 恢复命令模板

### 从中断点继续
```bash
# 方案1: 继续执行
claude "根据 EXECUTION_STATUS.json 从中断点继续执行，当前状态：$(cat EXECUTION_STATUS.json | jq '.execution_info')"

# 方案2: 从特定任务继续
claude "从任务 [任务ID] 继续执行，跳过已完成的任务"

# 方案3: 重新执行当前任务
claude "重新执行当前任务 [任务ID]，修复之前可能的问题"
```

### 重新开始执行
```bash
# 方案1: 完全重新开始
claude "重新开始执行项目任务，根据 PROJECT_PLAN.md 和 TASK_DEFINITIONS.md"

# 方案2: 保留进度，重新开始剩余任务
claude "保留已完成的任务进度，重新开始执行剩余的任务"
```

## 🔧 问题修复

### 修复状态文件损坏
```bash
# 备份损坏的状态文件
if [ -f "EXECUTION_STATUS.json" ]; then
    cp EXECUTION_STATUS.json "EXECUTION_STATUS.backup.$(date +%H%M%S).json"
fi

# 尝试修复JSON格式
fix_json() {
    local file="$1"
    python3 -c "
import json
import sys
try:
    with open('$file', 'r') as f:
        data = json.load(f)
    with open('$file', 'w') as f:
        json.dump(data, f, indent=2)
    print('JSON格式修复成功')
except Exception as e:
    print(f'JSON修复失败: {e}')
"
}

# 尝试修复
fix_json "EXECUTION_STATUS.json"
```

### 修复文件权限问题
```bash
# 修复文件权限
fix_permissions() {
    # 确保当前目录可写
    chmod 755 .

    # 修复已生成文件的权限
    find . -name "*.md" -exec chmod 644 {} \;
    find . -name "*.json" -exec chmod 644 {} \;

    echo "权限修复完成"
}
```

### 修复缺失文件
```bash
# 检查并恢复缺失的模板文件
restore_missing_files() {
    local required_files=(
        "PROJECT_PLAN.md"
        "TASK_DEFINITIONS.md"
        "QUALITY_STANDARDS.md"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "缺失文件: $file"
            echo "请从模板重新生成或手动创建"
        fi
    done
}
```

## 📋 恢复检查清单

### 恢复前检查
```markdown
## 恢复前检查清单

### 环境检查
- [ ] 项目目录存在且可访问
- [ ] Claude Code CLI正常工作
- [ ] 网络连接稳定
- [ ] 磁盘空间充足 (>1GB)
- [ ] 文件权限正确

### 状态检查
- [ ] 执行状态文件完整
- [ ] JSON格式正确
- [ ] 任务状态逻辑一致
- [ ] 进度信息准确

### 文件检查
- [ ] 项目规划文件存在
- [ ] 任务定义文件存在
- [ ] 质量标准文件存在
- [ ] 已生成文件完整
```

### 恢复后验证
```markdown
## 恢复后验证清单

### 执行验证
- [ ] Claude Code成功启动
- [ ] 能够读取状态文件
- [ ] 任务执行恢复正常
- [ ] 状态更新正常

### 内容验证
- [ ] 新生成内容质量正常
- [ ] 文件格式符合标准
- [ ] 链接和引用正确
- [ ] 代码示例可执行

### 系统验证
- [ ] 系统资源使用正常
- [ ] 监控机制工作
- [ ] 错误处理正常
- [ ] 日志记录完整
```

## 🚨 紧急恢复方案

### 完全恢复脚本
```bash
#!/bin/bash
# emergency_recovery.sh - 紧急恢复脚本

echo "🚨 开始紧急恢复..."

# 1. 环境检查
echo "检查环境..."
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code未找到"
    exit 1
fi

# 2. 备份当前状态
echo "备份当前状态..."
backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
cp -r *.md *.json "$backup_dir/" 2>/dev/null

# 3. 尝试恢复执行
echo "尝试恢复执行..."
if [ -f "EXECUTION_STATUS.json" ]; then
    echo "发现执行状态，尝试继续..."
    claude "执行紧急恢复：根据备份状态继续执行项目任务"
else
    echo "无执行状态，重新开始..."
    claude "执行紧急恢复：重新开始项目任务执行"
fi

echo "🎯 紧急恢复完成"
```

### 手动恢复步骤
```markdown
## 手动恢复流程

### 第一步: 环境准备
1. 确认Claude Code CLI可用
2. 检查项目目录权限
3. 验证网络连接
4. 清理临时文件

### 第二步: 状态评估
1. 检查EXECUTION_STATUS.json是否存在
2. 分析执行进度和任务状态
3. 识别失败原因
4. 确定恢复策略

### 第三步: 执行恢复
1. 选择合适的恢复命令
2. 监控恢复执行过程
3. 验证恢复结果
4. 更新状态记录

### 第四步: 验证完成
1. 检查任务执行状态
2. 验证生成内容质量
3. 确认系统正常运行
4. 记录恢复过程
```

## 📞 获取帮助

### 常见问题解决
```bash
# 问题1: Claude Code无法启动
solution_claude_down() {
    echo "解决方案:"
    echo "1. 检查Claude Code安装: claude --version"
    echo "2. 重新安装Claude Code"
    echo "3. 检查系统环境变量"
    echo "4. 重启系统"
}

# 问题2: 状态文件损坏
solution_status_corrupted() {
    echo "解决方案:"
    echo "1. 从备份恢复状态文件"
    echo "2. 重新生成执行状态"
    echo "3. 修复JSON格式错误"
    echo "4. 重新开始执行"
}

# 问题3: 权限问题
solution_permission_issues() {
    echo "解决方案:"
    echo "1. 检查文件权限: ls -la"
    echo "2. 修复权限: chmod 755 . && chmod 644 *.md *.json"
    echo "3. 检查磁盘空间: df -h"
    echo "4. 更改项目目录位置"
}
```

### 联系支持
```markdown
## 获取技术支持

如果自动恢复失败，可以：

1. **查看详细错误日志**
   - 检查ERROR_REPORT.md
   - 查看系统日志
   - 分析执行日志

2. **收集诊断信息**
   - 系统环境信息
   - 错误截图
   - 执行状态文件

3. **寻求帮助**
   - 项目issue系统
   - 技术支持渠道
   - 社区论坛
```

---

**重要提示**: 恢复执行前务必备份当前状态，避免数据丢失。如果反复出现中断问题，建议检查系统环境和网络稳定性。