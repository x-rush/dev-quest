# Axum 0.8 精要

> **文档简介**: Axum 0.8 的全量速查——Router 与 `{param}` 路径语法、extractor 顺序规则、State 子状态、middleware 与 tower/Tower 生态对照、`IntoResponse` 错误处理
>
> **目标读者**: 有 Tokio 异步基础、搭建 HTTP API 的中级开发者
>
> **前置知识**: async/.await 与 Tokio 运行时（见 [12-tokio-guide](../library-guides/12-tokio-guide.md)）；Serde derive

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#rust` `#axum` `#reference` `#web` |
| **更新日期** | `2026年9月` |

</details>

> 版本基线：Axum **0.8** / Tokio **1.53**（见模块 [README](../../README.md) 技术基线区块）。

## 🎯 学习目标

- ✅ **写对路径**：0.8 起的 `{param}` / `{*wildcard}` 语法及其与旧语法的差异
- ✅ **排对参数**：extractor 清单与"消耗 body 者必须在最后"的顺序规则
- ✅ **组织状态**：`with_state`、`FromRef` 子状态与可嵌套路由
- ✅ **接管错误**：`IntoResponse` 自定义错误与 tower 中间件的错误层

---

## 🚨 0.8 版本要点：路径语法

0.8 起路径参数从 `:param` / `*wildcard` 改为 **`{param}` / `{*wildcard}`**（底层 matchit 路由器升级）。0.7 语法在构建 Router 时直接报错（提示改用花括号；确需字面匹配 `:`/`*` 开头的段可调 `without_v07_checks` 关闭检查）。

```rust
use axum::{extract::Path, routing::get, Router};

fn routes() -> Router {
    Router::new()
        .route("/users/{id}", get(user))                        // 单参数
        .route("/users/{user_id}/teams/{team_id}", get(team))   // 多参数
        .route("/files/{*key}", get(file))                      // 通配：捕获剩余全部段
}

async fn user(Path(id): Path<u64>) -> String { format!("user {id}") }

async fn team(Path((user_id, team_id)): Path<(u64, u64)>) -> String {
    format!("user {user_id} team {team_id}")                // 多参数按序解构成元组
}

async fn file(Path(key): Path<String>) -> String { key }    // 通配捕获为整段字符串
```

---

## 🔧 Router 速查

| 方法 | 用途 |
|------|------|
| `Router::new()` | 创建路由器 |
| `.route(path, MethodRouter)` | 注册一条路径；`get(h)` / `post(h)` / `put` / `delete` / `patch` / `head` / `options` / `trace` |
| `.route(path, get(h).post(h2))` | 同一路径多方法链式 |
| `.any(h)` / `.on([get, post], h)` | 全方法 / 指定方法集合 |
| `.nest("/api", sub_router)` | 前缀挂载子路由器（axum 路由器） |
| `.nest_service("/assets", ServeDir)` | 挂载非 axum 的 tower Service（如静态目录） |
| `.merge(other_router)` | 合并两个路由器（路径不得冲突） |
| `.fallback(handler)` | 未匹配路径的兜底处理器（默认返回空 404） |
| `.layer(layer)` | 给当前所有路由包一层 tower 中间件 |
| `.route_layer(layer)` | 仅请求**命中某路由**时才经过的中间件（404 请求不经过它） |
| `.with_state(state)` | 注入状态；调用后类型收敛为 `Router<()>` |
| `.without_v07_checks()` | 关闭 0.7 旧语法检查（需字面 `:`/`*` 段时用） |

---

## 🧲 Extractor 全表

Handler 参数即 extractor，实现 `FromRequestParts`（请求头阶段）或 `FromRequest`（可消耗 body）。

