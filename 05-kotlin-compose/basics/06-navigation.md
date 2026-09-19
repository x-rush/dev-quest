# 页面导航 - Navigation Compose 入门

## 先理解，再动手

导航状态决定当前页面与返回路径。参数传 ID，页面根据 ID 读取数据，可避免序列化整个对象与同步过期副本。

**本节自测**：从笔记列表进入详情，修改后返回，再模拟不存在 ID。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

返回列表显示更新；不存在时显示明确状态，不通过强制解包制造崩溃。

</details>

> **文档简介**: 使用 Navigation Compose 实现多页面切换：NavHost/NavController 三件套、路由参数传递、底部导航与嵌套导航图
>
> **目标读者**: 已掌握单页面布局与状态、需要构建多屏应用的开发者
>
> **前置知识**: [布局系统](./05-layouts.md)；了解 Scaffold 基本用法

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#Navigation` `#NavHost` `#路由参数` `#底部导航` `#嵌套图` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 引入 navigation-compose 依赖并搭建 NavHost
- ✅ 在路由中定义位置参数与可选参数
- ✅ 使用 `navigate`/`popBackStack` 管理返回栈
- ✅ 用 NavigationBar 实现底部标签导航
- ✅ 用嵌套导航图组织登录/主流程等多组页面

## 📋 目录

