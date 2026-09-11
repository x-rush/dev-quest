# net/http - HTTP 服务端与客户端

Go 标准库内置的 HTTP 实现，**无需任何第三方框架即可构建生产级服务**。本条目覆盖服务端路由、中间件模式与客户端请求全流程。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `reference/library-guides` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#net-http` `#HTTP` `#服务端` `#客户端` `#标准库` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 1. 服务端：Handler 与 ServeMux

### 核心类型

- `http.Handler` 接口：只有一个方法 `ServeHTTP(w, r)`
- `http.HandlerFunc` 函数适配器：让普通函数直接当 Handler 用
- `http.ServeMux`：多路复用器（路由器），按模式分发请求
- `http.ResponseWriter` / `*http.Request`：写响应与读请求的两个核心参数

### Go 1.22+ 增强路由

Go 1.22 重写了 ServeMux，支持**方法匹配**与**路径通配符**，多数场景不再需要第三方路由器：

```go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
)

type User struct {
    Name  string `json:"name"`
    Email string `json:"email"`
}

func userHandler(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id") // 捕获 {id} 通配符

    user := User{Name: "用户" + id, Email: "user" + id + "@example.com"}
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user) // 结构体直接序列化为 JSON
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintln(w, "ok") // Fprintln 直接写响应体
}

func newMux() *http.ServeMux {
    mux := http.NewServeMux()
    // "METHOD /path/{wildcard}" 模式语法
    mux.HandleFunc("GET /users/{id}", userHandler) // 方法不匹配自动返回 405
    mux.HandleFunc("GET /health", healthHandler)
    return mux
}

func main() {
    if err := http.ListenAndServe(":8080", newMux()); err != nil {
        panic(err)
    }
}
```

实测行为（go 1.25）：
- `GET /users/42` → 200，`r.PathValue("id")` 返回 `"42"`
- `POST /users/42` → **自动返回 405 Method Not Allowed**（无需手写）
- 精确模式优先于通配符模式；以 `/` 结尾的通配符匹配子树

**常用模式语法**：`GET /items/{id}`（单段）、`GET /files/{path...}`（剩余全部，含斜杠）、`{$}`（精确匹配根路径）。

## 2. 服务端：中间件模式

中间件是"接收 Handler、返回 Handler"的函数，利用 Go 闭包实现横切关注点（日志、鉴权、恢复 panic）：

```go
func logging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r) // 调用链中的下一个 Handler
        log.Printf("%s %s %s", r.Method, r.URL.Path, time.Since(start))
    })
}

func recoverPanic(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                http.Error(w, "internal error", http.StatusInternalServerError)
            }
        }()
        next.ServeHTTP(w, r)
    })
}

// 链式包裹：请求依次经过 recover → logging → 业务 Handler
mux := recoverPanic(logging(newMux()))
```

## 3. 客户端：请求全流程

**关键纪律**：用 `NewRequestWithContext` 携带超时/取消语义；必须 `defer resp.Body.Close()`；必须自己检查 `StatusCode`（4xx/5xx **不会**自动返回 error）。

```go
func fetchUser(baseURL, id string) (*User, error) {
    // 3 秒超时，超时或取消时请求中断
    ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
    defer cancel()

    req, err := http.NewRequestWithContext(ctx, http.MethodGet,
        baseURL+"/users/"+id, nil)
    if err != nil {
        return nil, fmt.Errorf("构造请求: %w", err)
    }
    req.Header.Set("Accept", "application/json")

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, fmt.Errorf("请求失败: %w", err)
    }
    defer resp.Body.Close() // 必须！否则连接无法复用直至泄漏

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("意外状态码: %d %s", resp.StatusCode, resp.Status)
    }

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, fmt.Errorf("读取响应体: %w", err)
    }

    var u User
    if err := json.Unmarshal(body, &u); err != nil {
        return nil, fmt.Errorf("解析 JSON: %w", err)
    }
    return &u, nil
}
```

### 简易快捷方法

无 body 的简单 GET 可用 `http.Get(url)`；但 `http.Get/http.Post` 使用 `http.DefaultClient`——**它没有超时**，生产代码应使用自定义 Client：

```go
client := &http.Client{Timeout: 5 * time.Second} // 覆盖连接+请求全流程
resp, err := client.Get("https://api.example.com/health")
```

## ⚠️ 常见陷阱

| 陷阱 | 后果 | 正确做法 |
|------|------|----------|
| 忘记 `resp.Body.Close()` | 连接泄漏，文件描述符耗尽 | 拿到 resp 立即 defer Close |
| 不检查 `resp.StatusCode` | 4xx/5xx 被当成正常响应处理 | 显式检查状态码 |
| 用 `http.DefaultClient` 发生产请求 | 无超时，可能永久挂起 | `&http.Client{Timeout: ...}` |
| `w.Write` 前未设置 Header | Header 修改无效（已隐式 200） | 先 `w.Header().Set` 再 Write |
| Handler 里启动 goroutine 后返回 | Handler 用的 request 会被复用/取消 | 需要异步时复制所需值（`r.Clone` 或提取字段） |

## 🔗 交叉引用

- **教程路径**: [basics/02-first-program.md](../../basics/02-first-program.md) → [frameworks/01-gin-framework-basics.md](../../frameworks/01-gin-framework-basics.md)（Gin 是 net/http 之上的路由增强层）
- **实战项目**: [projects/01-rest-api-server.md](../../projects/01-rest-api-server.md)（生产级 REST 服务）
- **并发基础**: [basics/07-concurrency-basics.md](../../basics/07-concurrency-basics.md)（每个请求就是一个 goroutine）
- **官方文档**: https://pkg.go.dev/net/http

---

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0
