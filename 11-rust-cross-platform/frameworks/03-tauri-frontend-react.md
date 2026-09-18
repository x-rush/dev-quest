# Tauri 2 前端集成：React + TypeScript 与 invoke 类型封装

## 先看框架承担哪部分职责

**Tauri 前端**：invoke 返回 Promise，Rust Result 的错误需要转成前端能够展示的契约。TypeScript 泛型标注并不验证 Rust 实际返回结构。

**最小练习与预期结果**：调用一个会失败的命令，在 UI 显示恢复操作；不要把拒绝的 Promise 当空字符串继续渲染。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 把 React + TypeScript 前端工程化地接进 Tauri 2——双根目录结构、全应用唯一的 invoke 类型封装层、事件订阅的 React Hook 化，以及 devUrl 热更新与 frontendDist 生产嵌入两套刷新语义。
>
> **目标读者**: 有 React/TS 经验、已在跑 Tauri 工程的前端向开发者
>
> **前置知识**: [Tauri 2 架构](./01-tauri-2-architecture.md)（invoke/event 模型）、React Hooks 基础
>
> **预计时长**: 3-4 小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 操作指南（frameworks/） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#tauri` `#react` `#typescript` `#ipc` |
| **更新日期** | `2026年9月` |

</details>

> 版本基线见模块 [README](../README.md)（Tauri 2.11，2026-09-16 核实）。React 基线参照 [02-nextjs-frontend](../../02-nextjs-frontend/README.md) 模块（React 19）。

## 🎯 学习目标

完成本篇后，你将能够：

- ✅ **分清两个工具**: create-tauri-app（脚手架）与 @tauri-apps/api（运行时）各自的职责
- ✅ **封装 invoke 层**: 用常量表 + 泛型包装 + 错误归一化收口全部跨进程调用
- ✅ **Hook 化事件**: 编写随组件卸载自动退订的 useTauriEvent
- ✅ **吃透两种刷新**: 前端 HMR 秒级生效 vs Rust 改动触发重编译重启

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

### 概念一：双根工程结构

**定义**: Tauri 项目天然有两个根——前端根（`src/` + `package.json`）与 Rust 根（`src-tauri/` + `Cargo.toml`）。两者唯一的耦合点是 `tauri.conf.json` 的 `build` 区块。

```text
dev-notes/
├── src/                      # React + TypeScript（Vite 托管）
│   ├── api/commands.ts       # invoke 类型封装（全应用唯一出口）
│   ├── hooks/useTauriEvent.ts
│   ├── App.tsx
│   └── main.tsx
├── src-tauri/                # Rust 核心进程
│   ├── src/
│   │   ├── main.rs           # 入口（thin wrapper）
│   │   ├── lib.rs            # Builder 装配（移动端复用）
│   │   └── commands.rs       # 命令实现
│   ├── capabilities/default.json
│   └── tauri.conf.json
└── package.json
```

**关键约定**: Rust 命令集中在 `commands.rs`，前端调用集中在 `api/commands.ts`——两边各有一个"命令清单"，改命令时两处同步。

### 概念二：createTauriApp vs @tauri-apps/api——常被混淆的两个东西

**定义**:

| | create-tauri-app | @tauri-apps/api |
|---|---|---|
| 形态 | 脚手架 CLI（`npm create tauri-app`） | 前端运行时 npm 包 |
| 职责 | 生成含模板（react-ts 等）的完整工程 | 提供 `invoke`/`listen`/窗口管理等 JS API |
| 使用阶段 | 项目创建一次 | 开发全程 |

**补充**: 还有 `app.withGlobalTauri: true` 配置项，会把 API 注入为页面全局 `window.__TAURI__`——适合无构建器的静态页面场景；React 项目一律走 npm 包（类型完备）。官方另有社区工具可从 Rust 类型生成 TS 类型（如 specta 系），本篇先用手工 DTO。

### 概念三：invoke 的 Promise 契约

**定义**: `invoke` 把 Rust 命令映射为 Promise：

- Rust 返回值（serde 序列化）→ Promise **resolve**
- Rust 返回 `Result::Err(e)` → Promise **reject**，payload 默认为错误值的字符串形式
- Rust 参数用 snake_case ↔ 前端 args 用 camelCase（框架自动转换）

**推论**: 前端拿到的类型安全完全取决于 DTO 手工对齐——这就是要把 invoke 收口进类型封装层的原因。

### 概念四：开发模式热更新的两套语义

**定义**: `tauri dev` 启动时按 `build.beforeDevCommand` 拉起前端 dev server，再在窗口里加载 `build.devUrl` 指向的地址：

1. **前端改动**: 由 Vite HMR 即时推送，WebView 内热替换，**不触碰 Rust 进程**
2. **Rust 改动**: tauri CLI 检测到 `src-tauri/` 变化，重编译并**重启整个应用进程**

