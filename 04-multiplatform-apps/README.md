# React Native 三端原生应用开发 — Android + iOS + 鸿蒙

> **模块简介**: 专注 React Native 跨平台原生应用开发，一套 TypeScript 代码覆盖 Android、iOS、鸿蒙（HarmonyOS，经 RNOH 适配）三端，实现原生级用户体验与生态全覆盖
>
> **技术栈**: React Native 0.7x 新架构（Fabric 渲染器 + TurboModules）· Expo SDK 最新稳定版 · TypeScript · Reanimated 3 · Expo Router / EAS
>
> **目标读者**: 有 React/TypeScript 基础、准备进入移动端开发的工程师，直至主导生产级应用交付的资深开发者

## 📚 模块元数据

| 属性 | 内容 |
|------|------|
| **模块类型** | 跨平台原生应用开发（应用帝国矩阵 · 核心重点） |
| **核心框架** | React Native 0.7x 新架构 + Expo SDK |
| **目标平台** | Android + iOS + HarmonyOS（RNOH） |
| **内容形式** | 纯文档学习路径（本仓库无可运行代码） |
| **更新日期** | 2026年9月 |
| **维护团队** | Dev Quest Team |

## 🎯 学习目标

完成本模块后，你将能够：

- ✅ **三端原生开发**：用 React Native 开发 Android、iOS、鸿蒙（RNOH 适配）原生应用
- ✅ **新架构素养**：理解 Fabric/TurboModules/JSI 并据此写出正确的性能代码
- ✅ **生态整合**：熟练使用 Expo Router、EAS、Zustand、MMKV 等主流生态工具
- ✅ **工程化交付**：建立"测试 → 构建 → 上架 → OTA → 监控"的完整发布闭环
- ✅ **生产级运营**：以崩溃率、启动耗时等质量指标运营真实应用

## 🧭 四象限导览

| 象限 | 目录 | 内容定位 | 文档 |
|------|------|---------|------|
| **教程** | `basics/` | 按序学习的入门教程，从环境搭建到第一个完整项目 | 8 篇 |
| **字典** | `reference/` | 全量参考条目，无难度门槛，任意跳入查阅 | 11 篇 |
| **操作指南** | `frameworks/` | React Native 框架从入门到进阶的任务式指南 + 生态集成 + 调试工具 | 4 篇 |
| **操作指南** | `projects/` | 四个递进实战项目：待办 → 天气 → 聊天 → 生产级 | 4 篇 |
| **操作指南** | `testing/` | Jest 单测 / RNTL 组件测试 / Maestro E2E 三层测试体系 | 3 篇 |
| **操作指南** | `deployment/` | EAS 构建 → 双商店上架 → OTA 与可观测性 | 3 篇 |
| **解释** | `advanced-topics/` | 新架构原理、渲染/启动性能、安全实践的深度剖析 | 4 篇 |

**单一事实来源**：概念的完整解释只在 `reference/` 存在一份，其他目录链接过去。查概念先翻字典，学技能按路径走。

## 🛤️ 学习路径

### 入门路径（⭐）

零基础到第一个可交付的跨平台应用：

[环境搭建](basics/01-environment-setup.md) → [第一个 App](basics/02-first-app.md) → [核心组件与 Flexbox](basics/03-components-jsx.md) → [状态与 Hooks](basics/04-state-hooks.md) → [导航基础](basics/05-navigation.md) → [综合练习：待办记账 App](basics/08-first-project.md) → [RN 框架入门](frameworks/01-react-native-basics.md) → [实战：待办应用](projects/01-todo-app.md)

### 进阶路径（⭐⭐）

原生能力、新架构开发与工程化：

[原生模块桥接](basics/06-native-modules.md) → [高级特性：Fabric/Hermes/动画](basics/07-advanced-features.md) → [RN 框架进阶](frameworks/02-react-native-advanced.md) → [生态集成](frameworks/03-ecosystem-integration.md) → [开发工具链](frameworks/04-devtools.md) → [实战：天气应用](projects/02-weather-app.md) → [实战：聊天应用](projects/03-chat-app.md) → [单元测试](testing/01-unit-testing.md) → [组件测试](testing/02-component-testing.md) → [端到端测试](testing/03-e2e-testing.md) → [EAS Build](deployment/01-eas-build.md) → [商店上架](deployment/02-app-store-release.md)

### 精通路径（⭐⭐⭐）

架构理解、性能攻坚与生产运营：

[新架构解析：Fabric/TurboModules/JSI](advanced-topics/architecture/01-new-architecture.md) → [渲染性能](advanced-topics/performance/01-rendering-performance.md) → [启动优化](advanced-topics/performance/02-startup-optimization.md) → [OTA 更新与可观测性](deployment/03-ota-updates-observability.md) → [安全实践](advanced-topics/security/01-security-practices.md) → [实战：生产级移动应用](projects/04-production-mobile-app.md)

> 💡 字典（reference/）不在任何路径中——它陪伴全程：遇到概念随时查 [核心 API](reference/language-concepts/01-rn-core-api.md)、[组件 Props](reference/language-concepts/02-components-props.md)、[Hooks 速查](reference/language-concepts/03-hooks-reference.md)、[CLI 与调试速查](reference/quick-references/01-cli-and-debug-cheatsheet.md)。

