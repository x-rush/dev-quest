# React Native 核心 API 字典

> **难度**: ⭐ | **前置**: React Native 基础（[02-first-app](../../basics/02-first-app.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#核心API` `#AppRegistry` `#Platform` `#Dimensions` |
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
- 📄 **[Hooks 速查](./03-hooks-reference.md)**: `useWindowDimensions` 等对应 Hook
- 📄 **[RNOH 架构](./05-harmonyos-rnoh-api.md)**: 鸿蒙平台判断与差异化 API
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)**: 深链/权限相关报错

*相关教程: [环境搭建](../../basics/01-environment-setup.md) · [第一个 App](../../basics/02-first-app.md)*
