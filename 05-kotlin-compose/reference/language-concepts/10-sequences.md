# Sequence 惰性求值

> **阅读准备**：集合 map/filter 和 Iterator；先理解惰性处理何时开始，才能判断是否节省工作。

> Sequence 与集合链的本质差异：中间操作惰性、末端操作触发、逐元素流水线、短路算子、迭代限制与副作用陷阱

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Sequence` `#惰性求值` `#性能` `#短路` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

`Sequence<T>` 是**惰性**的元素流水线：`map`/`filter` 等中间操作只记录变换、不立即计算，直到**末端操作**（`toList`/`first`/`sum`…）触发才逐元素执行整条链。对比集合（`List`）链的**急切**语义——每一步立刻生成完整中间集合。

两个关键差异（按语义解释，本轮未编译运行）：

| 维度 | 集合链 | Sequence 链 |
|------|--------|-------------|
| 执行模型 | 按步骤：每步处理**全部**元素，产生中间集合 | 按元素：每个元素走完整条链，再轮到下一个 |
| 触发时机 | 每个算子调用即执行 | 仅末端操作触发 |
| 短路 | `first {}` 停止本步，但**前面的中间集合已全部算完** | `first {}` 让整条链提前终止，只处理到命中为止 |
| 无限数据 | 不可能 | `generateSequence` 可表达 |

## 📖 语法 / API 表

### 1. 创建 Sequence

| API | 签名要点 | 说明 |
|-----|---------|------|
| `asSequence()` | `Iterable<T>.asSequence()` | 最常用：集合 → 惰性序列 |
| `sequenceOf()` | `sequenceOf(vararg elements)` | 字面量直接建 |
| `generateSequence` | `generateSequence(seed) { next: (T) -> T? }` | next 返回 null 即终止，可表达**无限序列** |
| `sequence { }` | 挂起构建器，`yield` / `yieldAll` 逐个产出 | 复杂生成逻辑 |

```kotlin
listOf(1, 2, 3).asSequence()
sequenceOf("a", "b")
generateSequence(2) { it * 2 }                        // 2, 4, 8, 16, ... 无限
generateSequence(1) { if (it < 5) it + 1 else null }  // 1..5
sequence {
    yield(0)
    yieldAll(listOf(1, 2))                            // 0, 1, 2
}
```

### 2. 中间操作（惰性，返回 Sequence）

`map` `mapIndexed` `filter` `filterNot` `flatMap` `take(n)` `takeWhile` `drop` `dropWhile` `distinct` `sorted` `onEach` `zipWithNext`…——与集合算子同名同义（见 [集合操作算子导览](./09-collections-operations.md)），差别仅在延迟执行。

### 3. 末端操作（触发计算）

| 类别 | 算子 | 一行语义 |
|------|------|---------|
| 收集 | `toList()` `toSet()` `toMap()` | 物化为集合 |
| 聚合 | `sum()` `count {}` `fold` `reduce` `maxByOrNull` | 同集合聚合 |
| **短路** | `first {}` `firstOrNull {}` `any {}` `all {}` `none {}` | 命中/判定完成即停止后续元素处理 |
| **短路** | `take(n)` + 末端收集 | 只让前 n 个元素流过整条链（无限序列截断手段） |
| 遍历 | `forEach` `forEachIndexed` | 逐个消费（别在这里做副作用，见陷阱） |

## 💡 示例

### 1. 惰性 vs 急切：同样的链，处理的元素数不同

```kotlin
// 急切：map 对全部 5 个元素执行完，first 才逐个判断
val eagerLog = mutableListOf<Int>()
listOf(1, 2, 3, 4, 5)
    .map { eagerLog.add(it); it * 2 }
    .first { it > 4 }                     // 结果 6
// 预期行为 eagerLog == [1, 2, 3, 4, 5]——map 全跑了一遍

// 惰性：1→2 不满足、2→4 不满足、3→6 命中，整条链立即终止
val lazyLog = mutableListOf<Int>()
listOf(1, 2, 3, 4, 5)
    .asSequence()
    .map { lazyLog.add(it); it * 2 }
    .first { it > 4 }                     // 结果 6
// 预期行为 lazyLog == [1, 2, 3]——只处理了 3 个元素
```

### 2. 执行顺序：Sequence 是"逐元素流水线"

```kotlin
// Sequence：m1 f1 m2 f2（元素 1 走完全链，才轮到元素 2）
listOf(1, 2).asSequence()
    .map { print("m$it "); it }
    .filter { print("f$it "); true }
    .toList()

// 集合：m1 m2 f1 f2（map 步先全部完成，才进 filter）
listOf(1, 2).map { print("m$it "); it }.filter { print("f$it "); true }
```

### 3. 短路与无限序列

```kotlin
generateSequence(1) { it + 1 }
    .first { it > 1_000_000 }      // 1_000_001——无限序列靠短路终止
generateSequence(2) { it * 2 }
    .take(5).toList()              // [2, 4, 8, 16, 32]——take 截断无限
listOf(1, 2, 3).asSequence()
    .takeWhile { it < 2 }.toList() // [1]
generateSequence(1) { it + 1 }
    .any { it > 100 }              // true——命中即停
sequence { yield(0); yieldAll(listOf(1, 2)) }
    .toList()                      // [0, 1, 2]
```

