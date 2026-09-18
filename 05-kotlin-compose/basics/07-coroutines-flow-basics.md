# 协程与 Flow 基础 - 在 ViewModel 中驱动异步数据

## 先理解，再动手

协程是一段可以挂起的工作，Flow 描述多次产生的值。谁创建作用域，谁就承担取消与生命周期责任。

**本节自测**：让 ViewModel 暴露加载与成功状态，页面退出时观察界面收集。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

区分停止 UI 收集与取消上游工作；不要假定所有 Flow 都会在无观察者时自动停止。

</details>

> **文档简介**: 学会用协程（Coroutines）写顺序风格的异步代码，用 Flow/StateFlow 把数据流接入 Compose 界面，完成"ViewModel 持有 UI 状态"的标准架构闭环
>
> **目标读者**: 已掌握 Compose 状态与导航、准备接入真实数据源（数据库/网络）的开发者
>
> **前置知识**: [Composable 与状态](./04-composables-state.md)；对异步编程（Promise/async-await 或 goroutine）有基本概念

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#协程` `#Flow` `#StateFlow` `#ViewModel` `#structured-concurrency` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 用 `suspend` 函数与 `viewModelScope` 写异步任务
- ✅ 区分 `launch` 与 `async/await`，理解结构化并发的自动取消
- ✅ 按需选择 `Dispatchers` 并用 `withContext` 切换线程
- ✅ 用 Flow 描述异步数据流，用 `stateIn` 转成 StateFlow
- ✅ 在 Compose 中用 `collectAsStateWithLifecycle` 安全收集

## 📋 目录

