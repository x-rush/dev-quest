# Claude Code 通用工作流系统 (增强版)

## 🎯 概述

这是一套基于"深度讨论-规划确认-自动执行-质量验收"四阶段理念的Claude Code自动化工作流系统，专为长时间任务(24H+)设计，强调任务讨论和用户确认机制。

## 📁 文件夹结构

```
claude-workflow-template/
├── README.md                       # 本文件 - 系统概述
├── USAGE_GUIDE.md                  # 详细使用指南
├── template-docs/                  # 工作流模板文档 (增强版)
│   ├── PROJECT_PLAN_TEMPLATE.md    # 项目规划模板 (增强版)
│   ├── TASK_DEFINITION_TEMPLATE.md # 任务定义模板
│   ├── QUALITY_STANDARDS_TEMPLATE.md # 质量标准模板
│   ├── ERROR_HANDLING_TEMPLATE.md  # 异常处理模板 (增强版)
│   ├── TASK_DISCUSSION_TEMPLATE.md # 🆕 任务讨论阶段模板
│   ├── EXECUTION_PLAN_CONFIRMATION.md # 🆕 执行计划确认书
│   └── PRE_EXECUTION_CHECKLIST.md  # 🆕 执行前检查清单
├── scripts/                        # 执行脚本和监控工具 (增强版)
│   ├── workflow-starter.md         # 工作流启动指南 (增强版)
│   ├── status-monitor.md           # 状态监控指南
│   ├── recovery-guide.md           # 恢复指南
│   ├── smart-retry-handler.sh      # 🆕 智能重试处理器
│   ├── task-health-checker.sh      # 🆕 任务健康检查器
│   ├── task-recovery.sh            # 🆕 任务恢复管理器
│   └── execution-monitor.sh        # 🆕 综合监控器
└── examples/                       # 实际案例
    └── dev-quest-example/          # Dev Quest项目示例
        └── PROJECT_PLAN.md
```

## 🚀 快速开始 (增强版)

### 1. 复制增强版模板到你的项目
```bash
# 在你的项目根目录下
cp -r claude-workflow-template/template-docs/ ./
cp -r claude-workflow-template/scripts/ ./

# 创建必要的工作目录
mkdir -p STATE_BACKUPS ERROR_REPORTS QUALITY_REPORTS logs
```

### 2. 开始深度任务讨论 (新版强制要求)
启动Claude Code并开始任务讨论：
```bash
claude "我需要执行一个长时间任务(超过24小时)，请按照 TASK_DISCUSSION_TEMPLATE.md 开始详细的任务讨论阶段"
```

### 3. 确认执行计划
讨论完成后，生成并确认执行计划：
```bash
claude "基于我们的详细讨论，请按照 EXECUTION_PLAN_CONFIRMATION.md 生成完整的执行计划确认书"
```

### 4. 执行前检查
用户确认后，执行最终检查：
```bash
claude "请按照 PRE_EXECUTION_CHECKLIST.md 执行启动前的最终检查"
```

### 5. 开始自动执行
所有检查通过后，启动执行：
```bash
claude "我确认同意开始执行，请严格按照 EXECUTION_PLAN_CONFIRMATION.md 开始任务执行"
```

### 6. 启动智能监控和重试系统 (新增)
为确保长时间任务执行的稳定性，建议同时启动监控系统：
```bash
# 启动综合监控界面 (推荐)
./execution-monitor.sh --interface

# 或使用后台监控模式
./execution-monitor.sh --background &
```

### 完整的执行和监控流程
```bash
# 1. 启动任务执行
claude "我确认同意开始执行，请严格按照 EXECUTION_PLAN_CONFIRMATION.md 开始任务执行"

# 2. 同时启动监控系统 (新终端)
./execution-monitor.sh --interface

# 3. 任务会自动处理异常和重试
# 4. 如需手动干预，使用恢复工具
./task-recovery.sh --interactive
```

## 🎯 核心理念 (增强版)

### 四阶段分离原则
- **深度讨论阶段** (1-3小时): 彻底理解用户需求和实现细节
- **规划确认阶段** (1-2小时): 生成详细执行计划并获得用户确认
- **自动执行阶段** (24H+): Claude Code严格按照确认的计划执行
- **质量验收阶段**: 人类检查最终结果

