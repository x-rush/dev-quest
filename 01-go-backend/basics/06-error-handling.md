# Go 错误处理机制

> **文档简介**: 全面掌握Go语言的错误处理机制，学会编写健壮、可靠的错误处理代码

> **目标读者**: Go初学者，需要掌握Go错误处理最佳实践的开发者

> **前置知识**: 已掌握Go基础语法、函数定义和接口概念

> **预计时长**: 2-3小时学习 + 实践

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `basics/programming-fundamentals` |
| **难度** | ⭐⭐⭐ (3/5) |
| **标签** | `#错误处理` `#error接口` `#panic-recover` `#异常处理` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

通过本文档学习，您将能够：
- 理解Go的错误处理哲学和设计理念
- 掌握error接口的使用和自定义错误类型
- 学会使用errors包进行错误包装和链式处理
- 掌握panic和recover机制的使用场景
- 建立良好的错误处理实践习惯

## 📖 Go错误处理哲学

### 为什么Go不使用异常

Go语言设计者选择了显式错误处理而不是异常机制，主要基于以下考虑：

1. **明确性**: 错误处理代码清晰可见，不会被隐藏
2. **可控性**: 错误处理流程由开发者完全控制
3. **简洁性**: 避免了复杂的try-catch-finally结构
4. **性能**: 显式错误处理比异常机制更高效

### error接口设计

Go的error是一个内置接口类型：

```go
// error是Go内置的唯一错误接口
type error interface {
    Error() string
}
```

任何实现了`Error() string`方法的类型都可以作为错误使用。

## 🔧 基础错误处理

### 1. 创建和返回错误

#### 使用errors包
```go
package main

import (
    "errors"
    "fmt"
)

func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

func main() {
    result, err := divide(10, 0)
    if err != nil {
        fmt.Printf("错误: %v\n", err)
        return
    }
    fmt.Printf("结果: %.2f\n", result)
}
```

#### 使用fmt.Errorf创建格式化错误
```go
func checkAge(age int) error {
    if age < 0 {
        return fmt.Errorf("年龄不能为负数: %d", age)
    }
    if age > 150 {
        return fmt.Errorf("年龄超出合理范围: %d", age)
    }
    return nil
}

func main() {
    ages := []int{-5, 25, 200}

    for _, age := range ages {
        if err := checkAge(age); err != nil {
            fmt.Printf("检查年龄 %d 失败: %v\n", age, err)
        } else {
            fmt.Printf("年龄 %d 有效\n", age)
        }
    }
}
```

### 2. 错误处理模式

#### 立即处理模式
```go
func processFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return fmt.Errorf("打开文件失败: %w", err)
    }
    defer file.Close()

    // 处理文件内容
    return nil
}
```

#### 错误聚合模式
```go
func validateUser(user *User) error {
    var errs []error

    if user.Name == "" {
        errs = append(errs, errors.New("姓名不能为空"))
    }

    if user.Age < 0 {
        errs = append(errs, errors.New("年龄不能为负数"))
    }

    if len(errs) > 0 {
        return fmt.Errorf("验证失败: %v", errs)
    }

    return nil
}
```

## 🎨 自定义错误类型

### 1. 结构体错误类型

```go
package main

import (
    "fmt"
)

// 自定义验证错误
type ValidationError struct {
    Field   string
    Value   interface{}
    Message string
}

func (e ValidationError) Error() string {
    return fmt.Sprintf("字段 '%s' 验证失败: %s (当前值: %v)",
        e.Field, e.Message, e.Value)
}

// 业务逻辑错误
type BusinessError struct {
    Code    string
    Message string
    Details map[string]interface{}
}

func (e BusinessError) Error() string {
    return fmt.Sprintf("业务错误 [%s]: %s", e.Code, e.Message)
}

func (e BusinessError) GetDetail(key string) interface{} {
    return e.Details[key]
}

// 使用示例
func validateEmail(email string) error {
    if email == "" {
        return ValidationError{
            Field:   "email",
            Value:   email,
            Message: "邮箱不能为空",
        }
    }

    if !strings.Contains(email, "@") {
        return ValidationError{
            Field:   "email",
            Value:   email,
            Message: "邮箱格式不正确",
        }
    }

    return nil
}

func checkUserPermission(userID int, resource string) error {
    // 模拟权限检查
    if userID == 0 {
        return BusinessError{
            Code:    "PERMISSION_DENIED",
            Message: "用户无权限访问该资源",
            Details: map[string]interface{}{
                "user_id":  userID,
                "resource": resource,
            },
        }
    }

    return nil
}

func main() {
    // 测试验证错误
    if err := validateEmail("invalid-email"); err != nil {
        fmt.Printf("验证错误: %v\n", err)
    }

    // 测试业务错误
    if err := checkUserPermission(0, "admin_panel"); err != nil {
        if bizErr, ok := err.(BusinessError); ok {
            fmt.Printf("业务错误: %v\n", bizErr)
            fmt.Printf("错误代码: %s\n", bizErr.Code)
            fmt.Printf("详细信息: %+v\n", bizErr.Details)
        }
    }
}
```

