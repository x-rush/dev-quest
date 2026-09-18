# Axum 0.8 Web 栈：Router、Extractor 与中间件分层

## 先看框架承担哪部分职责

**Axum 入口**：Router 决定路径，Extractor 从请求提取参数，handler 处理业务并返回可转为响应的值。状态共享和中间件是不同职责。

**最小练习与预期结果**：测试路径参数非法、JSON 非法和业务未找到，区分提取阶段与业务阶段产生的错误。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 用 Tokio 生态事实标准的 Axum 0.8 搭起生产级 Web 服务——模块化 Router 组织、extractor 实战排布规则、"后加先执行"的中间件分层语义，以及与 tower-http 的 CORS/日志/静态文件集成。
>
> **目标读者**: 掌握 Rust 异步基础（basics 09）、要做 REST API 的后端开发者
>
> **前置知识**: [basics 09 并发与 async](../basics/09-concurrency-async.md)、HTTP 基础（方法/状态码/头）
>
> **预计时长**: 4-5 小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 操作指南（frameworks/） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#axum` `#web` `#tower` `#middleware` |
| **更新日期** | `2026年9月` |

</details>

> 版本基线见模块 [README](../README.md)：Axum 0.8 / Tokio 1.53 / Serde 1.0.229（2026-09-16 核实）；tower-http 按 crates.io 当前稳定 0.7 线。

## 🎯 学习目标

完成本篇后，你将能够：

- ✅ **组织路由树**: 按资源拆分子 Router，用 merge/nest 组装成应用
- ✅ **排布 extractor**: 说清哪些提取器能并存、body 提取器为何必须殿后
- ✅ **控制中间件层级**: 预测任意 layer 组合的执行顺序，用 route_layer 守卫路由
- ✅ **集成 tower-http**: 一套代码获得 CORS、请求追踪与静态文件服务

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

### 概念一：Router 组织——merge、nest 与 0.8 路径语法

**定义**: `Router` 是一棵以"字节精确匹配 + 段参数"为规则的路由树：

- `route("/users/{id}", get(handler))`: 注册路径，**`{id}` 是 0.8 的段参数语法**（0.7 的 `/:id`、通配 `/*rest` 已分别改为 `/{id}`、`/{*rest}`，升级必改）
- `nest("/api", 子Router)`: 把子路由整体挂到前缀下，子路由内部无感知
- `merge(子Router)`: 同层级合并且**不**加前缀，适合多模块平铺
- `fallback_service(...)`: 兜底服务，未命中路由的请求都到它（静态站点的常见用法）

**匹配语义**（去依赖化实证，本机 rustc --edition 2024 通过）:

```rust
// 路由匹配心智模型演示（去依赖化，无第三方 crate）
// 对应正文 axum 0.8 的 "/{id}" 参数段语义：参数匹配且仅匹配一个非空段
#[derive(Debug, PartialEq)]
enum Resolved<'a> {
    Index,               // GET /
    UserDetail(&'a str), // GET /users/{id}
    Api(&'a str),        // nest("/api") 挂载的路径
    NotFound,            // 未命中任何路由 → 404
}

fn resolve(path: &str) -> Resolved<'_> {
    match path {
        "/" => Resolved::Index,
        p if p.starts_with("/api/") => Resolved::Api(p),
        p => {
            // 逐段比较：段数与字面量都必须精确对齐
            let mut segs = p.splitn(3, '/');
            let _ = segs.next(); // 跳过前导空串
            match (segs.next(), segs.next()) {
                (Some("users"), Some(id)) if !id.is_empty() && !id.contains('/') => {
                    Resolved::UserDetail(id)
                }
                _ => Resolved::NotFound,
            }
        }
    }
}

fn main() {
    assert_eq!(resolve("/"), Resolved::Index);
    assert_eq!(resolve("/users/42"), Resolved::UserDetail("42"));
    // {id} 不匹配空段：/users/ 需要单独注册 /users 路由
    assert_eq!(resolve("/users/"), Resolved::NotFound);
    // {id} 只匹配单段，不会吞掉后续路径
    assert_eq!(resolve("/users/42/notes"), Resolved::NotFound);
    assert_eq!(resolve("/api/health"), Resolved::Api("/api/health"));
    assert_eq!(resolve("/unknown"), Resolved::NotFound);
    println!("6 项路由匹配断言全部通过");
}
```

