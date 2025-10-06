# 工作流启动指南 (增强版)

> **使用说明**: 这是启动Claude Code长时间任务(24H+)的详细指南，重点强调任务讨论和用户确认流程。

## 🎯 新版工作流核心理念

### 三阶段分离原则
1. **深度讨论阶段** (1-3小时): 彻底理解用户需求和实现细节
2. **规划确认阶段** (1-2小时): 生成详细执行计划并获得用户确认
3. **自动执行阶段** (24H+): Claude Code严格按照确认的计划执行

### 关键改进
- ✅ **强制讨论机制**: 任何超过24小时的任务都必须经过详细讨论
- ✅ **用户确认书**: 用户必须签署确认书才能开始执行
- ✅ **歧义点澄清**: 所有可能歧义点都必须在执行前澄清
- ✅ **风险预案**: 所有识别的风险都必须有应对策略

## 🚀 完整启动流程

### 阶段1: 环境和准备 (15分钟)
```bash
# 1. 确保你在项目根目录
pwd  # 应该显示你的项目路径

# 2. 复制增强版模板文件到项目
cp -r claude-workflow-template/template-docs/ ./
cp -r claude-workflow-template/scripts/ ./

# 3. 验证新模板文件已复制
ls -la PROJECT_PLAN.md TASK_DEFINITIONS.md QUALITY_STANDARDS.md \
        TASK_DISCUSSION_TEMPLATE.md EXECUTION_PLAN_CONFIRMATION.md \
        PRE_EXECUTION_CHECKLIST.md

# 4. 创建必要的工作目录
mkdir -p STATE_BACKUPS ERROR_REPORTS QUALITY_REPORTS logs
```

### 阶段2: 深度任务讨论 (1-3小时)
```bash
# 启动Claude Code开始讨论阶段
claude "我需要执行一个长时间任务(超过24小时)，请按照 TASK_DISCUSSION_TEMPLATE.md 开始详细的任务讨论阶段"
```

#### 讨论阶段对话示例
```
人类: 我需要为 Dev Quest 项目生成完整的Go后端学习模块文档，这会是个长时间任务
Claude: 好的，既然这是长时间任务，我们必须进行详细的任务讨论。让我按照 TASK_DISCUSSION_TEMPLATE.md 开始：

## 🔍 阶段1: 任务目标深度讨论

我需要深入了解你的具体需求，确保我能完全满足你的期望：

### 1. 核心目标确认
- 你希望这个Go后端学习模块最终达成什么具体成果？
- 这个学习资料将如何被使用？谁会使用它？
- 成功的标准是什么？怎样算"完成得好"？

### 2. 技术要求和约束
- 有特定的Go版本要求吗？
- 涵盖哪些框架和技术栈？
- 性能、安全、可维护性方面的要求？

### 3. 范围和边界
- 哪些Go主题必须包含？
- 哪些内容明确排除？
- 有什么灰色地带需要确认？

请详细告诉我这些信息，我会基于你的回答制定执行方案。
```

### 阶段3: 执行计划制定和确认 (1-2小时)
```bash
# 讨论完成后，让Claude生成执行计划
claude "基于我们的详细讨论，请按照 EXECUTION_PLAN_CONFIRMATION.md 生成完整的执行计划确认书"
```

#### 计划确认阶段对话示例
```
Claude: 基于我们的详细讨论，我已经生成了完整的执行计划确认书。主要包括：

**技术方案**:
- Go 1.21+ 学习路径设计
- 从基础语法到微服务实战的完整体系
- Gin框架 + 标准库 + 现代工具链

**执行计划**:
- 阶段1: 基础设施搭建 (2小时)
- 阶段2: 核心内容生成 (12小时)
- 阶段3: 实战项目开发 (6小时)
- 阶段4: 质量验证优化 (4小时)

**质量保证**:
- 技术准确性验证
- 代码示例可执行性测试
- 学习路径合理性检查

请仔细阅读 EXECUTION_PLAN_CONFIRMATION.md 中的详细内容，确认是否符合你的预期。
```

### 阶段4: 用户最终确认 (30分钟)
```bash
# 用户确认后，执行最终检查
claude "请按照 PRE_EXECUTION_CHECKLIST.md 执行启动前的最终检查"
```

