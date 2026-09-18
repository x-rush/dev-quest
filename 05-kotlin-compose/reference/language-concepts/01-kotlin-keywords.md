# Kotlin 关键字与修饰符详解

## 从一行 Compose 代码拆开语言能力

前置：函数与变量。`var count by remember { mutableStateOf(0) }` 同时使用 var、属性委托 by、尾随 lambda 与库函数。var/by 是语言结构；remember/mutableStateOf 来自 Compose，不能把它们列成 Kotlin 关键字。

`val items = mutableListOf(1)` 后不能把 items 重新指向另一个列表，但可以 items.add(2)。val 限制重新赋值，不保证深度不可变。nullable 类型把缺失写成 `T?`；`?.` 传播缺失，`?:` 选择回退，`!!` 则把缺失变成运行时失败。

自测：令 name 为 null，预测 `name?.length ?: 0` 的结果为 0；把它换成 `name!!.length` 会失败。随后说明为什么“有默认值”不总是正确业务处理：缺少必填标题时可能应显示错误，而不是默默填空串。

> Compose/Android 开发高频的 Kotlin 关键字速查字典：官方关键字总索引 + 按"声明 → 继承 → 并发 → 其他"分组的高频词条，每个词条包含定义、语法、示例与陷阱。标注（实测）的断言均经本机 kotlinc 2.4.20 编译运行验证

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#关键字` `#修饰符` `#Kotlin` `#语言概念` |
| **更新日期** | `2026年9月` |

## 关键字总索引（官方分类）

