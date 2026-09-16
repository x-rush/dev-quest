# Tauri 2 插件体系：官方插件、权限申请与自研插件

> **文档简介**: Tauri 的一切系统能力都走插件——本篇给出官方插件全景清单、`tauri add` 一键安装流程、capabilities 细粒度权限写法（含 scope 收紧），以及用官方脚手架开发自研插件的完整结构。
>
> **目标读者**: 已跑通 Tauri 2 第一个工程、需要接入文件/对话框/自动更新等系统能力的中级开发者
>
> **前置知识**: [Tauri 2 架构](./01-tauri-2-architecture.md)（command/event/capabilities 三件套）
>
> **预计时长**: 4-5 小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 操作指南（frameworks/） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#tauri` `#plugins` `#security` |
| **更新日期** | `2026年9月` |

> 版本基线见模块 [README](../README.md)（Tauri 2.11，2026-09-16 核实）。插件清单与权限名以[官方插件页](https://v2.tauri.app/plugin/)为准。

## 🎯 学习目标

完成本篇后，你将能够：

- ✅ **按需选插件**: 从官方插件表中找到对应系统能力的插件及其 npm/crate 包名
- ✅ **一键接线**: 用 `npm run tauri add <plugin>` 完成 Rust + JS + 权限三处自动接线
- ✅ **收紧权限**: 用 scoped permission 对象把 fs 等插件限制到指定路径
- ✅ **开发自研插件**: 用 CLI 脚手架生成插件工程并暴露自己的 JS API

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

### 概念一：插件是"三层包装"

**定义**: 每个 Tauri 插件由三层构成：**Rust crate**（`tauri-plugin-<name>`，封装系统能力并以 command 暴露）、**权限集**（`allow-*/deny-*` 权限与 scope，供 capabilities 引用）、**JS 绑定包**（`@tauri-apps/plugin-<name>`，把 `invoke('plugin:<name>|<command>')` 包装成普通函数）。

**使用场景**:
- 应用进程内需要系统能力（文件系统、剪贴板、通知）时，装官方插件而非裸写 IPC 命令
- 自研插件适合把"多个应用复用的 Rust 逻辑"抽成可分享单元

### 概念二：官方插件清单

**定义**: 以下为官方维护、按本模块基线（Tauri 2.11 时期）常用的插件。JS 包名统一为 `@tauri-apps/plugin-<名>`，crate 名统一为 `tauri-plugin-<名>`。

| 插件 | 用途 | 代表权限 | 平台备注 |
|------|------|---------|---------|
| fs | 文件读写/目录操作 | `fs:default`、`fs:allow-*` + scope | 全平台 |
| dialog | 原生打开/保存/确认对话框 | `dialog:default` | 全平台 |
| opener | 用系统默认程序打开 URL/路径 | `opener:default` | 全平台（打开链接首选） |
| shell | 执行外部命令/sidecar | `shell:allow-execute` + scope | 全平台 |
| updater | 应用内自动更新 | `updater:default` | 仅桌面 |
| global-shortcut | 全局快捷键 | `global-shortcut:allow-register` | 仅桌面 |
| clipboard-manager | 剪贴板读写 | `clipboard-manager:allow-write-text` | 全平台 |
| http | Rust 侧 fetch（绕过 CORS） | `http:default` | 全平台 |
| log | 多目标日志 | `log:default` | 全平台 |
| notification | 系统通知 | `notification:default` | 全平台 |
| process | 退出/重启进程 | `process:allow-restart` | 全平台 |
| os | 操作系统信息 | `os:default` | 全平台 |
| store | 键值持久化存储 | `store:default` | 全平台 |
| window-state | 记忆窗口大小位置 | `window-state:default` | 仅桌面 |
| single-instance | 单实例互斥 | Rust 侧启用 | 仅桌面 |
| deep-link | 深链协议处理 | `deep-link:default` | 桌面+移动 |
| barcode-scanner / biometric / nfc / haptics | 移动专属硬件能力 | 各自 `default` | 仅移动 |

完整支持表（含逐平台勾选）见[官方插件页](https://v2.tauri.app/plugin/)。另有 `core:*` 系核心权限（窗口、事件、路径等），由 `core:default` 统一覆盖。

### 概念三：权限申请模型——capabilities

**定义**: 插件装好 ≠ 前端可用。每个窗口能用什么，由 `src-tauri/capabilities/*.json` 里的 capability 决定；目录内所有 capability 文件默认自动启用。

**关键字段**:

- `identifier`: capability 名字
- `windows`: 授予哪些窗口（label 数组，如 `["main"]`，可 `["*"]`）
- `permissions`: 权限字符串数组（`插件名:权限名`），也接受**对象形式**做 scope 收紧
- `platforms`（可选）: 限定平台子集（`"macOS"`、`"windows"`、`"linux"`、`"iOS"`、`"android"`）

**两种权限形态**:

1. 字符串型：`"fs:default"`——启用插件默认权限集
2. 对象型：`{"identifier": "fs:allow-exists", "allow": [{"path": "$APPDATA/*"}]}`——授予具体能力并限定作用域；仅有 `allow-*` 权限而没有 scope 时访问仍会被拒（`forbidden path`）

### 概念四：JavaScript API 注入的两条路

**定义**: 前端拿到插件 API 有两种方式：

1. **npm 绑定包**（推荐）：`npm install @tauri-apps/plugin-<name>`，类型完备、tree-shaking 友好
2. **全局注入**：`tauri.conf.json` 设 `app.withGlobalTauri: true`，页面得到 `window.__TAURI__` 全局对象——适合无构建工具的纯静态前端

---

## 🛠️ 实践指南

### 步骤一：一键安装插件

**目标**: 把 fs 插件完整接入工程（Rust + JS + 权限三处）

**操作指南**:

```bash
# 在 Tauri 项目根目录执行：自动完成
# 1) cargo add tauri-plugin-fs  2) lib.rs 注册 .plugin(tauri_plugin_fs::init())
# 3) capabilities 追加 fs:default  4) npm install @tauri-apps/plugin-fs
npm run tauri add fs
```

**验证方法**: `src-tauri/Cargo.toml` 出现 `tauri-plugin-fs` 依赖；`src-tauri/capabilities/default.json` 的 `permissions` 数组出现 `"fs:default"`；`package.json` 出现 `@tauri-apps/plugin-fs`。

### 步骤二：从 JS 调用插件

**目标**: 读写应用数据目录中的 JSON 配置

**操作指南**: 使用下方"代码示例一"；注意所有路径都配合 `BaseDirectory` 使用，让插件把相对路径钉在已知根目录（如 `AppData`）内。

**验证方法**: 运行后检查系统应用数据目录（如 Windows `%APPDATA%/<identifier>`、macOS `~/Library/Application Support/<identifier>`）下生成了目标文件。

### 步骤三：收紧权限 scope

**目标**: 前端只允许访问应用自己的配置目录，禁止其他路径

**操作指南**: 把 capability 从 `"fs:default"` 升级为"default + 带 allow 列表的细粒度权限"（见代码示例二）。scope 支持 `$APPDATA`、`$HOME`、`$DOCUMENT` 等内置变量与 `*`/`**` 通配。

**验证方法**: 访问 allow 列表内路径成功；访问列表外路径（如 `$HOME/secrets`）返回 `forbidden path`。

### 步骤四：接入 updater（自动更新）

**目标**: 应用启动时检查更新、下载安装并重启

**操作指南**:

1. `npm run tauri add updater` 安装插件
2. `tauri.conf.json` 加 `bundle.createUpdaterArtifacts: true` 与 `plugins.updater` 配置（见代码示例三）
3. `tauri signer generate` 生成签名密钥对，公钥内容填入 `pubkey`（**是内容，不是文件路径**）
4. 前端接入检查逻辑（见代码示例四）

**验证方法**: 打包产物旁边出现更新签名文件；改动 `latest.json` 端点版本号后应用提示更新。

### 步骤五：开发自研插件

**目标**: 用官方脚手架生成 `tauri-plugin-clipboard-sync` 插件工程

**操作指南**:

```bash
# 需要 JS 绑定时直接 new；纯 Rust 插件加 --no-api；要移动端加 --android/--ios
npx @tauri-apps/cli plugin new clipboard-sync
cd tauri-plugin-clipboard-sync
npm install && npm run build   # 先构建 guest-js 绑定
```

生成的目录结构：

```text
tauri-plugin-clipboard-sync/
├── src/                # Rust 实现
│   ├── lib.rs          # 入口：init() -> TauriPlugin
│   ├── commands.rs     # 对 webview 暴露的命令
│   ├── models.rs       # 共享数据结构
│   ├── desktop.rs / mobile.rs   # 平台实现分支
│   └── error.rs        # 插件错误类型
├── permissions/        # 权限定义（default.toml 等）
├── guest-js/           # JS 绑定源码（构建后进 dist-js）
├── android/ ios/       # 可选：移动端原生工程
├── build.rs            # 声明命令清单，自动生成 allow-/deny- 权限
└── Cargo.toml / package.json
```

**验证方法**: 模板自带 `examples/` 示例应用；`cargo build` 通过并在示例应用里 invoke 到插件命令。

---

## 💻 代码示例

### 示例一：fs 插件读写（JS 侧）

```typescript
import { readTextFile, writeTextFile, exists, BaseDirectory } from '@tauri-apps/plugin-fs';

// baseDir 把相对路径钉进应用数据目录，避免路径穿越
await writeTextFile('notes/config.json', '{"theme":"dark"}', {
  baseDir: BaseDirectory.AppData,
});

const raw = await readTextFile('notes/config.json', { baseDir: BaseDirectory.AppData });

if (await exists('notes/backup.json', { baseDir: BaseDirectory.AppData })) {
  console.log('备份存在');
}
```

### 示例二：capabilities/default.json——默认集 + scope 收紧

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "主窗口默认能力：核心 + fs + updater",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "fs:default",
    "updater:default",
    {
      "identifier": "fs:allow-exists",
      "allow": [{ "path": "$APPDATA/*" }]
    },
    {
      "identifier": "fs:scope",
      "allow": [{ "path": "$APPDATA" }, { "path": "$APPDATA/**/*" }]
    }
  ]
}
```

**关键点解析**:
- `core:default` 覆盖核心权限（窗口/事件/路径等）；插件权限按 `插件:权限` 命名
- 对象形式的权限 = 能力 + scope：`fs:allow-exists` 单独存在不授予任何路径
- `$schema` 指向 `../gen/schemas/`，编辑器据此补全权限名

### 示例三：updater 的 tauri.conf.json 配置

```json
{
  "bundle": { "createUpdaterArtifacts": true },
  "plugins": {
    "updater": {
      "pubkey": "<tauri signer generate 生成的公钥内容>",
      "endpoints": [
        "https://releases.example.com/{{target}}/{{arch}}/{{current_version}}"
      ]
    }
  }
}
```

### 示例四：updater 检查-下载-重启（JS 侧）

```typescript
import { check } from '@tauri-apps/plugin-updater';
import { relaunch } from '@tauri-apps/plugin-process';

