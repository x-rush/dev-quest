# 项目实战 2：rustnotes —— Tauri 2 桌面笔记应用（React + TS）

## 分阶段练习与验收

**最小阶段**：先让前端调用一个 Tauri 命令并显示结果。

**验收结果**：参数与错误可序列化，前端能处理失败，权限范围明确。

**扩展顺序**：再接真实笔记文件或数据库，区分 IPC 与普通 HTTP。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> **文档简介**: 用 Tauri 2 构建一个跨平台桌面笔记应用：React+TS 前端通过 IPC 调用 Rust 命令完成 CRUD，`State<Mutex<HashMap>>` 管理内存状态，JSON 文件持久化到系统应用数据目录，并覆盖窗口配置与 capabilities 权限模型
>
> **目标读者**: 完成 Rust 入门路径并有一定 React/TS 经验的开发者
>
> **前置知识**: 所有权与借用、`Mutex` 共享状态、async 基础；前端侧需熟悉 React 函数组件与 TS 类型

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 操作指南（项目实战） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#tauri` `#react` `#typescript` `#桌面应用` |
| **更新日期** | `2026年9月` |
| **内容状态** | 教学设计已编写；按本文验收条件完成本地或目标环境验证 |

</details>

> 版本基线以 [模块 README 技术基线区块](../README.md) 为准：Tauri 2.11、Serde 1.0.229。本篇 Rust 块未做本机编译（需 Tauri 全链依赖与 WebView 环境），API 均按 Tauri 2 官方文档核实。

## 🎯 学习目标

完成本项目后，你将能够：

- ✅ **理解 Tauri 2 进程模型**: 前端 WebView 与 Rust core 通过 IPC 边界通信
- ✅ **编写 `#[tauri::command]`**: 参数注入、`State` 托管可变状态、错误以 `Result<T, String>` 回传
- ✅ **设计持久化**: 启动时从磁盘恢复、每次变更后落盘的应用数据目录策略
- ✅ **配置安全边界**: `tauri.conf.json` 窗口定义 + capabilities 声明式权限

## 📋 目录

