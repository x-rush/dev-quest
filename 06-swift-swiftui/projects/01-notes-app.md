# 实战项目一：本地笔记应用（SwiftData）

## 分阶段练习与验收

**进入条件**：在 macOS/Xcode 的 iOS 17 或更高目标完成[首项目](../basics/08-first-project.md)的新增、保存、重启读取；能解释草稿、模型变化和 `context.save()` 成功的区别。新建独立的 Notes 工程并保留唯一 `@main`，不要直接把 `Note` 容器替换进已有待办记账数据库；模型迁移留到后续练习。

**最小产物**：含 `Note`、`NotesApp`、`NoteListView`、`NoteEditorView` 的 Xcode 工程，以及 Xcode/SDK/设备版本与验收记录。拆分文件时，模型文件导入 Foundation 和 SwiftData，两个视图文件均导入 SwiftUI 与 SwiftData。先做新增、列表、删除，再接编辑和搜索。

**验收动作**：新增 A/B，将 A 编辑为 A2，取消一次后确认仍是 A2；搜索 B 并删除，清空搜索后 A2 仍在。终止并重启应用，确认 A2 保留、B 不恢复；纯空格或换行标题不能保存。在独立测试工程的保存入口注入抛错替身，确认新建/编辑失败时表单保留、已保存数据回滚，删除失败时条目恢复且错误可见。本文未记录设备通过结果，未执行项写“未验证”。

**失败回查**：有界面更新却重启丢数据，先检查是否走到显式保存成功；保存失败查[错误处理](../reference/language-concepts/08-error-handling.md)，容器或模型错误查[SwiftData](../reference/framework-essentials/02-swiftdata-observability.md)。本练习关闭自动保存并只允许一个编辑动作，回滚会撤销该 context 中全部未保存修改。

**下一步**：上述验收通过后进入[天气应用](./02-weather-app.md)学习请求与取消；新增字段前先完成[模型迁移](../reference/framework-essentials/07-swiftdata-migration.md)，保留旧数据样本验证升级。

