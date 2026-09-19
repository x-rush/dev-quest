# Swift 语法 Essentials - 写 SwiftUI 前必须会的 Swift

## 先理解，再动手

可选值把“没有值”写进类型；guard let 先处理缺失，让后面使用确定存在的值。强制解包只是延后风险。

**本节自测**：把输入转为 Int?，分别测试 12、abc 与空串。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

只有有效数字进入计算；无效输入走明确失败分支，而不是触发崩溃。

</details>

> **文档简介**: 精选写 SwiftUI 代码时高频使用的 Swift 语法：可选值、struct/class、闭包、enum 与扩展，帮你"够用地"读懂并写出现代 Swift
>
> **目标读者**: 有任意语言（Go/JS/Kotlin 等）基础、首次系统接触 Swift 的学习者
>
> **前置知识**: 会变量、函数与条件判断。本页纯 Swift 程序可以先在命令行完成，再进入[第一个 SwiftUI 应用](./02-first-swiftui-app.md)；SwiftUI 片段需要 Xcode 工程。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#Swift语法` `#可选值` `#结构体` `#闭包` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 安全地处理可空值：`if let` / `guard let` / 可选链
- ✅ 选择正确的类型载体：struct、class、actor、enum
- ✅ 读懂 SwiftUI 中无处不在的闭包语法
- ✅ 用 extension 与协议扩展组织代码

## 🔍 一、可选值（Optional）

Swift 通常用 `Optional` 把“可能没有值”写进类型。类型系统要求先处理缺失，但 `!`、隐式解包可选值以及不正确的外部 API 契约仍可能导致运行时崩溃。

```swift
var nickname: String? = nil       // String? 表示"可能没有 String"
nickname = "小路"                  // 赋值后是 Optional("小路")，仍是可选类型

// 直接使用会编译报错：
// let count = nickname.count     // ❌ error

// ✅ 方式一：if let 绑定（推荐用于分支处理）
if let nick = nickname {
    print("昵称是 \(nick)")        // nick 在此分支内是普通 String
}

// ✅ 方式二：nil 合并运算符（推荐用于默认值）
let displayName = nickname ?? "游客"

// ✅ 方式三：可选链（任一环节为 nil 整体即 nil）
let firstChar = nickname?.first   // Character? 类型

// ⚠️ 强制解包：仅在你 100% 确定有值时使用，否则运行时崩溃
let forced = nickname!
```

Swift 5.7+ 支持**可选绑定简写**：当新局部变量与原可选值同名时，可以省略右侧表达式：

```swift
if let nickname {                 // 等价于 if let nickname = nickname
    print(nickname)
}

// 在函数体内同理可写 guard let nickname else { return }
```

`guard` 的特点：**早退出 + 绑定提升**。条件不满足就离开当前作用域，满足则绑定值在后续代码全程可用——SwiftUI 项目中最常见的解包方式。

更系统的可选值 API 参考：[02-optionals-collections.md](../reference/language-concepts/02-optionals-collections.md)。

## 🔍 二、struct、class、actor：值与引用

### 三者怎么选

| 类型 | 语义 | 继承 | 并发 | 典型用途 |
|------|------|------|------|----------|
| `struct` | 值类型（拷贝） | ❌ | 不自动并发安全；成员也可能是共享引用 | 独立模型与视图描述 |
| `class` | 引用类型（共享） | ✅ 单继承 | 需手动同步 | 需要继承/被 Objective-C 桥接的场景 |
| `actor` | 引用类型 + 隔离 | ❌ | 保护隔离状态；跨 `await` 仍可能交错 | 可变共享状态（见 [07-concurrency-async-await.md](./07-concurrency-async-await.md)） |

```swift
import Foundation

// id 在 init 中提供默认值，使 Codable 解码仍能恢复持久化的 id。
struct TaskItem: Identifiable, Codable {
    let id: UUID
    var title: String
    var isDone: Bool

    init(id: UUID = UUID(), title: String, isDone: Bool = false) {
        self.id = id
        self.title = title
        self.isDone = isDone
    }
}

// 值语义演示
var a = TaskItem(title: "买咖啡")
var b = a
b.isDone = true
print(a.isDone)   // false —— b 是 a 的拷贝，互不影响
```

SwiftUI 的自定义视图通常声明为 struct；`View` 是协议，不应据此断言所有符合者都是 struct。值类型里包含 class 引用时，复制外层值不会深拷贝内部对象；跨并发域还需检查 `Sendable`、隔离与可变访问。

### class 与引用语义

```swift
final class DownloadCenter {
    var progress: Double = 0
}

let c1 = DownloadCenter()
let c2 = c1          // c1、c2 指向同一个实例
c2.progress = 0.5
print(c1.progress)   // 0.5 —— 引用语义，共享状态
```

`final` 关键字禁止继承，既表达设计意图，也帮助编译器做动态派发优化。

## 🔍 三、闭包（Closure）

闭包是可以捕获周围上下文变量的匿名函数。SwiftUI 的 UI 树几乎全由闭包搭建。

```swift
// 完整形式
let add: (Int, Int) -> Int = { (a: Int, b: Int) -> Int in
    return a + b
}

// 类型推断 + 隐式返回
let add2 = { (a: Int, b: Int) in a + b }

// 尾闭包：最后一个参数是闭包时可移出括号
Button(action: {
    print("点了")
}) {
    Text("点我")
}

// 简写为最常见的 SwiftUI 写法
Button {
    print("点了")     // action 尾闭包
} label: {
    Text("点我")      // label 带标签的尾闭包
}
```

