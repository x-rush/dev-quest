# Composable 与状态 - 声明式 UI 的核心

## 先理解，再动手

remember 负责保留值，mutableStateOf 负责被观察的读写。重组重复计算界面描述，不应该在计算过程中发请求或改业务数据。

**本节自测**：加入重置按钮，再把同一状态传给两个子组件。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

两处数字一致；旋转后是否保留取决于状态保存方式，不能把 remember 当数据库。

</details>

> **文档简介**: 理解 Jetpack Compose 的心脏机制：`@Composable` 函数如何响应 `remember`/`mutableStateOf` 状态变化并自动重组（recomposition），以及状态提升（State Hoisting）设计模式
>
> **目标读者**: 已能跑通 Compose 项目、想搞懂"为什么改个变量界面就会刷新"的开发者
>
> **前置知识**: [Kotlin 语法基础](./03-kotlin-syntax-essentials.md)（lambda、data class）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#Composable` `#State` `#Recomposition` `#状态提升` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 理解 `UI = f(state)` 的声明式模型
- ✅ 使用 `remember { mutableStateOf(...) }` 创建可观察状态
- ✅ 解释重组的触发条件、范围与跳过机制
- ✅ 掌握状态提升模式，写出可复用的无状态组件
- ✅ 识别"在组合期间写状态"导致的死循环

## 📋 目录

