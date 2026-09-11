# sqlc vs GORM vs ent：Go 数据访问层选型

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

这是 Go 语言访问 SQL 数据库的三种主流心智模型：

- **sqlc（SQL-first）**：开发者手写 SQL 与 schema，由工具在编译期生成类型安全的 Go 访问代码。SQL 是事实来源（source of truth），Go 代码是产物。
- **GORM（ORM-first）**：开发者定义 Go 结构体与关联，通过链式 API 由 ORM 生成 SQL。Go 结构体是事实来源，SQL 是产物。
- **ent（Schema-as-Code 实体框架）**：与 GORM 同属模型优先阵营，但 schema 用 Go 代码声明（Fields/Edges），经代码生成产出强类型实体与查询 API——可以理解为"模型优先 + 编译期类型安全 + 图式关联遍历"。

解决的问题：**在"对 SQL 的完全掌控"与"开发效率与抽象收益"之间做出符合项目特征的取舍**。三者不互斥，可在同一服务内按场景混用。

## 📊 对比表

| 维度 | sqlc（SQL-first） | GORM（ORM-first） | ent（Schema-as-Code） |
|------|------------------|-------------------|----------------------|
| **心智模型** | 先写 SQL，代码是生成的产物 | 先写结构体，SQL 是生成的产物 | 先写 schema 声明，实体/查询代码是生成的产物 |
| **事实来源** | `.sql` 文件（schema + query） | Go struct + tag | Go schema 声明（Fields + Edges） |
| **类型安全** | 编译期生成强类型方法，参数与返回值类型精确 | 链式 API 类型安全，但 `Where("raw string")` 内的列名/条件不校验 | 生成强类型谓词与遍历 API，字段/关联均编译期校验 |
| **SQL 掌控力** | 完全掌控，所见即所得 | ORM 生成 SQL，复杂查询需 debug 生成结果 | 生成查询构造器，复杂 SQL 需 debug 或回落 raw |
| **关联/图遍历** | 手写 JOIN | `Preload`/`Joins` 声明式处理一对多、多对多 | 强项：Edges 图式遍历（多跳关联链式书写） |
| **迁移** | 通常配合 golang-migrate、goose 等独立迁移工具 | 内置 `AutoMigrate`（生产环境慎用） | 配套 Atlas 版本化迁移（ent 官方工具链） |
| **Codegen 负担** | 需要在构建/CI 流程中固定生成步骤 | 无 codegen，即写即用 | codegen 负担最重：schema 变更即需重新生成 |
| **生态与资料** | 社区活跃，文档以英文为主 | Go 生态最普及，中文资料最丰富 | Meta 出品、文档质量高，但社区规模小于 GORM |
| **性能特征** | 无运行时反射开销，生成代码即普通 Go 代码 | 有运行时反射与对象开销，可通过配置缓解 | 生成代码为主，开销介于两者之间 |
| **典型适用规模** | 查询相对固定、SQL 复杂度高的系统（报表、分析、遗留库） | 业务模型复杂、增删改频繁的 CRUD 应用 | 关联密集的领域模型（社交关系、内容图谱）、重视重构安全的团队 |

## 💡 示例

同一个需求「按城市查询成年用户」的三种写法：

**sqlc：先写 SQL，调用生成的代码**

```sql
-- query.sql（sqlc 的输入）
-- name: ListAdultUsersByCity :many
SELECT id, name, email, age
FROM users
WHERE city = $1 AND age >= $2;
```

```go
// 生成的代码（db 包由 sqlc 产出，勿手改）
users, err := queries.ListAdultUsersByCity(ctx, "Shanghai", 18)
// users 类型为 []db.User，参数个数/类型错误在编译期报错
```

**GORM：先定义结构体，链式查询**

```go
type User struct {
    ID    uint
    Name  string
    Email string
    Age   int
    City  string
}

var users []User
err := db.Where("city = ? AND age >= ?", "Shanghai", 18).
    Find(&users).Error
```

**ent：先声明 schema，使用生成的谓词查询**

