# 并发编程基础：goroutine、channel 与 sync

## 先理解，再动手

go f() 安排并发工作，不保证它在 main 返回前完成。等待完成和保护共享数据是两种不同职责，WaitGroup 不能代替 Mutex。

**本节自测**：启动两个任务，各发送一个整数到 channel，由 main 接收两次求和。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

求和确定，打印先后未必确定；若不接收、不等待就返回，不能保证任务完成。

</details>

> **文档简介**: 掌握Go最著名的并发模型——用 goroutine 启动并发任务、用 channel 在任务间通信、用 sync 包协调同步，并避开最常见的并发陷阱

> **目标读者**: 已掌握函数与控制结构、想理解Go并发精髓的学习者

> **前置知识**: 已完成 [函数和方法](05-functions-methods.md)（理解闭包）与 [控制结构](06-control-structures.md)

> **预计时长**: 3-4小时学习 + 练习

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/concurrency` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#goroutine` `#channel` `#select` `#sync` `#并发` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

通过本文档学习，您将能够：
- 用 `go` 关键字启动 goroutine，并用 `WaitGroup` 等待完成
- 使用无缓冲/有缓冲 channel 在 goroutine 间传递数据
- 用 `select` 实现多路复用、超时与非阻塞收发
- 用 `sync.Mutex` 保护共享数据，理解数据竞争
- 识别并避开死锁、close 误用等典型陷阱

## 📝 goroutine：轻量级并发

### 1. 用 go 关键字启动

`go` 关键字让函数在新的 goroutine 中运行——它比线程轻量得多（初始仅几 KB 栈），单程序轻松开数十万个：

```go
func worker(id int, wg *sync.WaitGroup) {
	defer wg.Done() // 完成时通知 WaitGroup
	fmt.Printf("worker %d 开始\n", id)
	time.Sleep(10 * time.Millisecond) // 模拟工作
	fmt.Printf("worker %d 结束\n", id)
}

func main() {
	var wg sync.WaitGroup
	for i := 1; i <= 3; i++ {
		wg.Add(1) // 每启动一个 goroutine 计数 +1
		go worker(i, &wg)
	}
	wg.Wait() // 阻塞直到计数归零
	fmt.Println("所有 worker 完成")
}
```

> ⚠️ **WaitGroup 传指针**：`wg *sync.WaitGroup` 是必须的——WaitGroup 含内部状态，按值传递会让每个 goroutine 拿到副本，`Wait()` 永远等不到完成。

> ⚠️ **main 退出 = 全部 goroutine 终止**。goroutine 没有父子层级，main 不等待就直接返回，未完成的 goroutine 被直接丢弃。所以需要 WaitGroup 或 channel 协调。

### 2. Go 1.22+ 的循环变量语义

在循环里启动 goroutine 是最经典的陷阱。**Go 1.22 起，循环变量每次迭代都是独立变量**，闭包捕获的值是正确的：

```go
var wg sync.WaitGroup
for i := 1; i <= 3; i++ {
	wg.Add(1)
	go func() {
		defer wg.Done()
		fmt.Print(i, " ") // Go 1.22+ 每个闭包捕获自己的 i
	}()
}
wg.Wait()
```

多次运行输出是 `3 2 1`、`1 2 3`、`2 1 3`……——**值总是 1/2/3 各出现一次（正确），但打印顺序不确定**。goroutine 的调度顺序没有任何保证，永远不要依赖它。

> 📌 Go 1.21 及更早版本中，所有迭代共享同一个 `i`：循环要等 `i <= 3` 不成立才退出，此时 `i` 已是 4，因此经典输出是 `4 4 4`（Go 从不因共享循环变量而 panic）。当时的惯用法是 `i := i` 复制一份，升级到 1.22+（循环变量每迭代新建）后不再需要。

## 📝 channel：goroutine 间的管道

> 💡 Go 的并发哲学：**不要通过共享内存来通信，而要通过通信来共享内存**。channel 就是"通信"的工具。

### 1. 无缓冲 channel：同步握手

无缓冲 channel 的发送和接收**必须同时就绪**——像面对面交接，双方都到场才能完成：

