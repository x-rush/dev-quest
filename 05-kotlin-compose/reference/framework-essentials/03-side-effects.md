# 副作用 API 速查

> **阅读准备**：组合/重组/离开组合的区别，以及 Kotlin 协程与取消。

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
- 把**用户事件触发**的逻辑塞进 `LaunchedEffect` 可能因所选 key 的变化或重新进入组合而再次执行；并非每次普通重组都重启——事件驱动用 `rememberCoroutineScope`。
- 在 `remember { }` 里启动协程：时序早于组合完成且无取消保障——统一用 `LaunchedEffect`。

<!-- full-library-explanation -->
## 取消的是哪一项工作

`LaunchedEffect(userId)` 取消的是它自己的协程。如果 `viewModel.loadProfile` 内部另起 viewModelScope.launch 后立即返回，旧加载任务不一定随 Effect 取消。可让 suspend 加载留在调用方的结构化作用域，或由 ViewModel 按 userId 取消/替换旧任务，不能只看外面包了 Effect 就认为竞态消失。

rememberUpdatedState 适合“任务继续，但使用最新回调”；key 适合“身份变了，任务必须重来”。例如倒计时期间更换 onTimeout 不必重新计时，而切换账户的详情请求通常必须替换。

练习：A 请求延迟两秒、B 请求延迟一百毫秒，快速从 A 切到 B。验收：最终只显示 B；退出组合时监听器成对移除；取消异常没有被当成普通失败吞掉。参考 [官方副作用指南](https://developer.android.com/develop/ui/compose/side-effects)。

## 🔗 相关条目

- 📄 [Compose 状态 API](../language-concepts/04-compose-state-api.md) — remember / derivedStateOf / snapshotFlow
- 📄 [协程与 Flow API 全表](../language-concepts/03-coroutines-flow-api.md)
- 📄 [重组与稳定性](./04-recomposition.md) — 理解为什么副作用需要 key
- 📄 操作指南：[Compose 进阶 - 侧效应](../../frameworks/02-compose-advanced.md)（完整用例）
- 📄 教程：[协程与 Flow 基础](../../basics/07-coroutines-flow-basics.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
