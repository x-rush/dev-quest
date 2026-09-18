# Swift 并发 - async/await、Task 与 Actor

## 先理解，再动手

await 允许挂起，不承诺换后台线程。Actor 限制状态访问的隔离边界，Task 还需要取消和错误处理。

**本节自测**：做一次可取消加载，快速离开页面后观察结果是否还修改已失效界面。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

取消后停止不需要的工作；处理取消与真实失败时给出不同反馈。

</details>

> **文档简介**: 系统掌握 Swift Concurrency：async/await 语法、Task 任务管理、Actor 数据隔离与 MainActor，理解 SwiftUI 中异步数据的正确加载方式
>
> **目标读者**: 已掌握 SwiftUI 基础、准备处理网络请求等异步操作的学习者
>
> **前置知识**: [04-views-state.md](./04-views-state.md)；[03-swift-syntax-essentials.md](./03-swift-syntax-essentials.md) 的闭包部分

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#async-await` `#Task` `#Actor` `#MainActor` `#并发` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 async/await 重写回调风格的异步代码
- ✅ 在 SwiftUI 中用 `.task` 与 `Task` 正确发起并取消异步工作
- ✅ 理解 actor 隔离与 `@MainActor`，写出通过 Swift 6 严格并发检查的代码

## 🔍 一、async/await：线性异步代码

```swift
func fetchUser(id: Int) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, response) = try await URLSession.shared.data(from: url)
    guard (response as? HTTPURLResponse)?.statusCode == 200 else {
        throw FetchError.badStatus
    }
    return try JSONDecoder().decode(User.self, from: data)
}
```

- `async` 标记"这是可挂起函数"；`throws` 表示错误用 `try` 传播
- `await` 标记"此处可能让出线程"，挂起期间线程可去做别的事——不是阻塞等待
- 组合顺序：`try await`（先挂起再检查错误）

## 🔍 二、Task：异步工作的生命周期

### 2.1 SwiftUI 的 .task 修饰符（首选）

```swift
struct UserListView: View {
    @State private var users: [User] = []

    var body: some View {
        List(users) { Text($0.name) }
            .task {
                // 视图出现时自动执行；视图消失时自动取消
                users = (try? await fetchAllUsers()) ?? []
            }
    }
}
```

`.task` 的三大优势：自动绑定视图生命周期、自动 `@MainActor`、视图消失自动取消。**优先于 `onAppear` 里手动起 Task**。

### 2.2 显式 Task：事件驱动的异步

```swift
Button("刷新") {
    Task {
        users = (try? await fetchAllUsers()) ?? []
    }
}
```

`Task { }` 创建**非结构化**任务：继承当前 actor 与优先级，但生命周期不挂在任何父任务上（视图销毁后仍在跑，SwiftUI 中优先用 `.task` 修饰符）。**结构化**并发请用 `async let` 或 `TaskGroup`——子任务随父任务作用域自动取消与等待。

### 2.3 取消

```swift
func fetchAllUsers() async throws -> [User] {
    var all: [User] = []
    for page in 1... {
        try Task.checkCancellation()      // 协作式取消检查点
        let batch = try await fetchPage(page)
        all += batch
        if batch.isEmpty { break }
    }
    return all
}
```

Swift 并发是**协作式取消**：取消只是打标记，代码需要在检查点主动响应。`URLSession.data(for:)` 等系统 API 已内置响应。

## 🔍 三、Actor：数据隔离

多个任务同时读写一个 class 实例 = 数据竞争。Swift 6 模式下编译器直接报错，而不是等线上崩溃。

### 3.1 actor：串行数据隔离

```swift
actor ImageCache {
    private var cache: [URL: Data] = [:]
    private var inflight: [URL: Task<Data, Error>] = [:]

    func data(for url: URL) async throws -> Data {
        if let hit = cache[url] { return hit }
        if let task = inflight[url] { return try await task.value }

        let task = Task { try await download(url) }     // 防缓存击穿
        inflight[url] = task
        let data = try await task.value
        cache[url] = data
        inflight[url] = nil
        return data
    }
}

// 调用方：await 表明"排队进入 actor"
let data = try await cache.data(for: imageURL)
```

