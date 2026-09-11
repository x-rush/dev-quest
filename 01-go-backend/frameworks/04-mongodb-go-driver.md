# MongoDB Go 驱动完整学习指南

> **文档简介**: 掌握MongoDB官方Go驱动(mongo-go-driver)的使用，学会在Go应用中高效操作MongoDB数据库
>
> **目标读者**: 具备Go基础和MongoDB基础知识的开发者
>
> **前置知识**: Go语言基础、MongoDB基础概念、数据结构基础
>
> **预计时长**: 3-4小时学习 + 2小时实践

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `frameworks/document-database` |
| **难度** | ⭐⭐⭐ (3/5) |
| **标签** | `#MongoDB` `#NoSQL` `#文档数据库` `#mongo-go-driver` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | 📋 计划中 |

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

## 🔗 相关资源

- **前置学习**: [reference/library-guides/01-go-standard-library.md](../reference/library-guides/01-go-standard-library.md)
- **相关文档**: [frameworks/03-gorm-orm-complete.md](03-gorm-orm-complete.md)
- **实践项目**: [projects/02-microservices-demo.md](../projects/02-microservices-demo.md)

---

**注意**: 本文档正在完善中，内容会持续更新。欢迎贡献反馈和建议！
