# 快速启动指南

> **目标**: 5分钟内启动Claude Code长时间任务的完整工作流

## 🚀 超快速启动 (3分钟)

### 1️⃣ 环境准备 (30秒)
```bash
# 复制所有必要文件
cp -r claude-workflow-template/template-docs/ ./
cp -r claude-workflow-template/scripts/ ./

# 创建目录和设置权限
mkdir -p STATE_BACKUPS ERROR_REPORTS QUALITY_REPORTS logs
chmod +x scripts/*.sh
```

### 2️⃣ 启动任务讨论 (2分钟)
```bash
# 启动Claude Code开始深度讨论
claude "我需要执行一个长时间任务(超过24小时)，请按照 TASK_DISCUSSION_TEMPLATE.md 开始详细的任务讨论阶段"
```

### 3️⃣ 启动执行和监控 (30秒)
```bash
# 终端1: 启动任务执行
claude "我确认同意开始执行，请严格按照 EXECUTION_PLAN_CONFIRMATION.md 开始任务执行"

# 终端2: 启动监控 (推荐)
./scripts/execution-monitor.sh --interface
```

## 📋 完整检查清单

### ✅ 启动前必做检查
- [ ] 已复制所有模板文件到项目根目录
- [ ] 已设置脚本执行权限 (`chmod +x scripts/*.sh`)
- [ ] 已创建必要目录 (`STATE_BACKUPS`, `ERROR_REPORTS`, etc.)
- [ ] 已完成深度任务讨论 (1-3小时)
- [ ] 已生成并确认执行计划确认书
- [ ] 已执行26项执行前检查
- [ ] 用户已明确确认"同意开始执行"

### ✅ 执行时必做操作
- [ ] 启动任务执行命令
- [ ] 启动监控系统 (新终端)
- [ ] 定期检查执行进度
- [ ] 必要时使用恢复工具

## 🛠️ 常用命令速查

### 监控命令
```bash
# 实时监控界面
./scripts/execution-monitor.sh --interface

# 后台监控
./scripts/execution-monitor.sh --background &

# 生成监控仪表板
./scripts/execution-monitor.sh --dashboard

# 一次性状态检查
./scripts/execution-monitor.sh --check
```

### 恢复命令
```bash
# 交互式恢复 (最常用)
./scripts/task-recovery.sh --interactive

# 自动恢复
./scripts/task-recovery.sh --auto

# 继续中断的任务
./scripts/task-recovery.sh --continue [task_id]

# 从恢复点恢复
./scripts/task-recovery.sh --recover-point [point_id]

# 列出可用恢复点
./scripts/task-recovery.sh --list-points
```

### 重试命令
```bash
# 手动重试任务
./scripts/smart-retry-handler.sh --retry [task_id]

# 查看重试统计
./scripts/smart-retry-handler.sh --stats

# 启动重试监控
./scripts/smart-retry-handler.sh --monitor
```

### 健康检查命令
```bash
# 执行健康检查
./scripts/task-health-checker.sh --check

# 启动健康监控
./scripts/task-health-checker.sh --monitor

# 生成健康报告
./scripts/task-health-checker.sh --report
```

## 📊 监控文件说明

执行过程中会生成以下关键文件：

### 核心状态文件
- **`EXECUTION_STATUS.json`** - 实时执行状态 (最重要)
- **`EXECUTION_LOG.md`** - 详细执行日志
- **`ERROR_REPORT.md`** - 错误报告和分析

### 监控日志文件
- **`MONITOR_LOG.md`** - 监控系统日志
- **`ALERT_HISTORY.md`** - 告警历史记录
- **`MONITOR_DASHBOARD.md`** - 监控仪表板

### 恢复相关文件
- **`RECOVERY_POINTS/`** - 恢复点目录
- **`RETRY_LOG.md`** - 重试操作日志

## ⚠️ 常见问题快速解决

