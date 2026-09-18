# Swift 常用关键字与相关语法分组清单

> **文档简介**: Swift 常用关键字的分组索引：按声明/类型转换/语句控制流/访问控制/所有权与并发五组收录，每条一行定义 + 最小示例；与 [01-swift-keywords.md](./01-swift-keywords.md) 语义精讲互补不重复
>
> **目标读者**: 查"这个关键字是什么/长什么样"的全体学习者（字典条目，可任意跳入）
>
> **前置知识**: 无；重点关键字的深入讲解见各互链条目

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#关键字` `#索引` `#Swift6` `#语言概念` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

本篇是常用语法**导航清单**：已收进 01 篇的关键字只做索引互链，不重写；本篇补齐 01 未收的全部常用关键字。

---

## 0. 分组总览

| 分组 | 关键字 | 详解位置 |
|------|--------|----------|
| 声明 | `struct` `class` `enum` `init` `deinit` | 本篇 §1 / 构造过程见 [12-initialization.md](./12-initialization.md) |
| 声明 | `func` `let` `var` `extension` | [01 §1](./01-swift-keywords.md) 已收 |
| 声明 | `protocol` `associatedtype` `where` | 本篇 §1 / 泛型原理见 [05-protocols-generics.md](./05-protocols-generics.md) |
| 声明 | `subscript` `typealias` `operator` `import` `macro` | 本篇 §1 |
| 类型与转换 | `is` `as` `as?` `as!` `self` `Self` | 本篇 §2 |
| 语句与控制流 | `if` `guard` `switch` `for-in` `while` `repeat` | [01 §4](./01-swift-keywords.md) 已收 |
| 语句与控制流 | `defer` `throw` `throws` `try` | defer/throw 见 [01 §4](./01-swift-keywords.md)；错误处理见 [08-error-handling.md](./08-error-handling.md) |
| 访问控制 | `open` `public` `internal` `fileprivate` `private` `final` | [01 §4](./01-swift-keywords.md) 已收（本篇 §4 仅补最易错示例） |
| 类型成员 | `static` `class` `lazy` | [01 §4](./01-swift-keywords.md) 已收 |
| 所有权与并发 | `actor` `async` `await` `sending` `Sendable` `nonisolated` `@MainActor` | [01 §3](./01-swift-keywords.md) 已收；API 全表见 [03-concurrency-api.md](./03-concurrency-api.md) |
| 所有权与并发 | `weak` `unowned` | 本篇 §5 / ARC 详解见 [10-value-types-arc.md](./10-value-types-arc.md) |
| 所有权与并发 | `inout` `borrowing` `consuming` `each` `repeat` | 本篇 §5 |
| 泛型修饰 | `some` `any` | [01 §2](./01-swift-keywords.md) 已收 |

---

## 1. 声明类

### 1.1 struct / class / enum

**定义**: 三种命名类型声明——值类型结构体、引用类型类、代数和类型枚举。

```swift
struct Point { var x: Double; var y: Double }   // 值语义，拷贝赋值
class Session { var id = UUID() }               // 引用语义，共享实例
enum LoadState { case idle, loading, failed(Error) }   // 互斥状态 + 关联值
```

**选择**: 默认 struct；需要身份/继承/deinit 才 class；互斥状态集一律 enum。差异全表见 [12-initialization.md §4](./12-initialization.md)。

### 1.2 protocol

**定义**: 声明方法/属性/构造器契约，类型遵循后承诺实现。

```swift
protocol Resizable {
    var size: CGSize { get set }        // { get } 只读要求，{ get set } 可读写
    func resize(to: CGSize)
}
```

面向协议的完整原理见 [05-protocols-generics.md](./05-protocols-generics.md)。

### 1.3 subscript

**定义**: 为类型声明下标访问语法（可重载，可声明只读或读写）。

```swift
extension Array {
    subscript(safe index: Int) -> Element? {   // 防越界下标
        indices.contains(index) ? self[index] : nil
    }
}
let first = [1, 2, 3][safe: 0]      // Optional(1)
```

协议中声明下标要求的实例见 [05-protocols-generics.md](./05-protocols-generics.md)。

### 1.4 typealias

**定义**: 给既有类型起新名字，常用于缩短长泛型签名或语义化回调。

```swift
typealias Handler = (Int) -> Void
typealias Notes = [Note]                       // 集合别名
```

### 1.5 operator（配 prefix / infix / postfix）

**定义**: `operator` 声明自定义运算符及其结合位置；`static func` 给出实现。

```swift
infix operator <>: AdditionPrecedence          // 声明中缀运算符 + 优先级组
extension Int {
    static func <> (lhs: Int, rhs: Int) -> Int { (lhs + rhs) / 2 }
}
5 <> 9      // 7
```

`prefix`/`postfix` 声明前缀/后缀运算符（如 `prefix operator ++`）；运算符可以由全局函数实现；写在类型内时使用 static 成员函数。

