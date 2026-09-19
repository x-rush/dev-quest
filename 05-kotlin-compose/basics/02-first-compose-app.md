# 第一个 Compose 应用 - 从零到运行

## 先理解，再动手

Activity 是系统入口，setContent 建立 Compose 界面内容。Composable 描述界面，Preview 帮助预览但不能代替真实生命周期。

**本节自测**：把欢迎文本换成按钮，点击后显示次数。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

设备上可交互；只在 Preview 看见按钮不代表运行时行为已验证。

</details>

> **文档简介**: 创建你的第一个 Jetpack Compose 项目，理解 Composable 函数、`setContent` 入口与 `@Preview`，并厘清 Compose 与传统 View 体系的关系
>
> **目标读者**: 已完成环境搭建的 Android 初学者，希望快速看到声明式 UI 跑起来的开发者
>
> **前置知识**: 已安装 Android Studio 与模拟器（见[环境搭建](./01-environment-setup.md)）；了解基本编程概念

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#Jetpack-Compose` `#Composable` `#Preview` `#声明式UI` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 通过官方模板创建一个 Compose 项目并跑在模拟器上
- ✅ 理解 Compose 项目的目录结构与关键依赖
- ✅ 编写自己的第一个 `@Composable` 函数
- ✅ 使用 `@Preview` 在 IDE 中实时预览 UI
- ✅ 理解 Compose 与传统 XML View 体系的关系

## 📋 目录

