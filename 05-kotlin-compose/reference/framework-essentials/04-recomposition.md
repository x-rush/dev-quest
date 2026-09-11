# 重组与稳定性速查

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
- `data class` 全部公开属性稳定 → 稳定；含 `List` / `Map` 等**接口**类型 → 默认视为**不稳定**（接口无法证明实现稳定），需 `@Immutable` 显式声明
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
    SearchBar(query)            // query 变化只重组 SearchBar，不重组整个 Screen
}

// 4. 派生值用 derivedStateOf 收窄重启范围
val showButton by remember { derivedStateOf { listState.firstVisibleItem > 0 } }
```

## ⚠️ 常见陷阱

- 重组是尽力而为的：组合体内**禁止写副作用**（见[副作用 API](./03-side-effects.md)），否则行为随跳过与否而漂移。
- 以为 `data class` 一定稳定：含 `List` / `Map` 接口属性、或来自其他模块的无注解类，默认不稳定，导致整条调用链跳过失效。
- 每帧创建新 lambda / 新集合传给子组件 → 参数"永远变了"，跳过失效；用 `remember` 包裹或把 lambda 下移。
- 用一个 `mutableStateOf` 包大对象再整对象替换 → 所有读取它的 Scope 全部重启；拆分状态或用 `derivedStateOf` 收窄。
- 优化前不量化：先确认重组热点再动手，度量方法见[重组优化](../../advanced-topics/performance/01-recomposition-optimization.md)。

## 🔗 相关条目

- 📄 [Compose 状态 API](../language-concepts/04-compose-state-api.md) — State / remember / derivedStateOf 全表
- 📄 [副作用 API](./03-side-effects.md)
- 🎓 解释深入：[重组优化](../../advanced-topics/performance/01-recomposition-optimization.md)
- 📄 教程：[Composable 与状态](../../basics/04-composables-state.md)
- 📖 官方文档：[Compose phases](https://developer.android.com/develop/ui/compose/phases)
