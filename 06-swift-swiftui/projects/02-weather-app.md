# 实战项目二：天气应用（网络 + CoreLocation）

> **文档简介**: 构建一个获取定位、请求天气 API、缓存到 SwiftData 的天气应用，打通"定位 → 网络 → 持久化 → UI"完整数据链路
>
> **目标读者**: 做过入门项目、要掌握异步数据流与系统能力集成的学习者
>
> **前置知识**: [frameworks/03-ecosystem-integration.md](../frameworks/03-ecosystem-integration.md)（SwiftData + URLSession）、[basics/07-concurrency-async-await.md](../basics/07-concurrency-async-await.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南（实战项目） |
| **难度** | ⭐⭐ |
| **标签** | `#URLSession` `#CoreLocation` `#async-await` `#SwiftData` `#错误处理` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

最终效果：打开 App 自动定位 → 拉取当前天气 → 展示温度/天气图标 → 保存查询历史，断网时显示缓存。

**功能清单**：
- ✅ CoreLocation 获取经纬度（含权限处理）
- ✅ 天气 API 请求（async/await + Codable）
- ✅ SwiftData 缓存最近一次成功结果
- ✅ 加载中 / 失败重试 / 无权限三类状态

## 🛠️ 第一步：定位服务（可注入的 LocationManager）

```swift
import CoreLocation

@Observable                                   // 让定位状态可被视图订阅
final class LocationManager: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()

    var location: CLLocation?
    var errorMessage: String?

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyKilometer   // 天气场景不需要米级
    }

    func requestPermission() {
        manager.requestWhenInUseAuthorization()   // 只申请"使用期间"权限
    }

    func requestLocation() {
        manager.requestLocation()                 // 单次定位，不用持续更新
    }

    // delegate 回调统一转发，非主线程回调在视图侧自动切主线程
    nonisolated func locationManager(_ manager: CLLocationManager,
                                     didUpdateLocations locations: [CLLocation]) {
        location = locations.last
    }

    nonisolated func locationManager(_ manager: CLLocationManager,
                                     didFailWithError error: Error) {
        errorMessage = error.localizedDescription
    }
}
```

**Swift 6 严格并发注意**：delegate 回调是 `nonisolated`，把结果赋给 `@Observable` 属性时 Swift 6 会检查隔离域——属性默认主 actor 隔离，回调经 runtime 切回主线程后写入是安全的；若编译器报警，用 `MainActor.assumeIsolated { }` 包裹。

## 🛠️ 第二步：天气服务（纯函数网络层）

```swift
struct WeatherService: Sendable {
    func fetch(latitude: Double, longitude: Double) async throws -> WeatherSnapshot {
        var components = URLComponents(string: "https://api.example.com/v1/weather")!
        components.queryItems = [
            .init(name: "latitude", value: "\(latitude)"),
            .init(name: "longitude", value: "\(longitude)"),
        ]
        let (data, response) = try await URLSession.shared.data(from: components.url!)

        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        return try JSONDecoder().decode(WeatherSnapshot.self, from: data)
    }
}

struct WeatherSnapshot: Codable, Sendable {
    let temperatureC: Double
    let conditionCode: String            // SF Symbol 名，如 "cloud.sun"
}
```

## 🛠️ 第三步：视图模型串联三态

```swift
import SwiftData

@Observable
@MainActor                                   // UI 相关状态全部主线程
final class WeatherViewModel {
    enum State {
        case idle, loading
        case loaded(WeatherSnapshot)
        case failed(String)
    }

    private(set) var state: State = .idle
    private var task: Task<Void, Never>?

    func load(location: CLLocation?, service: WeatherService) {
        task?.cancel()                       // 重复触发先取消旧请求
        guard let location else {
            state = .failed("尚未获得定位权限")
            return
        }
        state = .loading
        task = Task {
            do {
                let snapshot = try await service.fetch(
                    latitude: location.coordinate.latitude,
                    longitude: location.coordinate.longitude
                )
                guard !Task.isCancelled else { return }   // 已取消就别碰状态
                state = .loaded(snapshot)
            } catch is CancellationError {
            } catch {
                state = .failed(error.localizedDescription)
            }
        }
    }
}
```

## 🛠️ 第四步：页面组装与缓存落库

```swift
struct WeatherView: View {
    @State private var manager = LocationManager()
    @State private var viewModel = WeatherViewModel()
    @Environment(\.modelContext) private var context
    @Query(sort: \City.updatedAt, order: .reverse) private var cachedCities: [City]

    private let service = WeatherService()

    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                switch viewModel.state {
                case .idle:
                    ContentUnavailableView("等待定位", systemImage: "location.slash")
                case .loading:
                    ProgressView("获取天气中…")
                case .loaded(let snapshot):
                    weatherCard(snapshot)                    // 成功卡片
                case .failed(let message):
                    retryView(message)                       // 失败 + 重试按钮
                }
                Spacer()
            }
            .padding()
            .navigationTitle("天气")
            .toolbar {
                Button("定位") { manager.requestLocation() }
            }
            .onChange(of: manager.location) { _, newLocation in
                guard let newLocation else { return }
                viewModel.load(location: newLocation, service: service)
            }
            .task { manager.requestPermission() }            // 首次进入申请权限
        }
    }

    private func weatherCard(_ snapshot: WeatherSnapshot) -> some View {
        VStack {
            Image(systemName: snapshot.conditionCode)
                .font(.system(size: 64))
            Text("\(Int(snapshot.temperatureC))°")
                .font(.system(size: 72, weight: .thin))
        }
        .onAppear { persist(snapshot) }                      // 成功后落库
    }

    private func persist(_ snapshot: WeatherSnapshot) {
        let city = cachedCities.first ?? City(name: "当前位置", temperature: 0)
        city.temperature = snapshot.temperatureC
        city.updatedAt = .now
        if city.modelContext == nil { context.insert(city) }
        try? context.save()                                  // 断网时 @Query 仍能读出缓存
    }
}
```

## ✅ 检查点

- [ ] 首次启动弹出权限弹窗，拒绝后进入 `failed` 态且给出指引
- [ ] 断网请求失败点重试可恢复；杀 App 重开能看到上次的缓存温度
- [ ] 快速连点定位按钮不会出现旧结果覆盖新结果（任务取消生效）

## ❌ 常见问题

**Q1: 真机上定位无反应？** Info.plist 必须配 `NSLocationWhenInUseUsageDescription`，缺失会直接崩溃；模拟器用 Features → Location 手动注入。

**Q2: `onChange` 新旧签名分不清？** iOS 17+ 两参数版 `{ old, new in }`，单参数旧版已废弃。

**Q3: 权限被永久拒绝怎么办？** 引导用户去设置页：`UIApplication.openSettingsURLString`。

## 🎯 进阶挑战

- [ ] 多城市管理：增删城市，每城市独立卡片与缓存
- [ ] 用 `TaskGroup` 并发拉取 5 个城市天气（见 [02-concurrency-optimization.md](../advanced-topics/performance/02-concurrency-optimization.md)）
- [ ] 接入 `CLLocationManager` 的显著位置变化，做"离家提醒"

## 相关文档

- 📄 [03-habit-tracker.md](./03-habit-tracker.md) — 下一篇：习惯追踪器（数据建模 + 图表）
- 📄 [03-ecosystem-integration.md](../frameworks/03-ecosystem-integration.md) — 本项目依赖的集成指南
- 📄 [03-concurrency-api.md](../reference/language-concepts/03-concurrency-api.md) — Task/取消语义字典
- 📄 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md) — 定位/网络报错速查
