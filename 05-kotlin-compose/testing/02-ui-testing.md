# UI 测试 - Compose UI Test

> **文档简介**: 用 Compose 测试 API 针对单个组件与整个界面编写语义化 UI 测试：语义树、匹配器/断言/动作、异步等待与状态注入
>
> **目标读者**: 已掌握[单元测试](01-unit-testing.md)、想让 UI 行为有回归保障的进阶学习者
>
> **前置知识**: [Compose 入门核心](../frameworks/01-compose-basics.md)（尤其状态提升）、[Compose 状态 API 详解](../reference/language-concepts/04-compose-state-api.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（testing） |
| **难度** | ⭐⭐ |
| **标签** | `#compose-test` `#semantics` `#ui-test` |
| **更新日期** | `2026年9月` |

</details>

---

## 1️⃣ 依赖与最小骨架

```kotlin
dependencies {
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-test-manifest")   // 提供 test Activity
}
```

```kotlin
class CounterCardTest {

    @get:Rule
    val rule = createComposeRule()          // 纯组件测试用它；整 Activity 用 createAndroidComposeRule

    @Test
    fun `点击加号后 计数文本更新`() {
        var count by mutableStateOf(0)

        rule.setContent {
            AppTheme {
                CounterCard(count = count, onIncrement = { count++ })
            }
        }

        rule.onNodeWithText("计数：0").assertIsDisplayed()
        rule.onNodeWithText("+1").performClick()
        rule.onNodeWithText("计数：1").assertIsDisplayed()   // 自动同步重组，无需手动等待
    }
}
```

Compose 测试在**语义树（Semantics Tree）**上工作，不是截图或坐标：
`onNodeWithText / onNodeWithTag / onNodeWithContentDescription` 是三大匹配器。

## 2️⃣ 状态提升让组件可测

[无状态组件](../frameworks/01-compose-basics.md) 是 UI 测试的前提——上面示例直接注入 `count` 与回调，
不需要数据库、网络或 ViewModel。若组件内部持有状态，先状态提升再测。

给组件加自定义语义，让无障碍与测试共用一套描述：

```kotlin
@Composable
fun NoteRow(note: Note, onDelete: () -> Unit) {
    Row(
        modifier = Modifier
            .semantics { contentDescription = "笔记：${note.title}" }   // TalkBack 与测试共用
            .testTag("noteRow")                                          // 或用 testTag 精确定位
    ) { /* ... */ }
}

// 测试里按 tag 定位并断言数量
rule.onAllNodesWithTag("noteRow").assertCountEquals(3)
```

## 3️⃣ 异步内容：waitUntil

涉及协程/Flow 的界面（ViewModel 注入真实或 Fake 实现）需要显式等待：

```kotlin
@Test
fun `加载完成后 显示笔记列表`() {
    val viewModel = NotesViewModel(FakeNoteDao().withSeed())

    rule.setContent { NotesScreen(state = collectAs(viewModel.uiState)) }

    rule.waitUntil(timeoutMillis = 5_000) {
        rule.onAllNodesWithTag("noteRow").fetchSemanticsNodes().isNotEmpty()
    }
    rule.onNodeWithText("搜索标题").assertExists()
}
```

- 断言内部已自动等待一轮重组，**只有跨异步边界（网络/Room/延时）才需要 `waitUntil`**；
- 轮询条件必须"可终结"，用元素存在性而非固定 sleep。

## 4️⃣ 常用 API 速览

| 类别 | API | 用途 |
|------|-----|------|
| 匹配 | `onNodeWithText` / `onNodeWithTag` / `onNodeWithContentDescription` | 定位单个节点 |
| 匹配 | `onAllNodesWithTag(...)` | 定位集合，断言数量 |
| 动作 | `performClick` / `performTextInput` / `performScrollToIndex` | 模拟交互 |
| 断言 | `assertIsDisplayed` / `assertTextEquals` / `assertDoesNotExist` | 验证状态 |
| 等待 | `waitUntil` / `mainClock.advanceTimeBy` | 异步与动画时间控制 |

动画测试：`rule.mainClock.advanceTimeBy(300)` 可虚拟推进动画帧，不必等真实时间（配合
[Compose 进阶的动画](../frameworks/02-compose-advanced.md)）。

## 5️⃣ 从组件测试到页面测试

| 层级 | 工具 | 说明 |
|------|------|------|
| 组件 | `createComposeRule` + 注入状态 | 本文主体，秒级反馈 |
| 页面 | `createComposeRule` + Fake ViewModel | 走真实重组与交互流 |
| 全应用 | `createAndroidComposeRule<HiltActivity>` + Hilt 注入 | 见[集成与端到端测试](03-integration-e2e-testing.md) |

## 🎨 最佳实践

UI 测试从用户动作出发：输入、点击，然后检查结果或错误提示。相同文案出现在多行时，先限定父节点或语义范围，必要时补 testTag，而不是依赖偶然的节点顺序。

等待异步状态满足明确条件，并保留超时诊断。语义节点与内容描述有助于无障碍，但测试能找到按钮不等于 TalkBack 已可用；仍需检查朗读顺序、焦点、可点击区域和真实交互。

## 🔗 相关文档

- 📖 概念字典：[Compose 状态 API 详解](../reference/language-concepts/04-compose-state-api.md) ｜ [Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md) ｜ [Compose 测试 API 速查](../reference/framework-essentials/07-compose-testing.md)
- 🧪 同级指南：[单元测试](01-unit-testing.md) ｜ [集成与端到端测试](03-integration-e2e-testing.md)
- 🚀 实战应用：[入门项目的 UI 验收](../projects/01-notes-app.md) ｜ [生产级应用的质量门禁](../projects/04-production-android-app.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
