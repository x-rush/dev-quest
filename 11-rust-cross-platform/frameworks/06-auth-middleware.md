# Axum 0.8 认证中间件：JWT 守卫与自定义 Extractor

## 先看框架承担哪部分职责

**Axum 认证**：认证解释是谁，授权解释能否访问某个资源。有效 JWT 只证明签名和声明满足检查，不自动证明用户拥有目标记录。

**最小练习与预期结果**：用两个用户分别读写同一 ID，验证资源级拒绝；再测试过期与缺失令牌，不泄露内部错误。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 给 Axum 0.8 API 加上身份防线——用 `route_layer` 挂 JWT 守卫中间件（404 请求不误伤）、jsonwebtoken 11 完成签发与校验、自定义 `FromRequestParts` extractor 把用户身份递到 handler 签名里，形成"中间件校验一次、extractor 处处取用"的分层。
>
> **目标读者**: 已会用 Axum Router/extractor（frameworks 04）、要做受保护 API 的后端开发者
>
> **前置知识**: [Axum Web 栈](./04-axum-web-stack.md)（layer/route_layer 语义）、[状态与数据库 SQLx](./05-state-and-database-sqlx.md)（AppState 共享模式）
>
> **预计时长**: 3-4 小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 操作指南（frameworks/） |
| **难度** | ⭐⭐⭐ 高级 |
| **标签** | `#rust` `#axum` `#jwt` `#auth` `#middleware` |
| **更新日期** | `2026年9月` |

</details>

> 版本基线见模块 [README](../README.md)：Axum 0.8 / Tokio 1.53 / Serde 1.0.229（2026-09-16 核实）；jsonwebtoken 11.0（docs.rs 2026-07-24 发布）。

## 🎯 学习目标

完成本篇后，你将能够：

- ✅ **选对挂载点**: 说清 handler 内判断 / `layer` / `route_layer` 三种认证挂点的差异
- ✅ **校验 JWT**: 用 jsonwebtoken 11 的 decode + Validation 完成"签名 + 过期 + 声明"一揽子校验
- ✅ **写自定义 Extractor**: 实现 0.8 原生 async trait 形态的 `FromRequestParts`，从 extensions 读取身份
- ✅ **组装守卫路由**: 让 `/api/*` 全部受保护、`/login` 与 404 不受影响

## 📋 目录

