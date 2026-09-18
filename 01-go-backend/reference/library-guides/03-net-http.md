# net/http - HTTP 服务端与客户端

Go 标准库内置的 HTTP 实现，可以不依赖第三方框架提供 HTTP 服务；生产使用仍需配置超时、资源限制、日志和关停策略。本条目覆盖服务端路由、中间件模式与客户端请求全流程。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

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

</details>

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

以下函数片段需与 User 定义放在同一包，并导入 context、encoding/json、fmt、io、net/http、net/url、time。baseURL 应由可信配置提供；不能直接接受任意用户地址。

**关键纪律**：用 `NewRequestWithContext` 携带超时/取消语义；必须 `defer resp.Body.Close()`；必须自己检查 `StatusCode`（4xx/5xx **不会**自动返回 error）。

```go
func fetchUser(parent context.Context, baseURL, id string) (*User, error) {
    // 3 秒超时，超时或取消时请求中断
    ctx, cancel := context.WithTimeout(parent, 3*time.Second)
    defer cancel()

    req, err := http.NewRequestWithContext(ctx, http.MethodGet,
        baseURL+"/users/"+url.PathEscape(id), nil)
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

    const maxBody = 1 << 20 // 示例上限 1 MiB
    body, err := io.ReadAll(io.LimitReader(resp.Body, maxBody+1))
    if err != nil {
        return nil, fmt.Errorf("读取响应体: %w", err)
    }

    if len(body) > maxBody { return nil, fmt.Errorf("响应体超过大小上限") }
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
| 未设置 Client 或请求 context 的超时 | 可能无限等待 | 设置整体预算，并向下传递取消信号 |
| `w.Write` 前未设置 Header | Header 修改无效（已隐式 200） | 先 `w.Header().Set` 再 Write |
| Handler 返回后继续写响应或使用请求生命周期 | ResponseWriter 已失效，请求 context 会取消 | 提取必要数据，为独立任务明确生命周期；Clone 仍可能共享 Body，不能自动解决问题 |

## 🔗 交叉引用

- **教程路径**: [basics/02-first-program.md](../../basics/02-first-program.md) → [frameworks/01-gin-framework-basics.md](../../frameworks/01-gin-framework-basics.md)（Gin 是 net/http 之上的路由增强层）
- **实战项目**: [projects/01-rest-api-server.md](../../projects/01-rest-api-server.md)（生产级 REST 服务）
- **并发基础**: [basics/07-concurrency-basics.md](../../basics/07-concurrency-basics.md)（每个请求就是一个 goroutine）
- **官方文档**: https://pkg.go.dev/net/http

---

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0


<!-- full-library-explanation -->
## 一次请求从进入到释放资源

前置是函数、接口、JSON 和 context。Handler 运行期间读取请求、验证身份和输入，再调用业务逻辑，最后写响应。首次 Write 会隐式提交 200；此后再设置状态码不能撤销已经发出的数据。因此 JSON 编码可能失败时，可先在大小受控的缓冲区完成编码，再提交响应。示例 recover 中间件只能展示恢复位置，无法把已经部分写出的成功响应变回完整的 500，生产实现还应记录错误并处理连接或流中断。

客户端的网络错误与 HTTP 业务状态是两层问题：Do 返回 nil error 只说明拿到了响应，404/500 仍需要调用者判断。复用 Client 和 Transport 才能复用连接池；关闭 Body 释放资源，读取至 EOF 通常有利于 HTTP/1 连接复用，但不要为了复用而无限读取不可信响应。限制大小、检查状态、关闭响应体应同时做到。

练习：用 httptest.NewRecorder 和 httptest.NewRequest 调用 newMux，分别断言 GET /users/42 为 200、POST 同路径为 405、未知路径为 404，并解码成功响应。GET 模式也匹配 HEAD；不要把“只注册 GET”误当作拒绝 HEAD。再用 httptest.Server 模拟 500 与超过大小上限的响应，fetchUser 都应返回错误。请求完成后不得继续使用 ResponseWriter，异步可靠工作应有独立生命周期。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
