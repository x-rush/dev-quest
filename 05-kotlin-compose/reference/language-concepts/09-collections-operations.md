# 集合操作算子导览

> **阅读准备**：List/Set/Map、lambda 与可变/只读接口的区别；练习时为每步写出输入和输出类型。

> List/Set/Map 链式变换的字典层导览：变换、过滤、聚合、分组、分区切片、关联、zip 七类算子——签名 + 一行语义 + 最小示例

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#集合` `#算子` `#函数式` `#Stream对比` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

集合操作算子（collection operations）是 Kotlin 标准库为 `Iterable`/`List`/`Map` 内置的链式变换函数：这里主要讨论返回新集合或聚合值的操作；也有无 lambda 的算子、就地修改及延迟分组 API。List 的 map/filter 通常急切执行并生成结果集合；需要惰性流水线时用 `asSequence()`（见 [Sequence 惰性求值](./10-sequences.md)）。

与 Java Stream 一句话对比：Kotlin 集合算子直接写在集合上、**免 `stream()` / `collect(Collectors.toList())` 样板**，且默认急切；`list.stream().filter(p).map(f).collect(toList())` 在 Kotlin 里就是 `list.filter(p).map(f)`。Stream 的惰性优势对应 Kotlin 的 `Sequence`。

下文注释为预期结果；本轮未在 Kotlin/Android 工具链运行，不能作为预期行为记录。

## 📖 语法 / API 表

### 1. 变换

| 算子 | 签名要点 | 一行语义 |
|------|---------|---------|
| `map` | `map(transform: (T) -> R): List<R>` | 逐元素转换，结果长度不变 |
| `mapIndexed` | `mapIndexed { index, item -> R }` | 带 0 起始下标的 map |
| `mapNotNull` | `mapNotNull(transform: (T) -> R?): List<R>` | 转换后剔除 null 结果 |
| `flatMap` | `flatMap(transform: (T) -> Iterable<R>): List<R>` | 每元素映射为子集合并展平拼接 |
| `flatten` | `Iterable<Iterable<T>>.flatten()` | 二维拍成一维 |
| `distinct` | `distinct(): List<T>` | 按相等性去重，保留首次出现 |

```kotlin
data class User(val name: String, val age: Int, val tags: List<String>)

val users = listOf(
    User("Ada", 30, listOf("kotlin", "go")),
    User("Bob", 25, listOf("rust")),
    User("Cara", 30, listOf("kotlin")),
)

users.map { it.name }                               // [Ada, Bob, Cara]
listOf("a", "bc").mapIndexed { i, s -> "$i:$s" }    // [0:a, 1:bc]
listOf(1, null, 2, null).mapNotNull { it }          // [1, 2]
listOf("ab", "cde").flatMap { it.toList() }         // [a, b, c, d, e]
listOf(listOf(1, 2), listOf(3)).flatten()           // [1, 2, 3]
users.map { it.tags }.flatten().distinct()          // [kotlin, go, rust]
```

### 2. 过滤

| 算子 | 签名要点 | 一行语义 |
|------|---------|---------|
| `filter` | `filter(predicate: (T) -> Boolean): List<T>` | 保留判定为 true 的元素 |
| `filterNot` | `filterNot(predicate)` | 保留判定为 false 的元素（filter 取反） |
| `filterNotNull` | `filterNotNull(): List<T>` | 去除 null 元素 |
| `filterIndexed` | `filterIndexed { index, item -> Boolean }` | 下标 + 元素双重判定 |
| `filterIsInstance` | `filterIsInstance<R>()` | 按类型筛选拆箱 |

```kotlin
users.filter { it.age == 30 }                       // [Ada, Cara]
listOf(1, 2, 3, 4).filterNot { it % 2 == 0 }        // [1, 3]
listOf(1, null, 3).filterNotNull()                  // [1, 3]
listOf(1, 2, 3, 4).filterIndexed { i, _ -> i >= 2 } // [3, 4]
listOf<Any>(1, "a").filterIsInstance<Int>()         // [1]
```

