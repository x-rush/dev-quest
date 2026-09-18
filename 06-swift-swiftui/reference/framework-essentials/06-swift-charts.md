# SwiftUI Charts 数据可视化速查

> **文档简介**: Swift Charts 框架的条目式参考：Chart 容器与数据供给、四大基础 Mark、坐标轴定制、系列分组与图例，示例贴合习惯追踪场景
>
> **目标读者**: 需要查图表 API 细节或把数据画出来的学习者
>
> **前置知识**: [basics/04-views-state.md](../../basics/04-views-state.md)（视图与数据流）；实战见 [projects/03-habit-tracker.md](../../projects/03-habit-tracker.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#SwiftUI` `#Charts` `#可视化` `#iOS16+` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. Chart 容器与数据供给

**定义**: `Chart` 是声明式图表容器（`import Charts`，iOS 16+）。你描述"数据 → Mark"的映射，框架负责布局、刻度与图例。

```swift
import Charts

// 方式一：数据符合 Identifiable，直接闭包映射
Chart(dailyRecords) { record in
    BarMark(
        x: .value("日期", record.day, unit: .day),
        y: .value("完成", record.done ? 1 : 0)
    )
}

// 方式二：元组/非 Identifiable 数据，必须显式给 id（⚠️ 最常见坑）
Chart(habit.dailyCounts(last: 7), id: \.day) { item in
    BarMark(
        x: .value("日期", item.day, unit: .day),
        y: .value("完成", item.done ? 1 : 0)
    )
}

// 方式三：同一 Chart 内画多个系列（如柱 + 目标线）
Chart {
    ForEach(weekRecords, id: \.day) { item in
        BarMark(x: .value("日期", item.day, unit: .day),
                y: .value("次数", item.count))
    }
    RuleMark(y: .value("每日目标", 5))
        .foregroundStyle(.orange)
}
```

要点：

- `.value("标签", 值)` 构造 `PlottableValue`：字符串只是无障碍/图例描述，**真正决定标度的是值的类型**——`String` 走类别轴、`Date` 走时间轴、数值走数字轴
- `Date` 值可带 `unit:`（`.day` / `.hour` / `.month` …）按时间单位分桶；不写 unit 则按连续时间点处理
- 可绘图类型须符合 `Plottable`（常用如 Double、Int、String、Date；其他类型需检查当前 SDK 的一致性或转换后绘制）

## 2. 四大基础 Mark

| Mark | 用途 | 典型写法 |
|------|------|----------|
| `BarMark` | 柱状/条形（类别、频率） | `BarMark(x: .value("日", day, unit: .day), y: .value("次数", n))` |
| `LineMark` | 折线（趋势） | `LineMark(x: .value("日", day), y: .value("完成率", rate))` |
| `PointMark` | 散点（离散观测） | `PointMark(x: .value("日", day), y: .value("时长", mins))` |
| `RuleMark` | 参考线（阈值、均值） | `RuleMark(y: .value("目标", 5))` |

补充：`AreaMark`（面积）、`RectangleMark`（热力格）、`SectorMark`（饼图，iOS 17+）同属一族，用法一致。

**Mark 修饰**（挂在 Mark 实例上，不是 View 修饰符）：

```swift
BarMark(x: .value("日期", item.day, unit: .day),
        y: .value("完成", item.done ? 1 : 0))
    .foregroundStyle(item.done ? .green : .gray.opacity(0.25))
    .cornerRadius(4)

LineMark(x: .value("日期", r.day), y: .value("完成率", r.rate))
    .lineStyle(StrokeStyle(lineWidth: 2, dash: [5, 3]))
    .foregroundStyle(.orange)

RuleMark(y: .value("目标", 5))
    .annotation(position: .top) { Text("每日目标").font(.caption) }
```

## 3. 坐标轴与标度定制

```swift
Chart(data, id: \.day) { item in
    BarMark(x: .value("日期", item.day, unit: .day),
            y: .value("完成", item.done ? 1 : 0))
}
.chartYScale(domain: 0...1)                  // 固定标度范围（布尔打卡图常用）
.chartXScale(domain: weekStart...weekEnd)    // 固定 X 范围，7 根柱不漂移
.chartXAxis {
    AxisMarks(values: .stride(by: .day)) { _ in
        AxisGridLine()
        AxisValueLabel(format: .dateTime.weekday(.abbreviated))  // 周一/周二…
    }
}
.chartYAxis {
    AxisMarks(values: [0, 1]) { value in
        AxisValueLabel {
            if value.as(Int.self) == 1 { Text("完成") } else { Text("") }
        }
    }
}
```

| 修饰符 | 作用 |
|--------|------|
| `.chartXAxis { }` / `.chartYAxis { }` | 完全接管该轴：`AxisMarks` 内组合 `AxisGridLine` / `AxisTick` / `AxisValueLabel` |
| `.chartXAxis(.hidden)` / `.chartYAxis(.hidden)` | 隐藏整根轴 |
| `.chartYScale(domain:)` / `.chartXScale(domain:)` | 锁定标度范围（打卡图 `0...1`、评分 `0...5`） |
| `AxisMarks(values:)` | 接受数组、区间或 `.stride(by: .day)` 步进 |

## 4. 系列分组与图例

```swift
// 按"习惯名"自动分组、自动配色、自动出图例
Chart(checkIns, id: \.id) { entry in
    BarMark(
        x: .value("日期", entry.day, unit: .day),
        y: .value("次数", entry.count),
        width: 12
    )
    .foregroundStyle(by: .value("习惯", entry.habitName))
}
.chartLegend(position: .bottom)
// .chartLegend(.hidden)  // 多余图例关掉
```

| 修饰符 | 分组维度 |
|--------|----------|
| `.foregroundStyle(by: .value("系列", 值))` | 按值自动配色 + 图例 |
| `.symbol(by: .value("系列", 值))` | 散点形状分组 |
| `.lineStyle(by: .value("系列", 值))` | 线型分组 |

多个系列的通用做法：**一个 `Chart` 里放多个 `ForEach`**（每个系列一种 Mark/样式），需要共享 x 标度时优先用 `foregroundStyle(by:)` 让框架统一坐标。

## 5. 习惯追踪场景组合示例

```swift
// 周 7 天完成柱状图（对应 projects/03-habit-tracker.md 的 WeeklyChart）
struct WeeklyChart: View {
    let habit: Habit

    var body: some View {
        Chart(habit.dailyCounts(last: 7), id: \.day) { item in
            BarMark(
                x: .value("日期", item.day, unit: .day),
                y: .value("完成", item.done ? 1 : 0)
            )
            .foregroundStyle(item.done ? .green : .gray.opacity(0.25))
        }
        .chartYScale(domain: 0...1)
        .chartYAxis(.hidden)                       // 隐藏轴后仍需提供文本/无障碍状态，不能只靠颜色
        .chartXAxis {
            AxisMarks(values: .stride(by: .day)) { _ in
                AxisValueLabel(format: .dateTime.weekday(.narrow))
            }
        }
        .frame(height: 160)
    }
}
```

## ⚠️ 高频陷阱速查

- **元组数据不给 `id:`**：`Chart(habit.dailyCounts(...))` 直接传元组数组编译报错——元组不满足 `Identifiable`，必须 `id: \.day`
- **忘写 `unit: .day`**：`Date` 不带 unit 会按连续时间标度布点，7 天打卡变成长短不一的散柱
- **值类型不可绘图**：`y: .value("完成", item.done)`（Bool 不是 `Plottable`）会编译失败——先映射成 `1/0` 或 `Double`
- **把 Mark 修饰写在 Chart 容器上**：Mark 的 cornerRadius/lineStyle 调整柱与线；容器上同名 View 修饰可能只改变整体外观，并非修改各个 Mark
- **图例莫名出现**：用了 `foregroundStyle(by:)` 就自动出图例；单系列不需要时 `.chartLegend(.hidden)`

## 相关文档

- 📄 [03-habit-tracker.md](../../projects/03-habit-tracker.md) — 周趋势图实战与数据聚合
- 📄 [02-swiftdata-observability.md](./02-swiftdata-observability.md) — 图表数据来源（@Query 与关系）
- 📄 [01-swiftui-essentials.md](./01-swiftui-essentials.md) — 视图与修饰符总表

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，Charts 概念完整解释以此处为单一事实来源*


<!-- full-library-explanation -->
## 先定义统计口径，再画图

同一天两次打卡究竟算 1 天完成还是 2 次事件，要在聚合阶段决定。Chart 的 unit: .day 表示时间区间语义，不会替你完成任意去重与业务聚合。先把数据按指定 Calendar/时区归到日桶，再生成完整七天序列，区分“记录为零”与“数据缺失”。

练习：准备周一 2 次、周二 0 次、周三缺数据三种情况。为图旁边提供文本列表，明确显示 2、0、未知；不要把未知转换为 0 后声称周完成率降低。日目标参考线使用“每天目标”名称，周目标需画在周累计图上，避免单位混用。

折线数据先按时间排序；同一日期多系列使用稳定的系列标识。柱状图通常从零起，截断坐标轴应明确标注。验收包含大字体、VoiceOver、色觉差异以及空数据，颜色不能是表达完成状态的唯一渠道。本页前面的 habit/data 等是项目集成片段，需配套模型，不是独立可运行文件。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
