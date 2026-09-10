# 实战项目三：习惯追踪器（数据建模 + 图表）

> **文档简介**: 构建一个习惯打卡应用：多对多数据建模、打卡统计聚合、用 SwiftUI Charts 绘制周趋势图，掌握"数据先想清楚再写 UI"的建模思路
>
> **目标读者**: 已完成两个入门项目、要练习数据建模与可视化的学习者
>
> **前置知识**: [projects/01-notes-app.md](./01-notes-app.md)（SwiftData CRUD）、[frameworks/02-swiftui-advanced.md](../frameworks/02-swiftui-advanced.md)（@Observable）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南（实战项目） |
| **难度** | ⭐⭐ |
| **标签** | `#SwiftData` `#数据建模` `#关系` `#Charts` `#聚合统计` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

最终效果：维护一组习惯（如"阅读 30 分钟"），每天可打卡，首页看今日待办，详情页看最近 7 天打卡柱状图与连续天数。

**建模先行——两个核心问题**：
1. "打卡"是独立实体还是习惯的属性？→ **独立实体**（一天可能多次、要按时间聚合）
2. "连续天数"算出来还是存起来？→ **算出来**（派生数据存了就得同步，必出 bug）

## 🛠️ 第一步：模型设计（一对多 + 反向关系）

```swift
import SwiftData

@Model
final class Habit {
    var name: String
    var icon: String                     // SF Symbol 名
    var createdAt: Date
    @Relationship(deleteRule: .cascade, inverse: \CheckIn.habit)
    var checkIns: [CheckIn] = []         // 一个习惯多次打卡；删习惯级联删打卡

    init(name: String, icon: String) {
        self.name = name
        self.icon = icon
        self.createdAt = .now
    }
}

@Model
final class CheckIn {
    var date: Date                       // 只保留年月日（时分秒归零，见下）
    var note: String?
    var habit: Habit?                    // 反向关系：从打卡找到习惯

    init(date: Date) {
        self.date = date.startOfDay      // 归一化到当天 00:00，比较才不出错
    }
}

extension Date { var startOfDay: Date { Calendar.current.startOfDay(for: self) } }
```

**建模要点**：
- `deleteRule: .cascade` 保证删习惯不留孤儿打卡记录
- 日期归一化到天，否则"今天打没打过"比较会因毫秒差失败

## 🛠️ 第二步：业务逻辑放模型扩展（不放视图）

```swift
extension Habit {
    /// 今天是否已打卡
    func isChecked(on day: Date = .now) -> Bool {
        checkIns.contains { $0.date == day.startOfDay }
    }

    /// 打卡 / 取消打卡（幂等切换）
    func toggleCheckIn(on day: Date = .now) {
        if isChecked(on: day) {
            checkIns.removeAll { $0.date == day.startOfDay }
        } else {
            checkIns.append(CheckIn(date: day))
        }
    }

    /// 最近 n 天的每日打卡数组（图表数据源）
    func dailyCounts(last days: Int) -> [(day: Date, done: Bool)] {
        return (0..<days).reversed().compactMap { offset in
            guard let day = Calendar.current.date(byAdding: .day, value: -offset, to: .now.startOfDay)
            else { return nil }
            return (day, isChecked(on: day))
        }
    }

    /// 连续打卡天数
    var streak: Int {
        var count = 0
        var day = Date.now.startOfDay
        // 今天没打也从昨天起算，避免"还没打"清零
        if !isChecked(on: day) {
            guard let yesterday = Calendar.current.date(byAdding: .day, value: -1, to: day)
            else { return 0 }
            day = yesterday
        }
        while isChecked(on: day) {
            count += 1
            guard let previous = Calendar.current.date(byAdding: .day, value: -1, to: day)
            else { break }
            day = previous
        }
        return count
    }
}
```

业务规则写在模型扩展里，视图只负责调用——这是**可测试性**的前提，测试方案见 [01-unit-testing.md](../testing/01-unit-testing.md)。

