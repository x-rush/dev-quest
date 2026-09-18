# go-redis 客户端完整学习指南

## 先看框架承担哪部分职责

**Redis**：Redis 中保存的通常是派生副本或明确设计的状态。缓存键、失效与 TTL 是正确性契约，而不是只调用 GET/SET。

**最小练习与预期结果**：写入一个带 TTL 的测试键，过期后应回源或报告缺失；缓存不可用时观察主流程是否按设计降级。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 掌握go-redis客户端的使用，学会在Go应用中高效使用Redis进行缓存、消息队列等操作
>
> **字典速查**: [go-redis 速查](../reference/framework-essentials/06-go-redis.md) - 概念与API的字典级定义以此处为单一事实来源
>
> **目标读者**: 具备Go基础和Redis基础知识的开发者
>
> **前置知识**: Go语言基础、Redis基础概念、数据结构基础
>
> **预计时长**: 3-4小时学习 + 2小时实践

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `frameworks/cache-database` |
| **难度** | ⭐⭐⭐ (3/5) |
| **标签** | `#Redis` `#缓存` `#go-redis` `#消息队列` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | 📋 计划中 |

</details>

## 🎯 学习目标

通过本文档学习，您将能够：

1. **掌握go-redis基础**
   - 连接Redis服务器
   - 执行基本的缓存操作
   - 理解Redis数据结构

2. **学习高级用法**
   - 发布订阅模式
   - 分布式锁实现
   - 管道和事务

3. **实践最佳实践**
   - 连接池管理
   - 错误处理
   - 性能优化

## 📋 内容大纲

### 1. go-redis基础
- [ ] 安装和配置
- [ ] 连接Redis服务器
- [ ] 基本数据操作
- [ ] 连接池管理

### 2. 数据结构操作
- [ ] String操作
- [ ] Hash操作
- [ ] List操作
- [ ] Set操作
- [ ] Sorted Set操作

### 3. 高级特性
- [ ] 发布订阅
- [ ] 事务处理
- [ ] 管道操作
- [ ] Lua脚本

### 4. 应用模式
- [ ] 缓存模式
- [ ] 分布式锁
- [ ] 限流器
- [ ] 会话存储

### 5. 性能优化
- [ ] 连接优化
- [ ] 批量操作
- [ ] 内存管理
- [ ] 监控和调试

## 🛠️ 代码示例

### 基础操作示例
```go
package main

import (
    "context"
    "fmt"
    "github.com/redis/go-redis/v9"
)

func main() {
    // 创建Redis客户端
    rdb := redis.NewClient(&redis.Options{
        Addr:     "localhost:6379",
        Password: "", // 无密码
        DB:       0,  // 使用默认DB
    })

    ctx := context.Background()

    // 测试连接
    err := rdb.Ping(ctx).Err()
    if err != nil {
        panic(err)
    }

    // 设置键值
    err = rdb.Set(ctx, "key", "value", 0).Err()
    if err != nil {
        panic(err)
    }

    // 获取值
    val, err := rdb.Get(ctx, "key").Result()
    if err != nil {
        panic(err)
    }

    fmt.Println("key:", val)
}
```

## 🔗 相关资源

- **前置学习**: [reference/library-guides/02-third-party-libs.md](../reference/library-guides/02-third-party-libs.md)
- **相关文档**: [frameworks/01-gin-framework-basics.md](01-gin-framework-basics.md)
- **实践项目**: [projects/02-microservices-demo.md](../projects/02-microservices-demo.md)

---

**注意**: 本文档正在完善中，内容会持续更新。欢迎贡献反馈和建议！


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
