# 第一个完整项目：可保存、可恢复的待办与记账 App

先完成一条记录的新增、保存、重启读取，再增加分组和统计。学习重点是分清四件事：表单里的草稿、内存模型的变化、数据库保存成功、重新启动后读取到的数据。它们发生在不同的时刻。

前置：[视图与状态](./04-views-state.md)、[导航](./06-navigation.md)、Swift 的可选值、数组和错误处理。项目使用 SwiftUI 与 SwiftData，需要 macOS、Xcode 和 iOS 17 或更高的运行目标；Swift Linux 命令行只能验证纯 Swift 逻辑，不能构建此 UI。本文没有设备构建通过记录，下面的设备验收表须在 Xcode 工程执行后填写。

## 1. 先确定可交付范围

第一阶段只有待办：新增、完成、删除、重启仍能读取。第二阶段增加人民币支出：金额按整数“分”保存，显示时转为元。第三阶段增加本月统计与空数据状态。暂不增加云同步、通知、账户和数据库迁移，它们分别引入独立的失败条件。

| 输入或操作 | 应观察到的结果 |
|---|---|
| 空白标题 | 拒绝添加，已有记录不变 |
| 添加 A、B，完成 B，删除完成组的 B | A 保留，B 删除；不能用完成组的下标删除进行中数组 |
| 输入 `0.10` 与 `0.20` | 分别保存为 10、20，合计显示 0.30 元 |
| 输入 `12abc`、`1.234`、`-1`、`0` | 明确拒绝；键盘类型不是输入验证 |
| 保存失败 | 保留表单，显示错误；不得先关闭表单再报告成功 |
| 删除、完成后关闭并重新启动 | 查询结果与最后一次成功保存一致 |

## 2. 创建空工程

用 Xcode 创建 iOS App，Interface 选择 SwiftUI，部署目标设为 iOS 17 或更高。删除模板自带的 App 声明及示例模型文件，避免两个 `@main`；新建 `LedgerApp.swift`，放入下列完整应用代码。它不需要第三方依赖。

金额解析器只接受 ASCII 数字和小数点，约定单笔最高 999999.99 元；这是本练习的输入契约。面向不同地区发布时，应另外设计本地化货币输入和舍入规则，不能直接把逗号删掉再解析。