`in` 前是参数、后是函数体；`$0`、`$1` 是匿名参数简写：

```swift
let sorted = [3, 1, 2].sorted { $0 < $1 }
```

⚠️ 并发闭包中的捕获与 `[weak self]` 处理见 [07-concurrency-async-await.md](./07-concurrency-async-await.md)。

## 🔍 四、enum 与 associated value

```swift
enum LoadState {
    case idle
    case loading
    case loaded(items: [String])   // 关联值：每个 case 可携带不同数据
    case failed(message: String)
}

var state = LoadState.idle

// switch 必须穷尽所有 case
switch state {
case .idle:
    print("待机")
case .loading:
    print("加载中…")
case .loaded(let items):
    print("已加载 \(items.count) 条")
case .failed(let message):
    print("失败：\(message)")
}

// if case：只关心一个 case 时
if case .loaded(let items) = state {
    print(items)
}
```

enum + associated value 是 Swift 表达"互斥状态"的利器，比多个 Bool 标志位清晰得多。

## 🔍 五、extension 与协议扩展

```swift
extension TaskItem {
    var displayTitle: String {
        isDone ? "✅ \(title)" : title
    }
}
```

extension 无需源码即可为任意类型（包括 `String`、`View`）添加计算属性与方法，也能给协议加默认实现；SwiftUI 的大量修饰符正是 `View` 协议扩展。

## ✅ 最佳实践

struct 适合独立值，class 适合需要共享身份的对象；选择依据是修改一处后其他持有者是否应看到同一个对象变化。不要用固定“优先级”代替可选值的语义判断：guard 适合前置条件失败即退出，if let 适合局部分支，?? 适合确有合理默认值的情况。

强制解包表达“这里不允许没有值”，若该保证无法证明就显式处理 nil。用 enum 表示加载中、成功与失败，可以排除几个布尔值同时为真的矛盾状态；练习让空输入走失败分支，而非依靠崩溃暴露问题。

## ❓ 常见问题

### Q1: `String?` 打印出来是 `Optional("x")`，怎么去掉？

这是类型本身是可选的表现。用 `if let`/`guard let` 绑定或 `??` 提供默认值后再使用，而不是格式化时硬转。

## 🎯 练习与实践

### 练习一：基础练习

- [ ] 写函数 `parseAge(_ input: String?) -> Int?`：只接受 0...150 的整数；缺失、非法文本和越界均返回 nil，不能把失败伪装成合法年龄 0。
- [ ] 定义 `enum Weather`：晴/雨/多云三种 case，其中"雨"关联降水量 Double，并用 switch 打印描述
- [ ] 将数组 `[8, 3, 5]` 用闭包简写完成降序排序

### 完整程序：身份恢复、值与引用

保存为 `Main.swift`，运行 `swift Main.swift`。它只使用 Foundation，完整正文直接参与[本轮运行验证](../../shared-resources/tools/document-quality/reports/kotlin-swift-core-validation.md)。把 `let id: UUID` 改成声明时初始化的 `let id = UUID()` 再观察编译警告和 round-trip 断言，可以理解为什么“成功解码”还不等于“恢复同一身份”。

<!-- dq-case: swift-syntax-contracts -->
```swift
import Foundation

struct SavedTask: Codable {
    let id: UUID
    var title: String
    init(id: UUID = UUID(), title: String) {
        self.id = id
        self.title = title
    }
}

final class SharedCounter { var value = 0 }
struct Wrapper { let counter: SharedCounter }

func parseAge(_ raw: String?) -> Int? {
    guard let raw,
          let value = Int(raw.trimmingCharacters(in: .whitespacesAndNewlines)),
          (0...150).contains(value) else { return nil }
    return value
}

let original = SavedTask(title: "learn")
let data = try JSONEncoder().encode(original)
let restored = try JSONDecoder().decode(SavedTask.self, from: data)
precondition(restored.id == original.id)
var edited = restored
edited.title = "practice"
precondition(restored.title == "learn")
let first = Wrapper(counter: SharedCounter())
let second = first
second.counter.value = 3
precondition(first.counter.value == 3)
precondition(parseAge("0") == 0)
precondition(parseAge(" 12 ") == 12)
for invalid: String? in [nil, "", "abc", "-1", "151", "1.5"] {
    precondition(parseAge(invalid) == nil)
}
print("Swift syntax contracts passed")
```

需要分别解释两个结果：`edited.title` 独立变化，因为 String 是值；`second.counter.value` 影响 `first`，因为两份 Wrapper 持有同一个 class 实例。官方资料：[结构体与类](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/classesandstructures/)、[并发与 Sendable](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)。

---

## 相关文档

- 📄 [02-optionals-collections.md](../reference/language-concepts/02-optionals-collections.md) — 可选链与集合 API 全量字典
- 📄 [05-protocols-generics.md](../reference/language-concepts/05-protocols-generics.md) — 协议与泛型的完整讲解
- 📄 [01-swift-keywords.md](../reference/language-concepts/01-swift-keywords.md) — 全部关键字逐条详解


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
