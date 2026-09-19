# React Native：理解地图与学习规划

> 前置：React、TypeScript 和异步请求；先选择 Android 或 iOS 作为**计划中的首个本地运行目标**。iOS 原生本地构建需要 macOS/Xcode，鸿蒙适配单独核查。本仓库没有 Android、iOS 或鸿蒙工程运行记录；开始前请在目标工具链完成后文的构建与设备验收。

## 先回答一个问题

**熟悉的 React 状态怎样驱动原生控件，哪里仍然需要平台代码？**

React Native 用 React 思维描述原生界面，不是把 HTML 放进手机。JavaScript 打包、原生编译、设备权限是不同层；Expo 简化常用工程流程，但三端可用性仍取决于具体模块和平台适配。

## 概念怎样连接

单平台启动 → View/Text 与布局 → 状态 → 导航 → 网络与持久化 → 原生能力 → 平台适配

| 概念 | 必要解释 |
|---|---|
| Metro 与原生构建 | Metro 提供 JavaScript bundle；新增原生依赖往往还需重新构建应用，刷新 JS 不能替代。 |
| 组件 | View/Text 不是 div/span，布局和事件的细节要按原生组件规则理解。 |
| 平台能力 | 相机、定位、文件和通知都要处理授权与拒绝；安装包支持某平台不代表每个插件都支持。 |

## 从 0 到 1 的阅读顺序

先选一个设备目标和一种工程方式，在这个环境走完整条入门路径。学习到导航后就可以做本地待办；原生桥接、新架构和多端适配在有相应需求时再学，不作为第一个项目的前置。

版本和平台组合见[模块 README](README.md)，以所选工程的依赖及原生配置为准。官方起点：[React Native Get Started](https://reactnative.dev/docs/environment-setup)。Expo 工程与自行管理原生工程的配置不要拼接使用。

1. [环境搭建 — Node/RN CLI/Expo 与三端工具链](basics/01-environment-setup.md)
2. [第一个 App — 创建、Metro 与三端运行](basics/02-first-app.md)
3. [核心组件、JSX 与 Flexbox 布局](basics/03-components-jsx.md)
4. [状态管理 — useState/useEffect 与自定义 Hook](basics/04-state-hooks.md)
5. [导航基础 — React Navigation 栈/标签/抽屉](basics/05-navigation.md)
6. [综合练习 — 待办记账 App](basics/08-first-project.md)：先完成单平台输入、列表和存储，再扩展第二平台。
7. 选学：[原生模块桥接](basics/06-native-modules.md)，用于现有组件无法满足的平台能力。
8. 选学：[新架构、Hermes 与动画](basics/07-advanced-features.md)，带着实际渲染或性能问题学习。

## 三个阶段如何验收

| 阶段与入口 | 练习输入与动作 | 通过条件 |
| --- | --- | --- |
| 一台设备：[首个 App](basics/02-first-app.md)、[状态](basics/04-state-hooks.md) | 修改文本并添加点击计数 | 真机或模拟器能看到变化；记录设备、系统和构建方式，知道刷新 JS 与重建原生应用的区别 |
| 本地应用：[Todo 项目](projects/01-todo-app.md) | 添加普通标题，拒绝空白标题，删除所有项，再重启 | 操作有反馈，空列表可继续添加；接入持久化后重启仍能读回数据 |
| 网络与平台：[天气项目](projects/02-weather-app.md) | 请求成功、断网、拒绝定位授权、手动选城市 | 失败与拒绝均可恢复；第二平台重新构建并重复检查，多端成功分别记录 |

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

## 框架与高级主题怎么选

先明确采用 Expo 还是独立原生工程，再选择匹配的导航和插件。Fabric、TurboModules、Hermes 属于进阶理解，不是显示第一个按钮的前置。

## 共用的 JavaScript 基础参考

[关键词与完整语法实验](../shared-resources/javascript-keywords.md)解释语言语法；[内置对象、方法与边界](../shared-resources/javascript-builtins.md)解释数组、字符串、对象、集合和 Promise。先区分语言、宿主 API 与框架函数，再查本模块特有内容。

## 全量参考怎么查

关键词解决“语法是什么意思”，内置函数解决“直接能调用什么”，标准库解决“导入以后能做什么”。框架 API 另列，避免把库函数误当成语言本身。以下是现有文章的完整导航，不代表每个 API 都已充分讲解；具体覆盖缺口进入审查台账。

### framework-essentials

- [Expo 要点 — Router、EAS 与 expo-modules](reference/framework-essentials/01-expo-essentials.md)
- [React Navigation API 速查 — 导航器、linking 与深链](reference/framework-essentials/02-navigation-essentials.md)
- [Config Plugins 与 prebuild — 原生工程的生成模型](reference/framework-essentials/03-config-plugins-prebuild.md)
- [dev client 与 expo-updates — 运行模型与更新通道](reference/framework-essentials/04-dev-client-and-updates.md)

### language-concepts

- [React Native 核心 API 字典](reference/language-concepts/01-rn-core-api.md)
- [核心组件 Props 全表](reference/language-concepts/02-components-props.md)
- [Hooks 速查 — 官方与 RN 常用](reference/language-concepts/03-hooks-reference.md)
- [TypeScript 类型模式 — RN 工程实践](reference/language-concepts/04-typescript-patterns.md)
- [RNOH 字典 — React Native for OpenHarmony 架构与适配](reference/language-concepts/05-harmonyos-rnoh-api.md)
- [组件生命周期 — 挂载、更新与卸载](reference/language-concepts/06-component-lifecycle.md)
- [状态管理模型 — 分层与放置](reference/language-concepts/07-state-management.md)
- [桥接与原生通信原理 — Bridge、JSI 与 TurboModules](reference/language-concepts/08-bridge-principles.md)
- [导航模型 — 路由、栈与页面状态机](reference/language-concepts/09-navigation-model.md)
- [样式与布局模型 — Yoga、Flexbox 子集与平台差异](reference/language-concepts/10-styling-model.md)
- [新架构术语字典 — Fabric、TurboModules、JSI、Codegen 与 Hermes](reference/language-concepts/11-new-architecture-terms.md)
- [列表性能模型 — FlatList 虚拟化与调参](reference/language-concepts/12-list-performance-model.md)
- [平台 API 地图 — RN 核心 API 与 Expo SDK 模块速查](reference/language-concepts/13-platform-api-map.md)

### library-guides

- [状态与数据请求库指南 — Zustand / Redux / TanStack Query](reference/library-guides/01-state-and-data.md)
- [原生与设备能力库指南 — 相机/推送/存储/传感器](reference/library-guides/02-native-and-device-libs.md)
- [存储方案选型 — 键值、加密、SQLite 与文件](reference/library-guides/03-storage-options.md)
- [动画与手势库 — 共享值、worklet 与手势系统](reference/library-guides/04-animation-gesture-libs.md)

### quick-references

- [CLI 命令与调试速查表](reference/quick-references/01-cli-and-debug-cheatsheet.md)
- [故障排除 — 常见错误与解法](reference/quick-references/02-troubleshooting.md)

## 卡住时

先判断是术语不懂、输入输出不清、代码上下文缺失，还是运行环境不同。返回[学习方法](../shared-resources/learning-guide.md)按证据排查；通用术语见[术语解释](../shared-resources/glossary.md)。
