# Swift 并发 API 全表

> **文档简介**: Task、TaskGroup、Actor、AsyncSequence、锁与 GCD 桥接的完整条目式参考，每个 API 给出签名、示例与陷阱
>
> **目标读者**: 需要查阅并发 API 细节的中级学习者
>
> **前置知识**: 建议先学 [basics/07-concurrency-async-await.md](../../basics/07-concurrency-async-await.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#并发` `#Task` `#TaskGroup` `#Actor` `#AsyncSequence` |
| **更新日期** | `2026年9月` |

---

## 1. Task

**定义**: 异步工作的单元，携带取消状态、优先级与 task-local 值。

### 1.1 创建

```swift
// 非抛错任务
let t = Task { await work() }

// 抛错任务：结果为 Result
let t2 = Task { try await fetch() }

let t4 = Task.detached { independent() }   // 不继承 actor/优先级，慎用
```

### 1.2 静态成员

| API | 说明 |
|-----|------|
| `Task.checkCancellation()` | 取消则抛 `CancellationError` |
| `Task.isCancelled` | 只读取消标志 |
| `Task.yield()` | 让出线程，适合长循环 |
| `Task.sleep(for: .seconds(1))` | 非阻塞休眠 |

### 1.3 实例成员

`t.cancel()` 请求取消；`t.value` 是 `{ get async throws }` 属性——必须 `try await t.value` 取结果（非抛错任务免 `try`），不带 `await` 直接访问是编译错误，不存在同步阻塞变体。

**陷阱**: `Task {}` 在 SwiftUI View 中是**非结构化**的——视图销毁后任务仍在跑。视图生命周期任务必须用 `.task` 修饰符。

---

## 2. async let

**定义**: 并行子任务语法糖，编译器生成隐式 TaskGroup。

```swift
async let a = fetchA()          // 立即并行启动
async let b: [Post] = fetchB()
let summary = Summary(a: try await a, b: try await b)   // 汇合点
```

**陷阱**: 若 `a` 已 await 而 `b` 抛错，`a` 的子任务会被自动取消——取消语义是结构化的。

---

## 3. TaskGroup

**定义**: 动态数量并发任务的容器；适合"列表逐项处理、控制并发、收集结果"。

```swift
func thumbnails(for urls: [URL]) async throws -> [Image] {
    try await withThrowingTaskGroup(of: Image.self) { group in
        for url in urls {
            group.addTask { try await render(url) }
        }
        var images: [Image] = []   // 逐个收结果（按完成顺序）
        for try await image in group { images.append(image) }
        return images
    }
}
```

### 3.1 API 速查

| API | 说明 |
|-----|------|
| `withTaskGroup(of:returning:body:)` | 非抛错组 |
| `withThrowingTaskGroup(of:…)` | 任一子任务抛错 → 组取消并向外抛 |
| `group.addTask {…}` | 添加子任务（自动继承取消） |
| `group.addTaskUnlessCancelled {…}` | 已取消时不再添加 |
| `group.cancelAll()` | 取消全部子任务 |
| `group.waitForAll()` | 等待并排空 |

---

## 4. Actor

**定义**: 引用类型 + 自动串行化；所有可变状态被隔离，跨 actor 访问必须 `await`。

```swift
actor Counter {
    private(set) var count = 0
    func increment() { count += 1 }          // 内部：直接访问
}

let c = Counter()
await c.increment()                          // 外部：排队进入
let n = await c.count                        // 读也要 await
```

### 4.1 相关声明

| 声明 | 作用 |
|------|------|
| `actor` | 定义隔离域 |
| `@MainActor` | 主线程隔离，UI 默认域 |
| `nonisolated` | 成员豁免隔离（不可变/纯函数） |

### 4.2 MainActor 常用写法

```swift
@MainActor func updateUI() { … }                    // 函数级
@MainActor final class Store { … }                  // 类型级
await MainActor.run { label.text = "ok" }           // 代码块级（桥接旧代码）
```

**陷阱**: 在非隔离 async 函数中直接写 `@MainActor` 属性会编译报错；要么整个函数标 `@MainActor`，要么在 `MainActor.run` 内修改。

---

## 5. AsyncSequence / AsyncStream

**定义**: 异步版本的 Sequence，`for await` 逐个消费；组合子 `map`/`prefix`/`removeDuplicates` 均可用。内置来源如 `URL.lines`、`NotificationCenter.notifications(named:)`；自定义流用 `AsyncStream`：

```swift
let ticks = AsyncStream<Int> { continuation in
    let task = Task {
        for i in 0..<10 {
            try await Task.sleep(for: .seconds(1))
            continuation.yield(i)          // 产出值
        }
        continuation.finish()              // 结束序列
    }
    continuation.onTermination = { _ in task.cancel() }
}
for await tick in ticks { print(tick) }
```

---

## 6. 锁与 GCD 桥接

| 需求 | 现代写法 | 遗留写法 |
|------|----------|----------|
| 互斥保护 | `actor` 或 `Mutex`（Synchronization 框架） | `NSLock`、`os_unfair_lock` |
| 主线程回调 | `@MainActor` + async/await | `DispatchQueue.main.async` |
| 延迟执行 | `Task.sleep(for:)` | `asyncAfter` |

**迁移建议**: 新代码全用结构化并发；GCD 仅在无法改造的 ObjC 回调边界使用，用 `withCheckedContinuation` 包装：

```swift
func fetchLegacy() async throws -> Data {
    try await withCheckedThrowingContinuation { cont in
        legacyAPI { result in cont.resume(with: result) }
    }
}
```

## ⚠️ 高频陷阱速查

- **Task 泄漏**：`Task {}` 无外部引用也可能无限跑；循环轮询务必响应取消
- **continuation 只能 resume 一次**：多路径/异常路径都要覆盖，否则永久挂起或崩溃

## 相关文档

- 📄 [01-swift-keywords.md](./01-swift-keywords.md) — actor/sending/Sendable 关键字
- 📄 [04-swiftui-state-api.md](./04-swiftui-state-api.md) — 与 UI 状态配合的包装器
- 📄 [02-troubleshooting.md](../quick-references/02-troubleshooting.md) — 并发警告与线程问题排查
