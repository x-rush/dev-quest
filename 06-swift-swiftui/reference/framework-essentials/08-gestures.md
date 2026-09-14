# SwiftUI 手势 API 速查

> **文档简介**: SwiftUI 手势全量速查：五大手势类型与组合（Sequence/Simultaneous/Exclusive）、@GestureState 与 updating 回传、gesture() 系修饰符、与 .onTapGesture 简写的分工
>
> **目标读者**: 需要给视图加拖拽/捏合/长按等交互的全体学习者（字典条目，可任意跳入）
>
> **前置知识**: 视图与状态基础见 [basics/04-views-state.md](../../basics/04-views-state.md)；状态包装器对照见 [../language-concepts/04-swiftui-state-api.md](../language-concepts/04-swiftui-state-api.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#SwiftUI` `#手势` `#Gesture` `#交互` |
| **更新日期** | `2026年9月` |

## 📌 定义

SwiftUI 手势是**可组合的值**（不是回调）：先构造 `Gesture` 实例，再用 `.gesture()` 挂到视图上，通过 `updating`/`onEnded` 把手势值回传给状态。

---

## 1. 手势类型

| 手势 | 定义 | 关键参数 / 值 |
|------|------|---------------|
| `TapGesture(count:)` | 点按 | `onEnded` 触发（简写见 §4） |
| `LongPressGesture(minimumDuration:maximumDistance:)` | 长按（默认 0.5s） | 按压位移超 10pt 判失败 |
| `DragGesture(minimumDistance:coordinateSpace:)` | 拖拽 | value 见 §3 |
| `MagnificationGesture` | 捏合缩放 | value: `CGFloat` 倍率；**iOS 17 起改名 `MagnifyGesture`**（value: `.magnification`），旧名已弃用 |
| `RotationGesture` | 旋转 | value: `Angle`；**iOS 17 起改名 `RotateGesture`**（value: `.rotation`），旧名已弃用 |
| `SequenceGesture(a, b)` | 顺序：a 识别后接管给 b | value: `.first`/`.second` 两分支 |
| `SimultaneousGesture(a, b)` | 同时识别 | a、b 各自更新 |
| `ExclusiveGesture(a, b)` | 排他：a 优先，失败才轮到 b | value: 只有一边 |

## 2. 状态回传：@GestureState 与 updating

```swift
struct ZoomableImage: View {
    @GestureState private var scale: CGFloat = 1.0     // 手势结束自动回 1.0

    var body: some View {
        Image("photo")
            .scaleEffect(scale)
            .gesture(
                MagnifyGesture()
                    .updating($scale) { value, state, _ in
                        state = value.magnification     // 每帧回传
                    }
            )
    }
}
```

| 工具 | 生命周期 | 用途 |
|------|----------|------|
| `@GestureState` | **手势结束自动复位**到初值 | 只反映"进行中"的瞬时值 |
| `@State` + `onEnded` | 手动管理，不清零 | 保存最终结果（提交位移/缩放） |

`updating` 闭包签名：`{ value: Gesture.Value, state: inout State, transaction: inout Transaction in }`。

**标准套路**: 过程值给 `@GestureState`，结果值给 `@State`，`onEnded` 里合并：

```swift
@GestureState var dragging: CGSize = .zero
@State var position: CGSize = .zero

content
    .offset(x: position.width + dragging.width,
            y: position.height + dragging.height)
    .gesture(
        DragGesture()
            .updating($dragging) { v, s, _ in s = v.translation }
            .onEnded { v in position.width += v.translation.width
                              position.height += v.translation.height }
    )
```

## 3. DragGesture.Value 字段

| 字段 | 类型 | 含义 |
|------|------|------|
| `translation` | CGSize | 相对起点的位移（拖拽核心值） |
| `startLocation` / `location` | CGPoint | 起点 / 当前点（局部坐标） |
| `predictedEndTranslation` | CGSize | 按速度预测的落点位移（惯性/翻页判断） |
| `predictedEndLocation` | CGPoint | 预测终点 |
| `time` | Date | 手势开始时间 |
| `velocity` | CGSize | 速度（**iOS 17+**） |

## 4. 挂载修饰符与简写分工

| 修饰符 | 语义 |
|--------|------|
| `.gesture(g)` | 常规挂载（默认给系统控件让路） |
| `.simultaneousGesture(g)` | 与系统手势**并行**识别 |
| `.highPriorityGesture(g)` | 优先于子视图/系统手势 |
| `.onTapGesture { }` / `.onLongPressGesture { }` | 点按/长按**简写**，等价于挂 TapGesture |

**分工原则**:

- 纯点按/长按 → `.onTapGesture`/`.onLongPressGesture` 简写，零样板。
- 需要过程值（拖拽中跟手、捏合中缩放）→ 定义 Gesture + `@GestureState`。
- 自定义视图上手势不灵 → 先加 `.contentShape(Rectangle())` 扩大可点区域（透明区域默认不响应）。

## 5. 组合：顺序 / 同时 / 排他

```swift
// 长按解锁后才进入拖拽（SequenceGesture）
let longPressThenDrag = SequenceGesture(LongPressGesture(minimumDuration: 0.3), DragGesture())
    .onEnded { value in
        if case .second(let drag) = value {
            _ = drag.translation      // .second 分支携带 DragGesture.Value
        }
    }

// 捏合 + 旋转同时进行（simultaneously(with:)）
let pinch = MagnifyGesture().updating($scale) { v, s, _ in s = v.magnification }
let rotate = RotateGesture().updating($angle) { v, s, _ in s = v.rotation }
image
    .scaleEffect(scale)
    .rotationEffect(angle)
    .gesture(pinch.simultaneously(with: rotate))
```

排他组合用 `a.exclusively(before: b)`：a 优先识别，失败才交给 b。

## ⚠️ 常见陷阱

- ❌ **把最终值存进 @GestureState**：手势一结束自动复位，结果"跳回去"
  ✅ 过程值 `@GestureState`、最终值 `@State` + `onEnded` 提交（§2 套路）。
- ❌ **拖拽用 `translation` 直接当 offset**：松手后归零回弹，再次拖拽从头算
  ✅ `offset(累计位置 + 当前 translation)`，`onEnded` 累加进位置。
- ❌ **透明区域点了没反应**：Shape/透明图默认只响应不透明像素
  ✅ `.contentShape(Rectangle())` 声明命中区域。
- ❌ **List/ScrollView 内硬塞 DragGesture**：与系统滚动手势抢事件，时灵时不灵
  ✅ 列表行内交互用 Button/swipeActions；确需并存用 `.highPriorityGesture` 或 `.simultaneousGesture` 明确语义。
- ❌ **继续用 `MagnificationGesture`/`RotationGesture`**：iOS 17 起已弃用，编译告警
  ✅ 改 `MagnifyGesture`/`RotateGesture`（iOS 16 及以下才需旧名）。

## 🔗 相关条目

- 📄 **[01-swiftui-essentials.md](./01-swiftui-essentials.md)** - 视图/修饰符/动画总表（手势的挂载目标）
- 📄 **[04-swiftui-state-api.md](../language-concepts/04-swiftui-state-api.md)** - @GestureState 所在的状态包装器全表
- 🌐 **[官方文档：Gestures](https://developer.apple.com/documentation/swiftui/gestures)** - Apple 开发者文档手势总览

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
