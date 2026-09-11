# MongoDB Go Driver（官方驱动）速查

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

`mongo-go-driver` 是 MongoDB 官方 Go 驱动：通过一个长连接 `Client` 派生 `Database` 与 `Collection` 句柄，用 BSON 编解码文档，以 `context` 控制每次操作的超时与取消。适合文档型数据、灵活 schema 与聚合查询场景。

```bash
go get go.mongodb.org/mongo-driver/v2/mongo
```

## 📖 语法 / 签名

```go
import (
    "go.mongodb.org/mongo-driver/v2/mongo"
    "go.mongodb.org/mongo-driver/v2/mongo/options"
)

client, err := mongo.Connect(options.Client().ApplyURI(uri)) // 建立客户端
defer client.Disconnect(ctx)                                 // 进程退出前断开

db := client.Database("app")           // 数据库句柄（惰性创建）
col := db.Collection("users")          // 集合句柄（惰性创建）

col.InsertOne(ctx, doc)                             // 插入
col.InsertMany(ctx, docs)                           // 批量插入
col.FindOne(ctx, filter).Decode(&result)            // 查询单条
cursor, err := col.Find(ctx, filter)                // 查询多条 → 游标
col.UpdateOne(ctx, filter, update)                  // 更新
col.DeleteOne(ctx, filter)                          // 删除
col.CountDocuments(ctx, filter)                     // 计数
```

| 方法/对象 | 签名要点 | 说明 |
|-----------|---------|------|
| `mongo.Connect` | `func(opts ...*options.ClientOptions) (*Client, error)` | 返回即用；配合 `Ping` 确认可达 |
| `filter` | `bson.M` / `bson.D` / 结构体 | `D` 保序，构建 `$and` 等复合条件时优先用 |
| `FindOne` | 返回 `*SingleResult` | 未命中时 `Decode` 返回 `mongo.ErrNoDocuments` |
| `Find` | 返回 `*mongo.Cursor` | `cursor.All` 或 `cursor.Next` + `Decode` 消费 |
| `options.Find()` | `.SetLimit` `.SetSort` `.SetSkip` | 链式设置排序/分页 |
| 结构体 tag | `bson:"field_name,omitempty"` | 控制 BSON 字段映射与忽略 |

## 💡 示例

```go
package main

import (
	"context"
	"fmt"
	"time"

	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
)

type User struct {
	ID    bson.ObjectID `bson:"_id,omitempty"`
	Name  string        `bson:"name"`
	Email string        `bson:"email"`
	Age   int           `bson:"age"`
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(options.Client().ApplyURI("mongodb://localhost:27017"))
	if err != nil {
		panic(err)
	}
	defer client.Disconnect(context.Background())

	if err := client.Ping(ctx, nil); err != nil { // 确认连通性
		panic(err)
	}

	col := client.Database("app").Collection("users")

	// 插入
	res, err := col.InsertOne(ctx, User{Name: "Ada", Email: "ada@example.com", Age: 30})
	if err != nil {
		panic(err)
	}
	fmt.Println("inserted:", res.InsertedID)

	// 查询多条（带过滤 + 排序）
	cursor, err := col.Find(ctx, bson.M{"age": bson.M{"$gte": 18}},
		options.Find().SetSort(bson.D{{Key: "name", Value: 1}}).SetLimit(10))
	if err != nil {
		panic(err)
	}
	var users []User
	if err := cursor.All(ctx, &users); err != nil {
		panic(err)
	}
	for _, u := range users {
		fmt.Println(u.Name, u.Email)
	}
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：`Connect` 成功就当服务可用。
- ✅ **正确做法**：启动时 `Ping` 一次验证连通性；`Connect` 只构建客户端，不会立即发现 URI 错误。
- ❌ **错误做法**：对 `FindOne` 不区分"未找到"与其他错误。
- ✅ **正确做法**：`if errors.Is(err, mongo.ErrNoDocuments) { ... }` 单独处理空结果。
- ❌ **错误做法**：用 `bson.M`（map，无序）构建依赖顺序的 `$and`/`$sort` 文档。
- ✅ **正确做法**：需要保序时用 `bson.D`（切片，按元素顺序编码）。
- ❌ **错误做法**：每个请求都 `Connect` 一次。
- ✅ **正确做法**：`Client` 连接池化，应用生命周期内复用一个实例；为每次操作传入带超时的 `context`。
- ❌ **错误做法**：忘记消费 `Find` 返回的 `Cursor`，或漏查 `cursor.Err()`。
- ✅ **正确做法**：用 `cursor.All` 一次收齐，或 `defer cursor.Close(ctx)` 并在循环后检查 `cursor.Err()`。
- ❌ **错误做法**：结构体不加 `bson` tag 依赖默认字段名。
- ✅ **正确做法**：显式声明 `bson:"snake_case"`，与 `_id`/`omitempty` 语义保持一致。

## 🔗 相关条目

- 📄 **[MongoDB Go 驱动教程](../../frameworks/04-mongodb-go-driver.md)** - 操作指南层（含聚合与事务）
- 📄 **[go-redis 速查](./06-go-redis.md)** - 同为数据访问客户端的姊妹条目
- 📄 **[Go 错误处理](../language-concepts/07-error-handling.md)** - `errors.Is` 判定驱动错误的语法基础
- 📄 **[sqlc vs GORM 选型](./03-sqlc-vs-gorm.md)** - SQL 侧的数据访问选型对照
- 🌐 **[MongoDB Go Driver 文档](https://www.mongodb.com/docs/drivers/go/current/)** - 权威来源

---

*最后更新: 2026年09月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
