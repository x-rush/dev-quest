# Stream / Optional / Collector API 速查

## 把管道与值的缺失分开理解

前置：集合、lambda 与泛型。Stream 描述一次消费的数据处理，Optional 表达可能没有单个结果。filter/map 等中间步骤通常等终结操作才执行，不能依赖 peek 的副作用完成业务工作。

找第一位成年用户时，Stream 负责筛选，findFirst 返回 Optional。没有成年用户是合法的缺失，不应直接 get 后崩溃；选择 orElse、orElseGet 或 orElseThrow 要根据业务含义决定。

自测：为什么昂贵的默认值更适合 orElseGet(() -> loadDefault())？orElse(loadDefault()) 的参数会在调用前求值，即使已有结果也可能执行；Supplier 让需要回退时才计算。Stream 消费后不能再用同一个实例重跑，应重新从集合创建。

> **文档简介**: Stream 创建/中间/终止操作、Collector 收集器、原始类型流与 Optional 全 API 的条目式速查，含并行流与常见误用陷阱
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
Stream.generate(() -> UUID.randomUUID())   // 供给生成（必须 limit）
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
| `toList()` | 收集为不可变 List（Java 16+，首选） |
| `collect(Collector)` | 通用收集 |
| `forEach` / `forEachOrdered` | 遍历（后者保证并行时顺序） |
| `reduce(初值, 累加器)` / `reduce(累加器)` | 归约 |
| `count()` / `min(cmp)` / `max(cmp)` | 统计（返回 Optional） |
| `anyMatch` / `allMatch` / `noneMatch` | 短路判断（返回 boolean） |
| `findFirst` / `findAny` | 取元素（返回 Optional） |
| `toArray(String[]::new)` | 转数组 |

```java
// mapMulti：一对多且不想创建中间 List
stream.mapMulti((book, downstream) -> {
    if (book.available()) downstream.accept(book.title());
})

// reduce：求总和
int total = books.stream().mapToInt(Book::year).reduce(0, Integer::sum);
```

## 🧺 Collectors 收集器

```java
.collect(Collectors.toList())               // 等价 toList()（旧写法）
.collect(Collectors.toSet())
.collect(Collectors.toMap(Book::isbn, b -> b))       // 键冲突需第三参合并函数
.collect(Collectors.groupingBy(Book::author))        // Map<作者, List<Book>>
.collect(Collectors.groupingBy(Book::author, Collectors.counting()))
.collect(Collectors.partitioningBy(Book::available)) // 按布尔分两组
.collect(Collectors.joining(", ", "[", "]"))         // 字符串拼接
.collect(Collectors.teeing(sumA, sumB, (a, b) -> a + b)) // 双流合并（Java 12+）
```

**陷阱**: `toMap` 键重复直接抛 `IllegalStateException`——提供合并函数 `toMap(k, v, (a, b) -> b)`。

## 🔢 原始类型流（IntStream/LongStream/DoubleStream）

```java
IntStream.rangeClosed(1, 100).sum();          // 求和
intStream.average().orElse(0);                // OptionalDouble
intStream.summaryStatistics();                // {count,min,max,sum,average}
stream.boxed().collect(toList());             // 原始流 → 包装流
```

## 🫙 Optional API 全表

| 分类 | API | 说明 |
|------|-----|------|
| 创建 | `of(v)` / `ofNullable(v)` / `empty()` | 值确定非空 / 可能空 / 空 |
| 判断 | `isPresent()` / `isEmpty()` | 是否有值（Java 11+） |
| 取值 | `orElse(默认)` / `orElseGet(供给)` / `orElseThrow()` / `orElseThrow(异常供给)` | 优先 orElseThrow；orElse 的参数总是被计算 |
| 转换 | `map(f)` / `flatMap(f)` / `filter(p)` | 链式处理 |
| 消费 | `ifPresent(c)` / `ifPresentOrElse(c, r)`（Java 9+） | 有值/无值双路径 |
| 组合 | `or(供给)`（Java 9+） | 备选 Optional |
| 流化 | `stream()`（Java 9+） | 融入 Stream 管道 |

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
- ❌ Optional 作字段/参数/集合元素——它只是返回值契约
- ❌ 返回 null 的 Optional（自相矛盾）
- ❌ `isPresent()+get()` 组合——应直接 map/ifPresent

## ⚡ 并行流

```java
bigList.parallelStream()            // 或 stream().parallel()
       .filter(...)
       .toList();
```

**陷阱**:
- 默认使用 `ForkJoinPool.commonPool()`，共享全局——阻塞操作会拖垮整个 JVM 的并行任务
- 仅在**数据量大、无 IO、无共享可变状态**时考虑；小流并行反而更慢
- 现代替代：大 IO 任务直接用虚拟线程（见[并发 API](./04-concurrency-api.md)）

## 🔗 相关文档

- 📄 **[集合框架与泛型](./02-collections-generics.md)** - Stream 的数据源
- 📄 **[并发 API 速查](./04-concurrency-api.md)** - 并行流之外的并发选择
- 📄 **[现代 Java 特性](../../basics/07-modern-features.md)** - 教程式入门
- 📄 **[常见错误排查](../quick-references/02-troubleshooting.md)** - 流复用等运行时错误


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