```swift
import Foundation
import SwiftUI
import SwiftData

func parseCents(_ raw: String) -> Int? {
    let text = raw.trimmingCharacters(in: .whitespacesAndNewlines)
    let parts = text.split(separator: ".", omittingEmptySubsequences: false)
    guard (1...2).contains(parts.count),
          (1...6).contains(parts[0].count),
          parts[0].utf8.allSatisfy({ $0 >= 48 && $0 <= 57 }),
          let whole = Int(parts[0]) else { return nil }
    var fraction = 0
    if parts.count == 2 {
        guard (1...2).contains(parts[1].count),
              parts[1].utf8.allSatisfy({ $0 >= 48 && $0 <= 57 }),
              let digits = Int(parts[1]) else { return nil }
        fraction = parts[1].count == 1 ? digits * 10 : digits
    }
    let cents = whole * 100 + fraction
    return cents > 0 ? cents : nil
}

@Model final class TaskItem {
    var title: String
    var isDone: Bool
    var createdAt: Date
    init(title: String) {
        self.title = title
        self.isDone = false
        self.createdAt = .now
    }
}

@Model final class Expense {
    var cents: Int
    var category: String
    var createdAt: Date
    init(cents: Int, category: String) {
        self.cents = cents
        self.category = category
        self.createdAt = .now
    }
}

@main struct LedgerApp: App {
    var body: some Scene {
        WindowGroup {
            TabView {
                NavigationStack { TaskListView() }
                    .tabItem { Label("待办", systemImage: "checklist") }
                NavigationStack { StatsView() }
                    .tabItem { Label("支出", systemImage: "chart.bar") }
            }
        }
        .modelContainer(for: [TaskItem.self, Expense.self], isAutosaveEnabled: false)
    }
}

struct TaskListView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \TaskItem.createdAt, order: .reverse) private var tasks: [TaskItem]
    @State private var title = ""
    @State private var errorText: String?
    private var active: [TaskItem] { tasks.filter { !$0.isDone } }
    private var completed: [TaskItem] { tasks.filter { $0.isDone } }

    var body: some View {
        List {
            Section("新建") {
                TextField("做什么？", text: $title)
                Button("添加") { add() }
                    .disabled(title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                if let errorText { Text(errorText).foregroundStyle(.red) }
            }
            Section("进行中") {
                ForEach(active) { task in row(task) }
                    .onDelete { delete($0, from: active) }
            }
            Section("已完成") {
                ForEach(completed) { task in row(task) }
                    .onDelete { delete($0, from: completed) }
            }
        }
        .navigationTitle("待办")
    }

    private func row(_ task: TaskItem) -> some View {
        Button {
            task.isDone.toggle()
            _ = save()
        } label: {
            Label(task.title, systemImage: task.isDone ? "checkmark.circle.fill" : "circle")
                .strikethrough(task.isDone)
        }
        .accessibilityHint(task.isDone ? "标为未完成" : "标为已完成")
    }

    private func add() {
        let value = title.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !value.isEmpty else { return }
        context.insert(TaskItem(title: value))
        if save() { title = "" }
    }

    private func delete(_ offsets: IndexSet, from displayed: [TaskItem]) {
        let selected = offsets.map { displayed[$0] }
        for task in selected { context.delete(task) }
        _ = save()
    }

    private func save() -> Bool {
        do {
            try context.save()
            errorText = nil
            return true
        } catch {
            context.rollback()
            errorText = "保存失败，已恢复上次保存的数据。请重试。"
            return false
        }
    }
}

struct StatsView: View {
    @Query private var tasks: [TaskItem]
    @Query(sort: \Expense.createdAt, order: .reverse) private var expenses: [Expense]
    @State private var showExpense = false
    private var total: Decimal {
        expenses.filter {
            Calendar.current.isDate($0.createdAt, equalTo: .now, toGranularity: .month)
        }.reduce(Decimal.zero) { $0 + Decimal($1.cents) } / 100
    }

    var body: some View {
        List {
            Section("汇总") {
                Text("完成 \(tasks.filter { $0.isDone }.count) / \(tasks.count) 项")
                Text("本月支出：\(total.formatted(.currency(code: "CNY")))")
            }
            Section("全部支出") {
                if expenses.isEmpty { Text("还没有支出记录") }
                ForEach(expenses) { expense in
                    LabeledContent(expense.category) {
                        Text((Decimal(expense.cents) / 100).formatted(.currency(code: "CNY")))
                    }
                }
            }
        }
        .navigationTitle("支出")
        .toolbar { Button("记一笔") { showExpense = true } }
        .sheet(isPresented: $showExpense) { ExpenseSheet() }
    }
}

struct ExpenseSheet: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss
    @State private var amount = ""
    @State private var category = "餐饮"
    @State private var errorText: String?

    var body: some View {
        NavigationStack {
            Form {
                TextField("金额，例如 12.50", text: $amount).keyboardType(.decimalPad)
                Picker("分类", selection: $category) {
                    ForEach(["餐饮", "交通", "其他"], id: \.self) { Text($0) }
                }
                if let errorText { Text(errorText).foregroundStyle(.red) }
            }
            .navigationTitle("记一笔")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("取消") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("保存") { save() }.disabled(parseCents(amount) == nil)
                }
            }
        }
    }

    private func save() {
        guard let cents = parseCents(amount) else { return }
        context.insert(Expense(cents: cents, category: category))
        do {
            try context.save()
            dismiss()
        } catch {
            context.rollback()
            errorText = "支出尚未保存，请重试。"
        }
    }
}
```

## 3. 为什么这样组织

`@Model` 让模型参与 SwiftData 管理，`insert` 把新对象登记到 context。本文关闭自动保存，在用户动作后显式 `try context.save()`，才能把保存失败展示出来。自动保存不保证每次赋值都已经落盘。参考 [ModelContext.save](https://developer.apple.com/documentation/swiftdata/modelcontext/save()) 与 [ModelContext.rollback](https://developer.apple.com/documentation/swiftdata/modelcontext/rollback())。

`@Query` 查询容器提供的 context，界面随模型变化刷新。此处只有一个编辑动作，失败时 `rollback()` 恢复全部未保存变化；扩大到多页面并行编辑时，应设计独立编辑 context 或事务边界，避免一个操作撤回其他页面的修改。

分组删除传入该组的数组快照。`IndexSet` 是当前分组下标，既不是数据库主键，也不是另一组的下标。完成操作用按钮触发显式保存，避免把双向绑定误解为数据库提交。

统计使用用户当前日历判断月份；若财务月份固定在某地区，应固定日历与时区。演示数据量小，所以本地筛选便于观察；大量记录应使用合适的查询条件，避免每次汇总都读取全库。

## 4. 按层验收，保留失败证据

先运行纯金额函数：用独立 Swift 命令行文件复制 `parseCents`，断言 `0.1 → 10`、`0.20 → 20`、`999999.99 → 99999999`，并确认非法输入返回 `nil`。这只证明解析逻辑，不证明 SwiftData 或 UI 可运行。

再在 Xcode 逐项执行第 1 节表格，记录 Xcode/SDK/目标系统版本与设备型号。用单独测试 context 验证存储失败与回滚，不要破坏个人数据目录制造失败。容器创建失败发生在应用启动阶段，本文 `.modelContainer` 简写尚未提供恢复 UI，正式工程需要处理这一独立错误路径。

进阶练习依次完成：给支出添加删除并验证重启；给待办加编辑草稿且取消不修改模型；给已有数据库增加字段并制定迁移方案；最后接入同步。每一步都有成功和失败的观察结果后再继续。

## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [SwiftData 与 Observation](../reference/framework-essentials/02-swiftdata-observability.md) · [错误处理](../reference/language-concepts/08-error-handling.md)
