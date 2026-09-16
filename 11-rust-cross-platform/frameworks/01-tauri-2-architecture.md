# Tauri 2 架构：核心进程模型与多端支持

> **文档简介**: 拆解 Tauri 2 的进程模型与 IPC 面——Rust 核心进程承载业务逻辑、系统 WebView 渲染前端，一套代码跑通 Windows/macOS/Linux/iOS/Android。读完后你能解释"为什么 Tauri 产物小"，并搭出第一个多端可跑的工程骨架。
>
> **目标读者**: 有 Rust 基础（所有权/借用过关）与任意前端框架经验的中级开发者
>
> **前置知识**: [basics 09 并发与 async](../basics/09-concurrency-async.md)、npm/包管理器基本操作
>
> **预计时长**: 3-4 小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 操作指南（frameworks/） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#tauri` `#architecture` `#ipc` `#cross-platform` |
| **更新日期** | `2026年9月` |

> 版本基线见模块 [README](../README.md)：Tauri 2.11 / Rust 1.98.1（2026-09-16 核实）。本篇的 API 层如有升级，以官方文档为准核对。

## 🎯 学习目标

完成本篇后，你将能够：

- ✅ **画出进程模型图**: 说清核心进程与 WebView 进程各自拥有什么、边界在哪
- ✅ **对比选型**: 从体积、内存、安全模型三个维度判断 Tauri vs Electron 是否适合你的项目
- ✅ **搭建多端骨架**: 用 create-tauri-app 生成工程并接入 iOS/Android 目标
- ✅ **设计 IPC 面**: 用 command + event + capabilities 三件套控制前端可调用的能力

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

### 概念一：双进程模型——Rust 核心 + 系统 WebView

**定义**: Tauri 应用由两部分进程组成——一个运行你编写的 Rust 二进制的**核心进程**（主进程），以及承载前端页面的**WebView 渲染进程**。关键在于：WebView 不是打包进来的浏览器，而是**操作系统自带**的 WebView 组件。

**各平台的 WebView 来源**:

| 平台 | WebView 实现 |
|------|-------------|
| Windows | WebView2（Edge 内核，Win10+ 系统组件） |
| macOS / iOS | WKWebView（Safari 内核） |
| Android | 系统 WebView（Chromium 内核） |
| Linux | WebKitGTK |

Tauri 对这些系统组件的封装层是默认运行时 **Wry**（跨平台 WebView 绑定库），你通常不需要直接接触它。

**使用场景**:
- 业务逻辑（文件读写、数据库、密钥处理）留在 Rust 核心进程
- 界面交互、表单、动画交给前端（React/Vue/Svelte 均可）

### 概念二：与 Electron 对比——三维度权衡

**定义**: Electron 为每个应用捆绑一个完整 Chromium + Node.js 运行时；Tauri 复用系统 WebView，后端换成 Rust。这是"一致性换体积"与"体积换一致性"的经典权衡。

| 维度 | Tauri 2 | Electron |
|------|---------|----------|
| 渲染引擎 | 系统 WebView（随操作系统浮动） | 捆绑 Chromium（全平台一致） |
| 后端运行时 | Rust 编译产物（静态链接） | Node.js 解释执行 |
| 产物体积 | 通常数 MB 至十几 MB | 通常数十至上百 MB |
| 内存占用 | WebView 由系统按需复用 | 每应用独立 Chromium 实例 |
| 安全模型 | **默认拒绝**的能力门控（capabilities/ACL）+ CSP | Node 主进程天然全权，需自行收敛 |
| UI 一致性风险 | 不同系统 WebView 渲染差异需测试覆盖 | Chromium 锁定行为 |

**判断原则**: 追求安装包轻量、原生安全边界、与系统集成的工具类/桌面应用——Tauri 占优；要求像素级一致的复杂 Web 应用、深度依赖 Node 生态——Electron 仍是稳妥选择。

### 概念三：多端支持——desktop · iOS · Android

**定义**: Tauri 2 的核心能力是"一份 Rust 核心 + 一份前端"，三端复用。桌面端开箱即用；移动端通过 CLI 脚手架把 Rust 工程接入原生构建体系（iOS 走 Xcode/SwiftPM，Android 走 Gradle/Android Studio），生成的原生工程放在 `src-tauri/gen/` 下，不要手工改动。

