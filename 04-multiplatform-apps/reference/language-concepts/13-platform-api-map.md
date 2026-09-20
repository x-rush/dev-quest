# 平台 API 地图 — RN 核心 API 与 Expo SDK 模块速查

## 能力存在、权限允许和设备可用是三道检查

前置：Promise 和平台条件。相机 API 存在只证明代码入口可用；用户可能拒绝权限，模拟器可能没有硬件，插件可能只支持部分目标平台。兼容表应记录这些不同条件，而不是只写“支持三端”。

以定位为例：先判断平台与模块，再申请或读取授权，随后发起定位并处理取消、超时和不可用。页面离开以后结果是否还需要，也要有明确决定。

自测：首次拒绝、允许后再次访问、永久拒绝、设备服务关闭四种场景分别出现什么？验收是用户知道下一步该做什么，且错误不会被当成默认经纬度。官方平台能力与插件支持范围要按项目锁定版本核对。

> **难度**: ⭐ | **前置**: 无（任意跳入查阅；新手建议先读 [02-first-app](../../basics/02-first-app.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#平台API` `#Expo SDK` `#选型地图` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

## 先分清语言内置能力、宿主 API 与原生模块

React Native 使用 JavaScript/TypeScript 写界面，但运行环境不是浏览器，也不是 Node.js。语言的 `Array`、`Map`、`Set`、`JSON`、`Promise` 是基础层；React 的 Hook、React Native 的组件以及相机模块分别在不同层提供能力。TypeScript 类型声明能帮助检查调用，却不能让设备凭空拥有对应功能。

| 任务 | 优先查什么 | 输入输出与失败边界 |
|---|---|---|
| 清理标题 | `String.trim()`，然后判断长度 | 返回新字符串；空白输入清理后可能为空，不修改原值 |
| 金额输入 | 完整格式校验，再转换整数分 | `parseFloat('12abc')` 会得到 12，因此不能用它代替整段输入校验 |
| 更新列表 | `map` / `filter`，保持稳定业务 ID | 返回新数组；只复制数组不代表深复制元素；下标不是记录身份 |
| 去重和按 ID 查找 | `Set` / `Map` | 对象键按引用身份比较；网络或磁盘 JSON 需另行编码结构 |
| 本地持久化 | JSON 编解码 + AsyncStorage 或数据库 | `JSON.parse` 可抛错；解析成功仍需验证字段类型与版本；不要将损坏数据当空列表覆盖 |
| 异步操作 | `Promise`、`async`/`await` 与错误处理 | `await` 暂停当前异步函数，不自动启动线程，也不自动取消请求 |
| 发 HTTP 请求 | RN 提供的 `fetch` 宿主 API | 检查 HTTP 状态、响应结构与取消；能联网不代表服务器健康 |
| 读应用文件 | 选用目标平台支持的文件模块 | 浏览器 DOM 与 Node `fs` 并非 RN 默认能力；先核对原生模块和目录权限 |

先阅读 [TypeScript 模式](./04-typescript-patterns.md)，再做[首项目](../../basics/08-first-project.md)中的输入解析和存储失败练习。语言能力可用纯函数测试；设备存储、权限与 UI 需要目标运行时验证。宿主能力范围以 [React Native JavaScript 环境](https://reactnative.dev/docs/javascript-environment)及项目锁定版本为准。

## 按用途找到平台 API

一张按**用途**分组的 API 地图：左列是"我想做什么"，中列是该模块的一句话职责，右列指向本字典已有条目或官方文档。**选型总原则**（详见 [原生与设备能力库指南](../library-guides/02-native-and-device-libs.md)）：有 Expo SDK 模块先用 Expo 模块，其次确认新架构适配的社区库，最后才自研 TurboModule。

## 📖 RN 侧（react-native 内置）

### 设备能力与系统

| API/组件 | 职责 | 深入 |
|----------|------|------|
| `Platform` | 识别运行平台，三端差异适配第一工具 | [核心 API 字典](./01-rn-core-api.md) |
| `AppState` | 监听前台/后台切换，暂停轮询、上报埋点 | [核心 API 字典](./01-rn-core-api.md) |
| `Dimensions` / `useWindowDimensions` | 窗口尺寸；Hook 版响应式 | [核心 API 字典](./01-rn-core-api.md) · [Hooks 速查](./03-hooks-reference.md) |
| `PixelRatio` | 逻辑像素与物理像素转换；细线用 `StyleSheet.hairlineWidth` | [核心 API 字典](./01-rn-core-api.md) |
| `NetInfo`（社区包） | 网络状态监听与探测，需单独安装；不属于 react-native 内置导出，也不保证目标服务器可达 | [核心 API 字典](./01-rn-core-api.md) · [NetInfo 仓库](https://github.com/react-native-netinfo/react-native-netinfo) |
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
| `InteractionManager` 迁移 | 查目标版本的迁移说明；长任务拆分后考虑空闲调度；`startTransition` 只标记非紧急 React 更新，不会把同步计算移到后台线程 | [核心 API 字典](./01-rn-core-api.md) |
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
| `expo-image` | 图片加载与缓存选项；列表中应比较解码、缓存命中、内存与滚动表现后选择 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/image/) |
| `expo-video` | 视频播放器 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/video/) |

> 注：旧音视频包 `expo-av` 已被官方拆分为 `expo-audio` / `expo-video`，新项目直接用新包，本仓库未收录 expo-av。

### 构建与运维

| 模块/工具 | 职责 | 深入 |
|-----------|------|------|
| `expo-router` | 文件系统路由（SDK 56 起内置 fork 版 React Navigation，不再直接 import 其包） | [docs.expo.dev](https://docs.expo.dev/router/introduction/) · [Expo 要点](../framework-essentials/01-expo-essentials.md) |
| `expo-updates` | 向兼容原生运行时分发 JS/资源更新；改变原生代码需新构建，发布仍需符合平台政策 | [docs.expo.dev](https://docs.expo.dev/versions/latest/sdk/updates/) · [dev client 与 updates](../framework-essentials/04-dev-client-and-updates.md) |
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


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
