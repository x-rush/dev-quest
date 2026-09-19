# 集成测试任务指南 — 数据层与服务层联调

> **文档简介**: 在真实 SwiftData 容器与受控的服务边界之间做集成验证：模型关系、级联删除、容器迁移、服务与数据库的协作链路
>
> **目标读者**: 单元测试已就位、要验证"模块拼在一起还能正常工作"的中级学习者
>
> **前置知识**: [01-unit-testing.md](./01-unit-testing.md)（Swift Testing）、[frameworks/03-ecosystem-integration.md](../frameworks/03-ecosystem-integration.md)（SwiftData + URLSession 链路）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#集成测试` `#SwiftData` `#内存容器` `#Stub` `#数据迁移` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 本指南解决什么问题

单元测试分别验证小单元；集成测试验证它们拼在一起后的可观察结果：**关系对不对**（级联、反向引用）、**链路通不通**（受控服务响应 → 落库 → 查询）、**升级稳不稳**（schema 迁移）。本篇的网络部分使用 stub，不向真实 API 发请求；存储和查询使用真实 SwiftData 容器。

## 🛠️ 任务一：搭建内存容器测试基建

集成测试的第一原则：**真容器、真查询，但不落磁盘**。

```swift
import Testing
import SwiftData
@testable import HabitTracker

// 测试基建：每次测试一个全新的内存容器
@MainActor
struct IntegrationHarness {
    let container: ModelContainer
    let context: ModelContext

    init() throws {
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        container = try ModelContainer(
            for: Habit.self, CheckIn.self,
            configurations: config
        )
        context = ModelContext(container)      // 独立 context，测试间零共享
    }

    func save() throws {
        try context.save()
    }
}
```

## 🛠️ 任务二：验证关系与级联删除

```swift
@MainActor
@Suite("关系完整性")
struct RelationshipTests {

    @Test("删除习惯级联删除打卡记录")
    func cascadeDelete() throws {
        let harness = try IntegrationHarness()

        let habit = Habit(name: "阅读", icon: "book")
        habit.checkIns.append(CheckIn(date: .now))
        habit.checkIns.append(CheckIn(date: .now.startOfDay - 86_400))
        harness.context.insert(habit)
        try harness.save()

        harness.context.delete(habit)           // 删习惯
        try harness.save()

        // 集成断言：重新查库验证，而不是看内存对象
        let checkInCount = try harness.context.fetchCount(FetchDescriptor<CheckIn>())
        #expect(checkInCount == 0, "打卡记录应随习惯级联删除")
    }

    @Test("反向关系可从打卡找到习惯")
    func inverseNavigation() throws {
        let harness = try IntegrationHarness()

        let habit = Habit(name: "运动", icon: "figure.run")
        let checkIn = CheckIn(date: .now)
        habit.checkIns.append(checkIn)
        harness.context.insert(habit)
        try harness.save()

        // 从库中查打卡，反向拿到习惯
        let fetched = try harness.context.fetch(FetchDescriptor<CheckIn>())
        #expect(fetched.count == 1)
        #expect(fetched[0].habit?.name == "运动")
    }
}
```

关系声明语法见字典 [02-swiftdata-observability.md](../reference/framework-essentials/02-swiftdata-observability.md)。

## 🛠️ 任务三：服务 → 数据库 链路测试（Stub 网络）

网络桩（stub）返回**结构真实的合成数据**，其余链路全部走真实现：

```swift
struct StubWeatherService: WeatherServicing {
    let snapshot: WeatherSnapshot

    func fetch(latitude: Double, longitude: Double) async throws -> WeatherSnapshot {
        snapshot                                 // 固定返回，不发真实请求
    }
}

@MainActor
@Suite("天气缓存链路")
struct WeatherCacheTests {

    @Test("网络结果落库后可经 @Query 语义查询")
    func persistThenQuery() async throws {
        let harness = try IntegrationHarness()
        let stub = StubWeatherService(
            snapshot: WeatherSnapshot(temperatureC: 21, conditionCode: "sun.max")
        )

        // 模拟"视图模型拿到数据并落库"的真实流程
        let snapshot = try await stub.fetch(latitude: 39.9, longitude: 116.4)
        harness.context.insert(City(name: "Beijing", temperature: snapshot.temperatureC))
        try harness.save()

        // 用 #Predicate 查库（与 @Query 同一查询语义）
        let predicate = #Predicate<City> { $0.name == "Beijing" }
        let cities = try harness.context.fetch(FetchDescriptor(predicate: predicate))

        #expect(cities.count == 1)
        #expect(cities[0].temperature == 21)
    }

    @Test("重复落库不产生重复城市（更新而非新增）")
    func upsertSemantics() async throws {
        let harness = try IntegrationHarness()
        let stub = StubWeatherService(
            snapshot: WeatherSnapshot(temperatureC: 25, conditionCode: "cloud.sun")
        )

        let first = try await stub.fetch(latitude: 0, longitude: 0)
        harness.context.insert(City(name: "Beijing", temperature: first.temperatureC))
        try harness.save()

        let second = try await stub.fetch(latitude: 0, longitude: 0)
        if let existing = try harness.context.fetch(FetchDescriptor<City>()).first {
            existing.temperature = second.temperatureC      // 已有则更新
        }
        try harness.save()

        #expect(try harness.context.fetchCount(FetchDescriptor<City>()) == 1)
    }
}
```

