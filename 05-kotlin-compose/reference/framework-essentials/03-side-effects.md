# 副作用 API 速查

> LaunchedEffect / DisposableEffect / SideEffect / rememberUpdatedState / rememberCoroutineScope / snapshotFlow——在"可组合、可跳过"的重组世界里安全地"做事"

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#副作用` `#LaunchedEffect` `#DisposableEffect` `#SideEffect` `#rememberCoroutineScope` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

**副作用（side effect）**：逃出组合作用域、影响外部世界的操作——网络请求、日志、导航、注册监听器等。Compose 组合可能**被任意次重组、任意次跳过**，因此副作用必须交给专用 API 托管，由框架保证"按 key 执行、随组合退出自动清理"，而不是散落在组合体内。

## 📖 语法与签名

| API | 签名要点 | 执行时机 | 清理方式 |
|-----|---------|---------|---------|
| `LaunchedEffect(key)` | `LaunchedEffect(vararg keys: Any?, block: suspend CoroutineScope.() -> Unit)` | 进入组合后启动协程；key 变化时**取消旧协程并重启** | 组合退出自动取消协程 |
| `DisposableEffect(key)` | `DisposableEffect(vararg keys: Any?, effect: () -> DisposableEffectResult)` | 进入组合后同步执行 | 必须返回对象并实现 `onDispose()` |
| `SideEffect` | `SideEffect(effect: () -> Unit)` | **每次成功重组后**同步执行 | 无需清理 |
| `rememberUpdatedState` | `rememberUpdatedState(newValue: T): State<T>` | 每次重组更新其值 | 无 |
| `rememberCoroutineScope` | `rememberCoroutineScope(context?): CoroutineScope` | 获得绑定组合的 scope | 组合退出自动取消其协程 |
| `snapshotFlow` | `snapshotFlow { state }: Flow<T>` | 把 State 读取转为冷流 | 收集方取消即停止 |

选型口诀：**组合驱动 → LaunchedEffect；注册/注销 → DisposableEffect；每次重组后同步 → SideEffect；事件驱动 → rememberCoroutineScope；防旧值 → rememberUpdatedState**。

## 💡 示例

```kotlin
// 1. LaunchedEffect：按 key 加载，userId 变化自动重载
LaunchedEffect(userId) { viewModel.loadProfile(userId) }

// 2. 一次性定时任务：常量 key + rememberUpdatedState 捕获最新回调
val currentOnTimeout by rememberUpdatedState(onTimeout)
LaunchedEffect(Unit) {
    delay(5_000)
    currentOnTimeout()
}

// 3. 事件回调里启动一次性协程（用户触发，不用 LaunchedEffect）
val scope = rememberCoroutineScope()
onScroll = { scope.launch { listState.animateScrollToItem(0) } }

// 4. DisposableEffect：成对注册/注销监听器
DisposableEffect(lifecycleOwner) {
    val observer = LifecycleEventObserver { _, _ -> /* ... */ }
    lifecycleOwner.lifecycle.addObserver(observer)
    onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
}
```

## ⚠️ 常见陷阱

- 在组合体内直接写 `println` / 全局变量 / 启动网络——**每次重组都会执行**；必须包进副作用 API。
- `LaunchedEffect(true)` 用常量 key 表示"组合期间只跑一次"；想"参数变了重来"必须把参数放进 key，否则读到旧参数。
- `DisposableEffect` 忘记返回 `onDispose` 直接编译失败；清理逻辑别写在 effect 块体末尾。
- 把**用户事件触发**的逻辑塞进 `LaunchedEffect` 会在重组时意外重启——事件驱动用 `rememberCoroutineScope`。
- 在 `remember { }` 里启动协程：时序早于组合完成且无取消保障——统一用 `LaunchedEffect`。

## 🔗 相关条目

- 📄 [Compose 状态 API](../language-concepts/04-compose-state-api.md) — remember / derivedStateOf / snapshotFlow
- 📄 [协程与 Flow API 全表](../language-concepts/03-coroutines-flow-api.md)
- 📄 [重组与稳定性](./04-recomposition.md) — 理解为什么副作用需要 key
- 📄 操作指南：[Compose 进阶 - 侧效应](../../frameworks/02-compose-advanced.md)（完整用例）
- 📄 教程：[协程与 Flow 基础](../../basics/07-coroutines-flow-basics.md)