- [核心概念](#-核心概念)
- [实践指南](#️-实践指南)
- [代码示例](#-代码示例)
- [最佳实践](#-最佳实践)
- [常见问题](#-常见问题)
- [模式不变量](#-模式不变量)
- [相关资源](#-相关资源)

---

## 🔍 核心概念

### 概念一：认证挂在哪一层——三种挂点对比

**定义**: 同一个"校验 Bearer 令牌"逻辑，可以挂在三个位置，行为差异决定了正确性：

| 挂点 | 校验时机 | 404 请求 | 适用场景 |
|------|---------|---------|---------|
| handler 内部 | 业务逻辑中 | 不涉及 | 仅个别路由需要、且判断依赖业务数据 |
| `Router::layer` | 路由匹配**前** | **也过守卫**（404 → 401 泄露路径情报） | 全局横切（日志/CORS），不适合认证 |
| `Router::route_layer` | 路由命中后、handler 前 | **绕过守卫**（保持 404） | 认证守卫的标准答案 |

`route_layer` 的文档给出明确动机：让提前返回的中间件"不会把 404 Not Found 变成 401 Unauthorized"。另有一个编译期约束：**在没有任何路由时调用 `route_layer` 会 panic**——它必须"先有路由、后挂守卫"。

### 概念二：JWT 校验的责任边界——decode 一次做完什么

**定义**: jsonwebtoken 11 的 `decode` 是校验的唯一入口，一次调用同时完成三件事：

```rust
// 核心签名（jsonwebtoken 11.0，docs.rs 核证）
jsonwebtoken::decode::<Claims>(
    token,                                            // impl AsRef<[u8]>
    &DecodingKey::from_secret(secret.as_ref()),       // 对称密钥
    &Validation::new(Algorithm::HS256),
) // -> Result<TokenData<Claims>, jsonwebtoken::errors::Error>
```

1. **签名验证**: 用密钥重算签名并比对，防伪造
2. **标准声明校验**: `Validation` 默认 `validate_exp: true`（过期拒绝）、`leeway: 60`（容忍 60 秒时钟偏移）、`required_spec_claims: {"exp"}`（缺 exp 直接拒）
3. **反序列化**: 通过校验的 payload 反序列化为你的 `Claims` 结构（`exp: usize`，秒级 Unix 时间戳）

**推论**: 业务代码只应见到"校验通过后的 Claims"，任何 handler 都不碰原始 token——校验点必须唯一。

### 概念三：extensions 传值 + 自定义 Extractor

**定义**: 中间件与 handler 之间没有参数通道，标准做法是中间件把校验产物 `req.extensions_mut().insert(claims)` 放进请求的 extensions，再写一个 extractor 统一取出：

- `FromRequestParts` 在 Axum 0.8 是**原生 async trait**（RPITIT），实现里直接写 `async fn from_request_parts`，不需要 `#[async_trait]`
- extractor 的 `type Rejection` 决定失败响应：实现 `IntoResponse` 后，handler 里照样可以用 `Result`/直接参数两种形态

这一组合的收益：**decode 只在中间件发生一次**，handler 用 `AuthUser` 参数拿到的是中间件写入的身份结果；万一中间件漏挂，extractor 拿不到值会返回 500——把接线错误暴露成服务端错误而不是放行。

---

## 🛠️ 实践指南

### 步骤一：声明依赖

**目标**: 建立可编译的认证工程骨架

**操作指南**:

```toml
# auth-api/Cargo.toml
[package]
name = "auth-api"
version = "0.1.0"
edition = "2024"

[dependencies]
# 版本基线见模块 README（Axum 0.8 / Tokio 1.53 / Serde 1.0.229）
axum = "0.8"
tokio = { version = "1.53", features = ["macros", "rt-multi-thread", "net"] }
serde = { version = "1.0.229", features = ["derive"] }
jsonwebtoken = "11"   # JWT 签发与校验（2026-07-24 发布 11.0）
```

**验证方法**: `cargo build` 通过。

### 步骤二：提取 Authorization 头（去依赖化纯函数）

**目标**: 把 `Authorization: Bearer <token>` 头解析成可独立测试的纯函数

**操作指南**: 落地下方"示例三"的 `extract_bearer`：`splitn(2, ' ')` 拆方案名与令牌，方案名大小写不敏感（RFC 7235 规定 auth-scheme 不区分大小写），空令牌与缺空格分别报错。

**验证方法**: 该块不依赖任何第三方 crate，已用 `rustc --edition 2024` 本机实测（6 项断言全部通过），可直接 `rustc extract.rs && ./extract` 复现。

### 步骤三：签发与校验 JWT

**目标**: `login` 签发令牌、中间件校验令牌

**操作指南**: 落地"示例一"的 `issue_token`/`verify_token`：`exp` 用 `std::time::SystemTime` 现算秒级时间戳加一小时；校验侧 `Validation::new(Algorithm::HS256)` 走默认规则。

**验证方法**: `curl` 拿到 token 后原样放进 Authorization 头访问受保护路由返回 200；篡改 token 任一字符返回 401。

### 步骤四：挂 route_layer 守卫

**目标**: `/api/*` 全部受保护，`/login` 与 404 保持原语义

**操作指南**: 落地"示例二"——受保护子 Router **先注册路由、再 `route_layer`**，主 Router 用 `nest("/api", ...)` 挂载。

**验证方法**: `curl /api/me`（带 token）200、不带 401；`curl /api/不存在` 仍是 404 而非 401。

---

## 💻 代码示例

### 示例一：auth.rs——Claims、签发、校验、守卫中间件、自定义 Extractor

```rust
// src/auth.rs —— 认证关注点的唯一归属地
use axum::{
    extract::{FromRequestParts, Request, State},
    http::request::Parts,
    middleware::Next,
    response::{IntoResponse, Response},
    StatusCode,
};
use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};
use serde::{Deserialize, Serialize};

// ---- 应用状态（生产环境与 PgPool 合并，见 05 篇）----
#[derive(Clone)]
pub struct AppState {
    pub jwt_secret: String, // 真实项目从环境变量读取，绝不硬编码进仓库
}

// ---- 1) 声明集：exp 是 usize 秒级时间戳（jsonwebtoken 要求）----
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Claims {
    pub sub: String, // 主题：用户标识
    pub role: String,
    pub exp: usize,
}

// ---- 2) 签发：SystemTime 现算 exp，避免引第三方时间库 ----
pub fn issue_token(sub: &str, role: &str, secret: &str) -> Result<String, jsonwebtoken::errors::Error> {
    let exp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .expect("系统时钟早于 Unix 纪元")
        .as_secs() as usize
        + 3600; // 1 小时有效期
    let claims = Claims { sub: sub.to_owned(), role: role.to_owned(), exp };
    encode(&Header::default(), &claims, &EncodingKey::from_secret(secret.as_ref()))
}

// ---- 3) 校验：decode 一次完成 签名 + exp + 必需声明 三重检查 ----
pub fn verify_token(token: &str, secret: &str) -> Result<Claims, jsonwebtoken::errors::Error> {
    decode::<Claims>(
        token,
        &DecodingKey::from_secret(secret.as_ref()),
        &Validation::new(jsonwebtoken::Algorithm::HS256),
    )
    .map(|data| data.claims)
}

// ---- 4) 错误类型：认证失败 → 401；接线失误（没过中间件）→ 500 ----
#[derive(Debug, PartialEq, Eq)]
pub enum AuthError {
    Malformed,   // 头格式无法解析
    Unsupported, // 认证方案不是 Bearer
    EmptyToken,  // Bearer 后没有令牌
    Missing,     // extensions 里没有 Claims（守卫没挂上）
}

impl std::fmt::Display for AuthError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let msg = match self {
            AuthError::Malformed => "Authorization 头格式无效",
            AuthError::Unsupported => "不支持的认证方案（仅接受 Bearer）",
            AuthError::EmptyToken => "Bearer 后令牌为空",
            AuthError::Missing => "服务端守卫未生效（内部错误）",
        };
        write!(f, "{msg}")
    }
}

impl IntoResponse for AuthError {
    fn into_response(self) -> Response {
        let status = match self {
            AuthError::Missing => StatusCode::INTERNAL_SERVER_ERROR, // 接线错误不放行为 401
            _ => StatusCode::UNAUTHORIZED,
        };
        (status, self.to_string()).into_response()
    }
}

// ---- 5) 守卫中间件：唯一 decode 点，产物流入 extensions ----
pub async fn require_auth(
    State(state): State<AppState>,
    mut req: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let header = req
        .headers()
        .get(axum::http::header::AUTHORIZATION)
        .and_then(|v| v.to_str().ok())
        .ok_or(StatusCode::UNAUTHORIZED)?;

    let token = extract_bearer(header).map_err(|_| StatusCode::UNAUTHORIZED)?;
    let claims = verify_token(token, &state.jwt_secret).map_err(|_| StatusCode::UNAUTHORIZED)?;

    req.extensions_mut().insert(claims);
    Ok(next.run(req).await)
}

// extract_bearer 与示例三完全一致（独立纯函数，可单测）
pub fn extract_bearer(header_value: &str) -> Result<&str, AuthError> {
    let mut parts = header_value.splitn(2, ' ');
    match (parts.next(), parts.next()) {
        (Some(scheme), Some(token)) if scheme.eq_ignore_ascii_case("bearer") => {
            let token = token.trim();
            if token.is_empty() { Err(AuthError::EmptyToken) } else { Ok(token) }
        }
        (Some(_), Some(_)) => Err(AuthError::Unsupported),
        _ => Err(AuthError::Malformed),
    }
}

// ---- 6) 自定义 Extractor：0.8 原生 async trait，无 #[async_trait] ----
pub struct AuthUser(pub Claims);

impl<S: Send + Sync> FromRequestParts<S> for AuthUser {
    type Rejection = AuthError;

    async fn from_request_parts(parts: &mut Parts, _state: &S) -> Result<Self, Self::Rejection> {
        parts
            .extensions
            .get::<Claims>()
            .cloned()
            .map(AuthUser)
            .ok_or(AuthError::Missing)
    }
}
```

**关键点解析**:
- `require_auth` 的参数排布遵守 `from_fn_with_state` 约定：extractor（`State`）在前，`Request` 与 `Next` 殿后
- 校验失败一律 401 且**不回显失败原因细节**（签名错/过期对客户端是同一件事，减少信息泄露）
- `AuthError::Missing` 映射 500 而非 401：它只会在"路由没挂守卫却用了 AuthUser"时发生，是服务端 bug

### 示例二：main.rs——登录路由 + 受保护子路由组装

```rust
// src/main.rs
mod auth;

use axum::{
    extract::State,
    middleware,
    routing::{get, post},
    Json, Router,
};
use auth::{issue_token, require_auth, AppState, AuthUser, Claims};
use serde::Deserialize;

#[derive(Deserialize)]
struct LoginRequest {
    username: String,
}

#[derive(serde::Serialize)]
struct TokenResponse {
    token: String,
}

// 演示级登录：真实实现接数据库与密码哈希（见 05 篇 PgPool）
async fn login(
    State(state): State<AppState>,
    Json(req): Json<LoginRequest>,
) -> Result<Json<TokenResponse>, StatusCode> {
    if req.username.trim().is_empty() {
        return Err(StatusCode::UNAUTHORIZED);
    }
    let token = issue_token(&req.username, "user", &state.jwt_secret)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    Ok(Json(TokenResponse { token }))
}

// 身份从 extractor 参数拿到——handler 里没有任何 JWT 代码
async fn me(AuthUser(user): AuthUser) -> Json<String> {
    Json(format!("你好 {}，角色 {}", user.sub, user.role))
}

#[tokio::main]
async fn main() {
    let state = AppState {
        jwt_secret: std::env::var("JWT_SECRET").expect("缺少 JWT_SECRET 环境变量"),
    };

    // 受保护子路由：先注册路由，后 route_layer（顺序即正确性）
    let protected = Router::new()
        .route("/me", get(me))
        .route_layer(middleware::from_fn_with_state(state.clone(), require_auth));

    let app = Router::new()
        .route("/login", post(login))
        .nest("/api", protected)
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

**关键点解析**:
- `route_layer` 只包裹"此前已注册"的 `/me`；`/login` 在另一个 Router 上，天然不受影响
- 404 请求不经过守卫：未登录探测 `/api/xxx` 得到 404，不泄露"这里其实有守卫"的信号
- `AuthUser(user): AuthUser` 参数失败时自动由 `Rejection`（AuthError::Missing → 500）应答

### 示例三：Authorization 头解析纯函数（去依赖化练习）

> 以下块不依赖任何第三方 crate。保存为 `extract.rs` 后，以 `rustc --edition 2024 extract.rs && ./extract` 运行；应看到 `extract_bearer 6 项断言完成`。示例一中的 `extract_bearer` 即取自这里。目标框架与路由接线仍需在 Axum 工程中另行测试。

```rust
// Authorization 头解析（去依赖化演示）
// 正文中的 from_fn_with_state 中间件与 FromRequestParts 实现都复用这一纯函数
use std::fmt;

#[derive(Debug, PartialEq, Eq)]
pub enum AuthError {
    Malformed,   // 头格式无法解析
    Unsupported, // 认证方案不是 Bearer
    EmptyToken,  // Bearer 后没有令牌
}

impl fmt::Display for AuthError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let msg = match self {
            AuthError::Malformed => "Authorization 头格式无效",
            AuthError::Unsupported => "不支持的认证方案（仅接受 Bearer）",
            AuthError::EmptyToken => "Bearer 后令牌为空",
        };
        write!(f, "{msg}")
    }
}

/// 从 Authorization 头值中提取 Bearer 令牌。
/// 方案名大小写不敏感（RFC 7235：auth-scheme 不区分大小写）。
pub fn extract_bearer(header_value: &str) -> Result<&str, AuthError> {
    let mut parts = header_value.splitn(2, ' ');
    match (parts.next(), parts.next()) {
        (Some(scheme), Some(token)) if scheme.eq_ignore_ascii_case("bearer") => {
            let token = token.trim();
            if token.is_empty() {
                Err(AuthError::EmptyToken)
            } else {
                Ok(token)
            }
        }
        (Some(_), Some(_)) => Err(AuthError::Unsupported),
        _ => Err(AuthError::Malformed),
    }
}

fn main() {
    assert_eq!(
        extract_bearer("Bearer eyJhbG.eyJzdC.SflKxw"),
        Ok("eyJhbG.eyJzdC.SflKxw")
    );
    assert_eq!(extract_bearer("bearer abc123"), Ok("abc123")); // 方案名大小写不敏感
    assert_eq!(extract_bearer("Bearer   padded  "), Ok("padded")); // 容忍多余空白
    assert_eq!(extract_bearer("Basic dXNlcjpwYXNz"), Err(AuthError::Unsupported));
    assert_eq!(extract_bearer("Bearer "), Err(AuthError::EmptyToken));
    assert_eq!(extract_bearer("BearerBearer"), Err(AuthError::Malformed));
    println!("extract_bearer 6 项断言全部通过");
}
```

### 示例四：端到端验证序列（bash，只写不执行）

```bash
# 1) 启动服务（JWT_SECRET 必须先注入）
JWT_SECRET="dev-only-secret" cargo run

# 2) 登录换取令牌
TOKEN=$(curl -s http://localhost:3000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"ada"}' | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')

# 3) 带令牌访问受保护路由 → 200 "你好 ada，角色 user"
curl -i http://localhost:3000/api/me -H "Authorization: Bearer $TOKEN"

# 4) 不带令牌 → 401
curl -i http://localhost:3000/api/me

# 5) 未命中路由且不带令牌 → 404（守卫不误伤）
curl -i http://localhost:3000/api/no-such-route
```

---

## 🎨 最佳实践

认证验证身份，资源授权判断当前身份能做什么；已验证身份可供后续处理复用，但不同入口仍需各自保证没有绕过检查。route_layer 与其他层的覆盖范围按路由组合实测，不能由返回 401 或 404 单独推断泄漏与否。

令牌传递方式要匹配客户端能力，避免进入 URL 日志和历史；Cookie 方案另有 CSRF 等边界。时钟容差按同步精度和风险设置，不应因为库默认某值就永远禁止调整。测试过期、错误签名、跨用户和未知路由。

---

## ❓ 常见问题

### Q1: 我明明写了守卫，为什么 `/api/不存在` 返回 401 而不是 404？

**A**: 守卫挂在 `Router::layer` 上了——它在路由匹配**前**执行，未命中请求也过守卫。把守卫移到 `route_layer`（且保证先注册路由再挂载），404 请求就会绕过守卫恢复 404。两种挂载的差异与 panic 条件见 04 篇概念三。

### Q2: 令牌刚签出来就 401，"token used before issued" 类问题怎么来的？

**A**: 服务器间/本机时区外的**时钟偏移**导致签发时间晚于校验方时钟。jsonwebtoken 的 `Validation` 默认 `leeway: 60`（秒）已覆盖秒级偏差；偏移更大时校准 NTP，而不是放大 leeway——leeway 同时也放宽了 exp 过期判定。

### Q3: 直接给 handler 加 `AuthUser` 参数但忘了挂守卫，会静默放行吗？

**A**: 不会放行，也不会 401——extensions 里没有 `Claims`，extractor 返回 `Rejection = AuthError::Missing`，映射为 **500**。这是刻意设计：缺守卫属于服务端接线错误，必须以 5xx 暴露给监控，而不是伪装成客户端问题。

---

## 🧭 模式不变量

1. **认证早于业务**: 身份判定在 handler 之前完成（守卫层），业务代码只消费守卫写入的身份结果——校验与业务解耦后，新路由仍须确认已挂载守卫
2. **404 与 401 不可互换**: 资源是否存在与调用者是否有权是正交事实，守卫必须在路由命中后生效（与 04 篇不变量呼应）
3. **令牌无状态，校验每请求重做**: JWT 免共享存储，代价是把信任检查压缩进每个请求的 decode——任何"缓存校验结果"的优化都要重新论证撤销语义
4. **凭据只走头，不走 URL**: 传输通道的选择决定凭据的泄露面（日志/Referer/历史），这与具体框架无关

---

## 🔗 相关资源

### 📖 延伸阅读

- **指南**: [Axum Web 栈](./04-axum-web-stack.md) - layer/route_layer 语义与 extractor 排布规则
- **指南**: [状态与数据库 SQLx](./05-state-and-database-sqlx.md) - 把 PgPool 并入 AppState 与登录的真实实现
- **字典**: [Axum Essentials](../reference/framework-essentials/11-axum-essentials.md) - extractor/响应类型速查

### 🛠️ 工具资源

- **API 文档**: [docs.rs/axum/0.8](https://docs.rs/axum/0.8/axum/) - middleware/extract 模块
- **API 文档**: [docs.rs/jsonwebtoken/11](https://docs.rs/jsonwebtoken/11.0.0/jsonwebtoken/) - decode/Validation 全字段
- **规范**: [RFC 7519 JWT](https://datatracker.ietf.org/doc/html/rfc7519) - 声明集与 exp 语义

---

## 📝 总结

### 核心要点回顾

1. **挂点即语义**: 认证守卫用 `route_layer`（404 旁路、无路由 panic），全局横切才用 `layer`
2. **decode 一揽子**: 签名 + exp + 必需声明一次校验完成，leeway 默认 60 秒兜底时钟偏移
3. **一条单向流**: 中间件 decode → extensions → 自定义 extractor → handler，校验点唯一、接线错误变 500

### 学习成果检查

- [ ] 说清 `layer` 与 `route_layer` 对 404 请求的不同处理
- [ ] 独立写出 Claims + issue_token + verify_token 并解释 exp 的类型约定
- [ ] 实现 0.8 原生 async trait 形态的 FromRequestParts extractor
- [ ] 组装出"登录开放、受保护子树、404 不误伤"三态可验证的路由

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
