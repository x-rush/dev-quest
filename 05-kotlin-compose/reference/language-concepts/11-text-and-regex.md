# 字符串 API 与正则导览

> **阅读准备**：Kotlin String、转义与可空返回；复杂校验先明确整串匹配还是提取一段。

> String 高频方法、模板与转义、原始字符串、Regex 全家桶（matches/find/findAll/命名分组/RegexOption）、格式化——本模块正则的完整参考

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#String` `#Regex` `#字符串模板` `#格式化` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

本页主要讨论 Kotlin/JVM 字符串及标准库扩展；其他 Kotlin 目标不能直接等同于 java.lang.String：高频操作（split/trim/replace/substringBefore…）全部以扩展函数提供，无需 `StringUtils` 类工具库；正则通过 `Regex` 类封装，API 比 Java `Pattern`/`Matcher` 的分离式设计更直接。下文注释为预期结果；本轮未在 Kotlin/Android 工具链运行。

## 先完成一个严格的时间字段解析器

前置：能写函数、理解 `String?` 和提前 `return`。产物是一份独立的 `Main.kt`，只依赖 Kotlin 标准库，不依赖 Android 或 Compose。输入约定为 ASCII 的 `HH:mm:ss`；输出为当天经过的秒数，非法输入返回 `null`。本练习不自动 trim，空格也属于格式错误。

先拆成两个判断：`matchEntire` 确认整个字段形状，再用范围确认时间含义。若用 `find`，`日志 09:05:30` 也会成功，违反“整个字段”的输入契约。[官方 matchEntire API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.text/-regex/match-entire.html) 明确规定不匹配时返回 `null`。

```kotlin
private val clockField = Regex("""([0-9]{2}):([0-9]{2}):([0-9]{2})""")

fun secondsSinceMidnight(input: String): Int? {
    val match = clockField.matchEntire(input) ?: return null
    val (hourText, minuteText, secondText) = match.destructured
    // 每组已限定为两位 ASCII 数字，转换不会溢出。
    val hour = hourText.toInt()
    val minute = minuteText.toInt()
    val second = secondText.toInt()
    if (hour !in 0..23 || minute !in 0..59 || second !in 0..59) return null
    return hour * 3600 + minute * 60 + second
}

fun main() {
    val cases = listOf("09:05:30", "00:00:00", "23:59:59",
        "24:00:00", "09:60:00", "9:05:30", "日志 09:05:30", "")
    cases.forEach { println("[$it] -> ${secondsSinceMidnight(it)}") }
    check(secondsSinceMidnight("09:05:30") == 32730)
    check(secondsSinceMidnight("24:00:00") == null)
}
```

在已安装 JDK 与 Kotlin/JVM 编译器的终端运行 `kotlinc Main.kt -include-runtime -d clock.jar`，再运行 `java -jar clock.jar`。依次预期得到 `32730`、`0`、`86399`，后五项均为 `null`。这些是人工推导的验收值；本次没有执行 Kotlin 编译或 Android 运行。

失败时按层回查：命令不存在先回环境安装；所有合法值都为 null 时检查原始字符串是否误写成双反斜杠；日志前缀也成功时检查是否用了 `find`；`24:00:00` 成功时检查数值范围层。接着将输入改成 `09:05:30 `，说明“允许空白”应是显式产品决策，而不是偷偷修改解析契约。正文的日志提取函数用途不同，它允许在长文本中找一段时间。

## 📖 语法 / API 表

### 1. 高频 String 方法

| 方法 | 一行语义 | 最小示例 |
|------|---------|---------|
| `trim()` / `trim(vararg chars)` | 去首尾空白/指定字符 | `"  hi ".trim()` → `"hi"`；`"xxhixx".trim('x')` → `"hi"` |
| `split(vararg delimiters)` | 按分隔符拆分，**保留空串（含尾空串）** | `"a,b,,c".split(",")` → `[a, b, , c]` |
| `substring(start, end)` | 按下标截取，end 不含 | `"abcdef".substring(2, 4)` → `"cd"` |
| `substringBefore/After(d)` | 取首个分隔符前/后子串 | `"hello.txt".substringBefore('.')` → `"hello"` |
| `substringBeforeLast/AfterLast(d)` | 取**最后一个**分隔符前/后 | `"hello.txt".substringAfterLast('.')` → `"txt"` |
| `replace(old, new)` | 全量替换 | `"hello".replace("l", "L")` → `"heLLo"` |
| `replaceFirst(old, new)` | 只替换首次出现 | `"a-b-c".replaceFirst('-', '_')` → `"a_b-c"` |
| `startsWith/endsWith` | 前缀/后缀判断 | `"img.png".endsWith(".png")` → true |
| `lowercase/uppercase` | 大小写转换 | `"Report.PDF".lowercase()` → `"report.pdf"` |
| `replaceFirstChar` | 首字符变换（旧 `capitalize` 已废弃） | `"kotlin".replaceFirstChar { it.uppercaseChar() }` → `"Kotlin"` |
| `isEmpty` / `isBlank` | 长度为 0 / 全空白 | `"  ".isBlank()` → true |
| `orEmpty()` | `String?` → `String`（null 变空串） | `nullableName.orEmpty().length` |