- [为什么需要协程](#-为什么需要协程)
- [协程基础：launch、async 与 suspend](#-协程基础launchasync-与-suspend)
- [调度器与线程切换](#-调度器与线程切换)
- [结构化并发与 viewModelScope](#-结构化并发与-viewmodelscope)
- [Flow：异步数据流](#-flow异步数据流)
- [StateFlow 与 UI 状态](#-stateflow-与-ui-状态)
- [在 Compose 中收集](#️-在-compose-中收集)
- [练习与实践](#-练习与实践)

---

## 🤔 为什么需要协程

Android 的规则：**主线程不能做耗时操作**（否则掉帧甚至 ANR），而 UI 更新又必须在主线程。协程用"看起来同步"的代码解决"实际异步"的问题：

```kotlin
// 回调地狱（老写法）
api.getUser { user ->
    api.getOrders(user.id) { orders ->
        runOnUiThread { render(orders) }
    }
}

// 协程（新写法）：顺序表达，挂起不阻塞线程
suspend fun loadOrders() {
    val user = api.getUser()          // 挂起点：等待期间释放线程
    val orders = api.getOrders(user.id)
    render(orders)                    // 自动回到调用方上下文
}
```

> 💡 与 Go 类比：协程像 goroutine 一样轻量（可同时开十万级），但多了**结构化取消**与**挂起函数**两个关键概念；与 JS 类比：`suspend fun` ≈ `async` 函数，调用处无 await 关键字，挂起是隐式的。

---

## 🚀 协程基础：launch、async 与 suspend

```kotlin
suspend fun fetchTitle(): String {          // suspend 标记：可被"挂起"的函数
    delay(1000)                             // delay 模拟耗时（非阻塞睡眠）
    return "Dev Quest"
}

// launch：启动一个"发射后不管"的协程，返回 Job
val job = scope.launch {
    val title = fetchTitle()
    println(title)
}

// async：需要结果时使用，返回 Deferred<T>，用 await 取值
scope.launch {
    val a = async { fetchTitle() }          // 两个请求并发执行
    val b = async { fetchSubtitle() }
    render(a.await() + b.await())           // 都完成后再继续
}
```

规则速记：

- `suspend` 函数**只能**被另一个 suspend 函数或协程调用
- `launch` 用于"做件事就行"，`async` 用于"要个结果"
- 异常处理：协程体内直接 `try/catch`；`async` 的异常在 `await()` 时抛出

---

## 🧵 调度器与线程切换

`Dispatchers` 决定协程跑在哪些线程上：

| 调度器 | 用途 | 类比 |
|--------|------|------|
| `Dispatchers.Main` | Android 主线程，只能在这里碰 UI | iOS main queue |
| `Dispatchers.IO` | 磁盘/网络等阻塞 IO，线程池可扩容 | 随便开线程读文件 |
| `Dispatchers.Default` | CPU 密集：排序、解析、JSON | 线程数 ≈ CPU 核数 |
| `Dispatchers.Unconfined` | 不固定（少用） | — |

```kotlin
suspend fun loadUser(): User = withContext(Dispatchers.IO) {   // 切到 IO 执行
    userDao.getById(id)          // 返回时自动切回原调度器
}
```

经验法则：Room/Retrofit 的 `suspend` 函数已自行处理线程，**不要**再包一层 `withContext(IO)`；自己用 `File`/`Socket` 时才需要手动切。

---

## 🌳 结构化并发与 viewModelScope

协程存在于**作用域（Scope）**中，作用域取消 → 其内所有协程自动取消，不会有"孤儿任务"：

```kotlin
class TaskViewModel(private val repo: TaskRepository) : ViewModel() {

    fun refresh() {
        viewModelScope.launch {              // ViewModel 销毁时自动取消，绝不泄漏
            _uiState.value = UiState.Loading
            try {
                val tasks = repo.getTasks()  // 页面退出后这行永远不会执行
                _uiState.value = UiState.Success(tasks)
            } catch (e: CancellationException) {
                throw e                      // ⭐ 取消异常必须重新抛出
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "未知错误")
            }
        }
    }
}
```

常用作用域：

- `viewModelScope` —— ViewModel 内，页面销毁自动取消（本课主力）
- `lifecycleScope` —— Activity/Fragment 内，随生命周期取消
- ⚠️ `GlobalScope` —— 生命周期与应用相同，**禁止**在业务代码中使用（协程泄漏的头号来源）

---

## 🌊 Flow：异步数据流

Flow 是**冷流**：构建时什么都不发生，每次 `collect` 才从头执行一次（类似 Java Stream 的惰性 + JS Observable）：

```kotlin
fun countdown(): Flow<Int> = flow {
    for (i in 5 downTo 1) {
        emit(i)              // 发射一个值
        delay(1000)
    }
}

// 操作符链：与集合 API 语义一致，但逐值异步处理
scope.launch {
    countdown()
        .map { "倒计时 $it" }
        .filter { !it.contains("4") }
        .collect { value -> println(value) }   // 终端操作：开始执行
}
```

数据源返回 Flow 的典型场景——**Room 查询天然返回 Flow**，表一变就重新发射：

```kotlin
@Dao
interface TaskDao {
    @Query("SELECT * FROM tasks ORDER BY createdAt DESC")
    fun observeAll(): Flow<List<Task>>        // 可观察查询
}
```

> 📖 CoroutineScope/Job/Dispatcher/操作符的完整 API 表见 [协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md)。

---

## 🎯 StateFlow 与 UI 状态

`StateFlow` 是"有当前值的 hot flow"，天然适合持有 UI 状态：新订阅者立刻拿到最新值。

```kotlin
class TaskViewModel(repo: TaskRepository) : ViewModel() {

    private val _query = MutableStateFlow("")            // 私有可写
    val query: StateFlow<String> = _query.asStateFlow()  // 对外只读

    // 把冷流转成"ViewModel 存活期"的热流：配置变更不重跑查询
    val tasks: StateFlow<List<Task>> = repo.observeTasks(_query)
        .map { tasks -> tasks.filter { it.title.contains(_query.value) } }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000), // 5 秒无订阅者才停止上游
            initialValue = emptyList()
        )
}
```

要点：

- 命名惯例：私有 `_xxx`（Mutable），公开 `xxx`（StateFlow 只读视图）——防止 UI 意外改状态
- `WhileSubscribed(5_000)`：屏幕旋转重订阅的间隙不断流，用户彻底离开才停——官方推荐值

---

## 🖥️ 在 Compose 中收集

```kotlin
@Composable
fun TaskListScreen(viewModel: TaskViewModel) {
    // 生命周期感知收集：界面 STOP 后自动停止收集，START 后恢复
    val tasks by viewModel.tasks.collectAsStateWithLifecycle()
    val query by viewModel.query.collectAsStateWithLifecycle()

    TaskListContent(
        tasks = tasks,
        query = query,
        onQueryChange = viewModel::onQueryChange      // 事件上抛给 ViewModel
    )
}
```

- **`collectAsStateWithLifecycle`**（`lifecycle-runtime-compose` 库）：比 `collectAsState` 更省电，后台不白收集
- 至此闭环完成：**DB → Flow → StateFlow → collectAsState → 重组**，任何一层变化界面自动更新，这就是现代 Android 的单向数据流架构

> ⚠️ 不要在 Composable 函数体里直接 `flow.collect { }`——那会在组合期间挂起。副作用收集一律放 `LaunchedEffect` 或用上述 API。

---

## 🎯 练习与实践

### 基础练习
- [ ] 写一个 `suspend fun` 用 `delay` 模拟下载，在 `viewModelScope.launch` 中调用并更新 `MutableStateFlow<UiState>`
- [ ] 用 `async` 并发"下载"两张图片的耗时（各 1 秒），验证总耗时接近 1 秒而非 2 秒
- [ ] 把 `GlobalScope.launch` 版本的计数器改写成 `viewModelScope` 版本，旋转屏幕观察状态保留
- [ ] 写一个每秒发射一次的 Flow，用 `.take(5)` 只收集五次

### 进阶挑战
- [ ] 实现"搜索防抖"：搜索词 Flow 经 `.debounce(300)` + `.flatMapLatest { repo.search(it) }` 再 `stateIn`
- [ ] 把本课的 TaskViewModel 与 Room 连接（可先看下一课的 Room 部分），验证"改表即刷 UI"
- [ ] 故意在 `catch` 中吞掉 `CancellationException`，观察页面退出后协程仍在跑的泄漏现象并修复

---

## 🔗 相关文档

- 📄 **[协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md)** - Scope/Dispatcher/操作符字典
- 📄 **[第一个项目：笔记应用](./08-first-project.md)** - 把本课架构落到完整项目
- 📄 **[Compose 状态 API 详解](../reference/language-concepts/04-compose-state-api.md)** - collectAsState 与 Compose 状态的关系
- 📖 **[Kotlin Coroutines 官方指南](https://kotlinlang.org/docs/coroutines-guide.html)** - 协程语言级文档


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
