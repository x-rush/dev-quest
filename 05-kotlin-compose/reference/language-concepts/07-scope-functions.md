# 作用域函数速查

> let / run / apply / also / with 五个作用域函数 + takeIf/takeUnless：临时作用域内访问对象、按"块内引用 + 返回值"选型的字典

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#作用域函数` `#let` `#apply` `#also` `#with` `#run` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

作用域函数：对某个对象开一个**临时作用域**执行代码块。五者差异只有两点——

1. 块内用 `it`（参数引用）还是 `this`（receiver）
2. 返回 **lambda 结果**还是 **receiver 本身**

选型口诀：**要对象用 apply/also，要结果用 let/run/with；链式传参用 it（let/also），构建配置用 this（apply/run）**。

## 📖 语法与签名

| 函数 | 块内引用 | 返回值 | 典型用途 |
|------|---------|--------|---------|
| `let` | `it` | lambda 结果 | 空安全分支、结果变换 |
| `run` | `this` | lambda 结果 | 计算并产出结果 |
| `with` | `this` | lambda 结果 | 对同一对象批量操作（非扩展，普通函数） |
| `apply` | `this` | **receiver** | 对象构建 / 配置（builder 风格） |
| `also` | `it` | **receiver** | 副作用旁路（日志、校验），不打断链 |
| `takeIf` / `takeUnless` | `it` | 条件满足返回 receiver，否则 `null` | 链中条件筛选 |

```kotlin
inline fun <T, R> T.let(block: (T) -> R): R
inline fun <T, R> T.run(block: T.() -> R): R
inline fun <T, R> with(receiver: T, block: T.() -> R): R
inline fun <T> T.apply(block: T.() -> Unit): T
inline fun <T> T.also(block: (T) -> Unit): T
inline fun <T> T.takeIf(predicate: (T) -> Boolean): T?
```

## 💡 示例

```kotlin
// let：空安全 + 变换
user?.let { bindView(it) }                    // 仅在非空时执行

// apply：构建配置（Intent / Bundle / Paint 等）
val intent = Intent(context, DetailActivity::class.java).apply {
    putExtra("id", noteId)
    flags = Intent.FLAG_ACTIVITY_NEW_TASK
}

// also：旁路日志，不打断链
val notes = mutableListOf<Note>().also { log("created: $it") }

// with：同一对象批量操作
with(titleView) { text = title; visibility = VISIBLE }

// 组合：takeIf + let + Elvis 做参数校验
val id = intent.getStringExtra("id")?.takeIf { it.isNotEmpty() } ?: return
```

## ⚠️ 常见陷阱

- `apply` / `run` 块内 `this` 与外层 receiver 同名时易写错对象；嵌套时用 label（`this@outer`）消歧。
- `let` 返回 lambda 结果：块内**最后一行表达式即返回值**，末尾误加一条语句会悄悄改变返回类型。
- 作用域函数嵌套超过两层可读性崩塌——链式场景优先提取具名中间变量。
- `with` 不是扩展函数，可空 receiver 无法 `?.with(...)`——改用 `run` 或先判空。
- 同一条链里混用 `it` 与 `this` 容易混淆引用目标，保持风格一致。

## 🔗 相关条目

- 📄 [可空性与集合 API](./02-null-safety-collections.md) — `?.let` 组合的空安全语境
- 📄 [扩展函数与扩展属性](./06-extension-functions.md)
- 📄 [Lambda 与高阶函数](./08-lambdas-higher-order.md) — 作用域函数的函数类型本质
- 📄 教程：[Kotlin 语法基础 - 作用域函数速览](../../basics/03-kotlin-syntax-essentials.md)