生产构建时窗口加载的是 `frontendDist`（`../dist`）里的静态产物，与 dev server 无关。

---

## 🛠️ 实践指南

### 步骤一：生成 React + TS 工程

**目标**: 得到本篇示例的工程骨架

**操作指南**:

```bash
npm create tauri-app@latest dev-notes -- --template react-ts
cd dev-notes && npm install && npm run tauri dev
```

**验证方法**: 窗口弹出；`npm run dev` 单独跑前端也能在浏览器预览（Tauri API 在浏览器中调用会失败，属正常）。

### 步骤二：建立 invoke 类型封装层

**目标**: 任何组件不得直接 `import { invoke }`，只允许经过 `api/commands.ts`

**操作指南**: 落地"代码示例一"：命令名常量表 → DTO 接口 → 泛型包装 + 错误归一化 → 按业务组织的 `api` 对象。

**验证方法**: 全局搜索 `from '@tauri-apps/api/core'`，只命中 `api/commands.ts` 一处。

### 步骤三：封装事件订阅 Hook

**目标**: Rust 推送的事件驱动 React 状态，且组件卸载自动退订

**操作指南**: 落地"代码示例二"的 `useTauriEvent`；在组件中以 `useTauriEvent<Note[]>('notes-changed', setNotes)` 使用。

**验证方法**: 组件反复挂载/卸载后，Rust 侧事件不再触发已卸载组件的 setState（React 无警告）。

### 步骤四：验证两套刷新语义

**目标**: 亲身区分 HMR 与进程重启

**操作指南**:

1. 改 `src/App.tsx` 的文案 → 窗口内容即时更新（无重编译日志）
2. 改 `src-tauri/src/commands.rs` 任意注释 → 终端出现 recompile → 应用自动重启

**验证方法**: 两种改动分别观察到"内容闪替"与"窗口重建"两种现象。

---

## 💻 代码示例

### 示例一：api/commands.ts——invoke 类型封装层

```typescript
// src/api/commands.ts —— 全应用唯一的 invoke 出口
import { invoke } from '@tauri-apps/api/core';

// 1) 命令名收敛为常量，防魔法字符串散落
export const CMD = {
  greet: 'greet',
  listNotes: 'list_notes',
  saveNote: 'save_note',
} as const;

// 2) DTO：与 Rust 命令返回的 JSON 结构手工对齐
export interface Note {
  id: number;
  title: string;
  body: string;
}

// 3) 错误归一化：Rust Result::Err 默认以字符串 reject
export class CommandError extends Error {
  constructor(
    public readonly command: string,
    message: string,
  ) {
    super(`[${command}] ${message}`);
    this.name = 'CommandError';
  }
}

async function call<T>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  try {
    return await invoke<T>(cmd, args);
  } catch (raw) {
    const message = typeof raw === 'string' ? raw : JSON.stringify(raw);
    throw new CommandError(cmd, message);
  }
}

// 4) 按业务组织：组件只 import 这个对象
export const api = {
  greet: (name: string) => call<string>(CMD.greet, { name }),
  listNotes: () => call<Note[]>(CMD.listNotes),
  saveNote: (note: Note) => call<void>(CMD.saveNote, { note }),
};
```

**关键点解析**:
- `CMD` 的值必须与 `generate_handler!` 注册的命令名一字不差
- 参数对象用 camelCase（与 Rust snake_case 参数自动互转）
- 错误归一化让 UI 层拿到统一的 `CommandError`，不必感知 IPC 细节

### 示例二：useTauriEvent——事件订阅 Hook

```typescript
// src/hooks/useTauriEvent.ts
import { useEffect, useRef } from 'react';
import { listen, type Event, type UnlistenFn } from '@tauri-apps/api/event';

export function useTauriEvent<T>(event: string, handler: (payload: T) => void): void {
  // handler 存 ref：订阅只建立一次，回调却始终是最新闭包
  const saved = useRef(handler);
  useEffect(() => {
    saved.current = handler;
  }, [handler]);

  useEffect(() => {
    let unlisten: UnlistenFn | undefined;
    let cancelled = false;

    listen<T>(event, (e: Event<T>) => saved.current(e.payload)).then((fn) => {
      if (cancelled) {
        fn(); // 竞态保护：组件已卸载才拿到 unlisten，立即退订
      } else {
        unlisten = fn;
      }
    });

    return () => {
      cancelled = true;
      unlisten?.();
    };
  }, [event]);
}
```

### 示例三：App.tsx——invoke 拉数据 + 事件推更新

