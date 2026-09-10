# 协程与 Flow API 全表

> CoroutineScope/Job/Dispatcher/Flow 操作符/StateFlow/SharedFlow 的字典式全表速查：每个 API 一条，含定义、示例与陷阱

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#协程` `#Flow` `#StateFlow` `#SharedFlow` `#Dispatcher` |
| **更新日期** | `2026年9月` |

---

## 一、协程核心 API

### 1. CoroutineScope - 协程作用域

**定义**: 持有 CoroutineContext 的容器，取消作用域即取消其内全部协程（结构化并发的根基）。

| 作用域 | 来源 | 生命周期 | 用途 |
|--------|------|----------|------|
| `viewModelScope` | lifecycle-viewmodel-ktx | ViewModel 销毁 | UI 状态任务（首选） |
| `lifecycleScope` | lifecycle-runtime-ktx | Activity/Fragment 销毁 | 页面级任务 |
| `rememberCoroutineScope()` | Compose | 离开组合 | 在事件回调中启动协程 |
| `GlobalScope` | 全局 | 应用进程 ⚠️ | **禁止**用于业务 |

```kotlin
// Compose 事件回调中启动协程（如点击后滚动翻页）
val scope = rememberCoroutineScope()
Button(onClick = { scope.launch { pagerState.animateScrollToPage(1) } }) { Text("下一页") }
```

### 2. 协程构建器

| 构建器 | 返回 | 用途 | 异常传播 |
|--------|------|------|----------|
| `launch { }` | `Job` | 发射后不管 | 立即向上冒泡 |
| `async { }` | `Deferred<T>` | 需要结果 | `await()` 时抛出 |
| `withContext(ctx) { }` | `T` | 切换上下文并阻塞当前协程至完成 | 直接抛出 |
| `runBlocking { }` | `T` | **阻塞当前线程** | 直接抛出（仅 main/测试用） |

```kotlin
scope.launch {
    val user = async { repo.getUser(id) }      // 并发 A
    val posts = async { repo.getPosts(id) }    // 并发 B
    render(user.await(), posts.await())        // 汇合
}
```

**陷阱**: `async` 抛异常时若未 `await`，会静默失败（结构化取消仍会传播，但结果丢失）；`runBlocking` 出现在 Android 生产代码里几乎都是错误。

### 3. Dispatchers - 调度器

| 调度器 | 线程池 | 适用 |
|--------|--------|------|
| `Dispatchers.Main` | 主线程 | UI 更新；`Main.immediate` 免除不必要的切换 |
| `Dispatchers.IO` | 可扩容（64+） | 文件、Socket、阻塞 IO |
| `Dispatchers.Default` | CPU 核数 | 排序、JSON 解析、图像处理 |
| `Dispatchers.Unconfined` | 不固定 | 极少用 |

```kotlin
suspend fun parse(json: String): Result =
    withContext(Dispatchers.Default) { mapper.decode(json) }
```

### 4. Job 与结构化并发

**定义**: `Job` 是协程句柄；父子 Job 形成树，父取消则子全取消，子失败默认取消父。

```kotlin
val parent = scope.launch {
    launch { /* 子1 */ }
    launch { /* 子2 */ }
}
parent.cancel()                  // 整树取消
```

- `SupervisorJob()`/`supervisorScope`：子失败不连坐父（UI 事件流常用）
- 取消是**协作式**：CPU 循环中需主动 `ensureActive()` 或 `yield()`

**陷阱**: 捕获异常时必须重新抛出 `CancellationException`，否则破坏取消机制：

```kotlin
try { task() } catch (e: CancellationException) { throw e }
     catch (e: Exception) { showError(e) }
```

### 5. 异常处理

```kotlin
// Flow 侧：catch 捕获上游异常
flow { emitAll(api.feed()) }
    .catch { e -> emit(emptyList()) }        // 降级

// 协程侧：CoroutineExceptionHandler（仅根协程生效）
val handler = CoroutineExceptionHandler { _, e -> log(e) }
scope.launch(handler) { /* ... */ }
```

---

## 二、Flow 核心 API

### 1. 冷流构建器

