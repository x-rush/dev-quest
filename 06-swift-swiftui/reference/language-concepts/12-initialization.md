# Swift 构造过程（Initialization）详解

> **文档简介**: 系统讲解 Swift 构造过程：init 家族（指定/便利/必要）、可失败构造器、委派链与两段式构造、合成构造器规则、属性包装器初始化与 deinit——语言核心主题的全量字典条目
>
> **目标读者**: 需要理清"这个 init 该怎么写、编译器为什么报错"的所有水平学习者（字典条目，可任意跳入）
>
> **前置知识**: [basics/03-swift-syntax-essentials.md](../../basics/03-swift-syntax-essentials.md)；类与值类型差异见 [10-value-types-arc.md](./10-value-types-arc.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#init` `#构造器` `#两段式构造` `#deinit` `#语言概念` |
| **更新日期** | `2026年9月` |

## 📌 定义

构造过程（initialization）是把类型的每个存储属性置为有效初值、使实例可用的阶段。Swift 用 `init` 家族完成它，并在**编译期**强制"所有存储属性在使用前必须完成初始化"——没有默认构造过程可用。

---

## 1. init 家族：指定 / 便利 / 必要

三个角色**仅类（含 actor）有完整区分**；值类型只有一种构造器，无需区分。

| 角色 | 写法 | 职责 | 约束 |
|------|------|------|------|
| 指定构造器 designated | `init(...)` | 主初始化路径：初始化本类全部存储属性，向上委派给父类 | 每个类**至少一个** |
| 便利构造器 convenience | `convenience init(...)` | 辅助路径：横向委派给同类其他构造器 | 必须最终到达指定构造器 |
| 必要构造器 required | `required init(...)` | 协议要求或框架契约：所有子类必须实现 | 覆写时不写 `override` |

```swift
class Document {
    var title: String
    init(title: String) {                    // 指定构造器
        self.title = title
    }
    convenience init() {                     // 便利构造器
        self.init(title: "未命名")
    }
}

class Report: Document {
    var pages: Int
    init(title: String, pages: Int) {        // 子类指定构造器
        self.pages = pages                   // ① 先初始化自己的属性
        super.init(title: title)             // ② 再向上委派
    }
    required init() {                        // 实现父类的 required（无 override）
        self.pages = 0
        super.init(title: "未命名")
    }
}
```

**委派链三条规则**（类的构造器关系）：

1. 指定构造器必须调用**直接父类**的指定构造器（向上委派）。
2. 便利构造器必须调用**同类**的另一个构造器（横向委派）。
3. 便利构造器最终必须到达某个指定构造器。

### 两段式构造（Two-Phase Initialization）与安全检查

类构造分两段：**第一段**沿委派链向上，每个类把"自己引入的存储属性"初始化完；到达链顶后**第二段**再回到链上，各层自定义和改写属性。

编译器安全检查（记这三条即可避开绝大多数报错）：

| 检查 | 内容 |
|------|------|
| ① | 指定构造器在**向上委派之前**，必须先初始化本类引入的全部存储属性 |
| ② | 指定构造器必须先向上委派，之后才能给**继承来的**属性赋值（否则会被父类覆盖） |
| ③ | 便利构造器必须先委派，之后才能给**任何属性**赋值（否则会被同类指定构造器覆盖） |
| ④ | 第一段完成前，不能读实例属性、调用实例方法、把 `self` 当值传递 |

### 构造器继承与覆盖

- 子类**默认不继承**父类构造器（安全考虑）；仅在子类未新增指定构造器、且全部新增属性有默认值时，自动继承父类全部指定构造器。
- 覆写父类指定构造器要写 `override`；实现 `required` 构造器**不写** `override`。
- 子类可通过继承或显式实现来满足 `required` 要求。

---

## 2. 可失败构造器 init? / init!

**定义**: 可能构造失败的构造器返回 `nil`；`init?` 返回可选值，`init!` 返回隐式解包可选值。

```swift
struct Celsius {
    let value: Double
    init?(fromFahrenheit f: Double) {
        guard f > -459.67 else { return nil }   // 低于绝对零度 → 失败
        value = (f - 32) / 1.8
    }
}

enum Direction: String {
    case north, south, east, west
    // 原始值枚举自动合成：init?(rawValue: String)
}
Direction(rawValue: "up")        // nil
```

要点：

- 失败只能发生在**全部存储属性初始化完成之后**（属性必须先有值，才能返回 nil）。
- 类的可失败构造器在属性初始化完后，可用 `guard let self = self else { return nil }` 解包 self（此时 self 为可选）。
- 委派规则：可失败构造器可以委派到可失败/非可失败构造器；`init!` 可委派 `init?`（隐式强解包）。子类可用**非可失败**构造器覆盖父类的**可失败**构造器（反向不允许）。
- `init!` 强解包失败即崩溃——只用于与 ObjC 契约互操作（如 `init?(coder:)` 的 `init!(coder:)` 场景），业务代码用 `init?`。

**抛错构造器**: `init(...) throws` 与函数同理，`try` 调用；可与可失败叠加为 `init?() throws`。

---

## 3. 合成构造器规则（编译器什么时候送你一个 init）

### 3.1 结构体：逐成员构造器（memberwise initializer）

结构体自动获得**逐成员构造器**，参数按存储属性声明顺序排列：

```swift
struct TaskItem {
    var title: String
    var done = false              // 有默认值 → 参数带默认值
    let id = UUID()               // let 且已赋值 → 不进参数
}
// 合成：init(title: String, done: Bool = false)
TaskItem(title: "写周报")
```

**合成规则**：

- `var` 有默认值 → 参数带默认值；无默认值 → 必传参数。
- `let` 且声明处已赋值 → 不出现在参数中。
- **访问级别**：任一存储属性为 `private` → 逐成员构造器为 private；任一为 `fileprivate` → 为 fileprivate；否则 internal。

### 3.2 类：默认构造器（default initializer）

类**没有**逐成员构造器。仅当**全部存储属性都有默认值、且未手写任何指定构造器**时，获得无参默认 `init()`。

### 3.3 抑制规则（高频坑）

- 在**类型主体内**手写任一 `init` → 默认构造器与逐成员构造器**全部消失**。
- 把 `init` 写进 **extension** → 不抑制合成构造器（想保留 memberwise 又加便利入口时用）。

### 3.4 枚举

- 枚举没有逐成员构造器；带原始值时自动合成 `init?(rawValue:)`。
- 可自定义构造器；**非委派构造器**内必须先把 `self` 设为某个 case，之后可重新赋值（纯委派构造器只写 `self.init(...)` 即可，无需先设 case）。

---

## 4. 构造器在类 / 结构体 / 枚举中的差异

| 维度 | struct | enum | class / actor |
|------|--------|------|---------------|
| 逐成员构造器 | ✅ 自动合成 | ❌ | ❌ |
| 默认无参 `init()` | 有默认值时同 memberwise | ❌ | 全属性有默认值且未手写 init 时 |
| convenience | ❌（写了会报错） | ❌ | ✅ |
| 继承 / required / 两段式 | ❌ | ❌ | ✅ |
| 可失败 init?/init! | ✅ | ✅ | ✅ |
| deinit | ❌ | ❌ | ✅（类与 actor） |
| 指定构造器数量限制 | 无 | 无 | 至少一个 |

值类型构造是**单段式**：没有委派链与两段式的约束，`init` 内直接给属性赋值即可。

---

## 5. deinit

**定义**: 引用类型实例释放（ARC 引用计数归零）前的清理回调。

```swift
final class FileHandleWrapper {
    let path: String
    init(path: String) { self.path = path }
    deinit {
        // 释放资源：关文件、断开连接、移除观察者
        // 无参数、无括号；此时实例属性仍可读
    }
}
```

- 只有 **class 与 actor** 有 deinit；struct/enum 没有。例外：Swift 6 的非拷贝类型（`~Copyable` 的 struct/enum，SE-0427）也可定义 deinit。
- 不能显式调用；无参数；每实例最多执行一次。
- deinit 中仍可读取实例属性做收尾（此时实例尚未释放）。

---

## 6. 属性包装器与构造器初始化

包装器属性改变逐成员构造器的参数形状（详见 [09-property-wrappers.md](./09-property-wrappers.md)）：

- 包装器类型有 `init(wrappedValue:)` → memberwise 参数收**被包装的值**。
- 另有 `init(projectedValue:)` → memberwise 额外收 `$name` 参数。

```swift
@propertyWrapper
struct Clamped<Value: Comparable> {
    var wrappedValue: Value
    let range: ClosedRange<Value>
    init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.wrappedValue = range.contains(wrappedValue) ? wrappedValue : range.lowerBound
        self.range = range
    }
}

struct Player {
    @Clamped(0...100) var stamina = 100
    // memberwise 合成为：init(stamina: Int = 100)
}
```

SwiftUI 场景中 `@State var count = 0` 的初值经 autoclosure 传入包装器，原理同上。

---

## 7. "mutating init"？—— 概念澄清

Swift **没有** `mutating init` 这个关键字组合。相关语义分属两个机制：

- 结构体/枚举的 `init` 中可以直接给 `self` **整体重赋值**（`self = Self(other)`），这是初始化语义，不是 mutating。
- 已有实例的重置放在 `mutating func` 中完成：`mutating func reset() { self = Self() }`（要求全部属性有默认值）。

---

## 💡 完整示例

```swift
protocol CacheStorable { init() }

final class ImageCache: CacheStorable {
    private var storage: [String: Data] = [:]      // private → 影响合成 init 可见性
    let capacity: Int

    init(capacity: Int) {                          // 指定构造器
        self.capacity = max(1, capacity)
    }

    convenience init() {                           // 便利构造器：横向委派
        self.init(capacity: 50)
    }

    required init() {                              // 满足协议 init 要求
        self.init(capacity: 50)                    // required 实现可委派其他构造器
    }

    deinit { storage.removeAll(keepingCapacity: false) }
}

struct Point {
    var x: Double
    var y: Double
    // 自动获得逐成员构造器：Point(x:y:)
}
let p = Point(x: 1, y: 2)
```

## ⚠️ 常见陷阱

- ❌ **便利构造器里先赋值再委派**：`convenience init() { title = "a"; self.init() }` —— 违反安全检查③，编译错误
  ✅ **先 `self.init(...)` 完成委派，再做第二段定制**。
- ❌ **手写 init 后抱怨 memberwise 消失**：类型主体内新增任何 init 都会抑制合成构造器
  ✅ 需要保留时把新 init 写进 `extension`，或显式重写逐成员签名。
- ❌ **给 private 存储属性的 struct 对外暴露 memberwise**：合成构造器可见性跟随最严属性（private），外部调用报"init 不可访问"
  ✅ 显式写公开构造器，或属性改 internal。
- ❌ **子类漏掉 required init**：父类标了 `required`，子类新增指定构造器后未实现
  ✅ 子类补 `required init(...)`（不加 override）。
- ❌ **用 init! 承接业务失败**：强解包可选值，nil 即崩溃
  ✅ 业务失败路径一律 `init?`，调用侧配合 `guard let`。
- ❌ **在 deinit 里发起 async 清理**：deinit 是同步上下文，且 Swift 严格并发下不允许在 deinit 中引用被隔离状态
  ✅ 清理放 `close()`/`teardown()` 显式调用，或用非隔离的同步清理。

## 🔗 相关条目

- 📄 **[01-swift-keywords.md](./01-swift-keywords.md)** - init/struct/class 等关键字语义速查
- 📄 **[09-property-wrappers.md](./09-property-wrappers.md)** - 属性包装器与 init(wrappedValue:) 的完整约定
- 📄 **[10-value-types-arc.md](./10-value-types-arc.md)** - ARC 与 deinit 时机、weak/unowned
- 🌐 **[官方文档：Initialization](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/initialization/)** - The Swift Programming Language 权威章节

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
