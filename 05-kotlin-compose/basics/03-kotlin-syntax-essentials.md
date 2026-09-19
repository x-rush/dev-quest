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
> **前置知识**: 会变量、函数与条件判断即可。先用 Kotlin/JVM 学本页语言语义，再到[第一个 Compose 应用](./02-first-compose-app.md)；Compose 片段需要 Android 工程，不能放进普通 JVM 文件。

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

类型写在变量名后面，用冒号分隔；分号通常可以省略；`String` 与 `String?` 是不同类型。`val` 只禁止重新赋值，不保证其引用的列表或对象不可变；`var` 本身也不会触发 Compose 重组，界面要观察 `State`、`StateFlow` 等状态容器。

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

// copy：生成修改了部分构造属性的新实例；这是浅拷贝
val t1 = Task(id = 1, title = "学 Compose")
val t2 = t1.copy(done = true)

// 解构声明
val (id, title, done) = t2

// 默认 equals 比较主构造函数中的属性，不包含类体里另声明的属性
println(t1 == Task(1, "学 Compose"))   // true
```

`data class` 适合把相关状态作为一个值传递，但它不自动让对象不可变，也不保证 Compose 跳过重组。`copy` 内含的可变列表仍共享；Compose 是否跳过还取决于状态观察、参数稳定性与编译器模式。先做到“创建新状态后交给可观察容器”，再根据性能证据优化。参见 [Kotlin data class 规则](https://kotlinlang.org/docs/data-classes.html) 和 [Compose strong skipping](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping)。

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

`enum` 的每个条目是固定实例，也可以声明属性和方法；`sealed` 的不同子类型可以拥有不同结构和任意多个实例，例如不同错误消息。只有固定选项时用 enum；不同状态所需的数据不同，用 sealed 可以减少无效组合。

> 📖 密封类、可见性等修饰符的完整字典见 [Kotlin 关键字详解](../reference/language-concepts/01-kotlin-keywords.md)。

---

## 🧩 扩展函数

扩展函数给既有类型"外挂"新方法，无需继承或修改原类：

```kotlin
// 给 String 添加扩展函数
fun String.truncate(max: Int): String {
    require(max >= 0) { "max must be non-negative" }
    return if (length <= max) this else take(max) + "..."
}

println("Jetpack Compose".truncate(10))   // Jetpack Co...

// Compose 生态实例：给 Modifier 链式扩展（这就是 Modifier 的工作原理）
fun Modifier.cardStyle(): Modifier = this
    .padding(8.dp)
    .clip(RoundedCornerShape(12.dp))
```

扩展函数的调用外形像成员，但它按接收者的声明类型静态解析，不能覆盖真正成员，也不能访问类的私有成员。这里的 `length`/`take` 按 UTF-16 单元计数，不能作为面向任意 emoji 的用户可见截断器。规则见 [Kotlin 扩展文档](https://kotlinlang.org/docs/extensions.html)。

---

## 🎯 Lambda 与尾随 lambda

函数在 Kotlin 中是一等公民，函数类型写作 `(参数类型) -> 返回类型`：

```kotlin
val sum: (Int, Int) -> Int = { a, b -> a + b }

// 尾随 lambda：函数的最后一个参数是 lambda 时，可把 lambda 挪到括号外
fun onClick(handler: () -> Unit) { handler() }
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

作用域函数同时区别接收者写法、返回值与调用形式；不要只记 `this`/`it` 而忽略表达式的最终结果：

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

### 一个不用 Android 的完整验收程序

保存为 `Main.kt`，运行 `kotlinc Main.kt -include-runtime -d main.jar`、`java -jar main.jar`。下面的断言把 `val`、浅拷贝、默认值和回调时序放在一起，任何错误都会使程序失败。只有此完整程序绑定到[本轮运行证据](../../shared-resources/tools/document-quality/reports/kotlin-swift-core-validation.md)，上面的界面片段仍需在 Compose 工程验收。

<!-- dq-case: kotlin-syntax-contracts -->
```kotlin
data class Draft(val title: String, val tags: MutableList<String>)

fun normalizeTitle(raw: String?): String? = raw?.trim()?.takeIf { it.isNotEmpty() }
fun runAction(action: () -> Unit) { action() }

fun main() {
    val original = Draft("read", mutableListOf("kotlin"))
    val shallow = original.copy(title = "write")
    shallow.tags.add("shared")
    check(original.title == "read")
    check(original.tags == listOf("kotlin", "shared"))
    val detached = original.copy(tags = original.tags.toMutableList())
    detached.tags.clear()
    check(original.tags.size == 2)
    check(normalizeTitle(null) == null)
    check(normalizeTitle("   ") == null)
    check(normalizeTitle(" learn ") == "learn")
    var calls = 0
    val callback: () -> Unit = { calls += 1 }
    check(calls == 0)
    runAction(callback)
    check(calls == 1)
    // runAction(callback()) 不编译：callback() 已执行并返回 Unit，不是函数。
    println("Kotlin syntax contracts passed")
}
```

### 基础练习
- [ ] 写一个 `data class User(name: String, age: Int)`，练习 `copy` 与解构
- [ ] 把一个 `String?` 依次用 `?.`、`?:`、`!!` 三种方式处理，观察编译器提示
- [ ] 为 `List<Int>` 写扩展函数 `fun List<Int>.second(): Int?`，返回第二个元素
- [ ] 用 `when` + `sealed interface` 表达"表单校验状态"：空 / 校验中 / 通过 / 失败(原因)

### 进阶挑战
- [ ] 不查资料，解释 `Button(onClick = { ... }) { Text("OK") }` 中两个 lambda 各自对应哪个参数
- [ ] 用 `apply` 重写一段"创建后逐个 set 属性"的 Java 风格代码
- [ ] 给 `Draft` 的 `tags` 增加元素，解释为什么 `copy` 后原对象也变了；然后改为传入独立列表，并通过上面的断言。

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
