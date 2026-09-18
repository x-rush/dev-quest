# 生态集成任务指南 — SwiftData 持久化 + URLSession 网络

## 先看框架承担哪部分职责

**SwiftData 与网络**：网络响应与持久化模型通常需要转换；保存完成、界面更新与远端确认不是同一事件。

**最小练习与预期结果**：先从固定 JSON 构造模型再保存并重启读取；另测 JSON 不合法，不把解码失败误当空数据库。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 把三大系统框架接进 SwiftUI：SwiftData 本地持久化、URLSession 网络请求（async/await）、以及"先网络后缓存"的完整数据链路
>
> **目标读者**: 会写 SwiftUI 界面、要为应用接上真实数据源的中级学习者
>
> **前置知识**: [02-swiftui-advanced.md](./02-swiftui-advanced.md)（@Observable）；[basics/07-concurrency-async-await.md](../basics/07-concurrency-async-await.md)（async/await）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#SwiftData` `#URLSession` `#持久化` `#网络` `#async-await` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 本指南解决什么问题

真实 App 的数据有两个来源：**网络**（远端接口）和**数据库**（本地状态）。本指南给出一条可直接照做的链路：模型定义 → 容器装配 → 网络拉取 → 落库 → UI 展示。

## 🛠️ 任务一：定义 SwiftData 模型

```swift
import SwiftData

@Model                                       // 宏：class → 持久化模型
final class City {
    #Unique<City>([\.name])                  // 唯一约束（Swift 6 写法）

    var name: String
    var temperature: Double
    var updatedAt: Date
    @Relationship(deleteRule: .cascade)      // 级联删除：删城市连带删记录
    var records: [WeatherRecord] = []

    init(name: String, temperature: Double) {
        self.name = name
        self.temperature = temperature
        self.updatedAt = .now
    }
}

@Model
final class WeatherRecord {
    var celsius: Double
    var fetchedAt: Date
    var city: City?                          // 多对一反向关系

    init(celsius: Double) {
        self.celsius = celsius
        self.fetchedAt = .now
    }
}
```

模型即 UI 数据：`@Model` 类自动具备变更追踪，视图读到哪个属性就订阅哪个属性（与 Observation 同一套机制，细节见 [02-swiftdata-observability.md](../reference/framework-essentials/02-swiftdata-observability.md)）。

## 🛠️ 任务二：装配容器与环境

```swift
import SwiftData
import SwiftUI

@main
struct WeatherApp: App {
    var body: some Scene {
        WindowGroup {
            CityListView()
        }
        .modelContainer(for: City.self)      // 一行完成：建库 + 注入环境
    }
}
```

需要自定义配置（如内存库用于 Preview/测试）时：

```swift
let config = ModelConfiguration(isStoredInMemoryOnly: true)   // 测试/预览用
let container = try ModelContainer(
    for: City.self, WeatherRecord.self,
    configurations: config
)
```

## 🛠️ 任务三：URLSession 网络层

### 3.1 定义 API 响应与解码

```swift
struct WeatherResponse: Codable, Sendable {       // Sendable：跨并发域传递
    let main: Main
    struct Main: Codable, Sendable {
        let temp: Double
    }
}
```

### 3.2 async/await 请求 + Swift 6 并发安全

```swift
enum WeatherError: Error {
    case badURL, badResponse(Int), decoding(Error)
}

struct WeatherService: Sendable {
    let session: URLSession = .shared

    func fetchCelsius(city: String) async throws -> Double {
        guard let url = URL(string: "https://api.example.com/weather?q=\(city)") else {
            throw WeatherError.badURL
        }
        let (data, response) = try await session.data(from: url)

        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw WeatherError.badResponse((response as? HTTPURLResponse)?.statusCode ?? -1)
        }
        do {
            return try JSONDecoder().decode(WeatherResponse.self, from: data).main.temp
        } catch {
            throw WeatherError.decoding(error)
        }
    }
}
```

