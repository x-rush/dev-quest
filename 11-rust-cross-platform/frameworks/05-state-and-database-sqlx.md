# 状态共享与 SQLx 0.9 数据库访问

> **文档简介**: Web 服务里最难管的两样东西——共享状态与数据库连接。本篇讲透 `Arc`/`State` 的共享与锁粒度模型，并系统掌握 SQLx 0.9：编译期校验的 `query!`/`query_as!`、离线 `.sqlx` 缓存、事务边界，以及 0.9 的 `AssertSqlSafe` 破坏性变化。
>
> **目标读者**: 已会用 Axum 组路由（04 篇）、要把服务接上 PostgreSQL 的中级开发者
>
> **前置知识**: [04 Axum Web 栈](./04-axum-web-stack.md)（State 注入）、[basics 08 智能指针](../basics/08-smart-pointers.md)、SQL 基础
>
> **预计时长**: 5-6 小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 操作指南（frameworks/） |
| **难度** | ⭐⭐⭐ 精通 |
| **标签** | `#rust` `#axum` `#sqlx` `#postgres` `#state` |
| **更新日期** | `2026年9月` |

> 版本基线见模块 [README](../README.md)：SQLx 0.9 / Axum 0.8 / Tokio 1.53（2026-09-16 核实）。SQLx 0.9 于 2026-05-06 发布，仓库已迁至 transact-rs 组织，破坏性变化见核心概念四。

## 🎯 学习目标

完成本篇后，你将能够：

- ✅ **设计共享状态**: 区分只读共享（Arc/Pool）、原子计数、互斥可变三档，锁粒度对齐不变量
- ✅ **编译期校验 SQL**: 用 `query!`/`query_as!` 让"列名写错"变成编译错误而非线上事故
- ✅ **离线构建**: 生成并提交 `.sqlx` 缓存，CI 无数据库也能过编译
- ✅ **管好事务**: 用 `begin/commit/rollback` 把业务原子性翻译成连接语义

## 📋 目录