```kotlin
"2026-09-14".split("-")                 // [2026, 09, 14]
"abcdef".substring(3)                   // def（省略 end = 到末尾）
(null as String?).orEmpty().isEmpty()   // true
```

### 2. 字符串模板与转义

规则（预期行为确认）：**`$` 后跟标识符或 `{` 才是模板**，否则按字面量处理。

```kotlin
val name = "Ada"
"Hi, $name (${name.length} chars)"   // Hi, Ada (3 chars)——$标识符 与 ${表达式}
"sum=${1 + 2}"                       // sum=3
"cost: \$5"                          // cost: $5——\$ 转义字面量 $
"$5"                                 // $5——$ 后跟数字不是模板，按字面量（预期行为）
"100$"                               // 100$——$ 结尾同理
"""${'$'}"""                         // $——原始字符串里输出 $ 的标准写法
"a\tb"                               // 转义序列同 Java：\t \n \\ \" A → A
```

### 3. 原始字符串（Raw String）

```kotlin
"""a\nb""".length                    // 4——反斜杠不转义，\n 是两个字符（预期行为）
"""C:\Users\new"""                   // Windows 路径免双反斜杠
val json = """{"name": "Ada"}"""     // 内嵌引号无需转义
"""
    line1
    line2
""".trimIndent()                     // → "line1\nline2"（去公共缩进）
"""
    >a
    >b
""".trimMargin(">")                  // → "a\nb"（去缩进 + 去前缀）
```

### 4. Regex 全家桶

| API | 一行语义 | 最小示例 |
|------|---------|---------|
| `Regex(pattern)` / `"\\d+".toRegex()` | 构造；pattern 用原始字符串免双反斜杠：`Regex("""\d+""")` | — |
| `matches(input)` | **整串**匹配 | `Regex("\\d+").matches("123")` → true；`matches("a123")` → false |
| `containsMatchIn(input)` | 含有任一匹配 | `Regex("\\d+").containsMatchIn("ab123")` → true |
| `find(input)` | 第一个匹配 → `MatchResult?` | `Regex("\\d+").find("ab123cd456")?.value` → `"123"` |
| `findAll(input)` | 全部匹配 → **惰性 Sequence** | `findAll("ab123cd456").map { it.value }.toList()` → `[123, 456]` |
| `replace(input, 字符串或变换lambda)` | 全量替换 | `Regex("\\d+").replace("a1b22c", "#")` → `"a#b#c"` |
| `replaceFirst` | 只替换第一处 | — |
| `String.split(regex)` | 按正则拆分（保留尾空串） | `"ab12cd3".split(Regex("\\d+"))` → `[ab, cd, ]` |

匹配结果取值（预期行为）：

```kotlin
val dateRe = Regex("""(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})""")
val m = dateRe.find("发布于 2026-09-14")!!
m.groups["year"]?.value        // 2026——命名分组（Kotlin 1.7+ 支持 groups["name"]）
m.groups[1]?.value             // 2026——按序号取
m.destructured.toList()        // [2026, 09, 14]——全部捕获组
```

选项（`RegexOption`，注意**没有 `g` 标志**——全局匹配就是 `findAll`）：

```kotlin
Regex("kotlin", RegexOption.IGNORE_CASE).matches("KOTLIN")   // true
Regex("a.b", setOf(RegexOption.DOT_MATCHES_ALL, RegexOption.IGNORE_CASE))
    .matches("A\nB")                                          // true——DOT_MATCHES_ALL 让 . 匹配换行
Regex("^a", RegexOption.MULTILINE).containsMatchIn("x\na")    // true——^/$ 逐行生效
```

### 5. 格式化

| 形式 | 说明 |
|------|------|
| `String.format("%.2f", x)` | Java 风格静态调用 |
| `"%.2f".format(x)` | Kotlin 扩展，等价上一行 |
| `String.format(Locale.US, "%.2f", x)` | **显式区域**，行为确定 |

| 占位符 | 语义 | 示例（Locale.US） |
|--------|------|-------------------|
| `%s` / `%d` | 字符串 / 整数 | `"%d 项 / %s".format(3, "ok")` → `"3 项 / ok"` |
| `%.2f` | 浮点保留 2 位小数 | `3.14159` → `"3.14"` |
| `%05d` | 宽度 5，0 填充 | `42` → `"00042"` |
| `%,d` | 千分位分组 | `1234567` → `"1,234,567"` |

