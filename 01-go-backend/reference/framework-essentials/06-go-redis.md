# go-redis（Redis Go 客户端）速查

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

`go-redis` 是 Redis 官方维护的 Go 客户端：一个 `Client` 对应一个连接池，方法名与 Redis 命令一一对应，所有方法接收 `context` 并返回 `*Cmd` 系列，`Err()`/`Result()` 拆出错误与值。v9 系列统一支持 RESP3、客户端可从单一 import 路径 `github.com/redis/go-redis/v9` 使用。

```bash
go get github.com/redis/go-redis/v9
```

## 📖 语法 / 签名

```go
import (
    "github.com/redis/go-redis/v9"
)

rdb := redis.NewClient(&redis.Options{
    Addr:     "localhost:6379", // 地址
    Password: "",               // 密码（无则留空）
    DB:       0,                // 逻辑库编号
})
defer rdb.Close()

rdb.Set(ctx, key, value, ttl)            // 写字符串键
rdb.Get(ctx, key)                        // 读字符串键 → *StringCmd
rdb.Del(ctx, keys...)                    // 删除
rdb.Exists(ctx, key)                     // 存在性检查
rdb.Expire(ctx, key, ttl)                // 设置过期
rdb.HSet(ctx, key, field, value)         // 哈希
rdb.LPush / rdb.RPop(ctx, key, vals...)  // 列表
rdb.SAdd / rdb.SMembers(ctx, key, ...)   // 集合
rdb.ZAdd / rdb.ZRange(ctx, key, ...)     // 有序集合
rdb.Publish / rdb.Subscribe(ctx, ...)    // 发布订阅
rdb.Pipelined(ctx, func(pipe redis.Pipeliner) error { ... }) // 管道批量
rdb.TxPipelined(...)                     // 事务管道（MULTI/EXEC）
```

| 方法/类型 | 签名要点 | 说明 |
|-----------|---------|------|
| `NewClient` | `func(opts *Options) *Client` | 内置连接池；单例复用，勿按请求创建 |
| `cmd.Result()` | `(T, error)` | 一步取出值与错误；`cmd.Err()` 只取错误 |
| `redis.Nil` | 错误常量 | 键不存在时 `Get` 返回它，需与真实错误区分 |
| `Pipeliner` | 接口 | 攒一批命令一次网络往返，显著降延迟 |
| `Options` | 结构体 | `PoolSize`、`DialTimeout`、`ReadTimeout` 等池化参数 |

## 💡 示例

```go
package main

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
)

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	rdb := redis.NewClient(&redis.Options{Addr: "localhost:6379"})
	defer rdb.Close()

	if err := rdb.Ping(ctx).Err(); err != nil { // 确认可达
		panic(err)
	}

	// 字符串：带过期时间的写入
	if err := rdb.Set(ctx, "session:u1", "token-abc", 30*time.Minute).Err(); err != nil {
		panic(err)
	}

	// 读取：区分"键不存在"与真实错误
	token, err := rdb.Get(ctx, "session:u1").Result()
	switch {
	case errors.Is(err, redis.Nil):
		fmt.Println("会话已过期")
	case err != nil:
		panic(err)
	default:
		fmt.Println("token:", token)
	}

	// 管道：一次往返执行多条命令
	var hits *redis.IntCmd
	_, err = rdb.Pipelined(ctx, func(pipe redis.Pipeliner) error {
		hits = pipe.Incr(ctx, "metrics:hits")
		pipe.Expire(ctx, "metrics:hits", time.Hour)
		return nil
	})
	if err != nil {
		panic(err)
	}
	fmt.Println("hits:", hits.Val())
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：把 `Get` 返回的 `redis.Nil` 当作服务故障处理。
- ✅ **正确做法**：`errors.Is(err, redis.Nil)` 单独分支表示"键不存在"，是正常业务态。
- ❌ **错误做法**：每个请求 `NewClient` 一次。
- ✅ **正确做法**：应用生命周期内复用单例 Client；连接池参数按并发量配置。
- ❌ **错误做法**：`Set` 不传 TTL，缓存键永不过期。
- ✅ **正确做法**：缓存场景一律给 TTL；确需持久键时显式注释原因。
- ❌ **错误做法**：循环里逐条执行命令，网络往返次数与数据量成正比。
- ✅ **正确做法**：`Pipelined` 攒批；需要原子性时用 `TxPipelined` 或 Lua 脚本。
- ❌ **错误做法**：`Subscribe` 后不处理消息通道关闭与错误。
- ✅ **正确做法**：遍历 `pubsub.Channel()`，配合 `context` 控制订阅生命周期。
- ❌ **错误做法**：用 Redis 存大于几百 KB 的大值（大 key 阻塞单线程）。
- ✅ **正确做法**：大对象拆分、压缩或改存对象存储，Redis 只存引用。

## 🔗 相关条目

- 📄 **[go-redis 完整教程](../../frameworks/05-go-redis-complete.md)** - 操作指南层
- 📄 **[MongoDB Go Driver 速查](./05-mongo-driver.md)** - 同为数据访问客户端的姊妹条目
- 📄 **[Go 并发基础](../language-concepts/08-concurrency-basics.md)** - context 超时与取消的底层语义
- 📄 **[Go 错误处理](../language-concepts/07-error-handling.md)** - `errors.Is` 判定 `redis.Nil` 的语法基础
- 🌐 **[go-redis 官方仓库](https://github.com/redis/go-redis)** - 权威来源

---

*最后更新: 2026年09月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
