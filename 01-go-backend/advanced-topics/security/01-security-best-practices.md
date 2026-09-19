# Go 安全实践：从输入到对象授权

前置知识：能写 HTTP handler、处理错误和执行参数化 SQL。本文以“用户修改自己的待办标题”为主线，先实现输入与对象权限，再说明 JWT、密码、浏览器和部署边界。目标是能用反例验证拒绝行为，而不是只安装一个认证中间件。

## 1. 先区分三道判断

| 判断 | 回答的问题 | 示例 |
|---|---|---|
| 认证 | 这是谁？ | 可信会话或验证完成的令牌识别用户 7 |
| 输入验证 | 这个请求是否合法？ | 标题非空、长度合理，没有未知字段 |
| 对象授权 | 他能改这一条吗？ | 待办 42 的 owner_id 必须是用户 7 |

合法 ID、有效 JWT、管理员字段格式正确，都不能代替对象授权。请求中的 `user_id`、`owner_id`、`role` 不决定当前身份。创建记录时，由服务端身份填写 owner；更新时，在同一个数据库操作里用 `WHERE id = ? AND owner_id = ?` 约束对象，检查受影响行数，避免检查后对象归属改变。

## 2. 可运行的输入与对象授权案例

下面保存为 `main.go`，运行 `go run main.go`。只依赖标准库，不启动公网服务。程序覆盖正常请求、空标题、未知字段、连续 JSON、超大正文和跨用户更新。输出应为 `security-boundaries: 6 checks passed`，任一错误接受都会 panic。

<!-- security-check: go-boundaries -->
```go
package main

import (
    "encoding/json"
    "errors"
    "fmt"
    "io"
    "net/http"
    "net/http/httptest"
    "strings"
    "unicode/utf8"
)

type updateInput struct { Title string `json:"title"` }
type todo struct { OwnerID int; Title string }

func readUpdate(w http.ResponseWriter, r *http.Request) (updateInput, error) {
    // 每次调用分配自己的 DTO；不要把同一个 *updateInput 捕获在中间件闭包中。
    var input updateInput
    r.Body = http.MaxBytesReader(w, r.Body, 4096)
    defer r.Body.Close()
    decoder := json.NewDecoder(r.Body)
    decoder.DisallowUnknownFields()
    if err := decoder.Decode(&input); err != nil { return input, err }
    var extra any
    if err := decoder.Decode(&extra); err != io.EOF {
        return input, errors.New("body must contain exactly one JSON value")
    }
    input.Title = strings.TrimSpace(input.Title)
    if input.Title == "" || utf8.RuneCountInString(input.Title) > 100 {
        return input, errors.New("title must contain 1 to 100 code points")
    }
    return input, nil
}

func updateTitle(currentUserID int, item *todo, title string) error {
    // currentUserID 来自认证结果；示例只讨论内存对象，真实存储在事务中约束权限。
    if currentUserID <= 0 || currentUserID != item.OwnerID {
        return errors.New("not found or not allowed")
    }
    item.Title = title
    return nil
}

func main() {
    cases := []struct { body string; accept bool }{
        {`{"title":"  学习 Go  "}`, true},
        {`{"title":" "}`, false},
        {`{"title":"x","owner_id":99}`, false},
        {`{"title":"x"} {"title":"y"}`, false},
        {`{"title":"` + strings.Repeat("x", 5000) + `"}`, false},
    }
    for _, tc := range cases {
        r := httptest.NewRequest(http.MethodPatch, "/todos/42", strings.NewReader(tc.body))
        input, err := readUpdate(httptest.NewRecorder(), r)
        if (err == nil) != tc.accept { panic("unexpected input decision") }
        if tc.accept && input.Title != "学习 Go" { panic("normalization failed") }
    }
    item := todo{OwnerID: 7, Title: "original"}
    if updateTitle(8, &item, "stolen") == nil || item.Title != "original" {
        panic("cross-user update allowed")
    }
    fmt.Println("security-boundaries: 6 checks passed")
}
```

这里的长度按 Unicode 码点计数，不是用户看到的字形数；正文大小按字节限制。外层 handler 还要检查请求 `Content-Type`、将错误映射为约定的 400/413/415，并在认证之前设置合理的服务器超时与入口流量限制。`encoding/json` 会接受重复字段并使用后值；若签名、代理或下游使用不同 JSON 解释规则，应在协议层拒绝重复字段。这个小例没有实现完整认证服务。

## 3. JWT 验证必须绑定服务端策略

适用情形：服务接受可信签发方的访问令牌。JWT 签名不隐藏内容；payload 不放密码或私密正文。以下是 `github.com/golang-jwt/jwt/v5` 的集成片段，放入项目的 `auth` 包，依赖版本由 `go.mod`/`go.sum` 锁定；它不是上一节标准库运行案例的一部分。

