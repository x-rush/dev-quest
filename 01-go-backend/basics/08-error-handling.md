# Go 错误处理：错误契约、资源清理与边界响应

前置：[函数和方法](05-functions-methods.md)、[控制结构](06-control-structures.md)。完成本章后，应能回答三个问题：调用者如何识别失败，失败以后资源如何清理，外部用户最终看到什么。

`error` 是一个只有 `Error() string` 方法的接口。它让函数把失败作为结果交给调用者决定。文件不存在、输入无效、请求超时通常是调用契约中的失败，不应改成 panic。panic 适合无法维持内部不变量的程序错误；在边界恢复时，也不能把失败伪装成成功。

本文五个完整程序可分别保存为 `main.go` 并执行 `go run main.go`，不要把它们拼成一个文件。它们由[验证器](../../shared-resources/tools/document-quality/verify_go_rust_basics.py)直接抽取并比较输出，限定证据见[报告](../../shared-resources/tools/document-quality/reports/go-rust-basics.md)。表格中的规则仍需结合具体 API 契约理解。

## 1. 先设计调用者需要判断什么

| 形式 | 适用场景 | 调用方做法 | 边界 |
|---|---|---|---|
| `errors.New` | 稳定的错误类别，如未找到 | 导出的同一个哨兵值配合 `errors.Is` | 每次新建同文案错误不是同一个哨兵 |
| 自定义错误类型 | 调用者需要字段，如哪个输入无效 | `errors.As` 提取字段 | 类型指针和值必须匹配 |
| `fmt.Errorf("...: %w", err)` | 增加操作上下文并保留底层类别 | 继续 `Is`/`As` | 包装会把底层错误纳入公开契约 |
| `errors.Join(a, b)` | 多个独立失败都值得保留 | `Is`/`As` 遍历错误树 | `errors.Unwrap` 不遍历 `Unwrap() []error` |
| 文案错误 | 只需人类诊断，不提供稳定类别 | 显示或记录，避免按字符串分支 | 文案变化不应破坏业务逻辑 |

### 包装后的错误还能按类别或类型判断

下面只用内存数据，聚焦错误协议。`findUser` 先校验 ID，再访问数据；业务层增加上下文但不重复记录日志。边界层最后统一解释结果。

<!-- verified-case: go-errors-contract -->
```go
package main

import (
    "errors"
    "fmt"
)

var ErrNotFound = errors.New("user not found")

type InputError struct { Field string }
func (e *InputError) Error() string { return "invalid field: " + e.Field }

func findUser(id int) (string, error) {
    if id <= 0 { return "", &InputError{Field: "id"} }
    if id != 1 { return "", ErrNotFound }
    return "Ada", nil
}

func loadUser(id int) (string, error) {
    name, err := findUser(id)
    if err != nil { return "", fmt.Errorf("load user %d: %w", id, err) }
    return name, nil
}

func main() {
    for _, id := range []int{1, 0, 2} {
        name, err := loadUser(id)
        var input *InputError
        switch {
        case err == nil:
            fmt.Println(name)
        case errors.As(err, &input):
            fmt.Println("invalid", input.Field)
        case errors.Is(err, ErrNotFound):
            fmt.Println("not found")
        default:
            panic(err) // 本程序没有其他失败路径；服务边界应映射为内部错误
        }
    }
    wrapped := fmt.Errorf("lookup: %w", ErrNotFound)
    fmt.Println(errors.Is(wrapped, errors.New("user not found")))
    joined := errors.Join(wrapped, &InputError{Field: "email"})
    var input *InputError
    fmt.Println(errors.Is(joined, ErrNotFound), errors.As(joined, &input))
    fmt.Println(errors.Unwrap(joined) == nil)
}
```

预期输出：

```text
Ada
invalid id
not found
false
true true
true
```

`errors.Is` 不只是一次 `==`：它会检查当前错误、可选的 `Is(error) bool` 方法及包装的错误树。`errors.As` 类似地寻找可赋给目标类型的错误，并支持自定义 `As`。因此不要手写 `for err != nil { err = errors.Unwrap(err) }` 来代替所有错误匹配；这种循环会漏掉 Join 的分支。

`var input *InputError; errors.As(err, &input)` 传入的是目标变量的地址，即 `**InputError`。`As` 需要把找到的 `*InputError` 写入这个变量；直接传入 nil 的 `input` 不符合 API 要求。

## 2. 接口中的 typed nil 不是 nil error

接口同时携带动态类型与动态值。一个类型为 `*InputError` 的 nil 指针装进 `error` 后，动态类型仍存在，所以 `err != nil`。成功时应明确返回无类型 `nil`。