let downloaded = 0;

const update = await check();
if (update) {
  await update.downloadAndInstall((event) => {
    switch (event.event) {
      case 'Started':
        console.log(`开始下载，总大小 ${event.data.contentLength}`);
        break;
      case 'Progress':
        downloaded += event.data.chunkLength;
        break;
      case 'Finished':
        console.log('下载完成');
        break;
    }
  });
  await relaunch();
}
```

### 示例五：自研插件最小实现

```rust
// src/lib.rs —— 插件唯一入口：init() 返回 TauriPlugin
use tauri::{
    plugin::{Builder, TauriPlugin},
    Manager, Runtime,
};

mod commands;

// 应用侧约定调用 tauri_plugin_clipboard_sync::init()
pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new("clipboard-sync")
        .invoke_handler(tauri::generate_handler![commands::sync_once])
        .setup(|app, _api| {
            // 插件内部状态：manage 后命令可用 app.state() 拿到
            app.manage(commands::SyncState::default());
            Ok(())
        })
        .build()
}
```

```rust
// src/commands.rs —— 插件命令就是普通 Tauri 命令
use tauri::{command, AppHandle, Manager, Runtime};

#[derive(Default)]
pub struct SyncState(pub std::sync::Mutex<u64>);

#[command]
pub(crate) async fn sync_once<R: Runtime>(app: AppHandle<R>) -> Result<u64, String> {
    let state = app.state::<SyncState>();
    let mut count = state.0.lock().map_err(|e| e.to_string())?;
    *count += 1;
    Ok(*count)
}
```

```rust
// build.rs —— 列出命令名，构建系统自动生成 allow-/deny- 权限
const COMMANDS: &[&str] = &["sync_once"];

