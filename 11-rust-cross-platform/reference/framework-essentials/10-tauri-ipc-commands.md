# Tauri IPC 命令

> **文档简介**: `#[tauri::command]` 的全量规则速查——参数与返回值约定、State 托管状态、Event 双向通道、异步命令的借用限制、错误类型 Serialize 约定与前端 `invoke` 对照
>
> **目标读者**: 已跑通 Tauri 项目骨架、需要设计 Rust↔前端接口的中级开发者
>
> **前置知识**: [09-tauri-2-essentials](./09-tauri-2-essentials.md)（Builder 与 invoke_handler）；Serde derive 基础

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#rust` `#tauri` `#reference` `#ipc` |
| **更新日期** | `2026年9月` |

> 版本基线：Tauri **2.11** / Serde **1.0.229**（见模块 [README](../../README.md) 技术基线区块）。

## 🎯 学习目标

- ✅ **声明命令**：掌握参数映射（camelCase/`rename_all`）、特殊参数（State/AppHandle/Window）与返回值规则
- ✅ **管理状态**：`manage` + `State<'_, T>` + 锁的惯用法
- ✅ **双向通信**：Rust `emit` ↔ 前端 `listen` 的事件全表
- ✅ **处理错误**：自定义错误类型满足 `Serialize` 约定的标准写法

---

## 🔍 命令声明规则

### 参数

| 规则 | 说明 |
|------|------|
| 普通参数 | 从前端 JSON 对象反序列化，要求实现 `Deserialize` |
| 键名映射 | Rust `snake_case` 参数默认对应前端 **camelCase** 键（`user_id` ← `userId`） |
| 改映射 | `#[tauri::command(rename_all = "snake_case")]` 可改整体命名风格 |
| 缺参/类型不符 | invoke 直接失败（`invalid args`），不会以 `None` 兜底 |
| `tauri::AppHandle` | 注入应用句柄，不占前端参数位 |
| `tauri::Window` / `tauri::WebviewWindow` | 注入调用方窗口，不占前端参数位 |
| `tauri::State<'_, T>` | 注入托管状态，不占前端参数位 |

### 返回值

| 形式 | 前端结果 |
|------|---------|
| `impl Serialize` | Promise resolve 该值 |
| `Result<T, E>`（T/E 均 `Serialize`） | `Ok` → resolve；`Err` → reject（E 被序列化后传给 `catch`） |
| `()` | resolve `null` |

---

## 💻 最小全链路示例

```rust
// src-tauri/src/commands.rs
use serde::Serialize;

#[derive(Serialize)]
pub struct CustomResponse {
    pub message: String,
    pub other_val: usize,
}

#[tauri::command]
async fn my_custom_command(
    window: tauri::WebviewWindow,        // 特殊参数：注入调用方窗口
    number: usize,                       // 普通参数：前端传 { number: 42 }
    database: tauri::State<'_, Database> // 特殊参数：托管状态
) -> Result<CustomResponse, String> {
    println!("Called from {}", window.label());
    Ok(CustomResponse { message: "hi".into(), other_val: 42 + number })
}
```

```rust
// src-tauri/src/lib.rs
pub struct Database;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(Database {})
        .invoke_handler(tauri::generate_handler![commands::my_custom_command])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

```typescript
// 前端（@tauri-apps/api）
import { invoke } from '@tauri-apps/api/core';

invoke<CustomResponse>('my_custom_command', { number: 42 })
  .then((res) => console.log(res.message, res.other_val))
  .catch((e) => console.error(e)); // Err 分支的 E 序列化结果
```

**关键点解析**:
- 命令名默认是函数名的 snake_case 形式（`my_custom_command`），invoke 用同名
- 未在 `generate_handler!` 注册的命令，前端调用直接报"不存在"
- `State<'_, Database>` 要求 `Database` 已被 `manage`，否则命令执行时 panic

---

## 🗃️ State 托管状态

```rust
use std::sync::Mutex;
use tauri::{Manager, State};

#[derive(Default)]
struct AppState {
    counter: Mutex<i32>,   // 可变状态用锁包住（State 只给共享引用）
    config: Mutex<Config>,
}

// 两个注册入口等价：
// 1) Builder 链上：  .manage(AppState::default())
// 2) setup 钩子里：  app.manage(AppState::default())
//    app.manage 重复注册同类型返回 false（首次 true）

#[tauri::command]
fn increment(state: State<'_, AppState>) -> i32 {
    let mut counter = state.counter.lock().unwrap();
    *counter += 1;
    *counter
}

// 非 command 上下文用 Manager trait 读取：
// let state: State<AppState> = app.state();
// let n = *app.state::<AppState>().counter.lock().unwrap(); // turbofish 写法
```

