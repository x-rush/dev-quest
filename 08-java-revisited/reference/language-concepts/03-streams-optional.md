# Stream / Optional / Collector API 速查

## 把管道与值的缺失分开理解

前置：集合、lambda 与泛型。Stream 描述一次消费的数据处理，Optional 表达可能没有单个结果。filter/map 等中间步骤通常等终结操作才执行，不能依赖 peek 的副作用完成业务工作。

找第一位成年用户时，Stream 负责筛选，findFirst 返回 Optional。没有成年用户是合法的缺失，不应直接 get 后崩溃；选择 orElse、orElseGet 或 orElseThrow 要根据业务含义决定。

自测：为什么昂贵的默认值更适合 orElseGet(() -> loadDefault())？orElse(loadDefault()) 的参数会在调用前求值，即使已有结果也可能执行；Supplier 让需要回退时才计算。Stream 消费后不能再用同一个实例重跑，应重新从集合创建。

> **文档简介**: 以 Java 21 为基线，查阅 Stream、Collector、原始类型流与 Optional 的常用契约。短片段用于检索；下方完整实验可分别保存为 Main.java 后编译运行。
>
> **目标读者**: 已会基本用法、需要按 API 名快速检索的开发者
>
> **前置知识**: Lambda 基础（见 [现代 Java 特性](../../basics/07-modern-features.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Stream` `#Optional` `#Collector` `#函数式` |
| **更新日期** | `2026年9月` |

</details>

## 🏗️ Stream 创建

```java
list.stream()                              // 集合
Stream.of("a", "b")                        // 显式元素
Arrays.stream(array)                       // 数组
Stream.iterate(1, n -> n * 2).limit(10)    // 迭代生成
Stream.generate(() -> UUID.randomUUID())   // 无限供给；需 limit 或其他能结束的短路消费
Files.lines(path)                          // 逐行读文件（需关闭，见陷阱）
IntStream.range(0, 100)                    // 原始类型区间 [0,100)
IntStream.rangeClosed(1, 10)               // 闭区间
new Random().ints(10, 0, 100)              // 随机数流
```

## ⚙️ 中间操作（惰性）

| API | 说明 | 示例 |
|-----|------|------|
| `filter(Predicate)` | 过滤 | `.filter(b -> b.available())` |
| `map(Function)` | 一一映射 | `.map(Book::title)` |
| `mapToInt/mapToLong/mapToDouble` | 转原始流 | `.mapToInt(Book::year)` |
| `flatMap(Function)` | 拍平嵌套 | `.flatMap(List::stream)` |
| `mapMulti(BiConsumer)` | 一对多手动推入（Java 16+） | 见下 |
| `distinct()` | 去重（按 equals） | `.distinct()` |
| `sorted()` / `sorted(Comparator)` | 排序 | `.sorted(comparing(Book::year))` |
| `peek(Consumer)` | 调试观察（勿用于生产逻辑） | `.peek(System.out::println)` |
| `limit(n)` / `skip(n)` | 截取/跳过 | `.skip(10).limit(5)` |
| `takeWhile` / `dropWhile` | 按条件截断（Java 9+） | `.takeWhile(x -> x < 100)` |

## 🏁 终止操作（触发执行）

| API | 说明 |
|-----|------|
| `toList()` | 收集为不可修改 List（Java 16+）；不保证元素深不可变，允许 null 元素 |
| `collect(Collector)` | 通用收集 |
| `forEach` / `forEachOrdered` | 遍历；后者遵循源本身有定义的 encounter order，不给无序源创造业务顺序 |
| `reduce(初值, 累加器)` / `reduce(累加器)` | 归约 |
| `count()` | 返回 long；实现可能利用已知大小跳过 map/peek 等步骤 |
| `min(cmp)` / `max(cmp)` | 返回 Optional；空流无结果 |
| `anyMatch` / `allMatch` / `noneMatch` | 短路判断（返回 boolean） |
| `findFirst` / `findAny` | 取元素（返回 Optional） |
| `toArray(String[]::new)` | 转数组 |

```java
// mapMulti：一对多且不想创建中间 List
stream.<String>mapMulti((book, downstream) -> {
    if (book.available()) downstream.accept(book.title());
})

// reduce：求总和
int total = books.stream().mapToInt(Book::year).reduce(0, Integer::sum);
```

## 🧺 Collectors 收集器

```java
.collect(Collectors.toList())               // 不保证具体类型、可修改性或线程安全性
.collect(Collectors.toCollection(ArrayList::new)) // 需要可修改 List 时显式指定
.collect(Collectors.toUnmodifiableList())  // 不可修改；拒绝 null 元素
.collect(Collectors.toSet())
.collect(Collectors.toMap(Book::isbn, b -> b))       // 键冲突需第三参合并函数
.collect(Collectors.groupingBy(Book::author))        // Map<作者, List<Book>>
.collect(Collectors.groupingBy(Book::author, Collectors.counting()))
.collect(Collectors.partitioningBy(Book::available)) // 按布尔分两组
.collect(Collectors.joining(", ", "[", "]"))         // 字符串拼接
.collect(Collectors.teeing(sumA, sumB, (a, b) -> a + b)) // 同一批输入分别交给两个下游收集器，再合并结果（Java 12+）
```

**陷阱**: 双参数 `toMap` 遇重复键抛 `IllegalStateException`。只有业务明确“后值覆盖前值”时才用合并函数 `(a, b) -> b`；重复订单号等冲突通常应拒绝。需要稳定迭代顺序时再传 `LinkedHashMap::new`。不要假设这些收集器都能接收 null 值。

## 🔢 原始类型流（IntStream/LongStream/DoubleStream）

```java
IntStream.rangeClosed(1, 100).sum();          // 求和
intStream.average().orElse(0);                // OptionalDouble
intStream.summaryStatistics();                // {count,min,max,sum,average}
stream.boxed().collect(toList());             // 原始流 → 包装流
```

## 🫙 Optional API（Java 21）

| 分类 | API | 说明 |
|------|-----|------|
| 创建 | `of(v)` / `ofNullable(v)` / `empty()` | 值确定非空 / 可能空 / 空 |
| 判断 | `isPresent()` / `isEmpty()` | isPresent 自 Java 8；isEmpty 自 Java 11 |
| 取值 | `get()` / `orElse(默认)` / `orElseGet(供给)` / `orElseThrow()` / `orElseThrow(异常供给)` | get 和无参 orElseThrow 在空时抛 NoSuchElementException；依据业务选择缺省值或异常 |
| 转换 | `map(f)` / `flatMap(f)` / `filter(p)` | 链式处理 |
| 消费 | `ifPresent(c)` / `ifPresentOrElse(c, r)`（Java 9+） | 有值/无值双路径 |
| 组合 | `or(供给)`（Java 9+） | 备选 Optional |
| 流化 | `stream()`（Java 9+） | 融入 Stream 管道 |
| 值语义 | `equals(o)` / `hashCode()` / `toString()` | 相等取决于所含值；不要用身份比较或锁住 Optional，调试字符串格式不是持久化协议 |

```java
// orElse vs orElseGet：默认值计算昂贵时用 orElseGet
Optional.of("x").orElse(expensive());      // expensive() 总会执行
Optional.of("x").orElseGet(this::expensive); // 有值则不执行

// Optional.stream() 打平查找
ids.stream()
   .map(repo::findById)         // Stream<Optional<Book>>
   .flatMap(Optional::stream)   // Stream<Book>，自动丢弃空值
```

**陷阱清单**:
- ❌ `get()` 裸取值（空时抛 NoSuchElementException）
- Optional 主要用于方法返回值；用作参数或字段并非语法错误，但通常增加包装、序列化和调用成本，应说明缺失含义。
- ❌ 返回 null 的 Optional（自相矛盾）
- 在已确认非空的同一个 Optional 上 get 并不错误；map/ifPresent 常能减少分支，复杂控制流则以可读性为准。

## ⚡ 并行流

```java
bigList.parallelStream()            // 或 stream().parallel()
       .filter(...)
       .toList();
```

**陷阱**:
- 常见 JDK 实现利用 ForkJoinPool；在普通调用环境中经常共享 common pool，但 Stream API 不承诺某个固定线程池。阻塞回调可能拖慢共享池上的其他任务。
- 对 CPU 密集、可拆分且操作独立的输入测量串行与并行耗时；并行开销、顺序约束和数据规模共同影响收益，不能由数据量单独决定。
- I/O 并发可考虑虚拟线程，但仍需超时、取消和资源并发上限（见[并发 API](./04-concurrency-api.md)）；线程便宜不等于数据库连接无限。

## 完整实验：列表契约与冲突策略

分别保存每个完整实验为 `Main.java`，执行 `javac --release 21 -encoding UTF-8 Main.java && java Main`。这组实验的输入包括 null、重复键和可变元素，避免只用正常字符串掩盖边界。

<!-- reference-case: {"id":"java-stream-collection-contracts","stdout":"[a, null]\nlist-rejects-add\n[changed]\n[a, b]\ncollector-rejects-null\nduplicate-rejected\n{a=3}\n"} -->
```java
import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        var list = Stream.of("a", (String) null).toList();
        System.out.println(list);
        try { list.add("b"); }
        catch (UnsupportedOperationException e) { System.out.println("list-rejects-add"); }

        var item = new StringBuilder("before");
        var shallow = Stream.of(item).toList();
        item.replace(0, item.length(), "changed");
        System.out.println(shallow);

        var mutable = Stream.of("a").collect(Collectors.toCollection(ArrayList::new));
        mutable.add("b");
        System.out.println(mutable);
        try { Stream.of("a", (String) null).collect(Collectors.toUnmodifiableList()); }
        catch (NullPointerException e) { System.out.println("collector-rejects-null"); }
        try { Stream.of("a", "a").collect(Collectors.toMap(s -> s, String::length)); }
        catch (IllegalStateException e) { System.out.println("duplicate-rejected"); }
        var counts = Stream.of("a", "a", "a").collect(
            Collectors.toMap(s -> s, s -> 1, Integer::sum, LinkedHashMap::new));
        System.out.println(counts);
    }
}
```

`toList()` 限制的是列表结构，元素对象仍可改变。`Collectors.toList()` 的契约没有承诺可修改性，因此实验需要可修改列表时使用 `toCollection`，不把某次返回 ArrayList 的现象当规范。

## 完整实验：空值与默认值何时计算

<!-- reference-case: {"id":"java-optional-fallbacks","stdout":"fallback\nx\nx\ntrue\nflatMap-rejects-null\nempty-rejected\n[x]\n"} -->
```java
import java.util.*;
import java.util.stream.*;

public class Main {
    static String fallback() {
        System.out.println("fallback");
        return "default";
    }
    public static void main(String[] args) {
        var value = Optional.of("x");
        System.out.println(value.orElse(fallback()));
        System.out.println(value.orElseGet(Main::fallback));
        System.out.println(value.map(v -> (String) null).isEmpty());
        try { value.flatMap(v -> (Optional<String>) null); }
        catch (NullPointerException e) { System.out.println("flatMap-rejects-null"); }
        try { Optional.empty().orElseThrow(); }
        catch (NoSuchElementException e) { System.out.println("empty-rejected"); }
        System.out.println(Stream.of(value, Optional.<String>empty())
            .flatMap(Optional::stream).toList());
    }
}
```

`map` 把映射得到的 null 转成空 Optional；`flatMap` 要求回调返回 Optional 对象，null 会破坏这层契约。练习：改成 `Optional.empty()`，确认两条默认值路径都执行；再让 fallback 抛异常，观察有值时 orElse 仍会失败。

## 完整实验：短路、归约和资源

<!-- reference-case: {"id":"java-stream-lifecycle","stdout":"true\nfalse\n6\n[a, b]\nreused-rejected\n2\ntrue\n"} -->
```java
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) throws Exception {
        System.out.println(Stream.<Integer>empty().allMatch(n -> n > 0));
        System.out.println(Stream.<Integer>empty().anyMatch(n -> n > 0));
        System.out.println(IntStream.rangeClosed(1, 3).parallel().reduce(0, Integer::sum));
        var stream = Stream.of("a", "b");
        System.out.println(stream.toList());
        try { stream.count(); }
        catch (IllegalStateException e) { System.out.println("reused-rejected"); }
        Path file = Files.createTempFile("stream-", ".txt");
        var closed = new AtomicBoolean();
        try {
            Files.writeString(file, "a\nb\n", StandardCharsets.UTF_8);
            try (var lines = Files.lines(file, StandardCharsets.UTF_8)
                    .onClose(() -> closed.set(true))) {
                System.out.println(lines.count());
            }
            System.out.println(closed.get());
        } finally { Files.deleteIfExists(file); }
    }
}
```

空流的 allMatch 返回 true、anyMatch 返回 false，这是逻辑约定，不能拿 allMatch 单独证明“至少有一条合格数据”。reduce 的初值必须是单位元，累加运算需满足结合律；例如用减法或把初值设成 10 后直接并行，分区合并就可能改变含义。若需要明确处理每项，使用 forEach 或循环；不要依赖 peek 搭配 count 完成保存。

官方契约：[Stream](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Stream.html)、[Collectors](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Collectors.html)、[Optional](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html)。限定运行范围见[本批验证报告](../../../shared-resources/tools/document-quality/reports/php-java-pipelines-validation.md)。

## 🔗 相关文档

- 📄 **[集合框架与泛型](./02-collections-generics.md)** - Stream 的数据源
- 📄 **[并发 API 速查](./04-concurrency-api.md)** - 并行流之外的并发选择
- 📄 **[现代 Java 特性](../../basics/07-modern-features.md)** - 教程式入门
- 📄 **[常见错误排查](../quick-references/02-troubleshooting.md)** - 流复用等运行时错误


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
