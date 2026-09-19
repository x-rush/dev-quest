# React Native 三端原生应用开发 — Android + iOS + 鸿蒙

> **本轮增强与版本核对**：学习路径及正文增强范围见 [逐文件台账](../shared-resources/tools/document-quality/reports/coverage.md)。下方技术基线中的旧核对日期属于历史记录，不表示这次已重跑所有平台；安装与升级以官方兼容要求、项目锁文件和实际构建结果为准。


第一次学习请从[理解地图与学习规划](LEARNING_GUIDE.md)开始，按其中的阶段任务和验收条件推进。先选 Android 或 iOS 一个平台运行待办应用，完成输入、列表和存储。第二平台、原生桥接与鸿蒙适配各有环境和依赖要求，分别学习与验收。

查语法、函数或库时使用下方参考目录；JavaScript 基础分别从共享的[关键词](../shared-resources/javascript-keywords.md)、[内置能力](../shared-resources/javascript-builtins.md)和[标准库与宿主能力](../shared-resources/javascript-standard-library.md)进入。文件数量与目录中的完成标记表示内容组织情况，不能替代示例运行证据；具体交付按[知识库质量基线](../shared-resources/standards/knowledge-delivery-baseline.md)验收。

> **模块简介**: 学习 React Native 的组件、状态、导航与原生能力；先完成单平台应用，再根据具体依赖与适配方案验证 Android、iOS 或鸿蒙目标
>
> **技术栈**: React Native 0.87 新架构（Fabric 渲染器 + TurboModules，旧架构已移除）· Expo SDK 57 · TypeScript · Reanimated 4 · Expo Router / EAS
>
> **目标读者**: 会基本编程、准备学习移动端的开发者；React 与 TypeScript 不熟时先完成导读列出的补课项

## 🧪 技术基线（核实日期：2026-09-16）

