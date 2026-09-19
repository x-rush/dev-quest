# 变量与类型 - 基本类型、var 与包装类型

## 先理解，再动手

基本类型保存数值等基础值，包装类型是对象并可为 null。var 是局部类型推断，不是动态类型。

**本节自测**：给 Integer 设为 null 后尝试赋给 int，再对比正常值。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

自动拆箱需要对象存在，null 会失败；编译期推断不会在运行时替你处理缺失值。

</details>

> **文档简介**: 复习 Java 8 种基本类型，掌握 var 局部类型推断的使用边界，避开包装类型 == 与自动拆箱的经典陷阱
>
> **目标读者**: 会基本编程、刚开始学习 Java 类型和对象的学习者
>
> **前置知识**: 已完成[第一个程序](./02-first-program.md)，能在 JShell 或工程中运行代码

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#变量` `#类型系统` `#var` `#自动装箱` `#文本块` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：
- 复习 8 种基本类型的取值范围与选型经验
- 正确使用 var 局部变量类型推断，清楚它的适用边界
- 识别并规避包装类型三大陷阱（==、拆箱 NPE、三元混合）
- 使用文本块（text block）书写多行字符串

## 🔄 旧回顾：类型声明的变化

本页短代码块是方法内或 JShell 中的局部语法演示，省略的 `map`、`path` 等需由使用场景提供；标为错误的语句用于解释失败条件。后面的两个完整实验包含入口和 import，可按给定命令单独执行。

**旧写法**：一切类型显式声明，泛型信息重复冗长。

```java
ArrayList<String> list = new ArrayList<String>();
Map<String, List<Integer>> index = new HashMap<String, List<Integer>>();
```

**现代写法**（Java 10+）：

```java
var list = new ArrayList<String>();
var index = new HashMap<String, List<Integer>>();
```

Java 仍是静态类型语言。`var` 根据初始化表达式推断一个编译期类型；它与显式写出该推断类型的含义相同，但不保证与任意原声明等价。例如 `List<String> x = new ArrayList<>();` 改成 `var x = new ArrayList<String>();` 后，变量类型从接口变为 `ArrayList<String>`，会影响后续赋值与重载选择。

## 🔢 8 种基本类型速览

| 类型 | 字节 | 范围 | 默认值 | 典型用途 |
|------|------|------|--------|---------|
| `byte` | 1 | -128 ~ 127 | 0 | 二进制流处理 |
| `short` | 2 | ±3.2万 | 0 | 少见，历史遗留 |
| `int` | 4 | ±21亿 | 0 | 默认整型 |
| `long` | 8 | ±9.2×10¹⁸ | 0L | 时间戳、大计数（字面量加 `L`） |
| `float` | 4 | IEEE 754 | 0.0f | 少用，字面量加 `f` |
| `double` | 8 | IEEE 754 | 0.0d | 默认浮点 |
| `char` | 2 | 0 ~ 65535 | `'\u0000'` | 一个 UTF-16 代码单元，不一定是完整字符 |
| `boolean` | - | true/false | false | 逻辑判断 |

表中的默认值适用于字段和数组元素，局部变量必须先明确赋值才能读取。`char` 的默认值是零代码单元，不是空格；许多 emoji 需要两个代码单元表示。整数字面量可用下划线增强可读性，如 `1_000_000`。金额可以用约定最小单位的 `long`，或带精度与舍入规则的 `BigDecimal`，避免用二进制浮点表达必须精确的十进制账务。

## 🪄 var：局部变量类型推断（Java 10+）

**定义**: 编译器根据右侧初始化表达式推断类型，仅作用于局部变量。

### 能用与不能用

```java
var list = new ArrayList<String>();        // ✅ 推断为 ArrayList<String>
var stream = list.stream();                // ✅
for (var entry : map.entrySet()) {}        // ✅ 增强 for
try (var reader = Files.newBufferedReader(path)) {} // ✅ try-with-resources

// ❌ 以下全部编译错误
// var x;                      // 缺少初始化器，无法推断
// var y = null;               // null 无类型信息
// public var name = "tom";    // 不能用于字段
// var f = (String s) -> s.length(); // 无目标类型的 lambda
```