```go
// schema/user.go（ent 的输入：声明而非定义结构体）
type User struct{ ent.Schema }

func (User) Fields() []ent.Field {
    return []ent.Field{
        field.String("name"),
        field.String("email"),
        field.Int("age"),
        field.String("city"),
    }
}
```

```go
// 生成的代码：user 包由 ent 产出，勿手改
users, err := client.User.
    Query().
    Where(
        user.CityEQ("Shanghai"),
        user.AgeGTE(18),
    ).
    All(ctx)
// 字段名拼错、类型不匹配都在编译期报错
```

混用策略（同一服务内）：

```go
// 常规 CRUD 走 GORM，保持开发效率
db.Create(&order)

// 复杂报表查询走 sqlc 生成的强类型方法
rows, err := queries.MonthlyRevenueByRegion(ctx, start, end)
```

## 🧭 选型建议

| 场景 | 推荐 | 理由 |
|------|------|------|
| 查询固定、SQL 密集（报表、数据仓库对接） | sqlc | SQL 即文档，编译期兜底 |
| 团队 SQL 能力强，追求零魔法 | sqlc | 无运行时抽象，行为可预测 |
| 标准业务 CRUD、模型关联复杂 | GORM | 声明式关联与预加载收益大 |
| 快速原型 / 内部工具 | GORM | `AutoMigrate` + 链式 API 起步最快 |
| 需要动态拼接查询条件（多条件筛选） | GORM（或 sqlc + 条件 SQL 技巧） | ORM 拼接更自然 |
| 遗留数据库、schema 不可控 | sqlc | 适配既有表结构，不反向约束 |
| 关联模型复杂、多跳关系查询频繁 | ent | Edges 图式遍历是该场景的最优表达 |
| 团队重构频繁、需要编译期兜底 schema 变更 | ent | 谓词 API 让字段/关联改动在编译期暴露 |
| 高性能、低反射开销敏感 | sqlc | 生成代码即普通代码 |
| 团队熟悉 Rails/Django 式 ORM 习惯 | GORM | 心智模型迁移成本最低 |

一句话结论：**把 SQL 当资产选 sqlc，把模型当资产选 GORM；模型优先且想要编译期类型安全与图遍历选 ent；混用（CRUD 用 GORM、复杂查询用 sqlc）在工程上完全成立。**

## ⚠️ 常见陷阱

- ❌ **错误做法**：sqlc 生成的代码手改后再次运行生成被覆盖。
- ✅ **正确做法**：生成目录纳入 `.gitignore` 或标注"勿改"，把 codegen 固定进 Makefile/CI。
- ❌ **错误做法**：GORM 循环中逐条查询关联数据。
- ✅ **正确做法**：用 `Preload` 一次性预加载，避免 N+1。
- ❌ **错误做法**：把 `AutoMigrate` 当作生产环境的迁移方案。
- ✅ **正确做法**：生产使用版本化迁移工具，schema 变更可审查、可回滚。
- ❌ **错误做法**：在 `Where("...")` 里拼用户输入字符串。
- ✅ **正确做法**：一律使用参数占位符 `?`，三者皆然。
- ❌ **错误做法**：ent 项目里手写/手改生成的实体代码，或 schema 与生成结果不同步。
- ✅ **正确做法**：schema 是唯一事实来源，改动后立即重新生成并纳入 CI 检查；手写逻辑放 hook/扩展层。

## 🔗 相关条目

- 📄 **[GORM ORM 速查](./02-gorm-orm.md)** - ORM-first 模型的完整字典
- 📄 **[路由器选型对比](./04-router-selection.md)** - 同系列的 Web 层选型条目
- 📄 **[GORM 完整教程](../../frameworks/03-gorm-orm-complete.md)** - 操作指南层
- 📄 **[Go 标准库核心 API](../library-guides/01-go-standard-library.md)** - `database/sql` 底层接口
- 🌐 **[sqlc 官方文档](https://docs.sqlc.dev/)** - 权威来源
- 🌐 **[GORM 官方文档](https://gorm.io/zh_CN/docs/)** - 权威来源
- 🌐 **[ent 官方文档](https://entgo.io/)** - 权威来源

---

*最后更新: 2026年09月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
