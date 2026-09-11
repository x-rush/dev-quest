# React Native 框架进阶 — 新架构、原生模块与动画

> **文档简介**: 面向任务的新架构开发指南：理解 Fabric 与 TurboModules 对日常开发的影响，用 Expo Modules API 封装原生能力，用 Reanimated 写出 60fps+ 的手势驱动动画
>
> **目标读者**: 能独立完成常规页面开发、希望深入框架底层的开发者
>
> **前置知识**: 已完成 [React Native 框架入门](./01-react-native-basics.md)；建议先读 [新架构解析](../advanced-topics/architecture/01-new-architecture.md) 了解"为什么"

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（frameworks） |
| **难度** | ⭐⭐ |
| **标签** | `#新架构` `#TurboModules` `#原生模块` `#Reanimated` |
| **更新日期** | 2026年9月 |

## 🎯 学习目标

- ✅ 理解新架构（Fabric/TurboModules/JSI）对 API 用法的实际约束
- ✅ 用 Expo Modules API 快速封装原生能力，必要时回落到 TurboModule
- ✅ 掌握 Reanimated 4 的 worklet 编程模型，实现 UI 线程动画
- ✅ 判断"哪些操作必须离开 JS 线程"

## 🏗️ 新架构下的开发约束

新架构（0.76 起默认开启，0.83 起为唯一架构，旧架构已移除）把渲染与原生调用全部重构，日常影响集中在三点（原理详见 [Fabric/TurboModules/JSI 架构解析](../advanced-topics/architecture/01-new-architecture.md)）：

1. **桥是同步的**：JSI 直调取代异步消息队列，原生同步方法（如 `measure`）不再强制回调地狱
2. **懒加载原生模块**：TurboModule 首次访问才初始化，App 启动不再为未用到的模块付费（启动优化见 [启动性能优化](../advanced-topics/performance/02-startup-optimization.md)）
3. **Fabric 严格要求初始化时机**：并发特性（`startTransition`、Suspense）可用，但组件树必须可中断渲染

```tsx
// 新架构推荐：用 useLayoutEffect 而非 setTimeout 等"等一帧"的 hack
import { useLayoutEffect, useState, startTransition } from 'react';

function SearchResults() {
  const [list, setList] = useState<Item[]>([]);
  const onChange = (text: string) => {
    startTransition(() => {   // 低优先级更新，保持键盘输入流畅
      fetchList(text).then(setList);
    });
  };
  // ...
}
```

## 🔌 原生模块：两条封装路线

手写 Android/iOS 原生模块的完整教程见 [原生模块桥接](../basics/06-native-modules.md)；此处聚焦"选路线"。

| 路线 | 适用场景 | 成本 |
|------|---------|------|
| **Expo Modules API**（推荐首选） | Swift/Kotlin 声明式封装，自动生成 JS 接口 | 低 |
| **TurboModule + Codegen** | 需要精确控制规格文件、参与开源生态 | 高 |

```ts
// Expo Modules API：三步封装一个"震动 + 触感"模块
// 1. android/src/.../HapticsModule.kt 用 Kotlin 声明（略，见 basics/06）
// 2. ios/HapticsModule.swift 用 Swift 声明（略）
// 3. src/index.ts 定义并导出 TS 接口
import { requireNativeModule } from 'expo-modules-core';

// requireNativeModule 在首次调用时才加载 TurboModule —— 懒加载即新架构默认行为
const Haptics = requireNativeModule<{
  impact: (style: 'light' | 'medium' | 'heavy') => void;
}>('Haptics');

export const hapticFeedback = (style: 'light' | 'medium' | 'heavy' = 'light') => {
  try {
    Haptics.impact(style);
  } catch {
    // 不支持的平台上静默降级，避免崩溃
    console.warn('haptics unavailable on this platform');
  }
};
```

## 🎬 Reanimated：UI 线程动画

动画分层的完整概念见 [高级特性 — Fabric、Hermes 与动画](../basics/07-advanced-features.md)；这里是任务式速成。

```tsx
// 可拖拽卡片：手势与动画都跑在 UI 线程，JS 掉帧也不影响跟手性
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';

export function DraggableCard() {
  const offsetX = useSharedValue(0);  // 共享值：UI 线程上的可变状态
  const offsetY = useSharedValue(0);

  // Pan 手势：onUpdate/onEnd 是 worklet，直接操作共享值
  const pan = Gesture.Pan()
    .onUpdate((e) => { offsetX.value = e.translationX; })
    .onEnd(() => {
      offsetX.value = withSpring(0);  // 松手 UI 线程自动回弹
      offsetY.value = withSpring(0);
    });

  // useAnimatedStyle 是 worklet：依赖的共享值变化即重算，不经过桥
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: offsetX.value }, { translateY: offsetY.value }],
  }));

  return (
    <GestureDetector gesture={pan}>
      <Animated.View style={[styles.card, animatedStyle]} />
    </GestureDetector>
  );
}
```

**worklet 规则**：`useAnimatedStyle`/手势回调内不能引用 JS 侧的可变变量（闭包捕获的是快照）；跨线程传值一律用 `useSharedValue` 与 `runOnJS`。

## ✅ 最佳实践

- ✅ **优先 Expo Modules API**，只有规格文件需求才写裸 TurboModule
- ✅ **动画数值动画化**：位移/缩放用 `transform` 与共享值，避免触发布局重算的属性（width/height/margin）
- ✅ **手势必须用 `react-native-gesture-handler`** 的 `GestureDetector`，原生 `onTouch` 拿不到 UI 线程
- ❌ **不要在动画循环里 setState**，每帧过一次桥会让 JS 线程饱和
- ❌ **不要混用旧版 `Animated` 与 Reanimated** 于同一节点，时序不可控

## ❓ 常见问题

**Q1: worklet 里报"Cannot access X because it is not a worklet"？**
A: 把需要的数据用 `useSharedValue` 或参数传入 worklet；纯函数加 `'worklet';` 指令声明。

**Q2: 新架构下第三方库报 `RCTBridge` 相关错误？**
A: 该库未适配新架构（现行 RN 已无旧架构兼容开关可退）。优先找替代库；否则等待/推动上游适配。

**Q3: 鸿蒙端动画能跑吗？**
A: RNOH 提供了 Fabric 与 Reanimated 的适配层，但部分版本支持滞后，发布前按 [RNOH 字典](../reference/language-concepts/05-harmonyos-rnoh-api.md) 核对版本对齐。

---

## 🔗 相关文档

- 📖 [RNOH 字典](../reference/language-concepts/05-harmonyos-rnoh-api.md) — 鸿蒙适配层对动画/新架构的支持矩阵
- 📖 [TypeScript 类型模式](../reference/language-concepts/04-typescript-patterns.md) — 原生模块的 TS 接口类型实践
- 📄 [原生模块桥接](../basics/06-native-modules.md) — 手写 Kotlin/Swift 模块的完整教程
- 📄 [高级特性 — Fabric、Hermes 与动画](../basics/07-advanced-features.md) — 动画概念入门
- 🎓 [Fabric/TurboModules/JSI 架构解析](../advanced-topics/architecture/01-new-architecture.md) — 本文的原理底座
- 🚀 [聊天应用实战](../projects/03-chat-app.md) — 动画与列表优化的综合演练