**关键点解析**:
- 每个类型只能托管一份；需要多实例时包一层新类型
- `state` 内部是 `Arc`，跨线程共享无成本；可变访问一律走 `Mutex`/`RwLock`
- 需要 `use tauri::Manager;` 才能调用 `manage`/`state`

---

## 📡 Event 事件通道

命令是"前端拉"模型，事件是"后端推"模型。Rust 侧需引入对应 trait：`tauri::Emitter`、`tauri::Listener`。

### Emitter（Rust → 前端）

| 方法 | 行为 |
|------|------|
| `app.emit(name, payload)` | 广播：所有 webview 的全局监听者都收到 |
| `app.emit_to("main", name, payload)` | 定向：只发给 label 为 `main` 的 webview |
| `app.emit_filter(name, payload, \|t\| ...)` | 过滤：按 `EventTarget` 闭包筛选（如 `EventTarget::WebviewWindow { label }`） |

### Listener（前端 → Rust / Rust 内部）

| 方法 | 行为 |
|------|------|
| `app.listen(name, handler)` | 监听全局事件；返回 `EventId`，`unlisten(id)` 注销 |
| `app.listen_any(name, handler)` | 不区分来源地监听 |
| `app.once(name, handler)` | 一次性监听 |

```rust
use tauri::{AppHandle, Emitter};

#[tauri::command]
fn download(app: AppHandle, url: String) {
    app.emit("download-started", &url).unwrap();
    for progress in [1, 15, 50, 80, 100] {
        app.emit("download-progress", progress).unwrap();
    }
}
```

```rust
use tauri::{Listener, Manager};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            // setup 中监听前端 emit 的事件
            app.listen("frontend-asked", |event| {
                // event.payload() 是 JSON 字符串，需再反序列化
                if let Ok(payload) = serde_json::from_str::<MyPayload>(event.payload()) {
                    println!("{:?}", payload);
                }
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

```typescript
// 前端监听（需 capability 含 core:event:default）
import { listen } from '@tauri-apps/api/event';

const unlisten = await listen<number>('download-progress', (event) => {
  console.log(event.payload); // 已反序列化
});
// 退出作用域时调用 unlisten() 防泄漏
```

**关键点解析**:
- Rust 侧 payload 进出都是 JSON 字符串/`Serialize` 值；前端侧 API 已自动反序列化
- 事件名与命令名同处一个命名空间即可读性而言建议分开前缀（如 `evt:download-progress`）
- 前端 `listen`/`emit` 受 ACL 门控：capability 里保留 `core:event:default`

---

## ⏳ 异步命令与借用限制

```rust
#[tauri::command]
async fn slow_fetch(url: String) -> Result<String, String> {
    let resp = reqwest::get(&url).await.map_err(|e| e.to_string())?;
    Ok(resp.text().await.map_err(|e| e.to_string())?)
}
```

**硬规则**：async 命令的**借用参数**（`State<'_, T>`、`&str` 等非 `'static` 引用）必须以 `Result<T, E>` 作为返回类型。

```rust
// ❌ 编译失败：async fn 持有借用参数但返回值不是 Result
// #[tauri::command]
// async fn bad(state: State<'_, AppState>) -> i32 { ... }

// ✅ 包一层 Result 即可
#[tauri::command]
async fn good(state: State<'_, AppState>) -> Result<i32, ()> {
    Ok(*state.counter.lock().unwrap())
}
```

**为什么**：async 命令的 future 会被 spawn 到 Tauri 内置的异步运行时（`tauri::async_runtime`，基于 tokio），future 必须满足 `Send`——裸借用无法跨 `await` 存活；`Result` 包装让宏改用值传递路径绕开该限制。同步命令无此约束（返回值可任意）。

---

## 🧯 错误类型的 Serialize 约定

`Err(E)` 的 `E` 必须实现 `Serialize`。三种常见形态，按需选择：

```rust
// 形态一：最简 —— E = String
#[tauri::command]
fn login(user: String, password: String) -> Result<String, String> {
    if user == "tauri" && password == "tauri" { Ok("logged_in".into()) }
    else { Err("invalid credentials".into()) }
}
```

```rust
// 形态二：thiserror 枚举 + 手动 Serialize（官方推荐结构）
use serde::ser::Serializer;

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error(transparent)]
    Io(#[from] std::io::Error),
    #[error("file {0} not found")]
    NotFound(String),
}

