# iOS 原生开发 — Swift 6 + SwiftUI 现代化开发

> **本轮增强与版本核对**：学习路径及正文增强范围见 [逐文件台账](../shared-resources/tools/document-quality/reports/coverage.md)。下方技术基线中的旧核对日期属于历史记录，不表示这次已重跑所有平台；安装与升级以官方兼容要求、项目锁文件和实际构建结果为准。


第一次学习请从[理解地图与学习规划](LEARNING_GUIDE.md)开始，按其中的阶段任务和验收条件推进。先学习 Swift 可选值、结构体和闭包，再用 SwiftUI 做状态界面与本地笔记。无需预先掌握 Go 或 React；原生应用构建与运行使用对应的 Apple 开发环境。

查语法、函数或库时使用下方参考目录。文件数量与目录中的完成标记表示内容组织情况，不能替代示例运行证据；具体交付按[知识库质量基线](../shared-resources/standards/knowledge-delivery-baseline.md)验收。

> **文档简介**: Dev Quest 应用帝国矩阵的 iOS 支柱模块：以 Swift 6.3 严格并发为地基，用 SwiftUI + Observation + SwiftData 构建现代原生应用，直至上架与运维
>
> **目标读者**: 会基本编程、初次学习 Swift 与 iOS 的学习者；Go 后端与前端经验可用于对照，不是前提
>
> **前置知识**: 需基本编程和 Swift 语法；有任一声明式 UI 框架（React/Compose）经验可显著加速

## 🧪 技术基线

本模块内容基于以下版本快照编写（核实日期：**2026-09-16**）。工具链请以你本机 `swift --version` 与 Xcode 实际输出为准。

| 技术 | 当前版本 | 核实要点 |
|------|---------|---------|
| Swift | 编译器版本以练习工程实际工具链为准，历史正文包含 6.3 示例 | 编译器版本与语言模式分别记录；使用 Swift 6 编译器不代表 target 已开启 Swift 6 语言模式，需检查项目构建设置 |
| Xcode | **26.6** | 内含 Swift 6.3.3 工具链，SDK 覆盖 iOS 26.5 等 |
| iOS SDK | **iOS 26** | SwiftUI / SwiftData 随 SDK 一体发布，无独立版本号；标志性变化为 Liquid Glass 设计与 `.glassEffect()` 等 SwiftUI 新 API |
| 构建系统 | Swift Build（开源） | Swift 6.3 起 Swift Build 以 preview 形式集成进 SPM（官方邀请试用反馈，尚未成为默认） |

