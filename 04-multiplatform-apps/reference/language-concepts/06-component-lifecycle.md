# 组件生命周期 — 挂载、更新与卸载

## 生命周期不是只执行一次的时间线

前置：组件渲染与 useEffect。把渲染看作计算界面，把 effect 看作建立外部同步，把 cleanup 看作解除这次同步。挂载、依赖变化、卸载分别影响同步的建立和清理；开发检查还可能额外运行建立/清理来暴露问题。

例如订阅聊天消息时，effect 依赖会话 ID。切换会话应先移除旧订阅再建立新订阅，卸载后不应继续接收更新。空依赖数组不代表整个应用生命期只执行一次，更不能替代稳定的服务端去重。

自测：进会话 A、切到 B、离开页面，再进入 B。每条 B 消息只处理一次，A 消息不更新 B。用订阅数量或日志验证，而不是根据界面看起来正常推断没有泄漏。

> **难度**: ⭐ | **前置**: 理解组件与 Props（[03-components-jsx](../../basics/03-components-jsx.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#生命周期` `#Effect` `#挂载` `#卸载` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

RN 组件生命周期与 React 完全一致：**挂载（mount）→ 更新（update）→ 卸载（unmount）** 三个阶段。本条目使用函数组件，生命周期的"钩子"不再是一组类方法，而是**渲染过程 + Effect 副作用同步点**：

- **渲染**（纯计算）：组件函数执行，返回 UI 描述。应当纯净，不产生副作用
- **Effect 同步**（副作用）：提交后运行 `useEffect`；需要绘制前完成的布局工作使用 `useLayoutEffect`，不把 Effect 当固定下一帧调度器，用于与外部系统同步
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

## 从组件可见性验证订阅清理

前置产物是已有能在 Android 或 iOS 启动的 RN 工程。上面的代码是组件定义，不是工程入口：保存到 `src/AppStateBadge.tsx`，给函数加 `export`，由现有屏幕导入。Expo Router 工程在当前路由中渲染，不另建第二个入口。

先把显示表达式改成 `<Text>应用状态：{state ?? 'unknown'}</Text>`。AppState 不只有 active/background：iOS 还可经过 inactive；保留原始字符串可避免把中间状态误判成后台。在 Effect 建立订阅前打印 `badge: subscribe`，在 cleanup 内先打印 `badge: cleanup` 再调用 sub.remove；监听回调改为打印 `badge: change` 与 next，然后 setState(next)。这是替换原回调，不要增加第二个订阅。

父屏幕用 `useState(true)` 保存 visible，Button 的 `onPress={() => setVisible(v => !v)}` 切换，再用 `{visible && <AppStateBadge />}` 条件渲染。父屏幕需导入 useState、Button、View 和 AppStateBadge。沿以下步骤记录实际日志：

| 输入与阶段 | 预期输出 | 失败回查 |
|---|---|---|
| 点击卸载，再重新挂载 | Text 消失再出现；订阅有对应清理 | 是否真正移除子树，而非仅隐藏样式 |
| 保持挂载，切其他应用再返回 | change 日志与原始状态字符串更新 | 平台是否经过 inactive；系统可能暂停后台应用 |
| 卸载后切后台/前台 | 不再产生该标记的 change 日志 | cleanup 是否 remove 本次建立的订阅 |
| 连续挂载/卸载五次后切应用 | 回调不随历史挂载次数增长 | 是否漏清理、在渲染体订阅，或存在多个组件实例 |

Strict Mode 开发检查可能先建立、清理、再建立；应验收对称释放，不要求首次只打印一次。应用切后台通常不卸载组件；导航离开页面也可能仅失去焦点。这三种输入需要分别处理，不能把没有 cleanup 直接判断为框架错误。现代 React 是否打印“卸载后更新”警告也不能证明订阅是否泄漏。

练习：由父组件传入日志 label，增加 A/B 切换按钮。Effect 读取 label 后将其加入依赖数组；预期先清理旧 A，再建立 B，后续事件只打印 B。漏依赖保留 A 闭包时，先修正依赖，而不是更换原生事件 API。

**验证边界：** 本轮依据官方 [React useEffect](https://react.dev/reference/react/useEffect) 与 [RN AppState](https://reactnative.dev/docs/appstate) 核对同步与订阅契约，未启动 RN 工程、模拟器或真机。表内是待执行验收，不是本轮运行记录。

## ⚠️ 常见陷阱

- **依赖数组漏写**：闭包捕获旧值，"偶现"读旧数据；用 `eslint-plugin-react-hooks` 强制检查
- **把 Effect 当生命周期事件**：`[]` 只该用于真正与组件共存亡的同步（订阅、测量），不是"初始化逻辑垃圾桶"
- **清理函数忘写**：定时器、订阅、动画句柄不清理 = 重复回调与未释放资源，是否出现警告不能作为泄漏判据
- **用"等一帧"类 hack 协调时序**：新架构渲染提交可中断、时序更严格，测量需求用 `useLayoutEffect` 或 `onLayout` 表达
- **渲染期做异步/IO**：读存储、发请求必须进 Effect 或事件回调

## 🔗 相关条目

- 📄 [状态与 Hooks 教程](../../basics/04-state-hooks.md) — 生命周期的入门讲法
- 📄 [Hooks 速查](./03-hooks-reference.md) — 每个 Effect 类 Hook 的签名与陷阱
- 📄 [状态管理模型](./07-state-management.md) — 副作用与状态放置的关系
- 📄 [渲染性能](../../advanced-topics/performance/01-rendering-performance.md) — 更新阶段的成本分析

*延伸: React 官方文档 "You Might Not Need an Effect"*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
