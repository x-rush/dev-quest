# Dev Quest 模块目录结构标准化指南

> **目标**: 为每个技术模块建立统一、高质量的文档结构标准
>
> **适用范围**: 所有技术模块（Go、Next.js、TanStack、React Native、Kotlin Compose、SwiftUI等）
>
> **更新日期**: 2026年9月

## 🎯 核心设计理念：双轴分离

模块内容按两个正交维度组织（借鉴 Diátaxis 文档框架）：

### 第一轴：内容用途（四象限）

| 象限 | 回答的问题 | 对应目录 | 写作特点 |
|------|-----------|---------|---------|
| **教程** (learning) | "带我入门，走一遍" | `basics/` | 按序学习，渐进构建，注重过程与练习 |
| **操作指南** (how-to) | "怎么完成这个任务" | `frameworks/` `projects/` `testing/` `deployment/` | 面向目标，步骤清晰，可直接照做 |
| **字典参考** (reference) | "X 的语法/参数是什么" | `reference/` | 全量覆盖，条目独立，可任意跳入 |
| **深度解释** (understanding) | "为什么这样设计" | `advanced-topics/` | 原理剖析，架构权衡，设计哲学 |

**核心原则：字典可独立查阅，学习有前置路径。** 同一个概念在 `reference/` 中只有一份权威条目，新手和专家查的是同一处；而学习过程按难度路径穿行各目录。

### 第二轴：难度标记（三级渐进）

难度不再用目录表达，改用文档元数据标记：

| 标记 | 含义 | 建议阶段 |
|------|------|---------|
| ⭐ | 入门 | 首次学习该技术 |
| ⭐⭐ | 进阶 | 完成入门路径后 |
| ⭐⭐⭐ | 精通 | 生产实践与深度优化 |

**README 三路径视图**：每个模块的 README 必须维护三条按难度筛选的学习路径（入门路径 / 进阶路径 / 精通路径），把散布在各目录的文档按 ⭐ 串联成学习顺序。

### 内容差异化原则
- **单一事实来源**: 完整 API 契约以 reference 为主，教程允许并应当提供必要的概念解释
- **就近合并**: 相关技术内容放在合适的上下文中，避免过度细分
- **专注核心**: frameworks 专注主流技术栈，避免过度分散
- **现代最佳实践**: testing 和 deployment 采用当前主流工具链

## 📁 标准模块目录结构

> **重要说明**: 此目录结构是标准框架，每个技术模块应根据语言特性、生态系统特点和学习路径灵活调整（见"结构适配原则"）。

```
NN-<tech>/                              # 模块根目录
├── README.md                           # 模块总览：四象限导览 + 三路径视图
│
├── 📖 basics/                          # 教程：按序学习入门
│   ├── 01-environment-setup.md          # ⭐ 环境搭建
│   ├── 02-first-program.md              # ⭐ 第一个程序
│   ├── 03-variables-types.md            # ⭐ 变量与类型
│   ├── 04-functions-methods.md          # ⭐ 函数与方法
│   ├── 05-control-flow.md               # ⭐ 控制流程
│   ├── 06-error-handling.md             # ⭐ 错误处理
│   ├── 07-advanced-features.md          # ⭐⭐ 高级特性（泛型/闭包/异步等）
│   └── 08-first-project.md              # ⭐ 第一个项目
│
├── 📚 reference/                        # 字典：声明覆盖范围，条目说明前置知识
│   ├── language-concepts/               # 语言核心概念
│   │   ├── 01-keywords.md               # 关键字详解
│   │   ├── 02-built-in-functions.md     # 内置函数
│   │   ├── 03-data-types.md             # 数据类型
│   │   ├── 04-control-flow.md           # 控制流程
│   │   └── 05-oop-concepts.md           # 面向对象/结构体概念
│   ├── framework-essentials/            # 框架核心要点
│   │   ├── 01-<framework>.md            # 主框架速查
│   │   └── 02-<framework>.md            # 次框架速查
│   ├── library-guides/                  # 标准库与三方库
│   │   ├── 01-standard-library.md       # 标准库
│   │   └── 02-third-party-libs.md       # 第三方库
│   └── quick-references/                # 纯速查表
│       ├── 01-syntax-cheatsheet.md      # 语法速查
│       └── 02-troubleshooting.md        # 故障排除
│
├── 🏗️ frameworks/                       # 操作指南：框架生态（文档内 ⭐ 标记）
│   ├── 01-<framework>-basics.md         # ⭐ 主框架入门
│   ├── 02-<framework>-advanced.md       # ⭐⭐ 主框架进阶
│   ├── 03-<ecosystem>.md                # ⭐⭐ 生态集成（数据库/缓存/工具）
│   └── 04-devtools.md                   # ⭐ 开发工具链
│
├── 🚀 projects/                         # 操作指南：实战项目（⭐ 递进排序）
│   ├── 01-starter-project.md            # ⭐ 入门项目
│   ├── 02-intermediate-project.md       # ⭐⭐ 进阶项目
│   ├── 03-advanced-project.md           # ⭐⭐ 高级项目
│   └── 04-production-app.md             # ⭐⭐⭐ 生产级应用
│
├── 🧪 testing/                          # 操作指南：测试工程
│   ├── 01-unit-testing.md               # ⭐⭐ 单元测试
│   ├── 02-mocking-stubbing.md           # ⭐⭐ Mock与桩测试
│   ├── 03-integration-testing.md        # ⭐⭐ 集成测试
│   └── 04-e2e-testing.md                # ⭐⭐ 端到端/性能测试
│
├── 🚀 deployment/                       # 操作指南：部署运维
│   ├── 01-containerization.md           # ⭐⭐ 容器化部署
│   ├── 02-ci-cd-pipelines.md            # ⭐⭐ CI/CD流水线
│   ├── 03-cloud-deployment.md           # ⭐⭐⭐ 云端部署
│   └── 04-observability.md              # ⭐⭐⭐ 可观测性
│
└── 🎓 advanced-topics/                  # 深度解释：原理与架构
    ├── architecture/                     # 架构设计
    │   └── 01-system-design.md           # ⭐⭐⭐ 系统架构设计
    ├── performance/                      # 性能优化
    │   ├── 01-concurrency-patterns.md    # ⭐⭐⭐ 并发模式
    │   └── 02-performance-tuning.md      # ⭐⭐⭐ 性能调优
    └── security/                         # 安全实践
        └── 01-security-best-practices.md # ⭐⭐⭐ 安全最佳实践
```

