# 扩展函数与扩展属性

> Kotlin 给既有类型"外挂"成员的机制——Compose 生态大量依赖它：Modifier 链、Context 工具、DSL 构建器都建立在扩展之上

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#扩展函数` `#扩展属性` `#receiver` `#Modifier` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

- **扩展函数**：`fun ReceiverType.method(...)` 在类外声明、以成员语法 `receiver.method()` 调用的函数。编译为静态函数，receiver 是第一个参数——**不会修改原类**，没有新成员注入，也没有虚方法分派。
- **扩展属性**：`val ReceiverType.prop: T` 通过自定义 getter 提供计算值；没有 backing field，不能初始化存储。
- **解析规则**：按**编译期静态类型**静态解析；同一签名的成员函数与扩展冲突时**成员胜出**。

## 📖 语法与签名

```kotlin
fun ReceiverType.extensionName(param: P): R          // 扩展函数
val ReceiverType.extensionProp: R get() = ...        // 扩展属性（必须有 getter）
var ReceiverType.mutableProp: R                      // 可变扩展属性需 getter + setter
fun <T> List<T>.genericExt(): T?                     // 泛型扩展
```

- 扩展体内 `this` 指 extension receiver；所在类的成员可省略 receiver 直接调用（dispatch receiver）。
- 两个 receiver 同时可用但名字冲突时，**dispatch receiver（类的成员）优先**，访问扩展 receiver 需要显式 `this@ReceiverType` 或限定。
- 泛型扩展与约束组合（`where` 子句）语法见[泛型与委托属性](./05-generics-delegates.md)。

## 💡 示例

```kotlin
// 1. 工具型扩展：避免 utils 静态调用风格
fun Context.toast(message: String) =
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()

// 2. Compose 生态实例：Modifier 链式扩展（Modifier 的所有能力都是扩展函数）
fun Modifier.cardStyle() = this
    .fillMaxWidth()
    .padding(16.dp)
    .clip(RoundedCornerShape(12.dp))

// 3. 集合泛型扩展
fun <T> List<T>.secondOrNull(): T? = getOrNull(1)

// 4. 扩展属性
val View.isVisible: Boolean get() = visibility == View.VISIBLE
```

## ⚠️ 常见陷阱

- 扩展函数**不能访问 private / protected 成员**——它只是静态语法糖，不是真成员。
- 成员与扩展同名冲突时成员静默胜出，IDE 不报错但行为可能不符预期；避免给别人的类加与成员同名的扩展。
- 扩展按**静态类型**解析：`val x: Base = Derived(); x.ext()` 调用的是 `Base` 的扩展，不是 `Derived` 的——与 override 的多态行为完全不同。
- 顶层扩展会污染全局命名空间：按功能放独立文件并配好包名，或在 object 中收拢。
- 嵌套 lambda 中 `this` 指向最近一层 receiver，需要外层时写 `this@label`。

## 🔗 相关条目

- 📄 [Kotlin 关键字与修饰符](./01-kotlin-keywords.md)
- 📄 [Lambda 与高阶函数](./08-lambdas-higher-order.md) — 带接收者的 lambda 与 DSL
- 📄 [泛型与委托属性](./05-generics-delegates.md) — 泛型扩展与 `where` 约束
- 📄 [可空性与集合 API](./02-null-safety-collections.md) — 集合扩展操作符全表
- 📄 教程：[Kotlin 语法基础 - 扩展函数](../../basics/03-kotlin-syntax-essentials.md)