<!-- verified-case: go-errors-typed-nil -->
```go
package main

import "fmt"

type Problem struct { Message string }
func (p *Problem) Error() string { return p.Message }

func incorrect() error {
    var p *Problem
    return p
}

func correct() error { return nil }

func main() {
    fmt.Println(incorrect() == nil)
    fmt.Println(correct() == nil)
}
```

预期输出：

```text
false
true
```

不要为了展示 typed nil 而随意调用它的 `Error()`：这里的方法会解引用 nil。泛型、接口和自定义指针错误混用时，应特别检查成功分支的返回值。

## 3. defer 清理资源，但清理也可能失败

`defer` 在包含它的函数返回时执行，不在代码块结束时执行；多个 defer 后进先出，调用参数在注册时求值。获取资源成功后再注册清理，循环里需及时释放时，把每次处理封装成一个函数。

普通返回和 panic 栈展开会执行 defer；`os.Exit`、`log.Fatal` 和进程被终止则不能依赖它。底层库应返回错误，把退出进程的决定留给程序入口。

写文件时 `Write` 或 `Close` 都可能失败。若只写 `defer f.Close()` 而丢弃结果，调用者可能以为数据已经成功提交。下面把“使用并关闭一个写入器”的所有权写在函数契约里，用故障替身同时触发写入与关闭错误。

<!-- verified-case: go-errors-cleanup -->
```go
package main

import (
    "errors"
    "fmt"
    "io"
)

var ErrWrite = errors.New("write failed")
var ErrClose = errors.New("close failed")

// 调用后，无论成功失败，w 都会被关闭；调用者不要再次使用它。
func writeAndClose(w io.WriteCloser, data []byte) (err error) {
    defer func() {
        if closeErr := w.Close(); closeErr != nil {
            err = errors.Join(err, fmt.Errorf("close output: %w", closeErr))
        }
    }()
    n, writeErr := w.Write(data)
    if writeErr != nil { return fmt.Errorf("write output: %w", writeErr) }
    if n != len(data) { return io.ErrShortWrite }
    return nil
}

type faultWriter struct { closed bool }
func (w *faultWriter) Write([]byte) (int, error) { return 0, ErrWrite }
func (w *faultWriter) Close() error { w.closed = true; return ErrClose }

func main() {
    writer := &faultWriter{}
    err := writeAndClose(writer, []byte("hello"))
    fmt.Println(writer.closed)
    fmt.Println(errors.Is(err, ErrWrite), errors.Is(err, ErrClose))
    order := func() {
        defer fmt.Println("last")
        n := 1
        defer fmt.Println("captured", n)
        n = 2
        fmt.Println("current", n)
    }
    order()
}
```

预期输出：

```text
true
true true
current 2
captured 1
last
```

函数使用具名返回 `err`，因此 defer 可以把 Close 的失败合并进最终结果。这不等于磁盘持久化保证：文件原子替换、`Sync`、目录同步、并发修改和平台语义属于另一个契约。复制文件时也不能未经检查就 `os.Create(dst)`：若源和目标指向同一文件，会先截断源；覆盖策略、临时文件和替换应显式设计。

## 4. recover 只能恢复当前 goroutine，不能接着执行 panic 后一行

恢复必须发生在同一 goroutine 中被 defer 直接调用的函数里。它会结束当前 panic 的栈展开；引发 panic 的操作不会自动重试，发生 panic 的函数也不会回到原位置。

下面用一个私有类型表示边界协议允许转换的 panic。非该类型的 panic 原样再次抛出，避免把未知程序错误默默吞掉。正常业务校验应直接返回 error，这个例子只是解释已有组件使用 panic 时的适配边界。

<!-- verified-case: go-errors-recover -->
```go
package main

import (
    "errors"
    "fmt"
)

type boundaryFailure struct { err error }
var ErrOperation = errors.New("operation failed")

func call(fn func()) (err error) {
    defer func() {
        if value := recover(); value != nil {
            failure, ok := value.(boundaryFailure)
            if !ok { panic(value) }
            err = failure.err
        }
    }()
    fn()
    return nil
}

func main() {
    fmt.Println(call(func() {}) == nil)
    continued := false
    err := call(func() {
        panic(boundaryFailure{ErrOperation})
        // panic 后的语句不会执行
    })
    if err == nil { continued = true }
    fmt.Println(errors.Is(err, ErrOperation), continued)
    func() {
        defer func() { fmt.Println("outer received", recover()) }()
        _ = call(func() { panic("unexpected") })
    }()
}
```

预期输出：

```text
true
true false
outer received unexpected
```

