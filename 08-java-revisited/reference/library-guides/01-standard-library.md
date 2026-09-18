# 标准库核心速查 - java.util / java.time / java.nio

## 以输入输出和资源边界选标准库

前置：字符串、集合、异常与 try-with-resources。java.lang 的常用类型通常自动可见，java.util、java.time、java.nio.file 等通过 import 使用；它们与 Spring、Jackson 等外部库不是同一层。

读 API 时先判断是否产生资源、是否返回视图、是否创建独立值。例如 Files.readString 一次读完整文本，Files.lines 返回需要关闭的 Stream；Collections.unmodifiableList 是不可修改视图，原列表改变仍可能反映到视图，List.copyOf 则建立不可修改的元素引用快照，二者都不保证元素深度不可变。

自测：从可变列表建立 unmodifiableList 后修改原列表，观察视图；再比较 copyOf。验收是能解释“不能通过此入口修改”“不会反映列表结构的后续改变”“元素自身不可变”三个不同承诺。不要只用一个“不可变”把它们合并。

时间也要区分：Instant 表示时间线上的时刻，LocalDate 表示无时区的日期，ZonedDateTime 带时区规则。预约当地早上 9 点与记录请求发生时间需要的模型不同；先确定业务意义，再选格式化方法。

> **文档简介**: 标准库最常用模块的条目式速查：String 现代方法、java.util 工具类、java.time 日期时间、java.nio 文件 IO 与 java.net.http 客户端
>
> **目标读者**: 需要按 API 快速检索、并了解"旧类 → 新 API"对照的开发者
>
> **前置知识**: 基本语法；集合细节见 [集合框架与泛型](../language-concepts/02-collections-generics.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#标准库` `#java.time` `#java.nio` `#字符串` |
| **更新日期** | `2026年9月` |

</details>

## 🔤 String 与文本

```java
" hello ".strip();                // 去首尾空白（Unicode 感知；trim 只处理 <=U+0020）
"  ".isBlank();                   // 是否全空白（Java 11+）
"a,b,c".lines().toList();         // 按行拆成流（Java 11+）
"ab".repeat(3);                   // "ababab"
"%s 有 %d 本".formatted("Java", 25);  // 格式化（Java 15+）
"abc".chars().filter(c -> c != 'b')   // 转字符流
```

**旧 → 新对照**: `new String("x")` → 字面量；`String.format` → `formatted`；多行拼接 → 文本块（见 [变量与类型](../../basics/03-variables-types.md)）。

## 🧰 java.util 工具类

```java
Objects.requireNonNull(x, "x 不能为空");       // 快速失败
Objects.requireNonNullElse(x, "default");      // Java 9+ 空安全默认值
Objects.equals(a, b);                          // null 安全比较
Objects.hash(a, b);                            // hashCode 组合

UUID.randomUUID().toString();                  // 随机唯一标识
new Scanner(System.in).nextLine();             // 简单输入（学习/脚本用）
String.join("; ", list);                       // 字符串拼接
Collections.unmodifiableList(list);            // 旧式不可变包装（新代码用 List.copyOf）
```

**陷阱**: `Arrays.asList(...)` 返回的是**定长视图**——不能 add/remove，但 set 可改；真正的不可变用 `List.of(...)`。

## 📅 java.time（Java 8+，Joda 的标准化后继）

### 核心类型选型

| 类型 | 含义 | 时区 | 典型用途 |
|------|------|------|---------|
| `LocalDate` | 日期 | 无 | 生日、账期 |
| `LocalTime` | 时间 | 无 | 营业时间 |
| `LocalDateTime` | 日期+时间 | 无 | 本地业务时间 |
| `ZonedDateTime` | 完整时区时间 | 有 | 跨时区调度 |
| `Instant` | 时间线时间戳 | UTC | 数据库/日志时间戳 |
| `Duration` | 时间量（秒级） | - | 耗时、超时 |
| `Period` | 日期量（天级） | - | 年龄、期限 |

### 常用操作

```java
LocalDate today = LocalDate.now();
LocalDate release = LocalDate.of(2026, 9, 1);
release.plusMonths(6).minusDays(1);              // 不可变：返回新对象
today.isAfter(release);
Period.between(release, today);                  // 期间

LocalDateTime ldt = LocalDate.of(2026, 9, 10).atTime(14, 30);
ZonedDateTime zdt = ldt.atZone(ZoneId.of("Asia/Shanghai"));
Instant instant = zdt.toInstant();               // 转 UTC 时间线

var fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
ldt.format(fmt);
LocalDateTime.parse("2026-09-10 14:30", fmt);
Instant.parse("2026-09-10T06:30:00Z");           // ISO-8601 直接解析
```

**旧 → 新对照**: `Date`/`Calendar`/`SimpleDateFormat` → 一律 java.time；`Date` 与 `Instant` 可用 `Date.toInstant()`/`Date.from(instant)` 互转（遗留接口边界）。

**陷阱**:
- `LocalDateTime` 无时区——跨时区场景必须 `ZonedDateTime` 或 `Instant`
- `Duration.between` 不能直接用于两个 `LocalDate`（用 `Period` 或 `ChronoUnit.DAYS.between`）

## 📁 java.nio 文件与流

```java
Path path = Path.of("data/books.csv");
Files.readString(path);                          // 一次性读（小文件）
Files.writeString(path, content);                // 一次性写
Files.lines(path);                               // Stream<String> 逐行（必须关闭！）
Files.newBufferedReader(path);                   // try-with-resources 用
Files.readAllLines(path);                        // 中等文件

Files.createDirectories(path.getParent());       // 递归建目录
Files.copy(from, to, StandardCopyOption.REPLACE_EXISTING);
Files.move(a, b);
Files.walk(Path.of("."))                         // 递归遍历（Stream<Path>，需关闭）
     .filter(p -> p.toString().endsWith(".java"));
Files.deleteIfExists(path);
```

**陷阱**: `Files.lines`/`Files.walk` 返回的流持有文件句柄，**必须 try-with-resources 关闭**，否则句柄泄漏。

```java
try (var lines = Files.lines(path)) {
    lines.filter(l -> !l.isBlank()).forEach(System.out::println);
}
```

## 🌐 java.net.http（Java 11+）

```java
var client = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(5))
        .build();                                // 客户端线程安全，全局复用

var request = HttpRequest.newBuilder(URI.create("https://api.example.com/books"))
        .timeout(Duration.ofSeconds(10))
        .header("Accept", "application/json")
        .GET()
        .build();

HttpResponse<String> resp = client.send(request, HttpResponse.BodyHandlers.ofString());
// 虚拟线程下直接 send 阻塞即可（见并发 API 速查）
```

## 🧮 数值类型

```java
new BigDecimal("0.1").add(new BigDecimal("0.2"));  // ✅ 0.3 —— 必须用字符串构造！
new BigDecimal(0.1);                               // ❌ 0.1000000000000000055511151231257827
bd.compareTo(BigDecimal.ZERO) == 0;                // ✅ 数值比较
bd.equals(new BigDecimal("1.0"));                  // ❌ false：equals 连 scale 一起比
```

**陷阱**: `BigDecimal.equals` 含 scale 语义——判断数值相等用 `compareTo`；除不尽的 `divide` 必须指定 `RoundingMode`。

## ✅ 最佳实践 / ❌ 陷阱清单

时间 API 按时间点、日期、时区和时长区分；不要在业务中把所有时间都压成一个本地字符串。Files.lines/walk 等持有资源的流要关闭，普通内存 Stream 则不是同一种资源责任。

HTTP 客户端按相同配置复用，不同代理或身份配置可有独立实例。十进制金额明确精度与舍入，BigDecimal 从字符串构造可避免先经过二进制浮点；线程间共享格式化器则检查其线程安全契约。

## 🔗 相关文档

- 📄 **[集合框架与泛型](../language-concepts/02-collections-generics.md)** - java.util 集合主战场
- 📄 **[并发 API 速查](../language-concepts/04-concurrency-api.md)** - HttpClient 与虚拟线程配合
- 📄 **[综合练习：图书管理系统](../../basics/08-first-project.md)** - Files/Path 实战


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