| Extractor | 阶段 | 说明 |
|-----------|------|------|
| `Path<T>` | parts | 路径参数；T 可为元组/结构体/`HashMap` |
| `Query<T>` | parts | 查询串反序列化（`T: Deserialize`） |
| `State<S>` | parts | 提取共享状态（见 State 节） |
| `HeaderMap` | parts | 全部请求头 |
| `Method` / `Host` / `Uri` / `OriginalUri` | parts | 请求方法 / 主机 / URI |
| `Extension<T>` | parts | 从请求扩展位读取（与 `layer(Extension(...))` 配套） |
| `String` / `Bytes` | **body** | 原始 body：校验 UTF-8 / 原始字节 |
| `Json<T>` / `Form<T>` | **body** | JSON / 表单反序列化（`T: Deserialize`） |
| `Multipart` | **body** | 文件上传（需 `features = ["multipart"]`） |
| `Request` | **body** | 整个请求，完全手动控制（必须最后） |
| `ConnectInfo<SocketAddr>` | parts | 客户端地址；需配合 `into_make_service_with_connect_info` |
| `Option<T>` | — | 可选提取，缺失时 `None`（要求该类型支持可选提取，标准类型均已支持） |

**上限**：单个 handler 最多 16 个 extractor；`Request` 或其他 body extractor 只能出现一次。

### 顺序规则（编译期强制）

**消耗 body 的 extractor 必须是最后一个参数**；parts 阶段 extractor 可任意排列（但在 body extractor 之前）。

```rust
use axum::extract::State;
use axum::http::{HeaderMap, Method};

#[derive(Clone)]
struct AppState;

// ✅ 合法：Method/HeaderMap/State 都不碰 body，String 消耗 body 且在最后
async fn handler(
    method: Method,
    headers: HeaderMap,
    State(state): State<AppState>,
    body: String,
) { let _ = (method, headers, state, body); }

// ❌ 编译失败：String 是 body consumer，必须最后
// async fn bad(body: String, method: Method) { }
```

**拒绝即短路**：任一 extractor 失败（如 `Path` 类型不匹配、`Json` 解析失败），请求直接以默认 rejection 响应终止，handler 不执行。`Result<T, T::Rejection>` 可捕获 rejection 自行响应。

---

## 🗄️ State

```rust
use axum::{extract::{State, FromRef}, routing::get, Router};

#[derive(Clone)]
struct AppState {
    db: DbPool,
    config: Config,
}

// 子状态：handler 只声明需要的部分，要求 Sub: FromRef<AppState>
#[derive(Clone, FromRef)]   // derive 需 axum features = ["macros"]
struct SubState {
    config: Config,
}

fn build() -> Router<()> {
    let state = AppState { db: DbPool, config: Config };
    Router::new()
        .route("/", get(|State(db): State<DbPool>| async { "ok" }))
        .route("/cfg", get(|State(cfg): State<SubState>| async { "ok" }))
        .with_state(state)   // 必须在所有路由注册之后调用
}
```

**关键点解析**:
- `with_state` 前的 Router 类型是 `Router<S>`；调用后收敛为 `Router<()>`，之后再 `.route()` 的 handler 只能要 `State<()>`——**顺序错了会收到难懂的 trait bound 报错**
- `State<Inner>` 对任意 `Inner: FromRef<Outer>` 成立，因此可用 `Arc<dyn Trait>`、子状态切片等模式
- 模块拆分惯用法：每个模块写 `fn routes(state: AppState) -> Router<AppState>`，在根路由器 `.nest()` / `.merge()`

```rust
// 可嵌套的子路由器：保持泛型 S，把 with_state 留给根
fn routes<S: Clone + Send + Sync + 'static>(state: AppState) -> Router<S> {
    Router::new()
        .route("/", get(|_: State<AppState>| async { "ok" }))
        .with_state(state)
}

fn build(app_state: AppState) -> Router {
    Router::new().nest("/api", routes(app_state))
}
```

---

## 🔗 middleware 与 tower

axum 没有自带中间件系统——**一切中间件都是 tower `Layer`**。

| 写法 | 场景 |
|------|------|
| `middleware::from_fn(f)` | 最常用：普通 async 函数当中间件，无需理解 tower `Service` trait |
| `Router::layer` vs `route_layer` | 前者包住全部（含 404）；后者仅命中路由时执行（鉴权用后者，避免 404 也走 auth） |
| `ServiceBuilder` | 组合多层时用，**自上而下 = 外到内**，顺序一目了然 |
| `error_handling::HandleErrorLayer` | 接住 tower 层的 `BoxError`（如 `TimeoutLayer` 超时错误），转为正常响应 |

