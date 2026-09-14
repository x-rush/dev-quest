# sync - 同步原语工具箱

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

sync 包提供**共享内存并发**的底层原语：锁（Mutex/RWMutex）、计数等待（WaitGroup）、单次执行（Once）、条件等待（Cond）与原子操作（atomic）。心智模型——channel 负责"传递数据的所有权"，sync 负责"原地保护共享状态"；两者互补而非互斥。

## 📖 语法 / 签名

```go
// Mutex：零值即可用（无需 make/New）
var mu sync.Mutex
mu.Lock(); /* 临界区 */ mu.Unlock()

// RWMutex：读锁共享、写锁独占，读多写少场景吞吐更高
var rw sync.RWMutex
rw.RLock(); rw.RUnlock()   // 多个读者可同时持有
rw.Lock();  rw.Unlock()    // 独占（等待全部读者退出）

// WaitGroup：等一组 goroutine 结束
var wg sync.WaitGroup
wg.Add(1)      // 计数 +1（在启动 goroutine 之前调用）
wg.Done()      // 计数 -1（defer 保证配对）
wg.Wait()      // 计数归零才返回
wg.Go(f)       // Go 1.25+ 语法糖：等价 Add(1)+go func{defer Done; f}

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
- ✅ **正确做法**：Wait 只在父 goroutine 调用；WaitGroup 复用前确认计数归零且 Wait 全部返回。
- ❌ **错误做法**：把含 Mutex 的 struct 按值传参/拷贝。
- ✅ **正确做法**：`go vet` 报 copylocks；统一传指针，锁字段不导出。
- ❌ **错误做法**：读写争用严重时仍坚持 RWMutex（写饥饿）。
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
- ✅ **正确做法**：标准模式 `for !condition() { c.Wait() }`；Broadcast 前后都持锁，防虚假唤醒。
- ❌ **错误做法**：用 atomic 保护多个相关字段。
- ✅ **正确做法**：原子操作只保护"单个独立值"；多字段一致性用 mutex，或 atomic.Value 整体替换快照。

## 🔗 相关条目

- 📄 **[map 语义](../language-concepts/11-map-semantics.md)** - 并发 map 的锁包装对比 sync.Map
- 📄 **[channel 语义](../language-concepts/12-channel-semantics.md)** - channel 与锁的分工
- 📄 **[context 包](./05-context.md)** - 取消场景下的 goroutine 编排
- 📄 **[Go 并发基础](../language-concepts/08-concurrency-basics.md)** - 内存模型与 happens-before
- 🌐 **[pkg.go.dev/sync](https://pkg.go.dev/sync)** - 官方文档
- 🌐 **[Introducing the Go Race Detector](https://go.dev/blog/race-detector)** - 配套 `go test -race` 验证

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
