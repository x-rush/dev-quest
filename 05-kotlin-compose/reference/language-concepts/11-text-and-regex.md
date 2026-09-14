# 字符串 API 与正则导览

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

Kotlin 字符串 = JVM `java.lang.String` + 标准库扩展函数：高频操作（split/trim/replace/substringBefore…）全部以扩展函数提供，无需 `StringUtils` 类工具库；正则通过 `Regex` 类封装，API 比 Java `Pattern`/`Matcher` 的分离式设计更直接。下文结果注释均经本机 kotlinc 2.4.20 编译运行验证。

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

规则（实测确认）：**`$` 后跟标识符或 `{` 才是模板**，否则按字面量处理。

```kotlin
val name = "Ada"
"Hi, $name (${name.length} chars)"   // Hi, Ada (3 chars)——$标识符 与 ${表达式}
"sum=${1 + 2}"                       // sum=3
"cost: \$5"                          // cost: $5——\$ 转义字面量 $
"$5"                                 // $5——$ 后跟数字不是模板，按字面量（实测）
"100$"                               // 100$——$ 结尾同理
"""${'$'}"""                         // $——原始字符串里输出 $ 的标准写法
"a\tb"                               // 转义序列同 Java：\t \n \\ \" A → A
```

### 3. 原始字符串（Raw String）

```kotlin
"""a\nb""".length                    // 4——反斜杠不转义，\n 是两个字符（实测）
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

匹配结果取值（实测）：

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
val price = "$%.2f".format(9.5)     // "$9.50"——$ 后跟 % 非模板，按字面量（实测）
```

## 💡 示例

解析日志时间戳，并做正则脱敏：

```kotlin
fun parseTimestamp(line: String): Triple<Int, Int, Int>? =
    Regex("""(?<h>\d{2}):(?<m>\d{2}):(?<s>\d{2})""").find(line)?.destructured
        ?.let { (h, m, s) -> Triple(h.toInt(), m.toInt(), s.toInt()) }

parseTimestamp("[INFO] 09:05:30 boot done")   // (9, 5, 30)

// findAll 是惰性 Sequence：取第一个匹配时后续不执行（实测）
val firstDigit = Regex("\\d").findAll("1a2a3").map { it.value }.first()   // "1"

// 手机号脱敏：分组引用 + replace 变换 lambda
Regex("""(\d{3})\d{4}(\d{4})""").replace("13812345678") { mr ->
    "${mr.groupValues[1]}****${mr.groupValues[2]}"
}   // 138****5678
```

## ⚠️ 常见陷阱

- ❌ 拿 `matches` 当"包含匹配"用——`Regex("\\d+").matches("abc123")` 是 **false**（整串匹配，实测）。
  ✅ 找子串用 `containsMatchIn`（只判断）或 `find`/`findAll`（要内容）。
- ❌ 以为 `split` 像 Java 一样丢弃尾部空串——Kotlin **保留**：`"a,b,,".split(",")` → `["a", "b", "", ""]`（实测）。
  ✅ 需要去空链上 `filter { it.isNotBlank() }`；解析 CSV 类输入时明确依赖保留语义。
- ❌ 沿用 `Pattern.compile` + `Matcher` 的 Java 习惯——冗长且非惯用。
  ✅ 直接 `Regex(...)` / `"...".toRegex()`；pattern 一律用原始字符串 `"""\d+"""` 免双反斜杠。
- ❌ 找 Java 的 `g` 标志——`RegexOption` 没有它。
  ✅ 全局匹配用 `findAll`（返回惰性 `Sequence`，实测短路消费只处理到命中处）。
- ❌ `"%.2f".format(x)` 在用户设备上输出 `3,14`——**format 默认跟随设备区域**（实测 `Locale.GERMANY` 即逗号小数点），序列化/协议场景直接出错。
  ✅ 机器可读输出显式 `String.format(Locale.US / Locale.ROOT, ...)`；仅人读展示才用默认区域。
- ❌ 在原始字符串里想输出字面量 `$` 却直接写——原始字符串同样支持模板，`$name` 仍会插值，歧义或编译错误。
  ✅ 字面量美元符统一写 `${'$'}`（实测）。

## 🔗 相关条目

- 📄 **[集合操作算子导览](./09-collections-operations.md)** - `split` 结果接 `map`/`filter` 的组合用法
- 📄 **[Sequence 惰性求值](./10-sequences.md)** - `findAll` 返回惰性 Sequence 的语义细节
- 📄 **[Kotlin 关键字与修饰符详解](./01-kotlin-keywords.md)** - 字符串字面量的词法规则
- 📄 **[Kotlin 语法基础](../../basics/03-kotlin-syntax-essentials.md)** - 入门视角的字符串教程
- 🌐 **[Strings（官方文档）](https://kotlinlang.org/docs/strings.html)** - 模板与原始字符串权威参考
- 🌐 **[Regex（官方 API 文档）](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.text/-regex/)** - 全 API 列表

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
