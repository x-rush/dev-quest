# 协议与泛型速查

> **文档简介**: 协议（含关联类型与协议扩展）、泛型约束、some/any 的完整条目式参考，解释 SwiftUI 类型签名背后的原理
>
> **目标读者**: 想读懂 `some View`/`any Shape` 背后机制的中级学习者
>
> **前置知识**: 建议先学 [basics/03-swift-syntax-essentials.md](../../basics/03-swift-syntax-essentials.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#协议` `#泛型` `#associatedtype` `#some` `#any` |
| **更新日期** | `2026年9月` |

---

## 1. 协议基础

**定义**: 方法、属性与关联类型的契约，类型通过遵循获得能力。

```swift
protocol Drawable {
    var color: Color { get }              // { get }：至少可读
    func draw(in context: GraphicsContext)
}

struct Badge: Drawable {
    let color: Color = .blue
    func draw(in context: GraphicsContext) { /* … */ }
}
```

### 1.1 协议扩展：默认实现与条件扩展

```swift
extension Drawable {
    func debugDescription() -> String { "Drawable(color: \(color))" }  // 默认实现
}

extension Array where Element: Drawable {          // 条件扩展
    var colors: [Color] { map(\.color) }
}
```

**陷阱**: 默认实现走**静态派发**——用 `any Drawable` 调用时，若遵循者后来重写了同名方法，重写版本不会覆盖默认实现（与 class 虚函数不同）。

### 1.2 常用标准库协议

| 协议 | 要求 | 用途 |
|------|------|------|
| `Identifiable` | `id` | SwiftUI ForEach/列表身份 |
| `Hashable / Equatable` | 哈希/相等 | 导航值、Diffable、Set 键 |
| `Codable` | 编解码 | JSON 持久化、网络 |
| `Comparable` | `<` | 排序 |
| `Sendable` | 跨隔离域安全 | Swift 并发 |
| `Error` | 空协议 | throw 的类型约束 |
| `CaseIterable` | `allCases` | 枚举遍历（Picker 常用） |

---

## 2. 关联类型与主关联类型

**定义**: `associatedtype` 让协议带"待定类型"，遵循者决定具体类型。

```swift
protocol Stack {
    associatedtype Element
    mutating func push(_ item: Element)
    func pop() -> Element?
}

struct IntStack: Stack {
    typealias Element = Int          // 可省略，编译器可推断
    private var items: [Int] = []
    mutating func push(_ item: Int) { items.append(item) }
    func pop() -> Int? { items.popLast() }
}
```

**使用关联类型协议的两种姿势**：

```swift
// 泛型函数：编译期解析具体类型（保留类型信息）
func drain<S: Stack>(_ stack: inout S) -> [S.Element] { … }

// 存在类型 any：擦除类型，运行时派发
let stacks: [any Stack] = [intStack, stringStack]   // 元素类型可不同
```

**主关联类型（primary associated types）**：

```swift
protocol Container<Item> {          // 尖括号声明主关联类型
    associatedtype Item
    var items: [Item] { get }
}

func merge<C: Container<String>>(_ c: C) { … }
// 更简洁：func merge(_ c: some Container<String>)
```

Swift 标准库的 `Sequence<Element>`、`Collection<Element>` 均已声明主关联类型。

---

## 3. 泛型

### 3.1 函数与类型

```swift
func firstMatch<T: Equatable>(in list: [T], target: T) -> Int? {
    list.firstIndex(of: target)
}

struct Cache<Key: Hashable, Value> {
    private var store: [Key: Value] = [:]
    subscript(key: Key) -> Value? {
        get { store[key] }
        set { store[key] = newValue }
    }
}
```

### 3.2 约束语法

| 写法 | 含义 |
|------|------|
| `<T: Hashable>` | 遵循协议 |
| `<T: Container>` | 遵循（含关联类型推断） |
| `<T> where T.Element == String` | where 细化 |
| `<T: Collection>` | 协议带主关联类型 |

---

## 4. some vs any：SwiftUI 签名解密

### 4.1 两种多态

| 维度 | `some P`（不透明类型） | `any P`（存在类型） |
|------|------------------------|---------------------|
| 类型确定时机 | 编译期（调用方不可见） | 运行时 |
| 性能 | 零开销（静态派发/特化） | 装箱 + 动态派发 |
| 类型身份 | 保留 → 可 diff | 丢失 → 不可比较 |
| 异构集合 | ❌ | ✅ |
| 嵌套 | 不能再包 another protocol | ✅ |

### 4.2 SwiftUI 为什么是 `some View`

```swift
var body: some View { … }
```

- 修饰符链产生的类型名长达数百字符（如 `ModifiedContent<ModifiedContent<…>>`），`some` 让你免写
- 类型身份保留 → SwiftUI diff 引擎能逐层比较，只更新变化的真实视图
- **返回 `any View` / `AnyView` 的代价**：丢身份、丢优化、强制 SwiftUI 整体重建该子树——仅用于打破无法统一的类型分歧

---

## ⚠️ 高频陷阱速查

- **分支返回不同类型 + some**：`if a { Text() } else { Image() }` 无法直接返回 `some View`——包进 ViewBuilder 或统一容器
- **any 协议里再用关联类型**：`any Stack` 的 `Element` 未知，直接调 `pop()` 编译不过；用 `any Stack<Int>` 指定主关联类型
- **协议扩展遮蔽**：类型自己的实现优先于协议扩展默认实现，但仅当静态类型是具体类型；`any` 引用可能走到默认实现
- **`==` 需要两参数同类型**：Equatable 的 any 版本比较受限，跨类型比较先转具体类型

## 相关文档

- 📄 [01-swift-keywords.md](./01-swift-keywords.md) — some/any/associatedtype 关键字条目
- 📄 [02-optionals-collections.md](./02-optionals-collections.md) — Collection 协议家族的使用侧
- 📄 [01-swiftui-essentials.md](../framework-essentials/01-swiftui-essentials.md) — View 协议体系的应用侧
