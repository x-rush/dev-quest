# 并发编程基础：goroutine、channel 与 sync

前置：[函数和方法](05-functions-methods.md)、[控制结构](06-control-structures.md)。本章用标准库完成“启动任务 → 传递结果 → 等待结束 → 取消任务 → 保护共享状态”。先单独保存并运行每个程序，再组合成 worker pool；不要把几个 `main` 函数放在同一个文件。

`go f()` 启动并发工作，不保证它在 `main` 返回前结束。等待任务完成和保护共享数据是不同职责：`WaitGroup` 负责前者，`Mutex` 或数据所有权转移负责后者。goroutine 使用可增长的栈，但数量、阻塞的网络连接和每个任务占用的内存仍需限制。

本文四个命名程序由[验证器](../../shared-resources/tools/document-quality/verify_go_rust_basics.py)原样抽取，以 `go build -race` 构建并比对输出；环境与范围见[报告](../../shared-resources/tools/document-quality/reports/go-rust-basics.md)。此处不包含外网性能测量。

## 1. 用 channel 收集结果，显式等待所有发送者

假设要并发计算 1、2、3 的平方，并返回总和。每个任务只拥有自己的输入，通过 channel 交付结果；主 goroutine 是唯一累加者，因此不需要锁。

<!-- verified-case: go-concurrency-results -->
```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    results := make(chan int)
    var wg sync.WaitGroup
    for i := 1; i <= 3; i++ {
        wg.Add(1) // 在启动之前增加，防止 Wait 看见零而提前返回
        go func(n int) {
            defer wg.Done()
            results <- n * n
        }(i)
    }
    go func() {
        wg.Wait()
        close(results) // 所有发送者结束后，由协调者关闭
    }()
    total := 0
    for value := range results {
        total += value
    }
    fmt.Println(total)
}
```

预期输出：

```text
14
```

这里不能先在主 goroutine 中 `wg.Wait()` 再接收：无缓冲 channel 的发送必须等到接收方，任务不完成，Wait 也不完成。单独的协调 goroutine 等待计数归零；主 goroutine 同时持续接收。结果到达顺序未规定，整数求和不受顺序影响。

`WaitGroup` 首次使用后不能复制。传给其他函数时通常使用 `*sync.WaitGroup`；也可以像示例那样闭包引用同一个变量。只有所有调用 `Done` 的任务确实结束，Wait 才能完成。Go 1.25 起还提供 `WaitGroup.Go`，但传入函数不能 panic；这里保留 `Add`/`Done` 以展示计数关系。

### 循环变量：版本和声明方式都重要

Go 1.22 语言语义下，`for i := ...` 或 `for _, v := range ...` 声明的循环变量每轮新建；通常由模块 `go.mod` 的 `go` 指令决定。对循环外变量赋值的 `for i = ...` 不适用此规则。旧语义下捕获共享变量可能读到不同值并产生数据竞争，不能保证某个固定输出。

示例显式把 `i` 作为参数传入，传参在启动语句处求值，因此也适用于旧语义。这不保证调度次序，也不保护循环体捕获的其他共享对象。

## 2. channel 的缓冲、关闭与单向类型

| 操作 | 未关闭、非 nil channel | 已关闭 channel | nil channel |
|---|---|---|---|
| 发送 | 无缓冲时等待接收；缓冲满时等待 | panic | 永久阻塞 |
| 接收 | 空且没有发送者时等待 | 先取缓冲值，再返回零值和 `false` | 永久阻塞 |
| `close` | 宣告不再发送；不会等待消费者处理结束 | panic | panic |

没有配对的收发会阻塞。只有运行时检测到整个程序无法继续推进时，才可能报告全局死锁；服务里仍有其他活动任务时，一个泄漏的 goroutine 可以一直挂住，没有自动报错。

<!-- verified-case: go-concurrency-channel -->
```go
package main

import "fmt"

func produce(out chan<- int) {
    out <- 7
    close(out)
}

func main() {
    values := make(chan int, 1)
    produce(values) // 缓冲能容纳一次发送，因此本例不需要 goroutine
    first, ok1 := <-values
    second, ok2 := <-values
    fmt.Println(first, ok1)
    fmt.Println(second, ok2)
    var disabled <-chan int
    select {
    case <-disabled:
        panic("nil channel cannot become ready")
    default:
        fmt.Println("no ready channel")
    }
}
```

预期输出：

```text
7 true
0 false
no ready channel
```

`chan<- T` 限定发送，`<-chan T` 限定接收，帮助编译器发现误用。关闭责任属于能证明“以后没人发送”的一方；单生产者通常自己关闭，多生产者通常用第一例的协调者。`sync.Once` 只能避免重复关闭，不能防止关闭与发送并发导致 panic。channel 无需为了释放内存而关闭；close 的用途是协议通知。