## 📁 实际文件树

```text
04-multiplatform-apps/
├── README.md                                   # 本文档
├── React Native三端原生应用学习路线.md            # 历史规划文档（存档）
├── basics/                                     # 教程：按序学习入门
│   ├── 01-environment-setup.md                 # ⭐ 环境搭建
│   ├── 02-first-app.md                         # ⭐ 第一个 App
│   ├── 03-components-jsx.md                    # ⭐ 核心组件、JSX 与 Flexbox
│   ├── 04-state-hooks.md                       # ⭐ 状态与 Hooks
│   ├── 05-navigation.md                        # ⭐ 导航基础
│   ├── 06-native-modules.md                    # ⭐⭐ 原生模块桥接
│   ├── 07-advanced-features.md                 # ⭐⭐ Fabric、Hermes 与动画
│   └── 08-first-project.md                     # ⭐ 综合练习：待办记账 App
├── reference/                                  # 字典：全量参考，无难度门槛
│   ├── language-concepts/
│   │   ├── 01-rn-core-api.md                   # RN 核心 API
│   │   ├── 02-components-props.md              # 核心组件 Props 全表
│   │   ├── 03-hooks-reference.md               # Hooks 速查
│   │   ├── 04-typescript-patterns.md           # TypeScript 类型模式
│   │   └── 05-harmonyos-rnoh-api.md            # RNOH 鸿蒙适配字典
│   ├── framework-essentials/
│   │   ├── 01-expo-essentials.md               # Expo 要点（Router/EAS）
│   │   └── 02-navigation-essentials.md         # React Navigation 速查
│   ├── library-guides/
│   │   ├── 01-state-and-data.md                # 状态与数据请求库
│   │   └── 02-native-and-device-libs.md        # 原生与设备能力库
│   └── quick-references/
│       ├── 01-cli-and-debug-cheatsheet.md      # CLI 与调试速查
│       └── 02-troubleshooting.md               # 故障排除
├── frameworks/                                 # 操作指南：框架生态
│   ├── 01-react-native-basics.md               # ⭐ 组件、样式与 Flexbox
│   ├── 02-react-native-advanced.md             # ⭐⭐ 新架构、原生模块与动画
│   ├── 03-ecosystem-integration.md             # ⭐⭐ Expo Router、EAS 与库选型
│   └── 04-devtools.md                          # ⭐ 调试与性能工具链
├── projects/                                   # 操作指南：实战项目（⭐ 递进）
│   ├── 01-todo-app.md                          # ⭐ 待办应用
│   ├── 02-weather-app.md                       # ⭐⭐ 天气应用（网络 + 定位）
│   ├── 03-chat-app.md                          # ⭐⭐ 聊天应用（实时 + 列表优化）
│   └── 04-production-mobile-app.md             # ⭐⭐⭐ 生产级移动应用
├── testing/                                    # 操作指南：测试工程
│   ├── 01-unit-testing.md                      # Jest 单元测试
│   ├── 02-component-testing.md                 # RNTL 组件测试
│   └── 03-e2e-testing.md                       # Maestro/Detox 端到端
├── deployment/                                 # 操作指南：部署运维
│   ├── 01-eas-build.md                         # EAS Build 构建流程
│   ├── 02-app-store-release.md                 # App Store / Google Play 上架
│   └── 03-ota-updates-observability.md         # OTA 更新 + Sentry/Crashlytics
└── advanced-topics/                            # 解释：原理与架构
    ├── architecture/
    │   └── 01-new-architecture.md              # ⭐⭐⭐ Fabric/TurboModules/JSI
    ├── performance/
    │   ├── 01-rendering-performance.md         # ⭐⭐⭐ 渲染性能
    │   └── 02-startup-optimization.md          # ⭐⭐⭐ 启动优化
    └── security/
        └── 01-security-practices.md            # ⭐⭐⭐ 安全实践
```

## 🔗 关联模块

- **[05-kotlin-compose](../05-kotlin-compose/README.md)** — Android 原生深水区：RNOH 鸿蒙模块的原生侧与 RN Android 原生模块（Kotlin）的技术底座
- **[06-swift-swiftui](../06-swift-swiftui/README.md)** — iOS 原生深水区：RN iOS 原生模块（Swift）与苹果生态特性的技术底座
- **[02-nextjs-frontend](../02-nextjs-frontend/README.md)** — Web 前端主战场：React 思维、组件模型与状态管理在此深入，与 RN 共享 React 心智模型

---

**模块状态**: ✅ 双轨结构完整（basics 8 篇 + reference 11 篇 + 第二波 15 篇）
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team

> 💡 **学习提示**：跨平台的价值在于一套代码服务多端用户。按入门 → 进阶 → 精通三条路径推进，字典随查随用；鸿蒙（RNOH）作为第三端贯穿各专题文档，版本对齐永远先查 [RNOH 字典](reference/language-concepts/05-harmonyos-rnoh-api.md)。