### 3. 聚合

| 算子 | 签名要点 | 一行语义 |
|------|---------|---------|
| `reduce` | `reduce(operation: (acc: S, T) -> S): S` | 无初值折叠，**空集合抛异常** |
| `reduceOrNull` | 同上，空集合返回 null | reduce 的安全版 |
| `fold` | `fold(initial: R, operation: (acc: R, T) -> R): R` | 带初值折叠，空集合安全，初值类型可与元素不同 |
| `sum` / `sumOf` | `sum()`；`sumOf(selector: (T) -> N)` | 数值求和；按选择器求和 |
| `count` | `count(predicate)` / `count()` | 满足条件的元素个数 |
| `maxByOrNull` | `maxByOrNull(selector: (T) -> R): T?` | 按 selector 最大值对应的**元素**，空集合返回 null |
| `maxOfOrNull` | `maxOfOrNull(selector): R?` | selector 的最大**值**本身 |
| `any` / `all` / `none` | `(predicate) -> Boolean` | 存在 / 全称 / 不存在 |

```kotlin
listOf(1, 2, 3, 4).reduce { acc, x -> acc + x }        // 10
listOf(1, 2, 3, 4).fold(10) { acc, x -> acc * x }      // 240（初值 10 也参与）
users.sumOf { it.age }                                 // 85
users.count { it.age == 30 }                           // 2
users.maxByOrNull { it.age }                           // User(name=Ada, ...)（并列时取先出现者）
emptyList<Int>().maxByOrNull { it }                    // null
users.maxOfOrNull { it.age }                           // 30
users.any { it.age > 28 }                              // true
```

### 4. 分组

| 算子 | 签名要点 | 一行语义 |
|------|---------|---------|
| `groupBy` | `groupBy(keySelector): Map<K, List<T>>` | 按键分桶，值为元素列表 |
| `groupBy` 双参 | `groupBy(keySelector, valueSelector)` | 分桶同时做值变换 |
| `groupingBy` | `groupingBy(keySelector): Grouping<T, K>` | 惰性分组句柄，接 `eachCount`/`fold`/`reduce` 做聚合，**不生成中间列表** |

```kotlin
users.groupBy { it.age }                                // {30=[Ada, Cara], 25=[Bob]}
listOf("apple", "avocado", "banana")
    .groupBy({ it.first() }, { it.length })             // {a=[5, 7], b=[6]}
listOf("a", "bb", "bc").groupingBy { it.first() }
    .eachCount()                                        // {a=1, b=2}
users.groupingBy { it.age }
    .fold(0) { acc, u -> acc + u.tags.size }            // {30=3, 25=1}
```

### 5. 分区与切片

| 算子 | 签名要点 | 一行语义 |
|------|---------|---------|
| `partition` | `partition(predicate): Pair<List<T>, List<T>>` | 一次遍历拆成"通过/不通过"两列表 |
| `chunked` | `chunked(size: Int): List<List<T>>` | 定长切块，末块可不足 |
| `chunked` 变换版 | `chunked(size) { chunk -> R }` | 每块直接变换 |
| `windowed` | `windowed(size, step = 1, partialWindows = false)` | 滑动窗口（与 chunked 的区别：窗口重叠） |
| `take` / `takeLast` | `take(n): List<T>` | 取前/后 n 个 |
| `takeWhile` | `takeWhile(predicate)` | 从头连续满足即取，遇假即停 |
| `drop` / `dropLast` | `drop(n): List<T>` | 丢弃前/后 n 个 |
| `dropWhile` | `dropWhile(predicate)` | 从头连续满足即丢，遇假停止丢弃并保留剩余全部 |

