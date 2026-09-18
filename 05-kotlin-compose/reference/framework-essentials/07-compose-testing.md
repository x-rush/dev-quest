# Compose 测试 API 速查

> **阅读准备**：基础单元测试、Composable 与语义树；设备测试还需要正确的测试 runner 和模拟器/设备。

> Jetpack Compose UI 测试的字典式速查：测试规则、依赖坐标、语义树查找器、断言、交互与主线程时钟

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Compose` `#compose-test` `#semantics` `#测试` |
| **更新日期** | `2026年9月` |

---

## 1. 依赖与测试规则

### 定义
Compose UI 测试跑在 instrumentation 环境（`androidTest` 源集 + 设备/模拟器），核心入口是 `ComposeTestRule`——它接管组合、驱动重组并提供语义树查询。

### 语法和示例
```kotlin
// build.gradle.kts（版本统一走 Compose BOM，不写独立版本号，以官方最新稳定版为准）
dependencies {
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")          // ⭐ 测试本体

    debugImplementation("androidx.compose.ui:ui-test-manifest")              // 纯组件测试所需 Activity 声明
}

android {
    defaultConfig {
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner" // JUnit4 运行器
    }
}
```

```kotlin
// 纯组件测试：不需要完整 Activity
class CounterTest {
    @get:Rule
    val rule = createComposeRule()               // 返回 ComposeContentTestRule

    @Test
    fun clicks_increment() {
        rule.setContent { Counter() }            // 挂载被测组合
        // ... 查找与断言
    }
}

// 整 Activity 测试：走真实启动流程（导航/主题全真）
class MainScreenTest {
    @get:Rule
    val rule = createAndroidComposeRule<MainActivity>()
}
```

| API | 场景 |
|-----|------|
| `createComposeRule()` | 测单个组件/组合片段（首选，秒级反馈） |
| `createAndroidComposeRule<T>()` | 需要 Activity 生命周期/导航图/注入入口时 |

## 2. 语义树与查找器

### 定义
Compose 测试不碰 View 层级，而是查询**语义树**（semantics tree）——无障碍使用的那棵树。`Modifier.testTag` 与 `semantics { contentDescription }` 是给节点"挂门牌"的两种方式。

### 语法和示例
```kotlin
// 生产代码：给节点打标
Text("提交", Modifier.testTag("submit_button"))          // 测试专用标签
Icon(Icons.Default.Delete, contentDescription = "删除")   // 无障碍描述兼可测试

// 测试代码：三种常用查找器
rule.onNodeWithText("计数：0")                            // 按显示文本
rule.onNodeWithTag("submit_button")                      // 按 testTag（文本会变/多行同文案时用它）
rule.onNodeWithContentDescription("删除")                // 按无障碍描述

rule.onAllNodesWithText("已完成").assertCountEquals(3)    // 多节点查询（onAllNodes 系）

// 子树合并：默认合并文本节点；要逐节点匹配时开未合并树
rule.onNodeWithText("账户设置", useUnmergedTree = true)
```

| 查找器 | 匹配依据 |
|--------|----------|
| `onNodeWithText(text)` | 渲染文本（substring/ignoreCase 可选） |
| `onNodeWithTag(tag)` | `Modifier.testTag` ⭐ 稳定定位首选 |
| `onNodeWithContentDescription(desc)` | 语义 contentDescription |
| `onAllNodesWithText/WithTag/...` | 返回集合，配 `assertCountEquals` 等 |

## 3. 断言

```kotlin
rule.onNodeWithText("计数：0").assertExists()             // 树里有这个节点
rule.onNodeWithTag("counter").assertIsDisplayed()         // 存在且可见（排除被滚出屏幕等）
rule.onNodeWithTag("label").assertTextEquals("计数：0")   // 文本内容精确等于
```

| 断言 | 含义 |
|------|------|
| `assertExists()` | 语义树中存在 |
| `assertIsDisplayed()` | 在屏幕可见区域内 ⭐ |
| `assertTextEquals(...)` | 文本精确匹配（可传多个期望值） |

## 4. 交互