规则清单：
1. 仅限局部变量（含 for 循环变量、try-with-resources）
2. 普通局部变量声明须有初始化器；后续赋值须兼容推断类型（允许适用的转换），类型不会随赋值改变
3. 字段、方法参数、返回类型仍需显式声明
4. 可在 lambda 参数上标注 var（Java 11+），用于加注解等场景

### 什么时候用 var

- ✅ 右侧类型一眼可见：`var map = new HashMap<String, List<Integer>>();`
- ✅ 中间变量：`var nameUpper = name.strip().toUpperCase();`
- ❌ 返回类型不直观的链式调用：`var result = service.process(input);`——读代码的人猜不出类型，可读性反而下降

## 🎁 包装类型与三大陷阱

每种基本类型都有对应包装类：`Integer`、`Long`、`Double`、`Boolean`、`Character`……编译器通过 `valueOf`（装箱）与 `intValue` 等（拆箱）在两者间自动转换。

### 陷阱一：== 比较的是引用

```java
Integer a = 127, b = 127;
System.out.println(a == b);      // true  —— 缓存池 [-128, 127] 内是同一对象

Integer c = 128, d = 128;
System.out.println(c == d);      // 不作保证：实现可以缓存更大范围
System.out.println(c.equals(d)); // true；c 非 null 时用 equals 比较值
```

