# 集合框架与泛型速查

> **文档简介**: 集合框架实现类全表、不可变集合工厂、SequencedCollection 新能力与泛型（边界、通配符 PECS）的条目式参考
>
> **目标读者**: 需要按场景选对集合实现、理清泛型通配符的开发者
>
> **前置知识**: 基本语法；系统学习见 [现代 Java 特性](../../basics/07-modern-features.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#集合` `#泛型` `#数据结构` `#PECS` |
| **更新日期** | `2026年9月` |

</details>

## 🌳 体系总览

```
Iterable
└── Collection
    ├── List（有序可重复）      → ArrayList / LinkedList / CopyOnWriteArrayList
    ├── Set（不重复）           → HashSet / LinkedHashSet / TreeSet / EnumSet
    └── Queue / Deque（队列）   → ArrayDeque / PriorityQueue / LinkedBlockingQueue
Map（键值对，独立体系）
    → HashMap / LinkedHashMap / TreeMap / EnumMap / ConcurrentHashMap
```

## 📊 实现类选型表

| 接口 | 实现 | 底层 | 复杂度（核心操作） | 典型场景 |
|------|------|------|------|---------|
| List | `ArrayList` | 动态数组 | get O(1)，中间插删 O(n) | **默认选择** |
| List | `LinkedList` | 双向链表 | 头尾插删 O(1)，随机访问 O(n) | 仅头尾频繁增删（一般用 ArrayDeque） |
| List | `CopyOnWriteArrayList` | 复制数组 | 读无锁，写复制全量 | 读多写极少的并发监听器列表 |
| Set | `HashSet` | 哈希表 | add/contains O(1) | 去重默认选择 |
| Set | `LinkedHashSet` | 哈希+链表 | O(1) | 保持插入顺序的去重 |
| Set | `TreeSet` | 红黑树 | O(log n) | 排序集合、范围查询 |
| Map | `HashMap` | 哈希表 | get/put O(1) | **默认选择** |
| Map | `LinkedHashMap` | 哈希+链表 | O(1) | 保持插入序；`accessOrder=true` 做 LRU |
| Map | `TreeMap` | 红黑树 | O(log n) | 按键排序、`headMap`/`tailMap` 范围视图 |
| Map | `EnumMap` | 数组 | 基本操作 O(1)，空间与枚举规模相关 | 键为同一枚举类型时优先考虑 |
| Map | `ConcurrentHashMap` | CAS + synchronized（桶头）/ 红黑树化 | O(1) | 并发键值存储（见[并发 API](./04-concurrency-api.md)） |
| Deque | `ArrayDeque` | 循环数组 | 两端操作 O(1) | 栈/队列首选（代替 Stack/LinkedList） |
| Queue | `PriorityQueue` | 二叉堆 | 出队 O(log n) | 优先级调度、Top-K |

> Java 21 新增 `SequencedCollection`：List/Deque 都有 `getFirst()`/`getLast()`/`reversed()`，`List.reversed()` 返回逆序视图。

表中哈希操作的 O(1) 依赖良好的哈希分布，数组队列扩容涉及复制，因此两端插入是摊还 O(1)。具体实现细节不等于接口保证；选型还应考虑遍历顺序、空值和并发契约。

## 🧊 不可变集合工厂（Java 9+）

**定义**: `List.of`/`Set.of`/`Map.of` 创建不可修改的集合；这只限制集合结构，不会冻结内部对象。`List.copyOf` 取得结构快照，但元素仍是相同引用。

```java
var langs = List.of("Java", "Go", "Rust");
var ports = Map.of("http", 80, "https", 443);            // 最多 10 对
var big   = Map.ofEntries(Map.entry("a", 1), Map.entry("b", 2));

var safe  = List.copyOf(mutableList);                     // 可能复用合适的不可修改实现，不保证对象身份
```

**陷阱**:
- 工厂拒绝 `null` 元素/键值（抛 NPE）。对不允许 null 的集合调用 `contains(null)` 可能抛异常，不能把它当成通用判空函数
- `Map.of` 重载只到 10 对，更多用 `Map.ofEntries`
- 不可变集合对调用方修改会抛 `UnsupportedOperationException`——序列化/反序列化时要留意

## 🛠️ Map 现代便利方法

```java
map.getOrDefault(key, 0);                       // 键不存在才返回 0；映射到 null 时仍返回 null
map.putIfAbsent(key, value);                    // 键不存在或映射为 null 时写入
map.computeIfAbsent(key, k -> new ArrayList<>()).add(item);  // 多值 Map 惯用法
map.computeIfPresent(key, (k, v) -> v + 1);
map.merge(key, 1, Integer::sum);                // 计数器惯用法
map.forEach((k, v) -> ...);
```

**陷阱**: 回调内不要修改同一个 map；不同实现的检测和异常不同，不能依赖一定抛 `ConcurrentModificationException`。`HashMap` 的这些便利方法不提供跨线程原子性，`ConcurrentHashMap` 的原子更新保证也不会自动延伸到其中存储的可变 `ArrayList`。

## 🔐 泛型

### 泛型类与方法

```java
public record Box<T>(T value) {
    public static <U> Box<U> of(U value) { return new Box<>(value); } // 静态方法自行声明 <U>
}

public static <T extends Comparable<T>> T max(List<T> list) { ... }   // 上界
```

### 通配符与 PECS 原则

**定义**: Producer Extends, Consumer Super——只读取用 `? extends`，只写入用 `? super`。

```java
// 生产者：从 src 读取 T
double sum(List<? extends Number> src) {
    return src.stream().mapToDouble(Number::doubleValue).sum();
}

// 消费者：向 dst 写入 T
static <T> void copy(List<? extends T> src, List<? super T> dst) {
    for (T t : src) dst.add(t);
}
```

**陷阱**: `List<? extends Number>` 不能安全添加任意非 null 数字，因为实际可能是 `List<Integer>`；仍能调用 `clear/remove` 等操作，因此它不是只读集合。添加 null 能通过类型检查，但集合实现可以拒绝。`List<?>` 读取结果只能赋给 `Object`。

### 泛型约束（编译期规则）

```java
// ❌ 全部非法
// new T()                     // 不能实例化类型参数
// new T[10]                   // 不能创建参数化数组
// class A<T> { static T f; }  // 静态成员不能用类级类型参数
// catch (T e)                 // 不能捕获泛型异常
// if (obj instanceof List<String> ls)  // instanceof 不能带具体参数化类型
```

### 类型擦除

**定义**: 泛型通过擦除实现，普通 `ArrayList<String>` 与 `ArrayList<Integer>` 对象有相同运行时类，不能从对象类推断其元素类型。部分声明签名仍保留泛型元数据，可由反射读取；“所有泛型信息在运行时都消失”并不准确。

绕过手段：方法内传入 `Class<T>` 参数做反射构造；或用超类型令牌（Jackson `TypeReference`）。排查详见[常见错误排查](../quick-references/02-troubleshooting.md)。

### 数组协变陷阱

```java
Object[] arr = new String[1];   // 编译通过（数组协变）
arr[0] = 42;                    // 运行时 ArrayStoreException
// List<Object> ls = new ArrayList<String>();  // ❌ 编译报错（泛型不变）——这是泛型更安全的原因
```

## 完整实验：结构、元素和映射空值

以下每个程序独立保存为 `Main.java`，用 JDK 21 执行 `javac --release 21 Main.java && java Main`。前面未包含 class/import 的代码是局部用法，不能整篇拼接编译。

第一个实验同时保留可变源、只读视图与快照。先预测源添加元素后两者长度，再观察修改内部对象时三者共享同一引用。

<!-- reference-case: {"id":"java-collection-snapshot-view","stdout":"2:1\nab\nstructure-rejected\n[c, b, a]\n"} -->
```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        var source = new ArrayList<StringBuilder>();
        source.add(new StringBuilder("a"));
        var view = Collections.unmodifiableList(source);
        var snapshot = List.copyOf(source);
        source.add(new StringBuilder("second"));
        System.out.println(view.size() + ":" + snapshot.size());
        source.getFirst().append("b");
        System.out.println(snapshot.getFirst());
        try {
            snapshot.add(new StringBuilder("forbidden"));
            throw new AssertionError("结构修改应失败");
        } catch (UnsupportedOperationException expected) {
            System.out.println("structure-rejected");
        }
        var letters = new ArrayList<>(List.of("a", "b"));
        var reverse = letters.reversed();
        letters.add("c");
        System.out.println(reverse);
    }
}
```

预期依次是 `2:1`、`ab`、`structure-rejected`、`[c, b, a]`。视图观察源的结构变化，快照不会；二者都没有深拷贝元素。`reversed()` 同样是视图。

第二个实验解释为什么 `getOrDefault` 不能代替 null 校验。

<!-- reference-case: {"id":"java-map-null-contract","stdout":"null\n0\n4\n7\n"} -->
```java
import java.util.HashMap;

public class Main {
    public static void main(String[] args) {
        var counts = new HashMap<String, Integer>();
        counts.put("known", null);
        System.out.println(counts.getOrDefault("known", 0));
        System.out.println(counts.getOrDefault("absent", 0));
        counts.putIfAbsent("known", 4);
        System.out.println(counts.get("known"));
        counts.merge("known", 3, Integer::sum);
        System.out.println(counts.get("known"));
    }
}
```

预期依次输出 `null`、`0`、`4`、`7`。如果业务不允许空计数，在写入入口拒绝 null；否则自动拆箱会产生 `NullPointerException`。

第三个实验把 `List<Integer>` 复制到 `List<Number>`，验证 PECS 两端的类型关系。移除源列表元素是合法操作，说明 `? extends` 不代表不可修改。

<!-- reference-case: {"id":"java-pecs-copy","stdout":"[1, 2]\n[2]\n"} -->
```java
import java.util.ArrayList;
import java.util.List;

public class Main {
    static <T> void copy(List<? extends T> src, List<? super T> dst) {
        for (T value : src) dst.add(value);
    }
    public static void main(String[] args) {
        List<Integer> integers = new ArrayList<>(List.of(1, 2));
        List<Number> numbers = new ArrayList<>();
        copy(integers, numbers);
        System.out.println(numbers);
        List<? extends Number> producer = integers;
        producer.remove(0);
        System.out.println(integers);
    }
}
```

练习：把目标改成 `List<String>` 并解释编译错误，再恢复；把第一个实验的 `StringBuilder` 改成不可变 `String`，说明快照隔离能力改变在哪里。运行证据只覆盖上面的 3 个完整程序，见 [基础边界验证报告](../../../shared-resources/tools/document-quality/reports/php-java-core-boundaries.md)。

## 选择集合时的检查顺序

集合先按操作选择：顺序遍历用列表、按键查询用映射、两端操作用队列；需要排序或并发再选择对应实现。List.copyOf 产生不可修改的浅层集合且拒绝 null，内部元素若可变仍可被修改。

泛型让编译器检查元素契约，生产者/消费者通配符用于表达可接受范围；原始类型会削弱静态保障。替换旧同步集合前检查线程安全需求，不能把 Vector 换 ArrayList 后仍假定拥有相同并发行为。

## 🔗 相关文档

- [JDK 21 List 契约](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html) · [Map 默认方法契约](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Map.html)
- 📄 **[Stream/Optional API 速查](./03-streams-optional.md)** - 集合的函数式操作
- 📄 **[并发 API 速查](./04-concurrency-api.md)** - ConcurrentHashMap 与并发集合
- 📄 **[常见错误排查](../quick-references/02-troubleshooting.md)** - 泛型擦除与 CME 问题
- 📄 **[标准库核心](../library-guides/01-standard-library.md)** - java.util 其他工具类


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
