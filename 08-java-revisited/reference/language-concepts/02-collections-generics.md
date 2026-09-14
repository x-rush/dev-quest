# 集合框架与泛型速查

> **文档简介**: 集合框架实现类全表、不可变集合工厂、SequencedCollection 新能力与泛型（边界、通配符 PECS）的条目式参考
>
> **目标读者**: 需要按场景选对集合实现、理清泛型通配符的开发者
>
> **前置知识**: 基本语法；系统学习见 [现代 Java 特性](../../basics/07-modern-features.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#集合` `#泛型` `#数据结构` `#PECS` |
| **更新日期** | `2026年9月` |

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
| Map | `EnumMap` | 数组 | O(1) 且最省内存 | 键为枚举时首选 |
| Map | `ConcurrentHashMap` | CAS + synchronized（桶头）/ 红黑树化 | O(1) | 并发键值存储（见[并发 API](./04-concurrency-api.md)） |
| Deque | `ArrayDeque` | 循环数组 | 两端操作 O(1) | 栈/队列首选（代替 Stack/LinkedList） |
| Queue | `PriorityQueue` | 二叉堆 | 出队 O(log n) | 优先级调度、Top-K |

> Java 21 新增 `SequencedCollection`：List/Deque 都有 `getFirst()`/`getLast()`/`reversed()`，`List.reversed()` 返回逆序视图。

## 🧊 不可变集合工厂（Java 9+）

**定义**: `List.of`/`Set.of`/`Map.of` 创建真正不可变集合，`List.copyOf` 防御性拷贝。

```java
var langs = List.of("Java", "Go", "Rust");
var ports = Map.of("http", 80, "https", 443);            // 最多 10 对
var big   = Map.ofEntries(Map.entry("a", 1), Map.entry("b", 2));

var safe  = List.copyOf(mutableList);                     // 已不可变则直接返回
```

**陷阱**:
- 不允许 `null` 元素/键值（抛 NPE）；`contains(null)` 也抛异常
- `Map.of` 重载只到 10 对，更多用 `Map.ofEntries`
- 不可变集合对调用方修改会抛 `UnsupportedOperationException`——序列化/反序列化时要留意

## 🛠️ Map 现代便利方法

```java
map.getOrDefault(key, 0);                       // 免判空的读取
map.putIfAbsent(key, value);                    // 不覆盖已有值
map.computeIfAbsent(key, k -> new ArrayList<>()).add(item);  // 多值 Map 惯用法
map.computeIfPresent(key, (k, v) -> v + 1);
map.merge(key, 1, Integer::sum);                // 计数器惯用法
map.forEach((k, v) -> ...);
```

**陷阱**: `computeIfAbsent`/`merge` 的映射函数内不要再修改同一个 map（ConcurrentModificationException）。

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

**陷阱**: `List<? extends Number>` 只能读不能 add（编译器不知道确切子类型）；`List<?>` 只能读出 Object。

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

**定义**: 泛型信息仅存在于编译期，运行时 `List<String>` 与 `List<Integer>` 是同一个 `List.class`；不可用 `new T[...]` 等即源于此。

绕过手段：方法内传入 `Class<T>` 参数做反射构造；或用超类型令牌（Jackson `TypeReference`）。排查详见[常见错误排查](../quick-references/02-troubleshooting.md)。

### 数组协变陷阱

```java
Object[] arr = new String[1];   // 编译通过（数组协变）
arr[0] = 42;                    // 运行时 ArrayStoreException
// List<Object> ls = new ArrayList<String>();  // ❌ 编译报错（泛型不变）——这是泛型更安全的原因
```

## ✅ 最佳实践 / ❌ 陷阱清单

- ✅ 集合选型默认 `ArrayList`/`HashMap`/`ArrayDeque`，有排序/并发需求再换
- ✅ 对外暴露不可变集合（`List.copyOf`）或返回副本
- ✅ 泛型方法优先于带通配符的签名；通配符遵循 PECS
- ❌ 不要用 `Stack`/`Vector`/`Hashtable`（遗留类）——用 `ArrayDeque`/`ArrayList`/`HashMap`
- ❌ 不要在不可变工厂集合里放 null
- ❌ 不要用原始类型 `List`（raw type）——丢失全部类型检查

## 🔗 相关文档

- 📄 **[Stream/Optional API 速查](./03-streams-optional.md)** - 集合的函数式操作
- 📄 **[并发 API 速查](./04-concurrency-api.md)** - ConcurrentHashMap 与并发集合
- 📄 **[常见错误排查](../quick-references/02-troubleshooting.md)** - 泛型擦除与 CME 问题
- 📄 **[标准库核心](../library-guides/01-standard-library.md)** - java.util 其他工具类
