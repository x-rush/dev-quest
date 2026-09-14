# 平台 API 地图 — RN 核心 API 与 Expo SDK 模块速查

> **难度**: ⭐ | **前置**: 无（任意跳入查阅；新手建议先读 [02-first-app](../../basics/02-first-app.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#平台API` `#Expo SDK` `#选型地图` |
| **更新日期** | `2026年9月` |

## 📌 定义

一张按**用途**分组的 API 地图：左列是"我想做什么"，中列是该模块的一句话职责，右列指向本字典已有条目或官方文档。**选型总原则**（详见 [原生与设备能力库指南](../library-guides/02-native-and-device-libs.md)）：有 Expo SDK 模块先用 Expo 模块，其次确认新架构适配的社区库，最后才自研 TurboModule。

## 📖 RN 侧（react-native 内置）

### 设备能力与系统

| API/组件 | 职责 | 深入 |
|----------|------|------|
| `Platform` | 识别运行平台，三端差异适配第一工具 | [核心 API 字典](./01-rn-core-api.md) |
| `AppState` | 监听前台/后台切换，暂停轮询、上报埋点 | [核心 API 字典](./01-rn-core-api.md) |
| `Dimensions` / `useWindowDimensions` | 窗口尺寸；Hook 版响应式 | [核心 API 字典](./01-rn-core-api.md) · [Hooks 速查](./03-hooks-reference.md) |
| `PixelRatio` | 逻辑像素与物理像素转换；细线用 `StyleSheet.hairlineWidth` | [核心 API 字典](./01-rn-core-api.md) |
| `NetInfo` | 网络状态监听与探测（社区包，需安装） | [核心 API 字典](./01-rn-core-api.md) · [NetInfo 仓库](https://github.com/react-native-netinfo/react-native-netinfo) |
| `Vibration` | 震动反馈 | [Vibration 文档](https://reactnative.dev/docs/vibration) |
| `PermissionsAndroid` | Android 运行时权限申请 | [PermissionsAndroid 文档](https://reactnative.dev/docs/permissionsandroid) |
| `Appearance` / `useColorScheme` | 系统深浅色；Hook 版响应式 | [核心 API 字典](./01-rn-core-api.md) · [Hooks 速查](./03-hooks-reference.md) |
| `AccessibilityInfo` | 查询/监听屏幕阅读器、减弱动效等无障碍状态 | [核心 API 字典](./01-rn-core-api.md) |
| `StatusBar` | 状态栏样式（组件形态 Props 见 Props 全表） | [Props 全表](./02-components-props.md) |

### 导航与返回

| API/组件 | 职责 | 深入 |
|----------|------|------|
| `Linking` | 打开系统页面/外部浏览器、处理深链 | [核心 API 字典](./01-rn-core-api.md) |
| `BackHandler` | Android 物理返回键/手势监听 | [核心 API 字典](./01-rn-core-api.md) |
| 导航器（Stack/Tabs） | 路由与页面状态机 | [导航模型](./09-navigation-model.md) |

### 交互与反馈

| API/组件 | 职责 | 深入 |
|----------|------|------|
| `Keyboard` | 编程式收起键盘、监听键盘事件 | [核心 API 字典](./01-rn-core-api.md) |
| `Alert` / `ToastAndroid` | 系统弹窗 / Android 吐司 | [核心 API 字典](./01-rn-core-api.md) |
| `Share` | 调起系统分享面板 | [Share 文档](https://reactnative.dev/docs/share) |
| ~~`InteractionManager`~~（已移除） | 把耗时任务推迟到交互完成后执行——**RN 0.87 起从核心移除**，替代：`requestIdleCallback` / `startTransition` | [核心 API 字典](./01-rn-core-api.md) |
| 核心组件（View/Text/Image/ScrollView/FlatList/Pressable/Modal…） | UI 骨架与列表 | [Props 全表](./02-components-props.md) |

## 📖 Expo SDK 模块（本仓库实际使用范围，SDK 57）

### 设备能力

| 模块 | 职责 | 文档 |
|------|------|------|
| `expo-location` | 定位与地理编码 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/location/) |
| `expo-sensors` | 加速度计/陀螺仪等传感器统一接口 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/sensors/) |
| `expo-battery` | 电量与充电状态 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/battery/) |
| `expo-network` | 网络状态查询（与 NetInfo 职责重叠，Expo 工程二选一） | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/network/) |
| `expo-local-authentication` | 指纹/面容生物识别认证 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/localauthentication/) |
| `expo-haptics` | 触觉反馈（比 Vibration 跨端语义更统一） | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/haptics/) |
| `expo-camera` | 相机取景与扫码 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/camera/) |
| `expo-image-picker` | 相册选图/拍照 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/imagepicker/) |

