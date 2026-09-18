# errors - 错误值工程

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

Go 把错误当**普通值**：`error` 是单方法接口，函数用最后一个返回值报错。errors 包配套提供**判断（Is）、提取（As）、解链（Unwrap）**三个工具，与 `fmt.Errorf("%w")` 的错误包装共同构成"可检查的错误链"——错误可以携带上下文一路向上传，同时调用方仍能识别根因。

## 📖 语法 / 签名

```go
package main

import (
	"errors"
	"fmt"
)

// customError 是可携带结构化字段的自定义 error 类型。
type customError struct {
	Path string
}

func (e *customError) Error() string { return "cannot read " + e.Path }

func main() {
	path := "config.json"
	target := errors.New("boom") // 匿名错误；动态消息不宜重新构造后做 sentinel 比较
	err := fmt.Errorf("read %s: %w", path, target) // %w 保留原错误形成链

	// Is 沿包装链匹配 sentinel；Unwrap 只调用 Unwrap() error。
	fmt.Println(errors.Is(err, target))
	fmt.Println(errors.Unwrap(err))

	structured := fmt.Errorf("request failed: %w", &customError{Path: path})
	var extracted *customError
	fmt.Println(errors.As(structured, &extracted), extracted.Path) // 提取具体类型

	err1 := errors.New("cache failed")
	err2 := &customError{Path: "metrics"}
	joined := errors.Join(err1, err2) // Go 1.20+；全 nil 时返回 nil，Is/As 能穿透成员
	fmt.Println(errors.Is(joined, err1))
	var joinedCustom *customError
	fmt.Println(errors.As(joined, &joinedCustom), joinedCustom.Path)
	fmt.Println(errors.Unwrap(joined) == nil) // Join 的 Unwrap() []error 不由 errors.Unwrap 展开
}
```

**Sentinel error 模式**：包级导出的预声明错误值（`var ErrNotFound = errors.New("not found")`），调用方用 `errors.Is(err, ErrNotFound)` 识别。命名惯例：导出为 `ErrXxx`。

**错误链工作方式**：单个 `%w` 的包装可通过 Unwrap() error 展开；多个 `%w` 或 Join 可以形成分支，Is/As 遍历错误树。内部具体类型名不是应依赖的 API。自定义类型想定制匹配，可实现 `Is(target error) bool` / `As(any) bool` 方法。

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
- ✅ **正确做法**：需要可识别性就用 `%w`（Go 1.20 起一次 Errorf 可以包含多个 `%w`）；确定顶层拦截、不暴露根因的场景才用 `%v`。
- ❌ **错误做法**：用 `errors.New(fmt.Sprintf(...))` 拼动态消息。
- ✅ **正确做法**：直接 `fmt.Errorf(...)`；动态消息错误只用于展示，不用于 Is 判定。
- ❌ **错误做法**：每次请求都 `errors.New` 当 sentinel，两处代码"长得一样"却永不相等。
- ✅ **正确做法**：sentinel 必须是包级 `var` 唯一实例。
- ❌ **错误做法**：panic 代替 error 向上传业务失败。
- ✅ **正确做法**：可预期失败一律 error（见 defer/panic 条目的分工）。
- ❌ **错误做法**：As 的目标是值类型 `var ve ValidationError` 但链上装的是 `*ValidationError`。
- ✅ **正确做法**：As 要求找到的错误可赋给目标类型，也支持接口目标；target 本身要是合法的非 nil 指针。此例错误的动态类型为 *ValidationError，因此使用 var ve *ValidationError，再传 &ve。

<!-- full-library-explanation -->
## 错误匹配是一项对调用者的承诺

前置是接口、指针和多返回值。errors.Is 用来询问“这个失败是否属于我需要处理的情况”，errors.As 用来提取结构化细节；打印错误文本给人看，不适合作为稳定控制流。若向外包装某个数据库驱动的具体错误，调用者可能开始依赖它，未来换驱动就会受约束。可在仓储边界将已知情况转换为领域错误，未知情况保留内部日志与关联 ID，避免把连接串或 SQL 原样发给用户。

Join 形成的是错误树，不一定是一条单链。errors.Is 和 errors.As 能遍历它，errors.Unwrap 只处理 Unwrap() error，不会拆开 Unwrap() []error。自测：创建 a := errors.New("a")，再对 errors.Join(a, errors.New("b")) 分别调用 Is(joined, a) 和 Unwrap(joined)，预期是 true 和 nil。nil 并不意味着 joined 没有子错误，只是该工具不处理这种展开方法。

练习：把示例 loadUser 的错误包装两层，在 HTTP 适配层将 ErrNotFound 映射为 404，将未知错误映射为 500。断言状态分类而非整段错误字符串；为错误添加“load user 42”上下文后，分类测试仍应通过。错误处理本身还要决定是否重试，不能因为所有错误都实现 error 接口就统一重试。

## 🔗 相关条目

- 📄 **[Go 错误处理](../language-concepts/07-error-handling.md)** - error 返回值的语言层基础
- 📄 **[接口语义](../language-concepts/13-interface-semantics.md)** - error 是接口，nil 判断同理
- 📄 **[defer/panic/recover](../language-concepts/14-defer-panic-recover.md)** - panic 与 error 的边界
- 📄 **[database/sql 包](./07-database-sql.md)** - sql.ErrNoRows 的 Is 用法
- 🌐 **[pkg.go.dev/errors](https://pkg.go.dev/errors)** - 官方文档
- 🌐 **[Working with Errors in Go 1.13（官方博客）](https://go.dev/blog/go1.13-errors)** - 错误链设计说明

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