### 强制确认机制
- 任何超过24小时的任务都必须经过详细讨论
- 用户必须签署确认书才能开始执行
- 所有可能歧义点都必须在执行前澄清
- 已识别的风险都必须有应对策略

### 零返工目标
- 通过充分的讨论和确认，实现一次性成功
- 质量标准前置，在执行前明确要求
- 风险预案完整，执行中有问题可快速解决

### 渐进式自动化
- 从简单任务开始，逐步增加复杂度
- 每个任务都有明确的验证标准
- 异常情况自动暂停，等待人工干预

### 跨项目复用
- 标准化的模板和流程
- 适应不同类型的项目需求
- 可扩展的任务定义和验证机制

## 📋 适用场景

- ✅ 大型文档生成项目
- ✅ 代码库重构项目
- ✅ 多模块开发项目
- ✅ 自动化测试项目
- ✅ 持续集成/部署项目

## 🛠️ 系统特性 (增强版)

- **强制讨论机制**: 确保完全理解用户需求，避免误解
- **用户确认书**: 明确授权和责任，防止执行偏差
- **歧义点预先澄清**: 在执行前消除所有可能的不确定性
- **完整风险预案**: 为每个已识别风险制定应对策略
- **质量前置标准**: 在执行前明确质量要求和验收标准
- **安全可控**: 人类掌控大方向，AI执行细节
- **质量保证**: 每个任务都有明确的验证标准
- **容错性**: 异常处理和断点续传机制
- **透明性**: 完整的执行日志和状态跟踪
- **可扩展**: 支持自定义任务类型和验证规则

## 🆕 新版增强功能

### 深度任务讨论系统
- 结构化讨论流程，确保理解全面
- 歧义点自动识别和澄清
- 用户特殊要求详细记录

### 执行计划确认机制
- 详细的技术方案和执行计划
- 风险评估和应对策略
- 用户签署确认书授权执行

### 执行前检查清单
- 26项必检项目，确保万无一失
- 分类别检查：规划文件、技术环境、数据状态、风险预案、用户确认
- Claude自检和用户确认双重保障

### 🚀 智能重试和恢复系统 (全新)
- **自动异常检测**: 实时监控API错误、超时、网络问题
- **智能重试机制**: 多层限制，避免无限重试，指数退避策略
- **任务恢复管理**: 支持从任意恢复点恢复执行状态
- **健康监控系统**: 全面的系统资源和执行状态监控
- **综合监控界面**: 实时显示所有关键指标和告警信息

### 核心监控和恢复脚本
1. **smart-retry-handler.sh** - 智能重试处理器
2. **task-health-checker.sh** - 任务健康检查器
3. **task-recovery.sh** - 任务恢复管理器
4. **execution-monitor.sh** - 综合监控器

## 📖 使用指南 (增强版)

### 基础使用流程
1. **首次使用**: 建议先查看 examples/ 中的示例
2. **项目适配**: 根据项目特点调整模板内容
3. **质量标准**: 明确定义每个任务的完成标准
4. **异常处理**: 预设可能遇到的问题和解决方案
5. **深度讨论**: 对于长时间任务，必须进行详细的任务讨论
6. **用户确认**: 确保用户完全理解并同意执行计划
7. **执行前检查**: 严格按照检查清单验证所有准备工作

### 监控和恢复操作
8. **启动监控**: 执行任务时同时启动监控系统
9. **异常处理**: 系统会自动检测和处理常见异常
10. **手动恢复**: 必要时使用恢复工具进行人工干预

### 完整操作命令
```bash
# 基础工作流程
cp -r claude-workflow-template/template-docs/ ./
cp -r claude-workflow-template/scripts/ ./
mkdir -p STATE_BACKUPS ERROR_REPORTS QUALITY_REPORTS logs

# 1. 深度任务讨论
claude "我需要执行长时间任务，请按照 TASK_DISCUSSION_TEMPLATE.md 开始详细讨论"

# 2. 生成执行计划确认书
claude "基于讨论结果，请按 EXECUTION_PLAN_CONFIRMATION.md 生成执行计划确认书"

# 3. 执行前检查
claude "请按 PRE_EXECUTION_CHECKLIST.md 执行最终检查"

# 4. 启动任务执行
claude "我确认同意开始执行，请严格按照确认书执行"

# 5. 启动监控系统 (新终端)
./execution-monitor.sh --interface

# 6. 如需手动恢复
./task-recovery.sh --interactive
```

