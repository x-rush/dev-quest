# 手势 API

> **阅读准备**：Modifier、协程与事件回调；掌握局部坐标、位移和最终位置的区别。

> pointerInput 三层手势体系：组件级 clickable、检测器级 detectTapGestures/detectDragGestures/detectTransformGestures、底层 awaitEachGesture/awaitPointerEventScope——以及事件消费与系统手势冲突处理

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#手势` `#pointerInput` `#detectTapGestures` `#事件消费` |
| **更新日期** | `2026年9月` |

> 本文属 Compose 框架层：API 签名按官方文档核对书写，**未实测（无 Android 环境）**，不编造参数名；纯 Kotlin 断言见语言概念篇。

---

## 📌 定义

Compose 手势 API 分三层，**优先使用能满足需求的高层 API**：

1. **组件级**：`Modifier.clickable`/`combinedClickable`/`scrollable`——自带涟漪反馈、无障碍语义（`onClick` action）、焦点处理。
2. **检测器级**：`Modifier.pointerInput(key) { detectXxxGestures(...) }`——预制的点按/拖拽/变换检测器，消化原始事件流后回调。
3. **底层**：`awaitEachGesture`/`awaitPointerEventScope` + `PointerEvent`/`PointerEventPass`——逐事件处理，实现自定义手势与拦截逻辑。

## 📖 语法与签名

### 1. 检测器级 API（`pointerInput` 内调用）

| 检测器 | 回调要点 | 场景 |
|--------|---------|------|
| `detectTapGestures(onPress, onDoubleTap, onLongPress, onTap)` | 四个回调均可选（尾 lambda 即 `onTap`）；存在 `onDoubleTap` 时单击会延迟一拍 | 点按/双击/长按 |
| `detectDragGestures(onDragStart, onDragEnd, onDragCancel, onDrag)` | `onDrag: (change: PointerInputChange, dragAmount: Offset) -> Unit`，任意方向 | 自由拖拽 |
| `detectDragGesturesAfterLongPress` | 同上，但长按后才进入拖拽 | 列表排序手柄 |
| `detectTransformGestures(panZoomLock, onGesture)` | `onGesture: (centroid: Offset, pan: Offset, zoom: Float, rotation: Float) -> Unit`（无返回值；事件消费由检测器内部处理，回调不接收消费标记） | 双指缩放/旋转 |

```kotlin
Modifier.pointerInput(Unit) {
    detectTapGestures(
        onDoubleTap = { tapOffset -> /* 双击位置 */ },
        onLongPress = { /* */ },
    ) { tapOffset -> /* 单击 */ }
}
```

### 2. 底层 API

| API | 一行语义 |
|-----|---------|
| `pointerInput(key1, block)` / `pointerInput(key1, key2, block)` | 挂起手势处理协程；**key 变化时取消旧块、重启新块**（用于把 lambda/状态固化进闭包） |
| `awaitEachGesture { }` | 每个手势（按下→全部抬起）跑一轮块体，结束自动等待下一次按下 |
| `awaitFirstDown(requireUnconsumed = true)` | 等第一个按下事件 |
| `waitForUpOrCancellation()` | 等抬起；中途被消费/取消返回 null（"点击是否有效"的判据） |
| `awaitPointerEventScope { }` | 事件级作用域，`awaitPointerEvent()` 逐事件取 |
| `PointerEventPass` | `Initial`（父→子预览）/ `Main`（子→父，默认处理）/ `Final`（父→子收尾） |
| `PointerInputChange.consume()` | 标记事件已消费，`isConsumed` 判断（与其他处理器协作的消费标记） |

### 3. 与组件级手势的分工

| 需求 | 用 |
|------|-----|
| 单击/长按/双击一个可点击元素 | `clickable` / `combinedClickable`（要涟漪与无障碍） |
| 滚动条目 | `verticalScroll`/`LazyColumn`（系统手势，勿手写） |
| 自定义点按语义（无涟漪的遮罩层、图片双击缩放） | `pointerInput` + `detectTapGestures` + 手动补 `semantics` |
| 拖拽跟手 / 双指变换 | `pointerInput` + `detectDragGestures` / `detectTransformGestures` |

## 💡 示例

