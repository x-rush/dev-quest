# 字符串不可变语义与 String Pool

> **文档简介**: String 的不可变语义、字符串常量池与 intern()、编译期常量拼接 vs 运行时拼接的 `==` 判断陷阱、`+` 运算符的编译器优化，以及不可变视角下的 String 常用 API 速览
>
> **目标读者**: 需要系统核对 String 语义、彻底搞清 `==`/`equals`/`intern` 行为的开发者
>
> **前置知识**: 基本语法；教程路径见 [变量与类型](../../basics/03-variables-types.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#String` `#不可变` `#常量池` `#语言概念` |
| **更新日期** | `2026年9月` |

## 📌 定义

String 是**不可变对象**：final 类、内部存储不可外泄、没有任何修改自身的方法，所有"修改"都返回新实例。字符串**字面量**由 JVM 收进字符串常量池（String Pool）去重，同内容字面量全局共享同一实例——这既是 `==` 陷阱的根源，也是其语义基础。

> 💡 本文行为断言均在本机 JDK 21（javac 21.0.12.1）下编译运行验证。

## 📖 语法 / 签名

### `==` 判断结果表（全部实测）

```java
String a = "hello";
String part = "llo";
final String FINAL_PART = "llo";
```

| 表达式 | 结果 | 原因 |
|--------|------|------|
| `a == "hello"` | `true` | 相同字面量入池共享 |
| `a == new String("hello")` | `false` | `new` 强制创建新对象 |
| `a == new String("hello").intern()` | `true` | `intern()` 返回池内实例 |
| `a == "he" + "llo"` | `true` | **编译期常量折叠**，结果作为字面量入池 |
| `a == "he" + part` | `false` | 含变量，运行时拼接产生新对象 |
| `a == "he" + FINAL_PART` | `true` | `final` 常量表达式同样编译期折叠（JLS 15.28） |
| `a == "he".concat("llo")` | `false` | 方法调用发生在运行时，返回新对象 |

> 关键分界线：**编译期能确定全部操作数的是常量表达式**（入池），出现变量/方法调用即推迟到运行时（新对象）。

### String 常用 API 速览（不可变视角）

| 方法 | 作用 | 注意 |
|------|------|------|
| `length()` / `charAt(i)` | 长度 / 取字符 | 越界抛 `StringIndexOutOfBoundsException` |
| `substring(b)` / `substring(b, e)` | 截子串 | 返回新对象 |
| `strip()` / `trim()` | 去首尾空白 | `strip` Unicode 感知；`trim` 只处理 `<= U+0020` |
| `isBlank()` / `isEmpty()` | 全空白 / 长度为 0 | `""` 是 `isEmpty` 但非 `isBlank` |
| `repeat(n)` | 重复 | Java 11+ |
| `lines()` | 按行拆 `Stream<String>` | Java 11+ |
| `formatted(...)` | 格式化 | Java 15+，实例版 `String.format` |
| `split(regex)` | 正则切分 | 参数是**正则**，见 [java.util.regex 导览](../library-guides/08-java-util-regex.md) |
| `indexOf` / `contains` / `replace` | 查找与替换 | `replace` 不改原串，返回新串 |
| `toUpperCase()` / `toLowerCase()` | 大小写转换 | locale 相关，返回新对象 |

## 💡 示例

```java
public class StringPoolDemo {
    public static void main(String[] args) {
        // 1. 字面量共享池内实例
        String a = "hello", b = "hello";
        System.out.println(a == b);                    // true

        // 2. new 强制新对象，intern 回池
        String c = new String("hello");
        System.out.println(a == c);                    // false
        System.out.println(a == c.intern());           // true

        // 3. 编译期常量折叠 vs 运行时拼接
        String part = "llo";
        System.out.println(a == "he" + "llo");         // true（常量折叠）
        System.out.println(a == "he" + part);          // false（运行时拼接）
        System.out.println(a == ("he" + part).intern()); // true

        // 4. 不可变：所有"修改"返回新对象，原串不变
        String s = "abc";
        System.out.println(s.toUpperCase());           // ABC
        System.out.println(s);                         // abc（原串不变）
    }
}
```

### `+` 的编译器优化

- **单表达式拼接**（`"x" + 1 + "y"`）：JDK 9+ 编译为一条 `invokedynamic`，委托 `StringConcatFactory.makeConcatWithConstants`，不再生成 `StringBuilder` 链（`javap -c` 实测确认）。
- **循环内 `+=`**：每轮迭代都是一次完整的新对象拼接——`javap -c` 实测显示循环体内没有 `StringBuilder`。字符串规模大时退化为 O(n²)，必须显式 `StringBuilder`：

```java
// ✅ 循环拼接用 StringBuilder
var sb = new StringBuilder();
for (String w : words) {
    sb.append(w).append(' ');
}
String result = sb.toString();
```

## ⚠️ 常见陷阱

- ❌ **用 `==` 判断字符串内容**：只有字面量/常量折叠情形恰好为 `true`，掺入变量立刻翻车。
  ✅ 判内容用 `equals`；判空用 `Objects.equals(x, "")` 或 `isEmpty()`。
- ❌ **`new String("x")`**：凭空多造一个不被共享的对象。
  ✅ 直接写字面量。
- ❌ **循环里用 `+` 拼大字符串**：每轮产生新对象，O(n²)。
  ✅ 循环外建 `StringBuilder`（线程场景 `StringBuffer`，见 [java.lang 导览](../library-guides/03-java-lang.md)）。
- ❌ **跨类依赖常量折叠做 `==`**：编译期常量会被内联进使用方的 class 文件（JLS 15.28），改了常量不重编使用方会出现"同一常量两个值"的诡异行为。
  ✅ 需要唯一性的枚举/引用统一用 `equals` 或枚举常量（见 [枚举详解](./08-enums.md)）。
- ❌ **到处手动 `intern()` 想省内存**：查表有成本，收益依赖场景。
  ✅ 字面量与常量表达式已自动入池；确有海量重复字符串需求时再评估。

## 🔗 相关条目

- 📄 **[Java 关键字详解](./01-java-keywords.md)** — `final` 与常量表达式的语法基础
- 📄 **[java.lang 导览](../library-guides/03-java-lang.md)** — StringBuilder/StringBuffer 完整 API
- 📄 **[java.util.regex 导览](../library-guides/08-java-util-regex.md)** — `String.matches/split` 背后的 Pattern 编译成本
- 📄 **[java.text 与时间格式化](../library-guides/07-java-text-and-time-format.md)** — 格式化输出字符串
- 🌐 **[String (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
