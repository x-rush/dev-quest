# Canvas 自定义绘制

> DrawScope 绘图原语、Path 构建、graphicsLayer 变换/裁剪/合成策略、状态驱动的"重绘"模式——View 时代 invalidate() 的 Compose 替代思维

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#Canvas` `#DrawScope` `#Path` `#graphicsLayer` |
| **更新日期** | `2026年9月` |

> 本文属 Compose 框架层：API 签名按官方文档核对书写，**未实测（无 Android 环境）**，不编造参数名；纯 Kotlin 断言见语言概念篇。

---

## 📌 定义

Compose 中没有独立的 Canvas 控件——绘制通过**绘制修饰符**挂在任意组件上，或用 `Canvas(modifier) { }` 这个"空壳 Composable"（等价于 `Spacer` + `drawBehind`）。绘制块的接收者是 `DrawScope`，提供 drawRect/drawPath/drawCircle 等原语与 size 等上下文。

**重绘模型**：没有 `invalidate()`。绘制块里**读取的 Compose 状态**变化时，只有**绘制阶段**失效重跑（不重组、不重测量布局）——状态即重绘开关。

## 📖 语法与签名

### 1. 绘制入口三件套

| API | 签名要点 | 语义 |
|-----|---------|------|
| `Canvas(modifier, onDraw: DrawScope.() -> Unit)` | Composable 函数 | 纯绘制区域（= Spacer + drawBehind） |
| `Modifier.drawBehind(onDraw)` | 在**内容之后**绘制（视觉上垫底） | 背景装饰 |
| `Modifier.drawWithContent(onDraw)` | 块内**手动调 `drawContent()`** 决定内容前/后 | 给内容叠加特效（遮罩、渐变） |
| `Modifier.drawWithCache { onDrawBehind / onDrawWithContent }` | 块体在**尺寸不变时只执行一次**，可缓存 `Path`/`Brush` 等对象 | 避免每帧分配（⭐性能首选） |

### 2. DrawScope 原语

| 原语 | 签名要点 |
|------|---------|
| `drawRect(color, topLeft, size, style)` | 矩形；`style = Fill`（默认）或 `Stroke(width, cap, join, pathEffect)` |
| `drawRoundRect(color, cornerRadius, ...)` | 圆角矩形 |
| `drawCircle(color, radius, center)` | 圆；radius/center 缺省为内切圆心 |
| `drawOval / drawLine / drawPoints` | 椭圆 / 线段 / 点集 |
| `drawArc(color, startAngle, sweepAngle, useCenter, topLeft, size, style)` | 弧；`useCenter = true` 扇形 |
| `drawPath(path, color, style)` | 任意路径 |
| `drawImage(image, srcOffset, dstSize, ...)` | 位图 |
| `drawText(textMeasurer, text, topLeft, style)` | 文字（需 `rememberTextMeasurer()`，来自 ui-text 的 DrawScope 扩展） |
| `drawIntoCanvas { canvas -> ... }` | 拿到底层 `Canvas`（`canvas.nativeCanvas` 桥接 Android View/Drawable 绘制） |
| `inset(l, t) / rotate(degrees) / scale / translate { }` | 绘制级变换作用域（只影响块内，不碰布局） |

### 3. Path 构建

```kotlin
val path = Path().apply {
    moveTo(0f, 0f)                       // 起笔
    lineTo(size.width / 2f, size.height) // 直线
    quadraticTo(x1, y1, x2, y2)          // 二次贝塞尔（旧 quadraticBezierTo 已废弃）
    cubicTo(x1, y1, x2, y2, x3, y3)      // 三次贝塞尔
    arcTo(rect, startAngle, sweepAngle, forceMoveTo)
    close()                              // 闭合
}
```

### 4. graphicsLayer（变换 / 裁剪 / 合成）

```kotlin
Modifier.graphicsLayer {
    scaleX = 1.2f; scaleY = 1.2f         // 缩放
    translationX = 0f; translationY = 0f // 平移
    rotationZ = 45f                       // 平面旋转（rotationX/Y 3D）
    alpha = 0.5f
    shape = CircleShape; clip = true      // 按形状裁剪（= Modifier.clip 的底层）
    transformOrigin = TransformOrigin.Center
    compositingStrategy = CompositingStrategy.Offscreen
}
```

- 块内读状态 → 状态变化**只重执行该层绘制**，跳过重组与布局（动画位移/缩放的标准姿势）。
- `compositingStrategy`：`Auto`（默认）/ `Offscreen`（先画到离屏层再合成——配合 alpha 解决半透明叠加穿透）/ `ModulateAlpha`（低成本 alpha，仅内容自身透明度）。