### 概念二：Extractor 体系——两类提取器与排布规则

**定义**: handler 签名中的每个参数都是一个 extractor，负责从请求中"提取"一段数据：

- **parts 类**（实现 `FromRequestParts`）: 只看请求头/URI/方法——`Path`、`Query`、`State`、`Extension`、`HeaderMap`…可**多个并存**
- **body 类**（实现 `FromRequest`）: 消费请求体——`Json`、`Form`、`String`…**全签名至多一个，且必须放最后**（请求体只能被读一次，这是 HTTP 协议约束的直接投影）

`State<T>` 是特殊的一员：应用状态经 `Router::with_state` 注入，任何 handler 都能提取。所有提取器失败时自动返回 4xx/5xx，也可用 `Result<T, E>` 包裹自定义错误响应。

### 概念三：中间件分层——洋葱模型与两种挂载

**定义**: 中间件是 tower 的 `Layer`，包裹 handler 形成"请求进 → 响应出"的洋葱结构。两条必须背下的规则：

1. **注册顺序 ≠ 执行顺序**: 多次 `.layer()` 时，**后添加的层在最外层、最先收到请求**（文档原话："middleware being executed from bottom to top"）。tower 的 `ServiceBuilder` 则相反，自上而下按书写顺序执行
2. **`.layer()` 只包裹"此前已添加"的路由**: 之后添加的路由不被包裹

**layer vs route_layer**:

| | `Router::layer` | `Router::route_layer` |
|---|---|---|
| 作用范围 | 所有已注册路由 + fallback | **仅命中路由的请求** |
| 404 请求 | 经过中间件 | **绕过中间件** |
| 典型用途 | TraceLayer、全局 CORS | 认证守卫（避免 404 被翻译成 401） |

`route_layer` 的文档明确给出动机：让提前返回的中间件（如鉴权）"不会把 404 Not Found 变成 401 Unauthorized"。另注意：在没有任何路由时调用它会 panic。

### 概念四：tower-http——CORS、Trace 与静态文件

**定义**: tower-http 是官方维护的中间件/服务集合，与 axum 同属 tower 生态：

- `CorsLayer`: 预检与响应头控制，`permissive()` 仅限开发环境
- `TraceLayer`: 为每个请求生成 tracing span，配合 `tracing-subscriber` 输出访问日志
- `ServeDir`: 静态文件服务，可作 `nest_service` 挂载或 `fallback_service` 兜底

---

## 🛠️ 实践指南

### 步骤一：声明依赖

**目标**: 建立可编译的 Cargo 工程

**操作指南**:

```toml
# 独立 API 服务工程：axum-api/Cargo.toml
[package]
name = "axum-api"
version = "0.1.0"
edition = "2024"

[dependencies]
# 版本基线见模块 README（Axum 0.8 / Tokio 1.53 / Serde 1.0.229）
axum = "0.8"
tokio = { version = "1.53", features = ["macros", "rt-multi-thread", "net"] }
serde = { version = "1.0.229", features = ["derive"] }
tower-http = { version = "0.7", features = ["cors", "trace", "fs"] }
tracing-subscriber = "0.3"
```

**验证方法**: `cargo build` 通过（首次拉取依赖较慢）。

### 步骤二：最小服务

**目标**: 单文件跑通 `axum::serve` 监听循环

**操作指南**:

```rust
// src/main.rs 最小版
use axum::{routing::get, Json, Router};

#[tokio::main]
async fn main() {
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    let app = Router::new().route("/health", get(|| async { Json("ok") }));
    axum::serve(listener, app).await.unwrap();
}
```

**验证方法**: `cargo run` 后 `curl http://localhost:3000/health` 返回 `"ok"`。

### 步骤三：按资源拆分 Router

