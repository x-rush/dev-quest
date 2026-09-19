# Swift 高频内置函数 / 全局函数：断言、转换、序列与生命周期边界

> **文档简介**: 说明 Swift 标准库中常见全局函数与类型方法的职责，重点区分调试断言、不可恢复不变量、可恢复输入错误和资源/对象生命周期。

> **前置知识**: [Swift 关键词](./01-swift-keywords.md)、[Optional 与集合](./02-optionals-collections.md)。Foundation 类型见 [Foundation 与标准库](../library-guides/01-foundation-and-stdlib.md)，错误模型见 [错误处理](./08-error-handling.md)。

Swift 的高频能力分布在全局函数、协议扩展与标准类型方法中。`print`、`min`、`zip`、`stride`、`assert` 和 `precondition` 都在标准库，但它们不是同一种“内置函数”：有些只用于诊断，有些决定控制流，有些只构造惰性序列。先决定失败能否由用户恢复，再选 API。

## 失败语义：不要把断言当校验

| 目的 | 能力 | 失败时 | 适用边界 |
|---|---|---|---|
| 开发期检查假设 | `assert(condition, message)` | Debug 配置触发断言；优化发布构建可不执行 | 开发者不变量，不处理外部输入 |
| 生产中也必须成立的不变量 | `precondition(condition, message)` | 条件不满足时终止程序（极端优化选项例外） | 调用者违反明确 API 前置条件 |
| 当前路径绝不应继续 | `fatalError(message)` | 不返回 | 尚未实现的内部不可达分支；不用于网络或表单错误 |
| 可恢复的业务失败 | `throws`、`Result`、可选值 | 调用方处理 | 用户输入、文件、网络、权限、数据解码 |

```swift
enum PageError: Error { case invalidPage }

func parsePage(_ text: String) throws -> Int {
    guard let page = Int(text), (1...100).contains(page) else {
        throw PageError.invalidPage
    }
    return page
}

// assert(text.isEmpty == false) 不能替代上面的外部输入检查。
```

`Int(text)` 只尝试整数转换；范围、业务权限和资源存在性仍需分别验证。把 `try!` 或强制解包用于来自 URL、JSON、存储或用户编辑的值，只会把可恢复错误变成崩溃。

## 常用序列与比较函数

| 任务 | 能力 | 结果与边界 |
|---|---|---|
| 取可比较序列的极值 | `min()` / `max()` | 空序列返回 `nil`；自定义比较使用 `min(by:)` / `max(by:)` |
| 配对两个序列 | `zip(left, right)` | 在较短序列结束时停止，不能发现“长度本应相同”的数据错误 |
| 生成范围步进 | `stride(from:to:by:)` / `through:` | `to` 不含终点，`through` 包含终点；步长方向必须能到达终点 |
| 遍历索引和值 | `enumerated()` | offset 是遍历位置，不一定是集合的真实 `Index` |
| 合并或变换 | `map` / `compactMap` / `flatMap` | `compactMap` 丢弃 nil；nil 若代表失败则应保留错误原因 |
| 只执行调试输出 | `print` / `debugPrint` | 输出格式不是稳定协议，生产日志应有结构化字段与隐私策略 |

```swift
let names = ["Ada", "Lin", "Mika"]
let scores = [91, 85]
print(Array(zip(names, scores))) // [("Ada", 91), ("Lin", 85)]

let steps = Array(stride(from: 0, to: 6, by: 2))
print(steps) // [0, 2, 4]
```

上例的第三个名字被 `zip` 安静忽略。若业务要求每位用户都有分数，先比较长度或按稳定 ID 连接数据，再决定如何报告缺项。

## 可选值、类型转换与对象生命周期

`as?` 是可失败类型转换，返回可选值；它只确认运行时类型，不检查内容。`as!` 在类型不符时崩溃，应仅用于已由受控框架 API 保证的场景，并在代码旁写出保证来源。`type(of:)` 可用于调试，不能用于授权或序列化协议判断。

`withExtendedLifetime(value) { ... }` 在底层指针或 C API 交互时延长值存活到闭包结束；它不修复悬垂指针、线程安全或资源所有权设计。普通 SwiftUI/网络代码不应因担心 ARC “太早释放”随意加入它。资源清理由 `defer`、`close`、任务取消处理或具体框架生命周期承担，不能依赖对象何时析构。

## 练习与验收

实现一个纯函数：输入两个 `String` 数组，代表用户 ID 与分数文本；只有长度相同、ID 非空、分数可转换且在 0...100 时才返回配对结果。分别测试长度不等、空 ID、非数字和边界分数。说明哪些失败用 `throws`/`Result` 返回，哪些内部不变量可用 `precondition`，并证明没有用 `zip` 静默丢失数据。

本页描述 Swift 标准库语义，不代表 SwiftUI、Xcode、iOS 设备或 C/Objective-C 桥接已在当前主机运行。权威 API 定义见 [Swift Standard Library](https://developer.apple.com/documentation/swift/swift-standard-library)。
