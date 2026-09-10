# 第一个完整项目 - 待办记账 App（SwiftUI + SwiftData）

> **文档简介**: 综合运用前七课知识，从零构建一个带持久化的"待办 + 记账"App：SwiftData 建模、列表交互、并发加载与统计页，是入门路径的毕业项目
>
> **目标读者**: 已完成 01-07 课、希望用一个完整项目串联知识点的学习者
>
> **前置知识**: [04-views-state.md](./04-views-state.md)、[06-navigation.md](./06-navigation.md)、[07-concurrency-async-await.md](./07-concurrency-async-await.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#实战项目` `#SwiftData` `#待办App` `#综合练习` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本项目后，你将能够：

- ✅ 定义 SwiftData 模型并配置 ModelContainer
- ✅ 用 @Query 驱动列表、用 @Model 实现增删改
- ✅ 独立评估：下一步该学什么（进阶路径的入口）

## 🏗️ 一、项目蓝图

**功能需求**：

1. 待办列表：新增/勾选完成/滑动删除，按是否完成分组
2. 记一笔支出：弹窗输入金额与分类，金额合计实时显示
3. 统计页：本月待办完成率 + 支出合计

新建项目（或复用 01 课的 SwiftNotes），建 5 个文件：`Models.swift`、`SwiftNotesApp.swift`、`TaskListView.swift`、`ExpenseSheet.swift`、`StatsView.swift`。

## 🔍 二、数据模型（SwiftData）

```swift
import SwiftData

@Model
final class TaskItem {
    var title: String
    var isDone = false
    var createdAt = Date.now

    init(title: String) { self.title = title }
}

@Model
final class Expense {
    var amount: Double
    var category: String
    var date = Date.now

    init(amount: Double, category: String) {
        self.amount = amount
        self.category = category
    }
}
```

`@Model` 宏让类获得持久化能力：属性自动映射为数据库列，对象变更自动保存（详见 [02-swiftdata-observability.md](../reference/framework-essentials/02-swiftdata-observability.md)）。

## 🔍 三、注入容器

```swift
@main
struct SwiftNotesApp: App {
    var body: some Scene {
        WindowGroup { MainTabView() }
            .modelContainer(for: [TaskItem.self, Expense.self])
    }
}
```

`.modelContainer(for:)` 做了三件事：创建数据库、注册模型、把 context 注入环境。所有子视图即可使用 `@Query` 与 `@Environment(\.modelContext)`。

## 🛠️ 四、待办列表页

```swift
import SwiftData
import SwiftUI

struct TaskListView: View {
    @Query(filter: #Predicate<TaskItem> { !$0.isDone }, sort: \TaskItem.createdAt, order: .reverse)
    private var activeTasks: [TaskItem]

    @Query(filter: #Predicate<TaskItem> { $0.isDone })
    private var doneTasks: [TaskItem]

    @Environment(\.modelContext) private var context
    @State private var newTitle = ""
    @State private var showAdd = false

    var body: some View {
        List {
            Section("进行中（\(activeTasks.count)）") {
                ForEach(activeTasks) { task in
                    TaskRow(task: task)
                }
                .onDelete(perform: delete)
            }

            Section("已完成") {
                ForEach(doneTasks) { task in
                    TaskRow(task: task)
                }
                .onDelete(perform: delete)
            }
        }
        .navigationTitle("待办")
        .toolbar {
            Button { showAdd = true } label: { Image(systemName: "plus") }
        }
        .alert("新建待办", isPresented: $showAdd) {
            TextField("做什么？", text: $newTitle)
            Button("添加") { add() }
            Button("取消", role: .cancel) {}
        }
    }

    private func add() {
        let title = newTitle.trimmingCharacters(in: .whitespaces)
        guard !title.isEmpty else { return }
        context.insert(TaskItem(title: title))   // 插入即持久化
        newTitle = ""
    }

    private func delete(at offsets: IndexSet) {
        for index in offsets { context.delete(activeTasks[index]) }
    }
}

struct TaskRow: View {
    @Bindable var task: TaskItem       // SwiftData 模型可直接双向绑定

    var body: some View {
        Toggle(isOn: $task.isDone) { Text(task.title).strikethrough(task.isDone) }
    }
}
```

关键点：`@Query` 是**响应式数据库查询**，数据库一变列表自动刷新；`#Predicate` 把 Swift 闭包编译为底层查询条件；`context.insert` 后无需手动 save（默认自动保存）。

## 🛠️ 五、记账弹窗与统计页

### 5.1 记账 Sheet

```swift
struct ExpenseSheet: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss

    @State private var amountText = ""
    @State private var category = "餐饮"
    private let categories = ["餐饮", "交通", "购物", "娱乐", "其他"]

    var body: some View {
        NavigationStack {
            Form {
                TextField("金额", text: $amountText)
                    .keyboardType(.decimalPad)
                Picker("分类", selection: $category) {
                    ForEach(categories, id: \.self) { Text($0) }
                }
            }
            .navigationTitle("记一笔")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("取消") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) { Button("保存") { save() } }
            }
        }
        .presentationDetents([.medium])
    }

    private func save() {
        guard let amount = Double(amountText), amount > 0 else { return }
        context.insert(Expense(amount: amount, category: category))
        dismiss()
    }
}
```

### 5.2 统计页（练习）

自己实现 `StatsView`：用两个不带参数的 `@Query` 分别取全部 `TaskItem` 与 `Expense`，在**计算属性**里完成统计——完成率 = 已完成数 ÷ 总数；本月支出用 `Calendar.current.isDate(_:equalTo:toGranularity:)` 过滤后求和；界面用 `Gauge`（完成率）与 `LabeledContent`（金额，`format: .currency(code: "CNY")`）各占一个 Section，`@Query` 不带参数即取全部数据。

## ✅ 最佳实践

- ✅ **推荐**：模型字段保持简单类型（String/Double/Date/Bool），复杂结构拆成关联模型
- ✅ **推荐**：查询过滤交给 `@Query(filter:)` / `#Predicate`，别把全表拉进内存再筛
- ❌ **避免**：把统计逻辑塞进 `body` 的闭包链里层层嵌套，抽成计算属性或 model 方法

## ❓ 常见问题

### Q1: `@Query` 报 "Query could not find a model container"？

`WindowGroup` 上没挂 `.modelContainer(for:)`，或挂在错误的 Scene 上。确认它在 App 的 `body` 里、`WindowGroup` 本身。

### Q2: Toggle 绑定模型的属性，修改没保存？

`@Model` 属性修改会自动保存，但前提是属性可写且视图用的是 `@Bindable`。检查 `TaskRow` 是否声明 `@Bindable var task: TaskItem`。

## 🎯 练习与实践

### 练习一：基础练习

- [ ] 完整跑通：新增待办 → 勾选完成 → 滑动删除 → 重启 App 数据仍在；记 3 笔支出并验证统计页合计
- [ ] 给 ExpenseSheet 加"金额为空或非法时保存按钮禁用"的逻辑

---

## 相关文档

- 📄 进阶路径入口：`frameworks/`、`projects/`（后续补充，规划见 [模块 README](../README.md)）
- 📄 [02-swiftdata-observability.md](../reference/framework-essentials/02-swiftdata-observability.md) — SwiftData 与 Observation 详解
- 📄 [02-troubleshooting.md](../reference/quick-references/02-troubleshooting.md) — 项目调试排错手册