**注意边界**: 移动端并非所有官方插件都支持（如 global-shortcut、single-instance 是桌面专属），移动专属插件（barcode-scanner、biometric、nfc）桌面无意义。开发前查[官方插件支持表](https://v2.tauri.app/plugin/)。

### 概念四：进程间通信面——command / event / ACL

**定义**: 前端与 Rust 之间只有三条受控通道：

1. **Command（前端 → Rust）**: 前端 `invoke("命令名", 参数)`，Rust 侧用 `#[tauri::command]` 标注的函数响应，走 `invoke_handler` 注册表
2. **Event（双向）**: Rust 侧 `app.emit(...)` 推送（`Emitter` trait），前端 `listen(...)` 订阅（`Listener` trait）；前端也可 `emit` 给 Rust
3. **ACL 门控**: 每个 command/插件权限都要通过 `src-tauri/capabilities/*.json` 显式授予某个窗口——Tauri 2 的安全模型核心是"默认拒绝"

**使用场景**:
- 命令适合"请求-响应"型调用（读配置、保存文件）
- 事件适合"Rust 主动通知"（下载进度、后台任务完成）

---

## 🛠️ 实践指南

### 步骤一：创建多端工程骨架

**目标**: 用官方脚手架生成 React + TypeScript 模板工程

**操作指南**:

```bash
# 生成 react-ts 模板（Node 18+ 与 Rust 工具链需已就绪）
npm create tauri-app@latest dev-notes -- --template react-ts
cd dev-notes
npm install

# 桌面端开发模式（首次运行会编译 Rust 依赖，耐心等待）
npm run tauri dev
```

**验证方法**: 桌面窗口弹出并显示模板欢迎页；终端无红色编译错误。

### 步骤二：打通第一条 IPC 通道

**目标**: 前端 invoke 一个 Rust 命令并拿到返回值

**操作指南**:

1. 在 `src-tauri/src/` 中定义命令函数（见下方代码示例）
2. 用 `generate_handler!` 把命令注册进 `invoke_handler`
3. 前端从 `@tauri-apps/api/core` 导入 `invoke` 调用

**验证方法**: 修改前端页面显示 Rust 返回的字符串；改动生效说明 HMR 正常。

### 步骤三：接入移动端目标

**目标**: 初始化 iOS / Android 原生工程并跑通开发模式

**操作指南**:

```bash
# 需要先装好 Xcode（macOS）或 Android Studio（全平台）
npm run tauri ios init
npm run tauri android init

# 移动端开发模式：ios 需 macOS + Xcode，android 可跨平台
npm run tauri ios dev
npm run tauri android dev
```

**验证方法**: 模拟器/真机中出现与桌面端一致的前端页面；`src-tauri/gen/` 下出现 `apple/`、`android/` 目录。

---

## 💻 代码示例

### 示例一：Builder 与命令注册（Rust 核心进程侧）

```rust
// src-tauri/src/main.rs
// release 构建时阻止 Windows 额外弹出控制台
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::Mutex;
use tauri::{AppHandle, Emitter, State};

#[derive(Default)]
pub struct Counter(pub Mutex<i64>);

// 最小命令：参数名即前端 invoke 传入的 JSON 字段名（驼峰映射）
#[tauri::command]
fn greet(name: &str) -> String {
    format!("你好，{name}！这条字符串来自 Rust 核心进程。")
}

// 带状态 + 事件下发的命令：
// - State<'_, T> 由 Builder::manage 注入，签名直接提取
// - Emitter trait 提供 emit，需显式 use（Tauri 2 从 Manager 拆分出来了）
#[tauri::command]
fn increment(app: AppHandle, counter: State<'_, Counter>) -> Result<i64, String> {
    let mut value = counter.0.lock().map_err(|e| e.to_string())?;
    *value += 1;
    app.emit("counter-changed", *value).map_err(|e| e.to_string())?;
    Ok(*value)
}

fn main() {
    tauri::Builder::default()
        .manage(Counter::default())
        .invoke_handler(tauri::generate_handler![greet, increment])
        .run(tauri::generate_context!())
        .expect("tauri 应用启动失败");
}
```

**关键点解析**:
- `Builder::manage<T: Send + Sync + 'static>` 注册共享状态，命令里用 `State<'_, T>` 免参数提取
- `generate_context!` 编译期读取 `tauri.conf.json`，所以改配置必须重新编译
- 返回 `Result` 时，`Err` 会以字符串形式 reject 到前端 Promise

### 示例二：前端 invoke 调用

```typescript
// src/ipc.ts —— 前端只 import 类型化封装，不散落裸 invoke
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';

export async function greet(name: string): Promise<string> {
  return invoke('greet', { name });
}

// 订阅 Rust 推送的计数变化事件
export function onCounterChanged(handler: (value: number) => void) {
  return listen<number>('counter-changed', (event) => handler(event.payload));
}
```

### 示例三：tauri.conf.json 骨架

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "dev-notes",
  "version": "0.1.0",
  "identifier": "com.devquest.notes",
  "build": {
    "beforeDevCommand": "npm run dev",
    "devUrl": "http://localhost:5173",
    "beforeBuildCommand": "npm run build",
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [{ "title": "Dev Notes", "width": 960, "height": 640 }],
    "security": { "csp": null }
  },
  "bundle": { "active": true, "targets": "all" }
}
```

**关键点解析**:
- `identifier` 必填且全局唯一（打包与移动端签名都依赖它）
- `devUrl` 指向前端 dev server（开发热更新），`frontendDist` 指向构建产物（生产嵌入）
- 配置完整字段见 [07 桌面打包](./07-desktop-packaging.md) 与[配置参考](https://v2.tauri.app/reference/config/)

---

## 🎨 最佳实践

### ✅ 推荐做法

- **敏感逻辑全部下沉 Rust**: 密钥、鉴权、文件路径拼接不进 WebView——前端只收到"结果"，攻击面收敛到 IPC 面
- **IPC 面最小化**: 每加一个 command 都问一句"前端真的需要吗"；能力授予用 capabilities 精确到窗口
- **大文件走 Rust 侧流式处理**: 不要把几 MB 的二进制序列化成 JSON 过 IPC，读写都留在 Rust

### ❌ 避免陷阱

- **以为 WebView 行为全平台一致**: WebKitGTK 与 WebView2 的 CSS/JS 引擎差异真实存在，跨端 UI 必须三平台实测
- **在命令函数里做长阻塞操作**: 阻塞会卡 UI 桥接，耗时任务改 async 命令或 `std::thread::spawn` + 事件回报
- **手工修改 `src-tauri/gen/`**: 移动端原生工程是 CLI 生成的构建产物，升级会被覆盖

---

## ❓ 常见问题

### Q1: 为什么我的应用在不同系统上渲染不一样？

**A**: 这是复用系统 WebView 的固有代价。解决方案按优先级：① 样式用渐进增强，避开各引擎行为差异大的特性；② 用自动化截图对比测试三平台；③ 确实需要像素级一致时，重新评估选型（对比表见核心概念二）。

### Q2: `app.emit` 编译报错找不到方法？

**A**: Tauri 2 把事件能力从 `Manager` trait 拆到了独立 trait——推送用 `tauri::Emitter`，订阅用 `tauri::Listener`。在文件头部 `use tauri::{Emitter, Listener};` 即可。这是从 Tauri 1 迁移代码最高频的编译错误。

### Q3: invoke 的参数名为什么对不上？

**A**: Rust 命令的 snake_case 参数在前端 invoke 时要用 **camelCase**（Tauri 默认做参数名转换）。要么前端用驼峰，要么给命令标注 `#[tauri::command(rename_all = "snake_case")]` 统一风格。

