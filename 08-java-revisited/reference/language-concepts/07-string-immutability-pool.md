# 字符串不可变语义与 String Pool

> **文档简介**: String 的不可变语义、字符串常量池与 intern()、编译期常量拼接 vs 运行时拼接的 `==` 判断陷阱、`+` 运算符的编译器优化，以及不可变视角下的 String 常用 API 速览
>
> **目标读者**: 需要系统核对 String 语义、彻底搞清 `==`/`equals`/`intern` 行为的开发者
>
> **前置知识**: 基本语法；教程路径见 [变量与类型](../../basics/03-variables-types.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#String` `#不可变` `#常量池` `#语言概念` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

String 是**不可变对象**：final 类、内部存储不可外泄、没有任何修改自身的方法，处理方法返回结果字符串，结果也可能复用已有实例。字符串**字面量**由 JVM 收进字符串常量池（String Pool）去重，同内容字面量全局共享同一实例——这既是 `==` 陷阱的根源，也是其语义基础。

> 示例给出预期行为与规范依据。本轮环境未提供 Java 编译器，未复现历史运行记录；请在项目约定 JDK 上编译验证。

## 📖 语法 / 签名

### `==` 判断结果表（预期行为）

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
| `a == "he" + FINAL_PART` | `true` | `final` 常量表达式同样编译期折叠（JLS 15.29） |
| `a == "he".concat("llo")` | `false` | 方法调用发生在运行时，返回新对象 |

> 关键分界线：**编译期能确定全部操作数的是常量表达式**（入池），含非常量变量或方法调用时不属于常量表达式；方法返回值是否新建对象取决于其契约。

### String 常用 API 速览（不可变视角）

| 方法 | 作用 | 注意 |
|------|------|------|
| `length()` / `charAt(i)` | 长度 / 取字符 | 越界抛 `StringIndexOutOfBoundsException` |
| `substring(b)` / `substring(b, e)` | 截子串 | 不改变原串，可能复用实例 |
| `strip()` / `trim()` | 去首尾空白 | `strip` Unicode 感知；`trim` 只处理 `<= U+0020` |
| `isBlank()` / `isEmpty()` | 全空白 / 长度为 0 | `""` 的 isEmpty 和 isBlank 都为 true |
| `repeat(n)` | 重复 | Java 11+ |
| `lines()` | 按行拆 `Stream<String>` | Java 11+ |
| `formatted(...)` | 格式化 | Java 15+，实例版 `String.format` |
| `split(regex)` | 正则切分 | 参数是**正则**，见 [java.util.regex 导览](../library-guides/08-java-util-regex.md) |
| `indexOf` / `contains` / `replace` | 查找与替换 | `replace` 不改原串，返回新串 |
| `toUpperCase()` / `toLowerCase()` | 大小写转换 | locale 相关；结果不变时可以返回原对象，不能把是否新建对象当作语义 |

## 💡 示例

<!-- ninth-reference-case: {"id":"java-string-pool-and-content","stdout":"true\nfalse\ntrue\nabc\n"} -->
```java
public class Main {
    public static void main(String[] args) {
        String literal = "abc";
        String constructed = new String("abc");
        System.out.println(literal == "a" + "bc");
        System.out.println(literal == constructed);
        System.out.println(literal.equals(constructed));
        System.out.println(literal.toUpperCase().toLowerCase());
    }
}
```

程序把对象身份和内容相等分开：常量表达式拼接与字面量共享池中实例，`new String` 不共享，但两个对象的内容仍由 `equals` 判定为相等。

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

        // 4. 不可变：处理返回结果，原串不变
        String s = "abc";
        System.out.println(s.toUpperCase());           // ABC
        System.out.println(s);                         // abc（原串不变）
    }
}
```

### `+` 的编译器优化

- **单表达式拼接**（如 `"x" + runtimeValue`）：现代 javac 通常使用 `invokedynamic`；纯常量 `"x" + 1 + "y"` 可直接折叠。运行时拼接，委托 `StringConcatFactory.makeConcatWithConstants`，不再生成 `StringBuilder` 链（`javap -c` 可用当前编译器检查）。
- **循环内 `+=`**：每轮迭代都是一次完整的新对象拼接——`javap -c` 常见编译结果显示循环体内没有 `StringBuilder`。字符串规模大时退化为 O(n²)，必须显式 `StringBuilder`：

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
- ❌ **跨类依赖常量折叠做 `==`**：编译期常量会被内联进使用方的 class 文件（JLS 15.29），改了常量不重编使用方会出现"同一常量两个值"的诡异行为。
  ✅ 需要唯一性的枚举/引用统一用 `equals` 或枚举常量（见 [枚举详解](./08-enums.md)）。
- ❌ **到处手动 `intern()` 想省内存**：查表有成本，收益依赖场景。
  ✅ 字面量与常量表达式已自动入池；确有海量重复字符串需求时再评估。

<!-- full-library-explanation -->
## 内容、对象身份与用户看到的字符

不可变表示 String 的内容不能被修改，不表示每次调用都必须分配新对象。例如 substring(0) 可以返回原字符串；程序不能通过引用是否变化判断处理是否成功。业务比较用 equals，只有确实判断共享身份时才用 ==。

```java
public class TextDemo {
    public static void main(String[] args) {
        String text = "A😀";
        System.out.println(text.length());
        System.out.println(text.codePointCount(0, text.length()));
        System.out.println("".isEmpty() + " " + "".isBlank());
        System.out.println(new String("x").equals("x"));
    }
}
```

保存为 TextDemo.java 后编译运行，预期输出 3、2、true true、true。length 统计 UTF-16 代码单元，不是用户感知字符；即使按码点计数，组合附加符和表情序列仍可能构成一个显示字符。练习：比较 "é" 和由 e 加组合重音组成的字符串，解释为什么看起来相同不保证 equals 相同，再根据业务决定是否规范化。

循环构建大文本时使用局部 StringBuilder 可避免反复复制累计结果；线程之间优先传递完成后的不可变 String，而不是为了“线程安全”把所有临时构建器换成共享 StringBuffer。

## 🔗 相关条目

- 📄 **[Java 关键字详解](./01-java-keywords.md)** — `final` 与常量表达式的语法基础
- 📄 **[java.lang 导览](../library-guides/03-java-lang.md)** — StringBuilder/StringBuffer 完整 API
- 📄 **[java.util.regex 导览](../library-guides/08-java-util-regex.md)** — `String.matches/split` 背后的 Pattern 编译成本
- 📄 **[java.text 与时间格式化](../library-guides/07-java-text-and-time-format.md)** — 格式化输出字符串
- 🌐 **[String (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