- [创建 Compose 项目](#-创建-compose-项目)
- [项目结构解析](#-项目结构解析)
- [编写第一个 Composable](#️-编写第一个-composable)
- [用 @Preview 实时预览](#-用-preview-实时预览)
- [Compose 与传统 View 的关系](#-compose-与传统-view-的关系)
- [常见问题](#-常见问题)
- [练习与实践](#-练习与实践)

---

## 🚀 创建 Compose 项目

1. Android Studio 欢迎页点击 **New Project**。
2. 模板选择 **Empty Activity**（新版本 Studio 中默认模板即 Compose，注意不要选带 Views 字样的模板）。
3. 填写配置：
   - **Name**: `HelloCompose`
   - **Package name**: `com.example.hellocompose`
   - **Minimum SDK**: 选择 API 24 及以上（覆盖绝大多数设备，且 Compose 支持良好）
4. 点击 Finish，等待首次 Gradle Sync 完成（可能需要几分钟下载依赖）。

> 💡 不要选 "Empty Views Activity"——那是传统 XML 模板。名字里没有 Compose 字样的模板要注意区分。

---

## 📁 项目结构解析

创建完成后，重点看这几个文件：

```text
HelloCompose/
├── app/
│   ├── build.gradle.kts            # 模块级构建脚本（依赖都在这里）
│   └── src/main/
│       ├── java/com/example/hellocompose/
│       │   └── MainActivity.kt     # 入口 Activity
│       └── res/values/
│           └── strings.xml         # 字符串资源
├── gradle/libs.versions.toml       # 版本目录（统一管理依赖版本）
└── build.gradle.kts                # 项目级构建脚本
```

打开 `app/build.gradle.kts`，确认这几个关键配置（模板已自动生成）：

```kotlin
android {
    buildFeatures {
        compose = true   // 开启 Compose 编译支持
    }
}

dependencies {
    // Compose BOM：统一管理所有 Compose 库版本，只升 BOM 即可
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.material3)
    implementation(libs.androidx.ui.tooling.preview)
}
```

> 💡 自 Kotlin 2.x 起，Compose 编译器已随 Kotlin 发行（Kotlin 编译器插件化），项目级脚本会应用 `org.jetbrains.kotlin.plugin.compose` 插件，不再需要手动匹配 Compose 编译器版本——这是老教程中常见的坑。

---

## ✍️ 编写第一个 Composable

打开 `MainActivity.kt`，逐段理解模板代码：

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {                       // Compose 的入口：不调用 setContentView
            HelloComposeTheme {            // Material 主题包裹
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    Greeting("Android")
                }
            }
        }
    }
}

@Composable                 // 声明这是一个 Composable 函数
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello, $name!",
        modifier = modifier
    )
}
```

**关键概念**：

- **`setContent {}`**: 用 Compose 内容树替换传统的 `setContentView(R.layout.xxx)`，整个 UI 由 Kotlin 函数描述
- **`@Composable` 函数**: UI 的基本单元，类似 React 组件——接收数据、描述界面，可嵌套组合
- **`Modifier`**: 每个组件的可选修饰符参数，控制尺寸、边距、点击等（详见[布局](./05-layouts.md)）

---

## 👀 用 @Preview 实时预览

在任何 `@Composable` 函数上方添加 `@Preview`，即可在 IDE 中预览而无需启动模拟器：

```kotlin
@Preview(showBackground = true, name = "问候语预览")
@Composable
fun GreetingPreview() {
    HelloComposeTheme {          // 预览中手动套用主题
        Greeting("Android")
    }
}
```

操作要点：
1. 编辑器右侧打开 **Split** 或 **Design** 视图，预览自动渲染
2. 修改字符串（如改为 `"Compose"`），预览即时刷新
3. 点击预览中的图标可进入交互式预览（Interactive Preview），能直接点击按钮

> ⚠️ `@Preview` 供 Android Studio 的设计工具调用，不能当作设备运行或生命周期验证；带注解的 Kotlin 函数仍会参与应用代码的编译。预览中应自行提供主题，否则会使用默认样式。

---

## 🔄 Compose 与传统 View 的关系

如果你接触过老教程（XML + Activity），需要厘清两者的关系：

| 维度 | 传统 View 体系 | Jetpack Compose |
|------|----------------|-----------------|
| UI 描述 | XML 布局文件 + findViewById/ViewBinding | 纯 Kotlin 函数 |
| UI 更新 | 手动调用 `setText()` 等命令式方法 | 状态变化自动重组（recomposition） |
| 组件来源 | `android.widget.*`、`androidx.*` | `androidx.compose.*` |
| 复用方式 | 自定义 View / include 标签 | 函数组合 |
| 现状 | 维护模式，存量项目大量使用 | 官方推荐，新项目默认选择 |

**三点认知**：

1. **两者可共存**: Compose 可通过 `ComposeView` 嵌入既有 XML 页面，也可用 `AndroidView` 反向包装老控件——迁移是渐进的
2. **底层仍依赖框架**: Compose 最终仍运行在 Android 框架之上，Activity、生命周期等概念依然存在
3. **声明式是核心差异**: 你描述"UI 在某状态下长什么样"，而不是"如何一步步改 UI"——这与 React、SwiftUI 是同一种思维（详见[状态与重组](./04-composables-state.md)）

---

## ❓ 常见问题

### Q1: Preview 面板一片空白或报错？
**A**: ① 确认依赖中有 `ui-tooling-preview` 与 debug 实现 `ui-tooling`；② 预览函数里是否用到了需要真机环境的 API（如 `LocalContext.current` 加载资源）——把这类逻辑移到子 Composable 中，预览只渲染纯 UI。

### Q2: 运行报错 "CompositionLocal ... not present"？
**A**: 通常是 Compose 库版本混用（部分库绕过 BOM 引入了不同版本的底层库）。检查 `build.gradle.kts`，确保所有 Compose 依赖都通过 BOM 引入、不带单独版本号。

### Q3: 模板里 `Greeting` 的第二个参数 `modifier: Modifier = Modifier` 是干什么的？
**A**: 这是 Compose 的约定惯例：让调用方可以从外部定制组件的布局行为（边距、尺寸等），默认值为空 Modifier。自己写组件时请保持这个参数签名。

---

## 🎯 练习与实践

### 基础练习
- [ ] 创建 `HelloCompose` 项目并在模拟器上运行成功
- [ ] 把 `Greeting` 的文本改为你自己的名字，观察预览与模拟器同步变化
- [ ] 新增一个 `@Composable fun ShowText(text: String)`，在 `setContent` 中调用它显示一段自我介绍
- [ ] 为 `Greeting` 添加 `modifier = Modifier.padding(16.dp)`，观察布局变化

### 进阶挑战
- [ ] 组合 `Text` 与 `Button` 到一个 `Column` 中（可先照抄文档示例，下一课会系统讲）
- [ ] 给同一个 Composable 写两个不同参数的 `@Preview`，并用 `@Preview(widthDp = 320)` 模拟小屏效果
- [ ] 运行应用后打开 `Layout Inspector`，观察 Compose 节点树与传统 View 树的差异

---

## 🔗 相关文档

- 📄 **[Kotlin 语法基础](./03-kotlin-syntax-essentials.md)** - 补齐阅读 Compose 代码所需的 Kotlin 知识
- 📄 **[Composable 与状态](./04-composables-state.md)** - 理解声明式 UI 的核心机制：状态与重组
- 📄 **[Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md)** - 常用组件字典式索引
- 📖 **[Jetpack Compose Basics Codelab](https://developer.android.com/codelabs/jetpack-compose-basics)** - 官方入门教程


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
