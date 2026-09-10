# SwiftUI 应用架构深度解析 — 从 MV 到 TCA 思想

> **文档简介**: 解释 SwiftUI 时代架构为何变"薄"：MV（Model-View）为什么够用、ViewModel 何时仍有价值、TCA 的单相数据流思想带来什么，帮助你按项目规模选型
>
> **目标读者**: 已写过多个完整应用、要为团队或长期项目做架构决策的中高级学习者
>
> **前置知识**: [basics/04-views-state.md](../../basics/04-views-state.md)（数据流基础）、[frameworks/02-swiftui-advanced.md](../../frameworks/02-swiftui-advanced.md)（@Observable 与环境）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#架构` `#MV` `#MVVM` `#TCA` `#单向数据流` |
| **更新日期** | `2026年9月` |

## 🔍 一、为什么 SwiftUI 让架构变薄了

理解架构选型，先理解 SwiftUI 吸收了哪些原本由架构层承担的职责：

| 传统痛点 | SwiftUI 的内置答案 | 架构层还剩什么 |
|----------|-------------------|---------------|
| 视图与状态同步 | `@State`/`@Observable` 声明式绑定 | 状态放哪、谁拥有 |
| 依赖注入 | `Environment` 原生支持 | 注入什么粒度的依赖 |
| 列表 diff | `List`/`ForEach` 按 id 自动 diff | 数据 id 的稳定性 |
| 导航栈管理 | `NavigationStack(path:)` 值驱动 | 路由值的设计 |

**结论**：SwiftUI 中"架构问题"收缩为两个纯粹问题——**状态所有权**与**副作用边界**。一切模式分歧都源于这两点的不同答案。

## 🔍 二、MV（Model-View）：SwiftUI 的默认架构

### 2.1 形态与代码

模型层 + 视图层，无中间层。`@Observable` 模型直接被视图观察：

```swift
@Observable
final class HabitListModel {
    private let store: HabitStoring              // 副作用收敛到模型内
    private(set) var habits: [Habit] = []

    init(store: HabitStoring) {
        self.store = store
        habits = store.fetchAll()
    }

    func toggle(_ habit: Habit) {                // 唯一对外动作：意图方法
        store.toggle(habit)
        habits = store.fetchAll()                // 或依赖 SwiftData 自动刷新
    }
}

struct HabitListView: View {
    @State private var model: HabitListModel     // 视图持有模型

    var body: some View {
        List(model.habits) { habit in
            Text(habit.name)
        }
    }
}
```

### 2.2 为什么对小中型项目"够"

- 数据流路径最短：UI 事件 → 模型方法 → 属性变化 → UI 刷新，**没有转发层**
- SwiftData `@Query` 本身就是"模型直连视图"，再包一层 ViewModel 纯属重复
- 可测试性由协议抽象保证（测试 `HabitListModel` 而非视图），不需要 VM 层才能测

### 2.3 MV 什么时候开始不够用

出现以下信号之一，就该引入中间层：
- 一个页面要**编排多个服务**（网络 + 缓存 + 分析上报），模型层开始臃肿
- 状态变化有**跨页面时序依赖**（A 页提交后 B 页必须回滚草稿）
- 需要**可重放的调试**（状态变化历史、时间旅行）

## 🔍 三、MVVM：中间层的正确定位

MVVM 在 SwiftUI 中**不再是必需品，而是工具**——只有当 ViewModel 承担"编排"职责时才值得引入：

```swift
@MainActor
@Observable
final class WeatherViewModel {
    enum Phase { case idle, loading, loaded(WeatherSnapshot), failed(AppError) }
    private(set) var phase: Phase = .idle

    private let weather: WeatherServicing        // 依赖全部经构造器注入
    private let cache: CacheStoring

    init(weather: WeatherServicing, cache: CacheStoring) {
        self.weather = weather
        self.cache = cache
    }

    func load(location: CLLocation) async {
        phase = .loading
        do {
            let snapshot = try await weather.fetch(
                latitude: location.coordinate.latitude,
                longitude: location.coordinate.longitude
            )
            cache.store(snapshot)
            phase = .loaded(snapshot)
        } catch let error as AppError {
            phase = .failed(error)
        } catch {
            phase = .failed(.offline)
        }
    }
}
```

**VM 的三条纪律**（违反任何一条，说明这个 VM 是多余的）：
1. 不 import SwiftUI（可与 Widget/macOS 共用）
2. 只暴露**状态 + 意图方法**，不暴露服务句柄
3. 所有依赖可注入，测试不需要网络与磁盘