| API | 说明 |
|-----|------|
| `flow { emit(x) }` | 通用构建器，lambda 可挂起 |
| `flowOf(a, b, c)` | 固定值序列 |
| `list.asFlow()` / `channelFlow { }` | 集合转换 / 支持多发射者并发发送 |

**定义**: 冷流每次 `collect` 都重新执行构建块；无收集则无执行。

### 2. 中间操作符（返回新 Flow，惰性）

| 操作符 | 作用 |
|--------|------|
| `map` / `mapLatest` | 变换；`Latest` 版丢弃未完成的旧变换 |
| `filter { }` / `filterNotNull()` | 过滤 |
| `onEach { }` | 旁路副作用（埋点/日志） |
| `debounce(300)` | 防抖：停顿 300ms 才发最新值（搜索框标配） |
| `sample(100)` | 采样：周期内取最新值 |
| `distinctUntilChanged()` | 相邻去重（`equals`） |
| `combine(f1, f2) { a, b -> }` | 任一上游发射 → 用最新值组合 |
| `zip(f2) { a, b -> }` | 一一配对（慢者为准） |
| `flatMapLatest { }` | 新值到来取消旧内层流（搜索联查标配） |
| `flatMapConcat` / `flatMapMerge` | 串行连接 / 并发合并 |
| `onStart { }` / `onCompletion { }` | 生命周期钩子 |
| `catch { }` | 捕获上游异常（不影响下游） |
| `retryWhen { }` / `retry(3)` | 条件重试 |
| `buffer(n)` / `conflate()` | 缓冲 / 只保留最新（生产快于消费时） |
| `flowOn(Dispatchers.IO)` | 只改变**上游**执行上下文 |

```kotlin
searchQuery
    .debounce(300)
    .distinctUntilChanged()
    .flatMapLatest { repo.search(it) }
    .flowOn(Dispatchers.IO)            // 上游在 IO，collect 仍在 Main
    .collect { results -> render(results) }
```

### 3. 终端操作符（触发执行）

| 操作符 | 作用 |
|--------|------|
| `collect { }` | 收集所有值 |
| `collectLatest { }` | 新值到来取消未完成的旧处理块（列表渲染常用） |
| `first { }` / `single()` | 取第一个 / 唯一值 |
| `toList()` / `toSet()` | 收集成集合（Flow 完成后） |
| `launchIn(scope)` | 用 `onEach{}.launchIn(scope)` 在指定作用域收集 |

### 4. stateIn / shareIn - 冷转热

```kotlin
val uiState: StateFlow<UiState> = repository.observe()
    .map { UiState.Success(it) as UiState }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),   // 见下表
        initialValue = UiState.Loading
    )
```

| SharingStarted | 行为 |
|----------------|------|
| `Eagerly` | 立即启动，永不停止 |
| `Lazily` | 首个订阅者到来才启动，之后永不停止 |
| `WhileSubscribed(5_000)` | 无订阅 5 秒后停止上游；旋转屏重订阅间隙不断流 ⭐推荐 |

### 5. StateFlow vs SharedFlow

| 维度 | StateFlow | SharedFlow |
|------|-----------|------------|
| 当前值 | 必有（`value`） | 可无 |
| 新订阅者 | 立即收到最新值 | 收到 `replay` 缓冲 |
| 值去重 | 相同值不发射（需 `equals`） | 原样发射 |
| 典型用途 | UI 状态 | 一次性事件（toast/导航） |

```kotlin
// 事件流：replay=0 防止旋转后旧事件重放
private val _events = MutableSharedFlow<Event>(extraBufferCapacity = 1)
val events = _events.asSharedFlow()
_events.tryEmit(Event.ShowToast("已保存"))
```

**陷阱**: StateFlow 去重意味着"连续两次 Toast 相同文本"会丢——事件语义必须用 SharedFlow/Channel。

---

## 相关文档

- 📄 **[可空性与集合 API](./02-null-safety-collections.md)** - 集合操作符与 Flow 的对应表
- 📄 **[Compose 状态 API 详解](./04-compose-state-api.md)** - collectAsStateWithLifecycle 与 UI 收集
- 📄 **[协程与 Flow 基础](../../basics/07-coroutines-flow-basics.md)** - 教程视角的系统学习
- 📖 **[Kotlin Flow 官方文档](https://kotlinlang.org/docs/flow.html)** - 语言级权威参考
