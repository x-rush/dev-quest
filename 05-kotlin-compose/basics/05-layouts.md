# 布局系统 - Column/Row/Box 与 LazyColumn

## 先理解，再动手

布局先接收父级约束，再测量孩子并放置。Modifier 的顺序会改变测量和点击范围，不能当成无顺序的样式字典。

**本节自测**：交换 padding 与 background 的顺序，观察背景覆盖范围。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

两种结果可能不同；通过可见边界解释内外间距，而不是背固定组合。

</details>

> **文档简介**: 掌握 Compose 三大基础布局容器、Modifier 修饰符链与列表利器 LazyColumn，能搭建典型页面结构
>
> **目标读者**: 已理解状态与重组、开始搭建真实页面的 Compose 初学者
>
> **前置知识**: [Composable 与状态](./04-composables-state.md)；了解 dp/参数默认值等基础语法

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#布局` `#Column` `#Row` `#Box` `#Modifier` `#LazyColumn` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 用 Column/Row/Box 组合出常见页面结构（对标 LinearLayout/FrameLayout）
- ✅ 理解 `Arrangement`（主轴）与 `Alignment`（交叉轴）的分工
- ✅ 掌握 Modifier 链式语法，理解**顺序影响布局**的原因
- ✅ 使用 `weight` 分配剩余空间
- ✅ 用 LazyColumn 渲染长列表并正确设置 key

## 📋 目录

