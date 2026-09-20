# MongoDB Go 驱动完整学习指南

## 先看框架承担哪部分职责

**MongoDB Driver**：文档数据库以文档存储，但 schema、索引与更新原子性仍要设计。驱动负责通信，不能从返回了对象推断写入约束正确。

**最小练习与预期结果**：使用固定测试集合插入、按 ID 查询和更新一个字段；未知 ID 明确表示未找到，不能当网络失败。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 掌握MongoDB官方Go驱动(mongo-go-driver)的使用，学会在Go应用中高效操作MongoDB数据库
>
> **目标读者**: 具备Go基础和MongoDB基础知识的开发者
>
> **前置知识**: Go语言基础、MongoDB基础概念、数据结构基础
>
> **预计时长**: 3-4小时学习 + 2小时实践

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `frameworks/document-database` |
| **难度** | ⭐⭐⭐ (3/5) |
| **标签** | `#MongoDB` `#NoSQL` `#文档数据库` `#mongo-go-driver` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 基础路径已完成；服务端练习待读者环境执行 |

</details>

## 🎯 学习目标

通过本文档学习，您将能够：

1. **掌握MongoDB Go驱动基础**
   - 连接MongoDB数据库
   - 执行基本的CRUD操作
   - 理解BSON数据格式

2. **学习高级操作**
   - 复杂查询和聚合操作
   - 索引创建和优化
   - 事务处理

3. **实践最佳实践**
   - 连接池管理
   - 错误处理
   - 性能优化

## 📋 内容大纲

### 1. MongoDB Go驱动基础
- [ ] 安装和配置
- [ ] 数据库连接管理
- [ ] BSON数据处理
- [ ] 基本CRUD操作

### 2. 查询操作
- [ ] 基本查询
- [ ] 条件查询
- [ ] 排序和分页
- [ ] 聚合管道

### 3. 数据建模
- [ ] 文档结构设计
- [ ] 嵌入文档vs引用
- [ ] 数组操作
- [ ] 数据类型映射

### 4. 高级特性
- [ ] 索引管理
- [ ] 文本搜索
- [ ] 地理空间查询
- [ ] 事务处理

### 5. 性能优化
- [ ] 查询优化
- [ ] 索引策略
- [ ] 连接池配置
- [ ] 批量操作

## 🛠️ 代码示例

> **驱动版本说明**：官方驱动当前主线为 v2（导入路径 `go.mongodb.org/mongo-driver/v2/...`），v1 路径已进入维护模式，新项目请使用：
>
> ```bash
> go get go.mongodb.org/mongo-driver/v2/mongo
> ```
>
> 下方示例均按 v2 API 编写（`Connect` 不再接收 `context` 参数）。字典级速查见 [MongoDB Go Driver 速查](../reference/framework-essentials/05-mongo-driver.md)。

### 基础连接示例
```go
package main

import (
    "context"
    "fmt"
    "go.mongodb.org/mongo-driver/v2/mongo"
    "go.mongodb.org/mongo-driver/v2/mongo/options"
)

func main() {
    // 连接到MongoDB（v2 起 Connect 不再接收 context 参数）
    client, err := mongo.Connect(options.Client().ApplyURI("mongodb://localhost:27017"))
    if err != nil {
        panic(err)
    }
    defer client.Disconnect(context.Background())

    // 选择数据库和集合
    collection := client.Database("testdb").Collection("users")

    // 插入文档
    result, err := collection.InsertOne(context.Background(), map[string]interface{}{
        "name":  "John Doe",
        "email": "john@example.com",
        "age":   30,
    })
    if err != nil {
        panic(err)
    }

    fmt.Printf("Inserted document with ID: %v\n", result.InsertedID)
}
```

上面的代码说明 API 形状，不应直接作为应用入口：它没有连接超时、健康检查、关闭错误的处理，也把数据写进固定名称的数据库。下面从一个可替换的连接构造开始。

## 1. 连接、生命周期与超时

`mongo.Client` 管理连接池，通常在进程启动时创建一个，并在进程退出时关闭；不要每个 HTTP 请求都 `Connect`。连接对象创建成功不代表服务器可用，因此启动检查使用 `Ping`。连接、每次数据库操作都应有自己的超时；请求取消时应把请求的 `context.Context` 向下传递，而不是改成 `context.Background()`。