fn main() {
    tauri_plugin::Builder::new(COMMANDS).build();
}
```

```toml
# permissions/default.toml —— 默认权限集，应用装好后可被 capabilities 引用
"$schema" = "schemas/schema.json"

[default]
description = "clipboard-sync 插件默认权限"
permissions = ["allow-sync-once"]
```

```typescript
// guest-js/index.ts —— JS 绑定：命令名格式为 plugin:<插件名>|<命令>
import { invoke } from '@tauri-apps/api/core';

export async function syncOnce(): Promise<number> {
  return await invoke('plugin:clipboard-sync|sync_once');
}
```

**关键点解析**:
- 插件命令与应用命令写法一致，但前端调用必须带 `plugin:<名>|` 前缀
- `build.rs` 的 `COMMANDS` 按命令函数的 snake_case 填写，自动生成 `allow-sync-once` / `deny-sync-once`
- 命令参数从前端传 JS 驼峰（`userInput`），Rust 侧自动映射 `user_input`

---

## 🎨 最佳实践

### ✅ 推荐做法

- **先试官方插件**: 系统能力优先官方实现（已处理跨平台怪癖 + 权限集成），自研只做业务特有部分
- **权限按需收紧**: 上线前把开发期图省事的宽 scope（`**`）替换为最小路径集，capability 变更走 code review
- **updater 公钥进配置、私钥进 CI**: 私钥只在构建机环境变量中出现，泄露即失去更新通道的信任根

### ❌ 避免陷阱

- **pubkey 填文件路径**: updater 要求公钥**内容**直接内联在配置里，填路径会导致运行时校验失败
- **改权限后忘记重启**: capabilities 编译进二进制（`generate_context!`），改完必须重新 `tauri dev/build`
- **shell 插件当 opener 用**: 执行任意命令走 `shell` 且必须配 scope 白名单；只是"打开网页/文件"用 `opener`，能力面小得多

---

## ❓ 常见问题

### Q1: 调用插件报 `forbidden path` / permission denied？

**A**: 三步排查：① capability 的 `permissions` 数组是否包含该插件权限（光装插件不授权不可用）；② 是否用了对象权限却漏了 scope（`allow-*` 不带 scope 不授予任何路径）；③ `windows` 数组是否覆盖了当前窗口 label。改完记得重启 dev。

### Q2: 自研插件的应用侧 `init()` 在哪调用？

**A**: 与官方插件一致——`Builder::default().plugin(tauri_plugin_clipboard_sync::init())`。插件名（`Builder::new("clipboard-sync")`）决定 JS 侧的 `plugin:clipboard-sync|命令` 前缀，与应用侧 crate 名无关。

### Q3: 哪些插件在移动端不可用？

**A**: global-shortcut、single-instance、window-state 等桌面概念在移动端无意义，官方支持表中标注了逐平台可用性；跨端项目应把桌面专属插件放在 `#[cfg(desktop)]` 分支注册，避免移动端编译失败。

