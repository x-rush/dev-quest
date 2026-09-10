# Compose 核心组件速查

> Jetpack Compose（Material 3）高频组件与 Modifier 的一览式速查：Scaffold 骨架、常用组件参数、Modifier 链全表

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#Compose` `#Material3` `#组件` `#Modifier` `#Scaffold` |
| **更新日期** | `2026年9月` |

---

## 1. Scaffold - 页面骨架

### 定义
标准页面容器，统一编排顶栏/底栏/FAB/内容区，并自动计算各区域避让边距。

### 语法和示例
```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun Page() {
    Scaffold(
        topBar = { TopAppBar(title = { Text("标题") }) },
        bottomBar = { NavigationBar { /* ... */ } },
        floatingActionButton = { FloatingActionButton(onClick = {}) { Icon(Icons.Default.Add, null) } },
        snackbarHost = { SnackbarHost(remember { SnackbarHostState() }) }
    ) { innerPadding ->
        Column(Modifier.padding(innerPadding)) {     // ⭐ 内容必须消费 innerPadding
            /* 页面内容 */
        }
    }
}
```

### 陷阱
忘记用 `innerPadding` 内容会被系统栏/底栏遮挡；`TopAppBar` 属于 experimental API，需 `@OptIn(ExperimentalMaterial3Api::class)`。

## 2. 文本与输入

```kotlin
Text(
    text = "标题",
    style = MaterialTheme.typography.headlineSmall,   // 用主题排版，勿硬编码字号
    fontWeight = FontWeight.Bold,
    maxLines = 1,
    overflow = TextOverflow.Ellipsis
)

OutlinedTextField(                                     // 带描边输入框
    value = query,
    onValueChange = { query = it },
    label = { Text("搜索") },
    placeholder = { Text("输入关键词") },
    leadingIcon = { Icon(Icons.Default.Search, null) },
    singleLine = true,
    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
    keyboardActions = KeyboardActions(onSearch = { doSearch() }),
    modifier = Modifier.fillMaxWidth()
)
```

| 组件 | 场景 |
|------|------|
| `Text` | 文本展示 |
| `OutlinedTextField` | 表单输入（带描边） |
| `TextField` | 填充式输入 |

## 3. 按钮家族

```kotlin
Button(onClick = {}) { Text("主要") }                 // 实心主按钮
OutlinedButton(onClick = {}) { Text("次要") }          // 描边
TextButton(onClick = {}) { Text("文字") }              // 低强调
ElevatedButton(onClick = {}) { Text("悬浮") }
IconButton(onClick = {}) { Icon(Icons.Default.Delete, contentDescription = "删除") }
FloatingActionButton(onClick = {}) { Icon(Icons.Default.Add, null) }
ExtendedFloatingActionButton(text = { Text("新建") }, icon = { Icon(Icons.Default.Add, null) }, onClick = {})
```

### 陷阱
`enabled = false` 会自动置灰并禁用点击；`contentDescription` 为 null 仅限纯装饰图标，可交互图标必须写。

## 4. 选择控件

```kotlin
Row(verticalAlignment = Alignment.CenterVertically) {
    Checkbox(checked = done, onCheckedChange = { done = it })
    Text("已完成")
}
Switch(checked = dark, onCheckedChange = { dark = it })
RadioButton(selected = gender == "M", onClick = { gender = "M" })
Slider(value = progress, onValueChange = { progress = it }, valueRange = 0f..100f)
```

## 5. 容器与卡片

```kotlin
Card(
    onClick = { /* 可点击卡片 */ },
    shape = RoundedCornerShape(12.dp),
    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
) {
    Column(Modifier.padding(16.dp)) { /* 内容 */ }
}

Surface(                       // 万能容器：控制颜色/形状/阴影
    color = MaterialTheme.colorScheme.surfaceVariant,
    shape = MaterialTheme.shapes.medium
) { /* ... */ }
```

## 6. 列表

