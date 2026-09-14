# React Native 核心 API 字典

> **难度**: ⭐ | **前置**: React Native 基础（[02-first-app](../../basics/02-first-app.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#核心API` `#AppRegistry` `#Platform` `#Dimensions` `#BackHandler` `#NetInfo` `#Appearance` |
| **更新日期** | `2026年9月` |

## AppRegistry — 应用注册

### 描述
注册应用根组件，是整个 bundle 的启动入口。Expo/新模板已封装，bare 工程的 `index.js` 中可见。

### 语法和示例
```tsx
import { AppRegistry } from 'react-native';
import App from './App';

AppRegistry.registerComponent('MyFirstApp', () => App);

// 仅有多个根组件（如 Widget/扩展场景）时才需要 registerConfig
```

### 陷阱
- 组件名必须与原生侧（Android `getMainComponentName()`、iOS 对应注册名）一致，否则白屏
- 只应调用一次；多次调用后者覆盖前者

## Platform — 平台识别

### 描述
识别当前运行平台，是三端差异适配的第一工具。

### 语法和示例
```tsx
import { Platform } from 'react-native';

Platform.OS                    // 'ios' | 'android'（RNOH 环境下仍返回 'android'，鸿蒙判断见 RNOH 词条）
Platform.Version               // Android: API level（数字）；iOS: 系统版本字符串
Platform.select({ ios: x, android: y, default: z })  // 平台分支取值
Platform.isPad                 // iPad 检测
```

```tsx
// 典型用法：平台分支样式
const titleStyle = Platform.select({
  ios: { fontFamily: 'PingFang SC' },
  android: { fontFamily: 'Roboto' },
  default: {},
});
```

### 陷阱
- 平台分支文件用命名约定替代运行时判断更干净：`Button.ios.tsx` / `Button.android.tsx`（Metro 自动选择）
- `Platform.OS` 不覆盖鸿蒙，RNOH 项目中鸿蒙特征用其注入的标记判断

## Dimensions / useWindowDimensions — 屏幕尺寸

### 描述
获取窗口/屏幕尺寸。`Dimensions.get` 是一次性快照，**推荐用 Hook 版本**以响应旋转、分屏变化。

### 语法和示例
```tsx
import { Dimensions, useWindowDimensions } from 'react-native';

// 一次性快照（不随旋转更新）
const { width, height } = Dimensions.get('window');

// 推荐：响应式
function ResponsiveGrid() {
  const { width, fontScale } = useWindowDimensions();
  const cols = width > 600 ? 3 : 1;
  return null; // 依据 width/fontScale 计算布局
}
```

### 陷阱
- `window` 与 `screen` 不同：Android 上 `screen` 含状态栏，iOS 横屏语义有差异
- 在模块顶层调用 `Dimensions.get` 会拿到模块加载时的旧值

## AppState — 前后台状态

### 描述
监听应用在前台/后台切换，用于暂停轮询、上报埋点、刷新数据。

### 语法和示例
```tsx
import { useEffect, useState } from 'react';
import { AppState } from 'react-native';

const [appState, setAppState] = useState(AppState.currentState);

useEffect(() => {
  const sub = AppState.addEventListener('change', setAppState);
  return () => sub.remove(); // 订阅必须清理
}, []);
```

### 陷阱
- iOS 首次启动值可能为 `null`，需判空
- `inactive`（iOS 来电/下拉通知）介于 active 与 background 之间，处理状态机时别遗漏

## Keyboard — 键盘控制

### 描述
编程式收起键盘与监听键盘事件，表单页必备。

### 语法和示例
```tsx
import { Keyboard, KeyboardAvoidingView, TextInput, Platform } from 'react-native';

Keyboard.dismiss(); // 收起键盘，常用于点空白处

<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
  style={{ flex: 1 }}
>
  <TextInput placeholder="输入内容" />
</KeyboardAvoidingView>
```

### 陷阱
- Android `adjustResize`（manifest）与 `KeyboardAvoidingView` 叠加会双重避让
- 复杂表单考虑 Reanimated 键盘 API 或成熟三方组件

## Linking — 深链与外部跳转

### 描述
打开系统页面（设置/拨号/浏览器）与处理 App 内深链。

### 语法和示例
```tsx
import { Linking } from 'react-native';

await Linking.openURL('https://reactnative.dev');          // 浏览器
await Linking.openSettings();                               // 本 App 设置页
await Linking.openURL('tel:10086');                         // 拨号

// 深链监听（路由方案见 navigation-essentials 的 linking 配置）
const sub = Linking.addEventListener('url', ({ url }) => console.log(url));
sub.remove();
```

### 陷阱
- `openURL` 前用 `canOpenURL` 检查时，iOS 需在 Info.plist 声明 `LSApplicationQueriesSchemes`
- 深链路由解析交给 React Navigation `linking` 配置，避免手写解析

## NetInfo — 网络状态（@react-native-community/netinfo）

### 描述
监听网络连通性与类型变化、主动探测当前状态。RN 内置无此 API，来自社区包：Expo 工程用 `npx expo install @react-native-community/netinfo` 对齐版本。与 `expo-network` 职责重叠，同一工程二选一（选型见 [原生与设备能力库指南](../library-guides/02-native-and-device-libs.md)）。

### 语法和示例
```tsx
import NetInfo from '@react-native-community/netinfo';

// 事件监听：状态变化时触发
const unsub = NetInfo.addEventListener((state) => {
  console.log(state.isConnected, state.type); // true 'wifi' | 'cellular' | 'none' ...
});
unsub(); // 清理订阅

// 一次性探测
const state = await NetInfo.fetch();
```

### 陷阱
- `isConnected=true` 只代表链路层连通，**不代表能上网**（ captive portal/弱网）；关键请求用真实 fetch 探测兜底
- `addEventListener` 返回取消函数而非订阅对象（与 AppState 风格不同），别调 `.remove()`
- 断网恢复瞬间可能连发多次回调，重连逻辑做幂等

## BackHandler — 返回键拦截

### 描述
监听 Android 物理返回键/手势返回（iOS 无系统返回键，仅 Android/鸿蒙侧生效），用于双击退出、返回前确认。

### 语法和示例
```tsx
import { useEffect } from 'react';
import { BackHandler } from 'react-native';

useEffect(() => {
  const sub = BackHandler.addEventListener('hardwareBackPress', () => {
    saveDraft();          // 返回 true = 已消费，阻止默认行为（退出/导航返回）
    return true;
  });
  return () => sub.remove();
}, []);
```

### 陷阱
- 返回 `true` 拦截后必须自行完成导航/退出，否则"返回键失灵"
- 栈导航内的返回拦截优先用 React Navigation 的 `usePreventRemove`（导航层 API，见 [导航模型](./09-navigation-model.md)），只在导航管不到的场景用 BackHandler
- RNOH/鸿蒙侧返回手势与系统手势同源，业务层自定义拦截与 ArkUI 手势可能冲突，优先交给栈导航默认行为

## PixelRatio — 像素密度

### 描述
逻辑像素（dp/pt）与物理像素转换，处理 1px 细线等场景。

### 语法和示例
```tsx
import { PixelRatio, StyleSheet } from 'react-native';

PixelRatio.get();                          // 密度倍数
StyleSheet.hairlineWidth;                  // 推荐的"1px 细线"写法
```

### 陷阱
- 细线请用 `StyleSheet.hairlineWidth`，手写 `borderWidth: 1` 在高分屏过粗

## AccessibilityInfo — 无障碍状态

### 描述
查询与监听无障碍服务状态：屏幕阅读器是否开启、系统"减弱动态效果"等，用于切换动效策略与增强读屏体验。

### 语法和示例
```tsx
import { useEffect, useState } from 'react';
import { AccessibilityInfo } from 'react-native';

const [screenReader, setScreenReader] = useState(false);

useEffect(() => {
  AccessibilityInfo.isScreenReaderEnabled().then(setScreenReader); // 异步查询
  const sub = AccessibilityInfo.addEventListener(
    'screenReaderChanged', // 另有 'reduceMotionChanged'、'boldTextChanged' 等事件
    setScreenReader,
  );
  return () => sub.remove();
}, []);

// 用法：屏幕阅读器开启或用户要求减弱动效时，跳过装饰性动画
```

### 陷阱
- 查询方法返回 Promise，**不要在渲染期同步读**，放进 Effect 或按需触发
- 与组件侧 `accessible` / `accessibilityLabel` / `accessibilityRole` 配合使用（Props 见 [组件 Props 全表](./02-components-props.md)），单靠状态查询不能让界面可读
- 事件名与平台支持度有差异，逐端验证（鸿蒙走 RNOH 适配层）

## Appearance / useColorScheme — 系统深浅色

### 描述
获取系统深浅色模式。`Appearance` 是命令式 API + 事件；`useColorScheme` 是对应的响应式 Hook，**组件内一律用 Hook**。

### 语法和示例
```tsx
import { Appearance, useColorScheme } from 'react-native';

// Hook 版（推荐）：主题切换自动重渲染
const scheme = useColorScheme(); // 'light' | 'dark' | null
const dark = scheme === 'dark';

// 命令式版：留给非组件环境（工具函数/模块顶层）
const current = Appearance.getColorScheme();
const sub = Appearance.addChangeListener(({ colorScheme }) => { /* ... */ });
sub.remove();
```

### 陷阱
- `useColorScheme` 首帧可能返回 `null`（启动早期/部分 Android 设备），按 `'light'` 兜底，勿对返回值直接做字符串操作
- "深色模式部分页面不生效"多半是颜色写死：先查硬编码色值，再查 Hook 是否覆盖该页
- 主题对象用 `useMemo` 缓存，避免每次渲染重建导致子组件级联重渲染；主题切换事件本身不触发未使用 Hook 的组件更新

## InteractionManager — 已从核心移除（迁移指引）

### 描述
`InteractionManager.runAfterInteractions` 曾用于把耗时任务推迟到当前动画/交互完成之后执行。**RN 0.87 已从核心移除该 API**：`index.js` 在 `__DEV__` 下对它的任何访问都会 invariant 报错（"InteractionManager has been removed from react-native core. Please refactor long tasks into smaller ones, and use 'requestIdleCallback' instead."），TypeScript 类型层也无此导出。旧代码按下述替代方案迁移。

### 语法和示例
```tsx
import { useEffect, startTransition } from 'react';

// 替代 1：requestIdleCallback（运行时全局函数，无需 import）——低优先级任务放到空闲期
useEffect(() => {
  const id = requestIdleCallback(() => {
    warmUpCache(); // 首屏空闲时再执行的重活
  });
  return () => cancelIdleCallback(id); // 组件卸载时取消未执行的任务
}, []);

// 替代 2：startTransition——把非紧急的状态更新降级，不阻塞交互响应
startTransition(() => {
  setQuery(nextQuery);
});
```

### 陷阱
- `requestIdleCallback` 的任务仍占用 JS 线程，只是错峰——不能把死循环重活变轻；真正的长任务移 UI 线程（Reanimated worklet）或原生侧
- 非紧急**更新**优先 `startTransition` / `useDeferredValue`（见 [Hooks 速查](./03-hooks-reference.md) 与 [渲染性能](../../advanced-topics/performance/01-rendering-performance.md)）
- 官方建议的第一步是把长任务拆小，这两个 API 只是排队机制，不是提速手段

## 其他常用速览

| API | 用途 | 备注 |
|-----|------|------|
| `StatusBar` | 状态栏样式 | 三端表现不同，逐端验证 |
| `ToastAndroid` | Android 吐司 | iOS/鸿蒙需用三方提示组件 |
| `Alert` | 系统弹窗 | 三端可用，样式原生 |
| `Vibration` | 震动 | iOS 时长模式有限制 |
| `Share` | 系统分享 | 鸿蒙走 RNOH 适配 |
| `PermissionsAndroid` | Android 运行时权限 | iOS 权限在 Info.plist + 三方库 |

## 🔗 相关文档

- 📄 **[组件 Props 全表](./02-components-props.md)**: 核心组件属性字典
- 📄 **[Hooks 速查](./03-hooks-reference.md)**: `useColorScheme`/`useWindowDimensions` 等对应 Hook
- 📄 **[新架构术语字典](./11-new-architecture-terms.md)**: 本篇 API 背后的架构术语
- 📄 **[列表性能模型](./12-list-performance-model.md)**: 列表掉帧归因、调参与 FlashList 选型
- 📄 **[平台 API 地图](./13-platform-api-map.md)**: 按用途找 API 的总入口
- 📄 **[RNOH 架构](./05-harmonyos-rnoh-api.md)**: 鸿蒙平台判断与差异化 API
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)**: 深链/权限相关报错

*相关教程: [环境搭建](../../basics/01-environment-setup.md) · [第一个 App](../../basics/02-first-app.md)*
