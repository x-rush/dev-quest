# 动画与手势库 — 共享值、worklet 与手势系统

> **难度**: ⭐⭐ | **前置**: 读过[动画教程](../../basics/07-advanced-features.md)更佳

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Reanimated` `#Gesture Handler` `#worklet` `#共享值` |
| **更新日期** | `2026年9月` |

## 📌 定义

现代 RN 动画的模型是**"UI 线程上的响应式系统"**，库是该模型的实现载体：

- **共享值（shared value）**：一个同时可被 JS 线程与 UI 线程读写的响应式数值。改它不触发 React 重渲染——这是"跟手"的关键
- **worklet**：声明可运行在 UI 线程的小函数（`useAnimatedStyle` 回调、手势回调天然是 worklet）。worklet 里引用 JS 可变变量只拿到快照，跨线程通信必须经共享值或 `runOnJS`
- **派生样式（animated style）**：worklet 依据共享值计算样式对象，值变即重算，直接提交给渲染器，绕过 setState
- **手势系统两层**：原生响应链（`onTouch`/responder）在 JS 侧、能力有限；专用手势库（Gesture Handler）在原生层识别手势并以事件流喂给 worklet，跟手动画由此闭环
- **动画函数**：`withSpring` / `withTiming` / `withDecay` 等在 UI 线程驱动物理插值，可与手势衔接（手势中断时动画接力）

**心智模型**：state 驱动"业务 UI"（低频、经 React）；共享值驱动"连续交互"（每帧、绕过 React）。两条通路不要互相入侵。

## 📖 语法/签名

```ts
import {
  useSharedValue,      // () => SharedValue<T>          UI 线程可写的响应式值
  useAnimatedStyle,    // (worklet) => StyleProp         值变即重算的派生样式
  useAnimatedScrollHandler, // (worklet) => ScrollHandler 滚动联动
  withSpring,          // (toValue, config?) => Animation 物理插值
  runOnJS,             // (fn)(...args)                  从 worklet 调回 JS 线程
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';

const offset = useSharedValue(0);          // 1. 声明共享值
const pan = Gesture.Pan()
  .onUpdate((e) => { offset.value = e.translationX; })  // 2. 手势事件流直接写值
  .onEnd(() => { offset.value = withSpring(0); });      // 3. 松手交还给物理动画

const style = useAnimatedStyle(() => ({                 // 4. 派生样式消费值
  transform: [{ translateX: offset.value }],
}));
// <GestureDetector gesture={pan}><Animated.View style={style} /></GestureDetector>
```

## 💡 示例

```tsx
// 滚动联动：头部视差（每帧更新，不经 React）
import Animated, {
  useSharedValue, useAnimatedStyle,
  useAnimatedScrollHandler, interpolate,
} from 'react-native-reanimated';

function ParallaxHeader() {
  const scrollY = useSharedValue(0);
  const onScroll = useAnimatedScrollHandler((e) => { scrollY.value = e.contentOffset.y; });
  const headerStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: interpolate(scrollY.value, [0, 200], [0, 100]) }],
    opacity: interpolate(scrollY.value, [0, 200], [1, 0]),
  }));
  return (
    <>
      <Animated.View style={[{ height: 200 }, headerStyle]} />
      <Animated.ScrollView onScroll={onScroll} scrollEventThrottle={16}>
        {/* 长列表内容 */}
      </Animated.ScrollView>
    </>
  );
}
```

## 内置 Animated vs Reanimated 边界

`react-native` 内置的 `Animated` 与 `react-native-reanimated` 是两套独立驱动体系，选型的分界线是**"要不要跟手"**：

| 维度 | 内置 Animated | Reanimated |
|------|--------------|------------|
| 驱动线程 | `useNativeDriver: true` 时插值在原生线程，否则全在 JS 线程（每帧过通信通道） | worklet 常驻 UI 线程，每帧更新不过 React |
| 手势/滚动联动 | 事件回调回到 JS 侧处理，跟手有限 | Gesture Handler 事件流直达 worklet，逐帧跟手 |
| 动画中断接力 | 中断后需手动衔接 | `withSpring` 等物理动画自动接管当前值 |
| 典型场景 | 入场淡入、一次性过渡、简单循环 | 跟手抽屉、视差滚动、手势打断、复杂编排 |
| 创建入口 | `new Animated.Value()` 或 Hook `useAnimatedValue` | `useSharedValue` |

选型两条硬规则：

1. **简单一次性动画用内置 Animated 足够**——记得始终给 `useNativeDriver: true`（仅支持非布局属性：transform/opacity 等），布局属性动画留给布局重排或换实现
2. **跟手、滚动帧级联动、可中断动画一律 Reanimated**——内置 Animated 的事件通道延迟做不了逐帧反馈

**混用禁令**：同一节点不要同时挂两套动画驱动（如 `Animated.View` 又接 Reanimated style），驱动时序不可控；两套体系可以共存于**不同**组件节点。`Animated.ScrollView` 等内置滚动容器要与 Reanimated 的 `useAnimatedScrollHandler` 联动时，改用 Reanimated 导出的 `Animated.ScrollView`。

## ⚠️ 常见陷阱

- **worklet 内 setState / 读外部可变量**：闭包捕获的是快照，且每帧 setState 会击穿 React；跨线程传值用共享值与 `runOnJS`
- **动画布局属性**：width/height/margin 触发重布局，掉帧；位移缩放用 `transform`
- **滚动联动不用 scrollHandler**：`onScroll` 回调在 JS 线程，每帧过桥必卡；用 `useAnimatedScrollHandler`
- **`scrollEventThrottle` 拉满却换 JS 回调**：节流解决不了线程问题，先选对通道
- **未适配新架构的动画库版本**：现行 RN 生态的动画/手势主流库仅支持新架构，鸿蒙端还需 RNOH 适配分支（见 [RNOH 字典](../language-concepts/05-harmonyos-rnoh-api.md)）
- **把 Animated（内置）与 Reanimated 混挂同一节点**：两套驱动时序不可控，二选一

## 🔗 相关条目

- 📄 [动画教程 — Fabric、Hermes 与动画](../../basics/07-advanced-features.md) — 动画分层概念入门
- 📄 [框架进阶 — 新架构、原生模块与动画](../../frameworks/02-react-native-advanced.md) — worklet 的任务式速成
- 📄 [渲染性能](../../advanced-topics/performance/01-rendering-performance.md) — 掉帧归因与规避清单
- 📄 [桥接与原生通信原理](../language-concepts/08-bridge-principles.md) — 为什么 UI 线程动画能绕过 JS

*延伸: Reanimated 官方文档 "Fundamentals" · Gesture Handler 文档 "Gestures API"*
