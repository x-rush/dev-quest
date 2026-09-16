# 项目实战 3：notes-api —— Axum REST API（SQLx + PostgreSQL）

> **文档简介**: 构建一个生产形态的 REST API：Axum 0.8 路由 CRUD、SQLx 0.9 连接 PostgreSQL、`IntoResponse` 统一错误映射、handler/service/repo 三层结构，为 WebSocket 实时应用与真实后端工程打底
>
> **目标读者**: 熟悉 Rust 基础与 async 语法、想进入 Rust 后端实战的开发者
>
> **前置知识**: async/.await 与 Tokio 基础、错误处理 anyhow/thiserror、HTTP 基本概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 操作指南（项目实战） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#axum` `#sqlx` `#postgresql` `#rest-api` |
| **更新日期** | `2026年9月` |
| **状态** | ✅ 已完成 |

> 版本基线以 [模块 README 技术基线区块](../README.md) 为准：Axum 0.8、SQLx 0.9、Tokio 1.53、Serde 1.0.229。注意 Axum 0.8 的路径参数语法是 `/{id}`（0.7 的 `/:id` 已废弃）。本篇 Rust 块未做本机编译（需 PostgreSQL 与全链依赖），API 按 docs.rs 与官方示例核实。

## 🎯 学习目标

完成本项目后，你将能够：

- ✅ **搭建分层结构**: handler（HTTP 语义）/ service（业务规则）/ repo（SQL）各司其职
- ✅ **实现统一错误映射**: 领域错误经 `IntoResponse` 在边界处一次转成状态码
- ✅ **使用 SQLx 数据访问**: 运行时 `query_as` + `FromRow`，并了解编译期校验宏的取舍
- ✅ **完成数据库迁移**: `sqlx::migrate!` 随应用启动自动建表

## 📋 目录

