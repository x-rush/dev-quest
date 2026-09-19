# Java 标准库：选择、输入输出、失败与资源责任

## 阅读准备

前置是 [Java 关键词](../language-concepts/01-java-keywords.md)、基本类型与方法调用。先能区分实例方法、静态方法和 checked exception；文件、HTTP、并发等章节会在这里给出入口，但不替代对应的专题文章。Spring、Jackson、JUnit 是外部依赖，不属于 Java 标准库。

Java 标准库随 JDK 提供；本篇覆盖日常应用的文本、集合工具、数值、时间、文件和 HTTP。所有完整示例使用 Java 21、无外部依赖；它们都是彼此独立的 `Main.java`，一次只保存并编译一个围栏，避免多个 `public class Main` 发生冲突。执行命令为 `javac --release 21 -encoding UTF-8 Main.java` 和 `java Main`。

查方法时同时看四项：输入单位是什么、返回的是新值还是视图、失败抛什么、谁关闭资源。只记“读文件”“不可变”“格式化日期”会漏掉真正影响程序行为的条件。更大的包覆盖范围由[JDK 官方模块列表](https://docs.oracle.com/en/java/javase/21/docs/api/index.html)提供索引。

## 1. 常用库地图

| 包与入口 | 适用问题 | 首先确认 |
|---|---|---|
| `java.lang`：String、Math、Integer、System | 文本、数值转换、运行时基础 | 自动可见不代表全部方法可任意调用；Integer.parseInt 对非法输入抛 NumberFormatException |
| `java.util`：List、Map、Set、Objects、Arrays、Collections、Optional | 容器、排序、空值、可选结果 | null 策略、顺序、重复键、原地修改、视图与快照 |
| `java.util.stream` | 过滤、映射、归约 | 惰性执行、一次消费、是否持有需关闭的外部资源 |
| `java.math`：BigDecimal、BigInteger | 明确精度的十进制、任意精度整数 | 舍入、相等性、除法及数据来源 |
| `java.time` 与 `.format` | 时刻、当地日期、时区、格式 | 日历时间与经过时长不是同一种模型 |
| `java.nio.file`、`java.io` | 文件、目录、字节/字符流 | 编码、内存上限、资源关闭、覆盖语义 |
| `java.net.http` | HTTP 客户端 | 状态码、超时、正文大小、重定向、取消 |
| `java.util.concurrent` | 执行器、队列、同步、原子类 | 生命周期、线程安全、不变式，见[并发 API](../language-concepts/04-concurrency-api.md) |
| `java.util.regex` | 按模式匹配文本 | matches 匹配整体、find 搜索片段；复杂模式需关注输入长度 |
| `java.sql` | JDBC 数据库接口 | 驱动通常是外部依赖，连接与事务需要明确关闭/提交/回滚 |

## 2. String：字节、代码单元与码点不同

`String.length()` 返回 UTF-16 代码单元数量，`chars()` 也是代码单元流；`codePoints()` 才按 Unicode 码点遍历。一个表情可能占两个代码单元，多个码点也可能组成一个可见字形，因此码点数仍不保证等于屏幕“字符数”。

`strip()`、`isBlank()` 使用 `Character.isWhitespace` 的空白定义，不是移除全部 Unicode 空格；例如不间断空格不一定被 strip 去掉。`trim()` 采用更窄的旧规则。`lines()` 按换行拆分，不会把逗号当换行；`split()` 的参数是正则表达式。

预期输出五行：`4`、`3`、`[a, b]`、`[a, b, ]`、`hello`。

<!-- reference-case: {"id":"java-text","stdout":"4\n3\n[a, b]\n[a, b, ]\nhello\n"} -->
```java
import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        String text = "A😀中";
        System.out.println(text.length());
        System.out.println(text.codePointCount(0, text.length()));
        System.out.println("a\nb\n".lines().toList());
        System.out.println(Arrays.toString("a,b,".split(",", -1)));
        System.out.println("  hello\n".strip());
    }
}
```

`split(..., -1)` 保留末尾空字段；默认 split 会去掉末尾空字段。真实 CSV 还可能含引号和带逗号的字段，不能仅靠 split 代替 CSV 解析器。详见 [String API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html)。

| 方法 | 最小调用与结果 | 边界 |
|---|---|---|
| `substring` | `"abcd".substring(1, 3)` → `"bc"` | 左闭右开；按代码单元索引 |
| `contains`、`startsWith`、`endsWith` | `"book.csv".endsWith(".csv")` → true | 区分大小写，不验证文件实际格式 |
| `replace` / `replaceAll` | `"a.b".replace(".", "-")` → `"a-b"` | 前者字面替换，后者按正则匹配 |
| `repeat` | `"ab".repeat(2)` → `"abab"` | 负次数抛 IllegalArgumentException；巨大输出受内存限制 |
| `String.join` | `String.join("/", "a", "b")` → `"a/b"` | 只是文本拼接，不替代 Path 的文件系统语义 |
| `formatted` | `"%s:%d".formatted("n", 2)` → `"n:2"` | 类型与占位符不匹配会抛格式化异常 |
| `Integer.parseInt` | `Integer.parseInt("12")` → 12 | `"12x"`、超范围整数失败；不会自动 trim |

## 3. 集合：定长、只读视图、快照

`Arrays.asList(array)` 是数组支持的定长列表，可 set，不能 add/remove；修改数组也影响列表。`Collections.unmodifiableList` 是禁止从此入口修改的视图，原集合变化仍然可见。`List.copyOf` 创建不可修改的元素引用快照，不接受 null 元素；`List.of` 同样不接受 null。两者都不递归复制元素。

预期输出三行：`[Ada, Lin]`、`[Ada]`、`[Ada, Lin]`。

<!-- reference-case: {"id":"java-collections","stdout":"[Ada, Lin]\n[Ada]\n[Ada, Lin]\n"} -->
```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        var original = new ArrayList<>(List.of("Ada"));
        var view = Collections.unmodifiableList(original);
        var snapshot = List.copyOf(original);
        original.add("Lin");
        System.out.println(view);
        System.out.println(snapshot);
        var sorted = new ArrayList<>(List.of("Lin", "Ada"));
        sorted.sort(String::compareTo);
        System.out.println(sorted);
    }
}
```

验收：对 view 调用 add 会失败，但 original.add 后 view 会变化。不能把两种行为都叫“真正不可变”而不区分。集合详细契约见 [List API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html) 与[集合和泛型](../language-concepts/02-collections-generics.md)。

`Objects.requireNonNull(value, message)` 用于明确不允许 null 的边界；`Objects.equals(a, b)` 允许两边为空；`Optional.ofNullable(value)` 表达可能没有结果，用 `orElseGet` 按需计算默认值。Optional 不应依赖无条件 `get()`，也不能代替所有字段的空值设计。

## 4. BigDecimal：先定义金额单位和舍入

十进制文本用 `new BigDecimal("0.1")`，整数最小单位也可用 `BigDecimal.valueOf(199, 2)` 表示 1.99。`BigDecimal.valueOf(0.1)` 使用 double 的规范字符串形式；它不会恢复此前浮点运算已丢失的精度。“只能字符串构造”过于绝对，但直接 `new BigDecimal(0.1)` 的含义确实是精确表示那个二进制浮点值。

预期输出四行：`0.3`、`false`、`0`、`0.33`。

<!-- reference-case: {"id":"java-decimal","stdout":"0.3\nfalse\n0\n0.33\n"} -->
```java
import java.math.BigDecimal;
import java.math.RoundingMode;

public class Main {
    public static void main(String[] args) {
        System.out.println(new BigDecimal("0.1").add(new BigDecimal("0.2")));
        var first = new BigDecimal("1.0");
        var second = new BigDecimal("1.00");
        System.out.println(first.equals(second));
        System.out.println(first.compareTo(second));
        System.out.println(BigDecimal.ONE.divide(new BigDecimal("3"), 2, RoundingMode.HALF_UP));
    }
}
```

equals 同时考虑数值和 scale；compareTo 返回 0 表示数值相等。这影响 HashMap/HashSet 的键，而不仅是 if 判断。精确 divide 遇到无限十进制展开会抛 ArithmeticException；选择 scale 和舍入模式是业务决定。参见 [BigDecimal API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/math/BigDecimal.html)。

## 5. java.time：日期、时刻、时区、时长

| 类型 | 表示的量 | 例子与边界 |
|---|---|---|
| `LocalDate` | 无时区的年月日 | 生日、账单日期；不是某个 UTC 时刻 |
| `LocalTime` | 无时区的日内时间 | 每天营业 09:00；没有日期 |
| `LocalDateTime` | 无时区的日期和时间 | 墙上时钟读数；夏令时转换时可能不存在或对应两个时刻 |
| `Instant` | 时间线上的时刻 | 日志事件；格式通常显示 UTC |
| `ZoneId` / `ZonedDateTime` | 时区规则 / 带时区的日期时间 | `Europe/Paris` 规则不等于一个固定 UTC 偏移 |
| `Duration` | 秒与纳秒组成的时间量 | 运行耗时、24 小时；不是只有秒级精度 |
| `Period` | 年、月、日组成的日历量 | 一个月、一个日历日；不能泛称“天级秒数” |

预期输出四行：`23`、`12:00`、`13:00`、`invalid date`。

<!-- reference-case: {"id":"java-time","stdout":"23\n12:00\n13:00\ninvalid date\n"} -->
```java
import java.time.Duration;
import java.time.LocalDate;
import java.time.Period;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.format.ResolverStyle;

public class Main {
    public static void main(String[] args) {
        var before = ZonedDateTime.of(2024, 3, 30, 12, 0, 0, 0, ZoneId.of("Europe/Paris"));
        var calendarDay = before.plus(Period.ofDays(1));
        var hours = before.plus(Duration.ofHours(24));
        System.out.println(Duration.between(before, calendarDay).toHours());
        System.out.println(calendarDay.toLocalTime());
        System.out.println(hours.toLocalTime());
        var parser = DateTimeFormatter.ofPattern("uuuu-MM-dd")
                .withResolverStyle(ResolverStyle.STRICT);
        try {
            LocalDate.parse("2025-02-30", parser);
        } catch (DateTimeParseException exception) {
            System.out.println("invalid date");
        }
    }
}
```

当地日历加一天仍是中午，但这段历史夏令时切换只经过 23 小时。代码用固定日期而非 now，结果可复现。严格日期解析用 `uuuu` 年字段和 STRICT，不能只用格式看上去正确就接受“2 月 30 日”。查询 [Duration](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/Duration.html)、[Period](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/Period.html) 和 [ZonedDateTime](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/ZonedDateTime.html) 可了解默认的重叠/缺口解析行为。

## 6. 文件与流：能读到数据还不够

`Files.readString` 一次读完整文本，默认 UTF-8，适合有大小限制的文件。`Files.lines`、`Files.walk` 返回的流持有资源，必须关闭；终端操作结束并不自动 close。`Files.writeString` 默认会创建或截断文件，它不保证一整套读改写事务的原子性。

<!-- reference-case: {"id":"java-files","stdout":"2\ntrue\n"} -->
```java
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

public class Main {
    public static void main(String[] args) throws Exception {
        var file = Files.createTempFile("reference-", ".txt");
        try {
            Files.writeString(file, "Ada\n\nLin\n", StandardCharsets.UTF_8);
            try (var lines = Files.lines(file, StandardCharsets.UTF_8)) {
                System.out.println(lines.filter(line -> !line.isBlank()).count());
            }
        } finally {
            Files.deleteIfExists(file);
        }
        System.out.println(Files.notExists(file));
    }
}
```

输出 2 表示非空行数量；true 表示临时文件已清理。本例在自己创建的临时文件上工作。`Files.exists` 检查与之后的读取之间文件仍可能变化，所以真正的读取异常必须处理；有些权限状态下 exists/notExists 也不互为简单取反。只需要当前目录文件名的 Path 可能没有 parent，不能无条件对 `path.getParent()` 调用 createDirectories。参见 [Files API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Files.html)。

## 7. HttpClient：请求成功返回不等于业务成功

`HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build()` 创建可复用客户端；`HttpRequest.Builder.timeout` 为请求设置超时。连接超时不覆盖全部业务处理时间；实际取消、正文消费和应用整体截止时间仍要设计。

`send(request, BodyHandlers.ofString())` 可能抛 IOException 或 InterruptedException，也可能正常返回状态码 404/500。检查 `response.statusCode()`，再按接口契约解析正文；不能因为没有抛异常就记录“成功”。`ofString` 将正文累积在内存，不能直接拿来接受任意大小的外部内容。

应用可在同配置请求间复用客户端。Java 21 的 HttpClient 实现 AutoCloseable，需要有清晰的应用生命周期；不要每个请求创建后立即丢弃。线程被中断时，通常传播 InterruptedException；捕获后若不能传播，应恢复中断标记并结束该操作。真实网络示例依赖服务端，本篇的离线验证不声称覆盖网络成功率、TLS 或超时实测。官方契约见 [HttpClient](https://docs.oracle.com/en/java/javase/21/docs/api/java.net.http/java/net/http/HttpClient.html)。

## 8. 验收练习

依次运行 5 个完整程序，逐行对照输出。然后完成三个改动：保留 CSV 尾部空字段；修改原集合后解释视图和快照的差异；把固定时间的日历一天换成 24 小时并解释输出。文件实验必须在异常路径也释放资源，不能用“运行后看起来没事”证明没有泄漏。

进入[图书管理项目](../../basics/08-first-project.md)时，再把文件、时间和集合组合起来：输入空标题应失败，未知编号应有明确结果，退出重启仍能读取数据。项目级持久化和并发测试超出这 5 个基础实验的验证范围。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