- [架构总览与需求](#架构总览与需求)
- [分步实现](#分步实现)
- [运行与验证](#运行与验证)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [扩展方向](#扩展方向)
- [相关资源](#相关资源)
- [总结](#-总结)

---

## 架构总览与需求

### Tauri 2 架构一图流

```mermaid
graph LR
    A[WebView 渲染进程<br/>React + TS] -->|invoke| B[IPC 边界]
    B -->|Rust 命令| C[Rust Core 进程<br/>NotesState + 持久化]
    C -->|std::fs| D["$APPDATA/notes.json"]
```

- **前端**不直接触达业务数据，只通过 `invoke` 调用 Rust 命令（对照 Tauri 1 的"前端自由访问后端"模式，Tauri 2 把一切收进 capabilities 权限声明）
- **状态归属 Rust 进程**：`State<Mutex<HashMap<u64, Note>>>` 是唯一内存事实来源

### 功能需求

- 笔记三要素：`id`（自增）、`title`、`content`
- CRUD 四命令：`list_notes` / `create_note` / `update_note` / `delete_note`
- 数据持久化到 OS 应用数据目录（Windows `%APPDATA%`、macOS `~/Library/Application Support`、Linux `~/.local/share` 下的 `com.devquest.rustnotes`）
- 启动恢复：`setup` 钩子里把磁盘 JSON 装回内存

### 项目结构

```bash
npm create tauri-app@latest rustnotes -- --template react-ts
```

```
rustnotes/
├── package.json            # 前端依赖：@tauri-apps/api、@tauri-apps/plugin-fs
├── src/                    # React 前端
│   └── App.tsx
└── src-tauri/
    ├── Cargo.toml
    ├── capabilities/default.json   # 权限声明
    ├── tauri.conf.json             # 窗口与打包配置
    └── src/
        ├── main.rs         # 入口（薄壳）
        └── lib.rs          # 全部 Rust 逻辑
```

安装前端依赖并注册 Rust 侧插件：

```bash
npm install @tauri-apps/api @tauri-apps/plugin-fs
cd src-tauri && cargo add tauri-plugin-fs@2
```

---

## 分步实现

### 步骤 1：数据模型与全局状态

`src-tauri/src/lib.rs` 第一部分——状态设计：

```rust
use std::{
    collections::HashMap,
    fs,
    path::PathBuf,
    sync::Mutex,
};
use serde::{Deserialize, Serialize};
use tauri::{Manager, State};

#[derive(Serialize, Deserialize, Clone)]
pub struct Note {
    pub id: u64,
    pub title: String,
    pub content: String,
}

/// 全局状态：一把锁保护"自增 ID + 笔记表"，保证二者一致
#[derive(Default)]
pub struct NotesState {
    inner: Mutex<NotesInner>,
}

#[derive(Default)]
struct NotesInner {
    next_id: u64,
    notes: HashMap<u64, Note>,
}
```

**关键点解析**：

- `Clone` 是命令返回值跨越 IPC 边界的必要条件（序列化后传给 WebView）
- `next_id` 与 `notes` 放进同一把锁：拆成两把锁会让"取号 + 插入"不再原子
- 用 `std::sync::Mutex` 而非 `tokio::sync::Mutex`——命令持锁时间极短且不做 `.await`，同步锁更简单高效

### 步骤 2：JSON 持久化

```rust
/// 应用数据目录下的 notes.json；路径随 OS 不同由 Tauri 解析
fn storage_path(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    let dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("定位应用数据目录失败: {e}"))?;
    Ok(dir.join("notes.json"))
}

/// 整表落盘：演示项目直接全量覆盖；笔记量大时换 SQLite（见扩展方向）
fn persist(app: &tauri::AppHandle, state: &NotesState) -> Result<(), String> {
    let path = storage_path(app)?;
    let guard = state.inner.lock().map_err(|_| "状态锁中毒".to_string())?;
    let notes: Vec<&Note> = guard.notes.values().collect();
    let json =
        serde_json::to_string_pretty(&notes).map_err(|e| format!("序列化笔记失败: {e}"))?;
    drop(guard); // IO 不占锁：锁内只做取数，写盘放在锁外
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|e| format!("创建数据目录失败: {e}"))?;
    }
    fs::write(&path, json).map_err(|e| format!("写入 {} 失败: {e}", path.display()))
}
```

**关键点解析**：

- `app.path().app_data_dir()` 需要先 `use tauri::Manager`
- `drop(guard)` 显式提前释放锁，随后才做文件 IO——锁的临界区应只覆盖内存操作
- 目录可能不存在（首次运行），`create_dir_all` 兜底

### 步骤 3：四个 IPC 命令

```rust
#[tauri::command]
fn list_notes(state: State<'_, NotesState>) -> Result<Vec<Note>, String> {
    let guard = state.inner.lock().map_err(|_| "状态锁中毒".to_string())?;
    let mut notes: Vec<Note> = guard.notes.values().cloned().collect();
    notes.sort_by_key(|n| n.id);
    Ok(notes)
}

#[tauri::command]
fn create_note(
    app: tauri::AppHandle,
    state: State<'_, NotesState>,
    title: String,
    content: String,
) -> Result<Note, String> {
    if title.trim().is_empty() {
        return Err("标题不能为空".into());
    }
    let note = {
        let mut guard = state.inner.lock().map_err(|_| "状态锁中毒".to_string())?;
        let id = guard.next_id;
        guard.next_id += 1;
        let note = Note { id, title, content };
        guard.notes.insert(id, note.clone());
        note
    };
    persist(&app, &state)?;
    Ok(note)
}

#[tauri::command]
fn update_note(
    app: tauri::AppHandle,
    state: State<'_, NotesState>,
    id: u64,
    title: String,
    content: String,
) -> Result<Note, String> {
    let note = {
        let mut guard = state.inner.lock().map_err(|_| "状态锁中毒".to_string())?;
        let note = guard
            .notes
            .get_mut(&id)
            .ok_or_else(|| format!("笔记 #{id} 不存在"))?;
        note.title = title;
        note.content = content;
        note.clone()
    };
    persist(&app, &state)?;
    Ok(note)
}

#[tauri::command]
fn delete_note(
    app: tauri::AppHandle,
    state: State<'_, NotesState>,
    id: u64,
) -> Result<(), String> {
    {
        let mut guard = state.inner.lock().map_err(|_| "状态锁中毒".to_string())?;
        if guard.notes.remove(&id).is_none() {
            return Err(format!("笔记 #{id} 不存在"));
        }
    }
    persist(&app, &state)?;
    Ok(())
}
```

**关键点解析**：

- 与 CLI 项目的 `Done` 分支同理：`&mut Note` 的借用必须先结束，`persist(&state)` 才能借整个状态（E0502）；块作用域 + `clone` 收敛借用
- 命令签名里注入 `AppHandle` / `State` 即可，无需手动传参——前端只传业务参数
- 错误类型用 `String` 是入门约定；结构化错误可用 `Result<T, CommandError>` + `thiserror`，见 [Tauri IPC 命令字典](../reference/framework-essentials/10-tauri-ipc-commands.md)

### 步骤 4：装配与启动恢复

```rust
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            // 启动时把磁盘上的 notes.json 装回内存
            let path = app.path().app_data_dir()?.join("notes.json");
            let mut inner = NotesInner::default();
            if let Ok(raw) = fs::read_to_string(&path) {
                if let Ok(notes) = serde_json::from_str::<Vec<Note>>(&raw) {
                    for note in notes {
                        inner.notes.insert(note.id, note);
                    }
                }
            }
            inner.next_id = inner.notes.keys().max().copied().unwrap_or(0) + 1;
            app.manage(NotesState { inner: Mutex::new(inner) });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            list_notes,
            create_note,
            update_note,
            delete_note
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

入口薄壳 `src-tauri/src/main.rs`（Tauri 脚手架标准形态，逻辑都在 lib 里以便移动端复用）：

```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    rustnotes_lib::run();
}
```

`src-tauri/Cargo.toml` 依赖（版本基线见模块 README）：

```toml
[package]
name = "rustnotes"
version = "0.1.0"
edition = "2024"

[lib]
name = "rustnotes_lib"
crate-type = ["staticlib", "cdylib", "rlib"]

[build-dependencies]
tauri-build = { version = "2", features = [] }

[dependencies]
tauri = { version = "2.11", features = [] }
tauri-plugin-fs = "2"
serde = { version = "1.0.229", features = ["derive"] }
serde_json = "1"
```

### 步骤 5：窗口配置与 capabilities

`src-tauri/tauri.conf.json`（Tauri 2 schema，省略 `version` 字段时回退到 Cargo.toml 的包版本——多端发布时的版本策略见 [项目实战 5](./05-multiplatform-release.md)）：

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "RustNotes",
  "identifier": "com.devquest.rustnotes",
  "build": {
    "beforeDevCommand": "npm run dev",
    "devUrl": "http://localhost:5173",
    "beforeBuildCommand": "npm run build",
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [
      {
        "title": "RustNotes",
        "width": 900,
        "height": 640,
        "minWidth": 640,
        "minHeight": 480,
        "resizable": true,
        "center": true
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ]
  }
}
```

`src-tauri/capabilities/default.json`——默认能力只覆盖 app 专属目录的读，写权限需显式追加：

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "主窗口默认能力",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "fs:default",
    "fs:allow-appdata-read-recursive",
    "fs:allow-appdata-write-recursive"
  ]
}
```

### 步骤 6：React 前端

`src/App.tsx`：

```tsx
import { useCallback, useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";

interface Note {
  id: number;
  title: string;
  content: string;
}

export default function App() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);

  const refresh = useCallback(async () => {
    setNotes(await invoke<Note[]>("list_notes"));
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const submit = async () => {
    if (editingId === null) {
      await invoke("create_note", { title, content });
    } else {
      await invoke("update_note", { id: editingId, title, content });
      setEditingId(null);
    }
    setTitle("");
    setContent("");
    await refresh();
  };

  const remove = async (id: number) => {
    await invoke("delete_note", { id });
    await refresh();
  };

  return (
    <main style={{ padding: 16 }}>
      <h1>RustNotes</h1>
      <section>
        <input value={title} placeholder="标题"
               onChange={(e) => setTitle(e.target.value)} />
        <textarea value={content} placeholder="内容"
                  onChange={(e) => setContent(e.target.value)} />
        <button onClick={submit}>
          {editingId === null ? "新增" : "保存修改"}
        </button>
      </section>
      <ul>
        {notes.map((n) => (
          <li key={n.id}>
            <b>{n.title}</b>：{n.content}
            <button onClick={() => {
              setEditingId(n.id); setTitle(n.title); setContent(n.content);
            }}>编辑</button>
            <button onClick={() => remove(n.id)}>删除</button>
          </li>
        ))}
      </ul>
    </main>
  );
}
```

**关键点解析**：

- `invoke("create_note", { title, content })`：对象键与 Rust 参数名对应；Tauri 2 默认把 JS 侧 camelCase 映射到 Rust 侧 snake_case，本例参数均为单词所以无感
- 前端不做校验兜底——`create_note` 的"标题不能为空"错误会 reject 这个 Promise，真实项目应 `try/catch` 后展示 toast

追加一个"导出备份"功能，演示 fs 插件从前端直接写文件（与本节 Rust 侧持久化互不干扰）：

```tsx
import { writeTextFile, BaseDirectory } from "@tauri-apps/plugin-fs";

const backup = async (notes: Note[]) => {
  await writeTextFile("notes-backup.json", JSON.stringify(notes, null, 2), {
    baseDir: BaseDirectory.AppData,
    create: true,
  });
};
```

---

## 运行与验证

```bash
npm run tauri dev    # 开发模式：热重载前端，Rust 侧增量编译
npm run tauri build  # 产出安装包：dmg / msi / AppImage / deb
```

验证清单：

1. 新增两篇笔记 → 重启应用 → 笔记仍在（setup 恢复生效）
2. 到应用数据目录确认 `notes.json` 内容随操作更新
3. DevTools Console 执行 `invoke("delete_note", { id: 999 })` → 应收到"笔记 #999 不存在"错误

---

## 最佳实践

明确内存状态、前端投影与磁盘持久化的权威关系。锁外保存快照能缩短临界区，但两个并发保存可能按相反顺序落盘，因此还需要串行写入、版本检查或其他一致性协议，不能只要求“所有 I/O 都移出锁”。

默认 capability 集也要审阅，自定义命令还需自己的业务检查。应用标识变更可能影响数据目录和升级身份，应设计迁移；serde default 只能填缺失字段，不能替代全部格式迁移。验收并发编辑、保存失败和重启后数据。

---

## 常见问题

### Q1: 命令改名/新增参数后前端没报错，但运行时报"找不到命令"或参数缺失？

**A**: `invoke_handler(generate_handler![...])` 是唯一注册点，新增命令必须登记；参数名不匹配会在运行时 reject。开发期先用 DevTools Console 直接 `invoke` 冒烟，可把问题从"界面行为"隔离到"IPC 契约"。

### Q2: 能不能让前端直接读写 notes.json，跳过 Rust 命令？

**A**: 技术上可行（fs 插件 + 上述权限），但不应作为主路径：业务规则（自增 ID、非空校验）会散落到前端，WebView 刷新即失内存态。fs 插件的合理定位是前端侧的文件能力（备份、导入、另存为），业务状态仍归 Rust。

---

## 扩展方向

- **练习 1（基础）**: 增加 `search_notes(keyword)` 命令，标题/内容做 `contains` 匹配
- **练习 2（进阶）**: 更新改为局部落盘（追加 JSON Lines），体会"全量覆盖 vs 增量日志"的取舍
- **练习 3（挑战）**: 迁移到 SQLite（`tauri-plugin-sql` 或 Rust 侧 `rusqlite`），对照 [状态与数据库（SQLx）](../frameworks/05-state-and-database-sqlx.md)

---

## 相关资源

### 📖 交叉引用

- 📄 **[Tauri IPC 命令字典](../reference/framework-essentials/10-tauri-ipc-commands.md)** — 命令签名、参数映射与错误类型全量参考
- 📄 **[状态与数据库（SQLx）](../frameworks/05-state-and-database-sqlx.md)** — 从 HashMap 到真实数据库的升级路径
- 📄 **[单元与集成测试](../testing/01-unit-integration-tests.md)** — Rust 侧命令逻辑可脱离 WebView 测试
- 📄 **[REST API 实战](./03-axum-rest-api.md)** — 同样的 CRUD 领域模型搬到服务端
- 📄 **[多端发布流水线](./05-multiplatform-release.md)** — 把本应用接入 CI 打包
- 📖 **[Tauri 官方文档](https://v2.tauri.app/)** — capabilities 与插件体系权威来源

---

## 📝 总结

### 核心要点回顾

1. **IPC 契约**: `#[tauri::command]` + `generate_handler!` 是前后端唯一接口，参数经 serde 跨界
2. **状态与锁**: `Mutex<Inner>` 一把锁保一致性，临界区只含内存操作
3. **持久化闭环**: setup 恢复 + 变更落盘，`app_data_dir` 让数据随 identifier 归位

### 学习成果检查

- [ ] 能解释前端 `invoke` 到 Rust 命令执行的完整链路
- [ ] 能说明为什么 `persist` 里要先 `drop(guard)`
- [ ] 能读懂 capabilities JSON 并为 fs 插件补一个新权限

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team

> 🎯 **下一步**: 桌面应用把数据存在本地；[项目实战 3：Axum REST API](./03-axum-rest-api.md) 把同样的 CRUD 模型搬到服务器，用 PostgreSQL 取代 JSON 文件。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