#### 用户确认对话示例
```
人类: 我已仔细阅读了 EXECUTION_PLAN_CONFIRMATION.md，计划看起来很完整
Claude: 很好！现在让我执行启动前的最终检查清单：

## ✅ 执行前检查

**规划文件检查**:
- PROJECT_PLAN.md ✅ 已创建且内容完整
- TASK_DEFINITIONS.md ✅ 已生成且任务详细
- QUALITY_STANDARDS.md ✅ 已定义且可量化
- EXECUTION_PLAN_CONFIRMATION.md ✅ 已生成

**技术环境检查**:
- 项目目录结构 ✅ 已准备就绪
- 磁盘空间 ✅ 充足 (>5GB)
- 网络连接 ✅ 稳定
- 系统权限 ✅ 充足

**用户确认检查**:
- 用户已最终确认 ✅ 可以开始执行
- 沟通机制 ✅ 已建立
- 执行权限 ✅ 已获得

## 🎯 最终确认

所有检查项都已通过！我现在已完全准备就绪，可以开始执行长时间任务。

**启动确认**: 请确认"我同意开始执行"，我将立即开始任务执行。
```

### 阶段5: 开始自动执行 (24H+)
```bash
# 用户最终确认后，启动执行
claude "我确认同意开始执行，请严格按照 EXECUTION_PLAN_CONFIRMATION.md 开始任务执行"
```

## 📋 新版执行监控指南

### 实时监控命令 (增强版)
```bash
# 1. 查看详细执行状态
cat EXECUTION_STATUS.json | jq '.' | head -20

# 2. 实时查看执行日志
tail -f EXECUTION_LOG.md | grep -E "(任务|错误|完成)"

# 3. 监控关键指标
watch -n 30 'echo "=== 进度统计 ===" && grep -E "(completed|failed|current_task)" EXECUTION_STATUS.json'

# 4. 质量监控
watch -n 60 'echo "=== 质量指标 ===" && grep -E "(quality_score|validation)" EXECUTION_STATUS.json'
```

### 进度检查脚本 (新增)
```bash
#!/bin/bash
# progress-check.sh - 增强版进度检查脚本

echo "🚀 Claude Code 任务执行状态报告"
echo "=================================="
echo "检查时间: $(date)"
echo ""

# 基础状态
if [ -f "EXECUTION_STATUS.json" ]; then
    echo "📊 执行进度:"
    total_tasks=$(jq -r '.execution_info.total_tasks' EXECUTION_STATUS.json)
    completed=$(jq -r '.execution_info.completed_tasks' EXECUTION_STATUS.json)
    failed=$(jq -r '.execution_info.failed_tasks' EXECUTION_STATUS.json)
    current=$(jq -r '.execution_info.current_task' EXECUTION_STATUS.json)

    echo "  总任务数: $total_tasks"
    echo "  已完成: $completed"
    echo "  失败: $failed"
    echo "  当前任务: $current"

    if [ "$total_tasks" != "null" ] && [ "$completed" != "null" ]; then
        progress=$((completed * 100 / total_tasks))
        echo "  完成度: ${progress}%"
    fi

    echo ""
    echo "📈 质量指标:"
    quality_score=$(jq -r '.quality_metrics.overall_score' EXECUTION_STATUS.json)
    echo "  总体质量评分: $quality_score/10"

    echo ""
    echo "⏱️ 执行性能:"
    tasks_per_hour=$(jq -r '.current_performance.tasks_per_hour' EXECUTION_STATUS.json)
    echo "  每小时任务数: $tasks_per_hour"
else
    echo "❌ 执行状态文件不存在"
fi

echo ""
echo "📝 最近活动 (最后5条):"
tail -5 EXECUTION_LOG.md 2>/dev/null || echo "暂无日志"
```

## 🔄 新版工作流程对比

### 旧版工作流程问题
- ❌ 缺乏详细的任务讨论
- ❌ 没有用户确认机制
- ❌ 歧义点容易在执行中暴露
- ❌ 执行返工率高

