# Navigation Compose 组件速查

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

## ⚠️ 常见陷阱

- 路由字符串里传的参数类型必须与 `navArgument` 声明一致（Long 传成 String 会在运行时崩溃）。
- 大对象别塞路由：路由参数以字符串承载并参与 SavedStateHandle 恢复，只放 ID，数据由 ViewModel 查询。
- 快速连点导致重复入栈：`launchSingleTop = true`，必要时叠加点击防抖。
- 底部栏切换不加 `saveState` / `restoreState` 会丢失各 tab 状态。
- "带结果返回"不要用全局单例事件——用后备栈条目的 SavedStateHandle 或共享 ViewModel。
- 深链三处必须一致：Manifest 的 intent-filter、`deepLinks` 声明、路由模板。

## 🔗 相关条目

- 📄 教程：[页面导航](../../basics/06-navigation.md)
- 📄 [Compose 状态 API](../language-concepts/04-compose-state-api.md)
- 📄 [副作用 API](./03-side-effects.md) — 导航触发即副作用
- 📄 [AndroidX 官方库指南](../library-guides/01-androidx-libraries.md)
- 📖 官方文档：[Navigation Compose](https://developer.android.com/develop/ui/compose/navigation)
