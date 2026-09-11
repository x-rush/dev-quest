# Compose 状态 API 详解

> State/remember/rememberSaveable/derivedStateOf/snapshotFlow 等 Compose 状态 API 的字典式速查：定义 → 语法 → 示例 → 陷阱

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#State` `#remember` `#rememberSaveable` `#derivedStateOf` `#snapshotFlow` |
| **更新日期** | `2026年9月` |

---

## 1. State / MutableState

### 定义
`State<T>` 是 Compose 的可观察值容器；读取其 `.value` 会建立订阅，写入 `MutableState` 的 value 触发重组。

### 语法和示例
```kotlin
val state: State<Int> = remember { mutableStateOf(0) }       // 只读视图
val mState: MutableState<Int> = mutableStateOf(0)            // 可写
mState.value++

var text by remember { mutableStateOf("") }                  // by 委托读写 value
var count by remember { mutableIntStateOf(0) }               // 基本类型专用（免装箱）
```

### 陷阱
- 带初值的 `mutableStateOf(0)` 类型可正常推断；报错 "Not enough information to infer type variable T" 出现在**无初值**的 `mutableStateOf()` 上，此时显式写 `mutableStateOf<Int>()`，或基本类型直接用 `mutableIntStateOf(0)`（免装箱）
- 读 `value` 发生在哪个 Composable，重组范围就是那个 Composable——把读取下沉到最小子组件可缩小重组范围

## 2. remember

### 定义
在组合期间缓存计算结果，重组时返回同一实例；作用域是"该调用点在组合树中的存在期"。

### 语法和示例
```kotlin
val density = remember { Density(density = 2f) }
val filtered = remember(tasks) { tasks.filter { it.done } }   // 带 key：tasks 变化才重算
```

### 陷阱
- `remember` 的 lambda 每次重组**不会**重新执行——普通"每次都要新值"的变量直接用局部 `val` 即可，别滥用 remember
- 带参数缓存必须写 key：`remember(user) { compute(user) }`，否则拿到陈旧缓存

## 3. rememberSaveable

### 定义
`remember` 的持久化版本：值自动写入 `Bundle`，能扛住**配置变更（旋转）与进程被杀恢复**。

### 语法和示例
```kotlin
var query by rememberSaveable { mutableStateOf("") }          // 基本类型自动支持

// 自定义对象：用 listSaver/mapSaver 提供 saver
data class City(val name: String, val country: String)

val CitySaver = run {
    val nameKey = "name"; val countryKey = "country"
    listSaver<City, Any>(
        save = { listOf(it.name, it.country) },
        restore = { City(it[0] as String, it[1] as String) }
    )
}
var city by rememberSaveable(stateSaver = CitySaver) { mutableStateOf(City("", "")) }
```

### 陷阱
Bundle 有体积上限（约 1MB 级）——**不要**把大列表存进 rememberSaveable；大数据的跨配置变更存活应交给 ViewModel（内存）+ Room/DataStore（磁盘）。

## 4. derivedStateOf

### 定义
把一个或多个状态**计算**成派生状态；仅当**派生结果**变化时才通知订阅者，过滤中间态抖动。

### 语法和示例
```kotlin
val showButton by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 0 }   // 滚动位置频繁变化，
}                                                            // 但布尔结果只在跨界时变
AnimatedVisibility(visible = showButton) { ScrollToTop() }
```

### 陷阱
只用于"高频源 → 低频结果"场景；普通一次性计算用 `remember(key)` 更简单，给所有计算都套 derivedStateOf 反而增加开销。

## 5. snapshotFlow

### 定义
把 Compose 状态转换为冷 Flow：块内读取的状态变化时发射新值。用于让 Flow 操作符（debounce 等）处理 Compose 状态。

### 语法和示例
```kotlin
LaunchedEffect(textFieldState) {
    snapshotFlow { textFieldState.text }
        .debounce(300)
        .collectLatest { query -> repo.suggest(query) }       // 搜索防抖
}
```

### 陷阱
必须在协程中收集（通常 `LaunchedEffect`）；遗漏收集则永远不会执行。

