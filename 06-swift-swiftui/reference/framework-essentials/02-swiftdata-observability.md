# SwiftData 与 Observation 框架速查

> **文档简介**: SwiftData（@Model/ModelContext/ModelContainer/关系查询）与 Observation（@Observable 追踪机制）两大现代框架的条目式参考
>
> **目标读者**: 需要查阅持久化与响应式数据细节的中级学习者
>
> **前置知识**: [basics/08-first-project.md](../../basics/08-first-project.md) 有完整实战；[basics/04-views-state.md](../../basics/04-views-state.md) 有数据流基础

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#SwiftData` `#Observation` `#持久化` `#数据建模` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. SwiftData

### 1.1 @Model 宏

**定义**: 把 class 变成持久化模型：属性自动建列、对象自动变更追踪。

```swift
import SwiftData

@Model
final class Note {
    var title: String
    var body: String?            // 正文；模型字段命名还需避免与生成成员冲突
    var createdAt: Date
    var priority: Int = 0

    @Attribute(.unique) var slug: String        // 唯一约束
    @Transient var cache: String?               // 不持久化字段

    init(title: String, slug: String) {
        self.title = title
        self.slug = slug
        self.createdAt = .now
    }
}
```

| 宏/修饰 | 作用 |
|---------|------|
| `@Model` | 生成持久化代码（宏展开为 `PersistentModel` 与 `Observation` 一致性实现，属性自动可观察；`@ModelActor` 是独立的并发宏，二者无关） |
| `@Attribute(.unique)` | 唯一性约束（重复插入会 upsert/报错） |
| `@Attribute(.externalStorage)` | 大数据外存（图片二进制） |
| `@Transient` | 跳过持久化 |
| `#Index<Note>([\.title], [\.createdAt])`（iOS 18+） | 建索引加速查询 |

**支持的属性类型**: String、数值、Bool、Date、Data、UUID、满足持久化要求的 Codable 枚举/值类型、其他 @Model（关系）、`[Model]`（一对多）。

### 1.2 模型关系

```swift
@Model
final class Project {
    var name: String
    @Relationship(deleteRule: .cascade, inverse: \TaskItem.project)
    var tasks: [TaskItem] = []
    init(name: String) { self.name = name }
}

@Model
final class TaskItem {
    var title: String
    var project: Project?
    init(title: String) { self.title = title }
}
```

| deleteRule | 删除 Project 时 |
|------------|----------------|
| `.cascade` | 级联删除全部 Task |
| `.nullify` | Task.project 置 nil |
| `.deny` | 有子对象则阻止删除 |
| `.noAction` | 不处理（危险） |

### 1.3 ModelContainer 与 ModelContext

```swift
// App 根部：容器 = 数据库
WindowGroup { Root() }
    .modelContainer(for: [Note.self, Project.self])
    // .modelContainer(for: Note.self, isStoredInMemoryOnly: true)  // 测试用

// 手动构造（脚本/预览）
let config = ModelConfiguration(isStoredInMemoryOnly: true)
let container = try ModelContainer(for: Note.self, configurations: config)
```

```swift
// 上下文 = 工作区（读写事务单位）
@Environment(\.modelContext) private var context

context.insert(note)          // 插入
context.delete(note)          // 删除
try context.save()            // 手动保存（mainContext 通常启用 autosave；手动创建的上下文需检查配置）
try context.fetchCount(descriptor) // 计数
try context.fetch(descriptor)  // 查询
```

### 1.4 @Query（视图查询）

```swift
@Query private var all: [Note]                                    // 全部
@Query(sort: \Note.createdAt, order: .reverse) private var recent: [Note]
@Query(filter: #Predicate<Note> { $0.priority > 2 },
       sort: [SortDescriptor(\.createdAt)])
private var hot: [Note]
```

**#Predicate 限制**: 只能引用模型自身属性与局部捕获变量；不能调用任意函数。复杂过滤取回后用 Swift `filter`，或改用 `FetchDescriptor`（编程式查询，支持 fetchLimit 等配置）。

---

## 2. Observation 框架

### 2.1 追踪机制

