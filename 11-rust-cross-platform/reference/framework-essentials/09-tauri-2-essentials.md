# Tauri 2.11 精要

> **文档简介**: Tauri 2 配置与 Rust 侧 API 的全量速查——`tauri.conf.json` 核心字段表、`Builder` 链式 API、能力-权限系统、CSP、窗口配置与 CLI 命令
>
> **目标读者**: 已掌握 Rust 基础、开始搭建 Tauri 桌面/移动应用的中级开发者
>
> **前置知识**: Rust 模块系统与 Cargo；前端工程基本概念（dev server / 构建产物目录）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#rust` `#tauri` `#reference` `#cross-platform` |
| **更新日期** | `2026年9月` |

</details>

> 版本基线：Tauri **2.11**（技术基线区块见模块 [README](../../README.md)，正文中易变层版本号以该区块为准）。

## 🎯 学习目标

- ✅ **读懂并编写** `tauri.conf.json`：根级字段、`app`/`build`/`bundle` 三大块
- ✅ **组装 Rust 入口**：`Builder` 链式 API 的完整调用顺序
- ✅ **配置安全模型**：capabilities 能力文件、权限标识符语法、CSP 指令
- ✅ **速查 CLI**：dev/build/icon/signer 等命令与常用 flag

---

## 🔍 进程模型一句话

Tauri 应用 = **Rust 二进制核心** + **系统 WebView**（Windows: WebView2 / macOS: WKWebView / Linux: WebKitGTK）。前端不打包浏览器，Rust 不暴露完整 Node API——前后端仅通过 IPC 命令与事件通信（见 [10-tauri-ipc-commands](./10-tauri-ipc-commands.md)）。架构细节见 [01-tauri-2-architecture](../../frameworks/01-tauri-2-architecture.md)。

---

## 📋 tauri.conf.json 核心字段表

文件位于 `src-tauri/tauri.conf.json`（v2 schema）。**未知字段直接报错**（schema 有 `deny_unknown_fields` 校验），拼错字段名不会静默失败。

### 根级字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `$schema` | string | 填 `https://schema.tauri.app/config/2` 可获得编辑器补全 |
| `productName` | string | 应用显示名，也是打包产物名 |
| `version` | string | 应用版本；缺省时回退到 `Cargo.toml` 的版本 |
| `identifier` | string | 应用唯一 ID（反向域名格式，如 `com.example.app`）；**发布后不可更改**（影响签名/数据目录） |
| `mainBinaryName` | string | 主二进制文件名（少用，默认跟随 productName） |
| `app` | object | 运行时配置：窗口、安全、全局 API |
| `build` | object | 前端开发/构建接入配置 |
| `bundle` | object | 打包配置 |
| `plugins` | object | 各插件配置命名空间（键为插件名） |

### `build` 子对象

| 字段 | 说明 |
|------|------|
| `beforeDevCommand` | `tauri dev` 启动前执行的命令（通常为前端 dev server，如 `npm run dev`） |
| `devUrl` | 开发时 WebView 加载的 URL（如 `http://localhost:5173`） |
| `beforeBuildCommand` | `tauri build` 前执行的命令（前端生产构建） |
| `frontendDist` | 生产模式下 WebView 加载的静态资源目录（相对 `src-tauri`，如 `../dist`） |

