# 状态管理 — useState/useEffect 与自定义 Hook

## 先理解，再动手

useState 保存组件状态，useEffect 用于与外部系统同步。派生值可以直接计算，不必用 effect 再写回另一份状态。

**本节自测**：保存待办数组，直接计算未完成数量；再实现一项可清理的订阅。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

列表变化后数量自动一致；卸载时订阅被清理，重新进入不会重复收到事件。

</details>

> **文档简介**: 掌握 React Hooks 在移动端的正确用法：useState/useEffect、自定义 Hook 封装设备能力，以及 Context 处理全局状态
>
> **目标读者**: 会写静态界面的 RN 初学者，希望理解"状态驱动 UI"
>
> **前置知识**: 完成 [03-components-jsx](./03-components-jsx.md)，有 React Hooks 基础概念

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#Hooks` `#useState` `#useEffect` `#Context` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 useState/useEffect 实现计时器、表单等交互界面
- ✅ 正确处理 useEffect 的清理函数，避免卸载后的无效更新和重复订阅
- ✅ 把设备能力（网络状态、屏幕方向）封装成可复用的自定义 Hook
- ✅ 用 Context + useMemo 组织轻量全局状态

## 🔍 核心概念

### useState — 组件的记忆

**定义**: 声明一个随时间变化、变化后触发重新渲染的值。

**移动端注意点**: setState 是异步批处理的，永远通过函数式更新读取"上一次的值"，避免连点导致丢更新。

```tsx
import { useState } from 'react';
import { Text, TouchableOpacity, View } from 'react-native';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <TouchableOpacity onPress={() => setCount((prev) => prev + 1)}>
      {/* 函数式更新保证快速连点计数不丢失 */}
      <Text>点了 {count} 次</Text>
    </TouchableOpacity>
  );
}
```

### useEffect — 与外部系统同步

**定义**: 在渲染后执行副作用（订阅、请求、定时器），并在卸载/依赖变化时执行清理。

```tsx
import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';

function Timer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setSeconds((s) => s + 1), 1000);
    // 清理函数：组件卸载或 effect 重跑前停止仍在运行的 interval
    return () => clearInterval(id);
  }, []); // 空依赖 = 只在挂载后执行一次

  return <Text>计时 {seconds} 秒</Text>;
}
```

开发模式的 Strict Mode 可能额外执行一次“设置 → 清理 → 设置”来暴露不完整的清理逻辑，因此订阅回调与清理函数都应能安全地重复执行。

**RN 场景下 useEffect 最常见的三个用途**：

1. 挂载时请求接口（配合 AbortController 取消）
2. 订阅原生事件（`AppState`、键盘弹出、传感器），在清理函数中取消订阅
3. 根据路由参数变化重新拉数据（依赖里放路由 params）

### 自定义 Hook — 复用状态逻辑

**定义**: 以 `use` 开头、内部调用其他 Hook 的函数，用于抽取"状态 + 副作用"的组合逻辑。

```tsx
// hooks/useNetworkStatus.ts
import { useEffect, useState } from 'react';
import { AppState } from 'react-native';
import NetInfo from '@react-native-community/netinfo';

export function useNetworkStatus() {
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      setIsConnected(Boolean(state.isConnected));
    });
    // 切回前台时主动刷新一次，模拟器/真机切换网络时更可靠
    const appStateSubscription = AppState.addEventListener('change', (s) => {
      if (s === 'active') {
        NetInfo.fetch()
          .then((state) => setIsConnected(Boolean(state.isConnected)))
          .catch(() => setIsConnected(false)); // 按产品策略选择“未知”或“离线”
      }
    });
    return () => {
      unsubscribe();
      appStateSubscription.remove();
    };
  }, []);

  return isConnected;
}
```

```tsx
// 使用处
function OfflineBanner() {
  const isConnected = useNetworkStatus();
  if (isConnected) return null;
  return <Text style={{ color: '#fff', backgroundColor: '#c00', padding: 8 }}>
    网络已断开，展示的是缓存数据
  </Text>;
}
```

### Context — 跨层级传递

**定义**: 提供一棵组件树内共享、免逐层传 props 的机制。适合主题、登录态、语言包等低频变化的全局数据。