> 核实来源：[React Native 0.87 发布博客](https://reactnative.dev/blog/2026/08/11/react-native-0.87)、[React Native Releases Overview](https://reactnative.dev/releases/overview)、[Expo SDK 57 Changelog](https://expo.dev/changelog/sdk-57)、[Expo SDK 版本对照表](https://docs.expo.dev/versions/v57.0.0/)。各文档正文以概念为主，具体版本断言以本表与官方发布页为准。

| 技术 | 当前版本 | 关键事实 |
|------|---------|---------|
| **React Native** | **0.87**（2026-08-10 发布） | 最新稳定；支持窗口 0.85–0.87；Strict TypeScript API 成为默认 JS API；Metro 0.87；实验性 Swift Package Manager；最低 Node.js 22 / AGP 9 / Kotlin 2.0+ |
| **新架构** | 唯一架构 | 0.76 起默认开启；自 RN 0.82 起（SDK 55+）新架构成为唯一架构，旧架构不再可启用；Legacy 组件已在 0.84–0.85 移除 |
| **Expo SDK** | **57**（2026-06-30 发布） | 配套 RN 0.86 + React 19.2.3；最低 Node 22.13；Xcode 26.4+ / iOS 16.4+ / Android compileSdk 36；修复 SDK 56 的 Hermes V1 内存回归 |
| **React** | **19.2.x**（19.2.3） | **依赖锁版本**：随 SDK 57 / RN 0.86 锁定，不跟随 npm latest（19.3.0 已发布，2026-09-16 实核）单独升级；待 SDK 58 配套 19.3 时随 SDK 一并刷新 |
| **TypeScript** | **7.0**（Go 原生编译器版，npm latest 7.0.2） | 7.0 已 GA；Expo 模板随 SDK 附带对应版本，无特殊配置需求 |
| **Expo Router** | **57.x** | 自 SDK 55 起与 SDK 同步版本号；SDK 56 起不再支持从应用代码直接 import `@react-navigation/*` 包 |
| **Reanimated** | **4.x** | 仅支持新架构（v4 随 SDK 54 起线）；babel 插件移交 `react-native-worklets`，`babel-preset-expo` 自动处理 |
| **Hermes** | **V1 默认** | RN 0.84 起 V1 引擎为默认；调试统一走 React Native DevTools（Flipper 已移除） |

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 模块元数据

| 属性 | 内容 |
|------|------|
| **模块类型** | 跨平台原生应用开发（应用帝国矩阵 · 核心重点） |
| **核心框架** | React Native 0.87 新架构 + Expo SDK 57 |
| **目标平台** | Android + iOS + HarmonyOS（RNOH） |
| **内容形式** | 纯文档学习路径（本模块不随仓库分发可直接启动的 React Native 工程；正文片段须在学习者自己的目标工具链复测） |
| **更新日期** | 2026年9月 |
| **维护团队** | Dev Quest Team |

</details>

## 🎯 学习目标

按下面关卡推进，你先交付一个有输入校验、列表和本地存储的单平台应用，再按需求学习原生能力、第二平台和发布。阅读完目录不代表掌握三端适配或具备生产交付能力。

- 解释组件输入、状态拥有者和事件回调，让一次点击改变原生界面。
- 拒绝非法输入，保存有效数据，并在终止应用后读回；失败时保留可重试的输入。
- 为每个实际使用的平台记录依赖、构建与设备结果；鸿蒙的 RNOH 适配另行验证。
- 基础闭环完成后再选择原生模块，需要发布时进入构建、上架和更新专题。

## 🧭 四象限导览

| 象限 | 目录 | 内容定位 | 文档 |
|------|------|---------|------|
| **教程** | `basics/` | 按序学习的入门教程，从环境搭建到第一个完整项目 | 8 篇 |
| **字典** | `reference/` | 全量参考条目，可独立查阅，仍有前置知识，任意跳入查阅 | 23 篇 |
| **操作指南** | `frameworks/` | React Native 框架从入门到进阶的任务式指南 + 生态集成 + 调试工具 | 4 篇 |
| **操作指南** | `projects/` | 四个递进实战项目：待办 → 天气 → 聊天 → 生产级 | 4 篇 |
| **操作指南** | `testing/` | Jest 单测 / RNTL 组件测试 / Maestro E2E 三层测试体系 | 3 篇 |
| **操作指南** | `deployment/` | EAS 构建 → 双商店上架 → OTA 与可观测性 | 3 篇 |
| **解释** | `advanced-topics/` | 新架构原理、渲染/启动性能、安全实践的深度剖析 | 4 篇 |

**单一事实来源**：完整参考以 `reference/` 为主；教程就地解释当前步骤所需概念，再链接完整条目。查概念先翻字典，学技能按路径走。

## 🛤️ 学习路径

### 入门路径（⭐）

面向已有基本编程经验的单平台入门路线：

[环境搭建](basics/01-environment-setup.md) → [第一个 App](basics/02-first-app.md) → [核心组件与 Flexbox](basics/03-components-jsx.md) → [状态与 Hooks](basics/04-state-hooks.md) → [导航基础](basics/05-navigation.md) → [综合练习：待办记账 App](basics/08-first-project.md) → [RN 框架入门](frameworks/01-react-native-basics.md) → [实战：待办应用](projects/01-todo-app.md)

> 注：basics/06、07 两篇为 ⭐⭐ 深化内容（平台差异与原生桥接），建议完成入门路径后再读。

### 第一次动手：每次只增加一种不确定性

前置自检：能用 TypeScript 定义带 `id`、`title` 的对象，能用 `map` 返回新数组，能解释 Promise 的成功与失败分支。不熟悉 React 时先做[状态与 Hooks](basics/04-state-hooks.md)中的计数器，知道为什么直接改普通变量不能作为界面状态更新方式。完整阅读顺序见[学习规划](LEARNING_GUIDE.md)。

| 关卡 | 动作与产物 | 成功标准；失败后的恢复路径 |
|---|---|---|
| 1. 固定环境 | 按[环境篇](basics/01-environment-setup.md)选择 Expo 或自行管理原生工程；只选一个目标设备。保存工程、锁文件与 Node/SDK/设备版本 | 模板 App 实际打开并显示自定义文本；Metro 启动但手机未显示不算通过。先恢复模板可运行状态，再排查连接或原生构建日志 |
| 2. 状态闭环 | 增加受控输入、添加按钮和列表；输入 A/B，删除 B。先保持数据在内存中 | 列表只剩 A，空白输入不生成条目；无变化回查[核心组件](basics/03-components-jsx.md)及状态篇的输入、事件与数组更新，不先接存储 |
| 3. 持久化闭环 | 进入[首项目](basics/08-first-project.md)先完成记账；输入 `0.10`、`0.20`，再做[待办](projects/01-todo-app.md)。保存操作和重启结果 | 合计 0.30，待办 A 保留、B 不恢复。保存失败应显示错误并保留输入；无设备或未注入失败时如实记为未验证 |
| 4. 合并功能 | 按首项目第二阶段组合标签页和统计，交付源码、锁文件及用例记录 | 页面切换不产生重复数据，统计与列表一致；先回查存储键和状态来源，修好后再重复第三关 |

Expo SDK 与 React Native 是配套版本关系，不要把本页表格的 RN 独立版本强塞进 Expo 工程。变更依赖后按[官方升级流程](https://docs.expo.dev/workflow/upgrading-expo-sdk-walkthrough/)检查依赖兼容，并在涉及原生变化时重建开发客户端。Expo Go、development build 与商店发布构建分别记录，不能互相替代验收。

最小交付记录写清“工程版本、平台、操作、期望、实际、失败恢复结果”。本页只组织学习路线，本轮未运行 Android/iOS/RNOH 工程；以上标准是学习者需执行的任务。

### 进阶路径（⭐⭐）

原生能力、新架构开发与工程化：

[原生模块桥接](basics/06-native-modules.md) → [高级特性：Fabric/Hermes/动画](basics/07-advanced-features.md) → [RN 框架进阶](frameworks/02-react-native-advanced.md) → [生态集成](frameworks/03-ecosystem-integration.md) → [开发工具链](frameworks/04-devtools.md) → [实战：天气应用](projects/02-weather-app.md) → [实战：聊天应用](projects/03-chat-app.md) → [单元测试](testing/01-unit-testing.md) → [组件测试](testing/02-component-testing.md) → [端到端测试](testing/03-e2e-testing.md) → [EAS Build](deployment/01-eas-build.md) → [商店上架](deployment/02-app-store-release.md)

### 精通路径（⭐⭐⭐）

架构理解、性能攻坚与生产运营：

[新架构解析：Fabric/TurboModules/JSI](advanced-topics/architecture/01-new-architecture.md) → [渲染性能](advanced-topics/performance/01-rendering-performance.md) → [启动优化](advanced-topics/performance/02-startup-optimization.md) → [OTA 更新与可观测性](deployment/03-ota-updates-observability.md) → [安全实践](advanced-topics/security/01-security-practices.md) → [实战：生产级移动应用](projects/04-production-mobile-app.md)

> 💡 字典（reference/）不在任何路径中——它陪伴全程：遇到概念随时查 [核心 API](reference/language-concepts/01-rn-core-api.md)、[组件 Props](reference/language-concepts/02-components-props.md)、[Hooks 速查](reference/language-concepts/03-hooks-reference.md)、[组件生命周期](reference/language-concepts/06-component-lifecycle.md)、[状态管理模型](reference/language-concepts/07-state-management.md)、[桥接与原生通信原理](reference/language-concepts/08-bridge-principles.md)、[导航模型](reference/language-concepts/09-navigation-model.md)、[新架构术语](reference/language-concepts/11-new-architecture-terms.md)、[列表性能模型](reference/language-concepts/12-list-performance-model.md)、[平台 API 地图](reference/language-concepts/13-platform-api-map.md)、[CLI 与调试速查](reference/quick-references/01-cli-and-debug-cheatsheet.md)。

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
├── reference/                                  # 字典：全量参考，可独立查阅，仍有前置知识
│   ├── language-concepts/
│   │   ├── 01-rn-core-api.md                   # RN 核心 API
│   │   ├── 02-components-props.md              # 核心组件 Props 全表
│   │   ├── 03-hooks-reference.md               # Hooks 速查
│   │   ├── 04-typescript-patterns.md           # TypeScript 类型模式
│   │   ├── 05-harmonyos-rnoh-api.md            # RNOH 鸿蒙适配字典
│   │   ├── 06-component-lifecycle.md           # 组件生命周期
│   │   ├── 07-state-management.md              # 状态管理模型
│   │   ├── 08-bridge-principles.md             # 桥接与原生通信原理
│   │   ├── 09-navigation-model.md              # 导航模型
│   │   ├── 10-styling-model.md                 # 样式与布局模型
│   │   ├── 11-new-architecture-terms.md        # 新架构术语
│   │   ├── 12-list-performance-model.md        # 列表性能模型
│   │   └── 13-platform-api-map.md              # 平台 API 地图
│   ├── framework-essentials/
│   │   ├── 01-expo-essentials.md               # Expo 要点（Router/EAS）
│   │   ├── 02-navigation-essentials.md         # React Navigation 速查
│   │   ├── 03-config-plugins-prebuild.md       # Config Plugins 与 prebuild
│   │   └── 04-dev-client-and-updates.md        # dev client 与 expo-updates
│   ├── library-guides/
│   │   ├── 01-state-and-data.md                # 状态与数据请求库
│   │   ├── 02-native-and-device-libs.md        # 原生与设备能力库
│   │   ├── 03-storage-options.md               # 存储方案选型
│   │   └── 04-animation-gesture-libs.md        # 动画与手势库
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

**模块状态**: ✅ 双轨结构完整（basics 8 篇 + reference 23 篇）
**最后更新**: 2026年9月11日
**维护团队**: Dev Quest Team

> 💡 **学习提示**：跨平台的价值在于一套代码服务多端用户。按入门 → 进阶 → 精通三条路径推进，字典随查随用；鸿蒙（RNOH）作为第三端贯穿各专题文档，版本对齐永远先查 [RNOH 字典](reference/language-concepts/05-harmonyos-rnoh-api.md)。
