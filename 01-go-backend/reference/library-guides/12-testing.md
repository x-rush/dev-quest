# testing - 测试与基准框架

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

testing 包是 Go 内建的测试框架：`go test` 扫描 `*_test.go`（与被测代码同目录、同包），按约定自动发现 `TestXxx(t *testing.T)`、`BenchmarkXxx(b *testing.B)`、`FuzzXxx(f *testing.F)` 与 `ExampleXxx()`。零依赖、零注解——测试就是普通函数，断言就是 `if + t.Errorf`。

## 📖 语法 / 签名

```go
// 单元测试：t 失败方法族
func TestName(t *testing.T) {
    t.Error("失败但继续")        // 标记失败，继续执行
    t.Errorf("...: %v", x)
    t.Fatal("失败且终止本测试")   // 标记失败，立即停止当前测试函数
    t.Skip("跳过说明")           // 标记跳过
    t.Helper()                  // 把当前函数标记为辅助函数（报错行号指向调用方）
    t.Cleanup(func() {})        // 测试结束后执行（比 defer 更适合子测试共享）
}

// 命令行
// go test ./...            全部包
// go test -run TestAdd     按名字过滤
// go test -v               详细输出
// go test -race            竞态检测
// go test -bench=. -benchmem  基准测试
```

**表驱动测试**（Go 测试的标志性模式）：用匿名 struct 切片列出用例，`t.Run(name, ...)` 起子测试——单个用例失败可 `-run TestXxx/subname` 单独重跑，失败名可读。

**TestMain**：每包最多一个 `func TestMain(m *testing.M)`，接管整包测试的生命周期（连接测试库、全局 setup/teardown），最后必须 `os.Exit(m.Run())`。

## 💡 示例

```go
// mathx.go 存放 Add；本文件为 mathx_test.go，go test -v ./... 运行
package mathx

import (
	"os"
	"testing"
)

// 表驱动测试
func Add(a, b int) int { return a + b }

func TestAdd(t *testing.T) {
	tests := []struct {
		name string
		a, b int
		want int
	}{
		{"正数", 1, 2, 3},
		{"负数", -1, -2, -3},
		{"零", 0, 0, 0},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel() // 子测试并行执行
			if got := Add(tt.a, tt.b); got != tt.want {
				t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.want)
			}
		})
	}
}

// 基准测试：框架自适应放大 b.N，ResetTimer 隔离 setup 成本
func BenchmarkAdd(b *testing.B) {
	xs := make([]int, 100)
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		Add(xs[0], xs[1])
	}
}

// 新式基准（Go 1.24+）：b.Loop 自动处理计时与编译器优化抑制
func BenchmarkAddLoop(b *testing.B) {
	for b.Loop() {
		Add(1, 2)
	}
}

// Fuzzing 入门：种子语料 + 随机变异探索边界
func FuzzAdd(f *testing.F) {
	f.Add(1, 2) // 种子
	f.Add(-1, -2)
	f.Fuzz(func(t *testing.T, a, b int) {
		if got := Add(a, b); got != a+b {
			t.Errorf("Add 违反定义: %d", got)
		}
	})
}

// TestMain：整包级 setup/teardown
func TestMain(m *testing.M) {
	// 全局 setup：如启动测试容器、加载 fixture
	code := m.Run() // 跑全部测试
	// 全局 teardown
	os.Exit(code) // 必须显式退出
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：一个测试函数里验证多种行为，失败时无法定位。
- ✅ **正确做法**：表驱动 + t.Run 子测试；一个用例一个意图。
- ❌ **错误做法**：基准测试循环外做重 setup 却不 ResetTimer。
- ✅ **正确做法**：`b.ResetTimer()` 或 `b.StopTimer()/b.StartTimer()` 隔离非被测代码；小心编译器把无副作用调用优化掉（消费结果变量，或用 `b.Loop`）。
- ❌ **错误做法**：并行测试共享可变全局（同一 map、同一临时文件名）。
- ✅ **正确做法**：共享资源用互斥或每用例独立目录（`t.TempDir()` 自动清理）；循环变量传参（Go 1.22+ 自动按迭代绑定）。
- ❌ **错误做法**：TestMain 里忘记 `os.Exit(m.Run())`。
- ✅ **正确做法**：TestMain 接管退出权，不调用则测试"跑了"但退出码恒 0。
- ❌ **错误做法**：辅助函数里报错，行号指不进用户代码。
- ✅ **正确做法**：辅助函数开头 `t.Helper()`；失败信息用 `t.Errorf` 给出"got vs want"。
- ❌ **错误做法**：断言失败一律 t.Fatal，导致后续用例被跳过。
- ✅ **正确做法**：Fatal 只在"继续无意义"（如 fixture 加载失败）时用；资源清理交给 t.Cleanup。

## 🔗 相关条目

- 📄 **[io/bufio 包](./10-io-bufio.md)** - 表驱动测试配 bytes.Buffer 断言输出
- 📄 **[os 包](./11-os.md)** - TestMain 的 os.Exit 语义
- 📄 **[sync 包](./06-sync.md)** - 并行测试与竞态检测
- 📄 **[errors 标准库](./09-errors.md)** - errors.Is 断言错误类型
- 🌐 **[pkg.go.dev/testing](https://pkg.go.dev/testing)** - 官方文档
- 🌐 **[go.dev/doc/tutorial/add-a-test](https://go.dev/doc/tutorial/add-a-test)** - 官方入门教程

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