### 2. 错误类型断言

```go
func handleError(err error) {
    if err == nil {
        return
    }

    // 类型断言检查具体错误类型
    switch e := err.(type) {
    case ValidationError:
        fmt.Printf("验证错误 - 字段: %s, 值: %v, 消息: %s\n",
            e.Field, e.Value, e.Message)
    case BusinessError:
        fmt.Printf("业务错误 - 代码: %s, 消息: %s\n", e.Code, e.Message)
        // 可以访问特定业务错误的详细信息
        if resource, exists := e.Details["resource"]; exists {
            fmt.Printf("涉及资源: %v\n", resource)
        }
    default:
        fmt.Printf("未知错误类型: %v\n", err)
    }
}
```

## 🔗 错误包装和链式处理

### 1. 错误包装

Go 1.13+ 引入了错误包装功能：

```go
package main

import (
    "errors"
    "fmt"
)

// 使用 %w 动词进行错误包装
func loadConfig() error {
    // 模拟配置文件不存在
    return errors.New("config file not found")
}

func initializeApp() error {
    if err := loadConfig(); err != nil {
        // 包装错误，添加上下文信息
        return fmt.Errorf("初始化应用失败: %w", err)
    }
    return nil
}

func main() {
    if err := initializeApp(); err != nil {
        fmt.Printf("错误: %v\n", err)

        // 检查是否包含特定错误
        if errors.Is(err, errors.New("config file not found")) {
            fmt.Println("提示: 请检查配置文件是否存在")
        }

        // 解包错误获取原始错误
        if unwrapped := errors.Unwrap(err); unwrapped != nil {
            fmt.Printf("原始错误: %v\n", unwrapped)
        }
    }
}
```

### 2. 错误链处理

```go
package main

import (
    "errors"
    "fmt"
    "strings"
)

// 自定义错误类型
type NotFoundError struct {
    Resource string
    ID       string
}

func (e NotFoundError) Error() string {
    return fmt.Sprintf("%s not found: %s", e.Resource, e.ID)
}

func getUser(id string) error {
    if id == "invalid" {
        return NotFoundError{Resource: "User", ID: id}
    }
    return nil
}

func processUserData(userID string) error {
    if err := getUser(userID); err != nil {
        return fmt.Errorf("处理用户数据失败: %w", err)
    }
    return nil
}

func main() {
    if err := processUserData("invalid"); err != nil {
        fmt.Printf("完整错误链: %v\n", err)

        // 使用 errors.As 检查特定错误类型
        var notFoundErr NotFoundError
        if errors.As(err, &notFoundErr) {
            fmt.Printf("资源 '%s' ID '%s' 未找到\n",
                notFoundErr.Resource, notFoundErr.ID)
        }

        // 沿着错误链检查
        for err != nil {
            fmt.Printf("链中错误: %v\n", err)
            err = errors.Unwrap(err)
        }
    }
}
```

## 🚨 Panic和Recover机制

### 1. Panic的使用场景

Panic应该只在真正异常的情况下使用：

```go
package main

import (
    "fmt"
    "log"
)

func divide(a, b int) int {
    if b == 0 {
        // 除零错误属于程序逻辑错误，适合panic
        panic("division by zero")
    }
    return a / b
}

func accessSlice(s []int, index int) int {
    if index < 0 || index >= len(s) {
        // 数组越界属于严重错误
        panic(fmt.Sprintf("slice index out of range: %d", index))
    }
    return s[index]
}

func main() {
    defer func() {
        if r := recover(); r != nil {
            log.Printf("程序panic并恢复: %v", r)
        }
    }()

    fmt.Println("程序开始...")

    // 正常情况
    result := divide(10, 2)
    fmt.Printf("10 / 2 = %d\n", result)

    // 会触发panic的情况
    slice := []int{1, 2, 3}
    value := accessSlice(slice, 5) // 这里会panic
    fmt.Printf("访问结果: %d\n", value)

    fmt.Println("程序结束...")
}
```

