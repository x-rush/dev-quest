# SwiftData 模型迁移速查

> **文档简介**: SwiftData schema 版本化与迁移的条目式参考：VersionedSchema 版本化枚举、SchemaMigrationPlan、MigrationStage.lightweight/custom，以及默认值/重命名/关系变化三类陷阱
>
> **目标读者**: 已上架或已积累本地数据的 App，要改模型又不能丢旧数据的学习者
>
> **前置知识**: [02-swiftdata-observability.md](./02-swiftdata-observability.md)（@Model 与 ModelContainer）；实战见 [projects/01-notes-app.md](../../projects/01-notes-app.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#SwiftData` `#迁移` `#VersionedSchema` `#SchemaMigrationPlan` `#iOS17+` |
| **更新日期** | `2026年9月` |

---

## 1. 为什么需要迁移

**定义**: App 已发布后磁盘上已有旧结构的数据库文件。此时改 @Model 而不做任何处理，旧 store 的新旧 schema 不匹配，容器创建/打开就会失败，用户数据"消失"。**迁移 = 告诉框架"数据怎么从旧结构搬到新结构"**。

SwiftData 的做法分三步：

1. 把每个历史版本的模型用 `VersionedSchema` 枚举冻结
2. 用 `SchemaMigrationPlan` 声明"哪些版本、怎么迁移"
3. 容器装配时挂上 `migrationPlan`

> 核心纪律：**模型一旦发版，旧版本类就不再改**——要变就新建 SchemaV2 枚举里的新类。

## 2. VersionedSchema：冻结每个版本

```swift
import SwiftData

// 旧版本（已发版，只读，永不修改）
enum SchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [SchemaV1.Note.self] }

    @Model
    final class Note {
        var title: String
        var content: String
        var createdAt: Date
        init(title: String, content: String) {
            self.title = title
            self.content = content
            self.createdAt = .now
        }
    }
}

// 新版本（当前开发）
enum SchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] { [SchemaV2.Note.self] }

    @Model
    final class Note {
        var title: String
        var content: String
        var color: String?          // 本次新增字段（可选 → 轻量迁移可处理）
        var createdAt: Date
        init(title: String, content: String, color: String? = nil) {
            self.title = title
            self.content = content
            self.color = color
            self.createdAt = .now
        }
    }
}
```

要点：

- 每个版本枚举内**完整声明该版本用到的全部 @Model 类**（嵌套在枚举命名空间里）
- `versionIdentifier` 每次 schema 变化必须递增，它是 store 里记录的版本标记
- 视图/业务代码统一引用**最新版本**的类（`SchemaV2.Note`），旧枚举只为迁移服务

## 3. SchemaMigrationPlan 与 MigrationStage

**定义**: `SchemaMigrationPlan` 回答两个问题——"存在哪些版本"（`schemas`）与"每一步怎么迁"（`stages`）。每个 `MigrationStage` 是相邻两版之间的一次迁移。

```swift
enum NotesMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [SchemaV1.self, SchemaV2.self]          // 按版本顺序列出全部历史版本
    }

    static var stages: [MigrationStage] {
        [migrationV1toV2]
    }

    // 轻量迁移：加可选/带默认值字段这类可自动推断的改动
    static let migrationV1toV2 = MigrationStage.lightweight(
        fromVersion: SchemaV1.self,
        toVersion: SchemaV2.self
    )

    // 自定义迁移：框架推断不了时，手动搬数据（旧数据术语里的"重量级"）
    static let migrationV2toV3 = MigrationStage.custom(
        fromVersion: SchemaV2.self,
        toVersion: SchemaV3.self,
        willMigrate: { context in
            // 迁移前：旧 schema 的 ModelContext，可预读/暂存
        },
        didMigrate: { context in
            // 迁移后：新 schema 的 ModelContext，在此改写数据
        }
    )
}
```

| Stage | 何时用 |
|-------|--------|
| `MigrationStage.lightweight(fromVersion:toVersion:)` | 加/删字段（可选或有默认值）、加索引等框架可自动推断的变化 |
| `MigrationStage.custom(fromVersion:toVersion:willMigrate:didMigrate:)` | 重命名、改类型、关系结构调整等推断不了的变化；两个闭包都可选 |

容器装配：

```swift
WindowGroup { ContentView() }
    .modelContainer(for: SchemaV2.Note.self, migrationPlan: NotesMigrationPlan.self)
```

> 实际迁移发生在**容器首次打开 store 时**（启动路径上）；成功后 store 的版本标记更新为新版本。

## 4. 什么改动能轻量迁移

| 改动 | 能否 lightweight | 处理方式 |
|------|------------------|----------|
| 新增**可选**字段 | ✅ 通常可以 | 直接 lightweight |
| 新增**有默认值**字段 | ✅ 通常可以 | init 默认值或属性默认值 |
| 新增**无默认值必填**字段 | ❌ 不保证 | 补默认值/改为可选，或 custom |
| 删除字段 | ✅ 通常可以 | 旧列被忽略 |
| **重命名字段** | ❌ 框架不知道新旧字段同源 | custom stage：旧类读旧名 → 写入新类新名 |
| **改字段类型**（如 Int → String） | ❌ | custom stage 逐条转换 |
| **关系变化**（加关系/改删除规则/反转方向） | ⚠️ 视情况 | 加关系多为轻量；改删除规则/结构重组走 custom 验证 |

轻量能处理的就是"框架拿到新旧两份 schema 能自己算出怎么填空"的变化；**涉及数据判断与换算的一律 custom**。

## 5. custom 迁移示例：字段重命名

```swift
// SchemaV3.Note 把 content 重命名为 body（并保留 color）
static let migrationV2toV3 = MigrationStage.custom(
    fromVersion: SchemaV2.self,
    toVersion: SchemaV3.self,
    willMigrate: { context in },
    didMigrate: { context in
        // didMigrate 拿到新 schema 上下文；旧值已由框架按同名/可推断字段搬运，
        // 重命名的字段在此按业务规则补偿（简单场景可让新旧字段并存一版，这里搬值）
        let notes = try context.fetch(FetchDescriptor<SchemaV3.Note>())
        for note in notes where note.body == nil {
            note.body = note.content        // 旧列值补到新列
        }
        try context.save()
    }
)
```

> 重命名的"最省事"变体：**新旧字段并存一个版本**（保留旧列 + 新列一起写），下一版再删旧列走 lightweight——用两次轻量换一次 custom。

## ⚠️ 高频陷阱速查

- **迁移计划的 `schemas` 数组漏了历史版本**（指 SchemaMigrationPlan，VersionedSchema 用的是 `models`）：只写最新版，框架无法完成"旧 store → 新 schema"的链路，启动即迁移失败
- **改了模型忘递增 `versionIdentifier`**：新代码配旧版本号，store 判断"无需迁移"却对不上结构，行为不可预期
- **随手改已发版的旧枚举**：SchemaV1 是历史快照，动了它 = 伪造历史，老用户迁移必然错乱
- **无默认值的必填新字段**：不属于可自动推断的变化，轻量迁移会失败——新字段一律给默认值或设为可选
- **重命名当轻量处理**：SwiftData 没有 Core Data 的 renamingIdentifier 机制，直接改名对框架而言是"删一个加一个"，旧值丢失
- **只在新装 App 上测**：新装根本不走迁移——必须用**旧版本 App 造好的旧数据**（模拟器保留旧 store）升级验证
- **迁移跑在启动主线程**：数据量大时启动变慢；把重搬运的算术放 custom stage，必要时先 willMigrate 预聚合

## 相关文档

- 📄 [02-swiftdata-observability.md](./02-swiftdata-observability.md) — @Model/容器/@Query 基础
- 📄 [01-notes-app.md](../../projects/01-notes-app.md) — 进阶挑战"数据迁移"的实战入口
- 📄 [01-foundation-and-stdlib.md](../library-guides/01-foundation-and-stdlib.md) — Date 等基础类型

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，SwiftData 迁移概念完整解释以此处为单一事实来源*