- [分层架构与项目结构](#分层架构与项目结构)
- [分步实现](#分步实现)
- [运行与验证](#运行与验证)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [扩展方向](#扩展方向)
- [相关资源](#相关资源)
- [总结](#总结)

---

## 分层架构与项目结构

### 分层职责

```mermaid
graph TD
    A[handler<br/>HTTP 提取与响应] --> B[service<br/>业务规则与领域错误]
    B --> C[repo<br/>SQLx 数据访问]
    C --> D[(PostgreSQL)]
```

- **handler** 只关心 HTTP：提取 `Path`/`Json`/`State`，返回状态码
- **service** 只关心业务：标题非空、长度上限、资源是否存在；返回领域错误 `ServiceError`
- **repo** 只关心 SQL：参数化查询、行到结构的映射；返回 `sqlx::Error`
- 依赖方向单向：handler → service → repo，错误向上传递、边界处翻译

### 项目结构

`cargo new notes-api` 初始化后：

```
notes-api/
├── Cargo.toml
├── migrations/
│   └── 0001_create_notes.sql
└── src/
    ├── main.rs     # 装配：连接池 + 路由 + 启动
    ├── error.rs    # ServiceError / ApiError
    ├── models.rs   # Note / CreateNote / UpdateNote
    ├── repo.rs     # SQLx 数据访问
    ├── service.rs  # 业务规则
    └── handler.rs  # HTTP 层
```

`Cargo.toml` 依赖（版本基线见模块 README）：

```toml
[package]
name = "notes-api"
version = "0.1.0"
edition = "2024"

[dependencies]
axum = "0.8"
tokio = { version = "1.53", features = ["full"] }
sqlx = { version = "0.9", features = ["runtime-tokio", "tls-rustls", "postgres", "chrono", "migrate"] }
serde = { version = "1.0.229", features = ["derive"] }
serde_json = "1"
chrono = { version = "0.4", features = ["serde"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
anyhow = "1"
```

---

## 分步实现

### 步骤 1：数据模型与迁移

`migrations/0001_create_notes.sql`：

```sql
CREATE TABLE IF NOT EXISTS notes (
    id         BIGSERIAL PRIMARY KEY,
    title      TEXT NOT NULL,
    content    TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

`src/models.rs`——请求与响应模型分离，不把输入结构体直接当输出用：

```rust
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

/// 数据库行映射：字段与表列一一对应
#[derive(Serialize, FromRow)]
pub struct Note {
    pub id: i64,
    pub title: String,
    pub content: String,
    pub created_at: DateTime<Utc>,
}

/// 创建请求：只有客户端允许提供的字段
#[derive(Deserialize)]
pub struct CreateNote {
    pub title: String,
    pub content: String,
}

/// 更新请求：字段可选，None 表示"不修改"
#[derive(Deserialize)]
pub struct UpdateNote {
    pub title: Option<String>,
    pub content: Option<String>,
}
```

### 步骤 2：repo 层——纯数据访问

`src/repo.rs`：

```rust
use sqlx::PgPool;

use crate::models::Note;

pub async fn list(pool: &PgPool) -> sqlx::Result<Vec<Note>> {
    // 显式列名，不用 SELECT *：列序变化或新增大字段都不会破坏映射
    sqlx::query_as::<_, Note>("SELECT id, title, content, created_at FROM notes ORDER BY id")
        .fetch_all(pool)
        .await
}

pub async fn find(pool: &PgPool, id: i64) -> sqlx::Result<Option<Note>> {
    sqlx::query_as::<_, Note>("SELECT id, title, content, created_at FROM notes WHERE id = $1")
        .bind(id)
        .fetch_optional(pool)
        .await
}

pub async fn insert(pool: &PgPool, title: &str, content: &str) -> sqlx::Result<Note> {
    sqlx::query_as::<_, Note>(
        "INSERT INTO notes (title, content) VALUES ($1, $2) \
         RETURNING id, title, content, created_at",
    )
    .bind(title)
    .bind(content)
    .fetch_one(pool)
    .await
}

pub async fn update(
    pool: &PgPool,
    id: i64,
    title: Option<&str>,
    content: Option<&str>,
) -> sqlx::Result<Option<Note>> {
    // COALESCE 让 None 落为原值，实现部分更新
    sqlx::query_as::<_, Note>(
        "UPDATE notes SET title = COALESCE($1, title), content = COALESCE($2, content) \
         WHERE id = $3 RETURNING id, title, content, created_at",
    )
    .bind(title)
    .bind(content)
    .bind(id)
    .fetch_optional(pool)
    .await
}

pub async fn delete(pool: &PgPool, id: i64) -> sqlx::Result<u64> {
    sqlx::query("DELETE FROM notes WHERE id = $1")
        .bind(id)
        .execute(pool)
        .await
        .map(|r| r.rows_affected())
}
```

**关键点解析**：

- 所有值经 `.bind()` 参数化，杜绝 SQL 注入；SQL 字符串本身不含用户输入
- `fetch_optional` 把"查无此行"表达为 `Ok(None)`，让上层决定是不是 404
- 返回类型保持 `sqlx::Result`——repo 层不知道"404"这种 HTTP 概念

### 步骤 3：error 层——错误两段式翻译

`src/error.rs`：

```rust
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;

/// 领域错误：service 层向上抛出，不含任何 HTTP 语义
#[derive(Debug)]
pub enum ServiceError {
    NotFound,
    Validation(String),
    Db(sqlx::Error),
}

/// HTTP 错误：只在 handler 边界出现，实现 IntoResponse
pub struct ApiError(ServiceError);

impl From<ServiceError> for ApiError {
    fn from(e: ServiceError) -> Self {
        Self(e)
    }
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, message) = match self.0 {
            ServiceError::NotFound => (StatusCode::NOT_FOUND, "资源不存在".to_string()),
            ServiceError::Validation(msg) => (StatusCode::BAD_REQUEST, msg),
            ServiceError::Db(err) => {
                // 内部错误只记日志，不把 SQL 细节泄漏给客户端
                tracing::error!(error = ?err, "数据库错误");
                (StatusCode::INTERNAL_SERVER_ERROR, "内部错误".to_string())
            }
        };
        (status, Json(json!({ "error": message }))).into_response()
    }
}
```

**关键点解析**：

- 两个枚举的分工：`ServiceError` 可被非 HTTP 客户端复用（gRPC、CLI、测试），`ApiError` 才知道状态码
- handler 返回 `Result<T, ApiError>` 时，`?` 自动经 `From<ServiceError>` 完成第一段翻译
- `IntoResponse` 是 Axum 统一的响应转换点：handler 返回的任何错误最终都走这里

### 步骤 4：service 层——业务规则

`src/service.rs`：

```rust
use sqlx::PgPool;

use crate::{
    error::ServiceError,
    models::{CreateNote, Note, UpdateNote},
    repo,
};

pub async fn list(pool: &PgPool) -> Result<Vec<Note>, ServiceError> {
    repo::list(pool).await.map_err(ServiceError::Db)
}

pub async fn get(pool: &PgPool, id: i64) -> Result<Note, ServiceError> {
    repo::find(pool, id)
        .await
        .map_err(ServiceError::Db)?
        .ok_or(ServiceError::NotFound)
}

pub async fn create(pool: &PgPool, input: CreateNote) -> Result<Note, ServiceError> {
    let title = input.title.trim().to_string();
    if title.is_empty() {
        return Err(ServiceError::Validation("标题不能为空".into()));
    }
    if title.chars().count() > 100 {
        return Err(ServiceError::Validation("标题不能超过 100 字符".into()));
    }
    let content = input.content.trim().to_string();
    repo::insert(pool, &title, &content)
        .await
        .map_err(ServiceError::Db)
}

pub async fn update(pool: &PgPool, id: i64, input: UpdateNote) -> Result<Note, ServiceError> {
    if let Some(title) = &input.title {
        if title.trim().is_empty() {
            return Err(ServiceError::Validation("标题不能为空".into()));
        }
    }
    let note = repo::update(
        pool,
        id,
        input.title.as_deref().map(str::trim),
        input.content.as_deref().map(str::trim),
    )
    .await
    .map_err(ServiceError::Db)?
    .ok_or(ServiceError::NotFound)?;
    Ok(note)
}

pub async fn delete(pool: &PgPool, id: i64) -> Result<(), ServiceError> {
    let affected = repo::delete(pool, id).await.map_err(ServiceError::Db)?;
    if affected == 0 {
        return Err(ServiceError::NotFound);
    }
    Ok(())
}
```

**关键点解析**：

- "查无此行"在这里被翻译成 `ServiceError::NotFound`——404 语义是业务决定，不是 SQL 决定
- 校验规则（非空、长度）集中在 service，handler 与 repo 都不需要重复

### 步骤 5：handler 与路由装配

`src/handler.rs`：

```rust
use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};

use crate::{
    error::ApiError,
    models::{CreateNote, Note, UpdateNote},
    service,
    AppState,
};

pub async fn list_notes(State(app): State<AppState>) -> Result<Json<Vec<Note>>, ApiError> {
    Ok(Json(service::list(&app.pool).await?))
}

pub async fn get_note(
    State(app): State<AppState>,
    Path(id): Path<i64>,
) -> Result<Json<Note>, ApiError> {
    Ok(Json(service::get(&app.pool, id).await?))
}

pub async fn create_note(
    State(app): State<AppState>,
    Json(input): Json<CreateNote>,
) -> Result<(StatusCode, Json<Note>), ApiError> {
    let note = service::create(&app.pool, input).await?;
    Ok((StatusCode::CREATED, Json(note)))
}

pub async fn update_note(
    State(app): State<AppState>,
    Path(id): Path<i64>,
    Json(input): Json<UpdateNote>,
) -> Result<Json<Note>, ApiError> {
    Ok(Json(service::update(&app.pool, id, input).await?))
}

pub async fn delete_note(
    State(app): State<AppState>,
    Path(id): Path<i64>,
) -> Result<StatusCode, ApiError> {
    service::delete(&app.pool, id).await?;
    Ok(StatusCode::NO_CONTENT)
}
```

`src/main.rs`——连接池、迁移与路由一次装配：

```rust
mod error;
mod handler;
mod models;
mod repo;
mod service;

use axum::{routing::get, Router};
use sqlx::postgres::PgPoolOptions;
use tracing_subscriber::EnvFilter;

#[derive(Clone)]
pub struct AppState {
    pub pool: sqlx::PgPool,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()))
        .init();

    let database_url = std::env::var("DATABASE_URL")
        .expect("缺少 DATABASE_URL 环境变量，例如 postgres://dev:dev@localhost/notes");
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await?;
    sqlx::migrate!("./migrations").run(&pool).await?;

    let app = Router::new()
        .route(
            "/notes",
            get(handler::list_notes).post(handler::create_note),
        )
        .route(
            "/notes/{id}",
            get(handler::get_note)
                .put(handler::update_note)
                .delete(handler::delete_note),
        )
        .route("/healthz", get(|| async { "ok" }))
        .with_state(AppState { pool });

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await?;
    tracing::info!("notes-api listening on {}", listener.local_addr()?);
    axum::serve(listener, app).await?;
    Ok(())
}
```

**关键点解析**：

- `AppState` 是 `Clone` 的轻量句柄（内部 `PgPool` 本身是 Arc 包裹的连接池），`with_state` 注入后 handler 用 `State` 提取
- `sqlx::migrate!("./migrations")` 在编译期把迁移脚本打进二进制，启动时按序执行、已执行的跳过
- `PgPoolOptions::new().max_connections(5)`：连接池由 SQLx 管理，handler 拿到的 `&PgPool` 按需借连接，无需手动归还

---

## 运行与验证

启动 PostgreSQL（Docker）并运行：

```bash
docker run -d --name notes-pg \
  -e POSTGRES_USER=dev -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=notes \
  -p 5432:5432 postgres:17