```tsx
// src/App.tsx
import { useEffect, useState } from 'react';
import { api, CommandError, type Note } from './api/commands';
import { useTauriEvent } from './hooks/useTauriEvent';

export default function App() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [error, setError] = useState<string | null>(null);

  // 初始拉取：走封装层，错误已归一化
  useEffect(() => {
    api.listNotes().then(setNotes).catch((e: CommandError) => setError(e.message));
  }, []);

  // Rust 侧 app.emit("notes-changed", notes) 时自动同步
  useTauriEvent<Note[]>('notes-changed', setNotes);

  if (error) {
    return <p role="alert">{error}</p>;
  }
  return (
    <ul>
      {notes.map((n) => (
        <li key={n.id}>{n.title}</li>
      ))}
    </ul>
  );
}
```

### 示例四：Rust 侧对应命令（供对照）

```rust
// src-tauri/src/commands.rs
use crate::NoteRow;

// 命令名 snake_case，前端 CMD.listNotes = 'list_notes'
#[tauri::command]
pub fn list_notes(state: tauri::State<'_, crate::NoteStore>) -> Result<Vec<NoteRow>, String> {
    state.list().map_err(|e| e.to_string())
}
```

---

## 🎨 最佳实践

将命令名、参数和错误转换集中在可查阅的前端模块，组件就能表达“保存笔记”而不是反复拼装 IPC。invoke 的泛型帮助静态使用，不会自动验证 Rust 实际返回形状；契约变化应联动两端测试。

订阅事件需要清理，尤其 listen 异步完成可能晚于组件卸载；应处理这种时序而非只在同步返回里假设句柄已存在。批量读取与事件更新减少重复跨界，验收快速进入离开页面后不会积累重复响应。

---

## ❓ 常见问题

### Q1: invoke 返回的类型和 Rust 对不上，怎么系统性防？

**A**: 手工 DTO 的漂移不可避免，防线有三道：① code review 时对照 `commands.rs` 签名；② 用社区工具（specta 系）从 Rust 类型生成 TS 类型，让漂移变成编译错误；③ 集成测试里对关键命令做真实 invoke 断言（参考 testing/ 篇）。

### Q2: 前端页面在窗口里白屏，但浏览器里正常？

**A**: 按顺序查：① `tauri dev` 终端是否报 dev server 启动失败（`beforeDevCommand` 命令错误）；② `devUrl` 端口与 Vite 实际端口是否一致（改过端口必须同步）；③ 是否误跑 `tauri build` 产物而 `frontendDist` 路径没有产物。

### Q3: 为什么改了 Rust 代码整个应用都重启，体验比前端 HMR 差？

**A**: 语义本就不同——Rust 是进程本体，改它等于换二进制，无法热替换。缓解手段：把尽量多的迭代放前端层；Rust 侧用日志快速确认改动生效；命令拆细，单次重编译影响面小。

---

## 🧭 模式不变量

1. **前端类型是命令签名的投影**: 类型安全的源头在 Rust 侧，前端 DTO 只是投影——投影与源头的同步机制（手工/生成）必须显式选择
2. **跨进程调用必须收口**: 散落的裸 invoke 让"应用到底暴露了哪些 IPC 面"无法审计；封装层是审计单位
3. **订阅的生命周期归宿主管辖**: 事件 listen 返回的退订函数必须由 React 生命周期管理，任何框架集成都是这一个模式
4. **热更新边界即构建边界**: 前端资源可热替换，编译型代码只能换进程——混合栈的 DX 策略要按此边界分别设计

---

## 🔗 相关资源

### 📖 延伸阅读

- **指南**: [Tauri 2 架构](./01-tauri-2-architecture.md) - invoke/event 的进程模型背景
- **字典**: [Serde 指南](../reference/library-guides/13-serde-guide.md) - JSON 序列化的字段命名与默认值规则
- **项目**: [02 Tauri 桌面笔记](../projects/02-tauri-notes-app.md) - 本篇封装层的完整实战载体

### 🛠️ 工具资源

- **API 文档**: [@tauri-apps/api](https://v2.tauri.app/reference/javascript/core/) - core/event/window 各模块
- **前端参照**: [02-nextjs-frontend](../../02-nextjs-frontend/README.md) - React 19 语法与模式的全量参照
- **调试**: WebView 内右键 Inspect（dev 构建默认开放）查 console/network

---

## 📝 总结

### 核心要点回顾

1. **两个工具一条边界**: create-tauri-app 只管生成工程，@tauri-apps/api 是运行时依赖
2. **封装层三件套**: 命令常量 + DTO 类型 + 错误归一化，构成可审计的 IPC 出口
3. **两套刷新语义**: 前端 HMR（资源层）与 Rust 重编译重启（进程层）不可混为一谈

### 学习成果检查

- [ ] 工程里 `import { invoke }` 只出现在一处
- [ ] useTauriEvent 在组件卸载后正确退订
- [ ] 能演示 HMR 与 Rust 重启两种刷新的差异
- [ ] 解释 Rust `Err` 如何变成前端 reject 的 payload

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
