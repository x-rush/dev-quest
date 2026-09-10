# Node 核心模块 API 速查

> **文档简介**: fs、path、events、process、os、url 等后端最常用内置模块的条目式速查

> **目标读者**: 需要确认核心模块 API 用法与陷阱的 Node 开发者

> **前置知识**: [模块系统](../../basics/03-modules-esm.md)（ESM 导入方式）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐ |
| **标签** | `#fs` `#path` `#events` `#process` `#核心模块` |
| **更新日期** | `2026年9月` |

## 1. node:fs / node:fs/promises

### 定义
文件系统操作。`node:fs/promises` 提供全部异步 API 的 Promise 版本，是默认选择。

### 语法与示例

```ts
import { readFile, writeFile, mkdir, rm, stat, readdir } from "node:fs/promises";

await readFile("config.json", "utf-8");            // 字符串读取
await writeFile("out.json", JSON.stringify(data), { flag: "w" });
await mkdir("dist/assets", { recursive: true });    // 递归建目录
await rm("tmp", { recursive: true, force: true });  // 递归删除，不存在不报错
const info = await stat("data.db");                 // size/mtime/isFile()
const files = await readdir("src", { withFileTypes: true }); // 含类型（目录/文件）
```

### 陷阱
- 三个版本别混用：`node:fs`（回调）、`node:fs/promises`（Promise）、`*Sync`（同步阻塞，仅启动期可用）；大文件用流（见 [Stream API](./04-streams-api.md)）

## 2. node:path

### 定义
跨平台路径拼接与解析，永远用它而非字符串拼接。

### 语法与示例

```ts
import path from "node:path";

path.join("/app", "logs", "2026", "app.log");  // /app/logs/2026/app.log（自动补分隔符）
path.resolve("logs", "app.log");                // 基于 cwd 的绝对路径
path.resolve(import.meta.dirname, "data");      // 相对当前模块文件的路径
path.basename("/a/b/c.txt", ".txt");            // c
path.posix.join("a", "b");                      // 强制 POSIX 风格（生成 URL 路径用）
```

### 陷阱
- `path.join` 不解析 URL，URL 路径要用 `path.posix` 或 `new URL()`
- Windows 分隔符是 `\`，写跨平台代码绝不手拼 `/`

## 3. node:events

### 定义
EventEmitter 是 Node 事件模型基座：fs/net/http 等模块的流与服务器都继承它。

### 语法与示例

```ts
import { EventEmitter } from "node:events";

const bus = new EventEmitter();
bus.on("task:done", (id) => console.log(id));
bus.once("init", setup);                        // 触发一次后自动移除
bus.off("task:done", handler);                  // 解绑（返回自身可链式）

// Promise 化等待单次事件
import { once } from "node:events";
const [payload] = await once(bus, "task:done");

// 带取消信号的监听（自动解绑）
bus.on("tick", handler, { signal: controller.signal });
```

### 陷阱
- 同一事件默认超过 10 个监听器会警告（`setMaxListeners` 调整）
- `error` 事件没有监听器会直接抛出崩溃进程

## 4. node:process

### 定义
当前进程的信息与控制：环境变量、退出、信号、资源用量。

### 语法与示例

```ts
import process from "node:process";

process.env.PORT;                    // 环境变量（值全是 string）
process.exit(1);                     // 立即退出（有未刷写输出可能丢失）
process.exitCode = 1;                // 更温和：让进程自然结束后以此码退出
process.pid;
process.cwd();                       // 启动目录（≠ 模块所在目录）
process.version;                     // v22.x.x
process.memoryUsage();               // rss / heapUsed / external
process.hrtime.bigint();             // 高精度计时
process.on("SIGINT", handler);       // Ctrl+C / 信号处理
process.on("unhandledRejection", h); // 兜底（见错误处理教程）
```

### 陷阱
- `process.env` 所有值都是字符串：`if (process.env.DEBUG)` 对 `"false"` 也为真，需显式比较
- `process.exit()` 会截断 stdout 异步刷写，日志可能丢——优先 `exitCode`；容器中还要处理 `SIGTERM`

## 5. node:os

### 定义
操作系统与硬件信息，用于容量探测与运行环境诊断。

### 语法与示例

```ts
import os from "node:os";

os.availableParallelism();   // 可用核数（worker/cluster 数量依据）
os.totalmem();               // 物理内存总量（字节）
os.freemem();
os.platform();               // linux / darwin / win32
os.tmpdir();                 // 系统临时目录（容器内注意挂载）
os.EOL;                      // 换行符（win 是 \r\n）
```

### 陷阱
- 容器中 `os.totalmem()/freemem()` 反映宿主机而非 cgroup 限额，读取配额用 `/sys/fs/cgroup`

## 6. node:url 与全局 URL

### 定义
URL 解析与构造；现代代码直接用全局 `URL` 类，`node:url` 仅剩 `fileURLToPath` 等桥接工具。

### 语法与示例

```ts
import { fileURLToPath } from "node:url";

const url = new URL("https://api.example.com/v1/tasks?status=todo&page=2");
url.pathname;                       // /v1/tasks
url.searchParams.get("status");     // todo
url.searchParams.set("page", "3");
url.searchParams.append("tag", "a");
url.toString();                     // 修改后序列化

// file 协议与磁盘路径互转
const abs = fileURLToPath(import.meta.url);           // file:// → 磁盘路径
new URL("./worker.js", import.meta.url);              // 模块相对定位（Worker 常用）
```

### 陷阱
- `searchParams` 的值会自动 URL 编码，取回是解码后的；不要二次 decodeURIComponent
- 用字符串拼接 URL 极易漏斜杠/漏编码，一律用 `URL` 构造

## 7. 其他常用模块一览

| 模块 | 用途 | 高频 API |
|------|------|---------|
| `node:crypto` | 哈希/随机/加密 | `randomUUID()`、`createHash("sha256")`、`timingSafeEqual` |
| `node:util` | 工具 | `util.inspect`（调试打印）、`util.promisify` |
| `node:assert` | 断言（测试/内部校验） | `strict.equal`、`rejects` |
| `node:child_process` | 子进程 | `execFile`（Promise 版）、`spawn` |
| `node:zlib` | 压缩 | `createGzip()`、`gzipSync` |
| `node:timers/promises` | Promise 定时 | `setTimeout`、`setInterval` |

---

## 🔗 相关文档

- 📄 **[Stream API 速查](./04-streams-api.md)** — fs 流式读写的深入条目
- 📄 **[内置模块导航表](../library-guides/01-core-modules.md)** — 全部内置模块总览
- 📄 **[Stream 与 Worker 教程](../../basics/07-streams-workers.md)** — os 核数与多线程的实战