### 1.6 import

**定义**: 引入模块的 API；可加种类限定只导入特定类别。

```swift
import SwiftUI
import class Foundation.NSString               // 只导入该类的 API（种类限定）
```

### 1.7 macro

**定义**: 编译期代码展开单元（Swift 5.9+）：`@freestanding` 独立宏（`#` 调用）、`@attached` 附加宏（`@` 调用）。

```swift
// 定义侧：@attached(member) macro Observable()
// 调用侧（本模块高频出现）：
@Observable final class Model { var text = "" }   // 宏自动展开出观察机制
#Preview { ContentView() }                        // 独立宏
```

区分 `@Observable`/`@Model` 是宏、`@State`/`@Query` 是属性包装器，见 [09-property-wrappers.md](./09-property-wrappers.md)。

### 1.8 init / deinit

**定义**: 构造器与析构器。init 家族、委派链、可失败与合成规则的全量讲解见 **[12-initialization.md](./12-initialization.md)**，此处不重复。

---

## 2. 类型检查与转换（is / as 组合）

| 写法 | 含义 | 失败行为 |
|------|------|----------|
| `x is T` | 类型检查，返回 Bool | — |
| `x as? T` | 条件转换，返回 `T?` | 得 nil |
| `x as! T` | 强制转换 | 崩溃 |
| `x as T` | 向上转型/协议擦除/字面量类型标注（总能成功） | — |

```swift
protocol Shape {}
struct Circle: Shape { var radius = 1.0 }
struct Square: Shape { var side = 1.0 }

let shapes: [any Shape] = [Circle(), Square()]
shapes[0] is Circle                     // true
if let c = shapes[0] as? Circle { _ = c.radius }   // 安全向下转型
let up: any Shape = Circle() as any Shape          // 向上转型
```

### self 与 Self

**定义**: `self` 指当前实例；`Self` 指动态类型（类中为实际运行时类型，协议/扩展中指"遵循该协议的类型"）。

```swift
protocol Duplicable {
    func duplicated() -> Self           // 返回"与自己同类型"的实例
}
```

---

## 3. 语句与控制流（本篇不重复，索引）

`if`/`guard`/`switch`/`for-in`/`while`/`repeat`/`defer`/`throw`/`throws`/`try` 均已在 [01 §4](./01-swift-keywords.md) 收录一句话定义；错误处理全量见 [08-error-handling.md](./08-error-handling.md)。补充一个 01 未提的细节：

```swift
defer { cleanup() }        // 按声明逆序执行；即使 throw/guard 退出也运行
```

---

## 4. 访问控制（01 已收速查，此处补最易错两组示例）

01 §4 已给出六个访问级别与 `final` 的一句话定义，这里只补最易错对比：

```swift
public struct Engine {        // struct 本就不能被继承；对外构造入口仍需声明
    public init() {}
    public func run() {}
}

open class Vehicle {          // open：跨模块可子类化、可重写（框架 API 才用）
    open func start() {}
    func tick() {}            // 默认 internal：模块内可见
}

final class Settings { }      // final：禁止继承，编译器可去虚化优化

class Timer {
    static let shared = Timer()          // static：类型成员，禁止子类重写
    class var name: String { "Timer" }   // class：允许子类重写的类型成员
    lazy var cache = loadCache()         // lazy：首次访问才求值，仅 var
    private func loadCache() -> [String: Int] { [:] }
}
```

---

## 5. 所有权与并发

### 5.1 weak / unowned

**定义**: 打破引用循环的弱引用修饰——`weak` 必须是可选 `var`，对象释放后自动置 nil；`unowned` 可以是非可选或可选引用，但不会像 weak 一样在对象释放后自动清零，必须由程序保证有效生命周期。

```swift
class Parent { var child: Child? }
class Child {
    weak var parent: Parent?          // weak：生命周期可能短于引用方
    // unowned let owner: Owner       // unowned：确定"至少同生共死"时用
}
```

ARC 细节与检测手段见 [10-value-types-arc.md](./10-value-types-arc.md)。

### 5.2 inout

**定义**: 参数以可写回语义传递（copy-in copy-out），调用侧加 `&`。

```swift
func bump(_ n: inout Int) { n += 1 }
var score = 9
bump(&score)     // 10
```

**约束**: inout 受独占访问规则约束，不能被逃逸闭包捕获。异步函数可以有 inout 参数，但不能因此绕过 actor 隔离或制造重叠访问；不要把 actor 隔离的可变属性直接借给跨挂起调用。

### 5.3 borrowing / consuming（所有权修饰，Swift 5.9+，SE-0377）

**定义**: 显式声明参数所有权——`borrowing` 借用参数，`consuming` 使被调函数取得参数值的所有权。可拷贝值可能通过隐式拷贝满足 consuming 调用，因此调用方随后仍能使用；非拷贝值不能靠这种拷贝保留第二份所有权。

