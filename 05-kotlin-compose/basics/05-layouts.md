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

Compose 只提供三个原子容器，复杂界面全靠组合嵌套：

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
- **Alignment**: `Top`/`CenterVertically`/`Bottom`（Column 中）；`Start`/`CenterHorizontally`/`End`（Row 中）
- **Box** 例外：参数直接是 `contentAlignment = Alignment.Center`

---

## 🎨 Modifier 修饰符

Modifier 是每个 Composable 的可选参数，链式叠加控制外观与行为：

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

**记忆法**：先写的在外面。`clickable` 的水波纹范围由它之前的修饰符决定。

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

注意：带 `weight` 的子项在**第二遍测量**中才分配空间，因此 `weight(1f)` 的组件不会把兄弟组件挤出屏幕——这是实现"左列表右详情"类布局的关键。

---

## 📜 LazyColumn 长列表

`Column` 会一次性组合所有子项；数据量大时必须用 **LazyColumn**（对标 RecyclerView，按需组合 + 自动回收）：

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

- **`key` 必填意识**: 传入稳定唯一 key（通常是 id），删除/插入项时才能正确定位与播放动画；用默认位置 key 在数据变化时会出现错位
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

### 基础练习
- [ ] 用 `Column` + `Row` 实现一个"头像 + 两行文字"的联系人卡片
- [ ] 用 `Box` 实现一张带左上角角标（"NEW"）的卡片
- [ ] 写两个 Text 分别设置 `padding(16.dp).background(...)` 与 `background(...).padding(16.dp)`，截图对比差异
- [ ] 把上一课的计数器放入 `Column` 中，主轴用 `spacedBy(12.dp)` 排布

### 进阶挑战
- [ ] 实现"1 : 2 : 1"三栏等高的横向布局（提示：weight）
- [ ] 用 `LazyColumn` + `key` 渲染 100 条数据，添加"随机删除一条"按钮，观察列表动画是否平滑；再去掉 key 对比
- [ ] 实现一个吸顶效果：LazyColumn 的 `stickyHeader { }` 展示按首字母分组的联系人列表

---

## 🔗 相关文档

- 📄 **[Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md)** - Scaffold/组件参数字典
- 📄 **[Material 3 主题系统](../reference/framework-essentials/02-compose-material3.md)** - 让布局用上主题颜色与字体
- 📄 **[Navigation Compose](./06-navigation.md)** - 下一篇：多页面切换
- 📖 **[Layouts in Compose](https://developer.android.com/develop/ui/compose/layouts)** - 官方布局文档


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
