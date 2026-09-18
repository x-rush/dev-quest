# Compose 进阶 - 侧效应、导航与动画

## 先看框架承担哪部分职责

**Compose 副作用**：副作用 API 把工作绑定到组合与 key 的生命周期，导航与动画也有自身状态。避免用“只执行一次”掩盖重入和取消。

**最小练习与预期结果**：使用随参数改变的 LaunchedEffect，切换 key 并离开页面；旧工作应按协程规则取消，新工作使用新参数。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 掌握 Compose 侧效应处理（LaunchedEffect 等）、Navigation Compose 路由与常用动画 API 的任务式指南
>
> **目标读者**: 已能用 remember/布局搭出静态界面、准备开发多页面交互应用的进阶学习者
>
> **前置知识**: [Compose 入门核心](01-compose-basics.md)、[协程与 Flow 基础](../basics/07-coroutines-flow-basics.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（frameworks） |
| **难度** | ⭐⭐ |
| **标签** | `#side-effects` `#navigation-compose` `#animation` |
| **更新日期** | `2026年9月` |

</details>

---

## 1️⃣ 侧效应：在声明式世界里"做事"

Composable 应当是幂等无副作用的，但真实需求总要"做事"（请求网络、埋点、注册回调）。
Compose 提供的侧效应 API 就是**受控的副作用出口**：

| API | 适用场景 | 关键行为 |
|-----|---------|---------|
| `LaunchedEffect(key)` | 组合时启动挂起任务 | key 变化 → 取消旧协程、重启新协程；离开组合 → 自动取消 |
| `rememberCoroutineScope()` | 事件回调中启动协程 | 生命周期与组合点绑定，需在回调中手动调用 |
| `DisposableEffect(key)` | 注册/注销成对的监听器 | 离开组合（或 key 变化）时执行 `onDispose` |
| `rememberUpdatedState` | 长生命周期协程要读最新值 | 不重启协程的前提下捕获新值 |
| `SideEffect` | 每次重组成功后同步非 Compose 状态 | 无 key，每次重组后都执行 |

### 示例：按 userId 加载资料

```kotlin
@Composable
fun UserProfile(userId: String, repo: UserRepository) {
    var profile by remember { mutableStateOf<Profile?>(null) }

    // userId 变化 → 旧请求取消、发起新请求；离开屏幕 → 协程自动取消
    LaunchedEffect(userId) {
        profile = repo.fetchProfile(userId)
    }
}
```

### 示例：事件回调里启动协程

```kotlin
@Composable
fun LoginScreen(viewModel: LoginViewModel) {
    val scope = rememberCoroutineScope()

    Button(onClick = {
        scope.launch { viewModel.login() }   // 用户事件中启动，不能写在组合体里
    }) { Text("登录") }
}
```

### 示例：不重启协程地捕获最新回调

```kotlin
@Composable
fun RefreshableContent(onRefresh: () -> Unit) {
    // 回调更新只改这里持有的引用，LaunchedEffect 不会重启
    val currentOnRefresh by rememberUpdatedState(onRefresh)

    LaunchedEffect(Unit) {
        delay(60_000)
        currentOnRefresh()   // 读到的始终是最新回调
    }
}
```

### 示例：成对注册/注销监听器

```kotlin
@Composable
fun ConnectivityStatus(onStatusChange: (Boolean) -> Unit) {
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) onStatusChange(true)
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)   // 离开组合必然执行
        }
    }
}
```

> 协程 API 细节（调度器、异常、Flow）见 [协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md)。

## 2️⃣ Navigation Compose：单 Activity 路由

依赖：`androidx.navigation:navigation-compose`。

```kotlin
@Composable
fun AppNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController = navController, startDestination = "list") {
        composable(route = "list") {
            NotesListScreen(
                onNoteClick = { id -> navController.navigate("detail/$id") }
            )
        }
        // 路径参数：{noteId}
        composable(
            route = "detail/{noteId}",
            arguments = listOf(navArgument("noteId") { type = NavType.LongType })
        ) { backStackEntry ->
            val noteId = backStackEntry.arguments?.getLong("noteId") ?: 0L
            NoteDetailScreen(noteId = noteId, onBack = { navController.popBackStack() })
        }
    }
}
```

实践要点：

- **参数走 route，大数据走共享 ViewModel**，避免把整个对象序列化进 URL；
- 返回结果用共享 ViewModel 或 `savedStateHandle`，而不是"回传参数"；
- 深层嵌套用嵌套导航图（`navigation(...) {}`）按功能域拆分，见[页面导航教程](../basics/06-navigation.md)。

## 3️⃣ 动画：从状态差到过渡效果

Compose 动画的核心思路：**你只改变状态，动画 API 负责在状态之间插值**。

```kotlin
@Composable
fun Demo() {
    var expanded by remember { mutableStateOf(false) }
    // ① 属性动画：单个值随状态平滑变化
    val alpha by animateFloatAsState(
        targetValue = if (expanded) 1f else 0.3f,
        animationSpec = tween(300),
        label = "alpha",
    )

    Column {
        Box(
            Modifier
                .size(100.dp)
                .graphicsLayer { this.alpha = alpha }
                .background(MaterialTheme.colorScheme.primary)
        )

        // ② 出现/消失动画：条件组合
        AnimatedVisibility(visible = expanded) {
            Text("更多详情……")
        }

        // ③ 内容切换动画：按状态交叉淡入淡出
        Crossfade(targetState = expanded, label = "crossfade") { isExpanded ->
            if (isExpanded) Text("已展开") else Text("已折叠")
        }

        // ④ 尺寸动画：容器随内容变化自动过渡
        Card(Modifier.animateContentSize()) {
            Text(if (expanded) "很长很长的详情内容……" else "摘要……")
        }

        Button(onClick = { expanded = !expanded }) { Text("切换") }
    }
}
```

选型口诀：值变用 `animate*AsState`、显隐用 `AnimatedVisibility`、内容切换用 `Crossfade`、
尺寸自适应用 `animateContentSize`；页面转场在 `NavHost` 的 `enterTransition/exitTransition` 配置。

## 🎨 最佳实践

LaunchedEffect 的 key 决定何时取消旧任务并重启，例如用户 id 改变就重新加载；计数器若确实代表“重试一次”也可以成为 key，关键是行为是否符合预期。任务不应重启但需要读取最新回调时，可用 rememberUpdatedState。见[官方副作用说明](https://developer.android.com/develop/ui/compose/side-effects)。

有注册与注销的资源可在 DisposableEffect 中成对处理。测试离开页面后监听是否移除、快速切换 id 后旧结果是否还会覆盖新页面。动画时长按交互目的和用户设置决定，不用一个固定毫秒数判断全部动画。

## 🔗 相关文档

- 📖 概念字典：[协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md) ｜ [Compose 状态 API 详解](../reference/language-concepts/04-compose-state-api.md) ｜ [副作用 API](../reference/framework-essentials/03-side-effects.md) ｜ [动画核心 API](../reference/framework-essentials/05-animation-core.md)
- 📖 前置教程：[页面导航](../basics/06-navigation.md) ｜ [协程与 Flow 基础](../basics/07-coroutines-flow-basics.md)
- 🚀 后续学习：[生态集成：Room + Hilt + Retrofit + ViewModel](03-ecosystem-integration.md) ｜ [重组优化](../advanced-topics/performance/01-recomposition-optimization.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
