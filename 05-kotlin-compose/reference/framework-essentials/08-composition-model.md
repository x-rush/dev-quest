# @Composable 与组合模型

> Composable 函数的本质（编译器插件改写）、组合与重组的关系、调用上下文限制、重组局部性、跳过与稳定性契约的衔接

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Composable` `#组合模型` `#编译器插件` `#重组局部性` |
| **更新日期** | `2026年9月` |

> 本文属 Compose 框架层：API 行为按官方文档核对书写，**未实测（无 Android 环境）**，不编造参数名；纯 Kotlin 断言见语言概念篇。

---

## 📌 定义

`@Composable` 标注的函数**不是普通函数**：Kotlin/Compose 编译器插件会在编译期改写它——注入 `Composer` 参数、把函数体切成可重启的分组（restartable group）、为参数生成可跳过（skippable）的比较代码。它描述的是"UI 在给定状态下应该长什么样"，由 Compose 运行时决定何时、以何顺序、执行几次。

三个核心概念：

- **组合（composition）**：首次执行 Composable 函数树，把"组合点"（调用位置）与结果记录进运行时的 SlotTable（组合记录）。
- **重组（recomposition）**：状态变化后，重新执行**读取了该状态**的 Composable，diff 后最小化写入界面。
- **组合局部性（重组范围）**：重组的粒度不是整个页面，而是**读取状态的最近重组作用域**——状态在哪里被读，重启范围就止于哪里。

## 📖 语法与签名

```kotlin
// 源码里你写的
@Composable
fun Counter(count: Int) {
    Text("点击了 $count 次")
}

// 编译器插件改写后的等价形态（示意，非真实产物）
fun Counter(count: Int, composer: Composer, changed: Int) {
    composer.startRestartGroup(/* 位置 key */)
    // 按参数比较决定跳过；把调用记录写入 SlotTable
    if (changed == 0 && composer.skipping) { /* 跳过函数体 */ }
    else { Text("点击了 $count 次", composer, ...) }
    composer.endRestartGroup()?.updateScope { c, _ -> Counter(count, c, changed) }
}
```

规则速查：

| 规则 | 说明 |
|------|------|
| 只能在组合上下文调用 | 仅 `@Composable` 函数（或 lambda 参数为 `@Composable` 的高阶函数）体内可调用 |
| 与 `suspend` 正交 | Composable 内不能直接调 suspend 函数（桥接见 [副作用 API](./03-side-effects.md) 的 `LaunchedEffect`）；suspend 内也不能调 Composable |
| 执行模型三不保证 | 不保证顺序（可乱序）、不保证次数（可跳过/重复）、不保证线程（官方文档明确可能并行） |
| 通常返回 `Unit` | UI 是状态的函数；要"把值给 UI"，用参数与状态提升，不是返回值 |
| 条件/循环中调用合法 | 编译器用**调用位置 + `key()`** 识别组合点身份，不必手写"渲染函数返回视图树" |

跳过（skippability）与稳定性的判定规则——参数比较的前提——完整展开见 [重组与稳定性速查](./04-recomposition.md)。一句话：`@Stable`/`@Immutable` 是向编译器承诺"该类型的相等性可比较、可用来跳过"，跳过失效的常见根源是不稳定参数。

## 💡 示例

```kotlin
// 1. 普通高阶函数的 lambda 里不能调 Composable（编译错误）
fun buildList2(items: List<String>): List<String> =
    items.map { Text(it) }            // ❌ @Composable invocations are only allowed
                                      //    from the context of a @Composable function

// ✅ 需要"组合中生成"时，在组合上下文里调用
@Composable
fun ItemList(items: List<String>) {
    Column {
        items.forEach { item -> Text(item) }   // ✅ 处于组合上下文
    }
}

// 2. 重组局部性：状态读在哪，重启范围就在哪
@Composable
fun Screen(user: User) {
    Column {
        Header(user.name)                      // name 不变 → 被跳过
        var liked by remember { mutableStateOf(false) }
        LikeButton(liked, onLike = { liked = !liked })   // liked 变化 → 只重启这里
        // Footer 不读 liked，完全不受影响
    }
}

// 3. 循环中调用：用 key() 固定身份，避免插入/删除项时状态错位
@Composable
fun MessageList(messages: List<Message>) {
    Column {
        messages.forEach { msg ->
            key(msg.id) {                      // 身份 = msg.id，而非"第 i 个调用位置"
                MessageRow(msg)
            }
        }
    }
}
```

## ⚠️ 常见陷阱

- ❌ 把 Composable 函数当普通函数手动调用（`val node = Counter(3)`）、缓存其结果、或在一个函数里"调用两次拼起来"。
  ✅ 只在组合上下文调用；组合结果由运行时持有，不由你持有。
- ❌ 依赖执行顺序与次数（在 Composable 函数体里写计数器、发请求、改全局变量）——重组随时跳过或重复执行，行为随跳过漂移。
  ✅ 副作用交给 [副作用 API](./03-side-effects.md)（`LaunchedEffect`/`DisposableEffect`/`SideEffect`）。
- ❌ 以为"参数没变就一定跳过"——前提是**参数类型稳定**：来自其他模块的无注解类、含 `List`/`Map` 接口属性的 data class 默认不稳定，整条调用链跳过失效。
  ✅ `@Immutable`/`@Stable` 标注 + 保持 `equals` 与公开属性一致；细节与度量见 [重组与稳定性速查](./04-recomposition.md)。
- ❌ 循环/条件分支里渲染同质子项时不给 `key()`——删除中间一项时，后续项按"调用位置"复用，`remember` 状态整体错位。
  ✅ `key(id) { ... }` 固定身份（LazyColumn 里对应 `items(key = { it.id })`）。
- ❌ 在 Composable 函数体内直接调用 suspend 函数（编译错误：挂起调用只能在协程内）。
  ✅ `LaunchedEffect(key) { suspendFun() }`；事件回调里用 `rememberCoroutineScope().launch { }`。

## 🔗 相关条目

- 📄 **[重组与稳定性速查](./04-recomposition.md)** - 跳过条件与 @Stable/@Immutable 的完整判定规则
- 📄 **[Compose 状态 API](../language-concepts/04-compose-state-api.md)** - remember/derivedStateOf/CompositionLocal/`key()`
- 📄 **[副作用 API](./03-side-effects.md)** - 组合世界里的"安全出口"
- 📄 教程：[Composable 与状态](../../basics/04-composables-state.md)
- 🌐 **[Thinking in Compose（官方文档）](https://developer.android.com/develop/ui/compose/mental-model)** - 组合/重组/执行模型权威解释
- 🌐 **[Compose 编译器（官方文档）](https://developer.android.com/develop/ui/compose/compiler)** - 插件行为与稳定性推断

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