按 [官方 Keyword reference](https://kotlinlang.org/docs/keyword-reference.html) 分类：**硬关键字**在任何位置都保留，作标识符必须反引号转义（`` `fun` ``）；**软关键字/修饰符关键字**仅在匹配其语法角色的上下文中保留，可直接作标识符。

| 类别 | 关键字 |
|------|--------|
| 硬关键字（31） | `as` `as?` `break` `class` `continue` `do` `else` `false` `for` `fun` `if` `in` `!in` `interface` `is` `!is` `null` `object` `package` `return` `super` `this` `throw` `true` `try` `typealias` `typeof`* `val` `var` `when` `while` |
| 软关键字（18） | `by` `catch` `constructor` `delegate` `dynamic` `field` `file` `finally` `get` `import` `init` `param` `property` `receiver` `set` `setparam` `value` `where` |
| 修饰符关键字（29） | `abstract` `actual` `annotation` `companion` `const` `crossinline` `data` `enum` `expect` `external` `final` `infix` `inline` `inner` `internal` `lateinit` `noinline` `open` `operator` `out` `override` `private` `protected` `public` `reified` `sealed` `suspend` `tailrec` `vararg` |

> \* `typeof` 为官方保留字，当前无用途。§1-18 覆盖高频词条，§19-35 补全其余硬关键字与常用修饰符。

---

## 1. val / var - 只读与可变变量

### 定义
`val` 声明只读引用（赋值后不可再指向新对象），`var` 声明可变引用。

### 语法和示例
```kotlin
val name: String = "Compose"     // 显式类型
val version = 2.2                // 类型推断为 Double
var counter = 0                  // 可重新赋值
counter++
```

### 陷阱
- `val` 只保证**引用**不变，对象内容仍可变（`val list = mutableListOf(1)` 后仍可 `list.add(2)`）
- Compose 状态惯用 `var x by remember { mutableStateOf(...) }`——`var` 指向 State 引用，变化的是其 value

## 2. fun - 函数声明

### 定义
声明函数；顶层函数、成员函数、扩展函数共用此关键字。

### 语法和示例
```kotlin
fun greet(name: String, greeting: String = "Hello"): String =   // 默认参数 + 单表达式
    "$greeting, $name!"

fun String.shout() = uppercase() + "!"     // 扩展函数

fun main() {
    println(greet(name = "Kotlin", greeting = "Hi"))            // 命名参数
}
```

## 3. class / object / interface - 类型声明

### 定义
`class` 声明类；`object` 声明单例（或伴生/匿名对象）；`interface` 声明接口（可带默认实现）。

### 语法和示例
```kotlin
interface Clickable {
    fun click()
    fun showLog() = println("clicked")       // 接口默认实现
}

class Button(var label: String) : Clickable {
    override fun click() { /* ... */ }
}

object Analytics {                            // 全局单例
    fun track(event: String) { /* ... */ }
}
```

### 陷阱
`object` 单例的生命周期与应用相同——不要在其中持有 Activity Context，否则内存泄漏。

## 4. data - 数据类

### 定义
`data class` 自动生成 `equals`/`hashCode`/`toString`/`copy` 与组件函数（解构用）。

### 语法和示例
```kotlin
data class User(val id: Long, val name: String, val age: Int = 0)

val u2 = u1.copy(name = "Bob")               // 不可变更新
val (id, name) = u1                          // 解构声明
```

### 陷阱
- 主构造函数**必须**至少有一个参数，且所有参数需为 `val`/`var`
- `copy` 是浅拷贝：嵌套可变集合字段复制的是引用

## 5. sealed - 密封类/接口

### 定义
`sealed` 限制继承层级：所有子类必须与父类在同一包（同一编译模块）中，使 `when` 分支可穷尽检查。

### 语法和示例
```kotlin
sealed interface UiEvent {
    data class ShowToast(val message: String) : UiEvent
    data object NavigateBack : UiEvent
}

fun handle(e: UiEvent) = when (e) {          // 无需 else
    is UiEvent.ShowToast  -> showToast(e.message)
    UiEvent.NavigateBack  -> navController.popBackStack()
}
```

### 陷阱
新增子类后忘记补 `when` 分支会直接编译报错——这正是它的价值；跨模块定义子类会编译失败。

## 6. enum class - 枚举

### 定义
有限常量集合，每个值是单例。

### 语法和示例
```kotlin
enum class SortOrder(val label: String) {
    TITLE("按标题"), CREATED("按时间");
}
```

与 sealed 的选择：常量集合且各值不携带不同结构 → enum；各形态携带不同字段/继承自接口 → sealed。

## 7. open / abstract / final - 继承控制

### 定义
Kotlin 类与成员**默认 final**；`open` 允许被继承/重写，`abstract` 强制子类实现。

### 语法和示例
```kotlin
abstract class BaseRepo {
    abstract fun fetch(): List<String>
    open fun onError(e: Throwable) {}        // 可选重写
}

class UserRepo : BaseRepo() {
    override fun fetch() = listOf("a")
}
```

## 8. override - 重写

### 定义
重写父类/接口成员；必须显式标注，且被重写成员需为 `open`/`abstract`。重写后默认仍是 `open`，可加 `final override` 封闭。

### 语法和示例
```kotlin
class ViewModelImpl : ViewModel() {
    final override fun onCleared() { /* 清理资源 */ }
}
```

## 9. companion / init - 伴生对象与初始化块

### 定义
`companion object` 是类级单例成员区（≈ Java 静态成员）；`init` 为主构造时的初始化块。

### 语法和示例
```kotlin
class NotesDatabase private constructor(...) : RoomDatabase() {
    abstract fun noteDao(): NoteDao

    init { /* 首次实例化时执行 */ }

    companion object {
        @Volatile private var INSTANCE: NotesDatabase? = null
        fun get(context: Context): NotesDatabase { /* 双检锁单例 */ }
    }
}
```

## 10. 可见性修饰符：public / private / protected / internal

### 定义
| 修饰符 | 顶层声明可见范围 | 类内成员可见范围 |
|--------|------------------|------------------|
| `public`（默认） | 任何地方 | 任何能见到该类的地方 |
| `internal` | 同一模块 | 同一模块 |
| `protected` | 不可用于顶层 | 本类 + 子类 |
| `private` | 同一文件 | 本类（不含子类） |

### 语法和示例
```kotlin
internal fun logDebug(msg: String) { }      // 仅本模块可见

class Repo {
    private val cache = mutableMapOf<String, Any>()   // 外部不可见
    public val size: Int get() = cache.size           // 只读暴露
}
```

### 陷阱
没有 Java 的"包私有"（package-private）；跨模块隐藏请用 `internal`。

## 11. suspend - 挂起函数

### 定义
标记可被挂起/恢复的函数，只能在协程或其他 suspend 函数中调用。编译器通过状态机实现"非阻塞等待"。

### 语法和示例
```kotlin
suspend fun fetchUser(id: Long): User =
    withContext(Dispatchers.IO) { api.fetch(id) }   // Room/Retrofit 的 suspend 已内置调度
```

### 陷阱
不要在 `runBlocking` 里包业务（会阻塞线程）；也不要为了让普通函数能调用 suspend 而开 `GlobalScope`——应沿调用链上提 suspend 或进入协程作用域。

## 12. inline / noinline / crossinline - 内联

### 定义
`inline` 把函数体与 lambda 参数**复制**到调用点，消除 lambda 对象与调用开销；`noinline` 排除个别 lambda；`crossinline` 允许 lambda 被放局部对象/另一执行上下文（禁用非局部返回）。

### 语法和示例
```kotlin
inline fun <T> List<T>.forEachIndexed2(action: (Int, T) -> Unit) {
    for ((i, item) in withIndex()) action(i, item)
}

inline fun logTime(block: () -> Unit) {       // 标准库 measureNanoTime 的同类手法
    val start = System.nanoTime()
    block()
    println("耗时 ${System.nanoTime() - start} ns")
}
```

### 陷阱
- inline 函数体过大反而膨胀字节码，只适合小工具函数
- inline 的 lambda 可 `return` 外层函数（非局部返回），不想要此行为就加 `crossinline`

## 13. reified - 具化泛型类型

### 定义
与 `inline` 搭配，让泛型参数 `T` 在运行时可见（突破擦除），可直接 `T::class`、`is T`。

### 语法和示例
```kotlin
inline fun <reified T : Activity> Context.startActivity() {
    startActivity(Intent(this, T::class.java))       // 无需传 Class 参数
}

inline fun <reified T> Gson.fromJson(json: String): T =
    fromJson(json, T::class.java)

context.startActivity<DetailActivity>()              // 调用点类型自动具化
```

### 陷阱
仅限 inline 函数；`T` 仍不能当普通对象实例化（无 `T()`）。

## 14. operator / infix - 运算符与中缀重载

### 定义
`operator` 重载约定运算符（`+`、`[]`、`++` 等）；`infix` 允许单参函数省点号调用。

### 语法和示例
```kotlin
data class Money(val cents: Long) {
    operator fun plus(other: Money) = Money(cents + other.cents)
    operator fun get(index: Int) = cents.toString()[index]
}

infix fun Int.pow2(n: Int): Int = toDouble().pow(n).toInt()

val total = Money(100) + Money(50)      // + 即 plus
val eight = 2 pow2 3                     // 中缀调用
```

## 15. lateinit - 延迟初始化

### 定义
允许 `var` 属性延后初始化而不置 null；访问未初始化属性抛 `UninitializedPropertyAccessException`。

### 语法和示例
```kotlin
class LoginFlowTest {
    private lateinit var scenario: ActivityScenario<MainActivity>   // 框架注入场景
    @Before fun setUp() { scenario = ActivityScenario.launch(MainActivity::class.java) }
}
```

### 陷阱
只能修饰 `var`、非空、非基本类型；与 Compose 无缘（UI 状态用 remember/stateIn）；可用 `::scenario.isInitialized` 判断。

## 16. const - 编译期常量

### 定义
`const val` 要求编译期已知的原始类型/String，位于顶层或 object/companion 中。

### 语法和示例
```kotlin
const val DEFAULT_PAGE_SIZE = 20
object Routes {
    const val LIST = "list"
    const val DETAIL = "detail/{taskId}"
}
```

### 陷阱
Room/Intent 等注解与 Bundle key 用 `const` 可避免运行时构造；不要拿 const 存对象——它只支持字面量。

## 17. by - 委托

### 定义
两个用途：①类接口委托 `class A by B()`；②属性委托 `val x by lazy { ... }`。

### 语法和示例
```kotlin
val config: Config by lazy { loadConfig() }          // 首次访问才计算
val vm: NotesViewModel by viewModels()                // AndroidX 委托
class BaseImpl : Base { /* ... */ }
class Derived(b: Base) : Base by b                    // 接口实现转发
```

> 📖 `by lazy`/`by viewModels` 的完整机制见 [泛型与委托属性](./05-generics-delegates.md)。

## 18. when / if - 表达式化控制流

### 定义
Kotlin 中 `when` 与 `if` 是**表达式**，有返回值，可直接赋值（Go 的 switch 无此能力）。

### 语法和示例
```kotlin
val label = when {
    score >= 90 -> "优秀"
    score >= 60 -> "及格"
    else -> "不及格"
}
```

## 19. for / while / do - 循环

### 定义
`for` 遍历任何提供 `iterator()` 的对象（没有 C 风格三段式循环）；`while` / `do while` 与 Java 同形，`do while` 先执行一次再判断。

### 语法和示例
```kotlin
for (i in 1..3) print(i)                       // 123
for ((index, item) in list.withIndex()) { }    // 下标 + 元素解构
for (c in "abc") print(c)                      // 字符串可迭代
while (x < 10) { x++ }
do { loadPage() } while (hasMore)
```

### 陷阱
- 倒序/跳步用区间运算（`for (i in 10 downTo 1 step 2)`），不要手写索引循环
- `do while` 的条件里可以使用**循环体内声明的变量**（官方语法作用域规则，Java 做不到）

## 20. in / !in / is / !is - 归属与类型判断

### 定义
`in` 判断成员/区间归属（正向调用 `contains`），`!in` 取反；`is` 做类型判断并在通过后**智能转换**，`!is` 取反。四者均为硬关键字；泛型处 `in`/`out` 是型变修饰符（见 [泛型与委托属性](./05-generics-delegates.md)）。

### 语法和示例
```kotlin
"a" in listOf("a", "b")            // true
3 !in 1..2                          // true

val v: Any = "text"
check(v !is Int)                    // （实测）
if (v is String) check(v.length == 4)   // is 通过后 v 已智能转换为 String
when (v) {
    is Int -> println(v + 1)
    is String -> println(v.uppercase()) // TEXT
    else -> println("其他类型")
}
```

### 陷阱
智能转换在属性可能被别处修改（自定义 getter、open 属性）时失效——必要时用局部变量中转或显式 `as`。

## 21. as / as? - 类型转换

### 定义
`as` 不安全转换，失败抛异常（类型不符实测抛 `ClassCastException`）；`as?` 安全转换，失败返回 null。

### 语法和示例
```kotlin
val s = obj as String                 // 失败即抛（实测 ClassCastException）
val len = (obj as? String)?.length    // 失败得到 null（实测）
val t = n as? String ?: "<unknown>"   // 安全转换 + Elvis 兜底
```

### 陷阱
- 可空目标写 `as String?`——`as` 转非空类型遇到 null 也会抛异常
- `as? ... !!` 连用是坏味道：先想想为什么编译器的类型推断不知道这个类型

## 22. try / catch / finally / throw - 异常

### 定义
`try` 是**表达式**（取 try 体或首个命中的 catch 分支的值）；`throw` 也是表达式（类型 `Nothing`，常与 Elvis 搭配）。Kotlin 没有受检异常；`catch`/`finally` 是软关键字。

### 语法和示例
```kotlin
val n = try { input.toInt() } catch (e: NumberFormatException) { 0 }   // try 取值

val name = raw ?: throw IllegalArgumentException("name 必填")          // throw 作表达式
```

### 陷阱
- `finally` 中 `return` 会吞掉 try/catch 的返回值与异常——只放清理逻辑
- `catch (e: Exception)` 一网打尽再静默吞掉，等于把崩溃推迟到更难定位的地方

## 23. return / break / continue - 跳转与标签

### 定义
三者在任意循环/lambda 前加 `label@` 标签即可精确跳转：`return@label` / `break@label` / `continue@label`。inline 函数的 lambda 里裸 `return` 直接退出外层函数（非局部返回，见 §12）。

### 语法和示例
```kotlin
// 标签跳转（实测：hits == 2）
var hits = 0
loop@ for (i in 1..5) {
    for (j in 1..5) {
        if (j == 3) continue@loop     // 直接进入外层下一轮
        if (i == 2) break@loop        // 连外层一起跳出
        hits++
    }
}

// 非局部返回：forEach 是 inline，return 退出整个函数
fun findUser(id: Long): User? {
    users.forEach { if (it.id == id) return it }
    return null
}
```

### 陷阱
- 非 inline lambda 里裸 `return` 编译错误——用 `return@函数名`（隐式标签）或自定义标签返回到 lambda
- 隐式标签默认与接收 lambda 的函数同名（`return@forEach`）；多层嵌套时显式命名标签更可读

## 24. this / super - 自引用与父类引用

### 定义
`this` 指当前接收者；多个接收者（扩展函数、inner 类、带接收者的 lambda）并存时用 `this@标签` 限定。`super` 调用父类实现；多接口都提供同名默认实现时用 `super<接口名>.成员` 显式选择。

### 语法和示例
```kotlin
class Outer2 {
    val tag = "outer"
    inner class Inner2 {
        fun who() = this@Outer2.tag        // 限定到外层接收者（实测）
    }
}

interface A { fun who() = "A" }
interface B { fun who() = "B" }
class C : A, B {
    override fun who() = super<A>.who() + super<B>.who()   // 实测 == "AB"
}
```

### 陷阱
两个接口提供同名默认实现而**不写** `super<A>` 时直接编译报错——编译器强制你表态，不会随机选一个。

## 25. package / import - 包与导入

### 定义
`package`（硬关键字）声明归属；`import`（软关键字）导入声明，支持 `as` 别名。`kotlin.*`、`kotlin.io.*` 等标准包与 JVM 平台的 `java.lang` 默认已导入。

### 语法和示例
```kotlin
package com.example.app

import androidx.compose.runtime.Composable
import kotlin.math.PI as PI2      // 别名：与项目内已有 PI 冲突时改名使用
```

### 陷阱
- Kotlin 没有 Java 的 `import static`——顶层函数/属性直接 `import 包名.声明名`
- 编译器不强制包与目录一致，但跨模块协作请保持惯例一致

## 26. true / false / null - 字面量关键字

### 定义
`true`/`false` 是 `Boolean` 的两个字面量；`null` 是所有可空类型的"空值"字面量，只能赋给可空类型——这是空安全系统的基石（详见 [可空性与集合 API](./02-null-safety-collections.md)）。

### 语法和示例
```kotlin
val ok: Boolean = true
val no: Boolean = false
val name: String? = null            // 非空类型不能赋 null
```

## 27. typealias - 类型别名

### 定义
为既有类型起新名字（硬关键字，1.7 起从修饰符升级）。别名**不引入新类型**，与原类型完全等价互换；给复杂函数类型命名是最常见用法。

### 语法和示例
```kotlin
typealias Handler = (Int, String) -> Unit        // 顶层（实测）
typealias Users = Map<String, User>

class Repo {
    typealias Callback = (Boolean) -> Unit       // 类内嵌套（1.7+ 稳定）
}

// fun f() { typealias Local = Int }             // 函数体内：实验特性，需 -Xlocal-type-aliases（实测编译错误）
```

### 陷阱
别名不是新类型：`typealias Meters = Double` 后两者可互相赋值、类型检查不拦——要"零开销 + 类型安全"用 `@JvmInline value class`（§28）。

## 28. value class - 值类

### 定义
`@JvmInline value class`（软关键字 `value`）包装单个 `val` 属性，编译器尽量把包装**内联消除**（不分配对象），以零运行时开销获得类型安全包装。

### 语法和示例
```kotlin
@JvmInline value class Meters(val value: Double)   // 实测
@JvmInline value class TaskId(val id: Long)

fun fetch(id: TaskId) { /* 参数层即文档：Double 传不进来 */ }
```

### 陷阱
- 只能有一个主构造属性；**不能声明为局部类或内部类**（实测编译错误：value class cannot be local or inner）
- 实现为接口/被当 `Any?` 使用等场景会触发实际装箱，`===` 身份语义随之改变——语义敏感处以官方内联规则为准

## 29. inner - 内部类

### 定义
Kotlin 嵌套类**默认不持有外部实例**（≈ Java 静态嵌套类）；`inner` 让嵌套类持有外部实例引用并可访问其成员。

### 语法和示例
```kotlin
class Outer {
    private val tag = "outer"
    inner class Inner {
        fun ping() = tag            // inner 才能访问外部实例成员（实测）
    }
}
// 无 inner 的嵌套类访问不到外部实例成员，直接编译错误
```

### 陷阱
`inner` 类隐式持有外部引用，外部实例生命周期被内部对象拉长即泄漏（Android 经典问题）——不需要外部实例就不加 `inner`。

## 30. vararg - 可变参数

### 定义
标记"可变数量"参数，函数体内类型为 `Array<out T>`（基本类型为对应 `IntArray` 等）；调用处用展开运算符 `*` 传入数组，并可与普通实参混用。

### 语法和示例
```kotlin
fun total(vararg nums: Int) = nums.sum()

total(1, 2, 3)
val arr = intArrayOf(4, 5)
total(*arr, 6)                     // 展开 + 追加实参（实测 == 15）
```

### 陷阱
- 一个函数只能有一个 `vararg` 参数；若不在末位，其后的参数必须命名传参
- `vararg xs: String` 在函数体内是 `Array<out String>`，遍历取值前先记住这一点，避免当 `List` 用

## 31. tailrec - 尾递归

### 定义
`tailrec` 让编译器把**尾调用递归**改写成循环，深递归不再消耗栈。函数须真正尾调用（最后一步是调用自身），否则编译器警告并按普通递归处理。

### 语法和示例
```kotlin
tailrec fun gcd(a: Long, b: Long): Long = if (b == 0L) a else gcd(b, a % b)   // 实测
tailrec fun countDown(n: Int): Int = if (n == 0) n else countDown(n - 1)
```

### 陷阱
递归调用外再包 `try/catch`/后续计算就不满足尾调用，`tailrec` 只会得到编译警告——检查"最后一步"是否真的是调用自身。

## 32. expect / actual - 多平台声明

### 定义
Kotlin Multiplatform 的成对关键字：`expect` 在公共源集声明"各平台需提供的 API"（只有声明无函数体），各平台源集用 `actual` 给出实现。

### 语法和示例
```kotlin
// commonMain
expect fun platformName(): String

// androidMain
actual fun platformName(): String = "Android"

// iosMain
actual fun platformName(): String = "iOS"
```

### 陷阱
`expect` 无对应 `actual` 直接编译错误——纯 JVM/Android 单平台项目用不上它，写普通声明即可。

## 33. annotation - 注解类

### 定义
`annotation class`（修饰符关键字）声明注解类型；用 `@Target` 限制可标注位置，`@Retention` 决定保留层级。

### 语法和示例
```kotlin
@Target(AnnotationTarget.CLASS, AnnotationTarget.FUNCTION)
@Retention(AnnotationRetention.RUNTIME)
annotation class Route(val path: String)

@Route("/detail")
class DetailScreen
```

### 陷阱
注解参数只能是编译期常量（`val`，无 `var`）；Kotlin 注解默认保留到**运行时**（Java 默认只到字节码）——不想进运行时显式 `@Retention(AnnotationRetention.BINARY)`。

## 34. constructor - 次构造函数

### 定义
软关键字，声明次构造函数。类有主构造函数时，每个次构造必须直接或间接（委托链）委托给主构造：`: this(...)`。

### 语法和示例
```kotlin
class User(val name: String) {
    var age = 0
    constructor(name: String, age: Int) : this(name) { this.age = age }
}

val u = User("Ada", 30)
```

### 陷阱
初始化逻辑优先用主构造默认值 + `init` 块；次构造委托链过长难追踪，通常两个构造就到头。

## 35. field / get / set - 幕后字段与访问器

### 定义
自定义访问器中用 `field`（软关键字）引用幕后字段——没有它，setter 里对属性名赋值会递归调用 setter 自身。`get()` / `set(value)` 分别定制读取与写入。

### 语法和示例
```kotlin
class Thermostat {
    var temperature = 50                   // 初始化直写幕后字段——不走 setter（实测：读到 50 而非 40）
        set(value) { field = value.coerceAtMost(40) }
}
// 之后 thermostat.temperature = 99 → 读到 40（实测）

var score = 0
    get() = field.coerceIn(0, 100)         // getter 里用 field 即有幕后字段
```

### 陷阱
- **属性初始化器直写幕后字段、绕过自定义 setter**（实测：上例初始值 50 而非 40）——初始约束放 `init` 块或工厂函数
- 访问器里不引用 `field` 则该属性没有幕后字段（纯计算属性）；此时写 `field` 编译错误

---

## 相关文档

- 📄 **[可空性与集合 API](./02-null-safety-collections.md)** - 空安全操作符与集合操作字典
- 📄 **[协程与 Flow API 全表](./03-coroutines-flow-api.md)** - suspend 生态的完整 API
- 📄 **[泛型与委托属性](./05-generics-delegates.md)** - reified 与 by 的展开
- 📄 **[Kotlin 语法基础](../../basics/03-kotlin-syntax-essentials.md)** - 入门视角的语法教程


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