**目标**: `users` 模块自治路由，主文件只做组装

**操作指南**: 新建 `src/users.rs`（代码示例二），主文件用 `.nest("/api", users::router())` 挂载；子路由内部路径不带 `/api` 前缀。

**验证方法**: `curl http://localhost:3000/api/users/42` 命中 `get_user`。

### 步骤四：挂中间件与静态文件

**目标**: 全局日志 + CORS + `public/` 目录兜底

**操作指南**: 按代码示例一组装；注意 `.layer(TraceLayer)` 写在 `.layer(CorsLayer)` **之后**（因此 Trace 在最外层先执行）。

**验证方法**: 访问任意路径终端输出 tracing 日志；浏览器跨域请求携带的 `Access-Control-Allow-*` 头存在；`public/index.html` 可直接访问。

---

## 💻 代码示例

### 示例一：完整组装（main.rs）

```rust
// src/main.rs —— 路由合并 + 中间件分层 + 静态兜底
mod users;

use axum::{routing::get, Json, Router};
use tower_http::{cors::CorsLayer, services::ServeDir, trace::TraceLayer};

async fn health() -> Json<&'static str> {
    Json("ok")
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();

    let app = Router::new()
        .route("/health", get(health))
        .nest("/api", users::router())
        // 未命中 API 的请求交给静态目录（SPA 常见托底）
        .fallback_service(ServeDir::new("public").append_index_html_on_directories(true))
        // 洋葱序：后写的在外层。Trace 最外层先执行，覆盖 CORS 预检在内的全程
        .layer(TraceLayer::new_for_http())
        .layer(CorsLayer::permissive()) // 生产环境务必换成精确 origin 白名单
        .with_state(users::AppState::default());

    // 0.8 的服务入口：axum::serve 接管监听循环，无需手写 accept
    axum::serve(listener, app).await.unwrap();
}
```

### 示例二：子路由模块（users.rs）

```rust
// src/users.rs —— 按资源拆分：/api 前缀由父级 nest 提供，这里不出现
use axum::{
    extract::{Path, Query, State},
    routing::get,
    Json, Router,
};
use serde::{Deserialize, Serialize};

#[derive(Clone, Default)]
pub struct AppState {
    pub db_url: String, // 演示占位；真实数据库状态见 05 篇 PgPool
}

#[derive(Deserialize)]
pub struct NewUser {
    pub name: String,
}

#[derive(Deserialize)]
pub struct ListQuery {
    pub q: Option<String>,
}

#[derive(Serialize)]
pub struct User {
    pub id: u64,
    pub name: String,
}

// 0.8 路径参数："/users/{id}"（0.7 的 "/:id" 已移除）
pub fn router() -> Router<AppState> {
    Router::new()
        // 同一资源多方法：MethodRouter 链式注册
        .route("/users", get(list_users).post(create_user))
        .route("/users/{id}", get(get_user))
}

// parts 类提取器（Query/State）在前、任意顺序；无 body 类
async fn list_users(
    Query(q): Query<ListQuery>,
    State(_state): State<AppState>,
) -> Json<Vec<User>> {
    let _ = q.q; // 真实实现接 PgPool，见 05 篇
    Json(vec![User { id: 1, name: "ada".into() }])
}

// Path 也是 parts 类：先提取参数再干活
async fn get_user(Path(id): Path<u64>, State(_state): State<AppState>) -> Json<User> {
    Json(User { id, name: format!("user-{id}") })
}

// body 类示范：Json 是全签名唯一且最后的参数
async fn create_user(
    State(_state): State<AppState>,
    Json(input): Json<NewUser>, // 必须殿后：请求体只能消费一次
) -> Json<User> {
    Json(User { id: 1, name: input.name })
}
```

**关键点解析**:
- `Router<AppState>` 表达"需要该状态"，由最外层 `with_state` 统一供给
- 同资源多方法用 `get(h).post(h)` 链式 MethodRouter，避免重复 route 行
- 提取器类型即文档：看 handler 签名就能还原请求协议

---

## 🎨 最佳实践

