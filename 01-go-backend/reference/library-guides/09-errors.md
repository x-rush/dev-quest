# errors - 错误值工程

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

Go 把错误当**普通值**：`error` 是单方法接口，函数用最后一个返回值报错。errors 包配套提供**判断（Is）、提取（As）、解链（Unwrap）**三个工具，与 `fmt.Errorf("%w")` 的错误包装共同构成"可检查的错误链"——错误可以携带上下文一路向上传，同时调用方仍能识别根因。

## 📖 语法 / 签名

```go
// error 接口
type error interface { Error() string }

// 三种构造
errors.New("boom")                      // 匿名错误（动态消息，不宜做 sentinel 比较）
fmt.Errorf("read %s: %w", path, err)    // %w 包装：保留原错误形成链
myErr{...}                              // 自定义类型（可携带结构化字段）

// 三个判读工具（1.13+）
errors.Is(err, target)    // 链上是否"等于" target（== 或 Is(target) error 方法）
errors.As(err, &target)   // 链上是否能"提取为"某具体类型
errors.Unwrap(err)        // 剥掉一层上下文，返回内层错误（无包装则 nil）

// 多错误合并（Go 1.20+）
joined := errors.Join(err1, err2)   // 全 nil 则返回 nil；Is/As 可穿透各成员
```

**Sentinel error 模式**：包级导出的预声明错误值（`var ErrNotFound = errors.New("not found")`），调用方用 `errors.Is(err, ErrNotFound)` 识别。命名惯例：导出为 `ErrXxx`。

**错误链工作方式**：`%w` 生成的 `*fmt.wrapError` 实现 `Unwrap() error`；`Is/As` 沿链递归。自定义类型想定制匹配，可实现 `Is(target error) bool` / `As(any) bool` 方法。

## 💡 示例

```go
package main

import (
	"errors"
	"fmt"
)

// Sentinel：包级唯一错误值
var ErrNotFound = errors.New("record not found")

// 自定义错误类型：携带结构化上下文
type ValidationError struct {
	Field string
	Msg   string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("字段 %s 无效: %s", e.Field, e.Msg)
}

// 包装层：模拟"带上下文向上传"
func loadUser(id int) error {
	return fmt.Errorf("load user %d: %w", id, ErrNotFound)
}

func save() error {
	return fmt.Errorf("save: %w", &ValidationError{Field: "email", Msg: "格式错误"})
}

func main() {
	// 1. errors.Is 穿透包装链识别 sentinel
	err := loadUser(42)
	fmt.Println(errors.Is(err, ErrNotFound)) // true
	fmt.Println(err)                         // load user 42: record not found

	// 2. errors.As 提取具体类型
	var ve *ValidationError
	if errors.As(save(), &ve) {
		fmt.Println(ve.Field) // email
	}

	// 3. errors.Join：一次操作收集多个失败
	e1 := errors.New("cache flush failed")
	e2 := errors.New("metrics flush failed")
	joined := errors.Join(e1, e2)
	fmt.Println(joined)                // cache flush failed\nmetrics flush failed
	fmt.Println(errors.Is(joined, e1)) // true（Join 后仍可 Is）

	// 4. Join(nil, nil) == nil：惯用的"聚合后统一报错"
	fmt.Println(errors.Join(nil, nil) == nil) // true

	// 5. errors.New 每次是新值，不能当 sentinel 用
	fmt.Println(errors.New("x") == errors.New("x")) // false
}
```

**业务错误分层惯例**：底层返回 sentinel/类型化错误 → 中间层 `fmt.Errorf("%w")` 补上下文 → HTTP 层 `errors.Is/As` 映射状态码。错误消息全小写、结尾不带标点，让多层拼接读起来像句子。

## ⚠️ 常见陷阱

- ❌ **错误做法**：`err == ErrNotFound` 直接比较包装过的错误。
- ✅ **正确做法**：`errors.Is(err, ErrNotFound)`；中间层一旦用 `%w` 包装，`==` 永远 false。
- ❌ **错误做法**：`fmt.Errorf("...: %v", err)` 丢弃错误链后再想 Is 识别。
- ✅ **正确做法**：需要可识别性就用 `%w`（每层只包一个 `%w`）；确定顶层拦截、不暴露根因的场景才用 `%v`。
- ❌ **错误做法**：用 `errors.New(fmt.Sprintf(...))` 拼动态消息。
- ✅ **正确做法**：直接 `fmt.Errorf(...)`；动态消息错误只用于展示，不用于 Is 判定。
- ❌ **错误做法**：每次请求都 `errors.New` 当 sentinel，两处代码"长得一样"却永不相等。
- ✅ **正确做法**：sentinel 必须是包级 `var` 唯一实例。
- ❌ **错误做法**：panic 代替 error 向上传业务失败。
- ✅ **正确做法**：可预期失败一律 error（见 defer/panic 条目的分工）。
- ❌ **错误做法**：As 的目标是值类型 `var ve ValidationError` 但链上装的是 `*ValidationError`。
- ✅ **正确做法**：As 目标类型必须与装包类型完全一致（指针对指针）；按实现方的方法集决定（指针方法 → 指针类型）。

## 🔗 相关条目

- 📄 **[Go 错误处理](../language-concepts/07-error-handling.md)** - error 返回值的语言层基础
- 📄 **[接口语义](../language-concepts/13-interface-semantics.md)** - error 是接口，nil 判断同理
- 📄 **[defer/panic/recover](../language-concepts/14-defer-panic-recover.md)** - panic 与 error 的边界
- 📄 **[database/sql 包](./07-database-sql.md)** - sql.ErrNoRows 的 Is 用法
- 🌐 **[pkg.go.dev/errors](https://pkg.go.dev/errors)** - 官方文档
- 🌐 **[Working with Errors in Go 1.13（官方博客）](https://go.dev/blog/go1.13-errors)** - 错误链设计说明

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
