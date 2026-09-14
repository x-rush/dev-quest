# URLSession 网络基础

> **文档简介**: URLSession 全量速查：shared 单例、async/await 的 data(for:)、URLSessionConfiguration、请求构造（方法/头部/请求体）、上传下载、URLError 错误处理与 Codable 解码组合
>
> **目标读者**: 需要查网络请求 API 形态的全体学习者（字典条目，可任意跳入）
>
> **前置知识**: async/await 见 [03-concurrency-api.md](./03-concurrency-api.md)；教程路径见 [basics/07-concurrency-async-await.md](../../basics/07-concurrency-async-await.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#URLSession` `#网络` `#async-await` `#Codable` |
| **更新日期** | `2026年9月` |

## 📌 定义

`URLSession` 是 Foundation 的 HTTP 客户端：负责发起请求、处理缓存/重定向/认证，并以 `Data`/文件/字节流三种形式返回响应体。iOS 15 起提供 async/await API，是 Swift 6 并发时代网络层的事实标准入口。

---

## 1. 入口：单例与自定义 Session

| 创建方式 | 场景 |
|----------|------|
| `URLSession.shared` | 简单请求的默认入口（无 delegate、不可后台） |
| `URLSession(configuration:)` | 需要定制超时/缓存/头部 |
| `URLSession(configuration:delegate:delegateQueue:)` | 需要证书校验、重定向、进度回调 |

**原则**: 一个 app 维护少量长生命周期 session，**不要每个请求新建**（session 自带连接池与缓存，频繁创建浪费资源）。

## 2. async/await API（iOS 15+）

| 方法 | 返回 | 用途 |
|------|------|------|
| `data(from: URL)` | `(Data, URLResponse)` | GET 取数据 |
| `data(for: URLRequest)` | `(Data, URLResponse)` | 自定义方法/头部/请求体 |
| `upload(for:from: Data)` | `(Data, URLResponse)` | 上传请求体 |
| `download(from:)` | `(URL, URLResponse)` | 下载到临时文件（大文件首选） |
| `bytes(for: URLRequest)` | `(URLSession.AsyncBytes, URLResponse)` | 流式逐行读取 |

旧式 `dataTask(with:completionHandler:)` 仍可用，但 Swift 并发代码统一用上表；两者都内建响应 Task 取消（挂起中取消会抛错，见 §5）。

## 3. 请求构造：URLRequest

```swift
var request = URLRequest(url: URL(string: "https://api.example.com/notes")!)
request.httpMethod = "POST"
request.setValue("application/json", forHTTPHeaderField: "Content-Type")
request.setValue("Bearer <token>", forHTTPHeaderField: "Authorization")
request.timeoutInterval = 15
request.httpBody = try JSONEncoder().encode(payload)   // 请求体（Data）
```

| 属性 | 说明 |
|------|------|
| `httpMethod` | `"GET"`（默认）`"POST"` `"PUT"` `"DELETE"` |
| `setValue(_:forHTTPHeaderField:)` | 逐条设置头部 |
| `httpBody` / `httpBodyStream` | 请求体 Data / 流 |
| `timeoutInterval` | 单请求超时（秒） |
| `cachePolicy` | 缓存策略（`.useProtocolCachePolicy` 默认） |

## 4. URLSessionConfiguration

| 配置 | 说明 |
|------|------|
| `.default` | 常规磁盘缓存 |
| `.ephemeral` | 不落盘（内存缓存/cookie 不持久），登录态等敏感会话 |
| `background(withIdentifier:)` | 系统托管的后台传输（**只支持上传/下载任务，不支持 dataTask**） |

常用字段：

```swift
let config = URLSessionConfiguration.default
config.timeoutIntervalForRequest = 15        // 两次数据包之间的空闲超时
config.timeoutIntervalForResource = 60       // 整个请求的总时限
config.waitsForConnectivity = true           // 无网时等待而非立即报错（适合自动重试场景）
config.httpAdditionalHeaders = ["X-App-Version": "2.1"]
let session = URLSession(configuration: config)
```

## 5. 响应与错误处理

**两层检查缺一不可**：网络层错误（抛 URLError）+ HTTP 状态码（不抛错，需自查）。

```swift
func fetchStatus() async throws -> Int {
    let (data, response) = try await URLSession.shared.data(from: url)
    guard let http = response as? HTTPURLResponse else {
        throw URLError(.badServerResponse)
    }
    guard (200..<300).contains(http.statusCode) else {
        throw APIError.status(http.statusCode)   // 404/500 不会抛 URLError！
    }
    return http.statusCode
}
```

URLError 高频 code（NSURLError 域，数值稳定）：

| code | 数值 | 含义 |
|------|------|------|
| `.badURL` | -1000 | URL 非法 |
| `.timedOut` | -1001 | 请求超时 |
| `.cannotFindHost` | -1003 | 域名解析失败 |
| `.cannotConnectToHost` | -1004 | 连接失败 |
| `.networkConnectionLost` | -1005 | 传输中断网 |
| `.notConnectedToInternet` | -1009 | 无网络连接 |
| `.cancelled` | -999 | 请求被取消（Task 取消时也抛 `CancellationError`，两者都要接） |

## 6. 与 Codable 组合（GET + 解码）

```swift
struct Weather: Codable { let city: String; let tempC: Double }

func loadWeather() async throws -> Weather {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(Weather.self, from: data)
}
```

键名策略、`CodingKeys`、嵌套默认值等解码细节见 [../library-guides/01-foundation-and-stdlib.md §3 Codable](../library-guides/01-foundation-and-stdlib.md)，此处不重复。

## 💡 完整示例（POST + 状态码 + 错误分流）

```swift
enum APIError: Error { case status(Int) }

func createNote(title: String) async throws -> Note {
    var request = URLRequest(url: URL(string: "https://api.example.com/notes")!)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.httpBody = try JSONEncoder().encode(["title": title])

    let (data, response) = try await URLSession.shared.data(for: request)

    guard let http = response as? HTTPURLResponse,
          (200..<300).contains(http.statusCode) else {
        throw APIError.status((response as? HTTPURLResponse)?.statusCode ?? -1)
    }
    return try JSONDecoder().decode(Note.self, from: data)
}
```

调用侧：`@MainActor` 方法内 `try await` 之后直接赋值 `@State` 即可（隔离随 actor 恢复，无需手动切线程）；取消会从 `await` 点抛出，自动冒泡。

## ⚠️ 常见陷阱

- ❌ **只 try 不查状态码**：404/500 是"成功完成的 HTTP 响应"，不抛 URLError，把错误页 body 当数据解码
  ✅ 每次请求都先 `guard (200..<300).contains(statusCode)`。
- ❌ **background session 跑 dataTask**：后台 session 只支持上传/下载任务，dataTask 直接失效
  ✅ 后台大文件用 `download`/`upload` + delegate 收进度；常规请求用 default/ephemeral。
- ❌ **每个请求 `URLSession(configuration:)` 新建**：连接池与缓存全部失效
  ✅ 应用级复用 1-2 个 session（共享单例 + 一个定制实例）。
- ❌ **catch 里不区分取消**：`URLError.cancelled` 与 `CancellationError` 混当普通错误上报
  ✅ 取消单独静默处理（见 [../quick-references/02-troubleshooting.md](../quick-references/02-troubleshooting.md)）。
- ❌ **`httpBody` 挂在 URLSession 上找**：请求体属于 `URLRequest`，不属于 session
  ✅ 构造完整 URLRequest 再 `data(for:)`。

## 🔗 相关条目

- 📄 **[01-foundation-and-stdlib.md](../library-guides/01-foundation-and-stdlib.md)** - Codable/JSONDecoder 解码细节（§3）
- 📄 **[03-concurrency-api.md](./03-concurrency-api.md)** - Task/取消与 async 签名全表
- 📄 **[02-weather-app.md](../../projects/02-weather-app.md)** - URLSession + SwiftData 实战项目
- 📄 **[02-third-party-libs.md](../library-guides/02-third-party-libs.md)** - Alamofire 引入边界
- 🌐 **[官方文档：URLSession](https://developer.apple.com/documentation/foundation/urlsession)** - Apple 开发者文档

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
