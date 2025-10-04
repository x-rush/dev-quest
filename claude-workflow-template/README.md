# Claude Code 通用工作流系统

## 🎯 概述

这是一套基于"规划-执行-验证"理念的Claude Code自动化工作流系统，适用于长时间、复杂的项目自动化执行。

## 📁 文件夹结构

```
claude-workflow-template/
├── README.md                       # 本文件 - 系统概述
├── USAGE_GUIDE.md                  # 详细使用指南
├── template-docs/                  # 工作流模板文档
│   ├── PROJECT_PLAN_TEMPLATE.md    # 项目规划模板
│   ├── TASK_DEFINITION_TEMPLATE.md # 任务定义模板
│   ├── QUALITY_STANDARDS_TEMPLATE.md # 质量标准模板
│   ├── EXECUTION_PLAN_TEMPLATE.md  # 执行计划模板
│   └── ERROR_HANDLING_TEMPLATE.md  # 异常处理模板
├── scripts/                        # 辅助指南
│   ├── workflow-starter.md         # 工作流启动指南
│   ├── status-monitor.md           # 状态监控指南
│   └── recovery-guide.md           # 恢复指南
└── examples/                       # 实际案例
    ├── dev-quest-example/          # Dev Quest项目示例
    │   └── PROJECT_PLAN.md
    └── simple-docs-example/        # 简单文档生成示例
        ├── PROJECT_PLAN.md
        ├── TASK_DEFINITIONS.md
        └── QUALITY_STANDARDS.md
```

## 🚀 快速开始

### 1. 复制模板到你的项目
```bash
# 在你的项目根目录下
cp -r claude-workflow-template/template-docs/ ./
cp -r claude-workflow-template/scripts/ ./
```

### 2. 开始规划对话
启动Claude Code并开始规划对话：
```bash
claude "我想要使用工作流系统来执行 [你的项目目标]，请根据 PROJECT_PLAN_TEMPLATE.md 帮我制定详细的执行计划"
```

### 3. 执行自动化任务
规划确认后，启动自动执行：
```bash
claude "根据 PROJECT_PLAN.md 和 TASK_DEFINITIONS.md 开始执行自动化任务"
```

## 🎯 核心理念

### 规划-执行-验证 分离
- **规划阶段**: 人机协作，制定详细方案
- **执行阶段**: AI自主执行，自我验证
- **验收阶段**: 人类检查最终结果

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

## 🛠️ 系统特性

- **安全可控**: 人类掌控大方向，AI执行细节
- **质量保证**: 每个任务都有明确的验证标准
- **容错性**: 异常处理和断点续传机制
- **透明性**: 完整的执行日志和状态跟踪
- **可扩展**: 支持自定义任务类型和验证规则

## 📖 使用指南

1. **首次使用**: 建议先查看 examples/ 中的示例
2. **项目适配**: 根据项目特点调整模板内容
3. **质量标准**: 明确定义每个任务的完成标准
4. **异常处理**: 预设可能遇到的问题和解决方案

## 🤝 支持和反馈

这套工作流系统是开源的，欢迎根据你的项目需求进行修改和扩展。如有问题或建议，请通过项目的issue系统反馈。

---

**版本**: 1.0
**更新时间**: 2025-10-04
**兼容性**: Claude Code CLI