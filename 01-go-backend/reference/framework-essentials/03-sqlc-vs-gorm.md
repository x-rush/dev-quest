# sqlc vs GORM：SQL-first 与 ORM-first 的数据访问选型

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

这是 Go 语言访问 SQL 数据库的两种主流心智模型：

- **sqlc（SQL-first）**：开发者手写 SQL 与 schema，由工具在编译期生成类型安全的 Go 访问代码。SQL 是事实来源（source of truth），Go 代码是产物。
- **GORM（ORM-first）**：开发者定义 Go 结构体与关联，通过链式 API 由 ORM 生成 SQL。Go 结构体是事实来源，SQL 是产物。

解决的问题：**在"对 SQL 的完全掌控"与"开发效率与抽象收益"之间做出符合项目特征的取舍**。二者不互斥，可在同一服务内按场景混用。

## 📊 对比表

| 维度 | sqlc（SQL-first） | GORM（ORM-first） |
|------|------------------|-------------------|
| **心智模型** | 先写 SQL，代码是生成的产物 | 先写结构体，SQL 是生成的产物 |
| **事实来源** | `.sql` 文件（schema + query） | Go struct + tag |
| **类型安全** | 编译期生成强类型方法，参数与返回值类型精确 | 链式 API 类型安全，但 `Where("raw string")` 内的列名/条件不校验 |
| **SQL 掌控力** | 完全掌控，所见即所得 | ORM 生成 SQL，复杂查询需 debug 生成结果 |
| **动态查询** | 弱项：条件分支需写多份查询或借助 COALESCE 等技巧 | 强项：链式条件可按逻辑自由拼接 |
| **关联/预加载** | 手写 JOIN | `Preload`/`Joins` 声明式处理一对多、多对多 |
| **迁移** | 通常配合 golang-migrate、goose 等独立迁移工具 | 内置 `AutoMigrate`（生产环境慎用） |
| **学习曲线** | 前提是熟悉 SQL；工具本身极简 | 需学习 ORM 概念（会话、钩子、关联标签） |
| **性能特征** | 无运行时反射开销，生成代码即普通 Go 代码 | 有运行时反射与对象开销，可通过配置缓解 |
| **Codegen 负担** | 需要在构建/CI 流程中固定生成步骤 | 无 codegen，即写即用 |
| **典型适用规模** | 查询相对固定、SQL 复杂度高的系统（报表、分析、遗留库） | 业务模型复杂、增删改频繁的 CRUD 应用 |

## 💡 示例

同一个需求「按城市查询成年用户」的两种写法：

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
| 高性能、低反射开销敏感 | sqlc | 生成代码即普通代码 |
| 团队熟悉 Rails/Django 式 ORM 习惯 | GORM | 心智模型迁移成本最低 |

一句话结论：**把 SQL 当资产选 sqlc，把模型当资产选 GORM；两者混用（CRUD 用 GORM、复杂查询用 sqlc）在工程上完全成立。**

## ⚠️ 常见陷阱

- ❌ **错误做法**：sqlc 生成的代码手改后再次运行生成被覆盖。
- ✅ **正确做法**：生成目录纳入 `.gitignore` 或标注"勿改"，把 codegen 固定进 Makefile/CI。
- ❌ **错误做法**：GORM 循环中逐条查询关联数据。
- ✅ **正确做法**：用 `Preload` 一次性预加载，避免 N+1。
- ❌ **错误做法**：把 `AutoMigrate` 当作生产环境的迁移方案。
- ✅ **正确做法**：生产使用版本化迁移工具，schema 变更可审查、可回滚。
- ❌ **错误做法**：在 `Where("...")` 里拼用户输入字符串。
- ✅ **正确做法**：一律使用参数占位符 `?`，两者皆然。

## 🔗 相关条目

- 📄 **[GORM ORM 速查](./02-gorm-orm.md)** - ORM-first 模型的完整字典
- 📄 **[路由器选型对比](./04-router-selection.md)** - 同系列的 Web 层选型条目
- 📄 **[GORM 完整教程](../../frameworks/03-gorm-orm-complete.md)** - 操作指南层
- 📄 **[Go 标准库核心 API](../library-guides/01-go-standard-library.md)** - `database/sql` 底层接口
- 🌐 **[sqlc 官方文档](https://docs.sqlc.dev/)** - 权威来源
- 🌐 **[GORM 官方文档](https://gorm.io/zh_CN/docs/)** - 权威来源

---

*最后更新: 2026年09月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