`select` 在多个已就绪分支之间伪随机选择，不保证严格轮转或某个任务在有限次数内必定获选。`default` 只代表此刻没有就绪分支；放进没有阻塞的无限循环会忙等占用 CPU。

## 3. 取消不仅是停止等待，还必须让工作者退出

旧式写法“后台 sleep 后向无缓冲 channel 发送；前台 `time.After` 超时返回”会留下无人接收的发送者。取消是双方约定：调用方发出信号，任务在阻塞处观察信号，随后调用方等待清理结束。

下面为了稳定演示，主动调用 `cancel()`，再观察任务结束。真实网络请求可以用 `context.WithTimeout` 建立截止时间，并把 context 传入 `http.NewRequestWithContext`；只在外面加 select 不会取消底层 I/O。

<!-- verified-case: go-concurrency-cancel -->
```go
package main

import (
    "context"
    "fmt"
)

func produce(ctx context.Context, out chan<- int, done chan<- struct{}) {
    defer close(done)
    for n := 0; ; n++ {
        select {
        case <-ctx.Done():
            return
        case out <- n:
        }
    }
}

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()
    values := make(chan int)
    done := make(chan struct{})
    go produce(ctx, values, done)
    fmt.Println(<-values)
    cancel()
    <-done // 观察工作者实际退出，不能用 Sleep 猜测它已结束
    fmt.Println(ctx.Err())
}
```

预期输出：

```text
0
context canceled
```

本例的输出 channel 不再有人接收，所以取消后只有 `ctx.Done()` 分支可推进。一般场景里若发送和取消同时就绪，select 仍可能选择发送，因此不能声称 cancel 返回后绝不再产生一个结果。需要严格停止边界时，应设计协调协议并等待完成通知。

## 4. Mutex 保护整个共享状态约束

多个任务必须读写同一个计数器时，给每次访问使用同一把锁。不要仅锁写、不锁并发读；也不要把含已使用 Mutex 的结构体复制到另一个变量。

<!-- verified-case: go-concurrency-mutex -->
```go
package main

import (
    "fmt"
    "sync"
    "sync/atomic"
)

type Counter struct {
    mu sync.Mutex
    value int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}

func (c *Counter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.value
}

func main() {
    var counter Counter
    var atomicCounter atomic.Int64
    var wg sync.WaitGroup
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            counter.Inc()
            atomicCounter.Add(1)
        }()
    }
    wg.Wait()
    fmt.Println(counter.Value(), atomicCounter.Load())
}
```

预期输出：

```text
100 100
```

单一计数可选 `atomic.Int64`。如果约束是“余额减少的同时库存也必须减少”，对两个独立变量分别执行原子操作并不能形成整体事务，此时需将整个检查与更新放进同一临界区。

保存任一完整程序为 `main.go` 后运行 `go run -race main.go`。竞争检测器会观测本次执行，未触发的路径没有被证明无竞争；目标平台还需支持 race 工具链及 C 编译器。将无锁计数器作为独立反例时，应观察 `WARNING: DATA RACE`，不能通过“这次刚好输出 100”判断安全。

## 5. 练习与验收

| 练习 | 先实现 | 通过条件 |
|---|---|---|
| 有界 worker pool | 一个生产者、3 个 worker、100 个整数任务 | 每项恰好处理一次、结果总和 5050；只有协调者关闭结果 channel |
| 提前停止 | 消费者拿到 10 个结果后取消 | 所有生产者和 worker 都观察 context，并通过 WaitGroup 确认退出；不依赖 sleep |
| 并发缓存 | map 的读写使用同一把锁 | 测试覆盖同时读写并运行 `go test -race`；不把 WaitGroup 误当成锁 |
| 请求取消 | 使用 `httptest` 本地服务器模拟等待 | 请求截止后返回可用 `errors.Is` 判断的取消/截止错误；服务端也观察请求 context |

先写出谁拥有数据、谁发送、谁接收、谁关闭、谁取消、谁等待，再决定是否需要 channel。性能优化应在正确性和任务生命周期清楚后进行。

## 相关资料

- [Go 内存模型](https://go.dev/ref/mem)：解释哪些同步操作建立可见性关系。
- [sync 官方文档](https://pkg.go.dev/sync)：Mutex、WaitGroup 的复制与使用约束。
- [context 官方文档](https://pkg.go.dev/context)：取消是通知机制，任务需自行响应。
- [Go 1.22 循环变量语义](https://go.dev/doc/go1.22#language)。
- [Go 标准库参考](../reference/library-guides/01-go-standard-library.md)与[错误处理](08-error-handling.md)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
