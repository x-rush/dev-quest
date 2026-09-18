# Go 错误处理

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

Go 用**普通值**表达错误：`error` 是一个仅含 `Error() string` 方法的内置接口。函数通过最后一个返回值传递错误，调用方必须显式检查——没有异常穿透，控制流一目了然。配套的 `errors` 包提供错误包装、判定与合并能力，`panic`/`recover` 仅用于不可恢复的编程错误。

## 📖 语法 / 签名

```go
// error 接口（内置）
type error interface {
    Error() string
}

// 构造与包装
errors.New("文件不存在")                      // 静态错误
fmt.Errorf("读取 %s 失败: %w", path, err)     // %w 包装，保留错误链
errors.Join(err1, err2)                      // 合并多个错误

// 错误链判定
errors.Is(err, target error) bool            // 链上是否存在目标错误（含 == 与 Unwrap() 匹配）
errors.As(err, target any) bool              // 链上是否存在可赋值的目标类型

// panic / recover（仅限不可恢复场景）
panic(v any)
recover() any                                // 只在 defer 的函数中直接调用才生效
```

| 元素 | 类型 | 说明 |
|------|------|------|
| `error` | 内置接口 | 值语义，nil 表示无错误 |
| `%w` | 格式动词 | 在 fmt.Errorf 中建立包装关系；自定义 Unwrap 与 errors.Join 也可建立错误链 |
| `errors.Is/As` | 函数 | 需要遍历包装链时使用；== 或直接断言只检查外层错误 |

## 💡 示例

```go
package main

import (
    "errors"
    "fmt"
    "os"
)

var ErrNotFound = errors.New("record not found") // 哨兵错误

type ValidationError struct {
    Field string
}

func (e *ValidationError) Error() string { // 自定义错误类型
    return fmt.Sprintf("字段 %s 校验失败", e.Field)
}

func loadConfig(path string) ([]byte, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("loadConfig %q: %w", path, err) // 包装并保留上下文
    }
    return data, nil
}

func main() {
    _, err := loadConfig("missing.toml")
    if err != nil {
        // 判定：穿透包装层匹配哨兵错误
        if errors.Is(err, os.ErrNotExist) {
            fmt.Println("文件不存在，使用默认配置")
        }
        // 类型判定：从错误链中提取具体类型
        var ve *ValidationError
        if errors.As(err, &ve) {
            fmt.Println("非法字段:", ve.Field)
        }
        fmt.Println(err)
        return
    }
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：`if err == ErrNotFound` 判断被 `%w` 包装过的错误。
- ✅ **正确做法**：一律 `errors.Is(err, ErrNotFound)`，让它处理整条链。
- ❌ **错误做法**：用 `fmt.Errorf("...: %v", err)` 包装——错误链被切断，Is/As 全部失效。
- ✅ **正确做法**：需要可判定性就用 `%w`；纯粹加日志上下文才允许 `%v`。
- ❌ **错误做法**：`recover()` 写在普通函数体里。
- ✅ **正确做法**：`defer func() { if r := recover(); r != nil {...} }()`，且只在明确能兜住的边界（如 HTTP 中间件）使用。
- ❌ **错误做法**：`if err != nil { return err }` 原样透传却不加任何上下文，或重复打印同一错误。
- ✅ **正确做法**：在职责边界加一次上下文（`fmt.Errorf("loadConfig: %w", err)`），上层统一记录。
- ❌ **错误做法**：用 panic 表达可预期的业务失败（如参数不合法）。
- ✅ **正确做法**：业务失败返回 error；panic 只留给断言失败、不变量破坏等程序级缺陷。

<!-- full-library-explanation -->
## 用错误链保留可判断的原因

前置是多返回值与接口。Error() 字符串供人阅读，不适合作为稳定的程序判断协议。包装增加“正在做什么”的上下文，errors.Is 判断约定错误，errors.As 提取可访问字段的具体错误类型；直接相等或类型断言只检查当前这一层。

练习构造 `base := errors.New("missing")`，再分别用 `fmt.Errorf("load: %w", base)` 和 `fmt.Errorf("load: %v", base)` 生成新错误。errors.Is 对前者应为 true，对后者应为 false；两段文本即使相似，可遍历的结构不同。自定义 Unwrap 方法和 errors.Join 也能建立错误链，%w 不是唯一途径。

处理错误时选一个负责最终记录的位置，避免底层打印后上层重复打印。是否包装取决于是否增加有用上下文；原样返回一个已经具有足够信息的错误也是合理选择。

## 🔗 相关条目

- 📄 **[函数与方法](../../basics/05-functions-methods.md)** - 多返回值与错误传递的语法基础
- 📄 **[Go 关键字详解](./01-go-keywords.md)** - `defer`/`panic`/`go` 关键字全解
- 📄 **[Go 并发基础](./08-concurrency-basics.md)** - goroutine 中的错误传播模式
- 🌐 **[错误处理与 Go（官方博客）](https://go.dev/blog/errors-are-values)** - 权威来源
- 🌐 **[errors 包文档](https://pkg.go.dev/errors)** - 权威来源

---

*最后更新: 2026年09月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