---

## 🧭 模式不变量

1. **渲染进程永远不可信**: 无论 Tauri 还是 Electron，凡是运行在 WebView 里的代码都在敌对面，任何敏感操作的"执行"必须发生在核心进程
2. **能力授予默认拒绝**: 跨进程暴露的每一个能力（command、插件权限）都应显式列白名单，而非默认放开再回收
3. **进程边界即信任边界**: IPC 序列化是唯一合法通道，绕过 IPC 共享内存/句柄的方案都要重新审视安全影响
4. **渲染引擎是外部依赖**: 复用系统 WebView 的框架，UI 兼容性策略必须按"浏览器矩阵"而非"固定引擎"规划

---

## 🔗 相关资源

### 📖 延伸阅读

- **字典**: [Tauri 2 Essentials](../reference/framework-essentials/09-tauri-2-essentials.md) - 命令/事件/配置的速查全集
- **字典**: [Tauri IPC Commands](../reference/framework-essentials/10-tauri-ipc-commands.md) - command 签名与参数映射细则
- **指南**: [Tauri 插件体系](./02-tauri-plugins.md) - 官方插件清单与 capabilities 权限写法
- **指南**: [前端集成 React+TS](./03-tauri-frontend-react.md) - 本篇骨架上的前端工程化展开

### 🛠️ 工具资源

- **官方文档**: [Tauri 2 文档](https://v2.tauri.app/) - 配置/插件/分发全量参考
- **API 参考**: [docs.rs/tauri/2.11.0](https://docs.rs/tauri/2.11.0/tauri/) - Builder/Emitter/Listener 签名
- **对标阅读**: [04-multiplatform-apps](../../04-multiplatform-apps/README.md) - 三端原生路线的对照实现

---

## 📝 总结

### 核心要点回顾

1. **进程模型**: Rust 核心进程 + 系统 WebView，前端代码永远处于低信任侧
2. **选型判断**: Tauri 用"引擎浮动"换体积与安全边界，Electron 用体积换一致性——按项目约束选
3. **通信面**: command（请求-响应）+ event（主动推送）+ capabilities（默认拒绝的门控），三者共同定义攻击面

### 学习成果检查

- [ ] 能不查资料画出双进程模型并标注各平台 WebView 来源
- [ ] 完成 create-tauri-app 工程创建并跑通第一条 invoke
- [ ] 知道 emit/listen 分别在哪个 trait 上
- [ ] 理解 capabilities"默认拒绝"与 Electron 安全模型的差异

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
