# 05 Kotlin Compose - Kotlin 2.4 + Jetpack Compose 现代化 Android 开发

> **本轮增强与版本核对**：学习路径及正文增强范围见 [逐文件台账](../shared-resources/tools/document-quality/reports/coverage.md)。下方技术基线中的旧核对日期属于历史记录，不表示这次已重跑所有平台；安装与升级以官方兼容要求、项目锁文件和实际构建结果为准。


> 第一次学习请从[理解地图与学习规划](LEARNING_GUIDE.md)开始；按关键词查阅可直接使用其中的完整参考导航。

> **文档简介**: 05-kotlin-compose 模块总览——面向有 Go 后端与现代前端经验的学习者的 Android 原生开发完整学习路径
>
> **技术栈基线**: Kotlin 2.4（K2 编译器）· Jetpack Compose（BOM 2026.09.00）+ Material 3 · Android Studio（Quail 或更新）· Gradle Kotlin DSL——具体版本见下方「技术基线」
>
> **更新日期**: 2026年9月

## 📐 技术基线（核实日期 2026-09-16）

| 技术 | 当前稳定版本 | 说明 |
|------|------------|------|
| **Kotlin** | 2.4（2.4.0 于 2026-06-03 发布，最新补丁 2.4.20） | K2 编译器唯一引擎，已移除 K1 与 `-language-version=1.9`；上下文参数、显式后备字段转正 |
| **Jetpack Compose BOM** | 2026.09.00 | 2026 年 9 月版（Google Maven group-index 实核），核心库（Animation/Foundation/Runtime/UI）统一 1.12.x |
| **Material 3** | 1.4.0（随 BOM 分发） | Compose 依赖一律走 BOM，不单独写版本号 |
| **AGP** | 9.4.0（2026-09-01） | 要求 Gradle 9.6.0、JDK 17；最高支持 compileSdk 37 |
| **Android Studio** | Quail（2026.1.4） | 兼容 AGP 7.1–9.4 |
| **KSP** | 2.3.x | KSP 已改用独立版本号，与 Kotlin 版本解耦 |
| **targetSdk** | 36（Android 16） | Play 2026 年新提交要求线；Android 17（API 37）尚在 Beta |

> 模块内示例默认不锁定上述版本（统一经 `gradle/libs.versions.toml` 管理，以官方最新稳定版为准）；少数涉及具体版本号的示例已按本表基线书写。

## 🧭 模块定位

本模块专为有 **Go 后端和现代前端开发经验**的学习者设计，系统掌握 Android 原生开发技术。Android 开发已全面进入 Jetpack Compose 声明式 UI 时代，本模块以 **Kotlin 2.4（K2 编译器）+ Jetpack Compose + Material 3** 为基线，帮你构建高性能、可发布、可维护的现代化 Android 应用。

**学习目标**：

- 掌握 Kotlin 2.4 语言特性与协程/Flow 并发范式
- 熟练使用 Jetpack Compose 进行声明式 UI 开发（状态驱动、组合模型）
- 理解现代 Android 分层架构与单向数据流（UDF），打通 Room + Hilt + Retrofit + ViewModel 完整链路
- 完成从入门项目到生产级应用的四个递进实战，掌握测试、签名发布与线上可观测性
- 与 SwiftUI（[06 模块](../06-swift-swiftui/README.md)）、跨平台方案（[04 模块](../04-multiplatform-apps/README.md)）形成声明式 UI 与移动端技术对照

## 🗺️ 四象限导览