## 📋 README 三路径视图（必需）

每个模块 README 必须包含三条按难度串联的学习路径。格式示例：

```markdown
### 🛤️ 学习路径

#### 入门路径（⭐）
环境搭建 → 第一个程序 → 变量类型 → 函数方法 → 控制流程 → 错误处理 → 入门项目

#### 进阶路径（⭐⭐）
高级特性 → 框架入门 → 框架进阶 → 生态集成 → 单元测试 → 容器化部署 → 进阶项目

#### 精通路径（⭐⭐⭐）
系统架构设计 → 并发模式 → 性能调优 → 安全实践 → 云端部署 → 生产级应用
```

## 📋 目录详细说明

### 1. 📖 basics/ - 教程（学习路径）

**目标**: 系统化学习，从零基础到能够独立开发

**通用学习顺序**:
1. **环境搭建** → 开发环境配置和工具安装
2. **第一个程序** → Hello World 详解，专注学习体验
3. **变量常量** → 变量、常量和基础数据类型
4. **函数方法** → 函数定义与方法调用
5. **控制结构** → 条件语句与循环控制
6. **错误处理** → 语言特色的错误处理机制
7. **高级特性** → 泛型、闭包、异步等（⭐⭐）
8. **首个项目** → 完整的入门级项目实践

**文档要求**:
- 使用详细文档模板（[`../templates/document-template.md`](../templates/document-template.md)）
- 注重学习过程和练习，教程式而非参考式
- 提供渐进式的代码示例
- basics 就地解释当前步骤需要的机制；完整参数和边界再链接 reference

### 2. 📚 reference/ - 字典（知识字典）

**目标**: 全量覆盖核心概念，支持任意跳入的独立查阅——**本模块的知识字典**

**子目录说明**:
- `language-concepts/`: 语言核心概念和基础语法（细粒度独立文件）
- `framework-essentials/`: 框架核心特性和使用方法
- `library-guides/`: 标准库与第三方库指南
- `quick-references/`: 纯速查表和故障排除（一行式片段）

**文档要求**:
- 使用快速参考模板（[`../templates/quick-template.md`](../templates/quick-template.md)）
- 条目式写作：定义 → 语法 → 示例 → 陷阱，无需学习顺序
- 不设难度门槛：同一词条对新手是讲解、对专家是索引
- 其他目录先解释当前任务必需的部分，再链接这里查阅完整范围

### 3. 🏗️ frameworks/ - 框架生态（操作指南）

**目标**: 深入掌握主流框架和生态系统

**内容重点**:
- 主流框架从基础到高级的任务式指南（不是百科全书）
- 生态覆盖：数据库、缓存、工具链的完整技术栈
- 框架的完整概念速查放 `reference/framework-essentials/`，此处是"怎么用"

### 4. 🚀 projects/ - 实战项目（操作指南）

**目标**: 通过真实项目巩固知识，积累实战经验

**通用项目层次**（⭐ 递进）:
- **入门项目** ⭐: 简单功能，理解基本概念
- **进阶项目** ⭐⭐: 复杂功能，掌握核心技术
- **高级项目** ⭐⭐: 完整应用，综合运用知识
- **生产级应用** ⭐⭐⭐: 企业级特性，最佳实践应用