**Swift 6 严格并发要点**：service 声明为 `Sendable` struct；`URLSession.data(from:)` 自带异步取消传播——视图消失时 `.task` 自动取消请求。

## 🛠️ 任务四：网络 → 落库 → UI 完整链路

```swift
struct CityListView: View {
    @Environment(\.modelContext) private var context   // 拿到数据库操作句柄
    @Query(sort: \City.name) private var cities: [City] // 响应式查询：库变视图变
    @State private var isLoading = false
    @State private var errorMessage: String?

    let service = WeatherService()

    var body: some View {
        List {
            ForEach(cities) { city in
                Text("\(city.name): \(Int(city.temperature))°C")
            }
            .onDelete(perform: deleteCities)           // 滑动删除直连数据库
        }
        .overlay {
            if isLoading { ProgressView("拉取天气中…") }
        }
        .alert("加载失败", isPresented: .constant(errorMessage != nil)) {
            Button("好") { errorMessage = nil }
        } message: {
            Text(errorMessage ?? "")
        }
        .task { await refresh() }                      // 出现时加载，消失自动取消
    }

    private func refresh() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let temp = try await service.fetchCelsius(city: "Beijing")
            // 网络结果写进 SwiftData：视图经 @Query 自动刷新
            if let city = cities.first(where: { $0.name == "Beijing" }) {
                city.temperature = temp                // 已有则更新
            } else {
                context.insert(City(name: "Beijing", temperature: temp))
            }
            try context.save()                         // 显式保存
        } catch {
            errorMessage = "\(error)"                  // 错误必须落地到 UI
        }
    }

    private func deleteCities(at offsets: IndexSet) {
        for index in offsets { context.delete(cities[index]) }
    }
}
```

## ✅ 最佳实践

先把网络结果解码成明确 DTO，再决定如何写入持久化模型；解码成功不代表已经满足业务校验。页面任务需要响应取消，写操作还要处理重复触发与服务端实际是否已提交。

Codable 描述编解码，Sendable 描述跨并发边界传递的安全契约，二者互不替代；成员和可变状态仍须满足编译器要求。不要用 unchecked 声明消除不了解的诊断。验收离开页面、重复保存和解码失败三条路径。

## ❌ 避免陷阱

- ❌ 在 `body` 里直接发请求——用 `.task`；`body` 必须保持纯描述
- ❌ 忘记 `try context.save()`——SwiftData 自动保存有时机限制，关键写入显式保存
- ❌ 把 `@Model` 对象跨线程传递——持久化操作走 `@ModelActor`（见并发专题）

## ❓ 常见问题

**Q1: Preview 里没有数据？** 用 `isStoredInMemoryOnly: true` 的容器 + `SampleData` 预填。

**Q2: 关系字段要双向声明吗？** 单向即可运行；声明反向属性便于从记录找城市，代价是级联语义要明确 `deleteRule`。

**Q3: API 域名没配 HTTPS 会被拒吗？** 会。ATS 默认强制 HTTPS，例外配置与原因见 [security-practices 专题](../advanced-topics/security/01-security-practices.md)。

## 🎯 练习

- [ ] 给城市列表加下拉刷新（`.refreshable`），复用 `refresh()`
- [ ] 把" Beijing "温度失败重试改为最多 3 次的指数退避
- [ ] 增加 `WeatherRecord` 写入，展示每城市最近 5 条历史

## 相关文档

- 📄 [02-swiftdata-observability.md](../reference/framework-essentials/02-swiftdata-observability.md) — SwiftData 全量字典
- 📄 [03-concurrency-api.md](../reference/language-concepts/03-concurrency-api.md) — Task/Actor 并发字典
- 📄 [02-weather-app.md](../projects/02-weather-app.md) — 实战：天气应用（本链路完整落地）
- 📄 [07-concurrency-async-await.md](../basics/07-concurrency-async-await.md) — async/await 教程


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