| 象限 | 目录 | 内容 | 状态 |
|------|------|------|------|
| 📖 **教程**（带我入门） | [basics/](basics/) | 8 篇按序教程：环境搭建 → 第一个 Compose 应用 → Kotlin 语法 → Composable 与状态 → 布局 → 导航 → 协程与 Flow → 第一个项目 | ✅ 8 篇 |
| 📚 **字典**（X 是什么） | [reference/](reference/) | 26 篇全量参考：语言概念 11（含关键字总索引/集合操作/序列/文本正则）、框架要点 10（含组合模型/手势/画布）、库指南 3、速查与排障 2 | ✅ 26 篇 |
| 🏗️ **操作指南**（怎么做事） | [frameworks/](frameworks/) | Compose 基础/进阶、生态集成（Room+Hilt+Retrofit+ViewModel）、开发工具链 | ✅ 4 篇 |
| 🏗️ **操作指南** | [projects/](projects/) | 4 个递进实战：笔记应用 → 天气应用 → 新闻阅读器 → 生产级应用 | ✅ 4 篇 |
| 🏗️ **操作指南** | [testing/](testing/) | 单元测试（JUnit+MockK）、Compose UI 测试、集成与端到端 | ✅ 3 篇 |
| 🏗️ **操作指南** | [deployment/](deployment/) | 签名与混淆构建、Play Store 上架、GitHub Actions + Crashlytics | ✅ 3 篇 |
| 🎓 **解释**（为什么这样设计） | [advanced-topics/](advanced-topics/) | 分层架构与 UDF、重组优化、启动与内存、安全实践（均 ⭐⭐⭐） | ✅ 4 篇 |

**单一事实来源**：完整参考以 `reference/` 为主；教程就地解释当前步骤所需概念，再链接完整条目。

## 🛤️ 学习路径

### 入门路径（⭐）

[环境搭建](basics/01-environment-setup.md) → [第一个 Compose 应用](basics/02-first-compose-app.md) → [Kotlin 语法基础](basics/03-kotlin-syntax-essentials.md) → [Composable 与状态](basics/04-composables-state.md) → [布局系统](basics/05-layouts.md) → [页面导航](basics/06-navigation.md) → [协程与 Flow 基础](basics/07-coroutines-flow-basics.md) → [第一个项目](basics/08-first-project.md) → [Compose 入门核心](frameworks/01-compose-basics.md) → [开发工具链](frameworks/04-devtools.md) → [实战：本地笔记应用](projects/01-notes-app.md)

### 进阶路径（⭐⭐）

[Compose 进阶：侧效应/导航/动画](frameworks/02-compose-advanced.md) → [生态集成四件套](frameworks/03-ecosystem-integration.md) → [单元测试](testing/01-unit-testing.md) → [Compose UI 测试](testing/02-ui-testing.md) → [实战：天气应用](projects/02-weather-app.md) → [实战：新闻阅读器](projects/03-news-reader.md) → [发布构建](deployment/01-release-build.md) → [Play Store 上架](deployment/02-play-store-release.md)

### 精通路径（⭐⭐⭐）

[应用架构与 UDF](advanced-topics/architecture/01-app-architecture.md) → [重组优化](advanced-topics/performance/01-recomposition-optimization.md) → [启动与内存优化](advanced-topics/performance/02-startup-memory.md) → [安全实践](advanced-topics/security/01-security-practices.md) → [集成与端到端测试](testing/03-integration-e2e-testing.md) → [CI/CD 与可观测性](deployment/03-ci-cd-observability.md) → [实战：生产级 Android 应用](projects/04-production-android-app.md)

## 📁 实际文件树