外层 recover 是本示例用来观察“未知 panic 被重新抛出”的测试边界。HTTP 服务器一般由框架边界记录堆栈、返回通用失败并中止该请求；日志需避免泄露请求秘密。已经写出的 HTTP 状态和响应体无法靠 recover 撤销，因此应先完成可能失败的工作，再提交响应。后台 goroutine 的 panic 不会被启动它的请求 goroutine 捕获。

## 5. 把业务错误映射为 HTTP 响应

缺少 ID 是输入失败，返回 400；资源不存在返回 404；未知内部错误返回不含内部细节的 500。认证与对象授权需要独立检查，不能通过“有 ID”就允许读取数据。示例仅展示错误映射，没有实现身份系统。

`httptest.ResponseRecorder` 可以直接调用 Handler 检查结果，无需启动端口或连接外网。我们在写状态前先编码 JSON；一旦响应开始，写入失败只能记录并结束，不能再尝试发送第二份错误 JSON。

<!-- verified-case: go-errors-http -->
```go
package main

import (
    "encoding/json"
    "errors"
    "fmt"
    "log"
    "net/http"
    "net/http/httptest"
    "strconv"
    "strings"
)

var ErrMissing = errors.New("missing user")

func lookup(id int) (string, error) {
    switch id {
    case 1: return "Ada", nil
    case 2: return "", ErrMissing
    default: return "", errors.New("internal connection details")
    }
}

func respond(w http.ResponseWriter, status int, payload map[string]string) {
    body, err := json.Marshal(payload)
    if err != nil { // 当前 map[string]string 不会编码失败；保留边界处理
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    if _, err := w.Write(append(body, '\n')); err != nil {
        log.Print("response write failed")
    }
}

func handler(w http.ResponseWriter, r *http.Request) {
    id, err := strconv.Atoi(r.URL.Query().Get("id"))
    if err != nil || id <= 0 {
        respond(w, 400, map[string]string{"error": "invalid id"})
        return
    }
    name, err := lookup(id)
    switch {
    case err == nil:
        respond(w, 200, map[string]string{"name": name})
    case errors.Is(err, ErrMissing):
        respond(w, 404, map[string]string{"error": "not found"})
    default:
        respond(w, 500, map[string]string{"error": "internal error"})
    }
}

func main() {
    for _, query := range []string{"", "?id=1", "?id=2", "?id=3"} {
        req := httptest.NewRequest(http.MethodGet, "/user" + query, nil)
        rec := httptest.NewRecorder()
        handler(rec, req)
        fmt.Println(rec.Code, strings.TrimSpace(rec.Body.String()))
    }
}
```

预期输出：

```text
400 {"error":"invalid id"}
200 {"name":"Ada"}
404 {"error":"not found"}
500 {"error":"internal error"}
```

数据库接入时先核对接口：`sql.Open(driverName, dsn)` 返回 `(*sql.DB, error)`，不是单个 error，且不保证已连接成功；需要连接检查时用有截止时间的 `PingContext`。错误日志可以保留操作、请求关联 ID 和已脱敏的原因，但不要把 DSN、密码或完整底层异常传给客户端。

## 6. 测试与练习

| 练习 | 要覆盖的分支 | 验收条件 |
|---|---|---|
| 扩展 loadUser | 正常、非法 ID、不存在、包装后的错误 | 用 `Is`/`As` 断言类别和字段，不依赖整段错误字符串 |
| 资源清理 | 写成功/关闭成功、仅写失败、仅关闭失败、两者都失败 | Close 恰好一次；两种错误类别都能保留；补短写反例 |
| HTTP 错误边界 | 缺 ID、负数、非数字、不存在、内部失败 | 400/404/500 正确；响应不含内部连接信息；每条分支只写一次响应 |
| 自定义错误 | 返回 nil、typed nil、指针错误 | 成功时 `err == nil`；失败时可用 `As` 得到正确目标类型 |

错误处理应围绕调用者的下一步决定设计：重试、修正输入、跳过还是终止。不要默认所有失败都可重试；网络写入失败可能已经产生副作用，重复执行前需要幂等契约。哨兵错误的价值首先是稳定分类，不应把它教成“避免每次分配字符串”的微优化。

## 官方资料与后续阅读

- [errors 包](https://pkg.go.dev/errors)：`Is`、`As`、`Join`、`Unwrap` 的完整契约。
- [Defer, Panic, and Recover](https://go.dev/blog/defer-panic-and-recover)：注册时求值、返回时清理、恢复边界。
- [database/sql.Open](https://pkg.go.dev/database/sql#Open)：数据库句柄与连接检查的区别。
- [httptest](https://pkg.go.dev/net/http/httptest)：Handler 测试工具。
- [Gin 框架基础](../frameworks/01-gin-framework-basics.md)：在具体 Web 框架中应用错误分类。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
