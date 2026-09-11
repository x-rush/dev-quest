# 重组优化 - 稳定性、derivedStateOf 与 key

> **文档简介**: 深入 Compose 重组机制：为什么组件会被跳过（skippable）、稳定性契约如何影响性能、derivedStateOf/key 的正确用法与度量手段
>
> **目标读者**: 已有真实项目经验、遇到列表卡顿或重组风暴的中高级学习者
>
> **前置知识**: [Compose 进阶](../../frameworks/02-compose-advanced.md)、[Compose 状态 API 详解](../../reference/language-concepts/04-compose-state-api.md)、[应用架构](../architecture/01-app-architecture.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 深度解释（advanced-topics） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#recomposition` `#stability` `#derived-state` `#lazy-list` |
| **更新日期** | `2026年9月` |

---

## 1️⃣ 重组与"跳过"

重组 = 重新执行读取了已变化状态的 Composable 函数。为控制成本，Compose 尽量**跳过**不必重跑的函数——
但前提是它能保证"入参没变"：

- 入参全部**稳定（stable）**且 equals 相等 → 可跳过
- 任一入参**不稳定（unstable）** → 永远不可跳过，每次父级重组都会连带重跑

**稳定性契约**：类型须保证"equals 结果与组合时读取的字段一致，且公开字段可追踪"。
满足者：基本类型、String、Function 类型、`@Immutable` / `@Stable` 标注类、
所有公开属性为 val 的 data class（属性类型也须稳定）。

不稳定常客：`List/Map`（接口可变）、`Application`/`Context` 引用、任何"Compose 不认识"的第三方类。

## 2️⃣ 度量先行：重组计数与编译器指标

优化前先量化（工具用法见[开发工具链](../../frameworks/04-devtools.md)）：

1. Layout Inspector 打开 **recomposition counts**，找到高频重组组件
2. 开启 compose compiler metrics，找 `skippable = 0` 的函数及其不稳定参数
3. Macrobenchmark/系统追踪确认掉帧与重组的因果关系

## 3️⃣ 修复不稳定性

```kotlin
// ❌ List 是接口（可能可变）→ 参数不稳定 → UserRow 永不跳过
@Composable
fun UserRow(user: User, tags: List<String>) { /* ... */ }

// 修复 A：切不可变集合（kotlinx.collections.immutable）
@Composable
fun UserRow(user: User, tags: ImmutableList<String>) { /* ... */ }

// 修复 B：把集合包进 @Immutable 模型（承诺不变，自担契约）
@Immutable
data class UserUi(val name: String, val tags: List<String>)

// 修复 C：集合内容确实需要变化时，缓存到 State 让"引用"稳定
@Composable
fun Chat(messages: List<Message>) {
    // ❌ messages.sorted() 每次重组产生新引用
    // ✅ 只有输入真的变化才重算
    val sorted by remember(messages) { derivedStateOf { messages.sorted() } }
    LazyColumn { items(sorted, key = { it.id }) { MessageRow(it) } }
}
```

## 4️⃣ derivedStateOf：从"宽状态"派生"窄状态"

原理：`derivedStateOf` 只在其**计算结果**变化时通知读取方，把高频上游写入收敛成低频下游重组。

```kotlin
@Composable
fun ContactList(contacts: List<Contact>, query: String) {
    // query 每敲一个字母都变（高频），但"过滤结果"多数时候不变
    val filtered = remember(query) {
        derivedStateOf { contacts.filter { it.name.contains(query, ignoreCase = true) } }
    }

    // 另一典型：滚动是否过阈值——firstVisibleItemIndex 高频变化，布尔值却稳定
    val listState = rememberLazyListState()
    val showFab by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }

    Column {
        LazyColumn(state = listState) { /* ... */ }
        AnimatedVisibility(visible = showFab) { Fab() }
    }
}
```

判断口诀：**当下游关心的"结果"与上游"变化的频率"需要解耦时，才用 derivedStateOf**；
单纯存值用 `remember` 即可（两种 API 的完整对比见
[Compose 状态 API 详解](../../reference/language-concepts/04-compose-state-api.md)）。

## 5️⃣ key：给 Lazy 列表项与组合块"身份"

```kotlin
LazyColumn {
    // key 缺失：删除中间一项后，后续项按位置复用，动画错乱、内部 remember 状态串位
    items(messages, key = { it.id }) { message ->     // ✅ 身份 = 数据 id，不是位置
        MessageRow(message)
    }
}

// key() 也可以包裹任意组合块：id 不变则整块跳过重组
@Composable
fun Avatar(userId: String) {
    key(userId) {          // userId 变化才重组内部
        AsyncImage(model = "https://cdn/avatar/$userId.png", contentDescription = null)
    }
}
```

## 6️⃣ 延迟读取：把状态消费推到 lambda 里

```kotlin
@Composable
fun ChatScreen(messages: List<Message>) {
    val listState = rememberLazyListState()

    // offset(lambda) 把读取推迟到布局/绘制阶段，滚动时零重组
    Box(Modifier.offset { IntOffset(0, listState.firstVisibleItemScrollOffset) })
}
```

同一原理的兄弟用法：颜色/透明度等高频动画值走 `graphicsLayer { }` / `drawBehind { }` 读取；
对比之下，在组合期直接读取这些值（如 `Modifier.alpha(state.value)`）会让每次变化触发整层重组。

## 7️⃣ 工程级补充：Baseline Profiles

重组快只是一半；首帧前的代码加载（类校验/JIT）也决定流畅度。
Baseline Profile 让核心路径（首屏、列表滚动）预编译，冷启动与滚动开销显著下降——
生成与验证方法见[启动与内存优化](02-startup-memory.md)。

## 🎨 最佳实践

### ✅ 推荐

- 稳定性问题在**模型层**解决（@Immutable 模型/不可变集合），不在调用点打补丁
- Lazy 列表项一律提供稳定 `key`
- 每次优化前后用同一组指标（重组计数/帧数据）对比验收

### ❌ 避免陷阱

- 到处加 `@Stable` 说谎——契约破坏后跳过机制会产出**错误 UI**，比慢更糟
- 无差别 `derivedStateOf`/多层 `remember`：复杂度暴涨而收益趋零
- 在 `@Composable` 里 new 出 List/Filter 链却不加 remember key，重组即重算

## 🔗 相关文档

- 📖 概念字典：[Compose 状态 API 详解](../../reference/language-concepts/04-compose-state-api.md) ｜ [重组与稳定性](../../reference/framework-essentials/04-recomposition.md) ｜ [Compose 核心组件速查](../../reference/framework-essentials/01-compose-essentials.md)
- 📖 操作指南：[开发工具链](../../frameworks/04-devtools.md)（度量工具） ｜ [新闻阅读器](../../projects/03-news-reader.md)（key 实战）
- 🎓 延伸解释：[启动与内存优化](02-startup-memory.md) ｜ [应用架构](../architecture/01-app-architecture.md)