## 🛠️ 任务四：Schema 迁移测试

模型升级后，旧库能否打开必须通过**磁盘夹具**验证；只改当前模型的类名或写一条 `#expect(true)` 都不能证明迁移可用。SwiftData 的版本化 schema 与迁移 API 会随 Xcode / SDK 工具链变化，本节不给出会伪装成可直接运行的通用代码，而是给出每个项目都应实现的验收步骤：

1. 使用上一版的 `VersionedSchema` 在每条测试独有的临时目录创建持久化存储，并写入有代表性的旧数据。夹具至少包含普通字段、需要保留的关系和边界值；不要用“改名后的当前模型”冒充旧 schema。
2. 关闭旧 `ModelContainer`，再用当前 schema 及项目实际采用的迁移配置打开**同一个存储位置**。为避免缓存掩盖问题，重新创建容器和 `ModelContext` 后再读取。
3. 断言旧记录的标识与关键值仍在；新增字段取得预期默认值；关系、排序和基数没有被改变。随后保存一次、再次重开存储，确认迁移后的数据可持续读取。
4. 对不兼容变更（例如字段语义或类型变化、删除或拆分字段）先写清数据转换规则，再在独立夹具中演练对应的迁移计划。若无法安全转换，应让升级停止并保留可恢复的旧数据，而不是静默丢弃字段。
5. 在 `defer` 中清理临时目录；测试失败时保留或导出夹具路径，便于复现并检查迁移日志。

“轻量迁移”取决于实际 schema 演进与当前 SDK 支持，不能按“加字段就一定自动、删字段就一定失败”的口诀判断。每次模型变更都要用真实旧版夹具跑一次升级验收；迁移报错的定位路径见 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md)。

## ✅ 运行验收

将示例中的模型名和 scheme 替换为项目实际名称后，在 macOS/Xcode 环境运行测试：

```bash
xcodebuild test -scheme <scheme> -destination '<destination>'
```

通过的最低证据是：级联删除后重新查询为零；stub 响应只经受控接口进入数据库且不产生外网请求；重复写入遵循项目定义的唯一键 / 更新规则；旧版磁盘夹具可迁移、重开后数据仍正确。仓库没有可构建的 Swift/Xcode 示例工程，因此本仓库未执行上述原生测试命令；提交项目时应保存 CI 的测试输出和使用的 Xcode 版本。

## ✅ 最佳实践

持久化集成测试应从新的查询上下文读取结果，必要时重建存储实例，避免只验证内存里的对象已经变化。模拟 API 使用能反映真实契约的合成数据，并包含缺字段、错误状态和延迟。

隔离测试容器或明确清理数据，保证每条用例独立。对一次失败保存检查没有留下半条记录，再对重启后的读取作断言，才能证明协作链满足要求。

## ❌ 避免陷阱

- ❌ 集成测试里连真实 API——被测的是"拼装"，不是远端服务本身
- ❌ 忘记 `save()` 就断言查询结果——未落库的变更 `fetch` 可能查不到
- ❌ 主线程外的 context 混用——每个 `ModelContext` 只在创建它的隔离域使用

## ❓ 常见问题

**Q1: `fetchCount` 和 `fetch().count` 有何区别？** 前者只在数据库层计数不加载对象，大数据量下性能差异显著。

**Q2: 测试里 `@Query` 属性包装器不可用？** `@Query` 是视图专属；测试中用 `FetchDescriptor` + `fetch`，语义等价。

**Q3: 内存容器需要 save 吗？** 需要，`save()` 触发的是上下文提交，与是否落盘无关。

## 🎯 练习

- [ ] 为习惯追踪器写"删习惯 → 打卡数为 0"的级联测试
- [ ] 把天气缓存链路测试接入 CI，断言重复落库不翻倍
- [ ] 给 `Habit` 加 `weeklyGoal` 字段，写一条轻量迁移测试

## 相关文档

- 📄 [01-unit-testing.md](./01-unit-testing.md) — 单元测试（本篇的上游）
- 📄 [02-ui-testing.md](./02-ui-testing.md) — UI 层旅程测试（本篇的下游）
- 📄 [03-ecosystem-integration.md](../frameworks/03-ecosystem-integration.md) — 被测数据链路的搭建指南
- 📄 [03-concurrency-api.md](../reference/language-concepts/03-concurrency-api.md) — 并发测试涉及的 API 字典


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
