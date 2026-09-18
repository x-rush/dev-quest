# Swift 并发深度解析 — Actor、结构化并发与 UI 协作

> **文档简介**: 在 Swift 6 严格并发检查下的并发实践：actor 的隔离模型、结构化并发的任务树、@ModelActor 数据库并发、以及与 SwiftUI 主线程的正确协作
>
> **目标读者**: 已用过 async/await、要理解"为什么编译器逼我这样写"并设计高吞吐并发系统的中高级学习者
>
> **前置知识**: [basics/07-concurrency-async-await.md](../../basics/07-concurrency-async-await.md)（async/await 入门）、[reference/language-concepts/03-concurrency-api.md](../../reference/language-concepts/03-concurrency-api.md)（并发 API 全表）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#Swift6` `#严格并发` `#Actor` `#TaskGroup` `#ModelActor` |
| **更新日期** | `2026年9月` |

</details>

## 🔍 一、严格并发在解决什么问题

Swift 6 的严格并发检查把"数据竞争"从运行时崩溃提前到编译期错误。核心概念只有两个：

1. **隔离域（isolation domain）**：一段代码"属于"哪个执行上下文。`@MainActor` 属于主线程；`actor` 声明属于自己；非隔离不等于固定线程，异步函数执行行为还受工具链与隔离设置影响
2. **可发送性（Sendable）**：值跨隔离域传递时的安全契约——传递后两边不会同时改它

```swift
// 编译器视角的一次跨域调用
@MainActor func refresh() async throws {
    let items = try await service.fetch()   // fetch 的执行域取决于声明和构建设置
    render(items)                           // items 必须是 Sendable，否则编译错误
}
```

**心智模型**：不是"线程安全技巧"，而是"值与代码的归属权证明"。编译器逼你回答的问题始终只有一个——这个状态谁有权改？

## 🔍 二、Actor：可变状态的串行化保险箱

```swift
// 场景：图片缓存被多个视图异步读写——经典竞争
actor ImageCache {
    private var storage: [URL: Data] = [:]      // 只在 actor 内可触碰
    private var inflight: [URL: Task<Data, Error>] = [:]

    func data(for url: URL) async throws -> Data {
        if let cached = storage[url] { return cached }

        // 合并重复请求：N 个调用方共享一次下载（inflight 去重）
        if let running = inflight[url] {
            return try await running.value
        }
        let task = Task { try await download(url) }
        inflight[url] = task

        defer { inflight[url] = nil } // 成功与失败都移除进行中记录
        let data = try await task.value
        storage[url] = data
        return data
    }

    private func download(_ url: URL) async throws -> Data {
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }
        return data
    }
}

// 调用方：await 即"排队进入 actor"，无需锁
let data = try await cache.data(for: url)
```

**要点**：

- actor 内的同步代码天然互斥，**不再需要 NSLock/串行队列**
- `nonisolated` 标注的成员脱离隔离域（只读常量、纯函数）
- 跨 actor 的每次 `await` 都有挂起开销——**热点路径勿按行加 actor**，按"状态簇"划分

### 何时不用 actor

| 场景 | 更优选择 | 原因 |
|------|---------|------|
| 纯计算、无共享状态 | 并发池 `Task.detached`/TaskGroup | actor 只会排队降吞吐 |
| UI 状态 | `@MainActor` 类 | 语义即"主线程" |
| SwiftData 批量写入 | `@ModelActor` | 见第四节 |

## 🔍 三、结构化并发：任务树与生命周期

### 3.1 结构 vs 非结构

```swift
// 结构化：子任务挂在父任务树上——父等待、父取消、错误上抛
try await withThrowingTaskGroup(of: WeatherSnapshot.self) { group in
    for city in cities {                          // 5 个城市并发拉取
        group.addTask {
            try await service.fetch(latitude: city.lat, longitude: city.lon)
        }
    }
    var snapshots: [WeatherSnapshot] = []
    for try await snapshot in group {             // 按完成顺序收割
        snapshots.append(snapshot)
    }
    return snapshots
}
// for try await 观察到错误并向作用域外传播时，未完成子任务收到取消；仍要等待它们响应

// 非结构化：Task { } 脱管运行——生命周期独立于创建者
Task { await syncInBackground() }   // 视图销毁后它还在跑；仅用于确需存活的场景
```

**决策口诀**：能结构化就结构化（`.task`、TaskGroup）；非结构化任务必须记录引用并负责 cancel。

### 3.2 优先级与取消的传播链

```swift
.task {                                     // 视图消失 → SwiftUI 取消此任务
    let detail = try await fetchDetail(id)  // 取消沿任务树自动传播到每个 await
    guard !Task.isCancelled else { return } // 恢复点检查：取消后不碰状态
    model.detail = detail
}
```

- `await` 只标记可能挂起的位置，不保证自动检查取消；**纯 CPU 循环需要手动 `try Task.checkCancellation()`**
- 取消不是强制中断而是"协作请求"——忽略取消是内存泄漏与旧数据覆盖的来源

## 🔍 四、@ModelActor：SwiftData 的并发写入