```kotlin
val (adults, minors) = users.partition { it.age >= 28 } // adults=[Ada, Cara], minors=[Bob]
listOf(1, 2, 3, 4, 5).chunked(2)                        // [[1, 2], [3, 4], [5]]
listOf(1, 2, 3, 4, 5).chunked(2) { it.sum() }           // [3, 7, 5]
listOf(1, 2, 3, 4, 5).windowed(3)                       // [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
listOf(1, 2, 3, 4, 5).windowed(3, step = 2)             // [[1, 2, 3], [3, 4, 5]]
listOf(1, 2, 3, 4, 5).windowed(3, step = 3)             // [[1, 2, 3]]（末尾不完整窗口默认丢弃）
listOf(1, 2, 3, 4, 5).take(2)                           // [1, 2]
listOf(1, 2, 3, 4, 5).takeWhile { it < 3 }              // [1, 2]
listOf(1, 2, 3, 4, 5).drop(2)                           // [3, 4, 5]
listOf(1, 2, 3, 4, 5).dropWhile { it < 3 }              // [3, 4, 5]
```

### 6. 关联（列表 → Map）

| 算子 | 签名要点 | 一行语义 |
|------|---------|---------|
| `associateBy` | `associateBy(keySelector): Map<K, T>` | 元素本身作值：key = selector(元素) |
| `associateWith` | `associateWith(valueSelector): Map<T, V>` | 元素本身作键：value = selector(元素) |
| `associate` | `associate(transform: (T) -> Pair<K, V>)` | 完全自定义键值对 |

```kotlin
users.associateBy { it.name }        // {Ada=User(Ada...), Bob=..., Cara=...}（按 key 找对象）
listOf("a", "bb").associateWith { it.length }   // {a=1, bb=2}
listOf("a", "bb").associate { it to it.length } // 同上，Pair 自定义
```

### 7. zip 与排序

| 算子 | 签名要点 | 一行语义 |
|------|---------|---------|
| `zip` | `zip(other): List<Pair<T, R>>` | 按位配对，**截断到较短者** |
| `zip` 变换版 | `zip(other) { a, b -> R }` | 配对同时变换 |
| `zipWithNext` | `zipWithNext(): List<Pair<T, T>>` | 相邻元素配对 |
| `sorted` / `sortedBy` / `sortedByDescending` | 返回**新列表** | 排序不修改原集合 |

```kotlin
listOf(1, 2).zip(listOf("a", "b", "c"))          // [(1, a), (2, b)]
listOf(1, 2).zip(listOf("a", "b")) { n, s -> "$n$s" }  // [1a, 2b]
listOf(1, 2, 3).zipWithNext()                    // [(1, 2), (2, 3)]
listOf(1, 2, 3).zipWithNext { a, b -> b - a }    // [1, 1]
users.sortedByDescending { it.age }.first()      // Ada（返回新列表）
```

## 💡 示例

组合管道：从订单列表一步算出"每个大额客户的去重商品数"。

```kotlin
data class Order(val customerId: Long, val amount: Double, val product: String)

val orders = listOf(
    Order(1L, 120.0, "键盘"), Order(1L, 80.0, "鼠标"), Order(2L, 30.0, "贴纸"), Order(2L, 250.0, "显示器"),
)

val bigSpenders: Map<Long, Int> =
    orders
        .filter { it.amount >= 100 }                 // 过滤大额单
        .groupBy { it.customerId }                   // 按客户分桶
        .mapValues { (_, list) ->                    // 桶内聚合
            list.map { it.product }.distinct().size  // 去重商品数
        }
// {1=1, 2=1}
```

### 可直接提取的运行案例

以下为完整 Kotlin 标准库程序，验证本页组合管道、重复 key 与空集合的边界；不涉及 Compose 或 Android 运行时。

```kotlin
data class Order(val customerId: Long, val amount: Double, val product: String)

fun main() {
    val orders = listOf(
        Order(1, 120.0, "keyboard"), Order(1, 80.0, "mouse"),
        Order(2, 250.0, "monitor"), Order(2, 250.0, "monitor"),
    )
    val actual = orders.filter { it.amount >= 100 }.groupBy { it.customerId }
        .mapValues { (_, rows) -> rows.map { it.product }.distinct().size }
    check(actual == mapOf(1L to 1, 2L to 1))
    check(listOf("a", "ab").associateBy { it.first() } == mapOf('a' to "ab"))
    check(emptyList<Int>().fold(0) { acc, value -> acc + value } == 0)
    println("Collection operation contracts passed")
}
```

