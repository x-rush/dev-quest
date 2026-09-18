# Navigation Compose 组件速查

> **阅读准备**：Composable、状态所有权和 Android 页面生命周期；理解路由参数不是可随意共享的对象容器。

> NavController / NavHost / 路由 / NavBackStackEntry / 参数与深链——单 Activity 多页面导航的字典层

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#navigation` `#NavHost` `#NavController` `#BackStackEntry` `#深链` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

Navigation Compose 用**路由 + 后备栈**管理页面：`NavHost` 是目的地容器，`NavController` 掌控跳转与返回栈，每个目的地对应栈上一个 `NavBackStackEntry`——它自带生命周期、SavedStateHandle 与 ViewModelStore，是"页面级状态"的天然宿主。

## 📖 语法与签名

```kotlin
// 1. 创建控制器
val navController = rememberNavController()

// 2. 声明导航图：起始目的地 + composable 路由（路径参数）
NavHost(navController, startDestination = "home") {
    composable("home") { HomeScreen() }
    composable(
        route = "detail/{noteId}",
        arguments = listOf(navArgument("noteId") { type = NavType.LongType }),
    ) { backStackEntry ->
        val noteId = backStackEntry.arguments?.getLong("noteId")
        DetailScreen(noteId)
    }
}

// 3. 跳转
navController.navigate("detail/$noteId") { launchSingleTop = true }

// 4. 返回栈操作
navController.popBackStack()
navController.navigate("home") { popUpTo("home") { inclusive = true } }
```

### 查询参数（可选参数）

路由模板用 `?key={key}` 声明查询参数：**可省略**，不传走 `defaultValue`——与路径参数（`detail/{noteId}`，必填、参与路由唯一性）互补，适合过滤/排序等修饰位。

```kotlin
composable(
    route = "list?filter={filter}",
    arguments = listOf(navArgument("filter") {
        type = NavType.StringType
        defaultValue = "all"          // 不传时的兜底值
    }),
) { backStackEntry ->
    ListScreen(filter = backStackEntry.arguments?.getString("filter"))
}
// navController.navigate("list")              → filter = "all"
// navController.navigate("list?filter=done")  → filter = "done"
```

### 嵌套导航图

`navigation(startDestination, route)` 把一组目的地聚合为子图：子图 route 可整体跳转、整体出栈、整体挂深链——登录/注册流的"一次清干净"靠它。

```kotlin
NavHost(navController, startDestination = "auth") {
    navigation(startDestination = "login", route = "auth") {
        composable("login") { LoginScreen(onDone = { navController.navigate("register") }) }
        composable("register") { RegisterScreen() }
    }
    composable("home") { HomeScreen() }
}

// 登录成功进 home：把整个 auth 子图出栈——login/register 不留返回栈
navController.navigate("home") {
    popUpTo("auth") { inclusive = true }   // popUpTo 指向子图 route，inclusive 连子图一起弹
}
```

核心组件：

| 组件 | 职责 |
|------|------|
| `rememberNavController()` | 创建并 remember 导航控制器 |
| `NavHost` | 目的地容器，路由切换时重组内容 |
| `composable(route)` | 声明目的地与内容 |
| `NavBackStackEntry` | 栈条目：生命周期 + SavedStateHandle + ViewModelStore |
| `currentBackStackEntryAsState()` | 观察当前目的地（供底部栏高亮） |
| `hiltViewModel()` | 按后备栈条目获取 ViewModel（Hilt 集成） |
| `NavDeepLink` | 声明深链匹配规则 |

## 💡 示例

```kotlin
// 底部导航联动：观察当前目的地高亮 + 状态保存
val navBackStackEntry by navController.currentBackStackEntryAsState()
val currentRoute = navBackStackEntry?.destination?.route

NavigationBar {
    items.forEach { item ->
        NavigationBarItem(
            selected = currentRoute == item.route,
            icon = { Text(item.route) }, // 教学占位；产品使用图标与可读标签
            onClick = {
                navController.navigate(item.route) {
                    popUpTo(navController.graph.findStartDestination().id) { saveState = true }
                    launchSingleTop = true
                    restoreState = true
                }
            },
        )
    }
}
```

`popUpTo` + `launchSingleTop` + `restoreState`（配合 `saveState`）是官方底部导航标准姿势，四个选项各司其职：

| 选项 | 作用 |
|------|------|
| `popUpTo(findStartDestination().id) { saveState = true }` | 弹掉起始目的地之上的所有目的地（起始目的地本身保留），弹出前保存其状态 |
| `launchSingleTop = true` | 目的地已在栈顶则不重复入栈（连点防重） |
| `restoreState = true` | 重新进入该 tab 时恢复先前保存的栈状态 |

三项都不加的效果：每个 tab 反复入栈、切走即丢状态、返回时要按入栈次数逐层退——这正是很多"底部栏越点越深"问题的根源。

## ⚠️ 常见陷阱

- 路由字符串里传的参数类型必须与 `navArgument` 声明一致（Long 传成 String 会在运行时崩溃）。
- 大对象别塞路由：路由参数以字符串承载并参与 SavedStateHandle 恢复，只放 ID，数据由 ViewModel 查询。
- 快速连点导致重复入栈：`launchSingleTop = true`，必要时叠加点击防抖。
- 底部栏切换不加 `saveState` / `restoreState` 会丢失各 tab 状态。
- "带结果返回"不要用全局单例事件——用后备栈条目的 SavedStateHandle 或共享 ViewModel。
- 深链三处必须一致：Manifest 的 intent-filter、`deepLinks` 声明、路由模板。
- 可选查询参数需明确默认值或可空类型等缺省语义——从深链进入缺参时没有兜底即出错。

<!-- full-library-explanation -->
## 导航是状态变更，参数是输入

示例必须声明 startDestination 指向的页面，否则导航图无法正常启动。生产工程可采用当前 Navigation 支持的类型安全路由；本页字符串示例用于理解路径/参数模型，路径中的文本参数需要编码，不能直接拼接任意标题或 URL。

同一目的地可能有多个 back stack entry，各自拥有状态作用域。launchSingleTop 只处理栈顶重复，不是全栈去重；清除 auth 栈避免返回登录流程，但资源权限仍由服务端校验。

练习：列表 → 编辑 → 返回结果，消费 SavedStateHandle 中的结果后移除或标记已处理；旋转并再次返回。验收：保存提示不会重复消费，未保存草稿的返回行为明确，深链携带无效 ID 时有错误页面。可选参数可使用默认值或可空声明，按具体路由类型约束设计。

## 🔗 相关条目

- 📄 教程：[页面导航](../../basics/06-navigation.md)
- 📄 [Compose 核心组件速查](./01-compose-essentials.md) - BackHandler 拦截返回与导航返回的分工
- 📄 [Compose 状态 API](../language-concepts/04-compose-state-api.md)
- 📄 [副作用 API](./03-side-effects.md) — 导航触发即副作用
- 📄 [AndroidX 官方库指南](../library-guides/01-androidx-libraries.md)
- 📖 官方文档：[Navigation Compose](https://developer.android.com/develop/ui/compose/navigation)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