`ModelContext` 不可跨线程，可用 @ModelActor 把上下文限定在明确的 actor 中：

```swift
import SwiftData

@ModelActor
actor DataImporter {
    /// 批量导入片段：是否占用主线程需检查创建上下文与实际 executor
    func importRecords(_ raw: [(name: String, day: Date)]) throws {
        let context = self.modelContext          // @ModelActor 自动生成，绑定本 actor
        for item in raw {
            let habit = try fetchOrCreateHabit(named: item.name, in: context)
            try Task.checkCancellation()
            let checkIn = CheckIn(date: Calendar.current.startOfDay(for: item.day))
            context.insert(checkIn)
            habit.checkIns.append(checkIn)
        }
        try context.save()                       // 事务性保存
    }

    private func fetchOrCreateHabit(named name: String,
                                    in context: ModelContext) throws -> Habit {
        var descriptor = FetchDescriptor<Habit>(
            predicate: #Predicate { $0.name == name }
        )
        descriptor.fetchLimit = 1
        if let existing = try context.fetch(descriptor).first {
            return existing
        }
        let habit = Habit(name: name, icon: "target")
        context.insert(habit)
        return habit
    }
}

// UI 层调用：主线程只发指令，等结果
try await importer.importRecords(rawRecords)     // 使用 importer 的隔离域；不应仅凭宏名断言后台线程
```

## 🔍 五、与 SwiftUI 的协作契约

```swift
@MainActor
@Observable
final class SyncViewModel {
    var isSyncing = false

    func sync(using importer: DataImporter) async {
        isSyncing = true                          // 主 actor：UI 即时响应
        defer { isSyncing = false }
        do {
            try await importer.importRecords(pending)   // 切到后台 actor
            // 回到主 actor：安全更新 UI 状态
        } catch {
            // 错误也已在主 actor 上，可直接进 UI 状态
        }
    }
}
```

**三条协作纪律**：
1. UI 状态类标 `@MainActor`，后台工作类标 `actor`/`@ModelActor`，边界靠 `await` 穿越
2. 跨边界传值全部 `Sendable`（struct 值类型最省心；`@Model` 对象**禁止**跨界，传 ID 或 DTO）
3. 长任务必须有取消路径（视图 `.task` 生命周期、用户取消按钮）

## ✅ 设计原则小结

- ✅ 隔离域按"状态簇"划分，不按代码行数划分
- ✅ 优先结构化并发，任务树生命周期 = 调用者生命周期
- ✅ 严格并发报错是设计反馈不是障碍——它暴露的是所有权未定义的状态

## ❌ 常见误区

- ❌ "加 actor 让它更快"——actor 是串行化工具不是加速器，热点用 TaskGroup 并行
- ❌ `Task.detached` 修隔离警告——警告说明所有权设计有缺口，绕过只是延后爆炸
- ❌ 在 actor 里跑重 CPU 计算——阻塞该 actor 全部排队者，重计算应 split 到并发池

## 🎯 实践检验

- [ ] 把图片加载改为带 inflight 去重的 ImageCache actor，用 5 个视图并发验证只下载一次
- [ ] 用 TaskGroup 并发拉取 5 城市天气，再制造一个超时，验证取消传播到全部子任务
- [ ] 把 1000 条打卡导入移入 @ModelActor，用 Instruments 对比主线程占用

## 相关文档

- 📄 [03-concurrency-api.md](../../reference/language-concepts/03-concurrency-api.md) — Task/actor/TaskGroup API 全表
- 📄 [01-rendering-performance.md](./01-rendering-performance.md) — 姊妹篇：渲染层性能
- 📄 [07-concurrency-async-await.md](../../basics/07-concurrency-async-await.md) — 入门教程（本文的地基）
- 📄 [01-app-architecture.md](../architecture/01-app-architecture.md) — 副作用边界的架构视角


<!-- full-library-explanation -->
## 失败清理与有界并发也是正确性

ImageCache 用 inflight 合并同 URL 的请求，但共享任务取消策略要单独定义：一个页面离开不一定应取消其他页面仍需要的下载。示例选择让共享下载继续，实际产品可按消费者计数取消；同时为缓存加入容量限制，否则长期使用会持续增长。

练习：并发请求同一 URL 五次，测试服务应只收到一次；第一次返回 500，再请求必须重新下载，不能永远复用失败 Task。随后请求 1000 个不同 URL，把同时执行数量限制为配置值，而不是一次创建所有网络任务。记录峰值并发和错误，结果按业务需要重新排序。

actor 在 await 处可重入，应在恢复后重新检查依赖的不变量。TaskGroup 的取消是协作式，作用域退出会等待子任务结束；子任务不响应取消时仍可能拖住父任务。Sendable 描述安全跨域契约，struct 若包含不安全引用成员也不会自动满足要求。

工具链、语言模式、默认 actor 隔离与 NonisolatedNonsendingByDefault 设置共同决定部分执行语义。不要用“async 就去后台”解释性能；参考 [SE-0461](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md)。本轮未执行 Swift 并发测试。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