```go
ch := make(chan string) // 无缓冲
go func() {
	ch <- "hello" // 阻塞，直到有人接收
}()
msg := <-ch // 阻塞，直到有人发送
fmt.Println("收到:", msg) // 收到: hello
```

这个"必然阻塞"的特性使无缓冲 channel 天然是**同步点**：发送方可以确定接收方已经拿到数据。

### 2. 有缓冲 channel：异步队列

```go
ch := make(chan int, 2) // 容量 2
ch <- 1 // 缓冲未满，不阻塞
ch <- 2
// ch <- 3 // 缓冲已满且无人接收：fatal error: all goroutines are asleep - deadlock!
fmt.Println(len(ch), cap(ch)) // 2 2
fmt.Println(<-ch, <-ch)       // 1 2
```

缓冲区满时发送阻塞、空时接收阻塞。**向无人接收且永远不会再被接收的 channel 发送，Go 运行时会直接报 deadlock 错误**（不是 panic，是 fatal error，无法 recover）。

### 3. close 与 range：生产者-消费者模式

channel 由**发送方**负责关闭，接收方用 `range` 自动消费到关闭为止：

```go
jobs := make(chan int, 5)
for i := 1; i <= 5; i++ {
	jobs <- i
}
close(jobs) // 发送方 close，告知"没有更多数据了"

for job := range jobs { // 取尽且已 close 时循环自动结束
	fmt.Print("处理任务", job, " ")
}
// 处理任务1 处理任务2 处理任务3 处理任务4 处理任务5
```

接收端也可以用 comma-ok 判断：

```go
v, ok := <-jobs // ok == false 表示 channel 已关闭且已取空
```

### 4. 单向 channel：表达意图

函数签名可以限定 channel 方向，让编译器帮你检查误用：

```go
func producer(out chan<- int) { // 只发送
	for i := 1; i <= 3; i++ {
		out <- i
	}
	close(out) // close 是发送方特权，双向/只发送 channel 才能调用
}

func consumer(in <-chan int, done chan<- bool) { // 只接收
	for v := range in {
		fmt.Print(v, " ")
	}
	done <- true
}
```

## 📝 select：多路复用

`select` 同时等待多个 channel 操作，哪个就绪执行哪个；多个就绪时**随机选择**（防止饥饿）：

### 1. 超时控制

```go
ch := make(chan string)
go func() {
	time.Sleep(100 * time.Millisecond)
	ch <- "慢消息"
}()

select {
case msg := <-ch:
	fmt.Println("收到:", msg)
case <-time.After(50 * time.Millisecond):
	fmt.Println("超时！没等到消息") // 100ms > 50ms，走这里
}
```

### 2. default：非阻塞收发

```go
select {
case <-ch:
	fmt.Println("收到了消息")
default: // 没有就绪的 case 时立即走 default，不阻塞
	fmt.Println("无数据，立即走 default")
}
```

`select + default` 是"试着读一下、没有就算了"的标准写法；`select + time.After` 是网络请求超时的标准写法。

## 📝 sync.Mutex：保护共享数据

channel 适合传递数据，但当多个 goroutine 要更新**同一个变量**时，互斥锁更直接：

```go
type Counter struct {
	mu    sync.Mutex
	count int
}

func (c *Counter) Inc() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.count++ // 同一时刻只有一个 goroutine 能执行到这里
}
```

1000 个 goroutine 并发递增：

```go
var c Counter
var wg sync.WaitGroup
for i := 0; i < 1000; i++ {
	wg.Add(1)
	go func() {
		defer wg.Done()
		c.Inc()
	}()
}
wg.Wait()
fmt.Println(c.count) // 1000 —— 稳定正确
```

**对比：不加锁会怎样？** 把 `c.Inc()` 换成裸的 `count++`，实测三次运行结果分别为 **987、1000、998**——有时碰巧正确，多数时候丢更新，且每次结果都不同。这种"偶尔才错"的数据竞争是最难排查的 bug 类型。

### 用 -race 检测竞争

Go 内置竞争检测器，`go run -race` / `go test -race` 会在发生竞争时打印详细报告：

```bash
$ go run -race main.go
==================
WARNING: DATA RACE
Read at 0x00c0000140f8 by goroutine 11: ...
```

