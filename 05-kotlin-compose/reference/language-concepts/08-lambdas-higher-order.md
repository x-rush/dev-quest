# Lambda 与高阶函数

> **阅读准备**：普通函数、参数和返回值；理解函数可以作为值传递，再学习接收者 lambda。

> 函数类型、尾随 lambda、带接收者的 lambda——读懂 `Button(onClick = { })` 与 Compose 内容 DSL 的语法基石

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#lambda` `#高阶函数` `#尾随lambda` `#DSL` `#函数类型` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

- **函数类型**：把"函数"当作值的一等公民类型，如 `() -> Unit`、`(Int) -> String`、`Receiver.(P) -> R`。
- **高阶函数**：接收函数类型参数或返回函数的函数。
- **尾随 lambda（trailing lambda）**：函数最后一个参数是函数类型时，lambda 可挪到括号外；唯一实参时连括号一起省略。
- **带接收者的 lambda**：类型 `Receiver.() -> R`，块内可省略前缀直接访问 receiver 成员——Compose 内容槽 `content: @Composable ColumnScope.() -> Unit` 即此模式。

## 📖 语法与签名

```kotlin
// 函数类型变量
val onClick: () -> Unit = { /* ... */ }
val double: (Int) -> Int = { it * 2 }            // 单参数默认命名为 it

// 高阶函数：函数类型作为参数
fun setState(update: (UiState) -> UiState) { /* ... */ }

// 自定义函数式接口（fun interface）可直接用 lambda 构造
fun interface OnItemClick { fun onClick(position: Int) }
val listener = OnItemClick { pos -> /* ... */ }
```

调用约定：

```kotlin
Column {                      // content 是最后一个参数 → 尾随 lambda 挪出括号
    Text("hi")                // this: ColumnScope，成员直接访问
}
```

## 💡 示例

```kotlin
// 1. 事件回调：onClick = { ... } 就是一个 () -> Unit 实参
Button(onClick = { count++ }) { Text("点击 $count 次") }

// 2. 自定义高阶函数：用函数参数描述状态更新
fun updateNote(noteId: Long, transform: (Note) -> Note) {
    notes.replaceAll { if (it.id == noteId) transform(it) else it }
}
updateNote(1) { it.copy(title = "新标题") }

// 3. 带接收者 lambda 实现 mini DSL
class MenuBuilder { fun item(label: String) { /* ... */ } }
fun buildMenu(block: MenuBuilder.() -> Unit) = MenuBuilder().apply(block)
buildMenu {
    item("首页")            // 等价于 this.item("首页")
    item("设置")
}

// 4. 方法引用与 lambda 等价
list.map(::processItem)       // 等价于 list.map { processItem(it) }
```

## ⚠️ 常见陷阱

- **回调捕获旧值**：闭包可捕获变量，但每次组合的参数和局部值可能属于不同执行；长生命周期任务要按需求用 rememberUpdatedState 读取最新回调（见[副作用 API](../framework-essentials/03-side-effects.md)）。
- 裸 return 只在允许非局部返回的 inline lambda 等场景可用；局部返回使用 return@label，不能假设任何 lambda 都能返回外层函数。
- 带接收者 lambda 块内 `this` 与外层 `this` 冲突：需要外层时写 `this@outer`。
- 尾随 lambda 只对**最后一个**函数参数生效——设计自己的 API 时把函数参数放在参数表末尾，否则调用端语法变难看。
- Kotlin 函数类型 ≠ Java SAM：Java 接口可直接传 lambda，Kotlin 侧自定义接口需标 `fun interface` 才能这样用。

<!-- full-library-explanation -->
## 区分“传递动作”和“现在执行”

`onClick = { save() }` 传递回调，点击时才调用；`onClick = save()` 是立即执行并把返回值传入，通常还会类型不匹配。Compose 重组会重新执行组件函数，回调的创建与回调的执行不能混为一谈。

```kotlin
fun main() {
    val values = listOf(1, 2, 3)
    values.forEach {
        if (it == 2) return@forEach
        println(it)
    }
    println("done")
}
// 输出 1、3、done；return@forEach 结束当前这次 lambda 调用
```

练习：把带标签返回换成裸 return，解释在 inline forEach 中为何会提前结束 main。再改成非 inline 自定义高阶函数，观察编译限制。验收：不再把 lambda 的 return 统一理解成循环 break 或外层 return。匿名函数 `fun(...) {}` 的返回规则也应单独区分。

## 🔗 相关条目

- 📄 [扩展函数与扩展属性](./06-extension-functions.md)
- 📄 [作用域函数](./07-scope-functions.md)
- 📄 [Kotlin 关键字与修饰符](./01-kotlin-keywords.md) — `inline` / `suspend` 修饰符
- 📄 [Compose 状态 API](./04-compose-state-api.md) — 状态读取 lambda
- 📄 教程：[Kotlin 语法基础 - Lambda 与尾随 lambda](../../basics/03-kotlin-syntax-essentials.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
