# 内置模块导航表

## 先区分语言、运行时与依赖

前置：[ESM](../../basics/03-modules-esm.md)。Array、Promise 来自 JavaScript；node:fs 来自 Node 运行时；Hono 是项目安装的包。AbortController 与 fetch 是 Node 提供的全局 Web API，不能据此拼出一个同名 node: 模块。

完整示例：保存为 `core-lab.mjs`，运行 `node core-lab.mjs`。通过 URL 指向脚本旁的文件，避免工作目录改变后读取了另一个文件。

```js
import { readFile } from 'node:fs/promises'
import { basename } from 'node:path'
import { fileURLToPath } from 'node:url'

const file = fileURLToPath(import.meta.url)
const text = await readFile(file, 'utf8')
console.log(basename(file))
console.log(text.includes("node:fs/promises"))
console.log(typeof AbortController)
```

预期为 core-lab.mjs、true、function。三个模块各负责读取、路径和 URL 转换；无需安装名为 fs 的 npm 包。练习把路径改成一个不存在文件并用 try/catch 输出错误 code，预期为 ENOENT，而不是把失败当成空文本。

<!-- core-p1-case: node-core-file-url -->
```js
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const currentFile = fileURLToPath(import.meta.url);
const source = await readFile(currentFile, 'utf8');
assert.match(basename(currentFile), /^case-\d+\.mjs$/);
assert.match(source, /node:fs\/promises/);
await assert.rejects(readFile(new URL('./missing.txt', import.meta.url), 'utf8'),
  error => error?.code === 'ENOENT');
console.log('core-file-url: module URL, source read, missing-file code');
```

该程序在临时目录中读取自身并验证不存在文件的错误码。它不覆盖权限、符号链接、Windows
路径格式或生产目录布局；这些条件须在目标环境单独验证。

> **文档简介**: Node.js 全部常用内置模块的分类导航，标注使用频率与一句话用途，快速定位该用哪个模块

> **目标读者**: 需要判断"这个功能是不是内置、该 import 什么"的开发者

> **前置知识**: [模块系统](../../basics/03-modules-esm.md)（`node:` 前缀导入）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐ |
| **标签** | `#内置模块` `#标准库` `#导航` |
| **更新日期** | `2026年9月` |

</details>

## 🔥 高频模块（几乎每个项目都会用到）

| 模块 | 用途 | 高频 API | 详解 |
|------|------|---------|------|
| `node:fs` | 文件系统 | `readFile` `createReadStream` `watch` | [核心模块速查](../language-concepts/03-node-core-api.md) |
| `node:path` | 路径处理 | `join` `resolve` `dirname` | 同上 |
| `node:http` | HTTP 服务/客户端 | `createServer` `request` | [第一个服务器](../../basics/02-first-server.md) |
| `node:url` | URL 处理 | `fileURLToPath` `pathToFileURL` | 同上 |
| `node:process`（全局） | 进程信息与控制 | `env` `exit` `on` | 同上 |
| `node:os` | 操作系统信息 | `availableParallelism` `totalmem` | 同上 |
| `node:events` | 事件基座 | `EventEmitter` `once` | 同上 |
| `node:stream` | 流处理 | `pipeline` `Transform` | [Stream API 速查](../language-concepts/04-streams-api.md) |
| `node:util` | 工具函数 | `inspect` `parseArgs` `styleText` | [util 详解](./06-util.md) |
| `node:crypto` | 加密与哈希 | `randomUUID` `createHash` `randomBytes` | [crypto 详解](./03-crypto.md) |
| `node:child_process` | 子进程 | `execFile` `spawn` `fork` | [子进程详解](./04-child-process.md) |
| `node:zlib` | 压缩 | `createGzip` `brotliCompress` | [压缩详解](./09-zlib.md) |

## ⚙️ 服务端常用（按需引入）

| 模块 | 用途 | 备注 |
|------|------|------|
| `node:https` | HTTPS 服务/客户端 | 现代出站请求直接用全局 `fetch` |
| `node:net` | TCP socket | 造协议、代理、端口探测 |
| `node:dgram` | UDP | DNS、监控打点类场景 |
| `node:dns` | 域名解析 | `promises.lookup` `resolve` |
| `node:tls` | TLS/SSL | 证书加载、安全 socket |
| `node:http2` | HTTP/2 | `http2.createServer` |
| `node:worker_threads` | 多线程 | CPU 密集任务，见 [Stream 与 Worker](../../basics/07-streams-workers.md) |
| `node:cluster` | 多进程服务 | 多核 I/O 扩展，云原生下渐被容器替代 |
| `node:v8` | V8 引擎信息 | `getHeapStatistics` 内存分析 |
| `node:perf_hooks` | 性能测量 | `performance.now()` `PerformanceObserver` |

