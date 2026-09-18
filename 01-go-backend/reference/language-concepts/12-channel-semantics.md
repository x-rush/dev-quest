# channel 语义

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

channel 是 goroutine 之间的**类型安全通信管道**，遵循 CSP 模型："不要通过共享内存来通信，而要通过通信来共享内存"。核心规则是**阻塞方向**：发送与接收在什么条件下阻塞、什么条件下成功，是所有并发模式的基础。

## 📖 语法 / 签名

```go
ch := make(chan int)      // 无缓冲：发送阻塞到有接收者就绪
ch := make(chan int, 5)   // 有缓冲：缓冲满时发送才阻塞

ch <- v          // 发送
v := <-ch        // 接收（丢弃第二返回值）
v, ok := <-ch    // ok=false 表示 channel 已关闭且缓冲已空
for v := range ch { ... } // 循环接收直到 channel 关闭
close(ch)        // 由确认不再发送的责任方关闭；只能关一次

// 单向 channel：约束在类型层面，常用于函数签名
func produce(out chan<- int)   // 只能发送
func consume(in <-chan int)    // 只能接收
```

**阻塞与 panic 规则总表**（自 Go 1 起稳定语义）：

| 操作 | nil channel | 已关闭 channel | 正常 channel |
|------|-------------|----------------|--------------|
| 发送 `ch <- v` | **永久阻塞** | **panic**（send on closed channel） | 无缓冲阻塞等接收者；有缓冲满则阻塞 |
| 接收 `<-ch` | **永久阻塞** | 立即返回零值 + `ok=false`（缓冲里还有值则先取值） | 有值立即返回；无值阻塞 |
| `close(ch)` | **panic** | **panic**（重复关闭） | 成功 |

关键推论：**nil channel 是天然的"永久等待"工具**（配合 select 屏蔽某个分支）；**close 不会丢失缓冲数据**——接收方会把缓冲里的存量值取完后才收到 `ok=false`。

## 💡 示例

```go
package main

import "fmt"

func main() {
	// 1. 无缓冲 channel：同步交接点
	done := make(chan struct{})
	go func() {
		fmt.Println("worker: 工作")
		close(done) // 用 close 代替发送"完成"信号（惯用法）
	}()
	<-done // 阻塞直到 worker close

	// 2. 已关闭 channel 的接收行为
	ch := make(chan int, 2)
	ch <- 1
	ch <- 2
	close(ch) // 关闭后缓冲数据仍可读
	fmt.Println(<-ch, <-ch) // 1 2（先取存量）
	v, ok := <-ch
	fmt.Println(v, ok) // 0 false（存量取完，零值+false）

	// 3. select 多路复用 + default 非阻塞
	reqs := make(chan int, 1)
	reqs <- 42
	select {
	case r := <-reqs:
		fmt.Println("收到", r)
	default:
		fmt.Println("无数据，不阻塞") // 有 default 即非阻塞
	}

	// 4. nil channel 在 select 中被"静默忽略"
	quit := make(chan int)
	go func() { quit <- 1 }()
	var data chan int = nil // nil：case data 永远不就绪
	select {
	case <-data: // 永远不会选中
	case q := <-quit:
		fmt.Println("退出", q)
	}

	// 5. 单向 channel：双向在传参时隐式转换
	feed := make(chan int, 1)
	go produce(feed)
	fmt.Println(<-feed)
}

func produce(out chan<- int) {
	out <- 100
	close(out) // 发送方负责关闭
}
```

**经典死锁场景**：所有 goroutine 都在阻塞等待、无人再能推进时，runtime 报 `fatal error: all goroutines are asleep - deadlock!`（注意：若仍有其他可运行 goroutine 则不会触发检测，改为永久卡死）。

```go
// 死锁示例（勿运行）：无缓冲 channel 自己发自己收不可行
// ch := make(chan int)
// ch <- 1   // 发送阻塞，同一 goroutine 内无法走到接收
// <-ch
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：接收方 `close(ch)`。
- ✅ **正确做法**：close 是发送方的"我说完了"信号；接收方 close 会与后续发送 panic 互踩。
- ❌ **错误做法**：向已关闭的 channel 发送数据，指望像接收一样温和。
- ✅ **正确做法**：发送方统一负责 close，并且 close 前保证不再有发送；多发送者场景用额外 done channel 或 `sync.WaitGroup` 确认全部退出后再 close。
- ❌ **错误做法**：用 `v := <-ch` 后拿零值当有效数据处理。
- ✅ **正确做法**：用 `v, ok := <-ch` 或 `for range ch` 感知关闭；发送"结束"用 close 而不是发特殊零值。
- ❌ **错误做法**：忘记消费 channel 导致发送方永远阻塞、goroutine 泄漏。
- ✅ **正确做法**：谁创建 channel，谁保证有消费路径；用 `context` 取消 + select 写法保证发送可中断。
- ❌ **错误做法**：以为 select 多个就绪分支按书写顺序执行。
- ✅ **正确做法**：select 在就绪分支中均匀伪随机选择；不构成严格优先级或有限等待保证；需要优先级就先单独 try-default 再 select。
- ❌ **错误做法**：`ch == nil` 当作"空"并 close 它。
- ✅ **正确做法**：close nil 或已关闭的 channel 都 panic；关闭权唯一化：只让一个发送者在确定时刻 close 一次。

<!-- full-library-explanation -->
## 关闭表达发送完成，不是释放一块资源

前置是 goroutine 与阻塞。channel 不像文件那样必须靠 close 释放操作系统句柄；关闭的用途是通知接收方不会再有值。能够证明不会再发送的责任方决定关闭时机，多发送者通常由协调者等待所有发送者结束再关闭。

练习向容量为 2 的 channel 写入 0、7 后关闭，连续接收三次并打印 ok：应得到 `0 true`、`7 true`、`0 false`。只看零值无法区分合法消息与结束，range 则会消费存量后结束。

select 在多个就绪分支中选择一个，不提供严格的优先级或有限时间内绝不饥饿的保证。已经关闭且取空的接收分支会一直就绪；需要退出循环或将该 channel 变量设为 nil，避免反复处理结束信号。

## 🔗 相关条目

- 📄 **[Go 并发基础](./08-concurrency-basics.md)** - goroutine 与 WaitGroup 基础
- 📄 **[context 包](../library-guides/05-context.md)** - 取消信号与 channel 传播
- 📄 **[sync 包](../library-guides/06-sync.md)** - channel 与锁的分工
- 📄 **[nil 语义汇总](./15-nil-semantics.md)** - nil channel 阻塞行为汇总
- 📄 **[defer/panic/recover](./14-defer-panic-recover.md)** - panic 不跨 goroutine 边界
- 🌐 **[Go 内存模型：channel happens-before](https://go.dev/ref/mem)** - 官方同步保证

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
