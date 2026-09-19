# Swift / SwiftUI：理解地图与学习规划

> 前置：函数、结构体、可选值与闭包；macOS 和 Xcode 用于本地 SwiftUI 开发。Windows 上可阅读和做语义推演，但不能据此宣称完成原生运行验收。

## 先回答一个问题

**视图值反复产生，用户输入为什么能够保留，什么时候又会丢失？**

Swift 提供类型与并发语义，SwiftUI 根据状态描述界面。把视图身份、状态拥有者与持久化分开理解，比先记住所有属性包装器更重要。

## 概念怎样连接

Swift 值与可选值 → View → State/Binding → 布局与身份 → 导航 → Observation/Task → SwiftData

| 概念 | 必要解释 |
|---|---|
| State 与 Binding | State 在视图身份下持有状态，Binding 提供读写已有状态的通道；传 Binding 不会复制一份独立事实来源。 |
| 视图身份 | 相同代码位置或显式 ID 帮助框架对应视图；随意改变 ID 可能重置状态。 |
| Task 与 Actor | 异步任务可以挂起，Actor 管理隔离；await 不保证耗时计算自动离开主执行器。 |

## 从 0 到 1 的阅读顺序

先在 Xcode 中运行一个最小工程，再单独学习可选值、结构体和闭包，之后把这些语法带入 View 与状态。首次 App 一章可作为环境冒烟检查；若其代码读不懂，先完成下列语法篇再返回。

工具链与部署目标见[模块 README](README.md)，以练习工程的实际 Xcode、SDK 和目标系统配置为准。官方学习入口：[Apple Develop in Swift](https://developer.apple.com/tutorials/develop-in-swift)。Swift 命令行语法通过不等于 SwiftUI 工程已在目标设备运行。

1. [环境搭建 - Xcode 与 Swift 工具链](basics/01-environment-setup.md)
2. [Swift 语法 Essentials - 写 SwiftUI 前必须会的 Swift](basics/03-swift-syntax-essentials.md)
3. [第一个 SwiftUI App - 声明式 UI 入门](basics/02-first-swiftui-app.md)
4. [View 协议与状态管理 - @State、@Binding 与 @Observable](basics/04-views-state.md)
5. [布局系统 - Stack、Spacer 与滚动容器](basics/05-layouts.md)
6. [导航 - NavigationStack、TabView 与模态呈现](basics/06-navigation.md)
7. [Swift 并发 - async/await、Task 与 Actor](basics/07-concurrency-async-await.md)
8. [第一个完整项目 - 待办记账 App（SwiftUI + SwiftData）](basics/08-first-project.md)

## 三个阶段如何验收

| 阶段与入口 | 练习输入与动作 | 通过条件 |
| --- | --- | --- |
| 状态与绑定：[视图状态](basics/04-views-state.md) | 父视图展示数字，子视图增加和重置 | 数值一致；能解释 Binding 修改的是哪份状态 |
| 导航与持久化：[导航](basics/06-navigation.md)、[笔记应用](projects/01-notes-app.md) | 编辑笔记、进入详情再返回、保存后终止应用并重新启动 | 分别解释导航保留与持久化；数据库保存的内容可读回，空白输入按约定处理 |
| 异步请求：[并发入门](basics/07-concurrency-async-await.md)、[天气应用](projects/02-weather-app.md) | 成功、请求失败、请求中离开页面 | 有加载和恢复入口；取消与真正失败区分处理。验收在声明的 Apple 目标上执行，不能用 Linux 解析代替 |

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

## 框架与高级主题怎么选

先 SwiftUI，再根据需要引入 Observation、SwiftData 与 URLSession。SwiftData 的部署目标和迁移方案是工程条件；不能因为样例简短就跳过数据演进。

## 全量参考怎么查

关键词解决“语法是什么意思”，内置函数解决“直接能调用什么”，标准库解决“导入以后能做什么”。框架 API 另列，避免把库函数误当成语言本身。以下是现有文章的完整导航，不代表每个 API 都已充分讲解；具体覆盖缺口进入审查台账。

### framework-essentials

- [SwiftUI 核心视图与修饰符速查](reference/framework-essentials/01-swiftui-essentials.md)
- [SwiftData 与 Observation 框架速查](reference/framework-essentials/02-swiftdata-observability.md)
- [状态驱动视图（UI = f(state)）](reference/framework-essentials/03-state-driven-views.md)
- [ViewModifier 与修饰符链](reference/framework-essentials/04-view-modifier.md)
- [数据流与 Environment](reference/framework-essentials/05-data-flow.md)
- [SwiftUI Charts 数据可视化速查](reference/framework-essentials/06-swift-charts.md)
- [SwiftData 模型迁移速查](reference/framework-essentials/07-swiftdata-migration.md)
- [SwiftUI 手势 API 速查](reference/framework-essentials/08-gestures.md)

### language-concepts

- [Swift 关键字详解](reference/language-concepts/01-swift-keywords.md)
- [可选值与集合 API 速查](reference/language-concepts/02-optionals-collections.md)
- [Swift 并发 API 全表](reference/language-concepts/03-concurrency-api.md)
- [SwiftUI 状态属性包装器全表](reference/language-concepts/04-swiftui-state-api.md)
- [协议与泛型速查](reference/language-concepts/05-protocols-generics.md)
- [闭包与函数类型](reference/language-concepts/06-closures.md)
- [枚举与模式匹配](reference/language-concepts/07-enums-pattern-matching.md)
- [错误处理](reference/language-concepts/08-error-handling.md)
- [属性包装器（Property Wrapper）](reference/language-concepts/09-property-wrappers.md)
- [值类型、引用类型与 ARC](reference/language-concepts/10-value-types-arc.md)
- [Actor 隔离与 Sendable](reference/language-concepts/11-actors-sendability.md)
- [Swift 构造过程（Initialization）详解](reference/language-concepts/12-initialization.md)
- [Swift 关键字全量分组清单](reference/language-concepts/13-keywords-completion.md)
- [Swift 正则（Regex 与 RegexBuilder）](reference/language-concepts/14-regex.md)
- [URLSession 网络基础](reference/language-concepts/15-urlsession.md)
- [stdlib / Foundation 与系统框架低频地图](reference/language-concepts/16-stdlib-foundation-map.md)

### library-guides

- [Foundation 与标准库核心速查](reference/library-guides/01-foundation-and-stdlib.md)
- [常用第三方库速查](reference/library-guides/02-third-party-libs.md)

### quick-references

- [Swift + SwiftUI 一行式速查表](reference/quick-references/01-swift-swiftui-cheatsheet.md)
- [常见错误与故障排除](reference/quick-references/02-troubleshooting.md)

## 卡住时

先判断是术语不懂、输入输出不清、代码上下文缺失，还是运行环境不同。返回[学习方法](../shared-resources/learning-guide.md)按证据排查；通用术语见[术语解释](../shared-resources/glossary.md)。
