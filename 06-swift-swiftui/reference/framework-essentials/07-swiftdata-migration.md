# SwiftData 迁移：升级结构时保住旧数据

前置：@Model、ModelContainer、ModelContext。最低基础为支持 SwiftData 的系统；具体 schema 能力仍需按目标 SDK 检查。本页代码用于 iOS 工程中的模型层，本轮未在 Apple SDK 编译或执行迁移。

## 为什么新装成功不代表升级成功

新装直接创建当前结构；升级必须读取用户磁盘上的旧结构。迁移负责解释两者的对应关系。框架可推断部分轻量变化，不能假设所有修改都自动安全，也不能遇到打开失败就删库重建。

发布过的 VersionedSchema 应保留为历史快照。只修改新版本，在 SchemaMigrationPlan 中保留从受支持历史版本通往当前版本的路径。版本号不是绕过结构校验的开关。

## 字段重命名：使用 originalName 映射

下面保留旧版 content，把新代码中的属性称为 body。重命名不是必须写自定义搬运循环：@Attribute(originalName:) 可以表达同源属性。

```swift
import Foundation
import SwiftData

enum NotesV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [Note.self] }
    @Model final class Note {
        var content: String
        init(content: String) { self.content = content }
    }
}

enum NotesV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] { [Note.self] }
    @Model final class Note {
        @Attribute(originalName: "content") var body: String
        var color: String?
        init(body: String, color: String? = nil) {
            self.body = body
            self.color = color
        }
    }
}

enum NotesPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] { [NotesV1.self, NotesV2.self] }
    static var stages: [MigrationStage] {
        [.lightweight(fromVersion: NotesV1.self, toVersion: NotesV2.self)]
    }
}

func openNotes() throws -> ModelContainer {
    try ModelContainer(for: NotesV2.Note.self, migrationPlan: NotesPlan.self)
}
```

生产容器还应明确配置持久化位置。测试 V1 与 V2 时必须指向同一个测试 store；两个内存容器不可能证明迁移成功。示例当前没有启用 CloudKit，不能直接当云同步迁移方案。

## 默认值、类型变化与自定义阶段

| 改动 | 判断依据 | 验证重点 |
|---|---|---|
| 新增可选属性 | 旧记录可用 nil 表达缺省 | nil 是否符合业务规则 |
| 新增有存储默认值的属性 | schema 是否能够提供该默认值 | init 参数默认值不等于数据库迁移默认值 |
| 属性重命名 | originalName 是否指向正确旧属性 | 所有旧文本逐条保留 |
| String 改数值等类型变化 | 是否需要解析与异常处理 | 非法旧值不能静默变成 0 |
| 增加唯一约束 | 旧库是否已有重复 | 先定义去重/合并规则，保留必要关联 |
| 删除或重组关系 | 删除规则与引用是否有效 | 不产生孤立记录或意外级联删除 |

自定义 MigrationStage 的 willMigrate 面向旧 schema，didMigrate 面向新 schema。不能在 didMigrate 中读取已经不存在的旧字段，也不能凭空创建一个未声明的 SchemaV3。复杂转换可设计过渡版本，先保留旧值并新增可选目标字段，完成转换与校验后再移除旧字段。把工作放进 custom 不会自动使启动变快；需要测量数据规模与迁移耗时。

## 可重复的升级验收

1. 用真实历史模型生成专用 V1 测试库，含空文本、中文、长文本与关系边界数据，并保留原始副本。
2. 用 V2 打开该测试库，验证条数与每条 body 的值，新增 color 应为 nil。
3. 关闭后再次打开，确认不重复转换、不丢数据。
4. 从每个承诺支持的历史版本直接升级，而不只测试相邻一版；在最低支持系统上重复验证。
5. 模拟无可用空间或迁移错误，检查界面提供恢复与反馈路径，原库不会被自动删除。

自测：为什么只给 `init(body: String = "")` 加默认参数不足以填充旧库必填字段？因为旧记录的迁移不是逐条调用业务构造器创建新对象。

依据：[Apple 模型持久化说明](https://developer.apple.com/documentation/swiftdata/preserving-your-apps-model-data-across-launches)、[Attribute 原名称参数](https://developer.apple.com/documentation/swiftdata/attribute(_:originalname:hashmodifier:))。继续阅读 [SwiftData 基础](02-swiftdata-observability.md) 与 [笔记项目](../../projects/01-notes-app.md)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