### 存储

| 模块 | 职责 | 深入 |
|------|------|------|
| `expo-secure-store` | 加密键值存储（Keychain/Keystore） | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/securestore/) · [存储方案选型](../library-guides/03-storage-options.md) |
| `expo-sqlite` | 结构化 SQL 存储 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/sqlite/) |
| `expo-file-system` | 文件与目录读写 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/filesystem/) |

### 通知

| 模块 | 职责 | 深入 |
|------|------|------|
| `expo-notifications` | 本地通知与推送（推送需配套服务端凭证） | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/notifications/) |

### 媒体

| 模块 | 职责 | 深入 |
|------|------|------|
| `expo-image` | 高性能图片加载与缓存（列表图片首选） | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/image/) |
| `expo-video` | 视频播放器 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/video/) |

> 注：旧音视频包 `expo-av` 已被官方拆分为 `expo-audio` / `expo-video`，新项目直接用新包，本仓库未收录 expo-av。

### 构建与运维

| 模块/工具 | 职责 | 深入 |
|-----------|------|------|
| `expo-router` | 文件系统路由（SDK 56 起内置 fork 版 React Navigation，不再直接 import 其包） | [docs.expo.dev](https://docs.expo.dev/router/introduction/) · [Expo 要点](../framework-essentials/01-expo-essentials.md) |
| `expo-updates` | OTA 更新（绕过商店的 JS/资源热更） | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/updates/) · [dev client 与 updates](../framework-essentials/04-dev-client-and-updates.md) |
| `expo-dev-client` | 开发构建（dev client，替代 Expo Go 装原生依赖） | [docs.expo.dev](https://docs.expo.dev/develop/development-builds/introduction/) |
| EAS Build / Submit | 云构建与商店提交 | [docs.expo.dev](https://docs.expo.dev/build/introduction/) · [EAS Build 指南](../../deployment/01-eas-build.md) |
| `expo-doctor` | 检查工程依赖与配置健康度 | [docs.expo.dev](https://docs.expo.dev/develop/tools/#expo-doctor) |
| Config Plugins | prebuild 阶段注入原生配置 | [Config Plugins 与 prebuild](../framework-essentials/03-config-plugins-prebuild.md) |
| `AppRegistry` | bare 工程 bundle 启动注册（Expo 已封装） | [核心 API 字典](./01-rn-core-api.md) |

## 💡 示例

以 [实战：天气应用](../../projects/02-weather-app.md) 串一遍地图：定位（`expo-location`）→ 网络判断（`NetInfo`）→ 请求与状态（[状态与数据请求库](../library-guides/01-state-and-data.md)）→ 渲染（FlatList，性能见 [列表性能模型](./12-list-performance-model.md)）→ 缓存（`expo-sqlite`）→ 深色模式（`useColorScheme`）→ OTA（`expo-updates`）。

## ⚠️ 常见陷阱

- ❌ **假设权限已授予**，直接调能力
  ✅ Android 用 `PermissionsAndroid` 逐次申请，iOS 相机/定位等由 Info.plist 文案 + 系统弹窗控制（Expo 模块经 Config Plugins 声明）
- ❌ **同一职责混装两套库**（如 NetInfo 与 expo-network 同时在依赖里）
  ✅ 按 [选型优先级](../library-guides/02-native-and-device-libs.md) 定一套，减少包体与权限面
- ❌ **Expo 工程用 `npm install` 装带原生代码的模块**
  ✅ 用 `npx expo install` 让版本与 SDK 57 对齐
- ❌ **地图当教程读**
  ✅ 本篇只负责"找到工具"；每个工具的完整解释以其链接指向的字典条目或官方文档为单一事实来源

## 🔗 相关条目

- 📄 **[RN 核心 API 字典](./01-rn-core-api.md)** — RN 侧 API 的完整条目
- 📄 **[核心组件 Props 全表](./02-components-props.md)** — 组件级参数速查
- 📄 **[原生与设备能力库指南](../library-guides/02-native-and-device-libs.md)** — 选型优先级与社区库对比
- 📄 **[存储方案选型](../library-guides/03-storage-options.md)** — 四类存储载体的决策顺序
- 📄 **[生态集成](../../frameworks/03-ecosystem-integration.md)** — Expo Router、EAS 与库选型的任务式指南

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
