# 现代 Java 特性 - Lambda、Stream、Optional、虚拟线程与 Sealed

## 先理解，再动手

Stream 描述数据变换管道，终结操作驱动消费；Optional 表达可能缺失；虚拟线程影响任务执行方式。一次只用一个特性解决具体问题。

**本节自测**：用 filter/map 收集成年人姓名，分别输入空列表与无匹配列表。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

两者都得到空结果；不要使用无条件 Optional.get 来代替缺失处理。

</details>

> **文档简介**: 一站式回顾 Java 8 以来的范式转变：Lambda 与函数式接口、Stream 管道、Optional 空安全、Java 21 虚拟线程与 Sealed 类，从"命令式 Java"升级到"现代 Java"
>
> **目标读者**: 主力经验停留在 Java 8，需要系统补齐现代特性的开发者
>
> **前置知识**: 已完成[异常处理](./06-exceptions.md)及之前全部章节

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#Lambda` `#Stream` `#Optional` `#虚拟线程` `#Sealed` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：
- 用 Lambda 与方法引用替代匿名内部类
- 用 Stream 管道替代手写循环过滤/汇总
- 用 Optional 表达"可能缺失"并正确避免其误用
- 用虚拟线程处理高并发 IO 场景
- 用 Sealed 类约束继承体系并配合模式匹配

## 🔄 旧回顾：Java 8 是分水岭

Java 8（2014）引入的 Lambda/Stream/Optional 奠定了"现代 Java"的地基；Java 17/21/25 的 Record/Sealed/模式匹配/虚拟线程则是第二波范式升级。本文按依赖顺序逐个击破。

## 🎯 一、Lambda 与函数式接口

```java
// 旧写法：匿名内部类
Comparator<String> byLenOld = new Comparator<>() {
    @Override
    public int compare(String a, String b) {
        return Integer.compare(a.length(), b.length());
    }
};

// 现代写法：Lambda
Comparator<String> byLen = (a, b) -> Integer.compare(a.length(), b.length());

// 更进一步：方法引用
Comparator<String> byLen2 = Comparator.comparing(String::length);
```

核心函数式接口（`java.util.function`）：

| 接口 | 签名 | 用途 |
|------|------|------|
| `Function<T,R>` | `T -> R` | 转换 |
| `Predicate<T>` | `T -> boolean` | 判断 |
| `Consumer<T>` | `T -> void` | 消费 |
| `Supplier<T>` | `() -> T` | 生产 |

任何"单抽象方法接口"（如 `Runnable`、`Comparator`）都能接 Lambda；自己定义时加 `@FunctionalInterface` 让编译器把关。

## 🌊 二、Stream：声明式数据处理

```java
// 需求：找出所有在库图书的书名，按出版年排序，取前 5 本
List<String> titles = books.stream()                 // 1. 数据源
        .filter(Book::available)                     // 2. 中间操作：过滤
        .sorted(Comparator.comparing(Book::year).reversed())
        .limit(5)
        .map(Book::title)                            // 3. 映射
        .toList();                                   // 4. 终止操作（Java 16+）
```

要点：

- 中间操作惰性求值，遇到终止操作才执行；流**只能消费一次**
- 常用收集器：`Collectors.groupingBy`（分组）、`toMap`、`joining`、`partitioningBy`
- 数值流：`mapToInt(...).sum()/average()/summaryStatistics()`
- 完整 API 详见[Stream/Optional 速查](../reference/language-concepts/03-streams-optional.md)

**心智模型**：循环描述"怎么一步步做"（how），Stream 描述"要什么结果"（what）。简单遍历保留 for，复杂转换/聚合交给 Stream。

## 🫙 三、Optional：让"可能没有"成为类型的一部分

```java
// 旧写法：返回 null，把 NPE 风险转嫁给调用方
public Book findByIsbn(String isbn) { ... /* 可能返回 null */ }

// 现代写法：签名即文档
public Optional<Book> findByIsbn(String isbn) { ... }
```