```
05-kotlin-compose/
├── README.md                              # 本文档
├── Android原生开发学习路线.md             # 历史规划文档（旧版路线，现行标准见 shared-resources/standards/）
├── basics/                                # 📖 教程
│   ├── 01-environment-setup.md            #   ⭐ 环境搭建
│   ├── 02-first-compose-app.md            #   ⭐ 第一个 Compose 应用
│   ├── 03-kotlin-syntax-essentials.md     #   ⭐ Kotlin 语法基础
│   ├── 04-composables-state.md            #   ⭐ Composable 与状态
│   ├── 05-layouts.md                      #   ⭐ 布局系统
│   ├── 06-navigation.md                   #   ⭐ 页面导航
│   ├── 07-coroutines-flow-basics.md       #   ⭐ 协程与 Flow 基础
│   └── 08-first-project.md                #   ⭐ 第一个项目
├── reference/                             # 📚 字典
│   ├── language-concepts/
│   │   ├── 01-kotlin-keywords.md          #   Kotlin 关键字与修饰符
│   │   ├── 02-null-safety-collections.md  #   可空性与集合 API
│   │   ├── 03-coroutines-flow-api.md      #   协程与 Flow API 全表
│   │   ├── 04-compose-state-api.md        #   Compose 状态 API
│   │   ├── 05-generics-delegates.md       #   泛型与委托属性
│   │   ├── 06-extension-functions.md      #   扩展函数与扩展属性
│   │   ├── 07-scope-functions.md          #   作用域函数
│   │   └── 08-lambdas-higher-order.md     #   Lambda 与高阶函数
│   ├── framework-essentials/
│   │   ├── 01-compose-essentials.md       #   Compose 核心组件速查
│   │   ├── 02-compose-material3.md        #   Material 3 主题系统速查
│   │   ├── 03-side-effects.md             #   副作用 API 速查
│   │   ├── 04-recomposition.md            #   重组与稳定性速查
│   │   ├── 05-animation-core.md           #   动画核心 API 速查
│   │   ├── 06-navigation-components.md    #   Navigation Compose 组件速查
│   │   └── 07-compose-testing.md          #   Compose 测试 API 速查
│   ├── library-guides/
│   │   ├── 01-androidx-libraries.md       #   AndroidX 官方库指南
│   │   ├── 02-third-party-libs.md         #   第三方库指南
│   │   └── 03-ksp-configuration.md        #   KSP 代码生成配置指南
│   └── quick-references/
│       ├── 01-kotlin-compose-cheatsheet.md #  一行式速查表
│       └── 02-troubleshooting.md          #   常见错误与故障排除
├── frameworks/                            # 🏗️ 操作指南：框架生态
│   ├── 01-compose-basics.md               #   ⭐ Compose 入门核心
│   ├── 02-compose-advanced.md             #   ⭐⭐ Compose 进阶（侧效应/导航/动画）
│   ├── 03-ecosystem-integration.md        #   ⭐⭐ Room+Hilt+Retrofit+ViewModel 集成
│   └── 04-devtools.md                     #   ⭐ 开发工具链
├── projects/                              # 🚀 操作指南：实战项目
│   ├── 01-notes-app.md                    #   ⭐ 本地笔记应用
│   ├── 02-weather-app.md                  #   ⭐⭐ 天气应用（网络+定位）
│   ├── 03-news-reader.md                  #   ⭐⭐ 新闻阅读器（分页+缓存）
│   └── 04-production-android-app.md       #   ⭐⭐⭐ 生产级 Android 应用
├── testing/                               # 🧪 操作指南：测试工程
│   ├── 01-unit-testing.md                 #   ⭐⭐ 单元测试（JUnit+MockK+协程测试）
│   ├── 02-ui-testing.md                   #   ⭐⭐ Compose UI 测试
│   └── 03-integration-e2e-testing.md      #   ⭐⭐⭐ 集成与端到端测试
├── deployment/                            # 🚀 操作指南：部署运维
│   ├── 01-release-build.md                #   ⭐⭐ 签名、混淆与多渠道
│   ├── 02-play-store-release.md           #   ⭐⭐ Play Store 上架流程
│   └── 03-ci-cd-observability.md          #   ⭐⭐⭐ GitHub Actions + Crashlytics
└── advanced-topics/                       # 🎓 深度解释（均 ⭐⭐⭐）
    ├── architecture/
    │   └── 01-app-architecture.md         #   官方分层架构与 UDF
    ├── performance/
    │   ├── 01-recomposition-optimization.md # 重组优化
    │   └── 02-startup-memory.md           #   启动与内存优化
    └── security/
        └── 01-security-practices.md       #   安全实践
```

## 🔗 关联模块

- **[04-multiplatform-apps](../04-multiplatform-apps/README.md)** — React Native 跨端视角：JS 声明式 UI 与本模块的 Kotlin Compose 对照学习（Compose Multiplatform 属 KMP 生态，本模块聚焦 Android 官方栈）
- **[06-swift-swiftui](../06-swift-swiftui/README.md)** — iOS 平行的声明式 UI 体系：SwiftUI 与 Compose 的状态管理、布局思想可对照学习

---

*最后更新: 2026年9月*