```tsx
import { createContext, useContext, useMemo, useState } from 'react';
import type { ReactNode } from 'react';

type Theme = 'light' | 'dark';
interface ThemeCtx { theme: Theme; toggle: () => void }

const ThemeContext = createContext<ThemeCtx | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');
  // useMemo 缓存 value，避免每次渲染导致所有消费者重渲染
  const value = useMemo(
    () => ({ theme, toggle: () => setTheme((t) => (t === 'light' ? 'dark' : 'light')) }),
    [theme],
  );
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme 必须在 ThemeProvider 内使用');
  return ctx;
}
```

**边界**：Context 变化会让所有消费者重渲染。高频数据（输入框、列表滚动位置）不要放 Context；更完整的状态方案对比见 [state-and-data 库指南](../reference/library-guides/01-state-and-data.md)。

## 🎨 最佳实践

useState 可以接收对象或数组，React 不会每次渲染都重新采用初始值；只有创建初始值的计算昂贵时，惰性初始化才有实际收益。更新对象时生成新的值，并明确哪些组件需要共享它。[React 的 useState 说明](https://react.dev/reference/react/useState)区分了初始参数与后续更新。

Effect 用于同步订阅等外部系统；仍可能在组件离开后完成的请求，应取消或忽略其结果。循环更新要查“Effect 修改的状态是否又改变依赖”。Context value 的变化会影响相应消费者，但不能概括成必然重渲染整棵树。先复现一次不必要更新，再决定是否用 memo。

## ❓ 常见问题

### Q1: 页面跳走后定时器还在跑？
**A**: 经常是 `setInterval` 或订阅写在 useEffect 中却没有返回清理函数。仍会触发的 interval、监听器和请求都应在 cleanup 中停止、取消或让结果失效；已经自然结束且不会再回调的单次 timeout 不必为了形式额外保留。导航页面是否卸载也取决于导航器配置，不能假定跳走必然触发 cleanup。

### Q2: useEffect 里的接口请求竞态怎么处理？
**A**: 快速切换参数时旧请求可能后返回覆盖新数据。用 `AbortController` 取消旧请求，或在 setState 前比对请求序号（建议直接用 TanStack Query，见库指南）。

### Q3: 全局状态用 Context 还是 Redux/Zustand？
**A**: 主题/语言这类低频数据用 Context 足够；业务数据用 Zustand/TanStack Query，选型对比见 [state-and-data](../reference/library-guides/01-state-and-data.md)。

## 🎯 练习与实践

### 练习一：倒计时 Hook

**任务要求**:
1. 实现 `useCountdown(targetDate)` 返回剩余"天/时/分/秒"
2. 在界面上展示倒计时，组件卸载后用日志确认定时器已清除

**评估标准**: 记录目标时间、连续三次输出和卸载后至少等待两秒的日志；卸载后不再出现 tick。没有警告只是一条线索，不能代替这项行为观察。

### 练习二：屏幕方向 Hook

**任务要求**:
1. 用 `useWindowDimensions`（官方 Hook）实现 `useIsLandscape()`
2. 界面在横竖屏切换时展示不同布局

**提示**: `useWindowDimensions` 变化会触发重渲染，记得让布局样式基于它计算而非固定宽高。

---

## 🔗 相关文档

- 📄 **[导航基础](./05-navigation.md)**: 下一课，页面间传参离不开状态
- 📄 **[Hooks 速查](../reference/language-concepts/03-hooks-reference.md)**: 官方与社区 Hook 完整清单
- 📄 **[RN 核心 API 速查](../reference/language-concepts/01-rn-core-api.md)**: AppState 等被订阅对象的参数表
- 📄 **[状态与数据请求库指南](../reference/library-guides/01-state-and-data.md)**: Zustand/TanStack Query 选型
- 📄 **[TS 类型模式](../reference/language-concepts/04-typescript-patterns.md)**: Context 的类型安全写法

> 💡 **学习建议**: 把"每个订阅都要有清理"当成肌肉记忆——移动端页面频繁进出，泄漏会累积成卡顿甚至崩溃。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
