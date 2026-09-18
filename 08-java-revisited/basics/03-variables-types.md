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
> **目标读者**: 有旧版 Java 经验，需要厘清现代类型写法与历史陷阱的学习者
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

注意：Java 仍是**静态强类型**语言，`var` 只是"右侧类型显而易见时的省写"，编译后的字节码与显式声明完全一致。

## 🔢 8 种基本类型速览

| 类型 | 字节 | 范围 | 默认值 | 典型用途 |
|------|------|------|--------|---------|
| `byte` | 1 | -128 ~ 127 | 0 | 二进制流处理 |
| `short` | 2 | ±3.2万 | 0 | 少见，历史遗留 |
| `int` | 4 | ±21亿 | 0 | 默认整型 |
| `long` | 8 | ±9.2×10¹⁸ | 0L | 时间戳、大计数（字面量加 `L`） |
| `float` | 4 | IEEE 754 | 0.0f | 少用，字面量加 `f` |
| `double` | 8 | IEEE 754 | 0.0d | 默认浮点 |
| `char` | 2 | 0 ~ 65535 | ' ' | 单个 UTF-16 字符 |
| `boolean` | - | true/false | false | 逻辑判断 |

选型经验：默认 `int`/`double`；整数字面量可用下划线增强可读性 `1_000_000`（Java 7+）；**金额一律 `BigDecimal`**，不用浮点。

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
2. 必须有初始化器，且初始化与后续赋值类型一致
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
System.out.println(c == d);      // false —— 超出缓存，是两个对象
System.out.println(c.equals(d)); // true  —— 包装类型一律用 equals
```

### 陷阱二：拆箱 NPE

```java
Map<String, Integer> counter = new HashMap<>();
int total = counter.get("missing");          // get 返回 null，拆箱 → NullPointerException

int safe = counter.getOrDefault("missing", 0); // ✅ 现代写法
```

### 陷阱三：三元表达式隐式拆箱

```java
Integer nullable = null;
int flag = 1;
Integer result = flag > 0 ? 1 : nullable;  // 两个分支类型不一致时整体拆箱
                                            // nullable 为 null 时抛 NPE
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

缩进规则：以**结尾定界符的位置**为基准去除公共前导空白。`String` 的现代实例方法（`strip`/`isBlank`/`lines`/`repeat`/`formatted`）详见[标准库核心](../reference/library-guides/01-standard-library.md)。

## ✅ 最佳实践

数值类型由范围和精度需求决定：计数可能超出 int，金额通常需要约定十进制精度与舍入。var 保留静态类型推断，右侧无法一眼看出含义时显式类型可能更易读。

包装类型可能为 null，自动拆箱会因此失败；Objects.equals 等空值安全比较与对象自身 equals 的前提不同。Map.getOrDefault 也不把所有显式 null 值变成默认值。用缺键、存在且为 null、正常值三个输入检查边界。

## 🎯 练习与实践

### 练习一：验证缓存边界
1. 用循环找出 `Integer` 两侧 `==` 成立的最大数值，验证缓存范围

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
