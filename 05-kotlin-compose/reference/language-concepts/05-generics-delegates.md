# 泛型与委托属性速查

> **阅读准备**：Kotlin 类、接口和函数类型；泛型约束与属性委托分别阅读，不需要一次掌握全部高级语法。

> Kotlin 泛型（型变、约束、reified）与委托属性（by lazy / by viewModels / 自定义委托）的字典式速查：定义 → 语法 → 示例 → 陷阱

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#泛型` `#型变` `#委托属性` `#lazy` `#viewModels` |
| **更新日期** | `2026年9月` |

---

## 一、泛型

### 1. 泛型函数与泛型类

**定义**: 用类型参数 `T` 编写与具体类型无关的代码，编译期保证类型安全。

```kotlin
fun <T> List<T>.secondOrNull(): T? = getOrNull(1)

class ResultBox<T>(val value: T) {
    fun getOrDefault(default: T): T = value
}

val s: String? = listOf("a", "b").secondOrNull()
```

### 2. 上界约束

**定义**: `<T : Upper>` 限定 T 必须是 Upper 或其子类，从而可调用 Upper 的成员。

```kotlin
fun <T : Comparable<T>> List<T>.max2(): T? = maxOrNull()

fun <T> List<T>.joinPretty(separator: String): String
    where T : CharSequence, T : Comparable<T> =      // where 多约束
    joinToString(separator)
```

### 3. 型变：out 与 in

**定义**: 控制泛型参数的父子关系传递（Java 通配符 `? extends` / `? super` 的声明处版本）。

- `out T`（协变）：只**产出** T，`Producer<Apple>` 可当 `Producer<Fruit>` 用
- `in T`（逆变）：只**消费** T，`Consumer<Fruit>` 可当 `Consumer<Apple>` 用

```kotlin
interface Producer<out T> { fun produce(): T }
interface Consumer<in T>  { fun consume(item: T) }

val appleProducer: Producer<Apple> = object : Producer<Apple> {
    override fun produce() = Apple()
}
val fruitProducer: Producer<Fruit> = appleProducer     // ✅ out 协变

// 助记：PECS —— Producer-extends(out) / Consumer-super(in)
```

**陷阱**: 声明 `out` 的类中不能把 T 用作函数参数（写位置），否则编译报错——这正是在编译期防止"往猫列表里塞狗"。

### 4. 星投影 `*`

**定义**: 不关心/不知道类型参数时用 `*`，读取出来是 `out` 上界（默认 `Any?`）。

```kotlin
fun printBox(box: ResultBox<*>) {
    val v: Any? = box.value          // 只能按 Any? 读
}
```

### 5. reified + inline：运行时拿到 T

**定义**: inline 函数把字节码复制到调用点，`reified` 因此可在运行时拿到真实类型（突破擦除）。

```kotlin
inline fun <reified T : Any> String.fromJson(gson: Gson): T =
    gson.fromJson(this, T::class.java)

inline fun <reified T : ViewModel> ViewModelStoreOwner.vm(): T =
    ViewModelProvider(this)[T::class.java]        // by viewModels 的原理即如此

val user: User = json.fromJson(gson)
```

**陷阱**: 只能用于 inline 函数；普通函数中的 `T` 运行时不存在（JVM 擦除），不能 `T::class`、`is T`、`T()`。

---

## 二、委托属性（Delegated Properties）

### 1. by 的语法

**定义**: `val/var <属性>: <类型> by <委托表达式>` —— 属性的 getter/setter 转发给委托对象的 `getValue`/`setValue`。

```kotlin
class Example {
    var name: String by NameDelegate()      // 读写都走委托对象
}

interface ReadOnlyProperty<in R, out T> { fun getValue(thisRef: R, property: KProperty<*>): T }
interface ReadWriteProperty<in R, T> {
    fun getValue(thisRef: R, property: KProperty<*>): T
    fun setValue(thisRef: R, property: KProperty<*>, value: T)
}
```

### 2. by lazy - 惰性初始化

**定义**: 首次访问时执行 lambda 并缓存结果；默认线程安全（`SYNCHRONIZED`）。

```kotlin
val taxRate by lazy { loadTaxRateFromDisk() }     // 贵重计算，用到才算

// 三种模式
val a by lazy(LazyThreadSafetyMode.SYNCHRONIZED) { compute() }  // 默认：锁保证单次
val b by lazy(LazyThreadSafetyMode.PUBLICATION)  { compute() }  // 允许多次算，取首个
val c by lazy(LazyThreadSafetyMode.NONE)         { compute() }  // 不提供并发安全保证，不是零开销
```