MV vs MVVM 的判定一句话：**逻辑服务多个视图 → 提取 VM/模型类；逻辑只服务一个视图 → 就写在视图的扩展里**。

## 🔍 四、TCA 思想：把"一切皆消息"推到极致

The Composable Architecture（TCA）不只是一个库，更是一种可借鉴的思想——**单向数据流的完全体**：

```swift
// TCA 的核心心智模型（伪代码，非完整 Reducer API）
// State：页面的全部可能状态，一个值说完
struct FeatureState: Equatable {
    var items: [Habit] = []
    var isLoading = false
}

// Action：页面上可能发生的一切，一个枚举说完
enum FeatureAction {
    case onAppear                     // 生命周期事件也是 Action
    case itemsResponse(Result<[Habit], AppError>)
    case toggleTapped(Habit.ID)       // 用户意图
}

// Reducer：唯一的状态变更函数
func reducer(state: inout FeatureState, action: FeatureAction) -> Effect<FeatureAction> {
    switch action {
    case .onAppear:
        state.isLoading = true
        return .run { send in                       // 副作用隔离在 Effect 中
            let result = await Result { try await loadItems() }
            await send(.itemsResponse(result))
        }
    case .itemsResponse(.success(let items)):
        state.isLoading = false
        state.items = items
        return .none
    case .itemsResponse(.failure):
        state.isLoading = false
        return .none
    case .toggleTapped(let id):
        state.items[id: id]?.toggle()
        return .none
    }
}
```

### TCA 思想的三个可迁移要点（不用 TCA 也能用）

1. **状态一枚举**：用 `Phase` 枚举替代零散的 `isLoading`/`error`/`data` 三布尔，非法状态不可表达
2. **副作用不藏在 setter 里**：所有异步工作显式发出，可测试（断言收到的 Action 序列）
3. **可组合**：子 Feature 只暴露动作接口，父 Feature 不了解其内部

### TCA 的代价

- 样板代码量显著高于 MV/MVVM，个人小项目性价比低
- 学习曲线陡：Effect、依赖容器、TestStore 是一套新范式
- 与 SwiftData `@Query` 的"自动刷新"模型存在理念冲突（TCA 要求显式数据流），需要额外的桥接层

## 🔍 五、选型决策

```text
项目规模与状态复杂度
├── 原型 / 小工具（<10 页面，状态简单）
│     → MV + SwiftData @Query（SwiftUI 默认姿势）
├── 中型产品（多页面共享状态、多服务编排）
│     → MV 骨架 + 关键页面 MVVM + 协议注入
└── 大型/团队项目（强可测性、可重放调试、功能组合）
      → TCA 或"TCA 思想的手写简化版"
```

**演进路径**：从 MV 起步 → 出现编排需求时局部引入 VM → 状态复杂到需要重放调试时再评估 TCA。反向重构（TCA 减层到 MVVM）痛苦得多，所以**宁欠勿过**。

## ✅ 设计原则小结

- ✅ 单向数据流：状态单向向下传递，事件单向向上汇总，任何时刻数据流向可预测
- ✅ 状态所有权唯一：每个状态有且只有一个所有者（@State / @Observable 模型 / @Query）
- ✅ 副作用边界清晰：网络、磁盘、时钟只出现在模型/VM/Effect 层，视图是纯函数

## ❌ 常见误区

- ❌ "MVVM 是 SwiftUI 的标准架构"——SwiftUI 官方范式就是 MV，VM 是应对复杂度的可选项
- ❌ 把 ViewModel 当"大杂烩"——混入 UI 格式化、服务调用、持久化三种职责的 VM 必然失控
- ❌ 全局单例当依赖容器——编译期不可见、测试难替换，用构造器注入 + Environment

## 🎯 实践检验

- [ ] 把习惯追踪器的 TodayView 重构为"Phase 枚举状态机"版，观察非法状态是否被类型消灭
- [ ] 给 `HabitListModel` 写不依赖 SwiftData 真库的测试，验证协议注入的边界
- [ ] 选一页用 TCA 思想手写 State/Action/Reducer 三件套（不引入库），评估样板成本

## 相关文档

- 📄 [04-production-ios-app.md](../../projects/04-production-ios-app.md) — 本文思想的落地实施
- 📄 [04-swiftui-state-api.md](../../reference/language-concepts/04-swiftui-state-api.md) — 状态所有权工具全表
- 📄 [02-swiftdata-observability.md](../../reference/framework-essentials/02-swiftdata-observability.md) — @Query 与架构的交互细节
- 📄 [02-concurrency-optimization.md](../performance/02-concurrency-optimization.md) — 架构层的并发边界设计