### 2. Recover最佳实践

```go
package main

import (
    "fmt"
    "log"
    "runtime/debug"
)

// 安全的函数调用包装器
func safeCall(fn func()) (err error) {
    defer func() {
        if r := recover(); r != nil {
            // 记录panic堆栈信息
            log.Printf("panic recovered: %v\n%s", r, debug.Stack())
            err = fmt.Errorf("internal error: %v", r)
        }
    }()

    fn()
    return nil
}

// 业务函数
func riskyOperation(name string) {
    if name == "" {
        panic("name cannot be empty")
    }
    fmt.Printf("处理: %s\n", name)
}

func main() {
    fmt.Println("=== 安全函数调用示例 ===")

    // 正常调用
    err := safeCall(func() {
        riskyOperation("张三")
    })
    if err != nil {
        fmt.Printf("操作失败: %v\n", err)
    } else {
        fmt.Println("操作成功")
    }

    // 异常调用
    err = safeCall(func() {
        riskyOperation("") // 这会触发panic
    })
    if err != nil {
        fmt.Printf("操作失败: %v\n", err)
    } else {
        fmt.Println("操作成功")
    }
}
```

### 3. HTTP服务器中的错误处理

```go
package main

import (
    "fmt"
    "log"
    "net/http"
)

// 错误处理中间件
func errorHandler(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                log.Printf("panic in handler: %v", err)
                http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            }
        }()

        next(w, r)
    }
}

func businessHandler(w http.ResponseWriter, r *http.Request) {
    name := r.URL.Query().Get("name")
    if name == "" {
        panic("name parameter is required")
    }

    fmt.Fprintf(w, "Hello, %s!", name)
}

func main() {
    // 使用错误处理中间件包装处理器
    http.HandleFunc("/hello", errorHandler(businessHandler))

    fmt.Println("服务器启动在 :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

## 🎯 错误处理最佳实践

### 1. 错误处理原则

#### 原则1: 总是检查错误
```go
// ❌ 错误 - 忽略错误
data, _ := os.ReadFile("config.json")

// ✅ 正确 - 检查错误
data, err := os.ReadFile("config.json")
if err != nil {
    return fmt.Errorf("读取配置文件失败: %w", err)
}
```

#### 原则2: 提供上下文信息
```go
// ❌ 错误 - 缺少上下文
if err != nil {
    return err
}

// ✅ 正确 - 添加上下文
if err != nil {
    return fmt.Errorf("处理用户 %s 时失败: %w", userID, err)
}
```

#### 原则3: 避免错误处理中的错误
```go
// ❌ 危险 - 错误处理中可能发生新的错误
func safeClose(file *os.File) {
    if err := file.Close(); err != nil {
        log.Fatal(err) // 这可能导致程序退出
    }
}

// ✅ 安全 - 记录错误但不终止程序
func safeClose(file *os.File) {
    if err := file.Close(); err != nil {
        log.Printf("关闭文件失败: %v", err)
    }
}
```

### 2. 错误信息设计

#### 好的错误信息特征
```go
// ✅ 清晰、有用、可操作
func validatePassword(password string) error {
    if len(password) < 8 {
        return fmt.Errorf("密码长度不足，至少需要8个字符（当前: %d）", len(password))
    }

    if !containsUpperCase(password) {
        return fmt.Errorf("密码必须包含至少一个大写字母")
    }

    return nil
}

// ❌ 模糊、无用的错误信息
func badValidatePassword(password string) error {
    if len(password) < 8 {
        return errors.New("invalid password")
    }
    return nil
}
```

### 3. 性能考虑

```go
// ✅ 高效 - 使用预定义错误
var (
    ErrUserNotFound    = errors.New("user not found")
    ErrInvalidInput    = errors.New("invalid input")
    ErrPermissionDenied = errors.New("permission denied")
)

func getUser(id int) (*User, error) {
    if id <= 0 {
        return nil, ErrInvalidInput
    }
    // ... 查询逻辑
    return nil, ErrUserNotFound
}

