# Kotlin 关键字与修饰符详解

> Compose/Android 开发高频的 Kotlin 关键字速查字典：按"声明 → 继承 → 并发 → 其他"分组，每个词条包含定义、语法、示例与陷阱

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#关键字` `#修饰符` `#Kotlin` `#语言概念` |
| **更新日期** | `2026年9月` |

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

> 📖 `by lazy`/`by viewModels` 的完整机制见 [泛型与委托属性](../reference/language-concepts/05-generics-delegates.md)。

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

---

## 相关文档

- 📄 **[可空性与集合 API](./02-null-safety-collections.md)** - 空安全操作符与集合操作字典
- 📄 **[协程与 Flow API 全表](./03-coroutines-flow-api.md)** - suspend 生态的完整 API
- 📄 **[泛型与委托属性](./05-generics-delegates.md)** - reified 与 by 的展开
- 📄 **[Kotlin 语法基础](../../basics/03-kotlin-syntax-essentials.md)** - 入门视角的语法教程