impl Serialize for Error {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(self.to_string().as_ref()) // 前端拿到字符串
    }
}

pub type Result<T> = std::result::Result<T, Error>;

#[tauri::command]
fn read_file(path: String) -> Result<String> {
    std::fs::read_to_string(path).map_err(Error::from)
}
```

```rust
// 形态三：derive(Serialize) 的结构体 —— 前端拿到对象（可分支处理）
#[derive(serde::Serialize)]
struct ApiError {
    kind: String,   // "not_found" / "io" / ...
    message: String,
}
```

**关键点解析**:
- 形态二的 `thiserror` 只生成 `Display`，`Serialize` 仍需手动实现——这是官方 docs 的标准组合
- 前端 `catch(e)` 收到的是 **E 序列化后的值**（字符串/对象），不是 Error 实例
- 错误信息避免暴露文件系统路径等内部细节（WebView 内容可能是不可信输入）

---

## 🔀 权限边界速记

- **插件命令**（含 `core:*`）受 ACL 门控：未被 capability 授权 → 前端调用被直接拒绝
- **应用自定义命令**默认不经过 ACL；需要限制时在命令体内自行校验 `window.label()` 或调用来源
- 自定义命令在 Rust 侧执行、不受 WebView 沙箱限制；受约束的是发起 invoke 的前端侧

---

## 🎨 最佳实践

### ✅ 推荐做法
- **命令粒度对齐业务操作**：一个命令 = 一次完整业务动作，避免前端拼装多次 invoke 的中间态
- **长任务走事件**：超过几百毫秒的工作，立即 `emit` started，进度用事件推送，结束再 `emit` finished
- **前端封装类型层**：`invoke<T>()` 泛型 + 每命令一个包装函数，把命令名与参数形状收敛到单文件

### ❌ 避免陷阱
- **camelCase 拼写错位**：Rust `file_path` ↔ JS `filePath`，对不上报 `invalid args`，是最高频错误
- **async + State 忘了 Result**：编译错误信息指向 Send 约束，记住"借用参数必 Result"
- **事件监听不注销**：前端组件卸载时忘记 `unlisten()`，监听器随窗口累积

## ❓ 常见问题

### Q1: 前端 invoke 报 `invalid args` ？
**A**: 参数键名与 Rust 侧不匹配（camelCase 检查）或参数类型不兼容。命令没在 `generate_handler!` 注册时报的是"command not found"，可据此区分。

### Q2: 能否在命令里阻塞长任务？
**A**: 同步命令中执行长阻塞会占用其执行线程，界面虽不冻结但后续命令排队。耗时 IO 一律写 async 命令；CPU 密集任务用 `tauri::async_runtime::spawn_blocking`。

---

## 🧱 模式不变量

1. **跨进程边界即序列化边界**：参数、返回值、事件 payload 都必须经过 Serde，任何生命周期引用都不可能出现在边界上——这是"借用必 Result"规则的根源
2. **拉与推分离**：命令（invoke）是请求-响应，事件（emit/listen）是发布-订阅；把"后端主动通知"塞进命令轮询是模型误用
3. **状态所有权归 Rust 侧**：前端只持有视图状态，业务状态以类型为单位托管在 Rust，通过锁控制可变性
4. **授权按调用方判定**：前端是潜在不可信方，能力校验发生在"谁能调"（ACL）与"调用方是谁"（window label）两层

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[Tauri 2 精要](./09-tauri-2-essentials.md)**: Builder 注册与 capability 授权的宿主文档
- 📄 **[Tauri 插件体系](../../frameworks/02-tauri-plugins.md)**: 插件命令的权限定义与 scope
- 📄 **[Serde 指南](../library-guides/13-serde-guide.md)**: 参数/返回值/错误序列化的完整规则
- 📄 **[Future·Pin·Waker](../language-concepts/08-async-internals.md)**: 理解"future 必须 Send"的底层机制

### 参考章节
- 📖 **[模块 README 技术基线](../../README.md)**: 本篇所有版本号的单一事实来源

---

## 📝 总结

### 核心要点回顾
1. **命令规则三条**：参数默认 camelCase、返回值必须 Serialize、`Err` 即前端 reject
2. **状态一个入口**：`manage` 注册 + `State<'_, T>` 注入 + 锁保护可变部分
3. **异步一条硬规则**：借用参数的 async 命令必须返回 `Result`

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