- [三大基础布局](#-三大基础布局)
- [主轴与交叉轴](#️-主轴与交叉轴)
- [Modifier 修饰符](#-modifier-修饰符)
- [weight 权重分配](#️-weight-权重分配)
- [LazyColumn 长列表](#-lazycolumn-长列表)
- [布局选型速查](#️-布局选型速查)
- [练习与实践](#-练习与实践)

---

## 🧱 三大基础布局

本课先学习三个常用容器；Compose 还提供网格、自定义 Layout 等布局能力。以下是局部示意，`R.drawable.bg` 需要工程中的图片资源，不能直接复制成独立程序：

```kotlin
@Composable
fun BasicLayouts() {
    Column {                          // 垂直排列（对标 LinearLayout vertical）
        Text("标题")
        Row {                         // 水平排列（对标 LinearLayout horizontal）
            Text("左侧")
            Text("右侧")
        }
    }
}

@Composable
fun BoxDemo() {
    Box {                             // 层叠布局（对标 FrameLayout）
        Image(painter = painterResource(R.drawable.bg), contentDescription = null)
        Text("覆盖在图片上的文字")       // 后声明的在上层
    }
}
```

组合实例——一个典型的列表项：

```kotlin
@Composable
fun TaskRow(title: String, done: Boolean) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Checkbox(checked = done, onCheckedChange = null)
        Column(modifier = Modifier.weight(1f)) {   // 占据剩余宽度
            Text(title, fontWeight = FontWeight.Bold)
            Text(if (done) "已完成" else "进行中", style = MaterialTheme.typography.bodySmall)
        }
        IconButton(onClick = { /* 删除 */ }) {
            Icon(Icons.Default.Delete, contentDescription = "删除")
        }
    }
}
```

---

## ↔️ 主轴与交叉轴

每个容器都有两个方向：**主轴**（内容排列方向）与**交叉轴**（垂直于排列方向）。

```kotlin
Column(
    verticalArrangement = Arrangement.SpaceEvenly,      // 主轴：子项间的分配方式
    horizontalAlignment = Alignment.CenterHorizontally  // 交叉轴：子项的对齐方式
) { /* ... */ }
```

| 容器 | 主轴参数 `Arrangement` | 交叉轴参数 `Alignment` |
|------|------------------------|------------------------|
| `Column` | `verticalArrangement` | `horizontalAlignment` |
| `Row` | `horizontalArrangement` | `verticalAlignment` |

常用取值：

- **Arrangement**: `Start`/`End`/`Center`/`SpaceBetween`/`SpaceEvenly`/`spacedBy(8.dp)`（固定间距，最常用）
- **Alignment**: `Start`/`CenterHorizontally`/`End` 用于 Column 的水平对齐；`Top`/`CenterVertically`/`Bottom` 用于 Row 的垂直对齐
- **Box** 例外：参数直接是 `contentAlignment = Alignment.Center`

---

## 🎨 Modifier 修饰符

Modifier 是许多 UI Composable 接收的参数；自定义函数需显式声明并传给对应布局节点。下面是放在 Composable 内的局部片段：

```kotlin
Text(
    text = "Hello",
    modifier = Modifier
        .fillMaxWidth()          // 占满可用宽度
        .padding(16.dp)          // 内边距 16
        .background(Color.LightGray, RoundedCornerShape(8.dp))
        .clickable { /* 点击 */ } // 点击反馈（自带水波纹）
        .padding(8.dp)           // 再加一层内边距
)
```

### 顺序很重要！

Modifier 按声明顺序从外到内依次包裹，交换两个调用结果完全不同：

```kotlin
Modifier.background(Color.Red).padding(16.dp)   // 红色区域包含 padding（padding 在红底内）
Modifier.padding(16.dp).background(Color.Red)   // 先留白再铺红底（红底比父容器小一圈）
```

**记忆法**：先写的在外面。`clickable().padding(...)` 将这层间距包含在点击区域中；`padding(...).clickable()` 把这层间距放在点击区域外。反馈外观还受 indication、主题与裁剪影响，不能只看前面的修饰符推导水波纹。

> 📖 全部常用 Modifier（尺寸/裁剪/边框/偏移等）的一览表见 [Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md)。

---

## ⚖️ weight 权重分配

`weight` 只在 Row/Column 的**直接子级**中可用，把剩余空间按比例分配：

```kotlin
Row(modifier = Modifier.fillMaxWidth()) {
    Text("固定内容")                            // 先按内容测量
    Text(
        "弹性内容占据剩余空间",
        modifier = Modifier.weight(1f)          // 吃掉所有剩余宽度
    )
}

Row {
    Box(Modifier.weight(1f).height(40.dp))      // 1/3
    Box(Modifier.weight(2f).height(40.dp))      // 2/3
}
```

Row/Column 先测量无权重子项，再把主轴剩余空间按权重分给加权子项；这不是把同一个子项测量两遍。必须有可分配的有限主轴空间；在同方向滚动导致无界约束时，不应依赖 weight 分配“剩余空间”。固定内容过宽也不能由 weight 自动修好。

---

## 📜 LazyColumn 长列表

`Column` 不提供按视口惰性组合机制；长列表通常使用 **LazyColumn**，按显示需要组合和布局项目。下面是设计片段，依赖尚未定义的 `Task` 类型；后面的完整屏幕会提供数据模型：

```kotlin
@Composable
fun TaskList(tasks: List<Task>, onDelete: (Task) -> Unit) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),              // 列表整体内边距
        verticalArrangement = Arrangement.spacedBy(8.dp)    // 项间距
    ) {
        items(
            items = tasks,
            key = { it.id }                                  // ⭐ 稳定 key：复用与动画的前提
        ) { task ->
            TaskRow(title = task.title, done = task.done)
        }
    }
}
```

要点：

- **`key` 身份**: 默认按位置识别项目；稳定唯一 key 让项目重排后仍能关联自己的状态。在 Android 上，若项目使用 rememberSaveable，key 还应是 Bundle 支持的类型。key 本身不启用移动动画，动画需另配 `animateItem` 等 API
- **`items` 分段**: 可混用 `item { }`（头部）与 `items(list) { }`（主体）
- **横向版本**: `LazyRow` 参数一致；网格用 `LazyVerticalGrid(GridCells.Fixed(2))`

> ⚠️ LazyColumn 不能直接放在带 `verticalScroll` 的 Column 里（同方向无限高度冲突），需要用 `heightIn(max=...)` 约束或调整结构。

---

## 🗂️ 布局选型速查

| 需求 | 首选 | 备注 |
|------|------|------|
| 垂直/水平排列 | `Column` / `Row` | 子项少且固定 |
| 长列表 / 不确定数量 | `LazyColumn` / `LazyRow` | 记得设置 key |
| 层叠覆盖（角标、水印） | `Box` | 后声明者在上层 |
| 页面骨架（顶栏+内容+底栏） | `Scaffold` | 见组件速查文档 |
| 精确约束/裁剪/自绘 | `Layout` 自定义 | 进阶内容 |

---

## 🎯 练习与实践

### 先交付一个可观察的任务列表

前置是上一课已完成的 Empty Activity Compose 工程，已有 Material 3 与 Foundation 依赖。保留 `MainActivity.kt` 的 package 和 Activity，在同包新建 `LayoutLesson.kt`，放入下列完整屏幕代码；在原有 `setContent` 的主题内部调用 `LayoutLesson()`，替换原来的演示内容。不要把代码放到普通 JVM main 中。

```kotlin
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

private data class LayoutTask(val id: Int, val title: String)

@Composable
fun LayoutLesson() {
    var tasks by remember {
        mutableStateOf(List(100) { LayoutTask(it, "任务 ${it + 1}") })
    }
    Column(Modifier.fillMaxSize().safeDrawingPadding().padding(16.dp)) {
        Text("剩余 ${tasks.size} 项", style = MaterialTheme.typography.titleLarge)
        LazyColumn(
            modifier = Modifier.weight(1f).fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(8.dp),
            contentPadding = PaddingValues(vertical = 12.dp)
        ) {
            items(tasks, key = { it.id }) { task ->
                Row(
                    Modifier.fillMaxWidth().background(Color.LightGray).padding(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(task.title, Modifier.weight(1f))
                    TextButton(onClick = { tasks = tasks.filterNot { it.id == task.id } }) {
                        Text("删除")
                    }
                }
            }
        }
    }
}
```

输入是 100 个稳定 id 的任务，输出是顶部数量与可滚动列表。外层 Column 获得屏幕有限高度；标题占用自己的高度，列表的 weight 使用余下高度。每行文本使用剩余宽度，按钮按内容测量。点击第一项“删除”，预期数量从 100 变为 99，首行变成“任务 2”；这一步不承诺删除动画。重新创建 Activity 会重建演示数据，因为本课只用 remember，尚未持久化。

在 Android Studio 选择模拟器或真机并运行 app。若 `items` 报参数类型错误，检查是否导入 `androidx.compose.foundation.lazy.items`；若提示无限高度，检查是否另套了 verticalScroll；若标题被状态栏遮挡，检查是否保留 safeDrawingPadding，及外层 Scaffold 是否已处理同一 inset，避免重复留白。

本轮只完成官方资料核对与静态阅读，未运行 Android 构建、模拟器或截图验收。上面的结果是读者执行时的验收标准，不是本机实测记录。

反馈练习：把一条标题改成 60 个汉字，验收删除按钮仍可见、行高随换行增加；再交换 background 与 padding，验收灰底是否包含那 8.dp。若两个变化无法解释，分别回查本页 weight 与 Modifier 小节。

### 基础练习
- [ ] 用 `Column` + `Row` 实现一个"头像 + 两行文字"的联系人卡片
- [ ] 用 `Box` 实现一张带左上角角标（"NEW"）的卡片
- [ ] 写两个 Text 分别设置 `padding(16.dp).background(...)` 与 `background(...).padding(16.dp)`，截图对比差异
- [ ] 把上一课的计数器放入 `Column` 中，主轴用 `spacedBy(12.dp)` 排布

### 进阶挑战
- [ ] 实现"1 : 2 : 1"三栏等高的横向布局（提示：weight）
- [ ] 在完整屏幕的行内加入记忆状态后重排数据，比较稳定 key 与位置 key 对状态归属的影响；动画作为单独扩展练习
- [ ] 实现一个吸顶效果：LazyColumn 的 `stickyHeader { }` 展示按首字母分组的联系人列表

---

## 🔗 相关文档

- 📄 **[Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md)** - Scaffold/组件参数字典
- 📄 **[Material 3 主题系统](../reference/framework-essentials/02-compose-material3.md)** - 让布局用上主题颜色与字体
- 📄 **[Navigation Compose](./06-navigation.md)** - 下一篇：多页面切换
- 📖 **[Layouts in Compose](https://developer.android.com/develop/ui/compose/layouts)** - 官方布局文档

官方事实入口：[布局测量与基本容器](https://developer.android.com/develop/ui/compose/layouts/basics)、[Modifier 顺序与 weight](https://developer.android.com/develop/ui/compose/modifiers)、[惰性列表与项目 key](https://developer.android.com/develop/ui/compose/lists)。核对日期：2026-09-20。

完成删除与长标题验收后进入下一页导航：把任务 id 作为路由输入，在详情页展示所选任务。先保留这里的单一列表状态，避免在两个页面分别创建两份不同的任务集合。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