**定义**: `@Observable` 宏把每个存储属性包上 get/set 钩子——视图在 body 中**读取**某属性即注册追踪，**写入**该属性即通知相关视图重算。

```swift
@Observable
final class Session {
    var user: User?              // 被读取 → 被追踪
    var tokenCount = 0
    let launchDate = Date.now    // 不可变值，不产生属性修改通知

    private var _cache: [String: Int] = [:]   // private 属性同样参与
}
```

要点：

- **按属性粒度**：改 `tokenCount` 不会让只读了 `user` 的视图重算
- **读取即注册**：追踪发生在 body 求值期间的自然读取，无需任何显式订阅
- **非 UI 绑定**：可在测试、Service 层直接用，不 import SwiftUI
- `@ObservationIgnored`：豁免某个属性不被追踪（如计算型副作用字段）

```swift
@Observable
final class Router {
    var path: [Route] = []
    @ObservationIgnored var analyticsID = UUID()   // 不触发 UI
}
```

### 2.2 与 Combine 对象的边界

| 需求 | 做法 |
|------|------|
| 新模型 | 部署目标支持时考虑 `@Observable`，并确定所有者与隔离方式 |
| 桥接旧 ObservableObject | 视图包 `@StateObject`/`@ObservedObject` 维持旧机制 |
| 时序事件流 | AsyncSequence/AsyncStream（见 [03-concurrency-api.md](../language-concepts/03-concurrency-api.md)），或按已有 Publisher 管线选择 Combine |

**组合模式分工**：**SwiftData 管持久化事实，Observation store 管 UI 瞬时状态**（选中项、过滤器、加载相）——一个 `@MainActor @Observable` store 持有 `ModelContext` 与筛选字段即可，不重复存同一份数据。

---

## ⚠️ 高频陷阱速查

- **生成成员冲突**：不要凭名字猜测保留规则；出现宏展开诊断时检查当前 SDK 的生成成员，用更具体的业务字段名消除歧义
- **unique + CloudKit 冲突**：`.automatic` 同步不支持 `@Attribute(.unique)`
- **@Query 硬编码谓词**：谓词在 init 求值一次；想"随筛选条件变"的查询，改用 `context.fetch` + `.onChange`，或 `init(filter:)` 传入
- **@Observable 属性在非隔离线程写**：被 UI 追踪的属性应由 `@MainActor` 上下文写入（store 标 @MainActor）

## 相关文档

- 📄 [04-swiftui-state-api.md](../language-concepts/04-swiftui-state-api.md) — @Query/@State 等包装器
- 📄 [03-concurrency-api.md](../language-concepts/03-concurrency-api.md) — ModelActor 并发查询
- 📄 [07-swiftdata-migration.md](./07-swiftdata-migration.md) — 模型变更后的版本化迁移
- 📄 [01-foundation-and-stdlib.md](../library-guides/01-foundation-and-stdlib.md) — Data/UUID 等基础类型


<!-- full-library-explanation -->
## 从内存对象到可恢复的数据

修改 Note.title 先改变上下文管理的对象；save 成功才是可以向用户报告“已保存”的明确边界。Observation 负责通知依赖该属性的视图更新，不保证磁盘写入成功。网络上传成功、界面显示成功、本地保存成功是三件不同的事。

练习：用内存 ModelContainer 写测试，插入两条笔记、save、按 priority 查询、修改再查询、删除再查询。随后改用测试磁盘库，结束进程后重启验证持久化。内存库只能证明 CRUD 逻辑，不证明重启恢复。保存失败要保留用户草稿并展示可重试错误，不使用 try? 吞掉失败。

跨 actor 工作时传持久标识或 Sendable 值快照，在目标隔离域自己的上下文重新取对象；不要把同一个可变 ModelContext 或 @Model 实例交给任意后台任务。查询过滤必须被存储层支持，FetchDescriptor 不会使任意 Swift 函数自动可用于谓词。

最低系统版本、CloudKit 的 schema 限制与迁移路径需要一起设计。唯一约束、关系和自定义 Codable 字段都要用真实目标存储测试，不能仅凭预览成功认定兼容。参考 [SwiftData](https://developer.apple.com/documentation/swiftdata)。本轮未运行 SwiftData 测试。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