### 新版工作流程优势
- ✅ **强制深度讨论**: 确保理解无误
- ✅ **用户确认书**: 明确授权和责任
- ✅ **歧义点预先澄清**: 避免执行中出现问题
- ✅ **完整风险预案**: 提高成功率
- ✅ **质量前置**: 在执行前明确标准

## 📝 成功案例模板 (新版)

### 成功案例: Dev Quest Go后端模块 (使用新版流程)
```
**项目**: Dev Quest - Go后端学习模块
**开始时间**: 2025-10-04 10:00:00
**讨论完成**: 2025-10-04 13:30:00 (3.5小时讨论)
**计划确认**: 2025-10-04 15:00:00 (1.5小时确认)
**执行完成**: 2025-10-05 18:00:00 (24小时执行)
**总耗时**: 32小时 (含讨论和确认)

**关键成功因素**:
1. 深度任务讨论 (3.5小时): 完全理解用户需求
2. 详细执行计划 (1.5小时): 用户完全确认技术方案
3. 严格执行确认: 用户签署确认书后才开始执行
4. 风险预案完整: 执行中遇到的问题都有预案

**执行结果**:
- 生成文档: 32个 (超出预期)
- 代码示例: 150+个 (全部可执行)
- 质量评分: 平均9.2/10 (创新高)
- 零返工: 一次成功，无任何重大修改
- 用户满意度: 非常满意

**经验总结**:
- 前期讨论时间投入完全值得
- 用户确认机制避免了方向错误
- 详细的风险预案确保执行顺利
- 质量标准前置提高了最终质量
```

## 🎯 使用建议

### 什么时候使用新版流程
- **必须使用**: 预估执行时间 > 24小时的任务
- **推荐使用**: 任何重要或复杂的任务
- **可选使用**: 简单、重复性的任务

### 新版流程时间投入
- **阶段1**: 环境准备 (15分钟)
- **阶段2**: 深度讨论 (1-3小时)
- **阶段3**: 计划制定和确认 (1-2小时)
- **阶段4**: 最终检查 (30分钟)
- **阶段5**: 自动执行 (24H+)

**总前期投入**: 2.5-6小时 (完全值得)

### 用户使用技巧
1. **充分表达**: 在讨论阶段尽可能详细地表达需求
2. **及时确认**: 对Claude的理解及时确认或纠正
3. **仔细阅读**: 认真阅读执行计划确认书
4. **明确授权**: 清楚地表示同意或不同意开始执行

## 🛠️ 自动重试和恢复脚本使用指南

### 新增的核心脚本
1. **smart-retry-handler.sh** - 智能重试处理器
2. **task-health-checker.sh** - 任务健康检查器
3. **task-recovery.sh** - 任务恢复管理器
4. **execution-monitor.sh** - 综合监控器

### 启动完整的监控和重试系统
```bash
# 方式1: 启动综合监控 (推荐)
./execution-monitor.sh --interface

# 方式2: 后台监控模式
./execution-monitor.sh --background &

# 方式3: 分别启动各组件
./smart-retry-handler.sh --monitor &
./task-health-checker.sh --monitor &
```

### 手动恢复操作
```bash
# 自动恢复
./task-recovery.sh --auto

# 交互式恢复
./task-recovery.sh --interactive

# 继续中断的任务
./task-recovery.sh --continue [task_id]

# 从恢复点恢复
./task-recovery.sh --recover-point [point_id]

# 验证任务完整性
./task-recovery.sh --verify [task_id]
```

### 查看监控状态
```bash
# 生成监控仪表板
./execution-monitor.sh --dashboard

# 查看重试统计
./smart-retry-handler.sh --stats

# 执行健康检查
./task-health-checker.sh --check

# 查看实时状态
cat EXECUTION_STATUS.json | jq .
```

---

**重要提醒**:
- 新版流程增加了前期时间投入，但大幅提高了成功率
- 任何超过24小时的任务都必须使用新版流程
- 用户确认书是开始执行的法律依据，必须认真对待
- 一旦开始执行，Claude Code将严格按照确认的计划执行
- **自动重试机制**确保在API报错、任务超时时能智能恢复
- **避免无限重试**：系统内置多层重试限制和智能判断
- **任务中断恢复**：支持从任意恢复点恢复执行状态

## 🔄 执行监控指南

