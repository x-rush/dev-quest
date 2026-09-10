# 开发工具链 - Android Studio 高效工作流

> **文档简介**: 系统介绍 Android Studio（Koala 及更新版本）中 Compose 开发的核心工具：Compose Preview、Layout Inspector、Logcat 与编译器诊断
>
> **目标读者**: 已能跑通 Hello Compose、希望提升日常开发与调试效率的所有学习者
>
> **前置知识**: [环境搭建](../basics/01-environment-setup.md)、[第一个 Compose 应用](../basics/02-first-compose-app.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（frameworks） |
| **难度** | ⭐ |
| **标签** | `#android-studio` `#preview` `#layout-inspector` `#logcat` |
| **更新日期** | `2026年9月` |

---

## 1️⃣ Compose Preview：不跑模拟器看 UI

```kotlin
// 一个函数可叠多个 @Preview，同屏对比不同配置
@Preview(name = "浅色", showBackground = true)
@Preview(name = "深色", uiMode = Configuration.UI_MODE_NIGHT_YES)
@Preview(name = "大字体", fontScale = 1.5f, widthDp = 320)
@Composable
fun ArticleCardPreview() {
    AppTheme {
        ArticleCard(Article(1, "标题", "摘要", 0L))
    }
}
```

**PreviewParameter：一份预览覆盖多种数据形态**

```kotlin
class ArticleProvider : PreviewParameterProvider<Article> {
    override val values = sequenceOf(
        Article(1, "超长标题会怎样呢超长标题会怎样呢", "正常摘要", 0L),
        Article(2, "", "空标题边界", 0L),
    )
}

@Preview
@Composable
fun ArticleCardStates(@PreviewParameter(ArticleProvider::class) article: Article) {
    AppTheme { ArticleCard(article) }
}
```

要点：

- 预览函数必须**无状态、无副作用**——这正是[状态提升](01-compose-basics.md)带来的红利；
- 交互式预览（Interaction Mode）可点击按钮验证简单行为；
- Live Edit 开启后，改代码即时反映到运行中的模拟器/设备。

## 2️⃣ Layout Inspector：看穿运行中的组合

路径：`View → Tool Windows → Layout Inspector`（连接运行中的设备/模拟器）。

| 能力 | 用法 |
|------|------|
| 组件树 | 查看实际组合层次，定位"为什么这个组件没显示" |
| 重组计数 | 打开 "Show recomposition counts"，高亮频繁重组的组件——性能排查第一入口 |
| 属性面板 | 查看每个节点的参数值、modifier 链 |
| 3D 模式 | 检查层叠遮挡关系（Box、自绘、弹层） |

> 重组计数异常偏高时，带着数据去读[重组优化](../advanced-topics/performance/01-recomposition-optimization.md)。

## 3️⃣ Logcat：结构化排查运行问题

新版 Logcat 支持查询语法，比翻滚动条高效得多：

```text
package:com.example.app tag:Compose level:warning    # 组合相关的警告
tag:Choreographer level:warning                      # 掉帧线索（Skipped frames）
message:"Displayed"                                  # 冷启动耗时（ActivityTaskManager 输出）
```

- `Log.d(TAG, ...)` 统一 TAG 规范，避免日志淹没；
- 组合期间禁止打 IO 类日志；确需同步状态时放进 `SideEffect`（见[侧效应](02-compose-advanced.md)）；
- 崩溃堆栈出现 `Recomposer` / `Composition` 字样 → 优先怀疑组合期间异常，速查见
  [常见错误与故障排除](../reference/quick-references/02-troubleshooting.md)。

## 4️⃣ 编译期诊断：Compose Compiler Metrics

Kotlin 2.x 起 Compose 编译器随 Kotlin 发布（`org.jetbrains.kotlin.plugin.compose` 插件），
可开启"可跳过性"报告，把稳定性问题消灭在编码期：

```kotlin
// 模块 build.gradle.kts
composeCompiler {
    metricsDestination = file("${layout.buildDirectory.get()}/compose-metrics")
    reportsDestination = file("${layout.buildDirectory.get()}/compose-reports")
}
```

构建后查看 `*-composables.txt`：`skippable` 标记为 0 的组件，说明其入参存在不稳定类型，
正是重组优化的重点对象（解法见[重组优化](../advanced-topics/performance/01-recomposition-optimization.md)）。

## 5️⃣ 日常提效清单

| 场景 | 工具/操作 |
|------|----------|
| 写 UI | Preview 多配置对比 + Live Edit |
| 查"为什么不显示" | Layout Inspector 组件树 |
| 查"为什么变卡" | Layout Inspector 重组计数 + Compiler Metrics |
| 查崩溃/异常 | Logcat 查询语法 + [故障排除](../reference/quick-references/02-troubleshooting.md) |
| 查启动慢 | Logcat `Displayed` + [启动与内存优化](../advanced-topics/performance/02-startup-memory.md) |
| 查数据流 | 调试器断点在 ViewModel，观察 StateFlow 值变化 |

## 🎨 最佳实践

### ✅ 推荐

- 每个有意义的组件都配 Preview，逐渐积累成"活的设计规范"
- 性能问题先量化（重组计数/指标文件）再动手，不凭感觉优化
- Debug 构建集成 StrictMode，提前暴露主线程 IO 等问题

### ❌ 避免陷阱

- 预览函数里调用 ViewModel 或数据库——预览必然失败，还掩盖了"状态未提升"的设计问题
- 只在模拟器验证：真机的字体缩放、深色模式、性能特征差异很大
- 忽视 Gradle Sync 报错中的版本冲突提示，埋下依赖隐患（常用片段见
  [一行式速查表](../reference/quick-references/01-kotlin-compose-cheatsheet.md)）

## 🔗 相关文档

- 📖 概念字典：[Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md) ｜ [常见错误与故障排除](../reference/quick-references/02-troubleshooting.md)
- 📖 前置教程：[环境搭建](../basics/01-environment-setup.md) ｜ [第一个 Compose 应用](../basics/02-first-compose-app.md)
- 🚀 后续学习：[Compose 入门核心](01-compose-basics.md) ｜ [性能：启动与内存优化](../advanced-topics/performance/02-startup-memory.md)
