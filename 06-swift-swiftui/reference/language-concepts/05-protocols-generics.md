# 协议、泛型与 some / any

前置：会定义 struct 与函数。协议描述能力；泛型表达类型之间的关系。SwiftUI 的 some View 只是这些语言机制的一种应用，不应从 UI 性能传言反推语言规则。

## 协议要求与扩展新增方法

```swift
protocol Named { var name: String { get }; func greeting() -> String }
extension Named {
    func greeting() -> String { "hello" }
    func debugLabel() -> String { "default label" }
}
struct User: Named {
    let name: String
    func greeting() -> String { "你好，\(name)" }
    func debugLabel() -> String { "user label" }
}
let user = User(name: "Ada")
let named: any Named = user
print(named.greeting())  // 你好，Ada：greeting 是协议要求
print(named.debugLabel()) // default label：仅扩展新增的方法
print(user.debugLabel())  // user label
```

这里关键是方法有没有声明为协议要求。不能把所有扩展默认实现概括成“any 调用时永远静态派发”。继承类遵循协议时还有 witness 等细节，库接口应尽量清楚表达可定制能力。

## 泛型保留类型关系

```swift
func firstEqual<T: Equatable>(_ values: [T], to target: T) -> T? {
    values.first { $0 == target }
}
print(firstEqual([1, 2, 3], to: 2) as Any) // Optional(2)
```

同一个 T 将数组元素、target 和返回值连接起来。把所有参数改成 Any 会失去这个关系，调用方就要做运行时转换。associatedtype 让遵循者确定协议中的类型槽；where 用来限定槽之间的关系。主关联类型要在协议声明中明确列出，不能给任意协议凭空写 P<Int>。

## some 与 any 按谁选择具体类型区分

| 形式 | 谁决定具体类型 | 适合什么 |
|---|---|---|
| 返回 `some P` | 实现者选定并隐藏同一种底层类型 | 保留类型身份但隐藏长类型名 |
| 参数 `some P` / 泛型参数 | 调用者传入满足约束的具体类型 | 同一算法服务不同类型 |
| `any P` | 值中封装某个符合协议的实例，可换成另一种 | 运行时异构存储与接口边界 |

普通返回 some 的函数各返回分支须满足同一底层类型要求；ViewBuilder 可以把条件分支转换成一个统一的组合类型，所以 SwiftUI body 中的 if/switch 常常合法。any 可能引入装箱或动态派发，实际成本受表示和优化影响，不能绝对写成“some 零开销、any 必然堆分配”。

AnyView 是特定类型擦除包装器，any View 是语言存在类型，两者不等价。类型擦除可能影响 SwiftUI 身份与优化，但不能宣称每次更新必然整棵子树重建。先采用自然的 ViewBuilder 与子视图分解，有真实需求再擦除。

## 练习与反馈

把 greeting 从 Named 协议中移除，只保留扩展和 User 实现，预测上例调用结果。再写一个返回 some Named 的函数：分支返回两个不同具体类型时，解释编译器为什么拒绝。验收：能区别协议契约、类型身份和运行时容器，而不是只记“some 快、any 慢”。

标准协议入口：Equatable 管比较、Hashable 支持哈希集合、Codable 管编解码、Identifiable 管稳定身份、Sendable 管跨隔离域传递；它们都不会自动验证业务规则。参考 [Swift 官方 Opaque Types 源文档](https://github.com/swiftlang/swift-book/blob/main/TSPL.docc/LanguageGuide/OpaqueTypes.md)、[Actor 与 Sendable](./11-actors-sendability.md)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
