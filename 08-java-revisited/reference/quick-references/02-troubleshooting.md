# 常见错误排查

> **文档简介**: 现代 Java 高频运行时错误与设计陷阱的条目式排查手册：现象 → 原因 → 解决，覆盖 NPE、装箱比较、泛型擦除、并发陷阱等
>
> **目标读者**: 遇到具体报错来找答案的开发者；每条附预防措施
>
> **前置知识**: 对应主题的基础（每条目内链接到详解文档）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#故障排除` `#NPE` `#泛型擦除` `#并发陷阱` |
| **更新日期** | `2026年9月` |

## 1. NullPointerException

**现象**: `java.lang.NullPointerException: Cannot invoke "String.length()" because "s" is null`

**原因**: 对 null 引用调用方法/拆箱/同步。

**解决**:
```java
// Java 14+ 帮助性 NPE 会指出哪个变量为 null，按提示定位即可
// 根治：Optional 契约 + 快速失败
var user = findUser(id).orElseThrow(() -> new UserNotFoundException(id));
Objects.requireNonNull(input, "input 不能为空");
int n = map.getOrDefault(key, 0);                 // 免判空读取
```

**预防**: 对外接口返回 Optional；参数入口 `Objects.requireNonNull`；不要用返回 null 的方法签名。详见[变量与类型](../../basics/03-variables-types.md)。

## 2. 包装类型 == 比较失效

**现象**: `Integer.valueOf(128) == Integer.valueOf(128)` 为 false，而 127 时为 true。

**原因**: 包装类型 `==` 比较引用；-128~127 有缓存池，超范围是不同对象。

**解决**: 包装类型一律 `equals`/`compareTo`；数值比较可拆箱 `a.intValue() == b.intValue()`。

**预防**: 代码检查规则（如 Sonar）开启装箱比较检查。

## 3. ConcurrentModificationException

**现象**: 遍历集合时 `remove` 抛 `ConcurrentModificationException`。

**原因**: 迭代器检测到 modCount 与预期不符（遍历中结构化修改或并发修改）。

**解决**:
```java
list.removeIf(x -> x.isStale());                          // ✅ 首选
var it = list.iterator();
while (it.hasNext()) { if (it.next().isStale()) it.remove(); }  // 迭代器删除
// 并发场景：ConcurrentHashMap / CopyOnWriteArrayList
```

**预防**: 循环体内不直接调集合的 add/remove。详见[集合框架与泛型](../language-concepts/02-collections-generics.md)。

## 4. 泛型擦除相关错误

**现象**: `instanceof List<String>` 编译不过；`new T()`/`new T[]` 编译不过；强转后运行时 `ClassCastException`（堆污染）。

**原因**: 类型擦除——运行时只有 `List.class`，没有参数化信息。

**解决**:
```java
// 需要类型信息时显式传 Class<T>
static <T> List<T> parse(String json, Class<T> type) { ... }
// 泛型集合反序列化：超类型令牌
mapper.readValue(json, new TypeReference<List<User>>() {});
// 检查元素而非集合：list instanceof List && list.get(0) instanceof String
```

**预防**: 不做原始类型（raw type）操作；泛型可变参数方法谨慎暴露（`@SafeVarargs`）。详见[集合框架与泛型](../language-concepts/02-collections-generics.md)。

## 5. Stream 复用 IllegalStateException

**现象**: `IllegalStateException: stream has already been operated upon or closed`

**原因**: Stream 是一次性的，终止后不可再用。

**解决**: 每次从数据源重新 `stream()`；需要多轮处理就先 `toList()` 物化。

**预防**: Stream 不做字段/变量长持有；供应商模式 `Supplier<Stream<T>>` 缓解。详见[Stream/Optional 速查](../language-concepts/03-streams-optional.md)。

## 6. 死锁与竞态

**现象**: 程序卡死（线程 dump 显示 `Found one Java-level deadlock`）或计数偶发错误。