> ⚠️ `-race` 只能检出**运行时实际发生**的竞争，未触发的路径检不出来。测试时始终带上 `-race`，CI 中也应开启。

### 原子操作的极简场景

单纯计数可用 `sync/atomic` 免去显式锁管理：

```go
var count atomic.Int64
count.Add(1)
fmt.Println(count.Load())
```

## ⚠️ 常见陷阱速查

| 陷阱 | 现象 | 正确做法 |
|------|------|----------|
| 忘记 wg.Add 或在 goroutine 内 Add | Wait 提前返回或 panic | Add 在启动前、主 goroutine 中调用 |
| WaitGroup 按值传递 | Wait 永久阻塞 | 始终传 `*sync.WaitGroup` |
| 向已关闭 channel 发送 | panic: send on closed channel | 只有发送方 close；多发送方时用 WaitGroup 等"全部发完"再 close |
| 重复 close | panic: close of closed channel | close 只由发送方调用一次（可用 sync.Once 保护） |
| 循环内 goroutine 依赖共享变量（<1.22） | 闭包读到意外值 | 升级 Go 1.22+，或 `i := i` 复制 |
| 无缓冲 channel 双方不同时就绪 | deadlock fatal error | 检查发送/接收是否配对，需要异步时用缓冲 |

关于 close 后的行为，实测结论：**读是安全的**——先排空缓冲区剩余值，取尽后返回零值且 `ok == false`；**写会 panic**（`send on closed channel`）；**再 close 也会 panic**。

## 📈 深入方向

- **context**：生产级超时与取消传播，见 [Go 标准库字典](../reference/library-guides/01-go-standard-library.md) 的 context 条目
- **errgroup**：带错误传播的 WaitGroup 替代，见 `golang.org/x/sync/errgroup`
- **worker pool**：固定数量 goroutine 消费任务队列的完整模式，见 advanced-topics 并发模式专题
- **channel 底层实现**：hchan 结构与调度交互，见 advanced-topics Go 语言机制专题

## 🔗 文档交叉引用

### 相关文档
- 📄 **[函数和方法]**: [05-functions-methods.md](05-functions-methods.md) - 闭包语法是 goroutine 的基础
- 📄 **[错误处理]**: [08-error-handling.md](08-error-handling.md) - defer 与并发安全配合
- 📄 **[Go 标准库字典]**: [../reference/library-guides/01-go-standard-library.md](../reference/library-guides/01-go-standard-library.md) - sync 包完整条目

### 参考资源
- 📖 **[Go 内存模型]**: https://go.dev/ref/mem
- 📖 **[Share Memory By Communicating]**: https://go.dev/doc/codewalk/sharemem/
- 📖 **[Go 1.22 Release Notes: 循环变量变更]**: https://go.dev/doc/go1.22#language

## 📝 总结

### 核心要点回顾
1. **goroutine 极轻量**：`go f()` 即启动，但 main 退出会终止一切，需 WaitGroup 协调
2. **channel 是通信原语**：无缓冲=同步握手，有缓冲=异步队列，发送方负责 close
3. **select 处理多路**：`time.After` 做超时，`default` 做非阻塞
4. **共享状态用锁**：Mutex 保护，`-race` 检测，atomic 处理纯计数
5. **调度顺序不可依赖**：Go 1.22+ 修复的是循环变量值，不是执行顺序

### 实践练习
- [ ] 启动 10 个 goroutine 并发抓取 10 个 URL（用 WaitGroup 等待全部完成）
- [ ] 实现生产者-消费者：1 个生产者发送 100 个整数，3 个 worker 消费并统计总和
- [ ] 给练习 1 加上 2 秒超时：任一请求超时则输出超时信息
- [ ] 故意写一个数据竞争程序，用 `go run -race` 观察报告，再用 Mutex 修复

---

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0

---

> 💡 **学习建议**:
> - 并发代码必须用 `-race` 验证，养成习惯
> - 先想清楚数据的所有权归谁（谁来发、谁来收、谁来 close），再写 channel 代码
> - 不确定时选 Mutex——它比错误的 channel 用法容易排查得多


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