## 🛠️ 第三步：今日打卡列表

```swift
struct TodayView: View {
    @Query(sort: \Habit.createdAt) private var habits: [Habit]
    @Environment(\.modelContext) private var context

    var body: some View {
        List {
            ForEach(habits) { habit in
                HStack {
                    Image(systemName: habit.icon)
                        .frame(width: 32)
                    VStack(alignment: .leading) {
                        Text(habit.name)
                        Text("连续 \(habit.streak) 天")
                            .font(.caption)
                            .foregroundStyle(habit.streak > 0 ? .orange : .secondary)
                    }
                    Spacer()
                    CheckButton(habit: habit)      // 打卡按钮独立组件
                }
            }
            .onDelete { offsets in
                for index in offsets { context.delete(habits[index]) }
            }
        }
        .navigationTitle("今日")
        .overlay {
            if habits.isEmpty { ContentUnavailableView("添加第一个习惯", systemImage: "target") }
        }
    }
}

struct CheckButton: View {
    let habit: Habit

    var body: some View {
        Button {
            withAnimation(.snappy) { habit.toggleCheckIn() }   // 打卡带动画
        } label: {
            Image(systemName: habit.isChecked() ? "checkmark.circle.fill" : "circle")
                .font(.title2)
                .foregroundStyle(habit.isChecked() ? .green : .gray)
        }
        .buttonStyle(.plain)
    }
}
```

## 🛠️ 第四步：SwiftUI Charts 周趋势图

```swift
import Charts

struct WeeklyChart: View {
    let habit: Habit

    var body: some View {
        Chart(habit.dailyCounts(last: 7), id: \.day) { item in
            BarMark(
                x: .value("日期", item.day, unit: .day),    // 按天分桶
                y: .value("完成", item.done ? 1 : 0)
            )
            .foregroundStyle(item.done ? .green : .gray.opacity(0.25))
            .cornerRadius(4)
        }
        .chartYScale(domain: 0...1)
        .chartYAxis {                                       // Y 轴简化为是/否
            AxisMarks(values: [0, 1]) { value in
                AxisValueLabel {
                    if value.as(Int.self) == 1 { Text("完成") }
                }
            }
        }
        .frame(height: 160)
        .padding()
        .background(.ultraThinMaterial, in: .rect(cornerRadius: 12))
    }
}
```

## ✅ 检查点

- [ ] 打卡 → 取消 → 再打卡，`streak` 计算正确（今天没打卡不清零昨日连续）
- [ ] 删除习惯后 `checkIns` 无残留（级联生效，可查库验证）
- [ ] 周图表 7 根柱子与实际打卡记录一一对应

## ❌ 常见问题

**Q1: 图表数据是空的？** `dailyCounts` 返回元组数组，`Chart` 的 `id:` 必须写 `\.day`，元组不能自动 Identifiable。

**Q2: 想加"每周目标 5 次"？** 在 `Habit` 加 `weeklyGoal: Int` 字段，达标判断写在扩展方法里并补单元测试。

## 🎯 进阶挑战

- [ ] 月历视图：`Grid` 排 30 天打卡点阵
- [ ] 统计页：全部习惯完成率的 `LineMark` 折线趋势
- [ ] 用 `#Predicate` 把 `@Query` 改为只查今日需打卡的习惯

## 相关文档

- 📄 [04-production-ios-app.md](./04-production-ios-app.md) — 下一篇：生产级 iOS 应用
- 📄 [02-swiftdata-observability.md](../reference/framework-essentials/02-swiftdata-observability.md) — 关系与删除规则字典
- 📄 [01-unit-testing.md](../testing/01-unit-testing.md) — 给 streak/dailyCounts 写单元测试
- 📄 [01-swift-swiftui-cheatsheet.md](../reference/quick-references/01-swift-swiftui-cheatsheet.md) — 语法速查