## ⚠️ 常见陷阱

- ❌ `list.reduce { ... }` 直接用于可能为空的集合——空集合抛 `UnsupportedOperationException`（本机预期行为异常类型即此，非 IllegalStateException）。
  ✅ 有"零值"语义时用 `fold(0) { acc, x -> acc + x }`；或 `reduceOrNull { ... }` + `?:`。
- ❌ `users.maxBy { it.age }` 用于空集合会抛异常；当前 API 与旧版废弃重载要按版本区分。
  ✅ 一律 `maxByOrNull { ... }`，UI 层配合空态：`val top = users.maxByOrNull { it.age } ?: return`。
- ❌ 以为 `associateBy` 遇到重复 key 会报错——实际**后者静默覆盖前者**（`listOf("a", "ab").associateBy { it.first() }` 结果为 `{a=ab}`）。
  ✅ key 可能重复时先 `groupBy`，或用 `associateBy` 前保证 key 唯一。
- ❌ 在几十条数据的 UI 状态链上无脑套 `asSequence()`。
  ✅ 小集合可读性优先直接链 List；大集合 + 多步 + 短路场景才上 Sequence（对比见 [Sequence 惰性求值](./10-sequences.md)）。
- ❌ 想就地排序调用 `list.sortedBy { ... }` 却发现原列表没变。
  ✅ `sortedBy` 返回新列表；就地排序用 `MutableList` 的 `sortWith`/`sortBy`。
- ❌ `windowed(size, step)` 想要"分页式"切块——那是 `chunked` 的语义；`windowed` 是滑动窗口，且默认丢弃末尾不完整窗口。
  ✅ 定长切块用 `chunked`；需要末尾残块时给 `windowed` 传 `partialWindows = true`（预期行为 `[1,2,3,4,5].windowed(3, step=3, partialWindows=true)` → `[[1,2,3],[4,5]]`）。

<!-- full-library-explanation -->
## 把每一步的类型与业务含义写出来

订单例子先过滤“单笔金额至少 100”的订单，然后分组，最后数这些订单中的不同商品。它不是“客户累计消费至少 100 后，统计该客户的所有商品”。原始数据中客户 1 的鼠标订单金额是 80，会被第一步丢弃，所以结果是 `{1=1, 2=1}`。

练习：分别实现上述两种需求，给客户 3 添加两笔金额 60 的订单。验收：第一种没有客户 3，第二种应纳入客户 3；能解释 filter 与 groupBy 的顺序为何改变业务含义。金额练习使用整数最小单位或明确的十进制表示，示例 Double 不应直接作为支付计算方案。

把空输入、重复 key 和只有一个元素加入自测：fold 返回初值，associateBy 按相同 key 覆盖，zip 截断到较短集合。需要报重复数据错误时，必须显式检查，不能指望 associateBy 抛错。

## 🔗 相关条目

- 📄 **[Sequence 惰性求值](./10-sequences.md)** - 同一批算子的惰性版本与大集合选型
- 📄 **[可空性与集合 API 速查](./02-null-safety-collections.md)** - 集合接口体系（只读/可变）与查找类算子
- 📄 **[Lambda 与高阶函数](./08-lambdas-higher-order.md)** - 算子参数 lambda 的 IT 结构与 `it` 约定
- 📄 **[协程与 Flow API 全表](./03-coroutines-flow-api.md)** - 异步数据流上的同形算子（map/filter/flatMap…）
- 🌐 **[Collections overview（官方文档）](https://kotlinlang.org/docs/collections-overview.html)** - 权威参考
- 🌐 **[Collection operations（官方文档）](https://kotlinlang.org/docs/collection-operations.html)** - 全算子速览

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