- [添加依赖](#-添加依赖)
- [核心三件套](#-核心三件套)
- [路由传参](#-路由传参)
- [返回栈控制](#️-返回栈控制)
- [底部导航](#-底部导航)
- [嵌套导航图](#️-嵌套导航图)
- [练习与实践](#-练习与实践)

---

## 📦 添加依赖

在 `gradle/libs.versions.toml` 中添加以下固定版本示例；它不是“当前最新”的声明。已有项目应保留自己的版本目录，并核对 Navigation、Kotlin 与 Compose 工具链兼容性：

```toml
[versions]
navigationCompose = "2.9.5"

[libraries]
androidx-navigation-compose = { group = "androidx.navigation", name = "navigation-compose", version.ref = "navigationCompose" }
```

在 `app/build.gradle.kts` 中引用：

```kotlin
dependencies {
    implementation(libs.androidx.navigation.compose)
}
```

> 💡 Navigation 2.8+ 支持**类型安全路由**（配合 kotlinx.serialization 定义 `@Serializable data object`），本课先掌握字符串路由这一基础形态，其概念完全通用。

---

## 🧭 核心三件套

Navigation Compose 由三个角色组成：

| 角色 | API | 职责 |
|------|-----|------|
| **NavController** | `rememberNavController()` | 导航状态大脑，管理返回栈 |
| **NavHost** | `NavHost(navController, startDestination)` | 容器，根据当前目的地切换内容 |
| **目的地** | `composable("route") { }` | 一条路由对应一个 Composable 页面 |

导航接线骨架（`TaskListScreen` 等页面需由项目提供，不能整段当作独立应用运行）：

```kotlin
@Composable
fun App() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "list") {
        composable("list") {
            TaskListScreen(
                onTaskClick = { id -> navController.navigate("detail/$id") }
            )
        }
        composable("detail/{taskId}") { backStackEntry ->
            val taskId = backStackEntry.arguments?.getString("taskId")
            TaskDetailScreen(taskId = taskId)
        }
    }
}
```

---

## 🔤 路由传参

### 位置参数（必填）

路由中用 `{占位符}` 声明，配合 `navArgument` 指定类型：

```kotlin
composable(
    route = "detail/{taskId}",
    arguments = listOf(
        navArgument("taskId") { type = NavType.LongType }
    )
) { backStackEntry ->
    val taskId = backStackEntry.arguments?.getLong("taskId") ?: 0L
    TaskDetailScreen(taskId)
}

// 导航时直接填值
navController.navigate("detail/42")
```

### 查询参数（可选）

用 `?key={key}` 声明并提供默认值：

```kotlin
composable(
    route = "list?filter={filter}",
    arguments = listOf(
        navArgument("filter") {
            type = NavType.StringType
            defaultValue = "all"          // 缺省值
        }
    )
) { backStackEntry ->
    val filter = backStackEntry.arguments?.getString("filter") ?: "all"
}

navController.navigate("list?filter=done")
```

**经验法则**：参数只传简单标识（id、query），复杂对象不要塞进路由——它们应存于数据库或共享 ViewModel，页面只拿 id 现查。

---

## ↩️ 返回栈控制

```kotlin
// 基本前进
navController.navigate("detail/1")

// 返回上一页（系统返回键等价）
navController.popBackStack()

// 带导航选项：避免重复入栈 + 弹到指定目的地
navController.navigate("list") {
    launchSingleTop = true                         // 目的地已在栈顶则不重复创建
    popUpTo("list") { inclusive = false }          // 弹出到 list 为止
    // inclusive 也会移除目标条目；嵌套图下必须选对目标，不能视作通用“清空栈”。
}
```

典型场景——登录成功后进入主页并**清空**返回栈，防止按返回键回到登录页。

---

## 📑 底部导航

结合 `Scaffold` 与 `NavigationBar`，用当前返回栈条目驱动选中态：

```kotlin
@Composable
fun MainScaffold(navController: NavHostController) {
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route

    Scaffold(
        bottomBar = {
            NavigationBar {
                listOf(
                    "list" to Icons.Default.List,
                    "profile" to Icons.Default.Person
                ).forEach { (route, icon) ->
                    NavigationBarItem(
                        selected = currentRoute == route,
                        onClick = {
                            navController.navigate(route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true      // 切回标签恢复滚动位置等状态
                            }
                        },
                        icon = { Icon(icon, contentDescription = null) },
                        label = { Text(if (route == "list") "任务" else "我的") }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = "list",
            modifier = Modifier.padding(innerPadding)     // ⭐ 避免内容被底栏遮挡
        ) {
            composable("list") { TaskListScreen() }
            composable("profile") { ProfileScreen() }
        }
    }
}
```

`popUpTo + saveState/restoreState + launchSingleTop` 是官方推荐的标签切换"标准四件套"。

---

## 🗺️ 嵌套导航图

用 `navigation` 把相关页面编组，形成"图内路由"：

```kotlin
NavHost(navController, startDestination = "auth") {
    // 认证流程组
    navigation(startDestination = "login", route = "auth") {
        composable("login") {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate("home") {
                        popUpTo("auth") { inclusive = true }   // 登录后整组出栈
                    }
                }
            )
        }
        composable("register") { RegisterScreen() }
    }

    // 主流程组
    navigation(startDestination = "home", route = "home_graph") {
        composable("home") { HomeScreen() }
        composable("detail/{taskId}") { TaskDetailScreen() }
    }
}
```

嵌套图把认证流程编组，`popUpTo("auth") { inclusive = true }` 用于移除该流程。仅声明 `route = "auth"` 不会自动注册外部深链；还需声明 deepLinks，外部 URL 入口还涉及 Manifest 的 intent filter。参见 [Android 深链说明](https://developer.android.com/guide/navigation/design/deep-link)。

---

## 🎯 练习与实践

### 先交付可回查的两页练习

前置：Android Studio 中已有 Empty Activity Compose 项目，Gradle 同步成功，设备能显示静态 Text；下文沿用 Navigation 2.x 字符串路由，不能与 Navigation 3 的 API 混写。把 NavHost 放进 Activity 的 `setContent`，补齐 runtime、Material3 与 navigation-compose 的 import。文中的页面组件是接线占位，需自行实现。

产物：列表页固定展示 `id=1, title=第一条笔记`，详情只接收 Long ID，再从固定 Map 查询标题；提供返回按钮及“打开不存在的 999”按钮。详情查不到时显示“笔记不存在”，仍允许返回。导航层传 `onOpen(id)` 和 `onBack()` 回调给页面，页面不必直接持有 NavController，便于单独检查 UI。

| 输入 | 预期输出 | 失败回查 |
|---|---|---|
| 列表点 1 | 详情显示“第一条笔记” | route 占位名、NavType.LongType 与 getLong 的键是否一致 |
| 点返回 | 回到列表 | popBackStack 是否返回 false，是否已经位于根目的地 |
| 打开 999 | 明确缺失状态，可返回 | 是否把 ID 存在误当作业务记录存在 |
| 连续导航同一栈顶详情 | 配置 launchSingleTop 时不重复入栈 | 它只作用于栈顶，不负责全栈去重 |
| 详情按系统返回 | 回到列表 | 自定义 BackHandler 是否拦截事件 |

本轮未执行 Gradle 构建、Android 模拟器或真机，以上为验收预期，原生导航仍未验证。接入后先执行项目的 `gradlew.bat :app:assembleDebug`，再在设备走完整操作表，记录 Android API、Navigation 版本与截图；编译成功不等于回栈行为正确。

下一步先接入 [协程与 Flow](./07-coroutines-flow-basics.md)，把固定 Map 换成按 ID 查询的数据源，再检查删除记录后返回详情的缺失状态。最后才扩展标签页保存恢复和外部深链。参考 [官方导航操作](https://developer.android.com/guide/navigation/use-graph/navigate)。

### 基础练习
- [ ] 为笔记应用加上两个页面：列表页 + 详情页，点击条目携带 id 跳转
- [ ] 给详情页添加可空的 `?highlight={highlight}` 参数，实现"定位到指定关键词"
- [ ] 在详情页放一个"返回"按钮，用 `popBackStack()` 实现
- [ ] 用 `launchSingleTop` 阻止连续点击两次按钮产生的双重入栈

### 进阶挑战
- [ ] 实现三标签底部导航，验证切换标签后滚动位置被恢复（restoreState）
- [ ] 把登录流程封装为 `navigation(startDestination = "login", route = "auth")` 嵌套图，登录成功后整组出栈
- [ ] 进阶阅读：用 kotlinx.serialization 把字符串路由改造成类型安全路由（Navigation 2.8+）

---

## 🔗 相关文档

- 📄 **[协程与 Flow 基础](./07-coroutines-flow-basics.md)** - 下一篇：为页面注入异步数据
- 📄 **[AndroidX 官方库指南](../reference/library-guides/01-androidx-libraries.md)** - Navigation 与 ViewModel 的联动
- 📄 **[Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md)** - Scaffold/NavigationBar 参数速查
- 📄 **[Navigation Compose 组件速查](../reference/framework-essentials/06-navigation-components.md)** - NavController/NavBackStackEntry/深链字典
- 📖 **[Navigation Compose 官方文档](https://developer.android.com/develop/ui/compose/navigation)** - 路由与深链完整指南


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
