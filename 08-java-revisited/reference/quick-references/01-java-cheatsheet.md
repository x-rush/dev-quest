# 现代 Java 一行式速查

> **文档简介**: 现代 Java（21/25）高频操作的一行式代码速查，按场景分组，可整体作为案头卡片
>
> **目标读者**: 需要"直接抄"的日常开发者；每个片段的原理见对应详解文档
>
> **前置知识**: 已过一遍 [模块 README 的学习路径](../../README.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#速查` `#一行式` `#现代Java` |
| **更新日期** | `2026年9月` |

</details>

## 🔤 字符串

```java
var multiline = """
    第一行
    """;                                             // 文本块（开定界符 """ 后必须换行，不能单行书写）
"%s-%d".formatted("id", 1);                          // 格式化
"a,b,c,".split(",", -1);                             // 保留尾部空串
" abc ".strip();                                     // Unicode 感知 trim
"  ".isBlank();                                      // 空白判断
String.join(" / ", list);                            // 拼接
"a\nb".lines().toList();                              // 按行收集
"x".repeat(5);                                       // 重复
str.codePoints().distinct().count();                 // 统计不同 Unicode 码点；不等于显示字符数
```

## 📦 集合

```java
List.of("a", "b");                                   // 不可变
Map.of("k", 1);                                      // 不可变（≤10 对）
List.copyOf(source);                                 // 防御性拷贝
new ArrayList<>(List.of("x"));                       // 可变初始化
list.getFirst(); list.getLast();                     // Java 21+
list.reversed();                                     // 逆序视图 Java 21+
map.getOrDefault("k", 0);                            // 仅在键缺失时使用默认值；已存 null 不被替换
map.merge("k", 1, Integer::sum);                     // 计数
map.computeIfAbsent("k", k -> new ArrayList<>()).add(v);  // 多值 map
list.removeIf(String::isBlank);                      // 安全删除
Collections.shuffle(list);                           // 打乱
```

## 🌊 Stream

```java
list.stream().filter(x -> x > 0).map(String::valueOf).toList();
list.stream().distinct().sorted().toList();
list.stream().sorted(Comparator.comparing(Foo::name).reversed()).toList();
map.entrySet().stream().max(Map.Entry.comparingByValue());   // 求最大 value
list.stream().collect(Collectors.groupingBy(Foo::type));     // 分组
list.stream().collect(Collectors.joining(", "));             // 拼接
list.stream().mapToInt(Foo::score).summaryStatistics();      // 统计
list.stream().flatMap(List::stream).toList();                // 拍平
ids.stream().map(repo::findById).flatMap(Optional::stream).toList(); // 打平 Optional
Stream.iterate(1, n -> n * 2).limit(10).toList();            // 迭代生成
```

## 🫙 Optional

```java
Optional.ofNullable(maybeNull);
opt.orElse(defaultValue);
opt.orElseGet(this::computeDefault);                 // 惰性默认
opt.orElseThrow(() -> new BizException(id));
opt.map(Foo::name).filter(n -> !n.isBlank()).ifPresent(System.out::println);
opt.ifPresentOrElse(this::use, this::fallback);
```

## 🧩 record 与模式匹配

```java
public record Money(long amount, String currency) {
    public Money { if (amount < 0) throw new IllegalArgumentException("负金额"); }
}
if (obj instanceof Money(long a, _)) use(a);         // 解构 + 未命名（Java 22+）
var label = switch (shape) {                          // sealed 穷举
    case Circle c -> "r=" + c.radius();
    case Square s when s.side() > 1 -> "big";
    case Square s -> "small";
};
```

## 📁 文件 IO

```java
Files.readString(Path.of("a.txt"));                  // 全量读
Files.writeString(Path.of("a.txt"), content);        // 全量写
try (var lines = Files.lines(path)) {
    var nonBlank = lines.filter(s -> !s.isBlank()).toList();
}
try (var paths = Files.walk(dir)) {
    long javaFiles = paths.filter(p -> p.toString().endsWith(".java")).count();
}
Files.createDirectories(Path.of("a/b/c"));
Files.deleteIfExists(path);
Files.mismatch(p1, p2);                              // 内容比对
```

## 📅 日期时间

```java
LocalDate.now();  LocalDate.of(2026, 9, 10);
d.plusDays(7).minusMonths(1);
ChronoUnit.DAYS.between(d1, d2);                     // 天数差
LocalDateTime.parse("2026-09-10T14:30");
ldt.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
Instant.now();                                       // UTC 时间戳
LocalDate.from(instant.atZone(ZoneId.of("Asia/Shanghai")));
Duration.between(t1, t2).toSeconds();
```

## 🧵 并发

```java
Thread.startVirtualThread(() -> work());             // 虚拟线程
try (var ex = Executors.newVirtualThreadPerTaskExecutor()) { jobs.forEach(ex::submit); }
var q = new ArrayBlockingQueue<String>(100); q.put(x); q.take();
// 多个任务必须持有同一个 latch；等待方调用同一实例的 await。
var latch = new CountDownLatch(n);
// permit 必须成对释放；acquire 失败时不能 release。
var permits = new Semaphore(10);
permits.acquire();
try { work(); } finally { permits.release(); }
lock.lock(); try { work(); } finally { lock.unlock(); }
CompletableFuture.supplyAsync(ioTask, vthreadPool)
        .thenCombine(other, this::merge)
        .exceptionally(e -> fallback()).join();
```

## 🧪 测试（JUnit 6 Jupiter + AssertJ）

```java
@Test void works() { assertThat(calc(2)).isEqualTo(4); }
assertThatThrownBy(() -> lib.borrow("x")).isInstanceOf(BookNotFoundException.class);
assertThat(list).hasSize(3).contains("a");
@ParameterizedTest @ValueSource(ints = {1, 2, 3})
```

## 🛠️ 命令行

```bash
java Foo.java                     # 单文件直跑（Java 11+）
jshell                            # REPL
mvn clean verify                  # Maven 构建
./gradlew test                    # Gradle 测试
java -jar app.jar                 # 运行 fat jar
java -Xmx512m -Xms256m Foo        # 堆参数
jps -l                           # 列出进程
jstack <pid>                     # 查看指定进程线程
```

<!-- full-library-explanation -->
## 速查片段如何变成一次完整验证

这里的 list、repo、jobs 等代表已有变量，每段强调一种 API，不是可以整页复制运行的工程。先在 jshell 尝试无外部依赖的表达式，再把组合逻辑放进有明确输入输出的方法，最后写失败路径断言。带 Java 22+ 标记的语法不应放进目标 release=21 的源码。

集合“不允许增删”与元素“不可修改”是不同承诺；List.of 和 copyOf 不递归复制元素。getOrDefault 只有键不存在才返回默认值，键已映射到 null 时仍返回 null。reversed 返回视图，修改与原集合的联系取决于底层集合支持的操作。

**练习**：把可变对象放进 List.of 后修改其字段，确认列表结构不可变不代表元素被冻结；对包含 null 值的 HashMap 调用 getOrDefault 并拆箱，观察失败。文件流和锁的代码需要包含关闭或 finally，速查不应成为省略生命周期管理的理由。

## 🔗 相关文档

- 📄 **[常见错误排查](./02-troubleshooting.md)** - 出错时从这里查
- 📄 **[Stream/Optional API 速查](../language-concepts/03-streams-optional.md)** - Stream 全量 API
- 📄 **[标准库核心](../library-guides/01-standard-library.md)** - API 背后的说明


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
