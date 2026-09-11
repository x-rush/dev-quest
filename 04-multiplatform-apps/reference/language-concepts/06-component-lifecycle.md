# 组件生命周期 — 挂载、更新与卸载

> **难度**: ⭐ | **前置**: 理解组件与 Props（[03-components-jsx](../../basics/03-components-jsx.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#生命周期` `#Effect` `#挂载` `#卸载` |
| **更新日期** | `2026年9月` |

## 📌 定义

RN 组件生命周期与 React 完全一致：**挂载（mount）→ 更新（update）→ 卸载（unmount）** 三个阶段。现代 RN 开发只使用函数组件，生命周期的"钩子"不再是一组类方法，而是**渲染过程 + Effect 副作用同步点**：

- **渲染**（纯计算）：组件函数执行，返回 UI 描述。应当纯净，不产生副作用
- **Effect 同步**（副作用）：渲染提交到屏幕后（`useEffect`）或绘制前（`useLayoutEffect`）执行，用于与外部系统同步
- **清理**（卸载/重同步前）：Effect 返回的清理函数在组件卸载或依赖变化前调用

> 概念上对应类组件时代的 `componentDidMount` / `componentDidUpdate` / `componentWillUnmount`，但 Effect 的语义是"随依赖重同步"，不是"只在挂载时跑一次"。

## 📖 语法/签名

```tsx
// 副作用同步的标准签名
useEffect(() => {
  // 建立同步：订阅、请求、定时器
  const subscription = something.addEventListener('change', handler);
  return () => {
    // 清理：卸载前 / 下一次依赖变化前执行
    subscription.remove();
  };
}, [deps]); // deps 决定"何时重新同步"

useLayoutEffect(() => { /* 绘制前同步执行，用于测量 */ }, [deps]);
```

## 💡 示例

```tsx
import { useEffect, useState } from 'react';
import { AppState, Text } from 'react-native';

function AppStateBadge() {
  const [state, setState] = useState(AppState.currentState);

  useEffect(() => {
    // 挂载后订阅；deps 为空数组 = 只依赖"组件是否存在"
    const sub = AppState.addEventListener('change', setState);
    return () => sub.remove(); // 卸载时退订，防止泄漏
  }, []);

  return <Text>{state === 'active' ? '前台' : '后台'}</Text>;
}
```

## ⚠️ 常见陷阱

- **依赖数组漏写**：闭包捕获旧值，"偶现"读旧数据；用 `eslint-plugin-react-hooks` 强制检查
- **把 Effect 当生命周期事件**：`[]` 只该用于真正与组件共存亡的同步（订阅、测量），不是"初始化逻辑垃圾桶"
- **清理函数忘写**：定时器、订阅、动画句柄不清理 = 内存泄漏与卸载后 setState 警告
- **用"等一帧"类 hack 协调时序**：新架构渲染提交可中断、时序更严格，测量需求用 `useLayoutEffect` 或 `onLayout` 表达
- **渲染期做异步/IO**：读存储、发请求必须进 Effect 或事件回调

## 🔗 相关条目

- 📄 [状态与 Hooks 教程](../../basics/04-state-hooks.md) — 生命周期的入门讲法
- 📄 [Hooks 速查](./03-hooks-reference.md) — 每个 Effect 类 Hook 的签名与陷阱
- 📄 [状态管理模型](./07-state-management.md) — 副作用与状态放置的关系
- 📄 [渲染性能](../../advanced-topics/performance/01-rendering-performance.md) — 更新阶段的成本分析

*延伸: React 官方文档 "You Might Not Need an Effect"*