// ❌ 低效 - 每次都创建新的错误字符串
func badGetUser(id int) (*User, error) {
    if id <= 0 {
        return nil, errors.New("invalid input") // 每次都分配新字符串
    }
    return nil, errors.New("user not found")
}
```

## 🔍 常见错误和注意事项

### 1. 错误处理反模式

#### 忽略错误
```go
// ❌ 永远不要这样做
file, _ := os.Open("important.txt")
file.Close()

// ✅ 总是处理错误
file, err := os.Open("important.txt")
if err != nil {
    return fmt.Errorf("打开文件失败: %w", err)
}
defer file.Close()
```

#### 错误信息中暴露敏感信息
```go
// ❌ 危险 - 可能暴露敏感信息
func connectDB() error {
    if err := sql.Open("mysql", "user:password@tcp(db:3306)/db"); err != nil {
        return fmt.Errorf("数据库连接失败: %s://%s@%s", user, password, host)
    }
}

// ✅ 安全 - 不暴露敏感信息
func connectDB() error {
    if err := sql.Open(dsn); err != nil {
        return fmt.Errorf("数据库连接失败，请检查配置")
    }
}
```

### 2. 测试中的错误处理

```go
func TestDivide(t *testing.T) {
    tests := []struct {
        name     string
        a, b     float64
        want     float64
        wantErr  bool
        errCheck func(error) bool
    }{
        {
            name:    "valid division",
            a:       10, b: 2,
            want:    5,
            wantErr: false,
        },
        {
            name:    "division by zero",
            a:       10, b: 0,
            want:    0,
            wantErr: true,
            errCheck: func(err error) bool {
                return err.Error() == "division by zero"
            },
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := divide(tt.a, tt.b)

            if tt.wantErr {
                if err == nil {
                    t.Errorf("divide() expected error, got nil")
                    return
                }
                if tt.errCheck != nil && !tt.errCheck(err) {
                    t.Errorf("divide() error = %v, want check failed", err)
                }
                return
            }

            if err != nil {
                t.Errorf("divide() unexpected error = %v", err)
                return
            }

            if got != tt.want {
                t.Errorf("divide() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

## 📊 实际应用示例

### 示例1: 文件处理工具

```go
package main

import (
    "fmt"
    "io"
    "os"
    "path/filepath"
)

// 文件处理错误类型
type FileProcessError struct {
    Operation string
    Filename  string
    Err       error
}

func (e FileProcessError) Error() string {
    return fmt.Sprintf("文件处理失败 [%s]: %s - %v",
        e.Operation, e.Filename, e.Err)
}

func (e FileProcessError) Unwrap() error {
    return e.Err
}

// 文件复制函数
func copyFile(src, dst string) error {
    // 检查源文件是否存在
    if _, err := os.Stat(src); os.IsNotExist(err) {
        return FileProcessError{
            Operation: "stat",
            Filename:  src,
            Err:       fmt.Errorf("源文件不存在"),
        }
    }

    // 创建目标目录
    if err := os.MkdirAll(filepath.Dir(dst), 0755); err != nil {
        return FileProcessError{
            Operation: "mkdir",
            Filename:  filepath.Dir(dst),
            Err:       err,
        }
    }

    // 打开源文件
    srcFile, err := os.Open(src)
    if err != nil {
        return FileProcessError{
            Operation: "open",
            Filename:  src,
            Err:       err,
        }
    }
    defer srcFile.Close()

    // 创建目标文件
    dstFile, err := os.Create(dst)
    if err != nil {
        return FileProcessError{
            Operation: "create",
            Filename:  dst,
            Err:       err,
        }
    }
    defer dstFile.Close()

    // 复制内容
    if _, err := io.Copy(dstFile, srcFile); err != nil {
        return FileProcessError{
            Operation: "copy",
            Filename:  fmt.Sprintf("%s -> %s", src, dst),
            Err:       err,
        }
    }

    return nil
}

func main() {
    src := "source.txt"
    dst := "backup/destination.txt"

    if err := copyFile(src, dst); err != nil {
        fmt.Printf("文件复制失败: %v\n", err)

        // 检查具体错误类型
        var fileErr FileProcessError
        if errors.As(err, &fileErr) {
            fmt.Printf("操作: %s\n", fileErr.Operation)
            fmt.Printf("文件: %s\n", fileErr.Filename)
        }

        os.Exit(1)
    }

    fmt.Printf("文件复制成功: %s -> %s\n", src, dst)
}
```

### 示例2: API错误处理

```go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
)

// API错误响应结构
type APIError struct {
    Code    string                 `json:"code"`
    Message string                 `json:"message"`
    Details map[string]interface{} `json:"details,omitempty"`
}

func (e APIError) Error() string {
    return fmt.Sprintf("API错误 [%s]: %s", e.Code, e.Message)
}

// 常用API错误
var (
    ErrInvalidRequest = APIError{
        Code:    "INVALID_REQUEST",
        Message: "请求参数无效",
    }

    ErrUnauthorized = APIError{
        Code:    "UNAUTHORIZED",
        Message: "未授权访问",
    }

    ErrResourceNotFound = APIError{
        Code:    "RESOURCE_NOT_FOUND",
        Message: "资源不存在",
    }
)

// HTTP错误响应写入器
func writeError(w http.ResponseWriter, err error) {
    w.Header().Set("Content-Type", "application/json")

    var apiErr APIError
    if errors.As(err, &apiErr) {
        // 已知的API错误
        switch apiErr.Code {
        case "INVALID_REQUEST":
            w.WriteHeader(http.StatusBadRequest)
        case "UNAUTHORIZED":
            w.WriteHeader(http.StatusUnauthorized)
        case "RESOURCE_NOT_FOUND":
            w.WriteHeader(http.StatusNotFound)
        default:
            w.WriteHeader(http.StatusInternalServerError)
        }
    } else {
        // 未知错误
        apiErr = APIError{
            Code:    "INTERNAL_ERROR",
            Message: "内部服务器错误",
        }
        w.WriteHeader(http.StatusInternalServerError)
    }

    json.NewEncoder(w).Encode(apiErr)
}

// 业务处理器
func getUserHandler(w http.ResponseWriter, r *http.Request) {
    userID := r.URL.Query().Get("id")
    if userID == "" {
        writeError(w, ErrInvalidRequest)
        return
    }

    if userID == "123" {
        // 模拟未找到用户
        err := ErrResourceNotFound
        err.Details = map[string]interface{}{
            "user_id": userID,
            "resource": "user",
        }
        writeError(w, err)
        return
    }

    // 成功响应
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]interface{}{
        "user_id": userID,
        "name":    "张三",
    })
}

func main() {
    http.HandleFunc("/user", getUserHandler)
    fmt.Println("API服务器启动在 :8080")
    http.ListenAndServe(":8080", nil)
}
```

## 🔗 文档交叉引用

### 相关文档
- 📄 **[函数和方法]**: [04-functions-methods.md](04-functions-methods.md) - 函数定义和方法调用
- 📄 **[Go编程精华]**: [../knowledge-points/language-concepts/03-go-programming-essentials.md](../knowledge-points/language-concepts/03-go-programming-essentials.md) - Go语言设计哲学
- 📄 **[Gin框架错误处理]**: [../frameworks/01-gin-framework-basics.md](../frameworks/01-gin-framework-basics.md) - Web框架错误处理

### 参考资源
- 📖 **[Go错误处理文档]**: https://golang.org/pkg/errors/
- 📖 **[Go博客: 错误处理]**: https://blog.golang.org/error-handling
- 📖 **[Go FAQ: 错误处理]**: https://golang.org/doc/faq#exceptions

## 📝 总结

### 核心要点回顾
1. **错误处理哲学**: 理解Go显式错误处理的设计理念
2. **error接口**: 掌握Go错误系统的核心机制
3. **自定义错误**: 学会创建有意义的错误类型
4. **错误包装**: 使用errors包进行错误链式处理
5. **panic/recover**: 了解异常情况的处理机制

### 实践练习
- [ ] 为不同的业务场景创建自定义错误类型
- [ ] 练习错误包装和解包操作
- [ ] 实现一个带有错误处理的HTTP API
- [ ] 编写测试验证错误处理的正确性
- [ ] 建立项目的错误处理规范

---

**文档状态**: ✅ 已完成
**最后更新**: 2025年10月
**版本**: v1.0.0

---

> 💡 **学习建议**:
> - 将错误处理视为程序设计的重要组成部分
> - 为不同层次的错误设计不同的处理策略
> - 在日志中记录足够的错误信息用于调试
> - 定期审查和改进错误处理逻辑
> - 避免过度使用panic，只在真正异常时使用