- [什么是 @Composable](#-什么是-composable)
- [第一个可交互组件：计数器](#-第一个可交互组件计数器)
- [重组 Recomposition](#-重组-recomposition)
- [remember 与状态持久性](#-remember-与状态持久性)
- [状态提升](#️-状态提升)
- [常见误区](#️-常见误区)
- [练习与实践](#-练习与实践)

---

## 🧠 什么是 @Composable

`@Composable` 不是一个类，只是函数上的注解，但它改变了函数的能力：

```kotlin
@Composable
fun MessageCard(name: String) {
    Text("Hello, $name")
}
```

三条心智规则：

1. **函数即 UI**: 调用 `MessageCard("Ada")` 就是把它的内容"挂"到界面树上，可任意嵌套组合
2. **幂等可重入**: Compose 可能随时重新调用这个函数（重组），同一输入应产生同一界面——所以不要在函数体内写副作用（弹 toast、改数据库）
3. **顺序执行**: 函数体按顺序描述界面，类似"DSL 形式的布局文件"

> 💡 与 React 类比：`@Composable` ≈ 函数组件，`Modifier` ≈ props 中的样式，重组 ≈ re-render。

---

## 🔢 第一个可交互组件：计数器

直接用普通变量"记"状态是无效的，看正确写法：

```kotlin
@Composable
fun Counter() {
    // remember：让值跨重组存活；mutableStateOf：让值的变化可被 Compose 观察
    var count by remember { mutableStateOf(0) }

    Column {
        Text("点击了 ${count} 次")
        Button(onClick = { count++ }) {
            Text("点我")
        }
    }
}
```

运行后每点一次按钮，文本自动更新。这背后发生了什么：

1. `count++` 改变了 `MutableState` 的值
2. Compose 观察到"读取该状态的 Composable"需要更新
3. 重新执行 `Counter()` 函数体（重组），`Text` 拿到新的 `count` 渲染
4. `remember` 返回缓存中的同一状态对象，而不是重新初始化为 0

`by` 委托语法让我们直接读写 `.value`，比 `count.value++` 简洁（详见[泛型与委托属性](../reference/language-concepts/05-generics-delegates.md)）。

---

## 🔄 重组 Recomposition

**定义**: 状态变化后，Compose 重新执行受影响的 Composable 函数以更新界面树的过程。

关键特性：

| 特性 | 说明 |
|------|------|
| **智能范围** | 使读取状态的相关重组作用域失效；实际执行与跳过还取决于编译器、稳定性和读取位置 |
| **可跳过** | 符合跳过条件的 Composable 可能被跳过；比较与稳定性规则取决于编译配置，不能据此保证执行次数 |
| **可能频繁** | 动画、滚动、输入每帧都可能触发，因此 Composable 应轻量 |
| **顺序不定** | 不要依赖多个 Composable 的执行顺序，也不要依赖重组次数 |

```kotlin
@Composable
fun Profile(name: String, age: Int) {
    Column {
        Header(name)              // 若 name 没变，Header 可被跳过
        AgeBadge(age)             // 若 age 变了，只有它重新执行
    }
}
```

> 📖 状态 API（`State`/`derivedStateOf`/`snapshotFlow` 等）的完整字典见 [Compose 状态 API 详解](../reference/language-concepts/04-compose-state-api.md)。

---

## 💾 remember 与状态持久性

`remember` 的作用域是"该组件在界面树上的存在期"：

```kotlin
var query by remember { mutableStateOf("") }                    // 重组间存活
var query2 by rememberSaveable { mutableStateOf("") }           // 还能存活于配置变更/进程恢复
```

- **`remember`**: 重组不丢，但旋转屏幕、进程被杀后丢失
- **`rememberSaveable`**: 自动把值写入 `Bundle`，能扛住配置变更（需可序列化类型）
- **ViewModel**: 需要跨配置变更且包含业务逻辑的状态可放到 ViewModel；ViewModel 本身不保证进程重建后恢复（见[协程与 Flow 基础](./07-coroutines-flow-basics.md)）

一个常见递进：简单 UI 状态用 `remember` → 需要跨配置变更 → `rememberSaveable` → 涉及业务 → ViewModel + `StateFlow`。

---

## ⬆️ 状态提升

**原则**: 把状态从子组件"提升"到调用方，子组件变成无状态（stateless）组件。

```kotlin
// ❌ 有状态组件：内部锁死状态，难以复用与测试
@Composable
fun NameInputBad() {
    var name by remember { mutableStateOf("") }
    OutlinedTextField(value = name, onValueChange = { name = it })
}

// ✅ 无状态组件：状态由外部传入，事件向上回调
@Composable
fun NameInput(
    name: String,                          // 状态下行（参数）
    onNameChange: (String) -> Unit,        // 事件上行（回调）
    modifier: Modifier = Modifier
) {
    OutlinedTextField(
        value = name,
        onValueChange = onNameChange,
        modifier = modifier
    )
}

// 调用方持有状态，可同时服务多个场景（预览、表单、撤销栈……）
@Composable
fun Form() {
    var name by remember { mutableStateOf("") }
    NameInput(name = name, onNameChange = { name = it })
}
```

这就是 **单向数据流（UDF）**: 状态向下流动、事件向上传递。后续 ViewModel + StateFlow 的架构正是这个模式在页面级的放大。

---

## ⚠️ 常见误区

### 误区一：在组合期间写状态 → 无限重组死循环

```kotlin
@Composable
fun Broken() {
    var count by remember { mutableStateOf(0) }
    count++          // ❌ 组合中直接改状态：改完触发重组 → 再改 → 死循环崩溃
    Text("$count")
}
```

修正：由事件、业务状态持有者或合适的副作用 API 发起变化，避免在描述 UI 时直接写入自己正在读取的状态。

### 误区二：普通变量当状态用

```kotlin
@Composable
fun AlsoBroken() {
    var count = 0                     // ❌ 每次重组都重新初始化为 0，界面永远不变
    Button(onClick = { count++ }) { Text("$count") }
}
```

### 误区三：副作用直接写在函数体里
发送网络请求、写数据库等操作请放入 `LaunchedEffect`/ViewModel，明确工作生命周期：LaunchedEffect 在进入组合及 key 改变时启动，离开组合时取消；ViewModel 的工作遵循自身作用域。

> 更多疑难现象（重组死循环、状态丢失、协程泄漏）的排查手册见[故障排除速查](../reference/quick-references/02-troubleshooting.md)。

---

## 🎯 练习与实践

### 基础练习
- [ ] 复现计数器，并新增"重置"按钮把 count 归零
- [ ] 把计数器改造成无状态组件 `Counter(count: Int, onIncrement: () -> Unit)`，在父组件中持有状态
- [ ] 用 `OutlinedTextField` + `remember` 实现一个"输入即显示字数"的组件
- [ ] 把计数器的 `remember` 换成 `rememberSaveable`，旋转屏幕对比状态是否保留

### 进阶挑战
- [ ] 实现一个待办输入框：状态为 `data class Draft(val title: String, val done: Boolean)`，验证输入后界面正确刷新
- [ ] 故意写出组合期间写状态的死循环代码，观察 Logcat 报错信息并记录修复方法
- [ ] 用两个并排的 `NameInput` 共享同一个状态源，体会状态提升带来的复用性

---

## 🔗 相关文档

- 📄 **[Compose 状态 API 详解](../reference/language-concepts/04-compose-state-api.md)** - State/remember/derivedStateOf 完整字典
- 📄 **[布局系统](./05-layouts.md)** - 把状态组件放进 Column/LazyColumn
- 📄 **[Compose 核心组件速查](../reference/framework-essentials/01-compose-essentials.md)** - TextField/Button 等组件参数速查
- 📖 **[State and Jetpack Compose](https://developer.android.com/develop/ui/compose/state)** - 官方状态文档


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
