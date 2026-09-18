# 动画核心 API 速查

> **阅读准备**：State 驱动的 UI 与协程；知道动画中的当前值、目标值和速度不是同一个量。

> 从"状态差"自动生成过渡的声明式动画：animate*AsState / Animatable / rememberInfiniteTransition / AnimatedVisibility / animateContentSize / updateTransition

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#动画` `#animateAsState` `#Animatable` `#AnimatedVisibility` `#Transition` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

Compose 动画的统一心智模型：**动画 = 随时间驱动的状态**。所有高层 API 本质都是"监听目标值 → 用动画曲线（spring / tween）插值 → 每帧写回 State"，状态读取所在阶段决定哪些阶段需要更新，动画不必每帧都重组，开发者只需改变**目标状态**，不需要手动管理帧循环。

## 📖 语法与签名

| API | 签名要点 | 适用场景 |
|-----|---------|---------|
| `animate*AsState` | `animateFloatAsState(targetValue, animationSpec, label)` 等系列 | 单值目标切换（颜色 / 尺寸 / 位移） |
| `Animatable` | `Animatable(initialValue)` + `suspend fun animateTo(target, spec)` | 协程中编排多段动画 |
| `rememberInfiniteTransition` | + `animateFloat(initial, target, infiniteRepeatable(...))` | 无限循环动画（脉冲、加载） |
| `AnimatedVisibility` | `AnimatedVisibility(visible, enter, exit)` | 内容出现 / 消失的进出场 |
| `animateContentSize` | `Modifier.animateContentSize()` | 容器尺寸变化平滑过渡 |
| `updateTransition` | `updateTransition(targetState, label)` + `transition.animate*` | 多属性随同一状态联动 |
| `Crossfade` | `Crossfade(targetState)` | 内容切换淡入淡出 |

## 💡 示例

```kotlin
// 1. 单值切换：状态改变即动画（记得用 by 委托解包 State）
var expanded by remember { mutableStateOf(false) }
val elevation by animateDpAsState(if (expanded) 16.dp else 4.dp, label = "elevation")
Card(elevation = CardDefaults.cardElevation(elevation)) { /* ... */ }

// 2. Animatable：协程里编排多段动画
val alpha = remember { Animatable(0f) }
LaunchedEffect(Unit) {
    alpha.animateTo(1f, tween(durationMillis = 600))
    alpha.animateTo(0.6f, spring())
}

// 3. 无限脉冲动画
val infinite = rememberInfiniteTransition(label = "pulse")
val scale by infinite.animateFloat(
    initialValue = 0.9f, targetValue = 1.1f,
    animationSpec = infiniteRepeatable(tween(800), RepeatMode.Reverse),
    label = "scale",
)

// 4. 进出场动画组合
AnimatedVisibility(
    visible = isVisible,
    enter = fadeIn() + slideInVertically(),
    exit = fadeOut() + slideOutVertically(),
) {
    Text("提示条")
}
```

## ⚠️ 常见陷阱

- `animate*AsState` 返回 `State<T>`：漏写 `by` 委托拿到的就是 State 对象而不是值。
- `Animatable.animateTo` 是 **suspend 函数**——必须在协程 / 副作用作用域（如 `LaunchedEffect`）中调用。
- 无限循环动画跟随组合生命周期自动取消，但不要把它放到全局 scope 里手动跑——组件离屏仍会持续执行。
- 动画中间值不要用 `rememberSaveable` 持久化：恢复时直接落到目标值即可，存中间值会闪跳。
- 多属性联动各自堆 `animate*AsState` 会各自为战、时序不齐——同源联动用 `updateTransition`。

<!-- full-library-explanation -->
## 目标值、当前值和读取阶段

目标为 1 不表示动画这一帧已经到 1。动画进行中再次改变目标，API 按其规则接续或取消；业务是否提交完成不能仅凭视觉进度决定。动画值在组合阶段读取会影响重组，在 graphicsLayer 等后续阶段读取则可缩小更新范围。

练习：给展开卡片添加按钮，快速连续点击三次，再离开页面。验收：最后状态对应最后一次操作，离开后没有独立全局任务继续更新；关闭系统动画或启用减少动态效果时内容仍可理解。调试时记录目标状态，测试时用可控时钟观察起点、中间和终点，而不是固定 sleep。

只有透明度变为 0 并不等于节点已从布局或语义树移除。需要真正隐藏的交互内容，应明确控制可见性、可点击性和无障碍行为。

## 🔗 相关条目

- 📄 [Compose 状态 API](../language-concepts/04-compose-state-api.md)
- 📄 [副作用 API](./03-side-effects.md) — LaunchedEffect 驱动 Animatable
- 📄 [重组与稳定性](./04-recomposition.md) — 动画每帧写状态的代价
- 📄 操作指南：[Compose 进阶 - 动画](../../frameworks/02-compose-advanced.md)
- 📖 官方文档：[Compose Animation](https://developer.android.com/develop/ui/compose/animation)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
