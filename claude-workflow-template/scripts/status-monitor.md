# 状态监控指南

> **使用说明**: 在Claude Code执行自动化任务过程中，如何实时监控状态和进度。

## 🔍 监控方法概览

### 基础监控命令
```bash
# 1. 查看当前执行状态
cat EXECUTION_STATUS.json | jq '.execution_info'

# 2. 查看实时执行日志
tail -f EXECUTION_LOG.md

# 3. 监控文件变化
watch -n 5 'find . -name "*.md" -mmin -10 | head -5'

# 4. 查看错误报告
tail -f ERROR_REPORT.md
```

### 进度统计命令
```bash
# 总体进度百分比
grep -o '"progress_percentage": [0-9]*' EXECUTION_STATUS.json

# 各状态任务数量
echo "已完成: $(grep -c '"status": "COMPLETED"' EXECUTION_STATUS.json)"
echo "进行中: $(grep -c '"status": "IN_PROGRESS"' EXECUTION_STATUS.json)"
echo "失败: $(grep -c '"status": "FAILED"' EXECUTION_STATUS.json)"

# 质量评分
grep '"quality_score"' EXECUTION_STATUS.json
```

## 📊 状态文件解读

### EXECUTION_STATUS.json 结构
```json
{
  "execution_info": {
    "start_time": "2025-10-04T10:00:00Z",
    "current_task": "T002-005",
    "total_tasks": 50,
    "completed_tasks": 15,
    "failed_tasks": 2,
    "blocked_tasks": 1,
    "progress_percentage": 30
  },
  "current_performance": {
    "tasks_per_hour": 12.5,
    "average_duration": 240,
    "success_rate": 0.95
  },
  "quality_metrics": {
    "overall_score": 8.7,
    "validation_pass_rate": 0.94
  }
}
```

### 任务状态含义
- **PENDING**: 等待执行
- **IN_PROGRESS**: 正在执行
- **COMPLETED**: 已完成
- **FAILED**: 执行失败
- **BLOCKED**: 被阻塞
- **VALIDATING**: 验证中
- **NEEDS_REVIEW**: 需要人工检查

## ⚡ 实时监控面板

### 创建监控脚本
```bash
#!/bin/bash
# monitor.sh - 实时监控脚本

clear
echo "🚀 Claude Code 执行监控面板"
echo "=================================="

while true; do
    clear
    echo "🕐 更新时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=================================="

    # 基础信息
    if [ -f "EXECUTION_STATUS.json" ]; then
        echo "📊 执行状态:"
        start_time=$(jq -r '.execution_info.start_time' EXECUTION_STATUS.json)
        current_task=$(jq -r '.execution_info.current_task' EXECUTION_STATUS.json)
        total_tasks=$(jq -r '.execution_info.total_tasks' EXECUTION_STATUS.json)
        completed=$(jq -r '.execution_info.completed_tasks' EXECUTION_STATUS.json)

        echo "  开始时间: $start_time"
        echo "  当前任务: $current_task"
        echo "  进度: $completed/$total_tasks"

        # 计算进度百分比
        if [ "$total_tasks" != "null" ] && [ "$completed" != "null" ]; then
            progress=$((completed * 100 / total_tasks))
            echo "  完成度: ${progress}%"
        fi
    else
        echo "❌ 执行状态文件不存在"
    fi

    echo ""
    echo "📈 最近的活动 (最后5条):"
    tail -5 EXECUTION_LOG.md 2>/dev/null || echo "暂无日志"

    echo ""
    echo "按 Ctrl+C 退出监控"
    sleep 10
done
```

### 使用监控脚本
```bash
# 保存监控脚本
chmod +x monitor.sh

# 启动监控
./monitor.sh
```

## 🚨 异常状态检测

### 检测异常情况
```bash
# 检测长时间无响应
check_long_running_task() {
    current_task=$(jq -r '.execution_info.current_task' EXECUTION_STATUS.json)
    task_start=$(jq -r ".tasks.\"$current_task\".start_time" EXECUTION_STATUS.json)

    if [ "$task_start" != "null" ]; then
        start_seconds=$(date -d "$task_start" +%s)
        current_seconds=$(date +%s)
        duration=$((current_seconds - start_seconds))

        # 如果任务运行超过30分钟，发出警告
        if [ $duration -gt 1800 ]; then
            echo "⚠️ 警告: 任务 $current_task 已运行 $((duration/60)) 分钟"
        fi
    fi
}

# 检测失败率过高
check_failure_rate() {
    total_tasks=$(jq -r '.execution_info.total_tasks' EXECUTION_STATUS.json)
    failed_tasks=$(jq -r '.execution_info.failed_tasks' EXECUTION_STATUS.json)

    if [ "$total_tasks" != "null" ] && [ "$failed_tasks" != "null" ]; then
        failure_rate=$((failed_tasks * 100 / total_tasks))

        if [ $failure_rate -gt 10 ]; then
            echo "❌ 错误: 失败率过高 (${failure_rate}%)"
        fi
    fi
}
```

