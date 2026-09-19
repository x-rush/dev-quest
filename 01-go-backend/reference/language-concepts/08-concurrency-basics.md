# Go 并发基础（goroutine / channel / select / sync）

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

Go 的并发模型围绕三组原语：

- **goroutine**：由 Go 运行时调度的轻量级执行单元，`go` 关键字即可启动；相比操作系统线程，创建与切换成本极低，成千上万个并存是常态。
- **channel**：goroutine 之间传递值的类型化管道，"通过通信共享内存，而不是通过共享内存通信"。
- **sync 包**：当确实需要共享内存时的同步工具箱（`WaitGroup`、`Mutex`、`Once` 等）。

`select` 则用于在多个 channel 操作上做就绪选择，是编写多路复用逻辑的核心语法。

## 📖 语法 / 签名

```go
go f(x)                       // 启动 goroutine，无返回值、无 join 语义

ch := make(chan T)            // 无缓冲：发送阻塞直到有人接收
ch := make(chan T, n)         // 有缓冲：缓冲未满时不阻塞发送
ch <- v                       // 发送
v := <-ch                     // 接收
v, ok := <-ch                 // ok=false 表示 channel 已关闭且取空
close(ch)                     // 由发送方关闭；只发不收方负责
for v := range ch { ... }     // 持续接收直到 channel 关闭

select {                      // 多路复用：哪个 case 就绪走哪个
case v := <-ch1: ...
case ch2 <- x: ...
default: ...                  // 无 default 时阻塞等待
}

var wg sync.WaitGroup         // 等待一组 goroutine 结束
wg.Add(1); wg.Done(); wg.Wait()

var mu sync.Mutex             // 互斥锁保护共享数据
mu.Lock(); defer mu.Unlock()
```

| 元素 | 类型 | 说明 |
|------|------|------|
| `chan T` | 类型 | 双向；`chan<- T` 只发送，`<-chan T` 只接收 |
| `close(ch)` | 内置函数 | 只能关闭一次；向已关闭 channel 发送会 panic |
| `sync.WaitGroup` | 结构体 | 计数器语义：Add 在启动前、Done 在 goroutine 内 defer |
| `sync.Mutex` | 结构体 | 首次使用后不可复制；通常通过指针传递 |

## 💡 示例

```go
package main

import (
	"fmt"
	"sync"
)

func main() {
	results := make(chan int, 3)      // 有缓冲：先收集结果再等完成
	var wg sync.WaitGroup

	for _, id := range []int{1, 2, 3} {
		wg.Add(1)
		go func(n int) {              // 参数传值，避免闭包共享循环变量歧义
			defer wg.Done()
			results <- n * 10
		}(id)
	}

	go func() { wg.Wait(); close(results) }() // 收集完成后关闭

	for v := range results {          // range 到关闭为止
		fmt.Println(v)
	}
}
```

### 可复现验收：等待、关闭与接收

goroutine 的完成顺序没有保证，因此不要以逐行打印的顺序验收并发程序。下面的程序让工作 goroutine 把值写入 channel，由单独的 goroutine 在 `Wait` 返回后关闭它；主 goroutine 完整接收后排序。固定输出证明三件事：三项任务都完成、接收循环因关闭而退出、没有依赖调度顺序。

<!-- doc-verify:go-concurrency-collect-close -->
```go
package main

import (
	"fmt"
	"sort"
	"sync"
)

func main() {
	results := make(chan int, 3)
	var wg sync.WaitGroup

	for _, id := range []int{1, 2, 3} {
		wg.Add(1)
		go func(n int) {
			defer wg.Done()
			results <- n * 10
		}(id)
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	values := make([]int, 0, 3)
	for value := range results {
		values = append(values, value)
	}
	sort.Ints(values)
	fmt.Println(values)
}
```

预期输出：

```text
[10 20 30]
```

带超时的多路复用：

```go
select {
case v := <-dataCh:
    use(v)
case <-time.After(2 * time.Second):
    return fmt.Errorf("等待数据超时")
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：for 循环里直接 `go func() { use(i) }()` 并假设每次闭包拿到当次循环值。
- ✅ **正确做法**：`go func(n int){...}(i)` 显式传参（或使用循环内局部副本），可明确传入本次值。Go 1.22 起，采用新语言版本且在循环中声明的迭代变量具有逐次独立语义；循环外声明再赋值则不同。
- ❌ **错误做法**：从不关闭 channel，接收方的 `range` 永不结束。
- ✅ **正确做法**：由发送方在"不会再发"时 `close(ch)`，一条管道一个关闭者。
- ❌ **错误做法**：`wg.Done()` 忘记 defer，goroutine 提前 return 导致 Wait 永久阻塞；未 recover 的 goroutine panic 更严重——直接终止整个程序。
- ✅ **正确做法**：进入 goroutine 第一行 `defer wg.Done()`。
- ❌ **错误做法**：向已关闭的 channel 发送、或对 nil channel 收发（永久阻塞）。
- ✅ **正确做法**：发送责任方唯一化；nil channel 只应出现在 select 中用于禁用分支。
- ❌ **错误做法**：用 `time.Sleep` 等待 goroutine 完成。
- ✅ **正确做法**：用 `WaitGroup`、channel 信号或 `context` 取消来同步生命周期。
- ❌ **错误做法**：认为并发安全 = 加锁越多越好。
- ✅ **正确做法**：优先用 channel 归属权转移（同一时刻只有一个 goroutine 持有数据），锁只保护确需共享的状态；用 `-race` 检测数据竞争。

<!-- full-library-explanation -->
## 等待完成、取消工作、保护共享数据

前置是函数、channel 和指针。这三件事需要分开：WaitGroup 等待任务结束，context 提供取消信号，Mutex 保护共享不变量。调用 cancel 并不代表 goroutine 已经退出；任务必须检查信号并自行返回，调用方必要时继续等待确认结束。

运行本页完整程序，验收收到 10、20、30 各一次，并且循环正常结束；不要断言打印顺序。练习把 results 的缓冲从 3 改成 0，当前“独立 goroutine 等待并关闭、主 goroutine 持续接收”的结构仍应完成；若把 Wait 直接放到接收之前，则可能互相等待。

再增加提前取消的消费者，检查生产者的发送是否也能退出。无界启动任务、没有接收者的发送和跨 goroutine 共享切片，分别涉及资源上限、生命周期与数据竞争，不能用“Go 并发轻量”忽略这些成本。

## 🔗 相关条目

- 📄 **[Go 错误处理](./07-error-handling.md)** - 并发任务中的错误传播模式
- 📄 **[Go 关键字详解](./01-go-keywords.md)** - `go`/`chan`/`select` 关键字语法
- 📄 **[高级并发模式](../../advanced-topics/performance/01-concurrency-patterns.md)** - worker pool、fan-in/out 等深度解释
- 📄 **[Go 标准库核心 API](../library-guides/01-go-standard-library.md)** - `sync`/`context` 包全解
- 🌐 **[Go 并发模式（官方博客）](https://go.dev/blog/pipelines)** - 权威来源

---

*最后更新: 2026年09月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
