# 可空性与集合 API 速查

> **阅读准备**：Kotlin val/var、函数与类型标注；从可空值的分支处理开始，再读集合操作。

> Kotlin 空安全操作符与集合/Sequence/Flow 变换 API 的字典式速查：定义 → 语法 → 示例 → 陷阱

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#空安全` `#集合` `#Sequence` `#集合操作符` |
| **更新日期** | `2026年9月` |

---

## 一、空安全（Null Safety）

### 1. 可空类型 `?`

**定义**: 类型后加 `?` 表示该引用可为 null；非空类型不允许赋 null，编译期即报错。

```kotlin
var a: String = "hi"     // 非空，a = null 编译不通过
var b: String? = null    // 可空
```

### 2. 安全调用 `?.`

**定义**: 接收者为 null 时整条表达式返回 null，否则调用方法。链条中任一环为 null 即短路。

```kotlin
val city = user?.address?.city            // 类型 String?
val len = tasks?.size ?: 0                // 常与 Elvis 连用
```

**陷阱**: 长链 `a?.b?.c?.d` 是坏味道，通常意味着数据建模有问题——考虑默认值或领域模型重构。

### 3. Elvis 操作符 `?:`

**定义**: 左侧为 null 时取右侧值；右侧可 `return`/`throw` 提前退出。

```kotlin
val name = nickname ?: "匿名"
val id = backStackEntry.arguments?.getLong("id") ?: return   // 参数缺失直接退出
fun requireUser(u: User?): User = u ?: throw IllegalArgumentException("无用户")
```

### 4. 非空断言 `!!`

**定义**: 强行声明非空，若为 null 抛 NullPointerException。

```kotlin
val forced: String = nullableName!!       // ⚠️ 最后手段
```

**陷阱**: Compose/Android 中 `!!` 几乎总是可用 `?:`、`let` 或更早的非空建模替代；`lateinit` 是独立机制，未初始化访问会抛异常，也不需要靠 !! 读取。

### 5. let 与安全调用组合

**定义**: `?.let { }` 仅在非空时执行代码块，块内拿到非空值 `it`。

```kotlin
taskId?.let { id -> loadDetail(id) }      // null 时静默跳过
```

### 6. 安全转换 `as?`

**定义**: 转型失败返回 null 而非抛 ClassCastException，常与 Elvis 连用。

```kotlin
val id = arguments?.get("id") as? Long ?: 0L
```

### 7. 平台类型（Java 互操作）

**定义**: 来自 Java 的类型显示为 `String!`，可空性未知，赋给非空变量不会编译报错但可能运行时 NPE。

**陷阱**: 对 Java API 返回值先做非空防御（`?:` 或 `orEmpty()`），不要盲信其"看起来"非空。

---

## 二、集合体系

### 1. 只读与可变接口

**定义**: Kotlin 把"只读视图"与"可变实现"拆成两套接口，是编译期防误改的关键设计。

| 只读接口 | 可变接口 | 创建函数 |
|----------|----------|----------|
| `List<T>` | `MutableList<T>` | `listOf` / `mutableListOf` |
| `Set<T>` | `MutableSet<T>` | `setOf` / `mutableSetOf` |
| `Map<K,V>` | `MutableMap<K,V>` | `mapOf("a" to 1)` / `mutableMapOf` |

```kotlin
val readonly: List<String> = listOf("a", "b")     // 无 add 方法
val mutable: MutableList<String> = mutableListOf("a")
mutable.add("b")                                   // ok

val pairs = mapOf("id" to 1, "name" to "Ada")      // to 创建 Pair
```

**陷阱**: `List` 只保证"通过该引用不可改"，底层对象可能仍可变（如 `listOf(mutableListOf(1))`）；Compose 状态建模建议始终用不可变集合 + `copy` 更新。

### 2. 变换操作符

```kotlin
val users = listOf(User("Ada", 30), User("Bob", 25))

users.map { it.name }                    // [Ada, Bob] 逐元素转换
users.mapIndexed { i, u -> "$i:${u.name}" }
users.filter { it.age > 26 }             // 过滤
users.filterNotNull()                    // 去除 null 元素
users.flatMap { it.tags }                // 嵌套展平
users.map { it.name }.distinct()         // 去重
```

### 3. 聚合操作符

```kotlin
users.sumOf { it.age }                   // 55
users.count { it.age > 26 }              // 1
users.any { it.age > 28 }                // true（存在性）
users.all { it.age > 20 }                // true（全称）
users.maxByOrNull { it.age }             // User?（空集合返回 null ⭐）
users.fold(0) { acc, u -> acc + u.age }  // 带初值折叠
users.map { it.age }.reduce { acc, age -> acc + age }   // 无初值（空集合抛异常）
```

### 4. 分组与关联

```kotlin
users.groupBy { it.age }                 // Map<Int, List<User>>
users.associateBy { it.id }              // Map<Long, User>（id → 对象）
users.associateWith { it.age }           // Map<User, Int>
users.partition { it.age >= 28 }         // Pair<List, List>（通过/不通过）
```