```kotlin
LazyColumn(
    contentPadding = PaddingValues(16.dp),
    verticalArrangement = Arrangement.spacedBy(8.dp),
    state = rememberLazyListState()
) {
    item { Header() }                                    // 头部
    items(data, key = { it.id }) { item -> Row(item) }   // ⭐ 必给 key
    item { Footer() }
}

LazyRow { items(images, key = { it.url }) { Image(it) } }
LazyVerticalGrid(columns = GridCells.Fixed(3)) { items(photos, key = { it.id }) { Photo(it) } }
```

## 7. 对话框与提示

```kotlin
AlertDialog(
    onDismissRequest = { showDialog = false },          // 点外部/返回键关闭
    title = { Text("确认删除") },
    text = { Text("删除后不可恢复") },
    confirmButton = { TextButton(onClick = onDelete) { Text("删除") } },
    dismissButton = { TextButton(onClick = { showDialog = false }) { Text("取消") } }
)

// 轻量提示：Scaffold.snackbarHost + scope.launch { snackbarHostState.showSnackbar("已保存") }
```

## 8. 顶栏与底栏

```kotlin
TopAppBar(
    title = { Text("列表") },
    navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Filled.ArrowBack, "返回") } },
    actions = { IconButton(onClick = onSearch) { Icon(Icons.Default.Search, "搜索") } }
)
CenterAlignedTopAppBar(title = { Text("居中标题") })     // 大标题风格

NavigationBar {
    NavigationBarItem(selected = current == "home", onClick = { nav("home") },
        icon = { Icon(Icons.Default.Home, null) }, label = { Text("首页") })
}
```

## 9. Modifier 全表（顺序 = 从外到内）

| 类别 | 常用 API | 说明 |
|------|----------|------|
| 尺寸 | `size(48.dp)` `fillMaxSize()` `fillMaxWidth(fraction)` `widthIn(min,max)` `height(56.dp)` `aspectRatio(1f)` | 约束尺寸 |
| 布局 | `padding(16.dp)` `weight(1f)` ⭐ `offset(x,y)` | weight 仅限 Row/Column 直接子级 |
| 背景 | `background(color, shape)` | 在 padding 前则含边距 |
| 边框 | `border(1.dp, color, shape)` | |
| 形状 | `clip(RoundedCornerShape(12.dp))` `clip(CircleShape)` | 影响背景/内容裁剪 |
| 点击 | `clickable { }` `combinedClickable(onClick, onLongClick)` | 自带水波纹 |
| 滚动 | `verticalScroll(rememberScrollState())` `horizontalScroll(...)` | 非 Lazy 短列表 |
| 透明 | `alpha(0.5f)` | |
| 绘制 | `graphicsLayer { scaleX = 1.2f }` | 动画性能友好（不触发测量） |
| 语义 | `semantics { contentDescription = "x" }` | 无障碍 |

### 顺序示例（结果不同！）

```kotlin
Modifier.clickable { }.padding(16.dp)    // 水波纹铺满含 padding 的整个区域
Modifier.padding(16.dp).clickable { }    // 水波纹只在文字区域
```

---

## 组件选型速查

| 需求 | 用 |
|------|-----|
| 页面骨架 | `Scaffold` |
| 短列表（<20 固定项） | `Column` |
| 长列表/动态项 | `LazyColumn` + key |
| 可点击卡片 | `Card(onClick)` |
| 确认类弹窗 | `AlertDialog` |
| 轻量反馈 | `Snackbar` |
| 顶部标题栏 | `TopAppBar` / `CenterAlignedTopAppBar` |
| 底部标签 | `NavigationBar` |

---

## 相关文档

- 📄 **[Material 3 主题系统](./02-compose-material3.md)** - colorScheme/typography/shapes 深入
- 📄 **[布局系统](../../basics/05-layouts.md)** - Column/Row/Box/LazyColumn 教程
- 📄 **[Compose 状态 API 详解](../language-concepts/04-compose-state-api.md)** - 组件状态来源
- 📖 **[Compose Material 3 API 参考](https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary)** - 全量组件文档