## 6. collectAsState / collectAsStateWithLifecycle

### 定义
把 Flow/StateFlow 转为 Compose State；lifecycle 版本在界面进入后台时自动停止收集。

### 语法和示例
```kotlin
val uiState by viewModel.uiState.collectAsStateWithLifecycle()   // ⭐推荐
val uiState2 by viewModel.uiState.collectAsState()               // 不感知生命周期
```

### 陷阱
后台仍收集会浪费电量并可能覆盖新状态；两者差异只在 UI 不在屏幕时——测试中不可见。

## 7. 状态提升（State Hoisting）

### 定义
把状态上移到调用方、组件只收"值 + 回调"的模式，是 Compose 可复用组件的标准形态。

### 语法和示例
```kotlin
@Composable
fun Counter(
    count: Int,
    onIncrement: () -> Unit,
    modifier: Modifier = Modifier       // modifier 总是最后一个可选参数
) {
    Button(onClick = onIncrement, modifier = modifier) { Text("$count") }
}
```

### 陷阱
回调内不要偷改外部状态之外的东西（副作用分层混乱）；属性命名遵循 `value`/`onValueChange` 官方惯例。

## 8. key() 组合函数

### 定义
运行时工具：给一段组合逻辑加标识，身份变化时强制其内部状态重置。

### 语法和示例
```kotlin
key(userId) {
    UserProfile(userId)              // 切换 userId 时，内部 remember 状态全部重建
}
```

### 陷阱
与 LazyColumn `items(key = ...)` 是两回事：后者是列表项身份标识，前者是状态作用域重置。

## 9. CompositionLocal

### 定义
隐式向下传递值的机制（≈ React Context）：`CompositionLocalProvider` 提供值，子树用 `LocalX.current` 读取。

### 语法和示例
```kotlin
val LocalAppTheme = staticCompositionLocalOf<AppTheme> { error("未提供") }

CompositionLocalProvider(LocalAppTheme provides darkTheme) {
    Content()
}
// 子树任意深处
val theme = LocalAppTheme.current
```

### 陷阱
隐式依赖让数据流不可见——仅用于真正全局横切的量（主题、尺寸）；业务数据请走参数。

## 10. rememberCoroutineScope

### 定义
在组合中获取绑定当前组合点的协程作用域，离开组合自动取消；用于**事件回调**中启动协程。

### 语法和示例
```kotlin
val scope = rememberCoroutineScope()
Button(onClick = { scope.launch { listState.animateScrollToItem(0) } }) { Text("回到顶部") }
```

### 陷阱
不要在 Composable 函数体里直接 `scope.launch { }`（组合期间执行副作用）；动画/滚动类用 `animateScrollTo` 等挂起 API 时才需要它。

---

## 快速选型

| 需求 | 用什么 |
|------|--------|
| 简单 UI 状态 | `remember { mutableStateOf }` |
| 需扛旋转/进程恢复 | `rememberSaveable` |
| 承载业务状态 | ViewModel + `StateFlow` + `collectAsStateWithLifecycle` |
| 高频源派生低频结果 | `derivedStateOf` |
| 状态 → Flow 操作符 | `snapshotFlow` |
| 事件回调中起协程 | `rememberCoroutineScope` |

---

## 相关文档

- 📄 **[协程与 Flow API 全表](./03-coroutines-flow-api.md)** - Flow/StateFlow 层的完整字典
- 📄 **[副作用 API](../framework-essentials/03-side-effects.md)** - 在重组世界安全"做事"的 API 全表
- 📄 **[重组与稳定性](../framework-essentials/04-recomposition.md)** - 状态如何驱动重启与跳过
- 📄 **[泛型与委托属性](./05-generics-delegates.md)** - `by` 委托让 state.value 读写更简洁
- 📄 **[Composable 与状态](../../basics/04-composables-state.md)** - 状态与重组的入门教程
- 📖 **[Compose 状态官方文档](https://developer.android.com/develop/ui/compose/state)** - 权威参考