```swift
func inspect(_ s: borrowing String) { print(s.count) }   // 只读借用；实际性能需要测量
func take(_ s: consuming String) { print(s.count) }      // 函数体内接管
let name = "swift"
inspect(name)      // 之后 name 仍可用
take(name)        // 可拷贝类型：之后 name 同样仍可用（SE-0377）
```

普通参数默认按"拷贝或写时复制共享"传递；这两个修饰符用于热路径上避免多余拷贝。更深入的 `~Copyable` 非拷贝类型体系（SE-0427）超出本篇范围。

### 5.4 each / repeat（参数包，Swift 5.9 起；包迭代 Swift 6.0 起，SE-0393/0404/0408）

**定义**: 泛型参数包语法——`each` 引用包，`repeat` 展开包。

```swift
func describe<each T>(_ values: repeat each T) -> String {
    var parts: [String] = []
    for v in repeat each values {          // 包迭代（SE-0408，Swift 6.0）
        parts.append("\(v)")
    }
    return parts.joined(separator: "-")
}
describe(1, "two", 3.0)     // "1-two-3.0"
```

---

## ⚠️ 常见陷阱

- ❌ **`as!` 拿来当类型断言用**：类型不匹配直接崩溃
  ✅ 运行时来源不确定的数据一律 `as?` + `guard let`。
- ❌ **`unowned` 当 `weak` 用**：对象提前释放后访问即崩溃，且无法判空
  ✅ 引用方与被引用方生命周期无严格保证时选 `weak`。
- ❌ **inout 实参制造重叠访问或捕获到逃逸闭包**：违反访问规则
  ✅ 优先保持短的独占访问；并发场景使用值快照或隔离 API，改成类引用不会自动安全。
- ❌ **给 struct 写 `convenience init`**：convenience 是类专属，值类型写直接报错
  ✅ 值类型用普通 `init` + `self.init(...)` 委派（见 [12-initialization.md](./12-initialization.md)）。
- ❌ **`Self` 与 `self` 混写**：`Self` 是类型标注、`self` 是实例；协议扩展里签名写 `-> Self` 才满足多态
  ✅ 记口诀：小写拿实例，大写当类型。

<!-- full-library-explanation -->
## 从索引进入语义：控制流与成员修饰

这是一份常用词法入口，不替代特定编译器版本的完整语法规范。`Sendable` 是协议，`@MainActor` 是全局 actor 属性，不能因为常一起出现就都称为关键字。

| 写法 | 解决的问题 | 最小读法 |
|---|---|---|
| `break` / `continue` | 提前结束循环 / 跳过本次迭代 | 在搜索命中时 break；忽略空项时 continue |
| `case` / `default` / `fallthrough` | 分支匹配 / 兜底 / 显式继续下一分支 | Swift switch 默认不会穿透；fallthrough 不重新检查下一 case 条件 |
| `do` / `catch` / `rethrows` | 捕获错误 / 根据传入闭包是否抛错决定调用要求 | rethrows 不是“任意地方都可以 throw” |
| `mutating` / `nonmutating` | 值类型成员能否修改 self | 修改 struct 的存储属性通常要求 mutating 方法 |
| `get` / `set` / `willSet` / `didSet` | 计算访问 / 存储变化观察 | set 中可用 newValue，didSet 中可用 oldValue |
| `override` / `required` / `convenience` | 重写 / 子类构造契约 / 类内便利委派 | 见构造过程章节，不能套用于所有值类型 |
| `package` | 同一 Swift package 内跨模块访问 | 不等同于对所有依赖者 public |

```swift
var total = 0
for value in [2, -1, 4, 0, 9] {
    if value < 0 { continue }
    if value == 0 { break }
    total += value
}
print(total) // 6：负数跳过，0 结束循环，9 不处理
```

自测：把 break 改成 continue，预期变为 15；把 `var total` 改成 `let`，应因修改常量而失败。学习关键字应能预测执行路径，而不只记中文名。版本新增词法以 [官方词法参考](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/lexicalstructure/)为准；本文示例未在本轮 Swift 编译器执行。

## 🔗 相关条目

- 📄 **[01-swift-keywords.md](./01-swift-keywords.md)** - 重点关键字（some/any/actor/sending 等）语义精讲
- 📄 **[12-initialization.md](./12-initialization.md)** - init/deinit/构造过程全量讲解
- 📄 **[05-protocols-generics.md](./05-protocols-generics.md)** - protocol/associatedtype/where 泛型原理
- 📄 **[10-value-types-arc.md](./10-value-types-arc.md)** - weak/unowned 与 ARC
- 🌐 **[官方文档：Declarations](https://docs.swift.org/swift-book/documentation/thereference/declarations/)** - Swift 语言参考声明章节

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