DATABASE_URL=postgres://dev:dev@localhost/notes cargo run
```

curl 冒烟（覆盖 handler 的每个分支）：

```bash
curl -s -X POST localhost:8080/notes \
  -H 'content-type: application/json' \
  -d '{"title":"第一篇笔记","content":"Axum 真香"}'
# 201 {"id":1,"title":"第一篇笔记","content":"Axum 真香","created_at":"..."}

curl -s localhost:8080/notes            # 200 全量列表
curl -s localhost:8080/notes/1          # 200 单条
curl -s -X PUT localhost:8080/notes/1 \
  -H 'content-type: application/json' -d '{"title":"改标题"}'
curl -s -X DELETE localhost:8080/notes/1  # 204
curl -s localhost:8080/notes/1            # 404 {"error":"资源不存在"}
curl -s -X POST localhost:8080/notes \
  -H 'content-type: application/json' -d '{"title":"   "}'
# 400 {"error":"标题不能为空"}
```

---

## 最佳实践

### ✅ 推荐做法

- **输入输出模型分离**：`CreateNote`/`UpdateNote` 只含客户端可写字段，`Note` 才含 `id`/`created_at`——防止客户端伪造服务端字段
- **错误在边界翻译一次**：service 抛领域错误，`IntoResponse` 做唯一一次状态码映射，handler 里不出现 `StatusCode`
- **显式列名**：`SELECT id, title, ...` 而非 `SELECT *`，列序与字段增删都不会静默破坏映射

### ❌ 避免陷阱

- **不要在 repo 层判断 404**：repo 只返回 `Option`/行数，语义翻译是 service 的职责
- **不要把 `sqlx::Error` 直接返回给客户端**：连接串、表结构可能随错误消息泄漏
- **不要用 0.7 的 `/:id` 语法**：Axum 0.8 启动时会对旧语法直接报错（新语法为 `{capture}` 与 `{*wildcard}`）

### 模式不变量

- 错误映射在边界处完成一次：内部各层只携带领域错误，HTTP 语义不向内渗透
- SQL 显式列出所需列：数据契约不依赖数据库的物理列序
- 连接是池化资源：应用持有池，请求借用连接，任何一层都不自建连接

---

## 常见问题

### Q1: `sqlx::query!` 宏和运行时 `query_as` 怎么选？

**A**: `query!`/`query_as!` 宏在**编译期**连库（或读 `.sqlx` 离线缓存）校验 SQL 与类型，能抓住列名拼错、类型不匹配，代价是构建依赖 `DATABASE_URL` 或 `cargo sqlx prepare` 离线文件。教学与原型阶段用运行时 `query_as` 更顺畅；生产服务建议宏 + 离线缓存提交入库（详见 [状态与数据库（SQLx）](../frameworks/05-state-and-database-sqlx.md)）。

### Q2: handler 之间需要共享"可变状态"怎么办？

**A**: 继续放进 `AppState`：计数器用 `AtomicU64`，复杂结构用 `Mutex`/`RwLock`（同步锁够用），跨请求广播用 `tokio::sync::broadcast`——后者正是 [WebSocket 实时应用](./04-websocket-realtime.md) 的主题。原则与桌面项目一致：状态归最小必要作用域，锁临界区最小化。

---

## 扩展方向

- **练习 1（基础）**: 给列表接口加分页（`?page=&size=`），repo 层加 `LIMIT/OFFSET` 与总数查询
- **练习 2（进阶）**: 引入 `tower-http` 的 `TraceLayer`，给每个请求输出结构化日志（tracing span）
- **练习 3（挑战）**: 为 repo 层写集成测试——用 `sqlx::test` 宏自动建隔离测试库，见 [单元与集成测试](../testing/01-unit-integration-tests.md)

---

## 相关资源

### 📖 交叉引用

- 📄 **[Axum 要点字典](../reference/framework-essentials/11-axum-essentials.md)** — 提取器/响应/中间件全量参考
- 📄 **[并发与 async（Tokio 入门）](../basics/09-concurrency-async.md)** — 本篇异步语法的原理层
- 📄 **[错误处理](../basics/05-error-handling.md)** — anyhow/thiserror 与本篇错误分层的衔接
- 📄 **[WebSocket 实时应用](./04-websocket-realtime.md)** — 在本服务上叠加实时通道
- 📄 **[多端发布流水线](./05-multiplatform-release.md)** — notes-api 作为服务端产物进入统一发布
- 📄 **[单元与集成测试](../testing/01-unit-integration-tests.md)** — repo 层集成测试的完整策略
- 📖 **[Axum 官方文档](https://docs.rs/axum/0.8/axum/)** — 路由与提取器权威参考

---

## 📝 总结

### 核心要点回顾

1. **三层单向依赖**: handler(HTTP) → service(业务) → repo(SQL)，错误向上传递、边界翻译
2. **`IntoResponse` 统一出口**: 领域错误一次映射为状态码 + JSON 体
3. **SQLx 双件套**: `PgPool` 连接池 + `migrate!` 迁移随启动执行

### 学习成果检查

- [ ] 能说出 handler/service/repo 各自禁止出现的东西
- [ ] 能解释 `ServiceError` 与 `ApiError` 为什么分成两个类型
- [ ] 能用 curl 走通全部五个接口与两条错误路径

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team

> 🎯 **下一步**: 服务端已能"请求-响应"；[项目实战 4：WebSocket 实时应用](./04-websocket-realtime.md) 让服务器学会主动推送。