> **文档简介**: 从零构建一个带增删改查与搜索的本地笔记应用，完整走一遍 SwiftData 持久化 + SwiftUI 列表交互的最小闭环
>
> **目标读者**: 完成 basics 全部教程、首次做完整 iOS 应用的学习者
>
> **前置知识**: [basics/08-first-project.md](../basics/08-first-project.md)、[frameworks/01-swiftui-basics.md](../frameworks/01-swiftui-basics.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南（实战项目） |
| **难度** | ⭐ |
| **标签** | `#SwiftData` `#CRUD` `#List` `#搜索` `#入门项目` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 项目目标

最终效果：一个笔记列表页，支持新建、编辑、滑动删除、关键词搜索，数据重启不丢。预计 2-4 小时完成。

**功能清单**：
- ✅ 笔记列表（标题 + 摘要 + 时间）
- ✅ 新建 / 编辑笔记（详情页表单）
- ✅ 滑动删除 + 空状态视图
- ✅ 搜索栏过滤（本地过滤即可）

## 🛠️ 第一步：数据模型

```swift
import Foundation
import SwiftData

@Model
final class Note {
    var title: String
    var content: String           // 正文，列表页只显示前 50 字
    var createdAt: Date

    var summary: String {         // 派生数据用计算属性，不重复存储
        String(content.prefix(50))
    }

    init(title: String, content: String = "") {
        self.title = title
        self.content = content
        self.createdAt = .now
    }
}
```

模型设计原则速查见 [02-swiftdata-observability.md](../reference/framework-essentials/02-swiftdata-observability.md)。

## 🛠️ 第二步：App 入口装配容器

```swift
import SwiftData
import SwiftUI

@main
struct NotesApp: App {
    var body: some Scene {
        WindowGroup {
            NoteListView()
        }
        .modelContainer(for: Note.self, isAutosaveEnabled: false)
    }
}
```

## 🛠️ 第三步：列表页（查 + 删 + 搜）

```swift
struct NoteListView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \Note.createdAt, order: .reverse)   // 按创建时间倒序
    private var notes: [Note]

    @State private var searchText = ""
    @State private var showingEditor = false
    @State private var errorText: String?

    // 搜索过滤：纯内存过滤，数据量大再考虑 #Predicate
    private var filteredNotes: [Note] {
        searchText.isEmpty
            ? notes
            : notes.filter { $0.title.localizedStandardContains(searchText) }
    }

    var body: some View {
        NavigationStack {
            Group {
                if filteredNotes.isEmpty {
                    ContentUnavailableView.search     // iOS 17+ 官方空状态
                } else {
                    noteList
                }
            }
            .navigationTitle("我的笔记")
            .alert("删除未保存", isPresented: Binding(
                get: { errorText != nil },
                set: { if !$0 { errorText = nil } }
            )) {
                Button("知道了", role: .cancel) { errorText = nil }
            } message: { Text(errorText ?? "") }
            .searchable(text: $searchText, prompt: "搜索标题")
            .toolbar {
                Button {
                    showingEditor = true
                } label: {
                    Image(systemName: "plus")
                }
            }
            .sheet(isPresented: $showingEditor) {
                NoteEditorView(note: nil)             // nil = 新建
            }
        }
    }

    private var noteList: some View {
        List {
            ForEach(filteredNotes) { note in
                NavigationLink(value: note) {
                    VStack(alignment: .leading) {
                        Text(note.title).font(.headline)
                        Text("\(note.summary) · \(note.createdAt.formatted(date: .abbreviated, time: .shortened))")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .onDelete(perform: delete)                // 滑动删除
        }
        .navigationDestination(for: Note.self) { note in
            NoteEditorView(note: note)                // 点进去直接编辑
        }
    }

    private func delete(at offsets: IndexSet) {
        let selected = offsets.map { filteredNotes[$0] }
        for note in selected { context.delete(note) }
        do {
            try context.save()
            errorText = nil
        } catch {
            context.rollback()
            errorText = "删除失败，已恢复上次保存的数据。请重试。"
        }
    }
}
```

## 🛠️ 第四步：编辑页（增 + 改）

```swift
struct NoteEditorView: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss

    let note: Note?                       // nil 新建，非 nil 编辑

    @State private var title = ""
    @State private var content = ""
    @State private var errorText: String?

    var body: some View {
        NavigationStack {
            Form {
                TextField("标题", text: $title)
                TextField("正文", text: $content, axis: .vertical)
                    .lineLimit(6...12)
                if let errorText { Text(errorText).foregroundStyle(.red) }
            }
            .navigationTitle(note == nil ? "新建笔记" : "编辑笔记")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("保存") { save() }
                        .disabled(title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button("取消") { dismiss() }
                }
            }
            .onAppear(perform: loadIfNeeded)      // 编辑态回填表单
        }
    }

    private func loadIfNeeded() {
        guard let note else { return }
        title = note.title
        content = note.content
    }

    private func save() {
        let normalizedTitle = title.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalizedTitle.isEmpty else {
            errorText = "请输入非空标题。"
            return
        }
        if let note {
            note.title = normalizedTitle
            note.content = content
        } else {
            context.insert(Note(title: normalizedTitle, content: content))
        }
        do {
            try context.save()
            errorText = nil
            dismiss()
        } catch {
            context.rollback()
            errorText = "保存失败，输入仍保留。请重试。"
        }
    }
}
```

## ✅ 检查点

- [ ] 新建笔记后返回列表，新条目立即出现（`@Query` 响应式刷新）
- [ ] 杀掉 App 重开，数据还在（磁盘持久化）
- [ ] 滑动删除、空状态、搜索过滤均正常

## ❌ 常见问题

**Q1: `Note` 需要 `Identifiable` 吗？** `@Model` 自动提供 `persistentModelID`，`ForEach` 直接可用，无需手写 `id`。

**Q2: 保存报错 "unresolved model"？** 确认插入后再 save，且容器在 App 根部已装配。

**Q3: 想加图片附件？** 存文件路径或 `Data` 字段，大文件用外部存储 `@Attribute(.externalStorage)`。

## 🎯 进阶挑战

- [ ] 增加置顶功能（`isPinned` 字段 + 列表分区）
- [ ] 笔记按标签分类（`Tag` 模型 + 多对多关系）
- [ ] 数据迁移：给 `Note` 加一个 `color` 字段并保持旧数据可读

## 相关文档

- 📄 [02-weather-app.md](./02-weather-app.md) — 下一篇：天气应用（网络 + 定位）
- 📄 [02-swiftdata-observability.md](../reference/framework-essentials/02-swiftdata-observability.md) — SwiftData 字典
- 📄 [07-swiftdata-migration.md](../reference/framework-essentials/07-swiftdata-migration.md) — 数据迁移字典（进阶挑战"数据迁移"的参考）
- 📄 [01-swift-swiftui-cheatsheet.md](../reference/quick-references/01-swift-swiftui-cheatsheet.md) — 语法速查（写卡壳时翻）
- 📄 [08-first-project.md](../basics/08-first-project.md) — 教程侧的第一个项目


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
