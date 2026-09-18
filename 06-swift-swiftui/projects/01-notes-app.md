# 实战项目一：本地笔记应用（SwiftData）

## 分阶段练习与验收

**最小阶段**：先在 SwiftData 创建与查询一条笔记。

**验收结果**：重启后内容保留；无效标题失败；删除立即反映在查询结果。

**扩展顺序**：编辑和搜索作为第二阶段，关系与迁移单独测试。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

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
        .modelContainer(for: Note.self)     // 建库 + 注入环境，一行搞定
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
        for index in offsets { context.delete(filteredNotes[index]) }
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

    var body: some View {
        NavigationStack {
            Form {
                TextField("标题", text: $title)
                TextField("正文", text: $content, axis: .vertical)
                    .lineLimit(6...12)
            }
            .navigationTitle(note == nil ? "新建笔记" : "编辑笔记")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("保存") { save() }
                        .disabled(title.trimmingCharacters(in: .whitespaces).isEmpty)
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
        if let note {
            note.title = title                    // @Model 对象直接改属性
            note.content = content
        } else {
            context.insert(Note(title: title, content: content))
        }
        try? context.save()
        dismiss()
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