## 💡 示例

```kotlin
// 1. 环形进度：状态驱动重绘（无 invalidate）
@Composable
fun ProgressRing(progress: Float) {
    Canvas(Modifier.size(120.dp)) {
        drawArc(
            color = Color.LightGray, startAngle = 0f, sweepAngle = 360f, useCenter = false,
            style = Stroke(width = 12f, cap = StrokeCap.Round),
        )
        drawArc(
            color = MaterialTheme.colorScheme.primary,
            startAngle = -90f,
            sweepAngle = 360f * progress,          // 读状态：progress 变 → 仅绘制阶段重跑
            useCenter = false,
            style = Stroke(width = 12f, cap = StrokeCap.Round),
        )
    }
}

// 2. drawWithCache 缓存 Path（尺寸不变则不重建）
Spacer(
    Modifier
        .fillMaxSize()
        .drawWithCache {
            val path = Path()
            path.moveTo(0f, 0f)
            path.lineTo(size.width / 2f, size.height / 2f)
            path.lineTo(size.width, 0f)
            path.close()
            onDrawBehind {
                drawPath(path, Color.Magenta, style = Stroke(width = 10f))
            }
        }
)

// 3. 圆形裁剪：graphicsLayer 与 Modifier.clip 等价
Box(
    Modifier
        .size(200.dp)
        .graphicsLayer { clip = true; shape = CircleShape }
        .background(Color(0xFFF06292))
)

// 4. 文字绘制
val textMeasurer = rememberTextMeasurer()
Canvas(Modifier.fillMaxSize()) {
    drawText(textMeasurer, "Hello")
}

// 5. 桥接原生：把 Android Drawable 画进 Compose
Spacer(
    Modifier
        .fillMaxSize()
        .drawWithContent {
            drawIntoCanvas { canvas ->
                drawable.setBounds(0, 0, size.width.toInt(), size.height.toInt())
                drawable.draw(canvas.nativeCanvas)
            }
        }
)
```

## ⚠️ 常见陷阱

- ❌ 在 `drawBehind`/`Canvas` 的绘制块里 `Path()`/`Brush` 每帧新建——绘制块执行频率高，分配压力大。
  ✅ 用 `drawWithCache` 块体缓存（尺寸变化才重建），或 `remember { Path() }` 后在块内 `reset()` 复用。
- ❌ 沿用 View 思维找 `invalidate()` / `postInvalidate()`——Compose 没有这个概念，也不会"忘了重绘"。
  ✅ 把可变量做成状态（`mutableFloatStateOf` 等）并在绘制块里读取；变化自动触发**仅绘制阶段**重跑。
- ❌ 用动画驱动 `Modifier.offset { }` 做图形位移动画——每帧改 offset 走布局阶段（测量+摆放）。
  ✅ `graphicsLayer { translationX = 动画值 }`——只走绘制，动画不掉帧。
- ❌ 以为 `drawText("hi")` 直接收字符串——文字绘制需要 `TextMeasurer` 参与测量排版。
  ✅ `val textMeasurer = rememberTextMeasurer()` 后 `drawText(textMeasurer, "hi")`。
- ❌ 半透明元素叠加出现"叠黑"/意外遮挡——默认 `CompositingStrategy.Auto` 不建离屏层，alpha 逐元素混入背景。
  ✅ 需要整体统一透明度时 `graphicsLayer { alpha = x; compositingStrategy = CompositingStrategy.Offscreen }`。
- ❌ 从旧教程抄 `quadraticBezierTo`——已废弃。
  ✅ 用 `quadraticTo`（官方 API reference 明确标注替换关系）。
- ❌ 在绘制块里读状态后又写状态——绘制阶段递归失效，死循环风险。
  ✅ 绘制块保持"读状态 → 画"的纯函数性；写状态放交互回调或副作用 API。

## 🔗 相关条目

- 📄 **[手势 API](./09-gestures.md)** - 拖拽/缩放手势驱动绘制
- 📄 **[Compose 核心组件速查](./01-compose-essentials.md)** - graphicsLayer 在 Modifier 全表中的位置
- 📄 **[动画核心](./05-animation-core.md)** - animate*AsState 驱动绘制状态
- 📄 **[@Composable 与组合模型](./08-composition-model.md)** - 为什么绘制阶段可以跳过重组
- 🌐 **[Draw modifiers（官方文档）](https://developer.android.com/develop/ui/compose/graphics/draw/modifiers)** - 绘制修饰符权威指南
- 🌐 **[DrawScope（API 参考）](https://developer.android.com/reference/kotlin/androidx/compose/ui/graphics/drawscope/DrawScope)** - 全原语签名

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