**原因**: 循环等待锁；或复合操作（`i++`、check-then-act）非原子。

**解决**:
```bash
jstack <pid>   # 定位死锁线程与锁持有链
```
```java
// 计数竞态 → 原子类
private final LongAdder counter = new LongAdder();
// 全局锁顺序统一，或用 tryLock 带超时打破循环等待
```

**预防**: 共享可变状态优先并发集合/原子类；锁粒度最小化。详见[并发 API 速查](../language-concepts/04-concurrency-api.md)。

## 7. UnsupportedOperationException

**现象**: 对"集合"调用 add/remove 抛 `UnsupportedOperationException`。

**原因**: 该集合是不可变集合（`List.of`）或定长视图（`Arrays.asList`）。

**解决**: 需要可变副本时 `new ArrayList<>(immutable)`。

**预防**: API 契约中明确不可变性；勿把不可变集合当可变集合传参。

## 8. NoClassDefFoundError vs ClassNotFoundException

**现象**: 运行时类缺失——两种相近报错。

**原因**: `ClassNotFoundException`：显式 `Class.forName` 找不到；`NoClassDefFoundError`：编译在、运行时 classpath 缺失（或静态初始化失败导致的连锁）。

**解决**:
```bash
mvn dependency:tree        # 查依赖冲突（同名不同版本）
java -verbose:class Foo    # 观察类加载来源
```

**预防**: 用 Maven Enforcer/Gradle 锁定依赖版本；排查静态初始化块异常。

## 9. UnsupportedClassVersionError

**现象**: `UnsupportedClassVersionError: ... class file version 65.0`（65=JDK 21）

**原因**: 用更高版本 JDK 编译的字节码跑在低版本 JVM 上。

**解决**: 统一编译目标（`maven.compiler.release=21`）或升级运行时；构建用 toolchain 锁定。

**预防**: CI 与本地 JDK 版本对齐（见[环境搭建](../../basics/01-environment-setup.md)）。

## 10. OutOfMemoryError 分型

**现象/原因/解决**:
- `Java heap space`：堆不够或内存泄漏 → `jmap -histo:live <pid>` 找膨胀对象；泄漏常伴 `GC overhead limit exceeded`
- `Metaspace`：动态生成类过多（反射/CGLib）→ 检查类加载器泄漏
- `unable to create native thread`：线程数超限 → IO 场景虚拟线程改造（收益最大）

**预防**: 容器内显式设置 `-XX:MaxRAMPercentage`；压测监控堆直方图。

## 11. BigDecimal equals 失效

**现象**: `new BigDecimal("1.0").equals(new BigDecimal("1"))` 为 false。

**原因**: `equals` 连 scale（小数位数）一起比较。

**解决**: 数值比较用 `compareTo() == 0`。

**预防**: 构造一律用字符串；金额比较/哈希场景统一 scale（`setScale`）。

## 12. 虚拟线程"钉住"（Pinning）

**现象**: 虚拟线程吞吐不及预期，`jcmd <pid> Thread.dump_to_file` 显示大量虚拟线程卡在 `synchronized`。

**原因**: Java 21 中在 `synchronized` 块内阻塞会钉住载体线程（Java 24 起已修复）。

**解决**: JDK 21 上热点路径改用 `ReentrantLock`；或升级 JDK 24+。

**预防**: 虚拟线程应用升级 JDK 时检查锁用法。详见[并发 API 速查](../language-concepts/04-concurrency-api.md)。

---

## 🔗 相关文档

- 📄 **[现代 Java 一行式速查](./01-java-cheatsheet.md)** - 正确写法对照
- 📄 **[集合框架与泛型](../language-concepts/02-collections-generics.md)** - 集合/泛型语义
- 📄 **[并发 API 速查](../language-concepts/04-concurrency-api.md)** - 并发工具正确用法
- 📄 **[JPA 核心速查](../framework-essentials/02-jpa-essentials.md)** - LazyInitializationException 专题
