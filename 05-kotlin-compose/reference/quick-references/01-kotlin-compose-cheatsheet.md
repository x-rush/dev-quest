# Kotlin + Compose 一行式速查表

> 最高频语法的单行片段合集：声明 → 集合 → 协程 → Flow → Compose 状态 → 布局 → 导航，查一行就能用

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#速查表` `#cheatsheet` `#Kotlin` `#Compose` |
| **更新日期** | `2026年9月` |

---

## 1. Kotlin 基础

```kotlin
val name = "Compose"                          // 只读 + 类型推断
var count = 0                                 // 可变
fun add(a: Int, b: Int = 1): Int = a + b      // 默认参数 + 单表达式
val label = if (ok) "是" else "否"             // if 是表达式
val grade = when { score >= 90 -> "A"; else -> "B" }   // when 表达式
val msg = nickname ?: "匿名"                   // Elvis 默认值
val len = user?.name?.length ?: 0             // 安全调用链
data class User(val id: Long, val name: String)         // 数据类
val u2 = u1.copy(name = "Bob")                // 不可变更新
val (id, name) = u1                           // 解构
fun String.shout() = uppercase() + "!"        // 扩展函数
sealed interface State { data object Loading : State; data class Data(val v: Int) : State }
listOf(1, 2, 3).map { it * 2 }.filter { it > 2 }        // 集合链
val tag by lazy { expensive() }               // 惰性单例
```

## 2. 协程

```kotlin
viewModelScope.launch { doWork() }                       // 启动协程
val d = async { compute() }; val r = d.await()           // 并发取结果
val out = withContext(Dispatchers.IO) { read() }         // 切线程执行
delay(1_000)                                             // 非阻塞等待
scope.cancel()                                           // 取消整棵协程树
ensureActive()                                           // 循环中检查取消
runCatching { task() }.onFailure { log(it) }             // 结果化错误处理
```

## 3. Flow / StateFlow

```kotlin
val flow = flow { for (i in 1..3) emit(i) }              // 冷流构建
flow.map { it * 2 }.filter { it > 2 }.collect { p(it) }  // 变换 + 收集
flow.debounce(300).distinctUntilChanged()                // 搜索框双件套
flow.flatMapLatest { repo.search(it) }                   // 取消旧请求
flow.flowOn(Dispatchers.IO)                              // 上游切线程
flow.catch { emit(emptyList()) }                         // 上游异常降级
combine(flowA, flowB) { a, b -> a to b }                 // 多流合流
val ui: StateFlow<List<T>> = flow.stateIn(vmScope, WhileSubscribed(5_000), emptyList())
private val _x = MutableStateFlow(0); val x = _x.asStateFlow()   // 可写私有/只读公开
_x.value = 1                                             // 更新状态
```

## 4. Compose 状态

```kotlin
var text by remember { mutableStateOf("") }               // 简单状态
var count by remember { mutableIntStateOf(0) }            // Int 免装箱
var draft by rememberSaveable { mutableStateOf("") }      // 扛旋转/进程恢复
val show by remember { derivedStateOf { index > 0 } }     // 高频源→低频结果
val state by vm.uiState.collectAsStateWithLifecycle()     // 收集 ViewModel 状态
val scope = rememberCoroutineScope()                      // 事件回调中起协程
LaunchedEffect(userId) { vm.load(userId) }                // key 变化重新执行
DisposableEffect(Unit) { onDispose { cleanup() } }        // 清理副作用
snapshotFlow { query.text }.debounce(300)                 // 状态转 Flow
key(userId) { Profile(userId) }                           // 强制重置内部状态
```

## 5. 布局与 Modifier

```kotlin
Column(verticalArrangement = Arrangement.spacedBy(8.dp), horizontalAlignment = Alignment.CenterHorizontally) { }
Row(verticalAlignment = Alignment.CenterVertically) { }
Box(contentAlignment = Alignment.Center) { }
Modifier.fillMaxSize().padding(16.dp)                     // 尺寸 + 内边距
Modifier.weight(1f)                                       // 占据剩余空间（Row/Column 子级）
Modifier.background(color, RoundedCornerShape(12.dp))     // 背景圆角
Modifier.clip(CircleShape).border(1.dp, color, CircleShape)
Modifier.clickable { action() }                           // 点击（带水波纹）
Modifier.verticalScroll(rememberScrollState())            // 短列表滚动
Spacer(Modifier.height(8.dp))                             // 固定间距
```

## 6. 列表（Lazy）

```kotlin
LazyColumn(contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
    item { Header() }
    items(list, key = { it.id }) { item -> Row(item) }     // ⭐ 稳定 key
}
LazyRow { items(chips, key = { it.id }) { Chip(it) } }
LazyVerticalGrid(columns = GridCells.Fixed(3)) { items(photos, key = { it.id }) { Photo(it) } }
```

## 7. Material 3 常用组件

```kotlin
Scaffold(topBar = { TopAppBar(title = { Text("标题") }) }, floatingActionButton = { Fab() }) { pad -> Content(pad) }
Button(onClick = {}) { Text("主操作") }
OutlinedTextField(value = q, onValueChange = { q = it }, label = { Text("搜索") }, singleLine = true)
Card(onClick = {}) { Column(Modifier.padding(16.dp)) { Text("卡片") } }
AlertDialog(onDismissRequest = { close() }, confirmButton = { TextButton(onClick = {}) { Text("确定") } }, text = { Text("内容") })
Checkbox(checked = done, onCheckedChange = { done = it })
Switch(checked = dark, onCheckedChange = { dark = it })
Text("标题", style = MaterialTheme.typography.titleLarge)   // 用主题排版
val c = MaterialTheme.colorScheme.primary                   // 用主题颜色
```

## 8. 导航

```kotlin
val nav = rememberNavController()
NavHost(nav, startDestination = "list") { composable("list") { ListScreen() }; composable("detail/{id}") { e -> Detail(e.arguments?.getString("id")) } }
nav.navigate("detail/42")                                 // 前进
nav.popBackStack()                                        // 返回
nav.navigate("home") { popUpTo("auth") { inclusive = true }; launchSingleTop = true }   // 登出式清栈
val current by nav.currentBackStackEntryAsState()          // 驱动底部导航选中态
```

## 9. 常见模式

```kotlin
// 状态提升：组件只收值 + 回调
@Composable fun Input(value: String, onChange: (String) -> Unit, modifier: Modifier = Modifier) { }

// UiState 三态建模
sealed interface UiState<T> { data object Loading : UiState<Nothing>; data class Ok<T>(val data: List<T>) : UiState<T>; data class Err<T>(val msg: String) : UiState<T> }

// 一次性事件（防旋转重放）
private val _events = MutableSharedFlow<Event>(extraBufferCapacity = 1)

// 空态/加载态渲染
when (val s = uiState) { UiState.Loading -> Loader(); is UiState.Ok -> List(s.data); is UiState.Err -> Error(s.msg) }
```

---

## 相关文档

- 📄 **[故障排除速查](./02-troubleshooting.md)** - 症状导向的问题排查
- 📄 **[Compose 核心组件速查](../framework-essentials/01-compose-essentials.md)** - 组件参数展开版
- 📄 **[协程与 Flow API 全表](../language-concepts/03-coroutines-flow-api.md)** - Flow 操作符展开版
- 📖 **[Kotlin Playground](https://play.kotlinlang.org)** - 在线验证 Kotlin 片段