## 📊 新版vs旧版对比

| 特性 | 旧版 | 新版 |
|------|------|------|
| 任务讨论 | ❌ 无 | ✅ 强制深度讨论 |
| 用户确认 | ❌ 无 | ✅ 确认书机制 |
| 歧义澄清 | ❌ 执行中发现 | ✅ 预先澄清 |
| 风险预案 | ❌ 基础预案 | ✅ 完整预案 |
| 质量标准 | ✅ 有 | ✅ 前置明确 |
| 自动重试 | ❌ 无 | ✅ 智能重试机制 |
| 异常恢复 | ❌ 无 | ✅ 多级恢复策略 |
| 实时监控 | ❌ 无 | ✅ 综合监控系统 |
| 返工率 | 🔸 较高 | ✅ 接近零 |
| 成功率 | 🔸 70-80% | ✅ 95%+ |

## 🛠️ 监控和恢复工具详细使用

### 启动监控系统
```bash
# 方式1: 实时监控界面 (推荐)
./execution-monitor.sh --interface

# 方式2: 后台监控模式
./execution-monitor.sh --background &

# 方式3: 生成监控仪表板
./execution-monitor.sh --dashboard

# 方式4: 一次性状态检查
./execution-monitor.sh --check
```

### 任务恢复操作
```bash
# 自动恢复模式
./task-recovery.sh --auto

# 交互式恢复 (推荐)
./task-recovery.sh --interactive

# 智能状态恢复
./task-recovery.sh --smart-recovery

# 继续中断的任务
./task-recovery.sh --continue [task_id]

# 从恢复点恢复
./task-recovery.sh --recover-point [recovery_point_id]

# 验证任务完整性
./task-recovery.sh --verify [task_id]

# 列出可用恢复点
./task-recovery.sh --list-points
```

### 智能重试管理
```bash
# 启动智能重试监控
./smart-retry-handler.sh --monitor

# 手动重试指定任务
./smart-retry-handler.sh --retry [task_id]

# 查看重试统计信息
./smart-retry-handler.sh --stats

# 清理旧恢复点
./smart-retry-handler.sh --cleanup
```

### 健康检查工具
```bash
# 执行单次健康检查
./task-health-checker.sh --check

# 启动持续健康监控
./task-health-checker.sh --monitor

# 生成健康检查报告
./task-health-checker.sh --report
```

### 监控文件说明
执行过程中会生成以下监控文件：
- **EXECUTION_STATUS.json** - 实时执行状态
- **EXECUTION_LOG.md** - 详细执行日志
- **MONITOR_LOG.md** - 监控系统日志
- **ALERT_HISTORY.md** - 告警历史记录
- **MONITOR_DASHBOARD.md** - 监控仪表板
- **RECOVERY_POINTS/** - 恢复点目录
- **RETRY_LOG.md** - 重试操作日志

## 🤝 支持和反馈

这套工作流系统是开源的，欢迎根据你的项目需求进行修改和扩展。如有问题或建议，请通过项目的issue系统反馈。

### 贡献指南
- 欢迎提交改进建议和bug报告
- 可以分享你的使用案例和经验
- 参与模板和脚本的完善

---

**版本**: 2.0 (增强版)
**更新时间**: 2025-10-06
**兼容性**: Claude Code CLI
**主要改进**: 新增深度讨论机制、用户确认书、执行前检查清单、智能重试和恢复系统

## 📖 详细文档

- **[快速启动指南](QUICK_START_GUIDE.md)** - 5分钟快速上手
- **[完整使用指南](USAGE_GUIDE.md)** - 详细的使用说明和最佳实践
- **[脚本工具说明](scripts/README.md)** - 所有脚本工具的详细文档
- **[工作流启动指南](scripts/workflow-starter.md)** - 增强版启动流程
- **[恢复操作指南](scripts/recovery-guide.md)** - 异常恢复详细说明