按业务资源组合路由，使路径和状态依赖可以独立检查。handler 只取得所需状态，公共日志与认证层的顺序通过实际请求测试确认，不以“放最外层”概括所有组合。

消耗请求体的提取器通常只能有一个并置于参数末尾，不兼容组合可能在编译期就失败，不能笼统说最终只得到空 body。Axum 0.8 使用花括号捕获路径，旧冒号语法在默认检查下会在路由构建时 panic；认证层覆盖范围还要测试未匹配路径和方法。

---

## ❓ 常见问题

### Q1: 从 0.7 升级到 0.8，路由要改哪些？

**A**: 全量替换两类语法：段参数 `/:id` → `/{id}`；通配 `/*rest` → `/{*rest}`。其余高频变化：handler/extractor 不再需要 `#[async_trait]`（改用原生 async trait）；`axum::serve` 已是标准入口。升级核对以官方 changelog 为准。

### Q2: POST JSON 返回 415 或 400？

**A**: 415 Unsupported Media Type = 请求没带 `Content-Type: application/json`（Json 提取器的拒绝行为）；400 = body 不是合法 JSON 或字段类型不匹配。前端 fetch 记得带头；服务端要自定义错误体时，handler 返回 `Result<Json<T>, ApiError>` 并让 `ApiError: IntoResponse`。

### Q3: 两个中间件的执行顺序和我写的顺序相反？

**A**: 不是 bug——`Router::layer` 链式调用时后写的层在外层、先执行（文档："middleware being executed from bottom to top"）。想让代码书写顺序 = 执行顺序，用 `tower::ServiceBuilder`：`ServiceBuilder::new().layer(a).layer(b)` 中 a 先收到请求。

---

## 🧭 模式不变量

1. **先路由、后业务**: 请求先经过纯数据匹配的路由表再进入 handler，路由层永远不做业务判断——这让"哪些路径存在"可静态审计
2. **请求体只能消费一次**: 任何框架的 body 提取器都受此协议约束，"至多一个 body 提取器且殿后"是协议投影而非框架怪癖
3. **中间件顺序 = 关注点的洋葱层级**: 横切关注点（日志/CORS）在外层，业务前置条件（认证）在路由层，数据转换在最内层
4. **404 与 401 不可互换**: 资源是否存在与调用者是否有权是两个正交事实，守卫中间件必须只在路由命中后生效

---

## 🔗 相关资源

### 📖 延伸阅读

- **字典**: [Axum Essentials](../reference/framework-essentials/11-axum-essentials.md) - 提取器/响应类型速查全集
- **字典**: [Tokio 指南](../reference/library-guides/12-tokio-guide.md) - 运行时与 TcpListener 的底层机制
- **指南**: [状态与数据库 SQLx](./05-state-and-database-sqlx.md) - 本篇 AppState 的实战填充
- **指南**: [认证中间件](./06-auth-middleware.md) - route_layer 守卫的完整实现

### 🛠️ 工具资源

- **API 文档**: [docs.rs/axum/0.8](https://docs.rs/axum/0.8/axum/) - Router/middleware/extract 模块
- **中间件库**: [tower-http](https://docs.rs/tower-http/) - CORS/Trace/ServeDir 等
- **对照阅读**: [09-nodejs-backend](../../09-nodejs-backend/README.md) - 与 Express 中间件模型的语义对照

---

## 📝 总结

### 核心要点回顾

1. **路由树**: merge 平铺、nest 加前缀，`{id}` 段参数匹配单个非空段
2. **提取器**: parts 类可多个，body 类唯一且殿后——状态经 `State` 免缝注入
3. **分层**: 后加先执行的洋葱序 + `route_layer` 的 404 旁路，是守卫正确性的两块基石

### 学习成果检查

- [ ] 独立完成 merge/nest 组装并让 `/api/users/42` 命中子路由
- [ ] 写出含 Query + State + Json 的 handler 而不查文档
- [ ] 预测 `.layer(a).layer(b)` 的执行顺序并解释原因
- [ ] 说明认证守卫为什么必须用 route_layer

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