```rust
use axum::{
    extract::{Request, Response},
    http::StatusCode,
    middleware::{self, Next},
    routing::get,
    Router,
};

async fn auth(mut req: Request, next: Next) -> Result<Response, StatusCode> {
    let token = req.headers().get("authorization")
        .and_then(|h| h.to_str().ok())
        .ok_or(StatusCode::UNAUTHORIZED)?;
    if let Some(user) = authorize_current_user(token).await {
        // 中间件 → handler 传数据的标准通道：请求扩展位
        req.extensions_mut().insert(user);
        Ok(next.run(req).await)
    } else {
        Err(StatusCode::UNAUTHORIZED)
    }
}

async fn handler(axum::Extension(user): axum::Extension<CurrentUser>) { let _ = user; }

fn build() -> Router {
    Router::new()
        .route("/", get(handler))
        .route_layer(middleware::from_fn(auth))   // 404 不经过 auth
}
```

```rust
use tower::ServiceBuilder;
use tower_http::trace::TraceLayer;

fn build() -> Router {
    Router::new()
        .route("/", get(handler))
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())   // 外层：先记日志
                .layer(middleware::from_fn(auth))    // 内层：后鉴权
        )
}
```

### Tower 生态对照

| Crate | 常用件 | 用途 |
|-------|--------|------|
| `tower` | `ServiceBuilder`、`timeout`、`retry`、`limit` | 通用 Service 组合子（`BoxError` 体系） |
| `tower-http` | `TraceLayer`、`CorsLayer`、`CompressionLayer`、`TimeoutLayer`、`ServeDir` | HTTP 语义中间件（日志/CORS/压缩/超时/静态文件） |

**对照记忆**：`tower` 件多为"可能失败"（返回 `BoxError`），直接 `.layer` 到 axum 会吞掉错误——外面包 `HandleErrorLayer` 把 `BoxError` 转成 `Response`；`tower-http` 的 HTTP 层多为无失败设计，可直接 `.layer`。

---

## 🚀 服务启动

```rust
use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    let listener = TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())   // 收到信号后停止接收新请求
        .await
        .unwrap();
}

async fn shutdown_signal() {
    tokio::signal::ctrl_c().await.expect("failed to listen for ctrl-c");
}
```

需要客户端地址时把 `app` 换成 `app.into_make_service_with_connect_info::<std::net::SocketAddr>()`。

**默认 body 上限**约 2 MB，超出返回 `PAYLOAD_TOO_LARGE`；用 `axum::extract::DefaultBodyLimit::max(n)` 调整。

---

## 🧯 错误处理：IntoResponse

Handler 返回值只要实现 `IntoResponse`。基础件：`StatusCode`、`String`、`Json<T>` 及其元组组合。

```rust
use axum::{http::StatusCode, response::{IntoResponse, Response}, Json};
use serde_json::json;

// 组合优先：元组 (状态码, 内容) 直接当响应
fn not_found() -> Response {
    (StatusCode::NOT_FOUND, Json(json!({ "error": "not found" }))).into_response()
}
```

生产推荐：**统一 AppError**，让 `?` 在 handler 里自由传播。

```rust
use axum::{extract::rejection::JsonRejection, http::StatusCode, response::{IntoResponse, Response}, Json};

#[derive(Debug)]
enum AppError {
    BadJson(JsonRejection),      // 客户端输入问题：回 4xx 并透传原因
    Internal(anyhow::Error),     // 服务端问题：绝不回内部细节
}

impl From<JsonRejection> for AppError {
    fn from(r: JsonRejection) -> Self { Self::BadJson(r) }
}

// 有了 From 转换，handler 返回 Result<_, AppError> 即可用 ?

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        #[derive(serde::Serialize)]
        struct ErrorResponse { message: String }

        match self {
            AppError::BadJson(rejection) => {
                // 客户端造成的错误：用 extractor 自带的状态码与可读文本
                (rejection.status(), rejection.body_text()).into_response()
            }
            AppError::Internal(_) => {
                // 服务端错误：对外只说 "Something went wrong"
                // 内部错误可通过 response.extensions_mut().insert(Arc::new(self))
                // 交给日志中间件读取，而非写进响应体
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(ErrorResponse { message: "Something went wrong".into() }),
                ).into_response()
            }
        }
    }
}
```