---

## 🧭 模式不变量

1. **权限是资源边界的声明**: 插件权限体系的本质是"能力 → 资源范围"的映射，scope 粒度越细，前端被攻陷后的损失半径越小
2. **安装 ≠ 授权**: 任何跨进程能力的暴露都要经过显式声明（capability），这是默认拒绝模型与"默认全开"框架的分水岭
3. **JS 绑定是协议的投影**: 命令名、参数名、错误格式共同构成前后端契约；绑定包的价值是把契约固化为可类型检查的接口
4. **自研插件优先做成"可复用单元"**: 独立版本号、独立权限集、独立文档，而不是把业务代码堆进应用 crate

---

## 🔗 相关资源

### 📖 延伸阅读

- **指南**: [Tauri 2 架构](./01-tauri-2-architecture.md) - IPC 三件套与 ACL 模型的底层逻辑
- **字典**: [Tauri IPC Commands](../reference/framework-essentials/10-tauri-ipc-commands.md) - command 参数映射与错误传递
- **指南**: [桌面打包](./07-desktop-packaging.md) - updater 签名产物如何进入发布流水线

### 🛠️ 工具资源

- **官方插件页**: [v2.tauri.app/plugin](https://v2.tauri.app/plugin/) - 官方插件全表与逐平台支持
- **权限参考**: [Capabilities 文档](https://v2.tauri.app/security/capabilities/) - capability 文件全字段
- **项目**: [02 Tauri 桌面笔记](../projects/02-tauri-notes-app.md) - fs/dialog/updater 的综合实战

---

## 📝 总结

### 核心要点回顾

1. **三层结构**: crate + 权限集 + JS 绑定，`tauri add` 一次接线三处
2. **默认拒绝**: capability 显式列举窗口可用的权限，scope 把能力钉进路径白名单
3. **自研插件**: `cli plugin new` 脚手架 + `build.rs` 权限自动生成，命令前缀 `plugin:<名>|`

### 学习成果检查

- [ ] 能说出 fs/dialog/opener/updater 四个插件的用途与代表权限
- [ ] 完成 fs 插件安装并用 scope 限制到 `$APPDATA`
- [ ] 跑通 updater 的检查-下载-重启闭环
- [ ] 用脚手架生成自研插件并从示例应用 invoke 成功

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
