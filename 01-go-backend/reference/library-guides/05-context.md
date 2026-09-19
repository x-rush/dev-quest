# context - 跨 API 的取消与超时控制

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

context 是 Go 传递**请求作用域的截止时间、取消信号与请求级数据**的标准机制。心智模型——**一棵从请求入口生长的树**：父节点取消，取消信号向派生节点传播，实际响应时刻取决于调度和执行方是否检查；每个阻塞操作（DB 查询、HTTP 调用、channel 等待）都应感知 ctx 以便"随时可中断"。

## 📖 语法 / 签名

```go
// Context 接口四个方法
type Context interface {
    Deadline() (deadline time.Time, ok bool)
    Done() <-chan struct{}   // 取消时关闭的信号 channel
    Err() error              // 取消原因：Canceled / DeadlineExceeded
    Value(key any) any       // 请求级数据
}

// 树的构造（WithCancel/WithTimeout/WithDeadline 返回 cancel；WithValue 不返回 cancel）
ctx, cancel := context.WithCancel(parent)                    // 手动取消
ctx, cancel := context.WithTimeout(parent, 5*time.Second)    // 相对截止
ctx, cancel := context.WithDeadline(parent, someTime)        // 绝对截止
ctx2 := context.WithValue(parent, key, val)                  // 携带数据

// 消费端统一模式：select 监听 Done
select {
case <-ctx.Done():
    return ctx.Err() // context.Canceled 或 context.DeadlineExceeded
case v := <-ch:
    return v
}
```

**取消传播机制**：`Done()` 返回的 channel 被关闭是广播——所有等待者都可观察到关闭，但不保证同时执行。`cancel` 是幂等的，多调无害；不调用则 ctx 及其子树在父取消前一直占内存（轻微泄漏），规范写法 `defer cancel()`。

**第一参数惯例**：context 是函数第一个参数且命名 `ctx`：`func Do(ctx context.Context, ...) error`。它是**显式的**依赖传递——不像其他语言藏在参数对象或全局变量里。

## 💡 示例

<!-- go-example: context-cancellation-seventh -->
<!-- doc-verify:go-context-cancellation -->
```go
package main

import (
	"context"
	"fmt"
	"time"
)

type userIDKey struct{} // 私有 key 类型，防跨包键冲突

func slowWork(ctx context.Context) error {
	select {
	case <-time.After(3 * time.Second): // 模拟慢操作
		return nil
	case <-ctx.Done():
		return ctx.Err() // 让出：把取消原因向上传
	}
}

func main() {
	// 1. WithTimeout：超时自动取消
	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()
	if err := slowWork(ctx); err != nil {
		fmt.Println(err) // context deadline exceeded
	}

	// 2. 手动取消：所有派生 ctx 同时收到信号
	root, rootCancel := context.WithCancel(context.Background())
	defer rootCancel()
	childA, cancelA := context.WithCancel(root)
	defer cancelA()
	childB, cancelB := context.WithCancel(root)
	defer cancelB()
	go func() {
		time.Sleep(10 * time.Millisecond)
		rootCancel()
	}()
	<-childA.Done()
	<-childB.Done() // 子 context 已取消，不代表关联工作和清理已经完成
	fmt.Println("两个子 ctx 都已取消")

	// 3. WithValue：请求级数据沿树传递
	rctx := context.WithValue(context.Background(), userIDKey{}, 42)
	fmt.Println(rctx.Value(userIDKey{})) // 42
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：把 ctx 存进 struct 字段长期持有。
- ✅ **正确做法**：ctx 只在函数参数间流转（第一参数）；struct 存 ctx 会把一次请求的生命周期错绑到长寿命对象上。
- ❌ **错误做法**：用 WithValue 传业务参数（订单号、配置项…）。
- ✅ **正确做法**：WithValue 只放请求元数据（trace ID、鉴权身份）；业务数据走显式参数，类型与意图才可读。
- ❌ **错误做法**：拿到 `ctx, cancel` 后不调用 cancel。
- ✅ **正确做法**：`defer cancel()` 无条件写上；即使 ctx 因超时自行结束，cancel 也能立即释放资源。
- ❌ **错误做法**：把 string 字面量直接做 key（`"user"`）。
- ✅ **正确做法**：定义非导出的自定义类型作 key（如 `type userIDKey struct{}`），杜绝包间冲突与意外覆盖。
- ❌ **错误做法**：自建长耗时循环却从不检查 ctx。
- ✅ **正确做法**：循环体内周期性 `select { case <-ctx.Done(): return ctx.Err(); default: }`；否则超时配置形同虚设。
- ❌ **错误做法**：在已取消的 ctx 上继续发起新请求。
- ✅ **正确做法**：检查 `ctx.Err()`；确需"脱离取消"（如审计日志必须写完）可用 `context.WithoutCancel` 保留值但去除取消与截止时间，再设置独立的有限超时；它不保证任务必达。

<!-- full-library-explanation -->
## 取消是通知，等待退出是另一件事

前置是 channel 与 goroutine。cancel 不会强制杀死正在运行的函数，也不回滚已经提交的数据库写入。它使 Done 可被观察为关闭；执行方必须响应信号，调用方还需要 WaitGroup 或结果 channel 等待清理完成。Context 可以被多个 goroutine 同时使用，但放进 Value 的 map 或指针所指对象并不会因此自动获得并发保护。

例如请求总预算 2 秒，查询数据库已经用了 1.6 秒，再派生一个 1 秒超时的子 context，剩余预算最多仍为父请求的约 0.4 秒。若用 Background 创建新根节点，就切断了父取消与截止时间的传播。向下调用优先传现有 ctx，在真正独立的任务入口才建立新根。

练习：给 slowWork 加一个清理完成 channel，在收到 Done 后先清理再关闭该 channel。主函数先 cancel，再等完成信号，确认打印“取消请求”与“清理完成”不是同一个事件。若需求是可靠发送审计记录，进程内 goroutine 即使使用 WithoutCancel 也可能因进程退出丢失；持久化队列或事务 outbox 才能承载跨进程重试的职责。

## 🔗 相关条目

- 📄 **[net/http 包](./03-net-http.md)** - NewRequestWithContext 全流程
- 📄 **[database/sql 包](./07-database-sql.md)** - QueryContext/ExecContext
- 📄 **[channel 语义](../language-concepts/12-channel-semantics.md)** - Done channel 与 select
- 📄 **[sync 包](./06-sync.md)** - 取消场景下的 goroutine 等待
- 🌐 **[Go Concurrency Patterns: Context（官方博客）](https://go.dev/blog/context)** - 权威来源
- 🌐 **[pkg.go.dev/context](https://pkg.go.dev/context)** - 官方文档

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
