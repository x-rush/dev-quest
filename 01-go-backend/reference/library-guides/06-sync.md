# sync - 同步原语工具箱

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

sync 包提供**共享内存并发**的底层原语：锁（Mutex/RWMutex）、计数等待（WaitGroup）、单次执行（Once）、条件等待（Cond）；原子操作位于独立的 sync/atomic 包。心智模型——channel 负责"传递数据的所有权"，sync 负责"原地保护共享状态"；两者互补而非互斥。

## 📖 语法 / 签名

```go
// Mutex：零值即可用（无需 make/New）
var mu sync.Mutex
mu.Lock(); /* 临界区 */ mu.Unlock()

// RWMutex：读锁共享、写锁独占，读多写少时可能有利，需按临界区成本实测
var rw sync.RWMutex
rw.RLock(); rw.RUnlock()   // 多个读者可同时持有
rw.Lock();  rw.Unlock()    // 独占（等待全部读者退出）

// WaitGroup：等一组 goroutine 结束
var wg sync.WaitGroup
wg.Add(1)      // 计数 +1（在启动 goroutine 之前调用）
wg.Done()      // 计数 -1（defer 保证配对）
wg.Wait()      // 计数归零才返回
wg.Go(f)       // Go 1.25+：启动任务并计入等待组；f 必须不发生 panic

// Once：并发下首次调用执行，其余阻塞等待完成
var once sync.Once
once.Do(func() { /* 初始化恰好一次 */ })

// Cond：条件变量，配合 Locker 使用
c := sync.NewCond(&mu)
c.Wait()          // 必须持有锁调用；内部释放锁休眠，唤醒后重新拿锁
c.Broadcast()     // 唤醒全部等待者
c.Signal()        // 唤醒一个

// atomic：无锁原子读写（int32/64、uint、指针等）
var n atomic.Int64
n.Add(1); n.Load(); n.Store(3); n.CompareAndSwap(3, 4)
```

**拷贝锁检查**：sync 类型内嵌"不可复制"标记，`go vet` 会对按值拷贝（传参、赋值、嵌入后值拷贝）报 `copylocks` 错误。规则：锁要么零值内嵌 + 指针使用，要么作为 struct 字段时 struct 一律指针传递。

## 💡 示例

