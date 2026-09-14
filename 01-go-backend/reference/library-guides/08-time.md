# time - 时间、时长与定时器

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

time 包提供时间点（`time.Time`）与时长（`time.Duration`）两大值类型。两个独门心智模型——**值语义不可变**（Time 像 string，传值即可、并发安全）与**参考时间格式化**（用固定范例时间 `2006-01-02 15:04:05` 的写法当作格式模板）。

## 📖 语法 / 签名

```go
// 参考时间记忆法：Mon Jan 2 15:04:05 MST 2006（1 2 3 4 5 6 7 的美式写法）
const (
	layoutDate = "2006-01-02"
	layoutTS   = "2006-01-02 15:04:05"
	layoutISO  = time.RFC3339 // "2006-01-02T15:04:05Z07:00"
)

t := time.Now()                      // 本地时区当前时间
u := time.Now().UTC()                // UTC 表示
p, err := time.Parse(layoutDate, "2026-09-14")     // 无时区假定 UTC
l, err := time.ParseInLocation(layoutTS, "2026-09-14 08:00:00", time.Local)

// 取值与运算（全部返回新值，不修改原 Time）
year := t.Year(); month := t.Month(); day := t.Day()
later := t.Add(2 * time.Hour)        // 时长加减
next  := t.AddDate(0, 1, 0)          // 年月日加减
d := u.Sub(t)                        // Duration（优先走单调时钟）
t.Before(u); t.After(u); t.Equal(u)  // 比较用方法，不用 ==

// 定时器
time.After(100 * time.Millisecond)   // <-chan Time：延时发一次
timer := time.NewTimer(d)            // 可 Stop/Reset 的定时器
tick := time.NewTicker(time.Second)  // 周期触发，用完必须 Stop
time.Sleep(d)                        // 阻塞睡眠（测试可用，服务代码优先 Timer/ctx）
```

**单调时钟（monotonic clock）**：`time.Now()` 同时携带墙钟与单调钟读数。`Sub/Before/After/Until` 计算时**优先用单调钟**，因此 NTP 校时、夏令时跳变不会让"测量经过时长"倒退；序列化（JSON/存库）或显式 `.UTC()/.Round(0)/.In()` 会剥离单调读数，剥离后仅剩墙钟比较。

**时区**：`time.Time` 内部记 UTC 时刻 + 显示位置（`*Location`）；`LoadLocation("Asia/Shanghai")` 依赖系统 tzdata（交叉编译无 tzdata 时 import `_ "time/tzdata"` 打包）。

## 💡 示例

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	// 1. 参考时间格式化：模板写什么，输出就是什么形状
	t := time.Date(2026, time.September, 14, 8, 5, 3, 0, time.UTC)
	fmt.Println(t.Format("2006-01-02 15:04:05")) // 2026-09-14 08:05:03
	fmt.Println(t.Format("2006/01/02 03:04 PM")) // 2026/09/14 08:05 AM
	fmt.Println(t.Format(time.RFC3339))          // 2026-09-14T08:05:03Z

	// 2. 解析回 Time
	p, err := time.Parse("2006-01-02", "2026-09-14")
	fmt.Println(p, err == nil) // 2026-09-14 00:00:00 +0000 UTC true

	// 3. Duration 是 int64 别名，单位常量运算直观
	d := 90 * time.Minute
	fmt.Println(d, d.Minutes()) // 1h30m0s 90

	// 4. 时区转换：同一时刻不同显示
	sh, _ := time.LoadLocation("Asia/Shanghai")
	local := t.In(sh)
	fmt.Println(local) // 2026-09-14 16:05:03 +0800 CST

	// 5. 单调时钟的可见痕迹（m=+… 表示携带单调读数）
	now := time.Now()
	fmt.Printf("带单调: %v\n", now) // 2026-09-14 16:05:03.xxx +0800 CST m=+0.000…
	fmt.Printf("剥离后: %v\n", now.Round(0))

	// 6. Ticker：周期任务，退出必须 Stop
	ticker := time.NewTicker(10 * time.Millisecond)
	count := 0
	for range ticker.C {
		count++
		if count == 3 {
			ticker.Stop()
			break
		}
	}
	fmt.Println("tick 完成", count) // 3

	// 7. 超时惯用法：time.After + select
	ch := make(chan int)
	select {
	case <-ch:
	case <-time.After(time.Millisecond):
		fmt.Println("超时") // 必然走到（ch 无人发）
	}
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：用 `"2006-13-25"` 之类"真实日期"当格式模板。
- ✅ **正确做法**：模板永远是参考时间 `2006-01-02 15:04:05` 的对应位置；想输出什么分隔符，就在模板里写什么。
- ❌ **错误做法**：用 `==` 比较 Time。
- ✅ **正确做法**：`t.Equal(u)`；`==` 会连"位置"与单调读数一起比较，产生假不等。
- ❌ **错误做法**：`time.Sleep` 实现超时控制，无法取消。
- ✅ **正确做法**：`select + ctx.Done()/time.After` 或 `timer`，配合 context 可中断。
- ❌ **错误做法**：Ticker/Timer 忘记 Stop，在高频路径持续泄漏。
- ✅ **正确做法**：用完 `defer ticker.Stop()`；Reset 前先排干 channel（`for { select { case <-t.C: default: } }`）再 Reset。
- ❌ **错误做法**：跨时区"加 8 小时"手工算。
- ✅ **正确做法**：同一时刻用 `.In(loc)` 换显示位置；"天"的概念用 `time.Date(y, m, d, 0,0,0,0, loc)` 在目标时区构造。
- ❌ **错误做法**：把 `time.After` 放进 for 循环当周期定时器（每次新 Timer，泄漏+不准）。
- ✅ **正确做法**：循环周期任务用 `time.NewTicker`。

## 🔗 相关条目

- 📄 **[context 包](./05-context.md)** - WithTimeout 与时间预算
- 📄 **[encoding/json 包](./04-encoding-json.md)** - time.Time 的 RFC3339 序列化
- 📄 **[channel 语义](../language-concepts/12-channel-semantics.md)** - Timer/Ticker 的 channel 消费
- 📄 **[sync 包](./06-sync.md)** - 计时测量与竞态验证
- 🌐 **[pkg.go.dev/time](https://pkg.go.dev/time)** - 官方文档
- 🌐 **[pkg.go.dev/time 预定义 Layout 常量](https://pkg.go.dev/time#pkg-constants)** - 官方格式常量全集

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