**关键点解析**:
- 转换函数里不打印日志（避免副作用），把错误塞进 Extension 交给日志层——错误"转换"与"记录"解耦
- `rejection.status()` / `rejection.body_text()`：各类 rejection 自带状态码与人类可读文本
- 与 [14-error-libraries](../library-guides/14-error-libraries.md) 的 thiserror/anyhow 分工：thiserror 定义枚举，anyhow 收拢内部错误链

---

## 📦 Cargo.toml 骨架

```toml
[dependencies]
axum = "0.8"
tokio = { version = "1.53", features = ["macros", "rt-multi-thread", "net"] }  # 基线见模块 README
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
# 用 derive(FromRef) / Multipart 时启用对应 feature：
# axum = { version = "0.8", features = ["macros", "multipart"] }
# tower / tower-http / tracing 的版本随生态刷新，以 crates.io 核实为准：
# tower-http = { version = "...", features = ["trace", "cors"] }
```

---

## 🎨 最佳实践

组合 Router 时明确当前还缺少什么 State，再通过合适位置提供状态；with_state 后并非永远不能添加路由，类型是否匹配由完整组合决定。路径冲突和旧捕获语法通常在构建路由的运行阶段暴露，不应混称 rustc 编译错误。

认证中间件与 extractor 可以按应用需要组织，重点是身份验证不会遗漏，资源授权仍执行。错误响应保持稳定且不暴露内部原因，用真实请求验证合法路径、缺身份、无权限和未匹配路径的行为。

## ❓ 常见问题

### Q1: handler 能否返回多个不同状态码的响应？
**A**: 返回 `Response`（自己构造）或自定义枚举实现 `IntoResponse`（每个变体一种状态码）。后者保留 `?` 的便利，是推荐解。

### Q2: 为什么我的 tower 层让所有请求都 500？
**A**: 该层返回了未被转换的 `BoxError`。外包 `HandleErrorLayer::new(|err| async { ... })` 把错误转为响应，且注意它在 `ServiceBuilder` 中要放在会出错的那层**上面**（外层）。

---

## 🧱 模式不变量

1. **请求处理是流水线而非钩子**：middleware 与 handler 是同一套 tower Service 抽象，"框架特性"与"生态中间件"之间没有边界
2. **提取按阶段排序**：请求头阶段的信息（路由、状态、头）总是先于 body 可用，类型系统把这一时序固化为编译期约束
3. **错误分类决定暴露面**：客户端错误回原因、服务端错误回文案——状态码语义是 API 对外契约的一部分，与内部日志严格分离
4. **状态在组装期定型**：路由器一旦 `with_state` 即类型收敛，状态注入发生在构建时而非每请求，运行期零查找开销的代价是组装顺序敏感

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[Tokio 指南](../library-guides/12-tokio-guide.md)**: `#[tokio::main]`、`TcpListener`、signal 的运行时底座
- 📄 **[Future·Pin·Waker](../language-concepts/08-async-internals.md)**: `Send` 约束与 handler trait bound 报错的底层解释
- 📄 **[错误库指南](../library-guides/14-error-libraries.md)**: thiserror / anyhow 与 AppError 的配套用法
- 📄 **[Axum Web 栈](../../frameworks/04-axum-web-stack.md)**: 数据库（SQLx）接入的完整栈
- 📄 **[认证中间件](../../frameworks/06-auth-middleware.md)**: 本篇 auth 示例的工程化展开
- 📄 **[Node.js 后端模块](../../../09-nodejs-backend/README.md)**: Axum 与 Express 的心智模型对照

### 参考章节
- 📖 **[模块 README 技术基线](../../README.md)**: 本篇所有版本号的单一事实来源

---

## 📝 总结

### 核心要点回顾
1. **0.8 路径语法**：`{param}` / `{*wildcard}`，旧语法构建期报错
2. **extractor 两条铁律**：body consumer 必须最后；任一提取失败即短路
3. **中间件即 tower**：`from_fn` 起步、`ServiceBuilder` 定序、`HandleErrorLayer` 收错
4. **错误一套出口**：AppError + `IntoResponse`，对内 anyhow、对外文案

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
