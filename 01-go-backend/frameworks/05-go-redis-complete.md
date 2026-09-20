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
| **状态** | ✅ 基础路径已完成；服务端练习待读者环境执行 |

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

### 从一个明确的缓存契约开始

本页使用 go-redis `v9.22.0` 作为复现基线；安装时把版本写入模块，而不是让浮动依赖决定行为：

```bash
go get github.com/redis/go-redis/v9@v9.22.0
```

先决定缓存代表什么。下面的例子缓存的是可重新读取的用户资料副本，键包含实体类型和 ID，值使用 JSON，TTL 是“最多允许旧数据存在多久”。它不是会话、分布式锁或消息队列的通用模板。

```go
package main

import (
    "context"
    "encoding/json"
    "errors"
    "fmt"
    "time"

    "github.com/redis/go-redis/v9"
)

type UserProfile struct {
    ID   string `json:"id"`
    Name string `json:"name"`
}

func profileKey(id string) string { return "profile:v1:" + id }

func LoadProfile(ctx context.Context, rdb *redis.Client, id string) (UserProfile, bool, error) {
    text, err := rdb.Get(ctx, profileKey(id)).Result()
    if errors.Is(err, redis.Nil) {
        return UserProfile{}, false, nil // cache miss：由调用者回源
    }
    if err != nil {
        return UserProfile{}, false, fmt.Errorf("read profile cache: %w", err)
    }
    var profile UserProfile
    if err := json.Unmarshal([]byte(text), &profile); err != nil {
        return UserProfile{}, false, fmt.Errorf("decode profile cache: %w", err)
    }
    return profile, true, nil
}

func StoreProfile(ctx context.Context, rdb *redis.Client, profile UserProfile) error {
    encoded, err := json.Marshal(profile)
    if err != nil {
        return fmt.Errorf("encode profile cache: %w", err)
    }
    return rdb.Set(ctx, profileKey(profile.ID), encoded, 10*time.Minute).Err()
}
```

`redis.Nil` 表示 Redis 正常响应了“键不存在”，应与连接超时、认证失败和 JSON 损坏分开处理。调用者只有在业务允许回源时才把 miss 当作可恢复状态；例如权限、余额或强一致读不能默认相信缓存。

## 1. 客户端生命周期、超时与关闭

`redis.Client` 内部维护连接池，应在应用启动时构造并复用，在关闭阶段调用 `Close`。`Ping` 能检查当前连接路径，却不证明后续命令永远可用。地址、密码和 TLS 配置来自部署环境，不能硬编码在样例仓库。

```go
func NewClient(addr, password string) *redis.Client {
    return redis.NewClient(&redis.Options{
        Addr:         addr,
        Password:     password,
        DialTimeout:  2 * time.Second,
        ReadTimeout:  2 * time.Second,
        WriteTimeout: 2 * time.Second,
        PoolSize:     20, // 需按并发、Redis 容量和观测结果调整
    })
}

// 入口示意：shutdownCtx 应有自己的有限期限。
// defer client.Close() 适合小程序；长驻服务在收到停止信号后显式关闭。
```

命令使用调用方的 `context.Context`。HTTP handler 不应创建脱离请求的 `context.Background()` 来执行一次可取消的缓存操作；后台任务则应拥有自己的超时 context。不要仅为“更快”把读写超时设为无限，先记录错误率、池等待和下游延迟。

## 2. 缓存回源、失效和故障策略

缓存读取应返回三种状态：命中、正常 miss、缓存故障。业务层决定故障时的策略，而不是让缓存库暗中吞掉错误。以下伪代码展示写后失效；若主存储写入失败，绝不能先删除缓存后仍报告成功。

```text
updateProfile(id, input):
  updated = primaryStore.update(id, input)   // 先完成权威写入
  if updated fails: return error
  cache.delete(profileKey(id))               // 失败要记录，不回滚权威数据
  return updated

getProfile(id):
  value, hit, cacheErr = LoadProfile(...)
  if hit: return value
  profile = primaryStore.find(id)            // miss 或允许降级的 cacheErr 才回源
  if profile exists: StoreProfile(...)
  return profile
```

TTL、失效和版本化键要一起设计。`profile:v1:<id>` 中的版本只解决编码格式或字段含义的切换，不能代替写入后的失效；TTL 只能限制最长陈旧时间，不能保证刚写完立即可见。缓存不可用时是否回源必须受主存储容量和业务正确性约束，不能一律重试到成功。

## 3. 批量操作、Pipeline 与原子条件

Pipeline 减少多条独立命令的往返次数，但不把它们变成事务。需要“仅当余额足够才扣减”这类读写条件时，把条件和写入放在 Redis 原子操作或脚本中，并在业务层处理冲突、超时和重试；不要先 `Get`，再在另一条命令中 `Set`。

```go
pipe := rdb.Pipeline()
pipe.Set(ctx, "feature:v1:42", "enabled", time.Minute)
pipe.Incr(ctx, "metric:page-views")
commands, err := pipe.Exec(ctx)
// err 表示 pipeline 执行层错误；仍逐项检查 commands 中需要的结果。
```

事务、Lua 和分布式锁都不是“缓存的升级按钮”。锁至少需要唯一持有者令牌、有限 TTL、释放时只删除自己的键，以及临界区幂等性；跨服务正确性还取决于暂停、网络分区和主从切换。对于库存、支付和唯一写入，优先依赖权威数据库约束或专门的协调设计。

## 4. 数据结构按访问模式选择

| 需求 | 可考虑的 Redis 结构 | 先确认的边界 |
|---|---|---|
| 单个带 TTL 的缓存条目 | String | 编码格式、最大值大小、失效与回源规则 |
| 一个对象的少量独立字段 | Hash | 字段是否必须整体一致；过期作用于整个 key |
| 去重成员与集合运算 | Set | 成员大小、TTL、是否需要排序 |
| 按分数排序的排行榜 | Sorted Set | 分数精度、并列规则、清理策略 |
| 可确认的异步任务 | Stream/专业队列 | 消费组、确认、重试、积压和死信策略 |

不要因为 Redis 支持一种结构就把主数据迁过去。先问“断电、过期、淘汰或消费重复后，业务是否仍正确”。如果答案是否定的，Redis 只能保存派生状态或加速路径。

## 5. 练习与验收

1. 在隔离 Redis 容器或本地实例中写入 `profile:v1:test-user`，确认十分钟 TTL 存在；用短 TTL 的测试键验证过期后返回 `redis.Nil`。
2. 制造 JSON 损坏值，确认 `LoadProfile` 报解码错误而不是把它当作 miss；删除键后确认才是正常 miss。
3. 暂停或停止测试 Redis，观察业务入口是否按你定义的故障策略回源、报错或拒绝，而不是无限等待。
4. 给一个常用读路径写出键格式、权威数据源、TTL、失效时机、缓存故障策略和验收记录。

本仓不替读者启动或修改 Redis 服务，上述步骤是外部服务练习，不构成本机执行证据。API 用法以 [go-redis 官方 README](https://github.com/redis/go-redis#readme) 和 [Redis Go 客户端文档](https://redis.io/docs/latest/develop/clients/go/) 为准。

## 🔗 相关资源

- **前置学习**: [reference/library-guides/02-third-party-libs.md](../reference/library-guides/02-third-party-libs.md)
- **相关文档**: [frameworks/01-gin-framework-basics.md](01-gin-framework-basics.md)
- **实践项目**: [projects/02-microservices-demo.md](../projects/02-microservices-demo.md)

---

**注意**: 本文档正在完善中，内容会持续更新。欢迎贡献反馈和建议！


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
