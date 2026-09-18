# Kotlin 语法基础 - 面向 Compose 开发者

## 先理解，再动手

Compose 代码常混合 lambda、命名参数和属性委托。先识别“传入一个函数”与“立即调用函数”，再看界面代码。

**本节自测**：写接收 () -> Unit 的函数，分别传 lambda 与错误地直接调用目标函数。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

能解释前者把动作交出去，后者先执行并尝试传返回值；编译信息对应参数类型。

</details>

> **文档简介**: 只讲写 Compose 必需的 Kotlin 语法：可空性、data class、密封类、扩展函数与 lambda，让你能顺畅读懂并书写 Compose 代码
>
> **目标读者**: 有其他语言基础（Go/Java/JS/Python）、Kotlin 经验有限但即将投入 Compose 开发的学习者
>
> **前置知识**: 已运行第一个 Compose 应用（见[第一个 Compose 应用](./02-first-compose-app.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#Kotlin` `#语法基础` `#data-class` `#扩展函数` `#lambda` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 掌握 Kotlin 空安全语法（`?.`、`?:`、`!!`）并理解其设计动机
- ✅ 用 `data class` 与 `sealed interface` 建模 UI 状态
- ✅ 编写与使用扩展函数（Compose 生态大量使用此机制）
- ✅ 读懂 lambda 与尾随 lambda 语法（`Button(onClick = {})` 的原理）
- ✅ 了解作用域函数 `let`/`apply`/`also` 的适用场景

## 📋 目录

- [变量与函数](#-变量与函数)
- [空安全](#️-空安全)
- [data class 与状态建模](#-data-class-与状态建模)
- [sealed interface 与枚举状态](#-sealed-interface-与枚举状态)
- [扩展函数](#-扩展函数)
- [Lambda 与尾随 lambda](#-lambda-与尾随-lambda)
- [作用域函数速览](#-作用域函数速览)
- [练习与实践](#-练习与实践)

---

## 📦 变量与函数

```kotlin
val name = "Compose"      // val：只读引用（推荐默认使用），类型自动推断为 String
var count = 0             // var：可变引用，Compose 中尽量少用

fun add(a: Int, b: Int = 10): Int {   // 参数可带默认值，返回类型在冒号后
    return a + b
}

fun double(x: Int): Int = x * 2       // 单表达式函数：省略 return 与花括号
```

与 Go 的关键差异：类型写在**后面**、用冒号分隔；没有分号；参数默认可空性为**非空**。

---

## 🛡️ 空安全

Kotlin 类型系统在编译期区分可空与非空，这是它相对 Java 最大的安全改进：

```kotlin
var nickname: String? = null     // String? 表示可空类型

// 1. 安全调用 ?.：为 null 时整条表达式返回 null，不抛异常
val length = nickname?.length            // 类型是 Int?

// 2. Elvis 操作符 ?:：为 null 时给默认值
val display: String = nickname ?: "匿名"

// 3. 安全调用 + Elvis 链式组合
val upper: String = nickname?.uppercase() ?: ""

// 4. 非空断言 !!：强行声明"它一定不为 null"，为 null 时抛 NPE——慎用
val forced: String = nickname!!
```

**经验法则**：Compose 中优先用非空类型 + 默认值建模状态，把可空性留给"暂时没有"的语义（如尚未选中的用户）。

---

## 📋 data class 与状态建模

`data class` 自动生成 `equals`/`hashCode`/`toString`/`copy`，是承载 UI 状态的标准载体：

```kotlin
data class Task(
    val id: Long,
    val title: String,
    val done: Boolean = false
)

// copy：基于现有实例生成"改动部分字段"的新实例（不可变更新）
val t1 = Task(id = 1, title = "学 Compose")
val t2 = t1.copy(done = true)

// 解构声明
val (id, title, done) = t2

// data class 的 equals 按字段比较
println(t1 == Task(1, "学 Compose"))   // true
```

为什么 Compose 喜欢 data class：重组时靠 `equals` 快速判断"状态没变就跳过刷新"，见[状态与重组](./04-composables-state.md)。

---

## 🔀 sealed interface 与枚举状态

当一个值只能取有限几种形态时，用 `sealed interface` + `when` 获得编译器穷尽检查：

```kotlin
sealed interface UiState {
    data object Loading : UiState
    data class Success(val tasks: List<Task>) : UiState
    data class Error(val message: String) : UiState
}

fun render(state: UiState): String = when (state) {
    is UiState.Loading -> "加载中"
    is UiState.Success -> "共 ${state.tasks.size} 条任务"
    is UiState.Error   -> "出错了: ${state.message}"
    // 不需要 else 分支——编译器保证覆盖所有子类
}
```

与 `enum` 的区别：enum 的每个值都是单例常量，而 sealed 的子类可以携带不同字段（如 `Error(message)`）。网络/UI 状态建模几乎总是用 sealed。

> 📖 密封类、可见性等修饰符的完整字典见 [Kotlin 关键字详解](../reference/language-concepts/01-kotlin-keywords.md)。

---

## 🧩 扩展函数

扩展函数给既有类型"外挂"新方法，无需继承或修改原类：

```kotlin
// 给 String 添加扩展函数
fun String.truncate(max: Int): String =
    if (length <= max) this else take(max) + "..."

println("Jetpack Compose".truncate(10))   // Jetpack C...

// Compose 生态实例：给 Modifier 链式扩展（这就是 Modifier 的工作原理）
fun Modifier.cardStyle(): Modifier = this
    .padding(8.dp)
    .clip(RoundedCornerShape(12.dp))
```

调用时与成员方法毫无区别，IDE 会用斜体图标提示。阅读 Compose 代码时会遇到大量 `Modifier.xxx()` 扩展与 `Context.toast()` 之类的工具扩展。

---

## 🎯 Lambda 与尾随 lambda

函数在 Kotlin 中是一等公民，函数类型写作 `(参数类型) -> 返回类型`：

```kotlin
val sum: (Int, Int) -> Int = { a, b -> a + b }

// 尾随 lambda：函数的最后一个参数是 lambda 时，可把 lambda 挪到括号外
fun onClick(handler: () -> Unit) { /* ... */ }
onClick { println("clicked") }        // 等价于 onClick(handler = { ... })

// 单参数 lambda 默认命名为 it
listOf(1, 2, 3).map { it * 2 }        // [2, 4, 6]
```

这就是 Compose 组件调用的形态来源：

```kotlin
Button(onClick = { /* 处理点击 */ }) {
    Text("提交")                        // content: @Composable () -> Unit 尾随 lambda
}
```

---

## 🧰 作用域函数速览

五个作用域函数只在"如何引用对象"上有差别，先记最常用的两个：

| 函数 | 引用方式 | 返回值 | 典型场景 |
|------|----------|--------|----------|
| `let` | `it` | lambda 结果 | 空安全分支：`user?.let { ... }` |
| `apply` | `this` | 对象自身 | 构建配置：`Intent().apply { ... }` |
| `also` | `it` | 对象自身 | 附加副作用：日志、登记 |
| `run` | `this` | lambda 结果 | 计算并返回结果 |
| `with` | `this` | lambda 结果 | 对同一对象的连续操作 |

```kotlin
// let + 安全调用：仅当 nickname 非空时执行
nickname?.let { name -> greetingText = "你好, $name" }

// apply：配置对象并返回它自身
val intent = Intent(context, DetailActivity::class.java).apply {
    putExtra("id", taskId)
}
```

---

## 🎯 练习与实践

### 基础练习
- [ ] 写一个 `data class User(name: String, age: Int)`，练习 `copy` 与解构
- [ ] 把一个 `String?` 依次用 `?.`、`?:`、`!!` 三种方式处理，观察编译器提示
- [ ] 为 `List<Int>` 写扩展函数 `fun List<Int>.second(): Int?`，返回第二个元素
- [ ] 用 `when` + `sealed interface` 表达"表单校验状态"：空 / 校验中 / 通过 / 失败(原因)

### 进阶挑战
- [ ] 不查资料，解释 `Button(onClick = { ... }) { Text("OK") }` 中两个 lambda 各自对应哪个参数
- [ ] 用 `apply` 重写一段"创建后逐个 set 属性"的 Java 风格代码
- [ ] 思考：为什么 Compose 中的 UI 状态推荐 `data class` + `val`，而不是一堆 `var`？（提示：equals 与重组）

---

## 🔗 相关文档

- 📄 **[Kotlin 关键字与修饰符详解](../reference/language-concepts/01-kotlin-keywords.md)** - suspend/sealed/inline 等完整字典
- 📄 **[可空性与集合 API](../reference/language-concepts/02-null-safety-collections.md)** - 集合操作符全表
- 📄 **[泛型与委托属性](../reference/language-concepts/05-generics-delegates.md)** - `by lazy`、`by viewModels` 的原理
- 📄 **[扩展函数与扩展属性](../reference/language-concepts/06-extension-functions.md)** - 解析规则与 Modifier 链原理
- 📄 **[作用域函数](../reference/language-concepts/07-scope-functions.md)** - let/run/apply/also/with 选型表
- 📄 **[Lambda 与高阶函数](../reference/language-concepts/08-lambdas-higher-order.md)** - 尾随 lambda 与带接收者 lambda 全解
- 📄 **[Composable 与状态](./04-composables-state.md)** - 下一篇：把 Kotlin 语法用到 Compose 状态管理中


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