- [核心概念](#核心概念)
- [实践指南](#实践指南)
- [代码示例](#代码示例)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [模式不变量](#模式不变量)
- [相关资源](#相关资源)

---

## 🔍 核心概念

### 概念一：Arc 与共享状态——共享、原子、互斥三档

**定义**: `Arc<T>` 只解决"多所有者只读共享"；要可变，必须配内部可变性。按需选择三档：

| 需求 | 工具 | 代价 |
|------|------|------|
| 只读（配置、连接池） | 直接放 `Arc` 内 / Pool 自带 | 零锁 |
| 简单计数/开关 | `Arc<AtomicU64>` 等原子量 | 无锁 CAS |
| 复杂结构的互斥更新 | `Arc<Mutex<T>>` / `RwLock<T>` | 阻塞临界区 |

**Axum 里的对应物**: `State<T>` 提取的 `T` 正是"以 Arc 语义共享"的状态——`Pool` 克隆廉价（内部即 Arc 连接池），因此 `AppState` 自身实现 `Clone` 直接克隆即可。

**实证**（去依赖化演示，本机 rustc --edition 2024 通过，4 线程并发计数无丢失）:

```rust
// Arc<Mutex<T>> 共享状态模型（去依赖化演示）
// Axum 的 State<T> / Tauri 的 Builder::manage 底层共享语义与此一致：
// Arc 提供跨线程只读共享，内部可变性由 Mutex/RwLock 显式声明。
use std::sync::{Arc, Mutex};
use std::thread;

#[derive(Debug)]
struct AppState {
    app_name: String,          // 只读字段：无需任何锁
    request_count: Mutex<u64>, // 可变字段：内部可变性，锁粒度到字段
}

impl AppState {
    fn new(app_name: &str) -> Self {
        Self {
            app_name: app_name.to_string(),
            request_count: Mutex::new(0),
        }
    }

    /// 模拟一次请求计数（对应 handler 中的 State 提取）
    fn record(&self) -> u64 {
        let mut count = self.request_count.lock().expect("锁被污染");
        *count += 1;
        *count
    }
}

fn main() {
    let state = Arc::new(AppState::new("dev-quest-api"));

    // 4 个 worker 线程并发处理，各 100 次请求
    let workers: Vec<_> = (0..4)
        .map(|_| {
            let state = Arc::clone(&state);
            thread::spawn(move || {
                for _ in 0..100 {
                    state.record();
                }
            })
        })
        .collect();
    for worker in workers {
        worker.join().expect("线程 panic");
    }

    // 只读字段任意线程可读；计数无丢失
    assert_eq!(state.app_name, "dev-quest-api");
    assert_eq!(*state.request_count.lock().unwrap(), 400);
    println!("4 线程 × 100 次请求，request_count = 400，无竞态丢失");
}
```

**异步陷阱**: `std::sync::Mutex` 的锁守护**不能跨 `.await` 持有**（guard 不满足 Send，且阻塞 runtime worker）。跨 await 的互斥改用 `tokio::sync::Mutex`；能塞进临界区的计算尽量缩短到"拿值-放值"。

### 概念二：SQLx 定位与连接池

**定义**: SQLx 是"编译期校验 SQL 的异步工具箱"——不是 ORM：没有查询构建器，SQL 手写；换来的是 SQL 与 Rust 类型在**编译时**核对。核心类型：

- `PgPoolOptions`: 连接池配置器（max_connections、acquire_timeout）
- `PgPool`: 连接池句柄，**克隆即共享**（内部 Arc），全应用一个实例
- `sqlx::Error`: 统一错误类型，配合 `?` 与 axum 的 `IntoResponse`

### 概念三：query! / query_as!——把 schema 变成类型

**定义**: 两个宏在编译时做三件事：连接 `DATABASE_URL`（或读取 `.sqlx` 离线缓存）→ 解析 SQL → 核对参数与结果列的类型/可空性。

- `query!`: 返回匿名记录（按列名访问）
- `query_as!(Struct, sql, args...)`: 按**列名**映射到具名结构体字段，列名/类型错配是编译错误
- 执行方式按语义选：`fetch_one`（恰一行）/ `fetch_optional`（0 或 1）/ `fetch_all`（多行）/ `execute`（写）

**收益本质**: 数据库 schema 变更（改列名、改可空性）在 CI 编译阶段爆炸，而不是在流量高峰的运行时。

### 概念四：SQLx 0.9 的关键变化（2026-05-06 发布）

**定义**: 从 0.8 升级必须核对的破坏性/行为变化（源自官方 changelog）：

1. **`SqlSafeStr` 取代裸字符串**（破坏性）: 所有 `query*()` 函数现在接受 `impl SqlSafeStr`——只实现了 `&'static str` 与 `AssertSqlSafe`。动态拼接的 SQL 必须显式包 `AssertSqlSafe(...)`，把"是不是动态 SQL"变成类型可见的事实
2. **`sqlx.toml` 配置文件**（新）: 支持 DATABASE_URL 改名、全局类型覆盖、迁移表重定位（`sqlx-toml` feature，sqlx-cli 默认开启）
3. **offline 变为可选 feature**（破坏性）: 离线能力不再无条件编入（可脱离 serde 构建）；CI 离线编译确认 features 含相应开关；`SQLX_OFFLINE_DIR` 环境变量优先于默认 `.sqlx` 目录
4. **Postgres nullability 推断更准**: 部分查询的 `query!` 输出类型可能变化（改用通用计划推断）
5. **仓库迁移**: 移至 transact-rs 组织，`cargo install --locked sqlx-cli`（git 源）不再可用，走 crates.io 安装
6. **MSRV 1.94**（0.9 发布周期），本模块基线 Rust 1.98.1 满足

---

## 🛠️ 实践指南

### 步骤一：依赖与数据库准备

**目标**: 可编译的依赖集 + 可连接的 PostgreSQL

**操作指南**:

```toml
# Cargo.toml
[dependencies]
axum = "0.8"
tokio = { version = "1.53", features = ["macros", "rt-multi-thread", "net"] }
serde = { version = "1.0.229", features = ["derive"] }
# runtime + TLS + 驱动 + 宏，按需增删
sqlx = { version = "0.9", features = ["runtime-tokio", "tls-rustls", "postgres", "macros"] }
```

```bash
# sqlx-cli 从 crates.io 安装（0.9 起 git + --locked 已不可用）
cargo install sqlx-cli --no-default-features --features rustls,postgres

# .env（sqlx 宏与 CLI 都会自动读取）
# DATABASE_URL=postgres://dev:dev@localhost:5432/devquest

sqlx database create
sqlx migrate run
```

**验证方法**: `psql "$DATABASE_URL" -c '\dt'` 能列出迁移建出的表。

### 步骤二：定义 AppState 并接入 Router

**目标**: 连接池与进程内计数共享给全部 handler

**操作指南**: 落地"代码示例一"的 `AppState`，在 `main` 里 connect 后 `with_state`（代码示例二）。

**验证方法**: 应用启动日志显示连接成功；`/healthz` 返回的计数随请求递增。

### 步骤三：编译期校验查询

**目标**: 用 `query_as!` 替换手写结果映射

**操作指南**: 落地"代码示例三"。故意把 SQL 里 `title` 改成 `titel` 再编译，确认得到列名错误——这就是编译期校验在工作。

**验证方法**: `cargo build` 在列名写错时报错、改回后通过。

### 步骤四：离线缓存与 CI

**目标**: 提交 `.sqlx` 缓存，无数据库环境可编译

**操作指南**:

```bash
# 开发机（DATABASE_URL 可用）：生成/更新缓存目录 .sqlx/
cargo sqlx prepare

# 把 .sqlx/ 提交进仓库；CI 中无 DATABASE_URL 时宏自动回退缓存
# 显式离线开关与自定义目录：
SQLX_OFFLINE=true cargo build
# SQLX_OFFLINE_DIR=./.sqlx   # 0.9 起该变量优先级更高
```

**验证方法**: CI（或本机断开数据库）`cargo check` 通过。

### 步骤五：事务边界

**目标**: 多语句原子执行

**操作指南**: 落地"代码示例四"。原则：事务从 `begin` 到 `commit` 期间独占同一连接，中途 `?` 提前返回时**连接归还即回滚**。

**验证方法**: 人为让第二条语句失败，确认第一条的效果没有落库。

---

## 💻 代码示例

### 示例一：AppState——两种可变性来源

```rust
// src/state.rs
use sqlx::PgPool;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

#[derive(Clone)]
pub struct AppState {
    pub pool: PgPool, // 克隆便宜：Pool 内部就是 Arc 包裹的连接池
    pub requests: Arc<AtomicU64>, // 原子计数档：无锁；AppState 能 Clone 的前提
}

impl AppState {
    pub async fn connect(db_url: &str) -> Result<Self, sqlx::Error> {
        let pool = sqlx::postgres::PgPoolOptions::new()
            .max_connections(5) // 连接是稀缺资源，对齐数据库 max_connections 预算
            .acquire_timeout(std::time::Duration::from_secs(3))
            .connect(db_url)
            .await?;
        Ok(Self {
            pool,
            requests: Arc::new(AtomicU64::new(0)),
        })
    }

    pub fn bump(&self) -> u64 {
        self.requests.fetch_add(1, Ordering::Relaxed) + 1
    }
}
```

### 示例二：main 装配

```rust
// src/main.rs
mod notes;
mod state;

use axum::{routing::get, Json, Router};
use state::AppState;

async fn healthz(state: axum::extract::State<AppState>) -> Json<String> {
    Json(format!("requests={}", state.bump()))
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let db_url = std::env::var("DATABASE_URL").expect("需要 DATABASE_URL");
    let state = AppState::connect(&db_url).await?;

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    let app = Router::new()
        .route("/healthz", get(healthz))
        .nest("/api", notes::router())
        .with_state(state);

    axum::serve(listener, app).await?;
    Ok(())
}
```

### 示例三：query_as! 编译期校验查询

```rust
// src/notes.rs
use axum::{extract::{Path, State}, routing::get, Json, Router};
use serde::Serialize;
use state::AppState;

#[derive(Serialize)]
pub struct Note {
    pub id: i64,
    pub title: String,
}

pub fn router() -> Router<AppState> {
    Router::new()
        .route("/notes", get(list_notes))
        .route("/notes/{id}", get(get_note))
}

// 列名/类型/可空性在编译时核对：titel 这类笔误是编译错误
async fn list_notes(State(state): State<AppState>) -> Json<Vec<Note>> {
    let rows = sqlx::query_as!(
        Note,
        r#"SELECT id, title FROM notes ORDER BY updated_at DESC LIMIT 100"#
    )
    .fetch_all(&state.pool)
    .await
    .expect("查询失败"); // handler 层简化演示；生产错误映射见 06 篇

    Json(rows)
}

// 参数化查询：$1 占位由宏核对类型（i64），杜绝注入
async fn get_note(
    State(state): State<AppState>,
    Path(id): Path<i64>,
) -> Result<Json<Note>, axum::http::StatusCode> {
    let note = sqlx::query_as!(
        Note,
        r#"SELECT id, title FROM notes WHERE id = $1"#,
        id
    )
    .fetch_optional(&state.pool)
    .await
    .map_err(|_| axum::http::StatusCode::INTERNAL_SERVER_ERROR)?
    .ok_or(axum::http::StatusCode::NOT_FOUND)?;

    Ok(Json(note))
}
```

### 示例四：事务

```rust
// 多语句原子性：同一连接、要么全成要么全无
pub async fn remove_tag(pool: &sqlx::PgPool, note_id: i64, tag: &str) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    sqlx::query!(
        "DELETE FROM tags WHERE note_id = $1 AND name = $2",
        note_id,
        tag
    )
    .execute(&mut *tx) // 语句挂在事务上，而非池上
    .await?;

    sqlx::query!(
        "INSERT INTO tag_log (note_id, action) VALUES ($1, 'removed')",
        note_id
    )
    .execute(&mut *tx)
    .await?;

    tx.commit().await?; // 未走到这里就 return/panic：连接归还时自动回滚
    Ok(())
}
```

### 示例五：0.9 动态 SQL——AssertSqlSafe

```rust
// ❌ 0.9 起编译失败：query*() 只接受 &'static str 或 AssertSqlSafe
// let sql = format!("SELECT id, {column} FROM notes");
// sqlx::query(&sql).fetch_all(&state.pool).await?;

// ✅ 显式断言：安全性承诺由调用方代码背书
use sqlx::{row::Row, AssertSqlSafe};

pub async fn by_whitelisted_column(
    pool: &sqlx::PgPool,
    column: &str,
) -> Result<Vec<Note>, sqlx::Error> {
    // 动态部分只能来自白名单——AssertSqlSafe 解除的是编译器检查，不是安全检查
    let column = match column {
        "id" => "id",
        "title" => "title",
        _ => return Err(sqlx::Error::Configuration("非法列名".into())),
    };
    let sql = format!("SELECT id, {column} FROM notes ORDER BY id LIMIT 100");

    let rows = sqlx::query(AssertSqlSafe(sql)).fetch_all(pool).await?;
    Ok(rows
        .into_iter()
        .map(|row| Note {
            id: row.get("id"),
            title: row.get("title"),
        })
        .collect())
}
```

---

## 🎨 最佳实践

### ✅ 推荐做法

- **全应用一个 Pool**: 池是进程级单例（`with_state` 注入），按部署规格给 `max_connections`，多实例部署时乘上实例数留余量
- **`.sqlx` 进仓库**: 编译期校验的价值在 CI 无数据库时依然成立——缓存让 schema 契约随代码走
- **锁粒度对齐不变量**: 计数用原子量、配置只读、真正需要互斥的多字段更新才上 `Mutex`，并尽量短临界区

### ❌ 避免陷阱

- **`std::Mutex` 跨 `.await`**: guard 不 Send 导致编译错误是好事；更糟的是把数据库调用放进临界区造成排队。跨 await 用 `tokio::sync::Mutex`，或重构为"临界区内取值、锁外做 IO"
- **把用户输入拼进 SQL**: 0.9 的 `AssertSqlSafe` 不是免死金牌——动态部分必须白名单化，断言只对"已审查过的拼接"负责
- **事务里做慢 IO**: 事务独占连接，把外部 HTTP 调用塞进事务会放大连接饥饿

---

## ❓ 常见问题

### Q1: 编译报 "set DATABASE_URL"？

**A**: 宏需要 schema 信息，三选一：① 项目根放 `.env` 写 `DATABASE_URL=...`（sqlx 自动读取）；② 开发/CI 都连不上库时，先在有库的机器 `cargo sqlx prepare` 生成 `.sqlx` 缓存并提交，配合离线 feature 编译；③ 用 `SQLX_OFFLINE_DIR` 指向非默认缓存位置（0.9 起优先级更高）。

### Q2: SQLx 0.8 → 0.9 升级，代码会哪里炸？

**A**: 高频四处：① 动态 SQL——`sqlx::query(&format!(...))` 全部改 `AssertSqlSafe` 包裹（示例五）；② Postgres 查询的可空性推断变化可能让 `query!` 输出从 `T` 变 `Option<T>` 或反之；③ 若依赖离线编译，确认 features 仍启用离线能力（0.9 起可选）；④ CI 里 git 源安装 sqlx-cli 的命令失效，改 crates.io。

### Q3: PgPool、Arc<PgPool>、AppState 该怎么放？

**A**: `PgPool` 本身就是廉价句柄（内部 Arc），**不需要再包 Arc**。放进 `AppState`，`AppState` derive `Clone`（其余字段也要可 Clone，原子计数用 `Arc<AtomicU64>`），`with_state` 一次，处处 `State<AppState>`。

---

## 🧭 模式不变量

1. **连接池归框架所有**: 业务代码只经池"借还"连接，绝不自建自管连接生命周期——池化资源的所有权永远在基础设施层
2. **SQL 校验要么编译期、要么显式断言**: schema 契约必须在构建流水线闭环（宏 + 缓存）；绕过闭环（AssertSqlSafe）是显式签字而非默认路径
3. **锁的粒度等于不变量的粒度**: 锁保护的是"数据组合出的不变量"而非数据本身——粒度错配要么丢性能要么丢一致性
4. **事务边界即业务原子性边界**: 跨语句一致性只能靠同一事务（同一连接）表达，任何"先写一半再说"的设计都该被否决

---

## 🔗 相关资源

### 📖 延伸阅读

- **字典**: [Axum Essentials](../reference/framework-essentials/11-axum-essentials.md) - State/IntoResponse 与本篇衔接
- **字典**: [智能指针全表](../reference/language-concepts/07-smart-pointers.md) - Arc 内部机制（引用计数与 Send/Sync）
- **指南**: [认证中间件](./06-auth-middleware.md) - AppState 承载 JWT 密钥的下一步

### 🛠️ 工具资源

- **API 文档**: [docs.rs/sqlx](https://docs.rs/sqlx/) - PoolOptions/Transaction/宏文档
- **CLI 文档**: [sqlx-cli](https://docs.rs/sqlx-cli/) - prepare/migrate/database 子命令
- **对照阅读**: [09-nodejs-backend](../../09-nodejs-backend/README.md) - 连接池与 SQL-first 思路的 Node 侧对照

---

## 📝 总结

### 核心要点回顾

1. **共享三档**: 只读直接共享、计数用原子、互斥用锁——`AppState: Clone` 是 axum 状态的全部门槛
2. **编译期校验**: `query_as!` 按列名映射 + 类型核对，`.sqlx` 缓存把契约带进 CI
3. **0.9 变化**: `AssertSqlSafe` 显式化动态 SQL、offline 可选化、仓库迁移 transact-rs

### 学习成果检查

- [ ] 说得出三种共享档位各适合什么数据
- [ ] 故意写错列名并看到编译错误（然后修好）
- [ ] 无数据库环境下靠 `.sqlx` 缓存通过 `cargo check`
- [ ] 解释事务中途 return 为什么会回滚

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
