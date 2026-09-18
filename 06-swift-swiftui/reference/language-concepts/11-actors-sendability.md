# Actor 隔离与 Sendable

> **文档简介**: actor 隔离模型的条目式参考：串行执行域、@MainActor 与全局 actor、Sendable 检查、nonisolated，以及严格并发下的数据竞争防线
>
> **目标读者**: 已会用 async/await、想系统理解隔离与编译器报错的学习者
>
> **前置知识**: 建议先学 [basics/07-concurrency-async-await.md](../../basics/07-concurrency-async-await.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#actor` `#Sendable` `#MainActor` `#隔离` `#数据竞争` |
| **更新日期** | `2026年9月` |

</details>

---

## 📌 定义

**actor** 是一种引用类型，它把自己的可变状态圈进一个**串行执行域**：同一时刻只有一个任务能访问其状态，跨隔离域访问隔离成员通常需要 await；nonisolated 成员等有不同规则。**Sendable** 则标记"可以安全跨隔离域传递"的类型。两者配合，把数据竞争从运行时事故变成编译期错误。

严格并发检查在 Swift 6 **语言模式**下默认开启（本模块基线 6.3）：所有跨隔离域的引用都会被编译器审查。注意编译器的默认语言模式仍是 Swift 5，显式切换到 Swift 6 模式（`-swift-version 6`）后才默认获得严格并发。

> 心智模型：actor 是"自带串行队列的守卫对象"；UI 更新集中在一个特殊的全局 actor——**MainActor** 上。

## 📖 语法 / 签名

### actor 与跨域访问

```swift
actor ImageCache {
    private var cache: [URL: Data] = [:]

    func data(for url: URL) -> Data? { cache[url] }      // actor 内部：同步访问
    func store(_ data: Data, for url: URL) { cache[url] = data }
}

// 外部访问：必须 await（本质是挂起等待串行域空档）
let data = await cache.data(for: url)
```

### MainActor：UI 的专属隔离域

```swift
import Foundation

// 三种标注位置；MainActor.run 必须从 async 上下文调用。
@MainActor func refresh() { print("刷新 UI") }            // 函数
@MainActor final class AppModel {
    var title = "加载中"
    func finish() { title = "完成" }
}                                                         // 整个类型
func finish(_ model: AppModel) async {
    await MainActor.run { model.finish() }                // 一次性闭包
}
```

### Sendable 与跨越边界

```swift
import Foundation

// 所有成员满足 Sendable，编译器可以验证此声明。
struct Note: Sendable { let id: UUID; var title: String }

// 手写声明 + 编译器验证
final class Config: Sendable {
    let apiKey: String        // let 不可变属性可安全共享
    init(apiKey: String) { self.apiKey = apiKey }
}

// 自负其责的逃生门：锁保护全部可变状态；新增状态也必须在同一锁下访问。
final class AtomicBox<Value: Sendable>: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: Value
    init(_ value: Value) { storage = value }
    func withValue<Result: Sendable>(_ body: (inout Value) -> Result) -> Result {
        lock.lock()
        defer { lock.unlock() }
        return body(&storage)
    }
}

let counter = AtomicBox(0)
let next = counter.withValue { value in value += 1; return value }
print(next) // 1；闭包必须同步完成，不要在里面再次访问同一个 box（NSLock 不可重入）。

// nonisolated：把 actor 内的成员排除出隔离域（只读/不碰状态时）
actor Store {
    nonisolated let version = 2
}
```

## 💡 示例

### SwiftUI 的标准并发骨架

```swift
@MainActor @Observable                 // 模型整个落在 MainActor，UI 改它绝不越域
final class WeatherModel {
    var temperature: Double?
    private let service = WeatherService()   // service 自身 actor 隔离

    func load() async {
        // await 切到 service 的隔离域取数，返回值是 Sendable 的 Double
        temperature = try? await service.fetchTemperature()
    }
}
```

### 用 actor 保护跨视图共享资源

```swift
actor DraftStore {
    private var drafts: [Note] = []
    func append(_ note: Note) { drafts.append(note) }
    func all() -> [Note] { drafts }
}

// 两个视图的并发保存请求被 actor 自动串行化，无锁无竞争
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 | 解法 |
|------|------|------|
| 在 actor 外同步访问其状态 | 编译错误，必须 `await` | 调整函数为 async，或把数据做成 Sendable 值拷出 |
| 后台任务直接改 UI 状态 | 数据竞争，编译器会拦 | 模型标 `@MainActor`，或在 `MainActor.run` 中更新 |
| `@unchecked Sendable` 滥用 | 绕过检查，问题后移 | 只在用锁/队列实现真正线程安全时使用 |
| 全局可变 `var` | 严格并发下报"shared mutable state" | 收进 actor、标注 @MainActor，或改为参数传递 |
| 在 actor 里执行长阻塞操作 | 串行域被堵死，其他 await 全部排队 | 优先采用异步 API；确需阻塞调用时使用受控执行资源，不能把 detached 当作通用阻塞池 |
| 误以为 actor 等于线程 | actor 是隔离域不是线程 | 只需关心"谁能访问什么"，调度交给运行时 |

<!-- full-library-explanation -->
## await 之后重新检查假设

actor 防止同一隔离状态被并发无序读写，但方法在 await 挂起期间可能让其他任务进入。若先检查余额、await 一个服务、再扣款，余额可能已被另一任务改变；这属于业务竞态，不会因为使用 actor 自动消失。

练习：两个任务同时预订最后一张票，检查与扣减之间放一个可控挂起点。验收：只能一个成功；可以在不挂起的隔离代码段完成本地检查与预留，失败后按协议释放，服务端最终仍负责权威一致性。

Sendable 不是“复制后就安全”的别名：包含普通可变 class 的 struct 仍可能不满足要求。Task.detached 不自动获得父任务取消与隔离，也不能把阻塞 I/O 变成非阻塞；需给阻塞库设计有界的执行策略。编译器诊断还取决于 Swift 语言模式、默认隔离和所用 SDK，记录这些设置再比较示例。

## 🔗 相关条目

- 📄 [03-concurrency-api.md](./03-concurrency-api.md) — Task/TaskGroup/AsyncStream API 全表
- 📄 [06-closures.md](./06-closures.md) — 闭包捕获与 Sendable 的交集
- 📄 [10-value-types-arc.md](./10-value-types-arc.md) — 值类型天然 Sendable 的原因
- 📄 [advanced-topics/performance/02-concurrency-optimization.md](../../advanced-topics/performance/02-concurrency-optimization.md) — 并发深度专题


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