```kotlin
// 1. 图片双击缩放（官方示例模式）
var zoomed by remember { mutableStateOf(false) }
var zoomOffset by remember { mutableStateOf(Offset.Zero) }
Image(
    painter = painter,
    contentDescription = null,
    modifier = Modifier
        .pointerInput(Unit) {
            detectTapGestures(
                onDoubleTap = { tapOffset ->
                    zoomOffset = if (zoomed) Offset.Zero else calculateOffset(tapOffset, size)
                    zoomed = !zoomed
                }
            )
        }
        .graphicsLayer {
            scaleX = if (zoomed) 2f else 1f
            scaleY = if (zoomed) 2f else 1f
            translationX = zoomOffset.x
            translationY = zoomOffset.y
        }
)

// 2. 自由拖拽：必须在 onDrag 里消费事件
var offsetX by remember { mutableFloatStateOf(0f) }
var offsetY by remember { mutableFloatStateOf(0f) }
Box(
    Modifier
        .offset { IntOffset(offsetX.roundToInt(), offsetY.roundToInt()) }
        .pointerInput(Unit) {
            detectDragGestures { change, dragAmount ->
                change.consume()
                offsetX += dragAmount.x
                offsetY += dragAmount.y
            }
        }
)

// 3. 底层：手写一个"简单 clickable"（官方示例模式）
Modifier.pointerInput(onClick) {
    awaitEachGesture {
        awaitFirstDown().also { it.consume() }
        val up = waitForUpOrCancellation()
        if (up != null) { up.consume(); onClick() }
    }
}

// 4. 事件级循环：记录指针事件
Modifier.pointerInput(Unit) {
    awaitPointerEventScope {
        while (true) {
            val event = awaitPointerEvent()
            log("类型=${event.type}, 位置=${event.changes.first().position}")
        }
    }
}
```

## ⚠️ 常见陷阱

- ❌ 用 `pointerInput + detectTapGestures` 实现普通按钮点击——丢失涟漪反馈与无障碍 onClick 语义。
  ✅ 能用 `Modifier.clickable`/`combinedClickable` 就不用检测器；自定义点按区域时补 `semantics(mergeDescendants = true) { onClick { ...; true } }`。
- ❌ `pointerInput(Unit)` 里捕获"每次重组都变"的 lambda/状态——块只在 key 变化时重启，Unit 不随普通重组改变，但重新进入组合等仍会重新启动；捕获普通参数与读取同一 State 对象要区分。
  ✅ 把依赖作为 key：`pointerInput(onClick) { detectTapGestures { onClick() } }`；或用 `rememberUpdatedState` 固定引用。
- ❌ 拖拽回调里忘记 `change.consume()`——外层可滚动容器（`verticalScroll`/`LazyColumn`）会同时响应同一手势，"拖动子元素时列表也在滚"。
  ✅ 处理完即消费；反过来，需要**父级优先**拦截（下拉刷新等）时，在 `PointerEventPass.Initial` 阶段由父级消费。
- ❌ 在 `awaitPointerEventScope { }` 内调用指针事件无关的挂起函数（`delay`、网络请求）——破坏事件时序保证，事件可能被丢弃。
  ✅ 该受限挂起作用域只能调用允许的挂起操作；网络等工作移到适当的外部作用域；跨手势的耗时逻辑放到作用域外。
- ❌ 在可滚动列表子项上用 `detectDragGestures` 做横滑操作——拖拽与列表滚动系统竞争，行为漂移。
  ✅ 方向性拖拽用 `Modifier.draggable`/`anchoredDraggable`（与滚动系统协调）。
- ❌ 以为父级包一层 `clickable` 子级就不再触发——Compose 事件默认**子级先处理**（`Main` pass）。
  ✅ 需要父级先看一眼时用 `PointerEventPass.Initial` + 消费；未消费语义的检测器（`requireUnconsumed`）会自动跳过已消费事件。

<!-- full-library-explanation -->
## 手势事件消费是协作协议

consume 设置已消费标记，并不神奇地让事件从其他处理器眼前消失；其他处理器要尊重消费状态。高级检测器也可能已经消费相关变化，应查所用检测器契约，而非一律认为不手写 consume 就必然冲突。

pointerInput 的 key 改变可能中断正在进行的手势，因此每帧变化的位置一般不适合作为重启 key。若只想用最新回调，可通过 rememberUpdatedState 读取；若是拖拽对象换了身份，则重启才是合理行为。闭包持有同一个 State 对象时可以读取其新值，不等于“永远只能看到首次快照”。

练习：在纵向列表中做横向拖拽，分别测试短点按、斜向拖动、第二根手指加入、手势取消。验收：滚动与拖拽的优先规则一致；完成动作也能通过可访问按钮执行；自由拖动的 Box 具有明确尺寸与背景，否则空盒子可能没有可触摸面积。

## 🔗 相关条目

- 📄 **[Compose 核心组件速查](./01-compose-essentials.md)** - clickable/scrollable 等 Modifier 全表
- 📄 **[@Composable 与组合模型](./08-composition-model.md)** - pointerInput key 与重组的关系
- 📄 **[Canvas 自定义绘制](./10-canvas-drawing.md)** - 手势驱动的绘制目标
- 📄 **[Compose 状态 API](../language-concepts/04-compose-state-api.md)** - rememberUpdatedState 防旧闭包
- 🌐 **[Understand gestures（官方文档）](https://developer.android.com/develop/ui/compose/touch-input/pointer-input/understand-gestures)** - PointerEventPass 与事件分发模型
- 🌐 **[Drag, swipe, fling（官方文档）](https://developer.android.com/develop/ui/compose/touch-input/pointer-input/drag-swipe-fling)** - 拖拽官方指南

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