### 实时监控方法
```bash
# 方法1: 查看执行状态文件
tail -f EXECUTION_STATUS.json

# 方法2: 查看执行日志
tail -f EXECUTION_LOG.md

# 方法3: 查看当前任务
grep "current_task" EXECUTION_STATUS.json

# 方法4: 监控文件变化
watch -n 5 'find . -name "*.md" -mmin -10 | head -5'
```

### 进度检查命令
```bash
# 检查总体进度
grep -A 5 "execution_info" EXECUTION_STATUS.json

# 检查任务状态分布
grep -c "COMPLETED" EXECUTION_STATUS.json
grep -c "FAILED" EXECUTION_STATUS.json
grep -c "IN_PROGRESS" EXECUTION_STATUS.json

# 检查质量指标
grep "quality_score" EXECUTION_STATUS.json
```

## ⚠️ 常见问题和解决方案

### 问题1: 执行中断
```markdown
**症状**: Claude Code执行突然停止
**原因**: 可能是网络问题、系统资源不足、或API限制
**解决方案**:
1. 检查网络连接
2. 重启Claude Code
3. 从断点恢复: claude "根据 EXECUTION_STATUS.json 从中断点继续执行"
```

### 问题2: 任务失败
```markdown
**症状**: 某个任务执行失败，显示错误信息
**原因**: 权限问题、磁盘空间、或内容验证失败
**解决方案**:
1. 查看ERROR_REPORT.md了解具体错误
2. 根据错误类型进行人工干预
3. 修复问题后: claude "继续执行失败的任务 [任务ID]"
```

### 问题3: 质量不达标
```markdown
**症状**: 生成的内容质量不符合标准
**原因**: 质量标准定义不清晰或验证规则有误
**解决方案**:
1. 检查QUALITY_STANDARDS.md定义
2. 调整质量标准或验证规则
3. 重新执行质量检查: claude "重新验证已生成的内容质量"
```

### 问题4: 执行缓慢
```markdown
**症状**: 执行速度比预期慢很多
**原因**: 系统资源不足或任务定义过于复杂
**解决方案**:
1. 检查系统资源使用情况
2. 优化任务定义，减少不必要的验证
3. 调整并行执行参数
```

## 📊 执行结果验收

### 完成检查清单
```markdown
## 项目完成验收标准

### 内容完整性
- [ ] 所有计划任务都已完成
- [ ] 生成的文档数量符合预期
- [ ] 代码示例全部可执行
- [ ] 链接和引用完整有效

### 质量达标
- [ ] 技术内容准确性验证通过
- [ ] 文档格式规范统一
- [ ] 质量评分达到A级或B级
- [ ] 用户测试反馈良好

### 结构合规
- [ ] 目录结构符合规划
- [ ] 文件命名规范一致
- [ ] 模块组织逻辑清晰
- [ ] 依赖关系正确

### 可维护性
- [ ] 文档结构易于扩展
- [ ] 代码示例易于理解
- [ ] 更新机制明确
- [ ] 维护文档完整
```

### 验收命令
```bash
# 生成最终执行报告
claude "生成项目执行完成报告，包含执行统计、质量分析和改进建议"

# 质量最终检查
claude "对所有生成的内容进行最终质量检查和评分"

# 生成维护指南
claude "生成项目维护和更新指南"
```

## 🎯 成功案例模板

### 成功案例: Dev Quest Go后端模块
```
**项目**: Dev Quest - Go后端学习模块
**开始时间**: 2025-10-04 10:00:00
**完成时间**: 2025-10-04 18:30:00
**总耗时**: 8.5小时

**执行结果**:
- 生成文档: 26个
- 代码示例: 120+个
- 质量评分: 平均8.9/10
- 验证通过率: 96%

**关键成功因素**:
1. 详细的前期规划和任务定义
2. 明确的质量标准和验证规则
3. 完善的异常处理机制
4. 及时的监控和干预

**经验总结**:
- 规划阶段投入的时间非常值得
- 任务分解越细，执行越稳定
- 质量标准需要具体可量化
- 监控机制确保及时发现问题
```

---

**注意**: 这个启动指南是通用模板，请根据你的具体项目需求进行调整。建议第一次使用时选择较小的项目进行试验。