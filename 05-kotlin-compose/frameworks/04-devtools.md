# 开发工具链 - Android Studio 高效工作流

## 先看框架承担哪部分职责

**Android 工具链**：Preview 验证外观，调试器观察执行，Profiler 观察资源，测试验证行为。一个工具不能代替所有层次的证据。

**最小练习与预期结果**：设置断点查看按钮事件，再旋转设备测试状态；分别记录重组与 Activity 重建，而不是只统计日志行数。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 系统介绍 Android Studio（Quail 2026.1 及更新版本）中 Compose 开发的核心工具：Compose Preview、Layout Inspector、Logcat 与编译器诊断
>
> **目标读者**: 已能跑通 Hello Compose、希望提升日常开发与调试效率的所有学习者
>
> **前置知识**: [环境搭建](../basics/01-environment-setup.md)、[第一个 Compose 应用](../basics/02-first-compose-app.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（frameworks） |
| **难度** | ⭐ |
| **标签** | `#android-studio` `#preview` `#layout-inspector` `#logcat` |
| **更新日期** | `2026年9月` |

</details>

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

Preview 用合成状态展示空数据、加载、错误和长文本，便于不启动真实服务就比较界面。将可预览组件与负责取得 ViewModel 的入口分开，避免预览必须依赖数据库或登录环境。

卡顿使用同一交互的性能记录比较；主线程 I/O 可借助调试工具发现。模拟器适合功能反馈，目标真机负责补充字体、触控、系统权限和性能验证。构建失败先记录完整版本组合和首个相关错误，不反复清缓存来替代排查。

## 🔗 相关文档

- 📖 概念字典：[Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md) ｜ [常见错误与故障排除](../reference/quick-references/02-troubleshooting.md)
- 📖 前置教程：[环境搭建](../basics/01-environment-setup.md) ｜ [第一个 Compose 应用](../basics/02-first-compose-app.md)
- 🚀 后续学习：[Compose 入门核心](01-compose-basics.md) ｜ [性能：启动与内存优化](../advanced-topics/performance/02-startup-memory.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
