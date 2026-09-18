# 闭包与函数类型

> **文档简介**: 闭包（Closure）与函数类型的条目式参考：定义、语法简写阶梯、捕获语义、转义行为与 SwiftUI 中的典型用法
>
> **目标读者**: 需要查阅闭包语法细节与陷阱的学习者
>
> **前置知识**: 建议先学 [basics/03-swift-syntax-essentials.md](../../basics/03-swift-syntax-essentials.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#闭包` `#函数类型` `#escaping` `#捕获列表` `#尾随闭包` |
| **更新日期** | `2026年9月` |

</details>

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

// 非逃逸（默认）：闭包不能逃出这次调用；是否执行由函数实现决定，不能承诺零开销
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
| Task 内捕获非 Sendable 值 | 按 Swift 语言模式与隔离设置进行并发检查 | 只捕获 Sendable 值，或用 actor 隔离数据 |
| 捕获的值与任务生命周期不匹配 | 长期任务可能使用旧输入 | 明确重新启动任务还是读取最新输入，不能仅靠闭包写法猜测 |

<!-- full-library-explanation -->
## 画出引用方向，再决定 weak

若 Model 强持有闭包，闭包又强捕获 Model，就形成环。网络操作中的临时闭包不一定形成永久循环，weak 也可能让必要工作因对象消失而不执行。应先画“谁持有谁、持续多久”，再选捕获策略。

```swift
var value = 1
let live = { value }
let snapshot = { [value] in value }
value = 2
print(live(), snapshot()) // 2 1
```

捕获列表在创建闭包时求值。若捕获的是 class 引用，保存该引用并不等于深复制对象。@escaping 说明闭包可以在函数返回后调用，不保证它在后台、一定会调用或只调用一次。

练习：为 Model 添加 deinit 日志，分别使用强捕获、weak 捕获和显式清空回调。验收：能解释释放与否；任务失败有接收路径。丢弃返回句柄的 throwing Task 可能让错误无人观察，不能靠 `[weak self]` 同时解决取消和错误处理。

## 🔗 相关条目

- 📄 [basics/03-swift-syntax-essentials.md](../../basics/03-swift-syntax-essentials.md) §三 — 闭包入门教程
- 📄 [03-concurrency-api.md](./03-concurrency-api.md) — Task 与并发域中的闭包规则
- 📄 [11-actors-sendability.md](./11-actors-sendability.md) — 闭包跨隔离域的 Sendable 要求
- 📄 [01-swift-swiftui-cheatsheet.md](../quick-references/01-swift-swiftui-cheatsheet.md) — 闭包简写速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