```kotlin
val price = String.format(java.util.Locale.US, "$%.2f", 9.5)     // "$9.50"——$ 后跟 % 非模板，按字面量（预期行为）
```

## 💡 示例

解析日志时间戳，并做正则脱敏：

```kotlin
fun parseTimestamp(line: String): Triple<Int, Int, Int>? =
    Regex("""(?<h>\d{2}):(?<m>\d{2}):(?<s>\d{2})""").find(line)?.destructured
        ?.let { (h, m, s) -> Triple(h.toInt(), m.toInt(), s.toInt()) }

parseTimestamp("[INFO] 09:05:30 boot done")   // (9, 5, 30)

// findAll 是惰性 Sequence：取第一个匹配时后续不执行（预期行为）
val firstDigit = Regex("\\d").findAll("1a2a3").map { it.value }.first()   // "1"

// 手机号脱敏：分组引用 + replace 变换 lambda
Regex("""(\d{3})\d{4}(\d{4})""").replace("13812345678") { mr ->
    "${mr.groupValues[1]}****${mr.groupValues[2]}"
}   // 138****5678
```

## ⚠️ 常见陷阱

- ❌ 拿 `matches` 当"包含匹配"用——`Regex("\\d+").matches("abc123")` 是 **false**（整串匹配，预期行为）。
  ✅ 找子串用 `containsMatchIn`（只判断）或 `find`/`findAll`（要内容）。
- ❌ 以为 `split` 像 Java 一样丢弃尾部空串——Kotlin **保留**：`"a,b,,".split(",")` → `["a", "b", "", ""]`（预期行为）。
  ✅ 需要去空链上 `filter { it.isNotBlank() }`；解析 CSV 类输入时明确依赖保留语义。
- ❌ 沿用 `Pattern.compile` + `Matcher` 的 Java 习惯——冗长且非惯用。
  ✅ 直接 `Regex(...)` / `"...".toRegex()`；pattern 一律用原始字符串 `"""\d+"""` 免双反斜杠。
- ❌ 找 Java 的 `g` 标志——`RegexOption` 没有它。
  ✅ 全局匹配用 `findAll`（返回惰性 `Sequence`，预期行为短路消费只处理到命中处）。
- ❌ `"%.2f".format(x)` 在用户设备上输出 `3,14`——**format 默认跟随设备区域**（预期行为 `Locale.GERMANY` 即逗号小数点），序列化/协议场景直接出错。
  ✅ 机器可读输出显式 `String.format(Locale.US / Locale.ROOT, ...)`；仅人读展示才用默认区域。
- ❌ 在原始字符串里想输出字面量 `$` 却直接写——原始字符串同样支持模板，`$name` 仍会插值，歧义或编译错误。
  ✅ 字面量美元符统一写 `${'$'}`（预期行为）。

<!-- full-library-explanation -->
## 格式匹配与语义有效性

日期正则能匹配 `2026-99-99`，时间例子也能提取 `99:99:99`。正则确认形状后，还要通过日期时间 API 或数值范围验证业务含义。相同地，手机号脱敏示例不是通用号码校验器，也不能证明日志已经没有其他个人信息。

Kotlin/JVM 的字符串索引按 UTF-16 代码单元计，不一定等于用户看到的字符数。截断 emoji 或组合字符时不能简单用 length 当作字形数。多平台目标的 Regex 支持和 Unicode 行为也需按目标核对。

练习：测试空字符串、尾分隔符、emoji、错误时间以及包含引号/逗号的 CSV 行。验收：能说明 split 只做分割，不实现完整 CSV 语法；重复使用固定正则时复用 Regex 实例，外部输入有长度限制，避免把复杂表达式当万能解析器。

## 🔗 相关条目

- 📄 **[集合操作算子导览](./09-collections-operations.md)** - `split` 结果接 `map`/`filter` 的组合用法
- 📄 **[Sequence 惰性求值](./10-sequences.md)** - `findAll` 返回惰性 Sequence 的语义细节
- 📄 **[Kotlin 关键字与修饰符详解](./01-kotlin-keywords.md)** - 字符串字面量的词法规则
- 📄 **[Kotlin 语法基础](../../basics/03-kotlin-syntax-essentials.md)** - 入门视角的字符串教程
- 🌐 **[Strings（官方文档）](https://kotlinlang.org/docs/strings.html)** - 模板与原始字符串权威参考
- 🌐 **[Regex（官方 API 文档）](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.text/-regex/)** - 全 API 列表

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
