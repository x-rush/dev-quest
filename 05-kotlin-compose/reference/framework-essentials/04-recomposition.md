# 重组与稳定性速查

> **阅读准备**：会用 remember 和 mutableStateOf，能区分普通变量与被观察的状态读取。

> Compose 把"状态 → UI"重新执行的过程：三阶段模型、跳过（skip）条件、@Stable / @Immutable 稳定性契约——一切性能优化的概念底座

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#重组` `#跳过` `#稳定性` `#Stable` `#Immutable` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

- **重组（recomposition）**：状态变化后，Compose 重新执行受影响的 Composable 函数、更新组合树的过程。它是**尽力而为**的：不保证次数与时机，随时可能被跳过。
- **跳过（skip）**：函数所有参数未变且该函数可跳过时，整个调用被跳过、不重执行。
- **稳定类型（stable type）**：满足契约的类型——公开属性要么不可变，要么 Compose 能追踪其变化，且 `equals` 结果与公开属性一致。稳定性决定"参数是否变了"能否被可靠判定，从而决定能否跳过。

## 📖 语法与签名

```
UI = f(state)
状态写入 → 使读取该状态的 Scope 失效 → 重组受影响的 Scope → diff 后最小化写入
```

三个阶段：**组合**（执行 Composable 生成树）→ **布局**（测量与摆放）→ **绘制**。在哪个阶段读、在哪个阶段写，决定重启范围——窄读窄写优先。

稳定性契约与注解：

```kotlin
@Immutable   // 声明：公开属性永不变化（纯数据类）
@Stable      // 声明：可变但可追踪、equals 结果稳定
```

编译器判定规则：

- `val` + 原始类型 / String / 函数类型 / lambda → 稳定
- `data class` 全部公开属性稳定 → 稳定；含 `List` / `Map` 等**接口**类型 → 默认视为**不稳定**（接口无法证明实现稳定），应先保证数据契约，不能仅用 @Immutable 掩盖可变性；跳过还受编译器模式影响
- `MutableState<T>` 本身稳定（内部值被框架追踪）

## 💡 示例

```kotlin
// 1. 参数未变且类型稳定 → 整个函数被跳过
@Composable
fun Avatar(name: String) { /* ... */ }

// 2. 用 @Immutable 把"接口参数"收紧为可跳过
@Immutable
data class UserUi(val id: Long, val name: String, val avatarUrl: String)

// 3. 窄化读取：把 State 读取下推到最小 Scope
@Composable
fun Screen(state: ScreenState) {
    val query by state.queryFlow.collectAsStateWithLifecycle()
    SearchBar(query)            // query 在 Screen 中被读取，所以 Screen 的相关重启作用域会受影响
}

// 4. 派生值用 derivedStateOf 收窄重启范围
val showButton by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
```

## ⚠️ 常见陷阱

- 重组是尽力而为的：组合体内**禁止写副作用**（见[副作用 API](./03-side-effects.md)），否则行为随跳过与否而漂移。
- 以为 `data class` 一定稳定：含 `List` / `Map` 接口属性、或来自其他模块的无注解类，可能被推断为不稳定，但 strong skipping 等模式会影响能否跳过。
- 新集合身份、lambda 捕获及编译器缓存都会影响跳过；根据编译报告与测量定位，不要机械地全部加 remember。
- 用一个 `mutableStateOf` 包大对象再整对象替换 → 所有读取它的 Scope 全部重启；拆分状态或用 `derivedStateOf` 收窄。
- 优化前不量化：先确认重组热点再动手，度量方法见[重组优化](../../advanced-topics/performance/01-recomposition-optimization.md)。

<!-- full-library-explanation -->
## 稳定性注解是承诺，不是修复按钮

把包含普通可变列表的类型标为 Immutable，不会冻结列表，也不会让写入自动可观察。若事实不符合承诺，框架可能跳过本应更新的 UI。先检查状态是否可观察、数据是否正确替换，再查看编译器报告和性能记录。

当前 Compose 编译器的 strong skipping 模式还允许许多带不稳定参数的可重启函数跳过；不稳定参数通常用实例身份比较，稳定参数按相等性比较，lambda 也可由编译器缓存。因此“含 List 就整条调用链无法跳过”不是普遍规则。[官方 strong skipping 说明](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping)给出了模式与比较规则。

练习：在 Screen 内读取文本状态，与把读取移动到 SearchBar 内分别记录重组。验收：能够指出实际读取发生在哪个重启作用域；只把值作为参数传给 SearchBar，不会把 Screen 中已经发生的读取转移过去。最后检查交互耗时，而非追求重组计数为零。

## 🔗 相关条目

- 📄 [Compose 状态 API](../language-concepts/04-compose-state-api.md) — State / remember / derivedStateOf 全表
- 📄 [副作用 API](./03-side-effects.md)
- 🎓 解释深入：[重组优化](../../advanced-topics/performance/01-recomposition-optimization.md)
- 📄 教程：[Composable 与状态](../../basics/04-composables-state.md)
- 📖 官方文档：[Compose phases](https://developer.android.com/develop/ui/compose/phases)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
