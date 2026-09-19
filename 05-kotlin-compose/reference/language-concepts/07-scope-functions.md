# 作用域函数速查

> **阅读准备**：Kotlin lambda、接收者、返回值与可空类型；读代码时先找 it/this 指向谁。

> let / run / apply / also / with 五个作用域函数 + takeIf/takeUnless：临时作用域内访问对象、按"块内引用 + 返回值"选型的字典

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#作用域函数` `#let` `#apply` `#also` `#with` `#run` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

作用域函数是 Kotlin 标准库提供的普通函数，不是关键字或额外的并发机制。先区分块内对象引用和表达式返回值；还要注意调用形式：`with` 接受普通参数，`run` 另有无接收者重载。

1. 块内用 `it`（参数引用）还是 `this`（receiver）
2. 返回 **lambda 结果**还是 **receiver 本身**

选型口诀：**要对象用 apply/also，要结果用 let/run/with；链式传参用 it（let/also），构建配置用 this（apply/run）**。

## 📖 语法与签名

| 函数 | 块内引用 | 返回值 | 典型用途 |
|------|---------|--------|---------|
| `let` | `it` | lambda 结果 | 空安全分支、结果变换 |
| `run` | `this` | lambda 结果 | 计算并产出结果 |
| `run { ... }`（无接收者重载） | 没有额外对象 | lambda 结果 | 在表达式位置组织局部计算 |
| `with` | `this` | lambda 结果 | 对同一对象批量操作（非扩展，普通函数） |
| `apply` | `this` | **receiver** | 对象构建 / 配置（builder 风格） |
| `also` | `it` | **receiver** | 副作用旁路（日志、校验），不打断链 |
| `takeIf` | `it` | 条件为 true 返回 receiver，否则 `null` | 保留符合条件的对象 |
| `takeUnless` | `it` | 条件为 false 返回 receiver，否则 `null` | 排除符合条件的对象 |

下面仅为 API 签名速查，省略函数体，不是独立可编译文件。

```kotlin
inline fun <T, R> T.let(block: (T) -> R): R
inline fun <T, R> T.run(block: T.() -> R): R
inline fun <R> run(block: () -> R): R
inline fun <T, R> with(receiver: T, block: T.() -> R): R
inline fun <T> T.apply(block: T.() -> Unit): T
inline fun <T> T.also(block: (T) -> Unit): T
inline fun <T> T.takeIf(predicate: (T) -> Boolean): T?
inline fun <T> T.takeUnless(predicate: (T) -> Boolean): T?
```

## 💡 示例

下列是 Android 工程中的调用片段，依赖项目自己的 Activity、View 和模型。先学习后面的完整命令行例子，再把这些片段放进实际类中。

```kotlin
// let：空安全 + 变换
user?.let { bindView(it) }                    // 仅在非空时执行

// apply：构建配置（Intent / Bundle / Paint 等）
val intent = Intent(context, DetailActivity::class.java).apply {
    putExtra("id", noteId)
    flags = Intent.FLAG_ACTIVITY_NEW_TASK
}

// also：旁路日志，不打断链
val notes = mutableListOf<Note>().also { log("created: $it") }

// with：同一对象批量操作
with(titleView) { text = title; visibility = VISIBLE }

// 组合：takeIf + let + Elvis 做参数校验
val id = intent.getStringExtra("id")?.takeIf { it.isNotEmpty() } ?: return
```

## ⚠️ 常见陷阱

- `apply` / `run` 块内 `this` 与外层 receiver 同名时易写错对象；嵌套时用 label（`this@outer`）消歧。
- `let` 返回 lambda 结果：块内**最后一行表达式即返回值**，末尾误加一条语句会悄悄改变返回类型。
- 作用域函数嵌套超过两层可读性崩塌——链式场景优先提取具名中间变量。
- `with` 不是扩展函数，可空 receiver 无法 `?.with(...)`——改用 `run` 或先判空。
- 同一条链里混用 `it` 与 `this` 容易混淆引用目标，保持风格一致。

<!-- full-library-explanation -->
## 先看表达式返回什么

```kotlin
fun main() {
    val builder = StringBuilder("A")
    val same = builder.apply { append("B") }
    val length = builder.let { it.length }
    println(same === builder) // true
    println(length)           // 2
    println("  ".takeIf { it.isNotBlank() }) // null
}
```

apply 不复制对象，也不自动切线程；它返回同一接收者。let 的返回值是块最后的表达式，若把最后一行改成 println，结果类型就会变为 Unit。`?.let` 的判空来自 `?.`，不是 let 本身拒绝 null。

练习：把 `loadExpensive().takeIf { enabled }` 改为 enabled 为真才调用加载函数。反馈：takeIf 在接收者已经求值后才执行，不能用它避免之前的昂贵或有副作用调用；明确的 if 往往更合适。

## 可运行练习：返回值、null 与提前执行

把下面保存为 `ScopeContract.kt`，执行 `kotlinc ScopeContract.kt -include-runtime -d scope.jar`，再执行 `java -jar scope.jar`。不需要 Android SDK 或 Compose；此处验证的是 Kotlin 标准库。

```kotlin
fun main() {
    val absent: String? = null
    val direct = absent.let { it == null }
    val safe = absent?.let { it.length }
    check(direct && safe == null)
    val values = mutableListOf(1)
    val same = values.also { it.add(2) }
    check(same === values)
    val sum = with(values) { sum() }
    check(sum == 3)
    check(2.takeIf { it > 0 } == 2)
    check(2.takeUnless { it > 0 } == null)
    var calls = 0
    fun load(): String { calls += 1; return "loaded" }
    val enabled = false
    val tooLate = load().takeIf { enabled }
    check(tooLate == null && calls == 1)
    val lazyChoice = if (enabled) load() else null
    check(lazyChoice == null && calls == 1)
    val label = run { val count = values.size; "items=$count" }
    check(label == "items=2")
    println("scope contracts passed")
}
```

预期输出只有 `scope contracts passed`。`takeIf` 和 `takeUnless` 不会延迟求值，作用域函数也不会复制可变对象；`also` 返回原对象，块内 `add` 会影响原列表。`?.let` 的非空保证来自安全调用符，直接在可空值上调用 `let` 时参数仍可为 null。选择函数时先写普通局部变量版本，再决定缩短后是否仍清楚。

官方参考：[Kotlin 作用域函数](https://kotlinlang.org/docs/scope-functions.html)。内置能力与标准库的后续学习顺序：`require`/`check` 的错误契约、`toIntOrNull` 的失败返回、集合转换、序列、文本与资源管理。不要把常用函数统称为“关键字”。

## 🔗 相关条目

- 📄 [可空性与集合 API](./02-null-safety-collections.md) — `?.let` 组合的空安全语境
- 📄 [扩展函数与扩展属性](./06-extension-functions.md)
- 📄 [Lambda 与高阶函数](./08-lambdas-higher-order.md) — 作用域函数的函数类型本质
- 📄 教程：[Kotlin 语法基础 - 作用域函数速览](../../basics/03-kotlin-syntax-essentials.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
