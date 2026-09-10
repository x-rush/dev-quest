# 状态管理 — useState/useEffect 与自定义 Hook

> **文档简介**: 掌握 React Hooks 在移动端的正确用法：useState/useEffect、自定义 Hook 封装设备能力，以及 Context 处理全局状态
>
> **目标读者**: 会写静态界面的 RN 初学者，希望理解"状态驱动 UI"
>
> **前置知识**: 完成 [03-components-jsx](./03-components-jsx.md)，有 React Hooks 基础概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#Hooks` `#useState` `#useEffect` `#Context` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 useState/useEffect 实现计时器、表单等交互界面
- ✅ 正确处理 useEffect 的清理函数，避免移动端特有的内存泄漏
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
    // 清理函数：离开页面必须清除定时器，否则泄漏
    return () => clearInterval(id);
  }, []); // 空依赖 = 只在挂载后执行一次

  return <Text>已运行 {seconds} 秒</Text>;
}
```

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
    const appState = AppState.addEventListener('change', (s) => {
      if (s === 'active') {
        NetInfo.fetch().then((state) => setIsConnected(Boolean(state.isConnected)));
      }
    });
    return () => {
      unsubscribe();
      appState.remove();
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

### ✅ 推荐做法
- **副作用分层**: 组件内只留"页面级"副作用，可复用逻辑全部抽成自定义 Hook
- **每个订阅都配清理**: `addEventListener` 与 `remove`/`unsubscribe` 成对出现
- **依赖数组如实填写**: 用 ESLint 插件 `eslint-plugin-react-hooks` 强制检查

### ❌ 避免陷阱
- **在 useEffect 里直接 setState 无限循环**: 忘写依赖数组或依赖了每次变化的对象
- **对象/数组作为 useState 初始值**: 每次渲染新建引用，应惰性初始化 `useState(() => heavyInit())`
- **Context value 忘记 useMemo**: 导致整棵子树级联重渲染

## ❓ 常见问题

### Q1: 页面跳走后定时器还在跑？
**A**: 定时器写在 useEffect 且没有返回清理函数。任何 `setInterval`/`setTimeout`/订阅都必须在 cleanup 中回收；导航卸载时 RN 不会替你做。

### Q2: useEffect 里的接口请求竞态怎么处理？
**A**: 快速切换参数时旧请求可能后返回覆盖新数据。用 `AbortController` 取消旧请求，或在 setState 前比对请求序号（建议直接用 TanStack Query，见库指南）。

### Q3: 全局状态用 Context 还是 Redux/Zustand？
**A**: 主题/语言这类低频数据用 Context 足够；业务数据用 Zustand/TanStack Query，选型对比见 [state-and-data](../reference/library-guides/01-state-and-data.md)。

## 🎯 练习与实践

### 练习一：倒计时 Hook

**任务要求**:
1. 实现 `useCountdown(targetDate)` 返回剩余"天/时/分/秒"
2. 在界面上展示倒计时，组件卸载后用日志确认定时器已清除

**评估标准**: 1 秒 tick 一次且无泄漏警告。

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