语言模式决定源代码兼容规则。先记录 Xcode 的 Swift Language Version、Strict Concurrency Checking 及默认 actor 隔离设置，再解释并发诊断；不能只凭 `swift --version` 宣称严格并发检查已开启。依据：[Swift 版本兼容说明](https://docs.swift.org/latest/documentation/the-swift-programming-language/compatibility/)、[Apple 的 Swift 6 迁移说明](https://developer.apple.com/documentation/swift/adoptingswift6)。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 模块元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **定位** | 应用帝国矩阵（核心重点）· 苹果生态 |
| **技术栈** | Swift 6.3（严格并发）、SwiftUI + Observation（@Observable）、SwiftData、Xcode 26.x（iOS 26 SDK） |
| **更新日期** | `2026年9月` |

</details>

## 🎯 模块简介

本模块面向会基本编程、初次学习 Swift 与 iOS 的读者。先理解可选值、值语义和闭包，再学习视图身份、状态和持久化。Go 或前端经验可用于对照，不是前提；应用是否可发布需要在目标工具链和平台上另行验收。

完成本模块后，你将能够：

- 解释可选值、结构体、闭包与错误，能从编译器信息定位相关代码。
- 让父子视图共享同一份状态，验证导航前后哪些状态保留或重建。
- 保存并重新读取一条本地数据，再加入网络请求、取消和失败恢复。
- 在声明的目标系统上运行测试与构建；分发、签名和上架作为后续独立任务。

## 🧭 四象限导览

| 象限 | 目录 | 内容 | 访问方式 |
|------|------|------|---------|
| **📖 教程** | [basics/](./basics/01-environment-setup.md) | 环境搭建 → Swift 语法 → SwiftUI 视图/状态/布局/导航 → 并发入门 → 首个项目，共 8 篇 | 按导读的能力顺序学习 |
| **📚 字典** | [reference/](./reference/quick-references/01-swift-swiftui-cheatsheet.md) | 语言概念（16 篇，含构造/关键字总索引/正则/URLSession/包地图）/ 框架要点（8 篇，含手势）/ 库指南（2 篇）/ 速查与故障排除（2 篇），共 28 篇全量参考 | **可独立查阅，仍有前置知识**，任意跳入查询 |
| **🛠️ 操作指南** | [frameworks/](./frameworks/01-swiftui-basics.md) [projects/](./projects/01-notes-app.md) [testing/](./testing/01-unit-testing.md) [deployment/](./deployment/01-app-release.md) | 框架任务指南 4 篇 · 实战项目 4 个（⭐ 递进）· 测试工程 3 篇 · 部署运维 3 篇 | 面向目标，按需照做 |
| **🎓 解释** | [advanced-topics/](./advanced-topics/architecture/01-app-architecture.md) | 应用架构、渲染性能、并发深度、安全实践，共 4 篇深度专题（均 ⭐⭐⭐） | 有实践困惑后带着问题读 |

**单一事实来源**：完整参考以 `reference/` 为主；教程就地解释当前步骤所需概念，再链接完整条目。

## 🛤️ 学习路径

### 入门路径（⭐）

环境搭建 → Swift 语法要点 → 第一个 SwiftUI App → 视图与状态 → 布局系统 → 导航模式 → 首个完整项目 → 本地笔记应用

[01 环境搭建](./basics/01-environment-setup.md) → [03 Swift 语法要点](./basics/03-swift-syntax-essentials.md) → [02 第一个 SwiftUI App](./basics/02-first-swiftui-app.md) → [04 视图与状态](./basics/04-views-state.md) → [05 布局系统](./basics/05-layouts.md) → [06 导航模式](./basics/06-navigation.md) → [08 首个完整项目：待办记账](./basics/08-first-project.md) → [项目：本地笔记应用](./projects/01-notes-app.md)

首项目需要可用的 macOS/Xcode、iOS 17 或更高的运行目标，以及可选值、数组和错误处理基础。交付自己的 Xcode 工程和验收记录：新增 A/B、完成并删除 B，终止应用再启动后 A 仍在且 B 不在；支出 `0.10` 与 `0.20` 合计显示 0.30 元，非法金额不能保存。先完成待办阶段，再加入记账；未运行的设备检查标为未验证。遇到视图问题查[SwiftUI 基础任务指南](./frameworks/01-swiftui-basics.md)，工程启动问题查[Xcode 工具链](./frameworks/04-devtools.md)。完成后再做笔记应用的编辑与搜索；[并发入门](./basics/07-concurrency-async-await.md)在进入网络项目之前学习。

### 首次学习的四个可交付关卡

前置自检：能用函数转换输入，知道值缺失不等于空字符串。Swift 可选值、结构体和闭包不熟时，先在[语法篇](basics/03-swift-syntax-essentials.md)完成练习；没有 macOS/Xcode 可先学习语言，但将下面的 SwiftUI 与 SwiftData 设备结果留为未验证。

| 关卡 | 操作和最小产物 | 成功条件；失败恢复 |
|---|---|---|
| 1. 模板运行 | 新建 SwiftUI App，保留唯一 `@main`，选择目标设备并改一行显示文本；记录 Xcode、SDK、部署目标、语言模式 | 实际运行显示新文本；Preview 能显示不能代替应用运行。构建不通过先回[环境篇](basics/01-environment-setup.md)，不要添加持久化代码 |
| 2. 状态拥有者 | 父视图保存计数，子视图通过 Binding 增加和重置；记录 0→1→2→0 | 父子显示一致；子视图自己复制值导致分叉时，回[视图与状态](basics/04-views-state.md)检查事实来源和视图身份 |
| 3. 待办持久化 | 按首项目增加 A/B、完成并删除 B，再终止与重启；保存工程和设备步骤 | A 保留、B 不恢复；界面变化但重启丢数据时查显式 `save()` 结果、容器是否只在内存中及错误分支，不靠延时等待自动保存掩盖问题 |
| 4. 金额与失败 | 待办关通过后增加记账，输入 `0.10`、`0.20` 和非法金额；在独立练习的保存入口注入失败 | 合计为 0.30，非法输入不写入；保存失败保留表单、显示错误并允许恢复后重试。失败回查[首项目](basics/08-first-project.md)金额解析、保存和回滚范围 |

最后将“源码版本、目标环境、步骤、期望、实际、恢复后的结果”交付为一份记录，再新建独立[笔记项目](projects/01-notes-app.md)练习编辑和搜索。不要为跟随下一篇而把旧数据库模型直接替换；保留旧数据的模型演进需要迁移方案。本页本轮未执行 Xcode 构建、SwiftUI 交互或 SwiftData 故障注入，未取得这些关卡的运行通过证据。

### 进阶路径（⭐⭐）

async/await → SwiftUI 进阶 → SwiftData + 网络 → 天气应用 → 习惯追踪器 → 单元测试 → UI 测试 → 集成测试 → 签名与 TestFlight → App Store 上架

[07 并发 async/await](./basics/07-concurrency-async-await.md) → [SwiftUI 进阶任务指南](./frameworks/02-swiftui-advanced.md) → [SwiftData + URLSession 集成](./frameworks/03-ecosystem-integration.md) → [项目：天气应用](./projects/02-weather-app.md) → [项目：习惯追踪器](./projects/03-habit-tracker.md) → [单元测试](./testing/01-unit-testing.md) → [UI 测试](./testing/02-ui-testing.md) → [集成测试](./testing/03-integration-testing.md) → [签名、Archive 与 TestFlight](./deployment/01-app-release.md) → [App Store 上架](./deployment/02-app-store-release.md)

### 精通路径（⭐⭐⭐）

应用架构 → 渲染性能 → 并发深度 → 安全实践 → CI/CD 与可观测性 → 生产级 iOS 应用

[应用架构：MV 到 TCA](./advanced-topics/architecture/01-app-architecture.md) → [渲染性能深度解析](./advanced-topics/performance/01-rendering-performance.md) → [Swift 并发深度解析](./advanced-topics/performance/02-concurrency-optimization.md) → [安全实践深度解析](./advanced-topics/security/01-security-practices.md) → [CI/CD 与可观测性](./deployment/03-ci-cd-observability.md) → [项目：生产级 iOS 应用](./projects/04-production-ios-app.md)

> 💡 查字典不进路径：语法卡壳翻 [`01-swift-keywords.md`](./reference/language-concepts/01-swift-keywords.md)，API 忘记翻 [`01-swift-swiftui-cheatsheet.md`](./reference/quick-references/01-swift-swiftui-cheatsheet.md)，报错先查 [`02-troubleshooting.md`](./reference/quick-references/02-troubleshooting.md)。

## 📁 文件树（与磁盘一致）

```text
06-swift-swiftui/
├── README.md                                  # 本文档
├── iOS原生开发学习路线.md                       # 详细学习指南（历史参考）
│
├── basics/                                    # 📖 教程：按序学习入门
│   ├── 01-environment-setup.md                #   ⭐ 环境搭建
│   ├── 02-first-swiftui-app.md                #   ⭐ 第一个 SwiftUI App
│   ├── 03-swift-syntax-essentials.md          #   ⭐ Swift 语法要点
│   ├── 04-views-state.md                      #   ⭐ 视图与状态管理
│   ├── 05-layouts.md                          #   ⭐ 布局系统
│   ├── 06-navigation.md                       #   ⭐ 导航模式
│   ├── 07-concurrency-async-await.md          #   ⭐⭐ 并发与 async/await
│   └── 08-first-project.md                    #   ⭐ 第一个项目
│
├── reference/                                 # 📚 字典：全量参考（可独立查阅，仍有前置知识）
│   ├── language-concepts/                     #   语言核心概念
│   │   ├── 01-swift-keywords.md               #     Swift 关键字
│   │   ├── 02-optionals-collections.md        #     可选值与集合
│   │   ├── 03-concurrency-api.md              #     并发 API 全表
│   │   ├── 04-swiftui-state-api.md            #     SwiftUI 状态 API
│   │   ├── 05-protocols-generics.md           #     协议与泛型
│   │   ├── 06-closures.md                     #     闭包与函数类型
│   │   ├── 07-enums-pattern-matching.md       #     枚举与模式匹配
│   │   ├── 08-error-handling.md               #     错误处理
│   │   ├── 09-property-wrappers.md            #     属性包装器
│   │   ├── 10-value-types-arc.md              #     值类型、引用类型与 ARC
│   │   └── 11-actors-sendability.md           #     Actor 隔离与 Sendable
│   ├── framework-essentials/                  #   框架核心要点
│   │   ├── 01-swiftui-essentials.md           #     SwiftUI 视图与修饰符速查
│   │   ├── 02-swiftdata-observability.md      #     SwiftData 与 Observation
│   │   ├── 03-state-driven-views.md           #     状态驱动视图
│   │   ├── 04-view-modifier.md                #     ViewModifier 与修饰符链
│   │   ├── 05-data-flow.md                    #     数据流与 Environment
│   │   ├── 06-swift-charts.md                 #     SwiftUI Charts 数据可视化
│   │   └── 07-swiftdata-migration.md          #     SwiftData 模型迁移
│   ├── library-guides/                        #   标准库与三方库
│   │   ├── 01-foundation-and-stdlib.md        #     Foundation 与标准库
│   │   └── 02-third-party-libs.md             #     第三方库指南
│   └── quick-references/                      #   纯速查表
│       ├── 01-swift-swiftui-cheatsheet.md     #     语法速查
│       └── 02-troubleshooting.md              #     故障排除
│
├── frameworks/                                # 🛠️ 操作指南：框架生态
│   ├── 01-swiftui-basics.md                   #   ⭐ SwiftUI 基础任务
│   ├── 02-swiftui-advanced.md                 #   ⭐⭐ Observation/导航/动画
│   ├── 03-ecosystem-integration.md            #   ⭐⭐ SwiftData + URLSession
│   └── 04-devtools.md                         #   ⭐ Xcode 工具链
│
├── projects/                                  # 🛠️ 操作指南：实战项目（⭐ 递进）
│   ├── 01-notes-app.md                        #   ⭐ 本地笔记应用（SwiftData）
│   ├── 02-weather-app.md                      #   ⭐⭐ 天气应用（网络 + 定位）
│   ├── 03-habit-tracker.md                    #   ⭐⭐ 习惯追踪器（建模 + 图表）
│   └── 04-production-ios-app.md               #   ⭐⭐⭐ 生产级 iOS 应用
│
├── testing/                                   # 🛠️ 操作指南：测试工程
│   ├── 01-unit-testing.md                     #   ⭐⭐ Swift Testing 单元测试
│   ├── 02-ui-testing.md                       #   ⭐⭐ XCUITest 界面测试
│   └── 03-integration-testing.md              #   ⭐⭐ 集成测试
│
├── deployment/                                # 🛠️ 操作指南：部署运维
│   ├── 01-app-release.md                      #   ⭐⭐ 签名、Archive 与 TestFlight
│   ├── 02-app-store-release.md                #   ⭐⭐ App Store 上架流程
│   └── 03-ci-cd-observability.md              #   ⭐⭐⭐ Xcode Cloud + MetricKit
│
└── advanced-topics/                           # 🎓 解释：深度专题（均 ⭐⭐⭐）
    ├── architecture/
    │   └── 01-app-architecture.md             #   应用架构：MV 到 TCA 思想
    ├── performance/
    │   ├── 01-rendering-performance.md        #   渲染性能与视图求值
    │   └── 02-concurrency-optimization.md     #   Swift 并发深度实践
    └── security/
        └── 01-security-practices.md           #   安全实践：Keychain/ATS/隐私
```

## 💡 从其他平台到 iOS 的思维转换

- **UI 模式**：从命令式 UI 到声明式 UI——视图是状态的纯函数
- **内存管理**：从垃圾收集到 ARC——引用类型才谈所有权，struct 优先
- **并发模型**：从线程池到结构化并发——actor 隔离 + 编译期数据竞争检查
- **设计理念**：Human Interface Guidelines 与苹果平台惯例（导航、手势、动态字体）

## 🔗 关联模块

- 📄 [04-multiplatform-apps](../04-multiplatform-apps/README.md) — React Native 跨端视角：SwiftUI 声明式思想可与其组件模型对照学习
- 📄 [05-kotlin-compose](../05-kotlin-compose/README.md) — 声明式 UI 的安卓双生框架，状态管理与组合模型可互相印证

---

**最后更新**：2026年9月
**维护团队**：Dev Quest Team