```kotlin
rule.onNodeWithTag("increment").performClick()                    // 点击
rule.onNodeWithTag("title_input").performTextInput("Compose 指南") // 输入（先获得焦点）
rule.onNodeWithTag("title_input").performTextClearance()          // 清空
rule.onNodeWithTag("list").performScrollToNode(hasText("底部项"))  // 滚动到目标再断言
```

交互前不需要手动等待：**Compose 测试会自动同步重组与空闲状态**（无需 `Thread.sleep`）。

## 5. 主线程时钟（mainClock）

### 定义
`rule.mainClock` 是测试专用的**虚拟动画时钟**。测试默认 `autoAdvance = true` 自动走帧；关掉后可精确控制每一帧，专治动画/无限动画干扰断言。

### 语法和示例
```kotlin
@Test
fun progress_animates() {
    rule.mainClock.autoAdvance = false                  // ⭐ 关自动走帧
    rule.setContent { AnimatedProgress(target = 1f) }

    rule.mainClock.advanceTimeBy(500)                   // 虚拟推进 500ms（瞬时跳过等待）
    rule.mainClock.advanceTimeByFrame()                 // 只推进一帧
    rule.onNodeWithTag("progress").assertIsDisplayed()
}

// 不需要冻结时钟时的条件等待
rule.waitUntil(timeoutMillis = 5_000) { 
    rule.onAllNodesWithTag("loaded").fetchSemanticsNodes().isNotEmpty()
}
```

| API | 用途 |
|-----|------|
| `mainClock.autoAdvance = false` | 冻结自动走帧，手动控帧 |
| `mainClock.advanceTimeBy(ms)` | 虚拟推进时长（不等真实时间） |
| `mainClock.advanceTimeByFrame()` | 推进一帧 |
| `waitUntil { }` | 条件等待（异步加载结果） |

## 6. 陷阱

- ❌ 文本做唯一标识但列表多行同文案 → ✅ 稳定节点一律 `testTag`；文本匹配留给用户可见行为断言
- ❌ `contentDescription = null` 的装饰图标想按它查找 → ✅ null 不提供该图标的文字描述，但不能据此推断整个节点一定没有其他语义；可交互图标必须给描述
- ❌ 断言前 `Thread.sleep(2000)` 等加载 → ✅ `waitUntil` 条件等待；重组本身已自动同步
- ❌ 动画没完就断言，或无限动画让测试超时 → ✅ `mainClock.autoAdvance = false` + 手动走帧
- ❌ 交互测试直接改 ViewModel 内部状态会绕过事件链 → ✅ 行为测试走 UI；独立状态渲染测试可注入明确状态

---

## 相关文档

- 📄 **[Compose UI 测试指南](../../testing/02-ui-testing.md)** - 测试策略与分层选型的"怎么用"
- 📄 **[Compose 状态 API 详解](../language-concepts/04-compose-state-api.md)** - 被测状态的数据来源
- 📄 **[重组与稳定性速查](./04-recomposition.md)** - 理解自动同步的就是重组
- 📖 **[Compose 测试官方文档](https://developer.android.com/develop/ui/compose/testing)** - 全量 API 参考


<!-- full-library-explanation -->
## 一个完整的行为断言

将下例放入已配置测试依赖的 `src/androidTest/.../CounterTest.kt`。它在设备或模拟器中运行，本轮未在 Android 工具链执行。

```kotlin
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import org.junit.Rule
import org.junit.Test

class CounterBehaviorTest {
    @get:Rule val rule = createComposeRule()
    @Test fun clickChangesVisibleCount() {
        rule.setContent {
            var count by remember { mutableIntStateOf(0) }
            Button(onClick = { count++ }) { Text("计数：$count") }
        }
        rule.onNodeWithText("计数：0").performClick()
        rule.onNodeWithText("计数：1").assertIsDisplayed()
    }
}
```

这个测试验证用户可见变化，不验证某个内部变量恰好等于 1。真实业务把计数器替换成被测组件即可。网络、数据库和其他调度器并不都受 Compose mainClock 控制；使用可控依赖和条件等待，不要指望推进动画时钟就完成网络请求。

练习：把 onClick 改成空操作，测试应失败；再给屏幕增加两个同文案按钮，改用明确的层级或语义选择器。验收：测试不会因匹配错节点而“绿灯”，也不把 testTag 当作替代无障碍标签的产品信息。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