```go
package store

import (
	"context"
	"fmt"
	"time"

	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
	"go.mongodb.org/mongo-driver/v2/mongo/readpref"
)

func Connect(ctx context.Context, uri string) (*mongo.Client, error) {
	connectCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	client, err := mongo.Connect(options.Client().ApplyURI(uri))
	if err != nil {
		return nil, fmt.Errorf("create MongoDB client: %w", err)
	}
	if err := client.Ping(connectCtx, readpref.Primary()); err != nil {
		_ = client.Disconnect(context.Background())
		return nil, fmt.Errorf("ping MongoDB: %w", err)
	}
	return client, nil
}
```

应用入口负责在收到停止信号后调用 `Disconnect`。业务层只接收 `*mongo.Collection` 或更小的仓储接口；这样单元测试可用内存替身，集成测试才需要真实 MongoDB。URI 内的用户名、密码和副本集参数属于部署配置，不能写进源码或日志。

## 2. BSON 模型与字段契约

MongoDB 存储 BSON，不是 Go 结构体的原样内存表示。为稳定字段名写出 `bson` 标签；`omitempty` 会让零值字段不写入，这适合“可选字段”，却不适合必须区分 `false`、`0`、空字符串与缺失字段的业务。`_id` 常用 `bson.ObjectID`，由应用生成或由驱动在插入时生成。

```go
package store

import (
	"time"

	"go.mongodb.org/mongo-driver/v2/bson"
)

type Todo struct {
	ID        bson.ObjectID `bson:"_id,omitempty"`
	OwnerID   bson.ObjectID `bson:"owner_id"`
	Title     string        `bson:"title"`
	Done      bool          `bson:"done"`
	Labels    []string      `bson:"labels,omitempty"`
	CreatedAt time.Time     `bson:"created_at"`
	UpdatedAt time.Time     `bson:"updated_at"`
}
```

文档数据库允许同一集合存在不同形状的文档，不等于应用可以忽略约束。写入前仍需检查标题、所有者和状态迁移；集合验证规则、唯一索引和应用校验各保护不同边界。读取旧文档时要考虑新增字段不存在的兼容路径。

## 3. 创建、查询与“未找到”

以下函数是放入前述 `store` package 的业务片段；需要导入 `errors`、`fmt`、`time`、`bson` 和 `mongo`，并声明 `var ErrTodoNotFound = errors.New("todo not found")`。它们假定调用者已经取得集合，并把 `ctx` 传入。过滤条件使用 `bson.D` 或 `bson.M` 的值绑定，不要把用户输入拼成 JSON/查询字符串。`FindOne` 找不到文档会在 `Decode` 时返回 `mongo.ErrNoDocuments`；这不是网络故障，也不应被转换为空的成功对象。

```go
func CreateTodo(ctx context.Context, todos *mongo.Collection, todo Todo) (Todo, error) {
	todo.ID = bson.NewObjectID()
	now := time.Now().UTC()
	todo.CreatedAt, todo.UpdatedAt = now, now
	if _, err := todos.InsertOne(ctx, todo); err != nil {
		return Todo{}, fmt.Errorf("insert todo: %w", err)
	}
	return todo, nil
}

func FindTodo(ctx context.Context, todos *mongo.Collection, ownerID, id bson.ObjectID) (Todo, error) {
	var todo Todo
	err := todos.FindOne(ctx, bson.D{{Key: "_id", Value: id}, {Key: "owner_id", Value: ownerID}}).Decode(&todo)
	if errors.Is(err, mongo.ErrNoDocuments) {
		return Todo{}, ErrTodoNotFound
	}
	if err != nil {
		return Todo{}, fmt.Errorf("find todo: %w", err)
	}
	return todo, nil
}
```

这里的 `owner_id` 同时是授权边界：已经登录不意味着可以按任意 `_id` 读取文档。`ErrTodoNotFound` 是应用定义的稳定错误，例如 `var ErrTodoNotFound = errors.New("todo not found")`；HTTP 层可按它映射为 404，而不会把底层驱动错误文本直接发送给客户端。

## 4. 列表与 cursor 必须关闭

`Find` 返回 cursor。无论全部读取、提前返回还是解码失败，都要关闭 cursor；长列表还应限制返回条数并使用稳定排序。下例继续使用前一节的 `store` package、`fmt`、`bson`、`mongo` 与 `options` 导入，一次最多取 50 条，足以说明资源边界；更大的列表应采用基于已排序字段的游标分页，而不是无限增大的 `skip`。