### 最小骨架（Vite 前端）

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "MyApp",
  "version": "0.1.0",
  "identifier": "com.example.myapp",
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [
      {
        "title": "MyApp",
        "width": 800,
        "height": 600
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": ["icons/32x32.png", "icons/icon.icns", "icons/icon.ico"]
  }
}
```

**关键点解析**:
- `csp: null` 表示禁用 CSP——仅限原型期，生产必须配置（见下文 CSP 节）
- `identifier` 一旦发布即冻结，开发期就要定好
- `targets: "all"` 构建当前平台全部安装包格式

---

## 🔧 Builder 链式 API

Rust 入口在 `src-tauri/src/lib.rs`（桌面与移动共用），`main.rs` 只调用它。

### 链式方法速查

| 方法 | 用途 |
|------|------|
| `tauri::Builder::default()` | 创建 Builder |
| `.plugin(tauri_plugin_xxx::init())` | 注册插件（每个插件一次，顺序影响初始化次序） |
| `.manage(state)` | 注册托管状态（类型必须唯一，详见 [10-tauri-ipc-commands](./10-tauri-ipc-commands.md)） |
| `.setup(\|app\| Ok(()))` | 启动钩子：`app.manage()`、`app.state::<T>()`、获取 `app.handle()` |
| `.invoke_handler(tauri::generate_handler![cmd_a, cmd_b])` | 注册前端可调用的命令（**漏注册 = 前端 invoke 报命令不存在**） |
| `.on_window_event(\|window, event\| { ... })` | 全局窗口事件监听 |
| `.on_page_load(\|webview, payload\| { ... })` | 页面加载完成钩子 |
| `.run(tauri::generate_context!())` | 启动事件循环；宏在编译期读取 `tauri.conf.json` 与资源 |
| `.build(tauri::generate_context!())` | 拿到 `App` 实例后自行 `app.run()`（需要处理 `RunEvent` 时用） |

### 完整入口示例

```rust
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(AppState::default())
        .setup(|app| {
            // app.handle() 克隆一份 AppHandle，供任意线程/回调使用
            let handle = app.handle().clone();
            std::thread::spawn(move || {
                // 后台线程中通过 handle 发事件、调状态
                let _ = handle;
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::greet,
            commands::read_note
        ])
        .on_window_event(|window, event| {
            // 如：关闭最后一扇窗口时退出
            let _ = (window, event);
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**关键点解析**:
- `generate_context!()` 宏要求 `tauri.conf.json` 存在且合法，配置错误在编译期暴露
- `#[cfg_attr(mobile, tauri::mobile_entry_point)]`：移动端入口由 Tauri 生成，桌面端由 `main.rs` 调用 `run()`
- `.expect(...)` 而非 `unwrap`：Builder 初始化失败属于不可恢复场景
- 插件与 `manage` 应在 `setup` 之前调用，保证命令执行时状态已就绪

---

## 🔐 能力-权限系统（Capabilities）

Tauri 2 的核心安全模型：**前端对插件/核心 API 的每一次调用都必须被某条 capability 授权**。权限按 `插件名:权限名` 命名，核心功能视为 `core` 插件。

### 能力文件

位置：`src-tauri/capabilities/*.json`。该目录下的文件**默认全部启用**；一旦在 `tauri.conf.json` 的 `app.security.capabilities` 中显式列出，则以列表为准。

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "main-capability",
  "description": "主窗口基础权限",
  "windows": ["main"],
  "permissions": [
    "core:path:default",
    "core:event:default",
    "core:window:default",
    "core:app:default",
    "core:window:allow-set-title",
    "fs:allow-home-read"
  ]
}
```

### 字段表

| 字段 | 说明 |
|------|------|
| `identifier` | 能力文件自身的唯一标识 |
| `description` | 人类可读说明 |
| `windows` | 授权给哪些**窗口** label（如 `["main"]`；`["*"]` 全部） |
| `webviews` | 授权给哪些 webview label（多 webview 场景） |
| `local` | 是否作用于本地（打包内嵌）页面，默认 `true` |
| `remote` | `{ "urls": ["https://*.example.com"] }`——授权远程域时必填 |
| `permissions` | 权限标识符数组，支持 `default` 集合与单条 `allow-*`/`deny-*` 条目 |
| `platforms` | 限定平台：`["linux", "windows", "macOS", "iOS", "android"]`，省略即全平台 |

### 权限标识符语法

```
core:window:default            → 核心插件 window 的 default 权限集
core:window:allow-set-title    → 单条细粒度允许（放行 setTitle）
fs:allow-home-read             → fs 插件的 read-home 权限
fs:deny-home-read              → deny 条目优先级高于 allow
```

`*` 通配符（如 `fs:*`）只用于开发调试，禁止出现在生产 capabilities 中。`tauri build` 时权限集固化进二进制；`gen/schemas/` 目录是自动生成的 schema，可放心 gitignore。

---

## 🛡️ CSP（Content Security Policy）

配置于 `app.security.csp`：字符串或对象（对象形式键为指令名）。Tauri 会**自动为自身注入的内联脚本追加 nonce/hash**，因此不必为 Tauri 核心 IPC 放开 `unsafe-inline`。

```json
{
  "app": {
    "security": {
      "csp": {
        "default-src": "'self' customprotocol: asset:",
        "connect-src": "ipc: http://ipc.localhost",
        "font-src": ["https://fonts.gstatic.com"],
        "img-src": "'self' asset: http://asset.localhost blob: data:",
        "style-src": "'unsafe-inline' 'self' https://fonts.googleapis.com"
      }
    }
  }
}
```

**关键点解析**:
- `connect-src` 必须包含 `ipc: http://ipc.localhost`——这是 Tauri IPC 的通道，删掉后前端全部命令调用失败
- `asset:` / `http://asset.localhost`：使用 asset 协议读取本地文件时需要
- `style-src` 的 `'unsafe-inline'` 常被前端框架（内联样式）逼出来，脚本来源仍保持收紧
- `default-src` 兜底所有未列出的指令，从最严开始逐条放宽

---

## 🪟 窗口配置（app.windows[]）

数组内每个对象是一扇启动时创建的窗口；多窗口用不同 `label` 区分。

| 字段 | 默认 | 说明 |
|------|------|------|
| `label` | `"main"` | 窗口唯一标识，事件/权限/target 均引用它 |
| `title` | — | 标题栏文字 |
| `width` / `height` | `800` / `600` | 逻辑像素尺寸 |
| `x` / `y` / `center` | — | 位置；`center: true` 居中 |
| `url` | — | 加载路径；`/` 开头为内嵌页面，`http(s)://` 为远程 |
| `resizable` / `fullscreen` / `maximized` | — | 尺寸行为 |
| `decorations` | — | `false` 隐藏系统标题栏（自绘窗口） |
| `transparent` / `alwaysOnTop` / `alwaysOnBottom` | — | 视觉/置顶行为 |
| `dragDropEnabled` | `true` | HTML5 拖放与 Tauri 文件拖放事件的开关（`false` 时走浏览器原生拖放） |
| `userAgent` | — | 覆盖 WebView UA |
| `create` | `true` | `false` = 仅注册配置，不随启动创建（运行时再 `WebviewWindowBuilder` 构造） |

> 以上默认值仅为已核实项；完整字段以 `$schema` 补全提示为准（与版本绑定）。

---

## 🖥️ CLI 命令表

安装：`cargo install tauri-cli --locked`（或前端包管理器安装 `@tauri-apps/cli`，用 `npm run tauri ...` 调用）。以下命令均为速查、不实际执行。

```bash
cargo tauri dev                              # 开发模式：跑 beforeDevCommand + 热重载
cargo tauri build                            # 生产构建 + 按 bundle.targets 打包
cargo tauri build --config src-tauri/tauri.beta.conf.json   # 叠加一份覆盖配置
cargo tauri icon ./app-icon.png              # 由源图生成全平台图标集到 src-tauri/icons
cargo tauri info                             # 打印环境/工具链/依赖诊断（报障先跑这个）
cargo tauri init                             # 向既有前端项目注入 src-tauri 骨架
cargo tauri migrate                          # v1 → v2 的配置与 API 迁移助手
cargo tauri signer generate -w ~/.tauri/myapp.key   # 生成更新签名密钥对
```

---

## 🎨 最佳实践

capabilities 定义窗口或 WebView 能调用的受控能力，默认权限集合也需逐项理解；自定义业务命令还要验证资源路径和授权，不因已经注册命令就自动安全。状态必须在命令实际调用前准备好，但配置链的书写顺序不能简单等同于运行时顺序。

应用标识、数据目录和更新身份一起规划，变更后需要迁移与升级测试。收紧 CSP 或权限后，验证正常命令仍可用、越界访问确实被拒绝，不能只检查配置文件“看起来严格”。

## ❓ 常见问题

### Q1: `tauri dev` 改了 `tauri.conf.json` 没生效？
**A**: 部分字段（如 `identifier`、bundle）只影响 Rust 侧，需重启 dev；窗口字段走热更新。拿不准就重启。

### Q2: 前端报 `window.__TAURI__ is not defined`？
**A**: 不装 `@tauri-apps/api` 而用全局脚本时，须在 `app` 下设 `"withGlobalTauri": true` 并重启。推荐直接用 npm 包 `import { invoke } from '@tauri-apps/api/core'`。

---

## 🧱 模式不变量

1. **前端默认不可信**：WebView 内代码对系统能力的每一次访问都是一次显式授权决策（capability + permission），授权边界在进程间而非函数间
2. **配置错误要在编译期/启动期失败**：schema 校验与 `generate_context!` 的意义是把"配置漂移"挡在发布前，而非运行时容错
3. **窗口是权限与事件的最小分发单元**：label 即身份，事件路由、能力授予、IPC 目标都按 label 寻址
4. **CSP 是纵深防御而非唯一防线**：ACL 管"能调什么 API"，CSP 管"能加载什么资源"，二者不可互相替代

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[Tauri IPC 命令](./10-tauri-ipc-commands.md)**: Builder 里注册的命令如何编写与调用
- 📄 **[Tauri 2 架构](../../frameworks/01-tauri-2-architecture.md)**: 进程模型与插件体系全景
- 📄 **[Tauri 插件体系](../../frameworks/02-tauri-plugins.md)**: 插件开发与权限定义
- 📄 **[Serde 指南](../library-guides/13-serde-guide.md)**: 命令参数/返回值的序列化底座

### 参考章节
- 📖 **[模块 README 技术基线](../../README.md)**: 本篇所有版本号的单一事实来源

---

## 📝 总结

### 核心要点回顾
1. **配置即契约**: `tauri.conf.json` 的字段错误在编译/启动期失败，`$schema` 提供全量补全
2. **安全模型两件套**: capabilities 管 API 授权（按窗口 label），CSP 管资源加载（ipc 指令必留）
3. **Builder 顺序敏感**: plugin → manage → setup → invoke_handler → run

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