- actor 的可变属性只能在其内部访问，外部访问自动变为 `await` 排队
- actor 内部是**串行执行**的，天然免数据竞争
- `nonisolated` 可标记不需要隔离的成员（如纯计算常量）

### 3.2 @MainActor：UI 线程隔离

SwiftUI 的 `body`、`.task` 等已是 `@MainActor`。更新 UI 状态的代码必须跑在主 actor：

```swift
// ✅ 视图内：.task 已在 MainActor，直接改 @State
.task {
    users = try await api.fetchUsers()   // fetchUsers 本身可在后台 actor 运行
}

// ✅ 模型层：把整个 store 标为主 actor
@MainActor @Observable
final class NoteStore {
    var notes: [Note] = []
    func load() async {
        notes = try await api.fetch()    // await 处自动切回主 actor
    }
}
```

经验法则：**模型 store 标 `@MainActor`（简单安全），重 IO 的 API 客户端用独立 actor 或 nonisolated async 函数**。

## 🔍 四、SwiftUI 异步加载完整模式

把本课组合成标准的"加载中/成功/失败"界面：

```swift
struct ArticleListView: View {
    @State private var phase: LoadPhase<[Article]> = .idle

    var body: some View {
        content
            .navigationTitle("文章")
            .task { await load() }
            .refreshable { await load() }       // 下拉刷新，同样自动取消
    }

    @ViewBuilder
    private var content: some View {
        switch phase {
        case .idle, .loading:
            ProgressView("加载中…")
        case .loaded(let articles):
            List(articles) { Text($0.title) }
        case .failed(let message):
            ContentUnavailableView {
                Label("加载失败", systemImage: "wifi.exclamationmark")
            } description: {
                Text(message)
            } actions: {
                Button("重试") { Task { await load() } }
            }
        }
    }

    private func load() async {
        phase = .loading
        do {
            phase = .loaded(try await api.fetchArticles())
        } catch is CancellationError {
            // 取消不是错误：静默即可
        } catch {
            phase = .failed(error.localizedDescription)
        }
    }
}
```

## ✅ 最佳实践

任务应由真正负责它生命周期的对象持有。随页面存在而加载的数据可用 task/task(id:)，用户点击触发的任务则要考虑取消、重复点击和结果归属。取消是协作式的，任务内部或下游 API 仍需响应取消，不能视为免费清理一切。

UI 状态通常需要遵守主 actor 隔离；网络层是否需要独立 actor 取决于是否管理共享可变状态，不必为每个服务都创建 actor。模拟快速切换查询条件，确认旧结果不会覆盖当前内容。

## ❓ 常见问题

### Q1: "Mutation of captured var in concurrently-executing code"？

并发闭包捕获了局部 `var`。把可变状态挪进 actor，或用 `Task` 返回值（`TaskGroup` 收集结果，见 [03-concurrency-api.md](../reference/language-concepts/03-concurrency-api.md)）。

## 🎯 练习与实践

### 练习一：基础练习

- [ ] 把一个回调风格的网络请求封装改为 `async throws` 并在 `.task` 中调用
- [ ] 在分页加载循环中调用 `try Task.checkCancellation()`，验证页面离开时 `.task` 自动取消且不报错
- [ ] 实现 ArticleListView 的 idle/loading/loaded/failed 四态

---

## 相关文档

- 📄 [08-first-project.md](./08-first-project.md) — 综合运用：待办 App
- 📄 [03-concurrency-api.md](../reference/language-concepts/03-concurrency-api.md) — Task/TaskGroup/AsyncSequence 全表
- 📄 [01-swift-keywords.md](../reference/language-concepts/01-swift-keywords.md) — actor/sending 等关键字详解


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