### 自动告警机制
```bash
# 创建告警脚本
#!/bin/bash
# alert.sh - 异常告警脚本

send_alert() {
    local message="$1"
    local severity="$2"  # INFO, WARNING, ERROR

    echo "[$severity] $message"

    # 可以添加其他告警方式，如:
    # - 发送邮件
    # - 发送Slack通知
    # - 发送微信通知
    # - 桌面通知
}

check_execution_health() {
    # 检查执行状态文件是否存在
    if [ ! -f "EXECUTION_STATUS.json" ]; then
        send_alert "执行状态文件不存在" "ERROR"
        return
    fi

    # 检查是否长时间无更新
    last_update=$(stat -c %Y EXECUTION_STATUS.json)
    current_time=$(date +%s)
    age=$((current_time - last_update))

    if [ $age -gt 300 ]; then  # 5分钟无更新
        send_alert "执行状态超过5分钟未更新" "WARNING"
    fi

    # 检查失败率
    total_tasks=$(jq -r '.execution_info.total_tasks' EXECUTION_STATUS.json 2>/dev/null)
    failed_tasks=$(jq -r '.execution_info.failed_tasks' EXECUTION_STATUS.json 2>/dev/null)

    if [ "$total_tasks" != "null" ] && [ "$failed_tasks" != "null" ] && [ "$total_tasks" -gt 0 ]; then
        failure_rate=$((failed_tasks * 100 / total_tasks))

        if [ $failure_rate -gt 20 ]; then
            send_alert "失败率过高: ${failure_rate}%" "ERROR"
        fi
    fi
}

# 每2分钟检查一次
while true; do
    check_execution_health
    sleep 120
done
```

## 📋 质量监控

### 质量指标追踪
```bash
# 实时质量评分
monitor_quality() {
    if [ -f "EXECUTION_STATUS.json" ]; then
        quality_score=$(jq -r '.quality_metrics.overall_score' EXECUTION_STATUS.json)
        pass_rate=$(jq -r '.quality_metrics.validation_pass_rate' EXECUTION_STATUS.json)

        echo "📊 质量指标:"
        echo "  总体评分: $quality_score/10"
        echo "  验证通过率: $pass_rate"

        # 质量警告
        if (( $(echo "$quality_score < 7.0" | bc -l) )); then
            echo "⚠️ 质量评分偏低"
        fi

        if (( $(echo "$pass_rate < 0.9" | bc -l) )); then
            echo "⚠️ 验证通过率偏低"
        fi
    fi
}
```

### 性能监控
```bash
# 执行效率监控
monitor_performance() {
    if [ -f "EXECUTION_STATUS.json" ]; then
        tasks_per_hour=$(jq -r '.current_performance.tasks_per_hour' EXECUTION_STATUS.json)
        avg_duration=$(jq -r '.current_performance.average_duration' EXECUTION_STATUS.json)
        success_rate=$(jq -r '.current_performance.success_rate' EXECUTION_STATUS.json)

        echo "⚡ 性能指标:"
        echo "  每小时任务数: $tasks_per_hour"
        echo "  平均耗时: ${avg_duration}秒"
        echo "  成功率: $success_rate"
    fi
}
```

## 📱 移动端监控

### 简化状态查询
```bash
# 移动端友好的状态显示
mobile_status() {
    echo "🚀 Claude Code Status"
    echo "===================="

    if [ -f "EXECUTION_STATUS.json" ]; then
        current_task=$(jq -r '.execution_info.current_task' EXECUTION_STATUS.json)
        completed=$(jq -r '.execution_info.completed_tasks' EXECUTION_STATUS.json)
        total=$(jq -r '.execution_info.total_tasks' EXECUTION_STATUS.json)

        echo "当前: $current_task"
        echo "进度: $completed/$total"

        if [ "$total" != "null" ] && [ "$completed" != "null" ]; then
            progress=$((completed * 100 / total))
            echo "完成度: ${progress}%"
        fi
    else
        echo "状态: 未开始"
    fi

    echo "时间: $(date '+%H:%M')"
}
```

## 🔄 监控自动化

### 设置定时监控
```bash
# 添加到crontab，每10分钟检查一次
# */10 * * * * /path/to/your/project/check_health.sh

# check_health.sh
#!/bin/bash
cd /path/to/your/project

# 检查执行状态
if [ -f "EXECUTION_STATUS.json" ]; then
    # 记录状态快照
    cp EXECUTION_STATUS.json "status_backup_$(date +%H%M).json"

    # 检查异常
    ./check_alerts.sh
fi
```

### 状态报告生成
```bash
# 生成每日执行报告
generate_daily_report() {
    report_file="daily_report_$(date +%Y%m%d).md"

    echo "# 每日执行报告 - $(date +%Y-%m-%d)" > "$report_file"
    echo "" >> "$report_file"

    if [ -f "EXECUTION_STATUS.json" ]; then
        echo "## 执行统计" >> "$report_file"
        echo "- 开始时间: $(jq -r '.execution_info.start_time' EXECUTION_STATUS.json)" >> "$report_file"
        echo "- 完成任务: $(jq -r '.execution_info.completed_tasks' EXECUTION_STATUS.json)" >> "$report_file"
        echo "- 失败任务: $(jq -r '.execution_info.failed_tasks' EXECUTION_STATUS.json)" >> "$report_file"
        echo "- 质量评分: $(jq -r '.quality_metrics.overall_score' EXECUTION_STATUS.json)" >> "$report_file"
    else
        echo "今日无执行活动" >> "$report_file"
    fi

    echo "报告已生成: $report_file"
}
```

---

**提示**: 根据项目特点调整监控频率和告警阈值，确保及时发现和处理异常情况。