# Kotlin 高频内置函数：转换、校验、空值与资源边界

> **文档简介**: 把 Kotlin 标准库中最常用的顶层函数与扩展函数按失败语义组织：何时抛异常、何时返回 `null`、何时只做惰性包装，以及它们在 Compose/Android 代码中的边界。

> **前置知识**: [关键词](./01-kotlin-keywords.md)、[空安全与集合](./02-null-safety-collections.md)。集合流水线见 [09-collections-operations.md](./09-collections-operations.md)，作用域函数见 [07-scope-functions.md](./07-scope-functions.md)。

Kotlin 没有一张独立的“所有内置函数表”。高频能力分布在顶层函数、类型扩展函数和标准库类型的方法中。选择函数前先问：失败应当由调用者处理、应当提前终止，还是根本不该发生？不要把名字短的函数当成“更安全”。

## 按失败方式选择

| 需求 | 首选函数 | 成功结果 | 失败语义 |
|---|---|---|---|
| 校验调用者输入 | `require(condition) { message }` | 继续执行 | `IllegalArgumentException` |
| 校验内部状态 | `check(condition) { message }` | 继续执行 | `IllegalStateException` |
| 不存在的分支是程序错误 | `error(message)` | 不返回 | `IllegalStateException` |
| 将文本尝试转数字 | `toIntOrNull`、`toLongOrNull`、`toDoubleOrNull` | 数值 | `null`，不抛格式异常 |
| 为可空值提供默认 | `?:`、`orEmpty()` | 非空值或默认值 | 不区分“缺失”和“默认” |
| 明确要求非空 | `requireNotNull` / `checkNotNull` | 解包后的非空值 | 分别抛参数/状态异常 |
| 在资源结束时清理 | `use` | block 的结果 | 无论 block 是否抛异常都会关闭 `Closeable` |

`!!` 只是在运行时把 `null` 变为 `NullPointerException`，没有增加任何事实。外部输入、可选 UI 状态和异步结果应优先用 `?`、`?:`、显式分支或可恢复错误模型处理；只有不变量已经由更靠近边界的验证建立时，才考虑 `requireNotNull` 或 `checkNotNull`。

## 转换必须保留输入契约

```kotlin
fun parsePage(text: String?): Int? {
    val page = text?.toIntOrNull() ?: return null
    return page.takeIf { it in 1..100 }
}

fun main() {
    println(listOf(null, "0", "2", " 2", "abc", "101").map(::parsePage))
    // [null, null, 2, null, null, null]
}
```

`toIntOrNull()` 解决的是**整数文本能否转换**，不代表业务范围合法。上例把空、格式错误、0 和超过最大页数统一为 `null`；如果产品需要显示不同错误，应返回带原因的 sealed class，而不是继续堆叠 `null`。

### 在本机验收转换语义

把这一段单独保存为 `ParsePage.kt`，不要与下一段的第二个 `main` 拼在同一文件。使用 Kotlin/JVM 工具链执行：

```bash
kotlinc ParsePage.kt -include-runtime -d parse-page.jar
java -jar parse-page.jar
```

应输出 `[null, null, 2, null, null, null]`。把 `toIntOrNull()` 改成 `toInt()` 后再次运行，`"abc"` 应触发 `NumberFormatException`；这证明“可转换”与“范围合法”是两个独立判断，而不是只看到异常就算输入验证完成。

`as?` 也只解决运行时类型是否匹配：`value as? String` 返回 `String?`。它不验证字符串的格式、长度或权限。网络 JSON、Deep Link 与持久化内容要在类型转换后继续校验字段。

## 空值管道与集合函数

```kotlin
data class Draft(val title: String?)

fun normalizedTitles(drafts: List<Draft>): List<String> =
    drafts.mapNotNull { it.title?.trim()?.takeIf(String::isNotEmpty) }

fun main() {
    println(normalizedTitles(listOf(Draft("  Kotlin "), Draft(null), Draft(" "))))
    // [Kotlin]
}
```

`mapNotNull` 会同时变换与丢弃 `null`；若 `null` 表示“同步失败”而非“可忽略字段”，不能静默丢弃，应保留错误记录。`first()` 在空集合抛异常，`firstOrNull()` 返回 `null`；`single()` 还要求恰好一项。选哪一个反映数据不变量，不能为了少写分支一律使用 `first()`。

把这一段单独保存为 `NormalizedTitles.kt`，执行同样的 `kotlinc ... -include-runtime -d normalized-titles.jar` 和 `java -jar normalized-titles.jar`，应输出 `[Kotlin]`。把 `mapNotNull` 暂时替换成 `map`，再比较结果中保留的 `null`/空字符串，说明“清理无效标题”是当前函数的业务选择，而不是集合 API 自动替你决定的数据策略。

`let`、`also`、`run`、`apply`、`with` 都是普通函数，区别是接收者写法和返回值；它们不会自动创建协程、事务或 Compose 状态作用域。链条超过两三步且难以说明当前 `it`/`this` 指向时，改回具名局部变量更可读。

## 资源与惰性

`use` 适用于实现 `Closeable` 的文件、流或其他资源：它在正常返回和异常路径上关闭资源。不要把 Android `Context`、Compose `State` 或协程 `Job` 当作 `Closeable` 强行交给 `use`；它们有自己的生命周期 API。

`lazy { ... }` 首次访问才计算，并缓存成功结果。它适合稳定、无请求态依赖的初始化；若 lambda 读取当前用户、页面参数或可变配置，缓存会把第一次的值错误带到后续使用。Compose 中也不能用普通 `lazy` 替代 `remember`，两者的生命周期不同。

## 练习与验收

为“分页搜索”写一个纯函数：输入 `String? page`、`String? query`，返回合法页号与清理后的查询，或返回有区分原因的失败结果。覆盖空字符串、空白、非数字、0、101、重复空格和正常值；再把 `toIntOrNull` 换成 `toInt`，确认格式错误会从可恢复结果变为异常。若函数在 Compose 屏幕调用，分别说明哪部分是纯解析、哪部分由 UI 显示错误、哪部分应由网络层校验。

本页的示例仅依赖 Kotlin 标准库；尚未在当前主机的 Kotlin 工具链运行。权威 API 定义见 [Kotlin 标准库](https://kotlinlang.org/api/core/kotlin-stdlib/)。