### 5. 查找与截取

```kotlin
users.firstOrNull { it.age == 25 }       // User?，找不到返回 null（优于 first）
users.find { it.age == 25 }              // firstOrNull 别名
users.singleOrNull { it.id == 1L }       // 恰好一个才返回，否则 null
list.take(3)                            // 前三项
list.takeLast(3)                        // 后三项
list.drop(1)                            // 去掉第一项
list.chunked(10)                         // 分页式切块：List<List<T>>
list.sortedByDescending { it.createdAt } // 排序（返回新列表）
```

**陷阱**: `first {}` 空结果抛 `NoSuchElementException`；UI 层一律用 `firstOrNull` + 空态渲染。

---

## 三、Sequence：惰性序列

**定义**: `Sequence` 的操作符是**惰性**的（逐元素流水线），`List` 操作符是**急切**的（每步生成新中间集合）。

```kotlin
// 急切：map 生成中间集合，再 filter 再生成
listOf(1, 2, 3, 4, 5).map { it * 2 }.filter { it > 4 }

// 惰性：每个元素走完整条流水线，找到即止
listOf(1, 2, 3, 4, 5).asSequence()
    .map { it * 2 }
    .first { it > 4 }        // 只处理了 1,2,3
```

**选型**: 大集合 + 多步链式 + 短路/取头几条 → `asSequence()`；常规 UI 状态变换（几十条内）→ 直接 List，可读性优先。

---

## 四、与 Flow 的对应关系

**定义**: Flow 与集合有相似的变换名称，但取消、并发、冷/热流以及时间操作会改变行为，不能视为完全等价。

```kotlin
// 集合：同步一次性
tasks.filter { it.done }.map { it.title }

// Flow：异步持续到达
taskFlow
    .filter { it.done }
    .map { it.title }
    .debounce(300)             // Flow 特有：时间维度操作符
    .distinctUntilChanged()
    .collect { render(it) }
```

| 集合 | Flow 等价/对应 | 差异点 |
|------|----------------|--------|
| `map`/`filter`/`flatMap` | map/filter；展平需选择 flatMapConcat/Latest/Merge 等 | Flow 还要明确取消与并发语义 |
| `first()` | `first()` | 等第一个发射值 |
| `distinct()` | `distinctUntilChanged()` | 比较相邻发射值 |
| — | `debounce`/`sample` | 时间维度，集合无 |
| `Sequence` | `Flow` | 冷、惰性、可挂起、可取消 |

---

## 相关文档

- 📄 **[Kotlin 关键字详解](./01-kotlin-keywords.md)** - 语言关键字层速查
- 📄 **[协程与 Flow API 全表](./03-coroutines-flow-api.md)** - Flow 时间维度操作符全表
- 📄 **[Kotlin 语法基础](../../basics/03-kotlin-syntax-essentials.md)** - 空安全入门教程


<!-- full-library-explanation -->
## 不要让默认值掩盖缺失原因

`null`、空集合和请求失败通常是三种状态。搜索无结果可以是空列表，尚未加载不能直接假装无结果；用户 ID 缺失也不能随手用 0 替代。先确定业务契约，再选择 `?:` 的右侧是默认值、返回还是异常。

```kotlin
// 可独立放入 Main.kt；只依赖 Kotlin 标准库
fun main() {
    val source = mutableListOf("A")
    val view: List<String> = source
    val snapshot = source.toList()
    source.add("B")
    println(view)      // [A, B]：只读接口不是冻结对象
    println(snapshot)  // [A]：列表结构快照，元素若可变仍是浅复制
    println(emptyList<Int>().all { it > 0 }) // true
}
```

练习：为“接口未加载、加载成功但为空、失败”建一个 sealed 类型，并分别渲染。验收：不用 `null.orEmpty()` 抹掉失败原因，能解释空集合的 all 为什么为 true。对 Java 平台类型在边界处收窄，比到处添加 `!!` 更容易定位问题。

## 可复跑：只读接口、快照与空集合的标准库语义

`List` 是只读接口，不是不可变对象；`toList()` 才创建列表结构快照。空集合上的 `all` 也会返回 `true`，它表达“没有反例”，不能被误读为“至少存在一个通过项”。

<!-- dq-p1-case: kotlin-collections-contract -->
```kotlin
fun main() {
    val source = mutableListOf("A")
    val readOnlyView: List<String> = source
    val snapshot = source.toList()
    source += "B"

    check(readOnlyView == listOf("A", "B"))
    check(snapshot == listOf("A"))
    check(emptyList<Int>().all { it > 0 })
    check(emptyList<Int>().none { it > 0 })
    println("Kotlin collection contracts passed")
}
```

它只依赖 Kotlin 标准库，验证的是集合契约；元素对象本身仍可能可变，`toList()` 不是深拷贝，也不涉及 Compose 状态、Flow 或 Android 生命周期。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