```java
bookService.findByIsbn("978-7-111")
        .map(Book::title)
        .filter(t -> !t.isBlank())
        .ifPresentOrElse(
                System.out::println,
                () -> System.out.println("未找到图书"));
```

使用铁律：
- ✅ 方法**返回值**表达"可能缺失"；配合 `orElse`/`orElseThrow`/`ifPresent` 消费
- ❌ 不用作字段、方法参数、集合元素；不要 `get()` 裸取值；不要返回 `null` 的 Optional

## 🧵 四、虚拟线程（Java 21 LTS）

**解决的问题**：传统平台线程 1:1 映射 OS 线程，几千个阻塞 IO 请求就要几千个 OS 线程，内存与调度成本高。

```java
// 旧写法：线程池有界，IO 等待期间线程被白白占用
ExecutorService pool = Executors.newFixedThreadPool(200);

// 现代写法：每个任务一个虚拟线程，阻塞成本极低
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i ->
            executor.submit(() -> {
                Thread.sleep(Duration.ofSeconds(1));   // 模拟 IO 等待
                return fetchRemote(i);
            }));
}   // try-with-resources 等待全部任务完成
```

使用要点：
- 适合**IO 密集**（HTTP 调用、数据库访问、文件读写）；CPU 密集任务用它无收益
- **不要池化虚拟线程**——"一任务一线程"就是它的正确用法
- 同步阻塞风格的代码即可获得高并发，无需响应式编程的回调地狱
- Java 21 中 `synchronized` 块内阻塞会造成"钉住"（pinning），Java 24 已修复；21 上热点路径建议改用 `ReentrantLock`
- 更多细节见[并发 API 速查](../reference/language-concepts/04-concurrency-api.md)

## 🔒 五、Sealed 类：可控的继承体系

**旧问题**：`interface Shape` 谁都能实现，switch 分发永远要 default 兜底，新增实现类不会有任何编译期提醒。

```java
public sealed interface Shape permits Circle, Rectangle, Triangle {}
public record Circle(double radius) implements Shape {}
public record Rectangle(double w, double h) implements Shape {}
public final class Triangle implements Shape {}
```

子类必须选择一个修饰符收口：
- `final`：不再被继承（record 天然 final）
- `sealed`：继续限定下一层
- `non-sealed`：重新开放给任意继承

价值在组合：**sealed + record + switch 模式匹配 = 编译器保证穷举的代数数据类型**，配合示例见[控制流程](./05-control-flow.md)与[Record/Sealed/模式匹配参考](../reference/language-concepts/05-records-sealed-patterns.md)。

## ✅ 最佳实践 / ❌ 陷阱清单

Stream 适合清晰的变换、筛选与聚合；包含多步副作用或复杂退出逻辑时，普通循环往往更容易验证。Optional 表达单个结果可能缺失，空集合已经能表达“零项”，无需为一致形式层层包装。

虚拟线程降低某些阻塞等待的线程成本，不增加 CPU 算力，也不扩大数据库容量。并行流和虚拟线程都需要资源上限与实际基准，不能仅按“现代特性”一律开启。

## 🎯 练习与实践

### 练习一：循环改造
1. 写一段"过滤+分组+计数"的循环代码，用 Stream 重写并对比可读性

### 练习二：Optional 契约
1. 把一个返回 null 的方法改为返回 Optional，更新全部调用点

### 练习三：虚拟线程压测
1. 用虚拟线程并发模拟 1000 个"睡眠 1 秒"的 IO 任务，观察总耗时
2. 换成固定线程池（200）对比，体会差异

## 🔗 相关文档

- 📄 **[综合练习：图书管理系统](./08-first-project.md)** - 下一站：综合运用全部特性
- 📄 **[Stream/Optional API 速查](../reference/language-concepts/03-streams-optional.md)** - 函数式 API 全表
- 📄 **[并发 API 速查](../reference/language-concepts/04-concurrency-api.md)** - 虚拟线程与并发工具全表
- 📄 **[Spring Boot 核心](../reference/framework-essentials/01-spring-boot-essentials.md)** - 特性在主流框架中的应用


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
