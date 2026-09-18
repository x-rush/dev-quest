# Hooks 速查 — 官方与 RN 常用

> **难度**: ⭐ | **前置**: 理解 Hook 基本用法（[04-state-hooks](../../basics/04-state-hooks.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#Hooks` `#useEffect` `#useMemo` `#useNavigation` |
| **更新日期** | `2026年9月` |

</details>

## React 官方 Hooks（RN 全部可用）

### useState

### 描述
组件局部可变状态，变更触发重渲染。

### 语法和示例
```tsx
const [visible, setVisible] = useState(false);
const [list, setList] = useState<Item[]>(() => loadInitial()); // 惰性初始化
```

### 陷阱
- 初始值是昂贵计算时用函数式惰性初始化
- 连续 setState 依赖旧值时必须用 `setX((prev) => ...)` 函数式更新

### useEffect

### 描述
处理渲染后的副作用（订阅/请求/定时器），返回清理函数。

### 语法和示例
```tsx
useEffect(() => {
  const sub = AppState.addEventListener('change', handler);
  return () => sub.remove();
}, [deps]);
```

### 陷阱
- 依赖数组如实填写，用 `eslint-plugin-react-hooks` 强制检查
- 与外部系统同步才用它；纯派生数据用 useMemo 或直接计算

### useLayoutEffect

### 描述
原生视图挂载后同步执行，先于绘制。用于测量布局后立即调整。

### 陷阱
- 会阻塞绘制，勿滥用；常规副作用仍用 useEffect

### useMemo / useCallback

### 描述
缓存计算结果 / 函数引用，避免子组件因引用变化重渲染。

### 语法和示例
```tsx
const total = useMemo(() => items.reduce((s, i) => s + i.amount, 0), [items]);
const onSubmit = useCallback((v: string) => add(v), [add]);
```

### 陷阱
- 只对"昂贵计算"或"作为 props 传给 memo 组件"的值使用；到处包裹反而增加开销
- Context 的对象 value 身份变化会通知消费者；有性能证据时稳定其引用，常量对象或基础值不一定需要 useMemo

### useRef

### 描述
持有跨渲染的可变引用，或引用原生视图实例。

### 语法和示例
```tsx
const listRef = useRef<FlatList<Item>>(null);
listRef.current?.scrollToOffset({ offset: 0, animated: true });
```

### 陷阱
- `.current` 变化不触发渲染；需要"值变即渲染"用 useState

### useTransition / useDeferredValue

### 描述
并发特性：把非紧急更新降级，输入框打字不卡列表。

### 陷阱
- 需 React 18+（现行 RN 均满足）；长列表过滤场景收益明显

## RN 专用 Hooks（react-native 内置）

| Hook | 用途 | 等价的旧写法 |
|------|------|-------------|
| `useWindowDimensions` | 响应式窗口尺寸（旋转/分屏自动更新） | `Dimensions.get` + 事件监听 |
| `useColorScheme` | 系统深浅色模式 `'light' \| 'dark' \| null` | Appearance API |
| `useAnimatedValue` | 创建 `Animated.Value` | `new Animated.Value()` |

```tsx
function ThemedHeader() {
  const scheme = useColorScheme();
  const { width } = useWindowDimensions();
  return <Text style={{ color: scheme === 'dark' ? '#fff' : '#000' }}>
    {width > 600 ? '宽屏' : '窄屏'}
  </Text>;
}
```

### useColorScheme 详解

### 描述
订阅系统深浅色模式，返回 `'light' | 'dark' | null`。系统在设置里切换外观时自动触发组件重渲染，是主题适配的第一入口（对应的命令式 `Appearance` API 见 [核心 API 字典](./01-rn-core-api.md)，留给非组件环境使用）。

### 语法和示例
```tsx
import { useMemo } from 'react';
import { useColorScheme } from 'react-native';

const scheme = useColorScheme();          // 'light' | 'dark' | null
const dark = scheme === 'dark';
const theme = useMemo(() => (dark ? darkColors : lightColors), [dark]); // 主题对象缓存
```

### 陷阱
- 启动早期/部分 Android 设备首帧返回 `null`，按 `'light'` 兜底，勿对返回值直接做字符串操作
- 新建对象作为 Context value 可能触发消费者更新；直接选择已有的 darkColors/lightColors 常量时，不必为了此目的再缓存
- "深色模式部分页面不生效"先查硬编码色值，再查该页是否真的消费了 Hook

### useWindowDimensions 详解

### 描述
响应式窗口尺寸，返回 `{ width, height, scale, fontScale }`。旋转/分屏/窗口变化时自动触发重渲染，是 `Dimensions.get('window')` 一次性快照的 Hook 替代品。

### 语法和示例
```tsx
import { useWindowDimensions } from 'react-native';

const { width, fontScale } = useWindowDimensions();
const cols = width > 600 ? 3 : 1;        // 断点随旋转/分屏自动重算
const fontSize = 16; // Text 默认允许系统字号缩放，不要再乘 fontScale 导致重复缩放
```

### 陷阱
- 每次窗口变化都重渲染：别把它塞进与尺寸无关的高频计算路径
- 模块顶层调用 `Dimensions.get` 拿到的是加载时快照（见 [核心 API 字典](./01-rn-core-api.md) Dimensions 词条）；组件内一律用本 Hook
- 大字号适配依赖 `fontScale`，与布局断点分开处理

## React Navigation Hooks

| Hook | 用途 |
|------|------|
| `useNavigation()` | 拿 navigation 对象（深组件免层层传递） |
| `useRoute()` | 拿当前路由（含 params） |
| `useFocusEffect(cb)` | 页面聚焦时执行 cb，返回清理函数（Tab 切换场景核心） |
| `useIsFocused()` | 布尔值：页面是否聚焦 |
| `usePreventRemove(condition, callback)` | 拦截返回（未保存提示） |

```tsx
import { useFocusEffect } from '@react-navigation/native';
import { useCallback } from 'react';

useFocusEffect(
  useCallback(() => {
    refetch(); // 每次回到该页刷新数据
    return () => pausePolling();
  }, [refetch]),
);
```

完整导航 API 见 [navigation-essentials](../framework-essentials/02-navigation-essentials.md)。

## 通用校验清单

- ✅ Hook 只在组件/自定义 Hook 顶层调用（不在循环/条件/嵌套函数内）
- ✅ 每个 useEffect 都审视过清理函数
- ✅ 先测量列表更新成本，再决定是否稳定回调与缓存行组件
- ✅ 深层组件用 `useNavigation` 替代 props 透传

<!-- full-library-explanation -->
## 从订阅到清理：一个完整 Hook

前面的短片段都放在组件或自定义 Hook 内。下面的 Hook 可放在 `useAppStatus.ts`，由页面调用；需要已安装 React Native 的工程。

```tsx
import { useEffect, useState } from 'react';
import { AppState } from 'react-native';

export function useAppStatus() {
  const [status, setStatus] = useState(AppState.currentState);
  useEffect(() => {
    const subscription = AppState.addEventListener('change', setStatus);
    setStatus(AppState.currentState);
    return () => subscription.remove();
  }, []);
  return status;
}
```

状态让页面响应更新；Effect 建立订阅；清理函数负责移除该次订阅。依赖数组为空表示这次订阅不依赖组件内变化的值，不是“所有外部值永远不会变”。开发模式可能重复执行设置/清理，用来暴露副作用不对称的问题。

练习：显示该 Hook 的值，前后台切换后检查变化，再反复进入、离开页面。验收：监听器不随进入次数累积；不用 ref 保存本应显示的状态。若列表计算昂贵，再用分析工具决定是否 memo，不能把“全部加缓存”当作 Hook 使用规则。

## 🔗 相关文档

- 📄 **[RN 核心 API 字典](./01-rn-core-api.md)**: 与 Hook 对应的命令式 API
- 📄 **[TS 类型模式](./04-typescript-patterns.md)**: 自定义 Hook 的类型写法
- 📄 **[状态与数据请求库指南](../library-guides/01-state-and-data.md)**: 复杂状态交给 Zustand/Query
- 📄 **[状态与 Hooks 教程](../../basics/04-state-hooks.md)**: 系统学习路径

*相关教程: [导航中的 Hook 实战](../../basics/05-navigation.md)*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
