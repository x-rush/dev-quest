# 错误处理

> **文档简介**: Swift 错误处理的条目式参考：Error 协议、throws/try 家族、do-catch、Result 取舍与 typed throws
>
> **目标读者**: 需要查阅错误处理语法与策略的学习者
>
> **前置知识**: 建议先学 [07-enums-pattern-matching.md](./07-enums-pattern-matching.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Error` `#throws` `#do-catch` `#Result` `#typed-throws` |
| **更新日期** | `2026年9月` |

---

## 📌 定义

Swift 的错误处理是**显式的错误传播模型**：任何可能失败的函数用 `throws` 声明，调用方必须用 `try` 承认、用 `do-catch` 处理或继续向上抛——编译器强制让"失败路径"出现在类型签名里。

错误本身是值：任何遵循 `Error` 协议的类型（惯例是枚举）都能表示错误。与 Java/Kotlin 的受检异常不同，Swift 不要求逐个标注错误类型（typed throws 可选地缩小范围），也没有运行时栈展开的心智负担。

## 📖 语法 / 签名

### try 家族

| 写法 | 语义 | 何时用 |
|------|------|--------|
| `try` | 错误继续向上抛 | 已在 `throws` 函数内或 `do-catch` 中 |
| `try?` | 失败转 `nil`，结果变 Optional | 失败可容忍、只要"有没有" |
| `try!` | 断言必成功，失败即崩溃 | 仅限逻辑上可证明不会失败（如测试资源） |
| `try await` | 异步 + 可抛组合 | 网络、磁盘等异步调用 |

### do-catch 与错误分类

```swift
enum ApiError: Error {
    case network(URLError)
    case decoding
    case server(status: Int)
}

do {
    let notes = try await api.fetchNotes()
    render(notes)
} catch let error as ApiError {          // 模式匹配按类型分流
    switch error {
    case .network: showRetry()
    case .decoding: logCorruption()
    case .server(let status): showStatus(status)
    }
} catch {                                // 默认分支兜住一切
    showGenericFailure(error)
}
```

### typed throws：缩小抛出范围

```swift
// 声明只抛 ApiError，调用方 catch 时无需兜底分支
func parse(_ data: Data) throws(ApiError) -> Note { … }
```

### Result：把成败当普通值

```swift
let result: Result<Note, ApiError> = .success(note)   // 可存储、可传递
switch result {
case .success(let note): render(note)
case .failure(let error): alert(error)
}
```

### defer：无论如何都执行

```swift
func read() throws -> String {
    let file = openHandle()
    defer { file.close() }       // 与抛出顺序无关，函数退出前必执行
    return try file.readAll()
}
```

## 💡 示例

### 自定义错误给出用户可读信息

```swift
enum SyncError: Error, LocalizedError {
    case offline
    case conflict

    var errorDescription: String? {
        switch self {
        case .offline:  "网络不可用，稍后自动重试"
        case .conflict: "本地与云端记录冲突，请选择保留版本"
        }
    }
}
```

### SwiftUI 视图中的完整失败链路

```swift
@MainActor @Observable
final class NotesModel {
    var state: ContentState = .idle

    func load() async {
        state = .loading
        do {
            state = .loaded(try await api.fetchNotes())
        } catch is CancellationError {
            state = .idle                    // 任务被取消不算错误
        } catch {
            state = .failed(error.localizedDescription)
        }
    }
}
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 | 解法 |
|------|------|------|
| `try?` 吞掉原因 | 只剩 nil，排查无线索 | 需要上报/展示的错误不要用 `try?` |
| `try!` 进入生产 | 一旦失败直接崩溃 | 仅限测试与可证明的不变量 |
| catch 分支覆盖不全 | 未匹配的 catch 会继续向外抛 | 保留无条件的默认 `catch` |
| 把取消当失败 | Task 取消抛 `CancellationError` | catch 中单独处理 is CancellationError |
| Result 与 throws 混用一层函数 | 两种风格嵌套难读 | 可抛函数内直接 throws；Result 只用于存储/跨边界 |

## 🔗 相关条目

- 📄 [07-enums-pattern-matching.md](./07-enums-pattern-matching.md) — 错误分流依赖模式匹配
- 📄 [03-concurrency-api.md](./03-concurrency-api.md) — async throws 与任务取消
- 📄 [02-troubleshooting.md](../quick-references/02-troubleshooting.md) — 真实报错对照
- 📄 [projects/02-weather-app.md](../../projects/02-weather-app.md) — 网络 + 错误处理实战