```go
package auth

import (
    "errors"
    "github.com/golang-jwt/jwt/v5"
)

func ValidateToken(raw string, key []byte) (*jwt.RegisteredClaims, error) {
    // HS256 密钥至少 32 随机字节，由服务端密钥系统配置，不从请求取值。
    if len(key) < 32 { return nil, errors.New("invalid signing-key configuration") }
    claims := new(jwt.RegisteredClaims)
    token, err := jwt.ParseWithClaims(raw, claims,
        func(_ *jwt.Token) (any, error) { return key, nil },
        jwt.WithValidMethods([]string{"HS256"}),
        jwt.WithIssuer("https://auth.example.com"),
        jwt.WithAudience("todo-api"),
        jwt.WithExpirationRequired(),
    )
    // 必须先处理解析失败；畸形输入时 token 可能为 nil。
    if err != nil { return nil, err }
    if token == nil || !token.Valid || claims.Subject == "" {
        return nil, errors.New("invalid access token")
    }
    return claims, nil
}
```

`iss` 标识签发方，`aud` 限定接收服务，`sub` 标识主体，`exp` 限定过期时间。仅校验签名会误接收发给其他服务的合法令牌。多个签发方各自绑定算法、密钥与受众；不能根据未验证 payload 任意下载密钥 URL。HS256 的验签方也能签发令牌，需要分离签发权限时使用公钥验签方案。

验收时用测试密钥签发：正确令牌、错误签名、过期、缺 exp、错误/缺 iss、错误/缺 aud、空 sub、算法不符；再传空串和乱码。只有正确令牌通过，其余不得 panic。随后用正确令牌请求其他用户的对象，仍必须拒绝。令牌撤销、用户封禁和角色变化的生效时间需要另行设计；短有效期不能立即撤销已签发令牌。

依据：[jwt/v5 解析选项](https://golang-jwt.github.io/jwt/usage/parse/)、[WithExpirationRequired API](https://pkg.go.dev/github.com/golang-jwt/jwt/v5#WithExpirationRequired)。

## 4. 密码、SQL 和输出分别处理

密码使用专用密码哈希而不是可逆加密或单次 SHA-256。新系统可按资源预算评估 Argon2id；保留 bcrypt 的系统要处理其 72 字节输入上限，不能静默截断，中文字符的 UTF-8 字节数尤其容易超过限制。注册与登录使用相同规则，参数通过目标机器压测选择。不存在的账号与密码错误向客户端提供一致提示，并按账号与来源限制尝试；不要把哈希或令牌写进日志。

SQL 用驱动参数占位：例如 `db.ExecContext(ctx, "UPDATE todos SET title = ? WHERE id = ? AND owner_id = ?", title, id, userID)` 是采用 `?` 占位的驱动片段；PostgreSQL 驱动通常用 `$1` 等占位符。值绑定不能绑定表名或排序方向；动态排序用服务端允许列表映射，未知输入拒绝。修改操作检查 `RowsAffected`，并定义“对象不存在”和“不可访问”的统一响应策略。

输出到 HTML 时用 `html/template` 的上下文编码，不把用户文本强制转换为 `template.HTML`。JSON 编码不能自动保障 HTML、脚本、URL 等其他上下文安全。富文本需要受控标签、属性和协议清洗；上传文件除尺寸和内容类型外，还要随机命名、限制读取权限、放入不可执行存储，并防符号链接和路径穿越。

## 5. 浏览器与部署验收

| 触发条件 | 处理与验收 |
|---|---|
| 浏览器自动附带 Cookie 或其他凭据 | 写请求做 CSRF 防护；分别发送缺失、错误、正确 token，确认前两者不能产生写入。SameSite 是附加防线 |
| API 使用显式 Authorization Bearer | 确认服务确实不接受 Cookie/Basic 等自动凭据后，再评估 CSRF 策略。CORS 不能替代认证授权 |
| 接入反向代理 | 只信任已配置代理的转发头；伪造客户端 IP 不能绕过限流；HTTPS、内部传输和超时分别验收 |
| 密钥轮换 | 先部署新验证钥、切换签发钥，再在约定窗口结束后撤销旧钥；泄漏时需要紧急撤销策略 |
| 拒绝请求与异常 | 响应包含稳定错误码和请求 ID；受控日志记录事件与主体标识，不记录密码、Cookie、Authorization 或完整请求体 |

**完成练习**：在 [REST API 项目](../../projects/01-rest-api-server.md) 中接入这些边界，建立两用户测试；验证别人记录不可读写、超大正文不会写库、未知 owner 字段不生效、无效令牌不触发 500。静态代码检查和 `govulncheck` 可发现部分问题，不能替代这些业务验证。

延伸依据：[Go JSON 解码](https://pkg.go.dev/encoding/json#Decoder.DisallowUnknownFields)、[bcrypt 输入边界](https://pkg.go.dev/golang.org/x/crypto/bcrypt)、[OWASP 密码存储](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