**陷阱**: lambda 捕获的依赖在初始化后才变化不会触发重算——需要"随依赖刷新"的用 `remember(key)` 或 Flow，而非 lazy。

### 3. Delegates.observable / vetoable

**定义**: 可观察属性——值变化时收到回调；`vetoable` 还可否决赋值。

```kotlin
import kotlin.properties.Delegates

var score: Int by Delegates.observable(0) { _, old, new ->
    println("分数 $old → $new")                  // 类似 JS setter 拦截
}

var volume: Int by Delegates.vetoable(50) { _, _, new -> new in 0..100 }  // 非法值被拒
```

### 4. Android 常用委托全家桶

| 委托 | 来源 | 作用 |
|------|------|------|
| `by viewModels()` | activity/fragment-ktx | 获取/创建懒加载 ViewModel |
| `by activityViewModels()` | fragment-ktx | Fragment 共享宿主 Activity 的 ViewModel |
| `by navGraphViewModels(id)` | navigation | 导航图级别共享 |
| `by lazy { ... }` | stdlib | 惰性单例（Repository、适配器） |
| `by preferencesDataStore(name)` | datastore | 顶层声明 DataStore 实例 |

```kotlin
class DetailFragment : Fragment() {
    private val vm: DetailViewModel by viewModels { DetailViewModel.factory(repo) }

    // Activity 级共享：列表页与详情页共用同一个选中态 ViewModel
    private val selectionVm: SelectionViewModel by activityViewModels()
}

// DataStore 顶层声明（保证全应用单实例）
val Context.settingsStore by preferencesDataStore(name = "settings")
```

**陷阱**:
- `by viewModels()` 的 ViewModel 在配置变更时存活、在宿主**真正销毁**时清空——不要把 Activity Context 存进去
- `preferencesDataStore` 属性重复声明同名 store 会抛 `IllegalStateException`，全局只声明一次

### 5. 自定义委托

**定义**: 实现 `ReadOnlyProperty`/`ReadWriteProperty` 即可发明自己的属性行为。

```kotlin
import kotlin.properties.ReadWriteProperty
import kotlin.reflect.KProperty

class NotEmptyString(initial: String) : ReadWriteProperty<Any?, String> {
    private var value = initial.trim().also { require(it.isNotEmpty()) }
    override fun getValue(thisRef: Any?, property: KProperty<*>): String = value
    override fun setValue(thisRef: Any?, property: KProperty<*>, v: String) {
        require(v.isNotBlank()) { "${property.name} 不能为空" }
        value = v.trim()
    }
}

class Form {
    var title by NotEmptyString("未命名")          // 赋空串直接抛异常
}
```

---

## 快速选型

| 需求 | 用什么 |
|------|--------|
| 一次性贵重初始化 | `by lazy` |
| 页面状态跨旋转存活 | `by viewModels()` + StateFlow |
| Fragment 间共享状态 | `by activityViewModels()` |
| 泛型 JSON 反序列化 | `inline + reified` |
| 容器通用算法 | 泛型 + 上界约束 |
| 只读数据源暴露 | `out T` 协变接口 |

---

## 相关文档

- 📄 **[Kotlin 关键字详解](./01-kotlin-keywords.md)** - reified/inline/by 的关键字层说明
- 📄 **[Compose 状态 API 详解](./04-compose-state-api.md)** - `var x by remember` 背后的委托机制
- 📄 **[AndroidX 官方库指南](../library-guides/01-androidx-libraries.md)** - viewModels/DataStore 的库级用法
- 📖 **[Kotlin 泛型官方文档](https://kotlinlang.org/docs/generics.html)** - 型变完整规则


<!-- full-library-explanation -->
## 泛型信息和属性行为的两条边界

`reified T` 能帮助检查外层运行时类型，但 `List<String>` 的元素类型不会因此自动获得完整运行时校验。上面的 `T::class.java` JSON 写法只适用于目标库能正确处理的类型；嵌套泛型需其 TypeToken 或序列化器机制，并验证外部数据。

`lazy` 决定初始化时间，不决定线程。首次在主线程读取时，初始化块也可能在主线程执行，因此磁盘读取仍会卡住界面。`PUBLICATION` 允许并发初始化多次，不适合不可重复的扣款、注册监听器等副作用。

练习：在 lazy 初始化块打印标记，读取两次，应只得到一次成功初始化结果；再让初始化首次抛异常，下一次访问可重新尝试。验收：能区分“成功值缓存”和“异常永久缓存”。自定义非空字符串委托还应校验初值，否则 setter 严格而初始状态已违反约束。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