```go
package main

import (
	"fmt"
	"sync"
	"sync/atomic"
)

// 经典单例：并发安全的惰性初始化
type Config struct{ DSN string }

var (
	cfg     *Config
	cfgOnce sync.Once
)

func LoadConfig() *Config {
	cfgOnce.Do(func() {
		cfg = &Config{DSN: "postgres://localhost/app"}
	})
	return cfg
}

// WaitGroup：并发收集结果（Go 1.25 的 wg.Go）
func fetchAll(ids []int) []string {
	var (
		wg      sync.WaitGroup
		mu      sync.Mutex
		results = make([]string, 0, len(ids))
	)
	for _, id := range ids {
		wg.Go(func() { // Go 1.25+；旧写法 wg.Add(1)+go+defer wg.Done()
			res := fmt.Sprintf("result-%d", id)
			mu.Lock()
			results = append(results, res)
			mu.Unlock()
		})
	}
	wg.Wait()
	return results
}

// 读写锁 vs 互斥锁
type Counter struct {
	mu sync.RWMutex
	m  map[string]int
}

func (c *Counter) Inc(k string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.m[k]++
}

func (c *Counter) Get(k string) int { // 读走 RLock，可多读者并行
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.m[k]
}

func main() {
	fmt.Println(LoadConfig() == LoadConfig()) // true：同一实例
	fmt.Println(fetchAll([]int{1, 2, 3}))     // 元素齐全但顺序不定（并发调度）

	c := &Counter{m: make(map[string]int)}
	var wg sync.WaitGroup
	for i := 0; i < 100; i++ {
		wg.Go(func() { c.Inc("hits") })
	}
	wg.Wait()
	fmt.Println(c.Get("hits")) // 100，无竞态

	var n atomic.Int64
	n.Add(1)
	n.CompareAndSwap(1, 3)
	fmt.Println(n.Load()) // 3
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：WaitGroup 只 `go f()` 忘了 `Add(1)`，或 Add 在 goroutine 内调用。
- ✅ **正确做法**：Add 与启动放同一处（或用 wg.Go），Done 用 defer 配对；否则 Wait 可能提前返回。
- ❌ **错误做法**：goroutine 里 `wg.Wait()`，等自己 Done——计数永不到零。
- ✅ **正确做法**：Wait 的调用者不能等待包含自身未完成贡献的组；WaitGroup 复用前确认计数归零且 Wait 全部返回。
- ❌ **错误做法**：把含 Mutex 的 struct 按值传参/拷贝。
- ✅ **正确做法**：`go vet` 报 copylocks；统一传指针，锁字段不导出。
- ❌ **错误做法**：未测量临界区成本就认定 RWMutex 一定比 Mutex 快。
- ✅ **正确做法**：临界区极短时 Mutex 反而更快；RWMutex 适合读占绝对多数且临界区不短的场景。
- ❌ **错误做法**：Do 中 panic 后指望"下次调用会重新执行初始化"——panic 后 Do 视为已返回，done 照样置位。
- ✅ **正确做法**：panic 后后续调用**不会重试**（实测 go1.25.14：f 只执行 1 次）；Once 语义是"恰好执行一次"，不区分成败。需要失败可重试须自建 mutex + 标志位：

  ```go
  var initMu sync.Mutex
  var ready bool

  func ensureInit() error {
  	initMu.Lock(); defer initMu.Unlock()
  	if ready { return nil }
  	if err := doInit(); err != nil { return err } // 失败不置位，下次调用重试
  	ready = true; return nil
  }
  ```
- ❌ **错误做法**：Cond.Wait 不在持有锁时调用，或不用循环检查条件。
- ✅ **正确做法**：标准模式 `for !condition() { c.Wait() }`；检查及修改条件需受关联锁保护。Go 的 Wait 不会自行虚假唤醒，但重新获得锁前条件可能被其他 goroutine 改变，所以仍须循环。Signal/Broadcast 本身不要求调用方持锁。
- ❌ **错误做法**：用 atomic 保护多个相关字段。
- ✅ **正确做法**：原子操作只保护"单个独立值"；多字段一致性用 mutex，或 atomic.Value 整体替换快照。

<!-- full-library-explanation -->
## 锁保护的是不变量，不只是某一行代码

前置是 goroutine、共享内存与 map。假设账户有 balance 和 reserved，业务要求 reserved 始终不超过 balance。分别用两个 atomic.Int64 只能保证单个读写不可分割，不能让“检查余额再增加预留金额”成为一个整体。两个请求都通过检查后再更新，仍可能超额。应让检查与修改处在同一把 Mutex 的临界区，或设计并证明等价的原子状态更新。

WaitGroup 解决“何时全部结束”，Mutex 解决“能否同时访问”，Context 解决“是否应提前停止”；任何一个都不能替代另外两个。示例 fetchAll 的结果顺序不固定，测试应比较元素集合；若要与输入顺序一致，可以预分配结果切片，每个任务只写自己独占的下标，最后 Wait，再读取全部结果。

练习：用 100 个任务为同一账户各预留 1 元，余额只有 10 元，要求最终恰好 10 次成功、reserved 等于 10。把检查移到锁外应能说明为什么不再正确；支持 race detector 的环境可再运行 go test -race，但没有数据竞争也不等于业务不变量成立。避免持有锁执行网络请求，否则一个慢依赖会阻塞所有需要这把锁的操作。

## 🔗 相关条目

- 📄 **[map 语义](../language-concepts/11-map-semantics.md)** - 并发 map 的锁包装对比 sync.Map
- 📄 **[channel 语义](../language-concepts/12-channel-semantics.md)** - channel 与锁的分工
- 📄 **[context 包](./05-context.md)** - 取消场景下的 goroutine 编排
- 📄 **[Go 并发基础](../language-concepts/08-concurrency-basics.md)** - 内存模型与 happens-before
- 🌐 **[pkg.go.dev/sync](https://pkg.go.dev/sync)** - 官方文档
- 🌐 **[Introducing the Go Race Detector](https://go.dev/blog/race-detector)** - 配套 `go test -race` 验证

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
