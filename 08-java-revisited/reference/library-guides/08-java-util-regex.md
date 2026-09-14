# java.util.regex 导览

> **文档简介**: Pattern/Matcher 两阶段 API、matches/lookingAt/find 三种匹配语义、分组与命名分组、常用正则语法速查、String 正则便捷方法与 Pattern 的关系（重复编译陷阱）
>
> **目标读者**: 需要正确且高效使用正则的开发者
>
> **前置知识**: String 正则方法入口见 [字符串不可变语义](../language-concepts/07-string-immutability-pool.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#正则` `#Pattern` `#Matcher` `#标准库` |
| **更新日期** | `2026年9月` |

## 📌 定义

`java.util.regex` 提供两阶段 API：`Pattern` 是**编译后的正则表达式**（线程安全、可复用），`Matcher` 是 Pattern 对具体输入序列的**匹配引擎**（有状态，不可跨线程共享）。

> 💡 本文行为断言均在本机 JDK 21（javac 21.0.12.1）下编译运行验证。

## 📖 语法 / 签名

### 两阶段用法

```java
Pattern p = Pattern.compile("\\d{4}-\\d{2}");   // 阶段一：编译（一次）
Matcher m = p.matcher("id=2026-09 and 2025-12"); // 阶段二：绑定输入
while (m.find()) {
    m.group();                                   // 2026-09 → 2025-12
}
```

### 三种匹配语义（实测）

| 方法 | 语义 | `Pattern "\\d{4}-\\d{2}"` 对 `id=2026-09` |
|------|------|------|
| `matches()` | **整个**输入序列匹配 | false |
| `lookingAt()` | 从**开头**前缀匹配（不要求到尾，但必须从 index 0 起） | false（前缀 `id=` 不匹配；对 `2026-09x` 为 true，实测） |
| `find()` | 输入序列中**任意位置**查找，可迭代多次 | `"id=2026-09 and 2025-12"` 迭代 2 次（实测） |

### 分组

```java
Pattern date = Pattern.compile("(?<year>\\d{4})-(?<month>\\d{2})-(?<day>\\d{2})");
Matcher m = date.matcher("发布于 2026-09-14");
m.find();
m.group();            // 整个匹配（= group(0)）
m.group("year");      // 2026（命名分组，实测）
m.group(2);           // 09（编号分组，从 1 起）

"2026-09-14".replaceAll("(\\d{4})-(\\d{2})-(\\d{2})", "$3/$2/$1");  // 14/09/2026（实测）
date.matcher("2026-09-14").replaceAll("${day}/${month}");           // 14/09（实测）
```

### 常用语法速查

| 语法 | 含义 |
|------|------|
| `\d` `\w` `\s` | 数字 / 单词字符 / 空白（大写取反；Java 字符串里写 `\\d`） |
| `.` | 任意字符（不含换行；`DOTALL` 下含） |
| `*` `+` `?` `{n,m}` | 量词：≥0 / ≥1 / 0或1 / n 到 m 次 |
| 量词后缀 `?` | 惰性：`<.+?>` 对 `<a><b>` 取 `<a>`，贪婪 `<.+>` 吃到 `<a><b>`（实测） |
| `^` `$` | 行首行尾（`MULTILINE` 下对每行生效，实测） |
| `[abc]` `[a-z]` `[^a]` | 字符类 / 范围 / 取反 |
| `( )` / `(?: )` | 分组捕获 / 分组不捕获 |
| `(?=)` `(?!)` | 环视：肯定/否定前瞻 |
| `\|` | 或 |
| `(?i)` | 内嵌标志（等价 `CASE_INSENSITIVE`） |

### 标志位（实测）

```java
Pattern.compile("java", Pattern.CASE_INSENSITIVE).matcher("JAVA").matches(); // true
Pattern.compile("^\\w+$", Pattern.MULTILINE).matcher("ab\ncd").find();      // true（每行锚点）
Pattern.compile("a.b", Pattern.DOTALL).matcher("a\nb").matches();           // true
```

## 💡 示例

```java
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class RegexDemo {
    public static void main(String[] args) {
        // 字面量切分：正则元字符要转义或 quote（实测）
        System.out.println("a.b".split(".").length);              // 0！. 匹配一切
        System.out.println("a.b".split("\\.").length);            // 2
        System.out.println("a.b".split(Pattern.quote(".")).length); // 2

        // 替换中的 $ 与 \ 是特殊字符（实测）
        System.out.println("a$b".replaceAll("a", Matcher.quoteReplacement("$"))); // $$b（"a"→"$" 后拼上原串的 "$b"）
    }
}
```

### String.matches 与 Pattern 的关系

`String.matches/replaceAll/split` **每次调用都会重新 `Pattern.compile`**。实测：同一正则执行 10 万次，`String.matches` 约 79ms，预编译 `Pattern` 约 15ms（约 5 倍差距，数值随机器波动）。语义完全等价：

```java
"hello".matches("[a-z]+");          // 全串匹配，语义 = Pattern.matches("[a-z]+", "hello")
```

## ⚠️ 常见陷阱

- ❌ **`String.matches` 当"包含"用**：它是**全串**匹配（实测 `"id=2026-09"` 对 `"\\d{4}-\\d{2}"` 为 false）。
  ✅ 包含判断用 `Pattern.compile(x).matcher(s).find()`。
- ❌ **循环里调 `String.matches/split/replaceAll`**：每次重新编译 Pattern（实测 5 倍耗时差）。
  ✅ 循环外 `Pattern.compile` 一次，循环内复用。
- ❌ **`split` 直接传标点**：`.` `|` 等是元字符，`"a.b".split(".")` 得到空数组（实测）。
  ✅ `split("\\.")` 或 `split(Pattern.quote("."))`。
- ❌ **`replaceAll` 替换串里写裸 `$` 或 `\`**：被当分组引用/转义解析（实测裸 `$` 抛 `IllegalArgumentException: Illegal group reference: group index is missing`；而 `$N` 引用不存在的分组才抛 `IndexOutOfBoundsException: No group N`）。
  ✅ 用户输入作替换串时包 `Matcher.quoteReplacement(...)`；模式串用 `Pattern.quote(...)`。
- ❌ **Matcher 跨线程共享**：内部有游标状态。
  ✅ Pattern 共享、每线程各自 `pattern.matcher(input)`。

## 🔗 相关条目

- 📄 **[字符串不可变语义](../language-concepts/07-string-immutability-pool.md)** — String.split/matches 的不可变视角
- 📄 **[java.text 与时间格式化](./07-java-text-and-time-format.md)** — 另一类"解析 ↔ 生成"的文本处理
- 📄 **[Stream / Optional / Collector](../language-concepts/03-streams-optional.md)** — 正则过滤在流中的消费场景
- 🌐 **[Pattern (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/regex/Pattern.html)** — 权威来源（含完整语法表）

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