**项目要求**:
- 每个项目包含完整的需求、设计、实现、部署
- 包含常见问题和解决方案
- 建立与 basics/reference 相关知识的交叉链接

### 5. 🧪 testing/ - 测试工程（操作指南）

**测试层次**: 单元测试 → Mock/桩测试 → 集成测试 → 端到端/性能测试 → TDD 实践

### 6. 🚀 deployment/ - 部署运维（操作指南）

**部署层次**: 容器化 → CI/CD → 云端部署 → 可观测性（监控/日志/追踪）

### 7. 🎓 advanced-topics/ - 深度解释

**目标**: 深入理解"为什么"，提升架构与优化能力

**主题分类**: 架构设计、性能优化、安全实践（按技术栈可增减，如 api-advanced/）

## 💡 结构适配原则

在应用标准结构时，按技术特性适配：

#### 语言特性适配
- **编译型语言** (Go/Kotlin/Swift): 强调构建工具、编译器配置、性能优化
- **解释型语言** (Python/JavaScript/PHP): 注重包管理器、运行时环境、调试工具
- **面向对象语言** (Java/Kotlin): 强化类设计、继承体系、设计模式
- **声明式 UI 框架** (Compose/SwiftUI): 突出状态管理、组合模型、声明式思维

#### 生态系统适配
- **Web前端** (React/Next.js/TanStack): 强调组件化、状态管理、构建工具
- **移动开发** (React Native): 注重跨平台、原生集成、性能优化
- **后端开发** (Gin/Spring): 关注架构模式、数据库集成、部署策略

#### 目录可调整范围
- **子目录名可定制**: `advanced-topics/` 的子目录按技术栈特色命名（如 React Native 的 harmonyos-integration/）
- **文档数量可增减**: 按技术体量调整，不追求目录数量一致
- **顶层目录名保持**: 保持 basics/reference/frameworks/projects/testing/deployment/advanced-topics 七目录骨架，保证跨模块导航一致性

## 🎨 文档标准化要求

### 文档头部元数据（含难度标记）

```markdown
# 文档标题

> **文档简介**: 一句话概括本文档的核心内容和价值
>
> **目标读者**: 明确本文档适合哪类学习者
>
> **前置知识**: 学习本文档需要具备的基础知识

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `[模块名称]` |
| **象限** | 教程 / 操作指南 / 字典 / 解释 |
| **难度** | ⭐ / ⭐⭐ / ⭐⭐⭐ |
| **标签** | `#技术标签` `#概念标签` |
| **更新日期** | `YYYY年MM月` |
```

### 内容质量标准
- ✅ **准确性**: 技术内容准确无误
- ✅ **完整性**: 覆盖必要知识点
- ✅ **实用性**: 提供可操作的建议
- ✅ **时效性**: 使用最新版本技术

### 代码示例要求
- ✅ **可运行**: 所有代码示例都能正常运行
- ✅ **注释完整**: 关键代码都有详细注释
- ✅ **最佳实践**: 体现行业最佳实践
- ✅ **错误处理**: 包含适当的错误处理

### 交叉引用要求
- ✅ **概念引用**: 概念解释链接到 `reference/` 对应条目（单一事实来源）
- ✅ **前置知识**: 链接到必要的预备知识
- ✅ **后续学习**: 指向相关进阶内容
- ✅ **实践项目**: 关联到相关实战项目

## 🔄 模块创建流程

### 1. 目录结构创建
```bash
mkdir -p NN-<tech>/{reference/{language-concepts,framework-essentials,library-guides,quick-references},basics,frameworks,projects,testing,deployment,advanced-topics/{architecture,performance,security}}
```

### 2. 文档模板应用
- `reference/` → 使用 [`../templates/quick-template.md`](../templates/quick-template.md)
- `basics/` 及其他目录 → 使用 [`../templates/document-template.md`](../templates/document-template.md)

### 3. 学习路径编排
- 为每篇文档标注难度（⭐/⭐⭐/⭐⭐⭐）
- 在 README 编写入门/进阶/精通三条路径

### 4. 质量检查
- 检查链接有效性
- 验证元数据完整（象限 + 难度必填）
- 同步更新 `document-index.md` 与 `learning-progress.md`

## 📊 质量保证清单

### 内容审核
- [ ] 技术内容准确无误
- [ ] 代码示例可正常运行
- [ ] 学习目标明确具体
- [ ] 实践步骤清晰可操作

### 结构审核
- [ ] 七目录骨架符合标准
- [ ] 每篇文档标注象限与难度
- [ ] README 含三路径视图
- [ ] 交叉引用完整有效（概念统一链向 reference/）
- [ ] README.md 规划与实际文件一致

### 格式审核
- [ ] Markdown 语法正确
- [ ] 链接格式规范且目标存在
- [ ] 元数据信息完整

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team

> 🚀 **最终目标**: 字典角色（reference/）与学习路径（三路径视图）各司其职，同一批文档支撑"查字典"和"渐进学"两种访问模式