### 问题1: 监控界面无法启动
```bash
# 检查脚本权限
ls -la scripts/execution-monitor.sh

# 如果没有执行权限
chmod +x scripts/execution-monitor.sh

# 检查依赖工具
which jq
```

### 问题2: 任务卡住不动
```bash
# 1. 检查任务状态
cat EXECUTION_STATUS.json | jq '.execution_info'

# 2. 执行健康检查
./scripts/task-health-checker.sh --check

# 3. 尝试智能恢复
./scripts/task-recovery.sh --auto
```

### 问题3: API错误频繁
```bash
# 1. 查看重试统计
./scripts/smart-retry-handler.sh --stats

# 2. 检查网络状态
./scripts/execution-monitor.sh --check

# 3. 手动重试失败任务
./scripts/smart-retry-handler.sh --retry [task_id]
```

### 问题4: 需要暂停任务
```bash
# 1. 创建手动恢复点
./scripts/task-recovery.sh --list-points

# 2. 记录当前状态
cp EXECUTION_STATUS.json backup_pause_$(date +%Y%m%d_%H%M%S).json

# 3. 停止Claude Code进程
# (根据你的启动方式停止)
```

## 🎯 执行状态解读

### EXECUTION_STATUS.json 关键字段
```json
{
  "execution_info": {
    "status": "RUNNING",          // 当前状态
    "current_task": "T003-002",  // 当前任务
    "progress_percentage": 45,    // 完成百分比
    "start_time": "2025-10-06T10:00:00Z"
  },
  "retry_info": {
    "total_retries": 2,          // 总重试次数
    "task_retries": {            // 各任务重试次数
      "T002-001": 1
    }
  }
}
```

### 状态说明
- **READY_TO_START**: 准备开始
- **RUNNING**: 正在执行
- **PAUSED**: 已暂停
- **COMPLETED**: 已完成
- **FAILED**: 执行失败
- **RECOVERING**: 正在恢复

## 📱 移动端监控

### 快速状态查看
```bash
# 移动端友好的状态显示
cat EXECUTION_STATUS.json | jq -r '
  "状态: " + .execution_info.status + "\n" +
  "进度: " + (.execution_info.progress_percentage|tostring) + "%\n" +
  "当前: " + .execution_info.current_task + "\n" +
  "已完成: " + (.execution_info.completed_tasks|tostring) + "/" + (.execution_info.total_tasks|tostring)
'
```

### 简化监控脚本
```bash
# 创建简单监控脚本
echo '#!/bin/bash
echo "Claude Code 任务状态 - $(date)"
echo "=============================="
if [ -f "EXECUTION_STATUS.json" ]; then
    cat EXECUTION_STATUS.json | jq -r '
        "状态: " + .execution_info.status + "\n" +
        "进度: " + (.execution_info.progress_percentage|tostring) + "%\n" +
        "当前: " + .execution_info.current_task
    '
else
    echo "状态文件不存在"
fi
' > quick_status.sh && chmod +x quick_status.sh

# 使用
./quick_status.sh
```

## 🔧 高级技巧

### 1. 并行监控多个项目
```bash
# 在不同终端监控不同项目
# 终端1: cd project1 && ./scripts/execution-monitor.sh --interface
# 终端2: cd project2 && ./scripts/execution-monitor.sh --interface
```

### 2. 自定义监控间隔
```bash
# 修改监控间隔 (编辑脚本)
MONITOR_INTERVAL=30  # 30秒检查一次
```

### 3. 设置告警阈值
```bash
# 在监控脚本中自定义阈值
CPU_THRESHOLD=80        # CPU使用率告警阈值
MEMORY_THRESHOLD=85     # 内存使用率告警阈值
TIMEOUT_THRESHOLD=1800  # 任务超时阈值(秒)
```

---

**💡 提示**:
- 首次使用建议先看 `examples/` 中的示例
- 遇到问题时优先使用 `./scripts/task-recovery.sh --interactive`
- 保持监控系统运行，及时发现和处理异常
- 定期备份重要的状态文件