```go
func ListOpenTodos(ctx context.Context, todos *mongo.Collection, ownerID bson.ObjectID) ([]Todo, error) {
	limit := int64(50)
	cursor, err := todos.Find(
		ctx,
		bson.D{{Key: "owner_id", Value: ownerID}, {Key: "done", Value: false}},
		options.Find().SetSort(bson.D{{Key: "created_at", Value: -1}}).SetLimit(limit),
	)
	if err != nil {
		return nil, fmt.Errorf("find open todos: %w", err)
	}
	defer cursor.Close(ctx)

	var result []Todo
	if err := cursor.All(ctx, &result); err != nil {
		return nil, fmt.Errorf("decode todo cursor: %w", err)
	}
	return result, nil
}
```

## 5. 更新、删除与并发语义

更新操作的过滤条件必须同时表达“更新哪条记录”和“谁有权更新”。下例继续使用前一节相同的 package 与导入。`MatchedCount == 0` 表示没有匹配文档，不等同于更新后字段没有变化；`ModifiedCount == 0` 可能只是新值与旧值相同。不要使用无过滤条件的 `UpdateMany` 或 `DeleteMany` 处理用户输入。

```go
func MarkDone(ctx context.Context, todos *mongo.Collection, ownerID, id bson.ObjectID) error {
	result, err := todos.UpdateOne(
		ctx,
		bson.D{{Key: "_id", Value: id}, {Key: "owner_id", Value: ownerID}},
		bson.D{{Key: "$set", Value: bson.D{{Key: "done", Value: true}, {Key: "updated_at", Value: time.Now().UTC()}}}},
	)
	if err != nil {
		return fmt.Errorf("mark todo done: %w", err)
	}
	if result.MatchedCount == 0 {
		return ErrTodoNotFound
	}
	return nil
}
```

单个文档的一次更新具有原子性，但“读—判断—再写”跨多次操作仍可能发生竞争。需要确保状态尚未改变时，把预期状态也放入过滤条件；涉及多个文档或集合的一致性时，才评估事务、失败重试和幂等键。事务不是每个 CRUD 的默认配置，它会增加延迟和运维条件。

## 6. 索引从查询形状推导

索引不是“给每个字段加一个”。先写出最常用的过滤、排序和唯一性要求，再用 `explain` 和真实数据规模确认。对于上面的“某用户的未完成待办按创建时间倒序”查询，可以从复合索引开始；字段顺序应随等值过滤、排序方式与数据分布复核。

```go
_, err := todos.Indexes().CreateOne(ctx, mongo.IndexModel{
	Keys: bson.D{{Key: "owner_id", Value: 1}, {Key: "done", Value: 1}, {Key: "created_at", Value: -1}},
})
if err != nil {
	return fmt.Errorf("create todo list index: %w", err)
}
```

索引会占用磁盘并增加写入成本；唯一索引会在并发写入时由数据库强制约束，不能只在 Go 代码中先查再插。集合验证、索引创建、备份和迁移属于部署演练：应在隔离数据库中记录版本、样本数据、失败场景和回滚方式。

## 7. 学习练习与验收

1. **本地或容器 MongoDB**：用单独的测试数据库和随机集合名运行 `CreateTodo`、`FindTodo`、`MarkDone`。记录驱动版本、MongoDB 版本、连接 URI 中除密码外的结构和命令。
2. **未找到与授权**：用存在的 `_id` 配上另一个用户的 `owner_id` 查询；预期得到 `ErrTodoNotFound`，而不是泄露文档内容。
3. **索引与查询**：插入足够多的不同 `owner_id` 文档，比较加索引前后 `explain` 的执行计划；提交过滤、排序、索引定义和观察结果，不只提交“已优化”。
4. **失败处理**：把操作 context 的期限设得很短，确认调用者能看到可处理的超时错误；不要把 `context.Canceled` 或 deadline 错误伪装成“查无数据”。

本仓不随文档启动 MongoDB，也不保存 URI、账号或样本生产数据。因此以上是明确的读者验收步骤，不能被写成“本机已连接 MongoDB”的运行证据。

## 🔗 相关资源

- **前置学习**: [reference/library-guides/01-go-standard-library.md](../reference/library-guides/01-go-standard-library.md)
- **相关文档**: [frameworks/03-gorm-orm-complete.md](03-gorm-orm-complete.md)
- **实践项目**: [projects/02-microservices-demo.md](../projects/02-microservices-demo.md)

---

**注意**: 本文档正在完善中，内容会持续更新。欢迎贡献反馈和建议！


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