## 📦 异步与调度

| 模块 | 用途 | 备注 |
|------|------|------|
| `node:async_hooks` | 异步上下文追踪 | `AsyncLocalStorage` 是 tracing 基石 |
| `node:timers`（全局） | 定时器 | `setTimeout` `setImmediate` |
| `node:timers/promises` | Promise 定时 | 可取消的 `setTimeout` |
| 全局 `AbortController` / `AbortSignal` | 取消协议 | 直接使用；不存在可导入的 `node:abort_controller` 模块 |

## 🗄️ 数据与序列化

| 模块 | 用途 | 备注 |
|------|------|------|
| `node:buffer`（全局） | 二进制数据 | `Buffer.from` `alloc`；全局可用无需导入 |
| `node:querystring` | URL 查询串解析 | 优先用 `URL.searchParams` |
| `node:string_decoder` | Buffer → 字符串 | 处理跨 chunk 的多字节字符 |
| `node:assert` | 断言 | 测试与内部不变量校验 |
| `node:punycode` | 域名编码 | 已弃用，仅在兼容库中出现 |

## 🧪 测试与工程化（Node 24 重点）

| 模块 | 用途 | 备注 |
|------|------|------|
| `node:test` | 内置测试框架 | `test` `describe` `it` `mock`，轻量替代 Jest |
| `node:assert/strict` | 严格断言 | 与 `node:test` 配套 |
| `node:module` | 模块系统工具 | `createRequire` 桥接 CJS |
| `node:console`（全局） | 控制台输出 | `Console` 类可重定向输出目标 |

## 📜 系统与运行时信息

| 模块 | 用途 | 备注 |
|------|------|------|
| `node:readline` | 交互式输入/逐行读取 | CLI 工具；逐行读文件用流+分隔符 |
| `node:tty` | 终端检测 | `process.stdout.isTTY` |
| `node:vm` | 沙箱脚本执行 | 非安全沙箱，勿用于运行不可信代码 |
| `node:inspector` | 调试协议 | IDE/Chrome DevTools 调试的底层 |
| `node:trace_events` | 追踪事件 | `--trace-events-enabled` 性能分析 |
| `node:repl` | 交互式解释器 | `node` 直接回车即是；可内嵌自定义 REPL |
| `node:sea` | 单可执行应用 | Node 20+ 把脚本打包成独立二进制 |

## 🌐 Web 标准全局对象（无需导入）

Node 24 已内置大量 Web 标准 API，直接使用：

```ts
fetch(url, { signal });           // 出站 HTTP（undici 实现）
new URL(input); new URLPattern(p);
new Request("https://example.com"); new Response("ok"); // Request 必须提供输入
new Headers();
FormData / Blob / File;
structuredClone(value);
crypto.randomUUID();              // WebCrypto
atob() / btoa();
TextEncoder / TextDecoder;
```

## 🧭 选用决策速判

- 读写文件 → `node:fs/promises`（小文件）或 `node:stream`（大文件）
- 出站 HTTP → 新项目先评估全局 `fetch`：它已覆盖请求、响应和 `AbortSignal`。若项目需要统一拦截、重试策略、旧运行时兼容或已有客户端约定，再比较具体库；不要仅因“别人用了 axios”重复引入。
- 并发利用多核 → 先确认瓶颈是 CPU、I/O 还是外部依赖，并先看部署平台能否多实例扩展。CPU 密集工作可评估 `worker_threads`；`cluster` 是多进程 Node 机制，是否使用取决于进程管理、端口绑定、会话和可观测性方案，不能把它当作 I/O 的默认优化。
- 定时/重试 → `node:timers/promises` + `AbortSignal.timeout`
- 唯一 ID → `crypto.randomUUID()`，无需 nanoid/uuid 依赖

---

## 🔗 相关文档

- 📄 **[Node 核心模块 API 速查](../language-concepts/03-node-core-api.md)** — 高频模块的 API 细节
- 📄 **[生态库精选](./02-ecosystem-libs.md)** — 内置模块不够用时的三方选择
- 📄 **[Node 一行式速查](../quick-references/01-node-cheatsheet.md)** — CLI 命令与调试入口


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)

本轮语义核对来源：[Node 全局 AbortController](https://nodejs.org/api/globals.html#class-abortcontroller)（2026-09-18；不等同于本地完整工程运行验证）。