### 4. 性能对比（本机预期行为：JVM、200 万元素、filter→map→take(5)）

```kotlin
val big = (1..2_000_000).toList()

big.filter { it % 2 == 0 }.map { it * 2 }.take(5)        // 急切：全量过滤+映射，两个百万元素中间集合
big.asSequence().filter { it % 2 == 0 }.map { it * 2 }.take(5).toList()
```

这里不提供未经本轮复现的毫秒数。急切版先过滤与映射全部数据；该 Sequence 管道只需检查到第 10 个输入便取得五个偶数。实际耗时还取决于 JVM、输入形状和测量方法。

以下完整标准库程序验证“逐元素流水线”和短路边界。它不测量耗时，也不涉及 Compose 或 Android：输出中的访问记录是语义证据，而不是性能基准。

<!-- p1-runtime-case: kotlin-sequence-short-circuit -->
```kotlin
fun main() {
    val eagerSeen = mutableListOf<Int>()
    val eager = listOf(1, 2, 3, 4, 5)
        .map { eagerSeen += it; it * 2 }
        .first { it > 4 }

    val lazySeen = mutableListOf<Int>()
    val lazy = listOf(1, 2, 3, 4, 5)
        .asSequence()
        .map { lazySeen += it; it * 2 }
        .first { it > 4 }

    check(eager == 6 && lazy == 6)
    check(eagerSeen == listOf(1, 2, 3, 4, 5))
    check(lazySeen == listOf(1, 2, 3))
    println("Sequence short-circuit contracts passed")
}
```

## ⚠️ 常见陷阱

- ❌ 把"Sequence 惰性"理解成"能随便存起来反复用"——**单次迭代限制确实存在，但只作用于一次性来源**：`iterator().asSequence()`（预期行为第二次 `toList()` 抛 `IllegalStateException: This sequence can be consumed only once.`）与 `.constrainOnce()` 标记的序列。
  ✅ 需要多次消费先 `toList()` 固化；接收 Sequence 参数且来源不可控时，应明确只消费一次或允许重复的契约；不能对未知或无限来源直接 toList()。
- ❌ 反向误解：以为 `listOf(...).asSequence()` 也只能迭代一次——**预期行为可重复迭代**（集合 backed 与常见带 seed 的 generateSequence、sequence 构建器可重新迭代；某些 generateSequence 重载或一次性来源只允许一次消费，预期行为 `sequence{}` 第二次 `toList()` 重新产出 `[1, 2]`）。
  ✅ 但"可重复"= 每次迭代**从头重放**：预期行为同一序列迭代两次，`map` 里的 lambda 执行次数 ×2。
- ❌ 在 Sequence 的 `map`/`onEach`/构建器里写副作用（发请求、写状态）——惰性意味着**不迭代就一行不跑、迭代几次就跑几次**（预期行为 `sequence { sideEffect(); yield(1) }` 未迭代时构建体不执行）。
  ✅ 副作用与数据变换分离：先 `toList()` 固化再处理；异步事件流用 `Flow`（可取消、可背压，见 [协程与 Flow API 全表](./03-coroutines-flow-api.md)）。
- ❌ 把 Sequence 存进字段/参数"以后再用"——冷管道不触发就永远不执行，且可能是一次性的。
  ✅ 短生命周期内创建 → 消费；跨层传数据用集合或 Flow。
- ❌ 小集合（几十条）也套 `asSequence()`——迭代器等额外成本可能抵消收益，需按负载测量。
  ✅ 经验阈值：集合大（千级以上）+ 多步链 + 短路/取头部才用；否则可读性优先直接链集合。

<!-- full-library-explanation -->
## 惰性不等于恒定内存、异步或总是更快

`sorted()` 虽返回 Sequence，但要消费有限来源并缓存排序数据后才能给出首项；无限序列先 sorted 再 take 不会因为最后只要一项就完成。distinct 也需要记录已见元素。Sequence 的 lambda 仍在调用线程同步运行，不会自动让 Android 主线程免于阻塞。

练习：对 1 到 10 过滤偶数后取前五项，在 filter 内记录访问值。反馈：必须检查到 10，不能写成“只处理 9 项”。再将 take 放到 filter 前，输出会变成 2、4，证明算子顺序也是需求的一部分。

需要性能结论时，应固定输入、预热、重复测量并验证两种实现结果相同。短路能减少工作量，但不能把一个特定输入的结论推广成“所有 Sequence 都比 List 快”。参考 [官方序列指南](https://kotlinlang.org/docs/sequences.html)。

## 🔗 相关条目

- 📄 **[集合操作算子导览](./09-collections-operations.md)** - 急切版算子的完整字典
- 📄 **[协程与 Flow API 全表](./03-coroutines-flow-api.md)** - 异步世界的"惰性序列"：冷流、可挂起、可取消
- 📄 **[Lambda 与高阶函数](./08-lambdas-higher-order.md)** - 算子 lambda 的写法约定
- 📄 **[可空性与集合 API 速查](./02-null-safety-collections.md)** - Sequence 与 Flow 的对应关系表
- 🌐 **[Sequence（官方 API 文档）](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.sequences/-sequence/)** - 权威参考
- 🌐 **[Sequences 官方指南](https://kotlinlang.org/docs/sequences.html)** - 惰性求值与操作顺序详解

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
