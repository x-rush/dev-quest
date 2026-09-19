# defer / panic / recover 语义

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

三者构成 Go 的异常控制流机制：`defer` 注册函数退出时执行的延迟调用（LIFO）；`panic` 中断当前函数并向上传播运行时错误；`recover` 仅在 defer 函数中有效，捕获 panic 让流程恢复。常规资源清理使用 defer，可预期失败通过 error 返回；panic/recover 用于有明确责任边界的异常控制，不是一般业务分支的替代。

## 📖 语法 / 签名

```go
// defer：注册延迟调用，函数返回时按 LIFO 逆序执行
defer f.Close()
defer mu.Unlock()
defer func() { /* 闭包可引用外层变量 */ }()

// panic：中断执行，逐层向上传播，途中执行已注册的 defer
panic("致命状态")

// recover：仅在 defer 的函数体内直接调用才生效
defer func() {
    if r := recover(); r != nil {
        log.Printf("recovered: %v", r)
    }
}()
```

三条铁律：

1. **参数立即求值**：`defer fmt.Println(x)` 在 defer 语句执行那一刻就拷贝了 x 的值，不是函数返回时的值。
2. **与 return 的交互**：`return v` 不是原子操作——先给返回值赋值 → 执行 defer → 真正返回。命名返回值可被 defer 修改。
3. **recover 的边界**：只捕获本 goroutine 的 panic；跨 goroutine 的 panic（如子 goroutine 内 panic）无法被父 goroutine 的 recover 捕获，进程直接崩溃。

## 💡 示例

<!-- doc-verify:go-defer-panic-recover -->
```go
package main

import "fmt"

// 命名返回值 + defer 修改返回值：defer 在赋值之后、返回之前执行
func double(n int) (result int) {
	defer func() { result *= 10 }()
	return n // 先 result = n，再 defer，最后返回
}

// 参数立即求值 vs 闭包延迟求值
func evalOrder() {
	x := 1
	defer fmt.Println("defer 参数（立即求值）:", x) // 打印 1
	x = 99
	defer func() { fmt.Println("defer 闭包（延迟求值）:", x) }() // 打印 99
}

// LIFO 顺序
func lifo() {
	defer fmt.Println("first registered")   // 第 3 个执行
	defer fmt.Println("second registered")  // 第 2 个执行
	fmt.Println("body")                     // 第 1 个执行
}

// recover：把 panic 转回普通错误（HTTP 中间件兜底的标准写法）
func safeCall(f func()) (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("recovered: %v", r)
		}
	}()
	f()
	return nil
}

func main() {
	evalOrder()
	lifo()
	fmt.Println("double(3) =", double(3)) // 30

	err := safeCall(func() { panic("boom") })
	fmt.Println(err) // recovered: boom
}
```

**panic 传播路径**：`panic` → 当前函数剩余语句跳过 → 按注册逆序执行本函数 defer → 回到调用方继续跳过并执行其 defer → …… → 若无人 recover，到达 goroutine 栈顶后打印堆栈并终止进程。

## ⚠️ 常见陷阱

- ❌ **错误做法**：`defer file.Close()` 后又想检查 Close 的错误却拿不到返回值。
- ✅ **正确做法**：需要处理 Close 错误时用命名返回值 + 闭包回写：`defer func() { err = errors.Join(err, f.Close()) }()`；否则接受"关闭失败仅记日志"。
- ❌ **错误做法**：在循环内 defer 打开资源的 Close（资源累积到函数结束才释放）。
- ✅ **正确做法**：把循环体抽成函数，或立即显式 Close；defer 的作用域是**函数**而非代码块。
- ❌ **错误做法**：子 goroutine 里 panic，指望主 goroutine 的 recover 兜底。
- ✅ **正确做法**：需要隔离故障时，在该 goroutine 内的合适边界 recover、记录并返回失败；不能期待另一个 goroutine 捕获它，也不应无条件吞掉错误。
- ❌ **错误做法**：用 panic 做普通业务错误流控制。
- ✅ **正确做法**：可预期错误走 error 返回值；panic 只用于断言失败、不变量破坏等程序性 bug（与 recover 搭配仅限进程级兜底/中间件）。
- ❌ **错误做法**：在 defer 之外或 defer 语句本身调用 recover。
- ✅ **正确做法**：recover 只有在 panic 传播途中、被 defer 的**函数体内直接调用**才返回非 nil；其他位置恒返回 nil。
- ❌ **错误做法**：`os.Exit(1)` 之前依赖 defer 清理。
- ✅ **正确做法**：`os.Exit` 不执行任何 defer（见 os 条目）；先清理再退出。

<!-- full-library-explanation -->
## recover 以后从哪里继续

前置是函数调用栈和返回值。panic 展开调用栈时执行已注册 defer；某个 defer 成功 recover 后，该函数按返回流程结束，不会跳回原 panic 语句的下一行。调用它的上层函数随后可以继续执行。

练习在本页 safeCall 的回调中先 panic，再写一条打印；调用 safeCall 后也写一条打印。回调中 panic 后的打印不应出现，上层调用后的打印应出现。把 recover 移到未直接被 defer 调用的普通辅助函数中，它将无法按这个模式截获 panic。

恢复 panic 不能证明应用状态完好。若操作在修改共享数据中途失败，仍需定义如何隔离或终止受损任务。不要为每个 goroutine 无条件吞掉 panic；在能够恢复责任边界、记录故障并返回失败的地方使用它。

## 🔗 相关条目

- 📄 **[channel 语义](./12-channel-semantics.md)** - panic 不跨 goroutine 边界
- 📄 **[nil 语义汇总](./15-nil-semantics.md)** - nil 解引用类 panic 来源
- 📄 **[os 包](../library-guides/11-os.md)** - os.Exit 与 defer 不执行
- 📄 **[errors 标准库](../library-guides/09-errors.md)** - panic 与 error 的分工
- 🌐 **[Defer, Panic, and Recover（官方博客）](https://go.dev/blog/defer-panic-and-recover)** - 权威来源
- 🌐 **[pkg.go.dev/builtin#recover](https://pkg.go.dev/builtin#recover)** - recover 规范语义

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
