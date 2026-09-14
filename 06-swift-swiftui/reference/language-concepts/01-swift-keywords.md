# Swift 关键字详解

> **文档简介**: 按类别逐条讲解 Swift 关键字：重点覆盖 Swift 6 时代的 some/any/actor/sending 等并发与所有权关键字，附语法与陷阱
>
> **目标读者**: 需要快速查阅某个关键字语义的所有水平学习者（字典条目，可任意跳入）
>
> **前置知识**: 无硬性要求；配合 [basics/03-swift-syntax-essentials.md](../../basics/03-swift-syntax-essentials.md) 学习效果最佳

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#关键字` `#Swift6` `#并发` `#语言概念` |
| **更新日期** | `2026年9月` |

> 🧭 **指路**: 本篇为重点关键字语义精讲；关键字的完整分组总清单（声明/类型转换/控制流/访问控制/所有权/参数包）见 [13-keywords-completion.md](./13-keywords-completion.md)。

---

## 1. 声明类

### 1.1 let / var

**定义**: `let` 声明常量，`var` 声明变量（`let maxCount = 10`）。

**陷阱**: `let` 结构体内部属性也不可改；但 class 用 `let` 声明时**属性仍可改**（引用本身不变）。

### 1.2 func

**定义**: 声明函数/方法。参数标签 `_` 省略外部名。

```swift
func move(from start: Int, to end: Int) {}
func validate(_ input: String) -> Bool { !input.isEmpty }
```

### 1.3 extension

**定义**: 为既有类型（含外部类型与协议）追加方法、计算属性、协议遵循。

```swift
extension String {
    var trimmed: String { trimmingCharacters(in: .whitespaces) }
}
```

---

## 2. 类型与泛型类（SwiftUI 高频）

### 2.1 some（不透明类型）

**定义**: "某个**固定的**遵循该协议的类型"，编译期确定但对调用方隐藏。

```swift
var body: some View {      // 整个 body 返回同一个具体类型
    Text("hello")
}
```

**关键**: `some` 保留类型身份 → SwiftUI 能做 diff；同函数两个分支必须返回同一具体类型。

### 2.2 any（存在类型）

**定义**: "任意遵循该协议的类型"，运行时动态派发，存在装箱开销。

```swift
let shapes: [any Shape] = [Circle(), Rectangle()]   // 异构集合必须 any
```

**选择原则**: 默认 `some`；需要**异构集合/存属性**才用 `any`。SwiftUI 中返回 `any View` 会失去 diff 优化。

### 2.3 associatedtype

**定义**: 协议中的占位类型，由遵循者指定。

```swift
protocol Repository {
    associatedtype Item
    func all() -> [Item]
}
```

### 2.4 where

**定义**: 为泛型/关联类型加约束。

```swift
extension Array where Element == TaskItem {
    var allDone: [TaskItem] { filter(\.isDone) }
}
```

---

## 3. 并发类（Swift 6 重点）

### 3.1 async / await

**定义**: 标记可挂起函数与挂起点。

```swift
func load() async throws -> [Item] {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try decode(data)
}
```

### 3.2 actor

**定义**: 引用类型，内部状态串行访问，自动防数据竞争。

```swift
actor Counter {
    private var value = 0
    func increment() { value += 1 }
}
```

### 3.3 @MainActor

**定义**: 全局主 actor 标注，被标代码在主线程执行。UI 层默认隔离域。

```swift
@MainActor @Observable
final class Model { var text = "" }
```

### 3.4 nonisolated

**定义**: 在 actor/被隔离类型内声明"此成员不需要隔离"。

```swift
actor Config {
    nonisolated let appName = "SwiftNotes"   // 不可变常量可免隔离
}
```

### 3.5 sending

**定义**: 参数级标注"该值传给被调方后调用方不再使用"，是区域隔离（region isolation）的核心关键字，用于让编译器证明值安全跨越隔离域。例：`func process(_ data: sending [Byte]) async -> Summary`。

**注意**: 与 `Sendable` 不同——`Sendable` 是类型级"本身线程安全"声明，`sending` 是调用点的所有权证明，约束更宽松。

### 3.6 Sendable / @unchecked

**定义**: 标记类型可安全跨隔离域传递。值类型、不可变类型自动满足；不满足时用 `@unchecked Sendable` 自行担保（需注释说明同步策略）。

---

## 4. 控制流与访问控制

| 关键字 | 一句话 | 备注 |
|--------|--------|------|
| `if / guard / switch` | 条件与分支 | `guard` 必须退出作用域 |
| `for ... in` | 遍历 | 无传统 C 式三段 for |
| `while / repeat` | 循环 | `repeat {} while` |
| `defer` | 作用域退出前执行 | 资源清理 |
| `throw / throws / try` | 错误传播 | `try?` 变 nil，`try!` 崩溃 |
| `public / internal / fileprivate / private` | 访问级别 | 默认 internal |
| `open` | 允许跨模块继承 | 仅 class/成员 |
| `static / class` | 类型成员 | `class` 允许子类重写 |
| `final` | 禁止继承/重写 | 性能与意图 |
| `lazy` | 首次访问才初始化 | 仅 var |

## ⚠️ 高频陷阱速查

- **`some` 与 `any` 混用**: 返回类型里 `some` 只能有一个；需要多态分支时要么统一具体类型，要么接受 `any` 的代价
- **`sending` 误当 `Sendable`**: 前者约束调用点所有权，后者约束类型本身，不能互相替代
- **`weak` 与引用循环**: class 闭包强捕获 self 造成循环引用时用 `[weak self]`；struct 无此问题

## 相关文档

- 📄 [02-optionals-collections.md](./02-optionals-collections.md) — 可选值与集合 API
- 📄 [03-concurrency-api.md](./03-concurrency-api.md) — 并发 API 全表（Task/Actor/AsyncSequence）
- 📄 [05-protocols-generics.md](./05-protocols-generics.md) — some/any 与泛型的完整原理
