# 单元测试任务指南 — Swift Testing（#expect）

> **文档简介**: 用 Apple 新一代 Swift Testing 框架（`@Test`、`#expect`、参数化）为核心业务逻辑编写单元测试，告别旧 XCTest 的样板代码
>
> **目标读者**: 已能写出带业务逻辑的模型层、要为它们建立测试保障的中级学习者
>
> **前置知识**: [projects/03-habit-tracker.md](../projects/03-habit-tracker.md)（有可测的业务扩展）、[05-protocols-generics.md](../reference/language-concepts/05-protocols-generics.md)（协议用于 Mock）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#SwiftTesting` `#expect` `#参数化` `#异步测试` `#单元测试` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 本指南解决什么问题

Xcode 26.x 内置 Swift Testing（`import Testing`），与 XCTest 并存但**新代码首选 Swift Testing**：宏驱动、无继承、参数化一行搞定。本指南以习惯追踪器的业务扩展为例，建立"哪些测、怎么测、测到什么程度"的操作规程。

## 🛠️ 任务一：第一个 @Test

新建测试 Target 时选择 **Swift Testing** 框架。测试文件不需要类，函数即可：

```swift
import Testing
@testable import HabitTracker          // @testable 访问内部符号

struct HabitLogicTests {

    @Test("连续打卡天数计算")            // 中文描述直接写这里
    func streakWithConsecutiveDays() {
        // arrange：构造 3 天连续打卡
        let habit = Habit(name: "阅读", icon: "book")
        let calendar = Calendar.current
        for offset in 0..<3 {
            let day = calendar.date(byAdding: .day, value: -offset, to: .now)!
            habit.checkIns.append(CheckIn(date: day))
        }

        // act & assert：#expect 替代 XCTAssertTrue
        #expect(habit.streak == 3)
    }

    @Test("今天未打卡不清零昨日连续")
    func streakNotBrokenByToday() {
        let habit = Habit(name: "运动", icon: "figure.run")
        let yesterday = Calendar.current.date(byAdding: .day, value: -1, to: .now)!
        habit.checkIns.append(CheckIn(date: yesterday))

        #expect(habit.streak == 1)        // 今天还没打，连续不应归零
    }
}
```

**断言速查**：`#expect(条件)` 通用断言，失败时自动打印表达式两侧值；`#require(可选值)` 解包失败即中止本测试（抛错风格）。

## 🛠️ 任务二：参数化（一个测试跑多组数据）

```swift
@Test("打卡切换幂等", arguments: [
    (true, false),      // 已打卡 → 取消
    (false, true),      // 未打卡 → 打上
])
func toggleIsIdempotent(initial: Bool, expectedAfterToggle: Bool) {
    let habit = Habit(name: "喝水", icon: "drop")
    if initial {
        habit.checkIns.append(CheckIn(date: .now))
    }

    habit.toggleCheckIn()

    #expect(habit.isChecked() == expectedAfterToggle)
}
```

一组 `arguments` 生成 N 个独立测试用例，失败时精确到具体参数——这是 Swift Testing 相对 XCTest 的最大效率提升。

## 🛠️ 任务三：异步与并发测试

```swift
@Test("天气服务返回有效快照")
func weatherFetch() async throws {
    let service = LiveWeatherService()

    let snapshot = try await service.fetch(latitude: 39.9, longitude: 116.4)

    #expect(snapshot.temperatureC > -60 && snapshot.temperatureC < 60)
    #expect(snapshot.fetchedAt <= .now)
}

@Test("取消的任务不会改写状态")
func cancelledTaskDoesNotMutateState() async throws {
    let viewModel = WeatherViewModel()

    let task = Task { viewModel.load(location: nil, service: LiveWeatherService()) }
    task.cancel()
    _ = try? await task.value

    #expect(viewModel.state != .loading)   // 取消后不应停留在 loading
}
```

Swift Testing 测试函数**运行在并发安全的沙箱中**：默认每个测试独立并行执行，不存在 XCTest 类级的共享状态污染；需要串行时用 `@Suite(.serialized)`。

## 🛠️ 任务四：用协议 Mock 隔离依赖

```swift
struct MockWeatherService: WeatherServicing {
    var result: Result<WeatherSnapshot, Error>

    func fetch(latitude: Double, longitude: Double) async throws -> WeatherSnapshot {
        try result.get()                   // 返回预设结果，不发真实网络请求
    }
}

@Test("网络失败时视图模型进入 failed 态")
func loadFailureSetsFailedState() async {
    let mock = MockWeatherService(result: .failure(URLError(.notConnectedToInternet)))
    let viewModel = WeatherViewModel()

    viewModel.load(location: CLLocation(latitude: 1, longitude: 1), service: mock)

    // 等待状态流转（简单轮询；正式项目用 AsyncStream 等待）
    for _ in 0..<10 where viewModel.state == .loading {
        try? await Task.sleep(for: .milliseconds(50))
    }
    guard case .failed = viewModel.state else {
        Issue.record("预期 failed 态，实际 \(viewModel.state)")
        return
    }
}
```

协议定义见 [04-production-ios-app.md](../projects/04-production-ios-app.md) 第二步。

## ✅ 最佳实践

测试名称描述条件与结果，例如“连续记录中断后重新从一开始”，比“testModel”更能解释失败。用独立数据验证业务规则，再覆盖模型的成功、失败与重复触发状态。

对时间、随机和外部存储提供可控依赖，让测试换序或单独运行仍然成立。不要只断言函数被调用过：错误返回后数据是否保持原状，同样属于行为。

## ❌ 避免陷阱

- ❌ 测试里发真实网络请求——慢、不稳定、依赖外网；一律 Mock
- ❌ 测试 `SwiftData` 时用磁盘库——用 `isStoredInMemoryOnly: true` 的内存容器
- ❌ 断言只写 `#expect(true)` 占位——宁可不写，假绿比没测更危险

## ❓ 常见问题

**Q1: Swift Testing 和 XCTest 能共存吗？** 能，同一 Target 混用完全合法，逐步迁移即可。

**Q2: `@Observable` 模型能直接测吗？** 能，Observation 不影响纯逻辑测试；涉及视图刷新的验证交给 Preview 与 UI 测试。

**Q3: 测试跑得慢怎么办？** 先并行化（默认已并行），再查真实 I/O 与固定 sleep，改为等待条件满足。

## 🎯 练习

- [ ] 给 `streak` 补边界测试：跨月第一天、跨年、空打卡记录
- [ ] 把天气服务测试改为 Mock，覆盖成功 / 失败 / 取消三条路径
- [ ] 用 `#require` 重构所有 `#expect(x != nil) && #expect(x!.y)` 写法

## 相关文档

- 📄 [02-ui-testing.md](./02-ui-testing.md) — 下一篇：XCUITest 界面测试
- 📄 [05-protocols-generics.md](../reference/language-concepts/05-protocols-generics.md) — 协议与泛型字典（Mock 的语法基础）
- 📄 [03-habit-tracker.md](../projects/03-habit-tracker.md) — 被测业务逻辑出处
- 📄 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md) — 测试相关报错速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