`Integer.valueOf` 保证缓存 `-128..127`，允许缓存更多值；不能依靠 128 推断必然不同。两侧都是引用时 `==` 比较对象身份；一侧是基本类型时可能先拆箱。变量可能为 null 时可用 `Objects.equals(a, b)`。参见 [Integer.valueOf 的契约](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Integer.html#valueOf(int))。

### 陷阱二：拆箱 NPE

```java
Map<String, Integer> counter = new HashMap<>();
int total = counter.get("missing");          // get 返回 null，拆箱 → NullPointerException

int safe = counter.getOrDefault("missing", 0); // ✅ 现代写法
```

### 陷阱三：三元表达式隐式拆箱

```java
Integer nullable = null;
boolean useDefault = false;
Integer result = useDefault ? 1 : nullable; // 选择 nullable 分支时拆箱为 int，抛 NPE
// useDefault 为 true 时只计算字面量分支，不会因未选中的 null 抛异常
Integer safe = useDefault ? Integer.valueOf(1) : nullable; // 两分支同为 Integer，保留 null
```

> 💡 相关错误与排查详见[常见错误排查](../reference/quick-references/02-troubleshooting.md)。

## 📝 文本块（Java 15+）

```java
// 旧写法：拼接 + 转义
String jsonOld = "{\n" +
        "  \"name\": \"Java\",\n" +
        "  \"version\": 25\n" +
        "}";

// 现代写法：文本块
String json = """
        {
          "name": "Java",
          "version": 25
        }
        """;
```

文本块会规整换行、去掉公共附带缩进，再处理转义。公共缩进取决于非空内容行以及结尾定界符所在空行等因素，不能只看定界符一处。上面的 `json` 最后含换行，`jsonOld` 没有，因此二者并非逐字相同。文本块也不会自动进行 JSON 或 SQL 转义；实际 SQL 参数应使用预处理绑定。`String` 的相关方法见[标准库核心](../reference/library-guides/01-standard-library.md)。

## ✅ 最佳实践

数值类型由范围和精度需求决定：计数可能超出 int，金额通常需要约定十进制精度与舍入。var 保留静态类型推断，右侧无法一眼看出含义时显式类型可能更易读。

包装类型可能为 null，自动拆箱会因此失败；Objects.equals 等空值安全比较与对象自身 equals 的前提不同。Map.getOrDefault 也不把所有显式 null 值变成默认值。用缺键、存在且为 null、正常值三个输入检查边界。

## 完整实验：拆箱发生在什么时候

以下完整程序使用 Java 21，保存为 `Main.java`，执行 `javac --release 21 Main.java`，再执行 `java Main`。预期输出 `boxing boundaries: ok`。程序主动捕获需要观察的 NPE，其余错误会令进程失败；运行记录见 [基础类型验证记录](../../shared-resources/tools/document-quality/reports/php-java-types-validation.md)。

<!-- reference-case: {"id":"java-boxing-boundaries","stdout":"boxing boundaries: ok\n"} -->
```java
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class Main {
    private char initial;
    static void check(boolean value) {
        if (!value) throw new AssertionError("检查失败");
    }
    static void expectNpe(Runnable action) {
        try { action.run(); } catch (NullPointerException expected) { return; }
        throw new AssertionError("应发生 NPE");
    }
    public static void main(String[] args) {
        check(new Main().initial == '\u0000');
        check("😀".length() == 2);
        Integer a = 127, b = 127;
        check(a == b); // 保证范围内。
        Integer c = 128, d = 128;
        check(Objects.equals(c, d)); // 不对范围外的引用身份作假设。
        Map<String, Integer> counts = new HashMap<>();
        check(counts.getOrDefault("missing", 0) == 0);
        counts.put("present", null);
        expectNpe(() -> { int value = counts.getOrDefault("present", 0); });
        Integer nullable = null;
        boolean useDefault = false;
        expectNpe(() -> { Integer value = useDefault ? 1 : nullable; });
        Integer safe = useDefault ? Integer.valueOf(1) : nullable;
        check(safe == null);
        Integer selected = !useDefault ? 1 : nullable;
        check(selected == 1); // 未选中 nullable 分支，不会拆箱它。
        var number = 1L;
        number = 2; // int 可以拓宽为已推断的 long。
        check(number == 2L);
        System.out.println("boxing boundaries: ok");
    }
}
```

## 完整实验：文本块的空白就是数据

此程序另存成 `Main.java`，用同样命令执行，预期输出 `text block: ok`。不要与上面的同名类拼到一个文件。

<!-- reference-case: {"id":"java-text-block-boundaries","stdout":"text block: ok\n"} -->
```java
public class Main {
    public static void main(String[] args) {
        String block = """
                alpha
                  beta
                """;
        if (!block.equals("alpha\n  beta\n")) {
            throw new AssertionError("公共缩进或结尾换行不符预期");
        }
        String noFinalNewline = """
                alpha""";
        if (!noFinalNewline.equals("alpha")) throw new AssertionError();
        System.out.println("text block: ok");
    }
}
```

练习时先在纸上标出每行的空格和换行，再调整结尾定界符位置。规则来源：[JLS 字面量与文本块](https://docs.oracle.com/javase/specs/jls/se21/html/jls-3.html#jls-3.10.6)、[装箱转换](https://docs.oracle.com/javase/specs/jls/se21/html/jls-5.html#jls-5.1.7) 与 [条件表达式](https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.25)。

## 🎯 练习与实践

### 练习一：验证缓存边界
1. 比较 127、128、1000 的装箱身份和值；记录运行环境，但不要把观察到的缓存上限当作语言承诺。用 `Objects.equals` 重写业务比较。

### 练习二：var 重构
1. 找一段旧代码，为合适的局部变量加上 `var`，为不合适的位置写下理由

### 练习三：文本块
1. 用文本块输出一段 SQL 与一段 JSON，并用 `.formatted()` 填充变量

## 🔗 相关文档

- 📄 **[类、接口与 Record](./04-classes-records.md)** - 下一站：从字段类型走向类型设计
- 📄 **[Java 关键字详解](../reference/language-concepts/01-java-keywords.md)** - var 关键字条目
- 📄 **[常见错误排查](../reference/quick-references/02-troubleshooting.md)** - NPE 与装箱问题速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
