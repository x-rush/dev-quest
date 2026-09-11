# 闭包与函数类型

> **文档简介**: 闭包（Closure）与函数类型的条目式参考：定义、语法简写阶梯、捕获语义、转义行为与 SwiftUI 中的典型用法
>
> **目标读者**: 需要查阅闭包语法细节与陷阱的学习者
>
> **前置知识**: 建议先学 [basics/03-swift-syntax-essentials.md](../../basics/03-swift-syntax-essentials.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#闭包` `#函数类型` `#escaping` `#捕获列表` `#尾随闭包` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

**闭包**是捕获了所在上下文常量与变量的自包含函数值。Swift 中函数与闭包是**一等公民**：可以赋值给变量、作为参数传递、作为返回值返回。

**函数类型**写作 `(参数类型列表) -> 返回类型`，例如 `(Int, Int) -> Int`；`()` 表示无参数，`Void` 表示无返回值。

> 与其他语言对照：Kotlin lambda、Go 的函数值、JavaScript 箭头函数都属同类概念；Swift 的差异点在**捕获语义**与**转义（escaping）区分**。

## 📖 语法 / 签名

### 从完整形式到最简形式的阶梯

```swift
// 1. 完整形式
let add: (Int, Int) -> Int = { (a: Int, b: Int) -> Int in
    return a + b
}

// 2. 类型可从上下文推断 → 省略参数类型与 return
let add2: (Int, Int) -> Int = { a, b in a + b }

// 3. 隐式参数 $0、$1…
let add3: (Int, Int) -> Int = { $0 + $1 }

// 4. 操作符函数直接当闭包用
let sum = [1, 2, 3].reduce(0, +)
```

### 尾随闭包（Trailing Closure）

```swift
// 函数的最后一个参数是函数类型时，可把闭包移出括号
Button("保存") { save() }

// 多个尾随闭包：第一个省略参数标签，其余保留
Button {
    save()
} label: {
    Text("保存")
}
```

### escaping 与捕获列表

```swift
// @escaping：闭包生命周期超出函数调用（存储起来稍后调用）
func observe(onUpdate: @escaping () -> Void) { … }

// 非逃逸（默认）：闭包在函数返回前执行完毕，无捕获管理开销
func twice(_ work: () -> Void) { work(); work() }
```

```swift
// 捕获列表：显式声明捕获方式，[weak self] 防止引用循环
class Model {
    var title = "Swift"
    var onUpdate: (() -> Void)?
    func bind() {
        onUpdate = { [weak self] in
            guard let self else { return }
            print(self.title)
        }
    }
}
```

## 💡 示例

### 1. SwiftUI 中的闭包无处不在

```swift
struct CounterView: View {
    @State private var count = 0
    var body: some View {
        Button("加一") {               // action 是逃逸闭包（Button 会存储它）
            count += 1
        }
        .onAppear {                   // 生命周期回调也是闭包
            print("appeared")
        }
    }
}
```

### 2. 集合变换五件套

```swift
let scores = [88, 45, 92, 60]
let passed  = scores.filter { $0 >= 60 }        // [88, 92, 60]
let names   = scores.map { "分数：\($0)" }
let highest = scores.max()                       // 92
let sorted  = scores.sorted { $0 > $1 }          // 自定义比较闭包
```

### 3. 闭包做回调（逃逸 + weak self）

```swift
final class WeatherService {
    var onFetched: ((Double) -> Void)?
    func load() {
        Task { [weak self] in
            let temp = try await fetchTemperature()
            self?.onFetched?(temp)
        }
    }
}
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 | 解法 |
|------|------|------|
| 强引用循环 | 逃逸闭包捕获 `self`，`self` 又持有闭包 | 捕获列表 `[weak self]` + `guard let self` |
| `$0` 滥用 | 多个隐式参数可读性差 | 参数超过 2 个时改用具名参数 |
| 尾随闭包错位 | 多尾随闭包漏写第二个标签 | 第一个省略标签，其余必须写标签 |
| Task 内捕获非 Sendable 值 | 严格并发（默认开启）下编译报错 | 只捕获 Sendable 值，或用 actor 隔离数据 |
| 在 `body` 里定义闭包又捕获状态 | 造成不必要的重算 | 闭包里只改状态，别复制状态 |

## 🔗 相关条目

- 📄 [basics/03-swift-syntax-essentials.md](../../basics/03-swift-syntax-essentials.md) §三 — 闭包入门教程
- 📄 [03-concurrency-api.md](./03-concurrency-api.md) — Task 与并发域中的闭包规则
- 📄 [11-actors-sendability.md](./11-actors-sendability.md) — 闭包跨隔离域的 Sendable 要求
- 📄 [01-swift-swiftui-cheatsheet.md](../quick-references/01-swift-swiftui-cheatsheet.md) — 闭包简写速查
