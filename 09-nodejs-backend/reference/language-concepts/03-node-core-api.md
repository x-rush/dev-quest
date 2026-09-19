# Node 核心模块 API 速查

> **文档简介**: fs、path、events、process、http、worker_threads、os、url 等后端最常用内置模块的条目式速查

> **目标读者**: 需要确认核心模块 API 用法与陷阱的 Node 开发者

> **前置知识**: [模块系统](../../basics/03-modules-esm.md)（ESM 导入方式）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐ |
| **标签** | `#fs` `#path` `#events` `#process` `#http` `#worker_threads` `#核心模块` |
| **更新日期** | `2026年9月` |

</details>

## 1. node:fs / node:fs/promises

### 定义
文件系统操作。`node:fs/promises` 提供常用文件操作的 Promise API；文件流等接口仍在 node:fs 中，是默认选择。

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
// EventEmitter.on 没有第三个 signal 选项；使用可取消的异步迭代工具
import { on } from "node:events";
try {
  for await (const args of on(bus, "tick", { signal: controller.signal })) {
    handler(...args);
  }
} catch (error) {
  if (!controller.signal.aborted) throw error;
}
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

process.env.PORT;                    // 环境变量（存在时为 string，未设置为 undefined）
process.exit(1);                     // 立即退出（有未刷写输出可能丢失）
process.exitCode = 1;                // 更温和：让进程自然结束后以此码退出
process.pid;
process.cwd();                       // 启动目录（≠ 模块所在目录）
process.version;                     // v24.x.x
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
URL 解析与构造；现代代码直接用全局 `URL` 类，node:url 还提供 fileURLToPath、pathToFileURL、域名转换等工具，不只一个桥接函数。

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

## 7. node:http

### 定义
Node 原生 HTTP 服务与客户端。业务项目通常经 Hono 等框架封装（`@hono/node-server` 底层即它），但健康检查、代理、内网探针等场景仍会直接使用。

### 语法与示例

```ts
import http from "node:http";

const server = http.createServer((req, res) => {
  console.log(req.method, req.url);            // "GET" "/ping?x=1"
  res.writeHead(200, { "Content-Type": "application/json" }); // 状态码 + 响应头
  res.end(JSON.stringify({ ok: true }));       // 结束响应（必须调用）
});

server.listen(3000, "127.0.0.1");  // 监听端口；回调可省
server.close();                    // 停止接新连接，存量请求处理完再退出

// 客户端：现代代码直接用全局 fetch
const res = await fetch("http://127.0.0.1:3000/ping");
```

### 陷阱
- `req`/`res` 是 Node 自己的 IncomingMessage/ServerResponse（**不是** Web 标准 Request/Response）——迁移 Hono 时心智模型要换：Hono 处理器 `return c.json()`，这里必须显式 `res.end()`
- 忘调 `res.end()` 客户端会悬挂到超时；`setHeader` 可先设置默认头，`writeHead` 的同名头会覆盖它。实际项目选定一种组织方式，避免在分支中产生难追踪的覆盖
- `req.url` 只含路径与查询串（`/ping?x=1`），不含协议与主机

<!-- node-python-seventh-case: node-core-api-contracts -->
```js
import assert from 'node:assert/strict';
import { EventEmitter, once } from 'node:events';
import { basename, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const bus = new EventEmitter();
const received = once(bus, 'done');
queueMicrotask(() => bus.emit('done', 'task-7'));
assert.deepEqual(await received, ['task-7']);

const file = fileURLToPath(pathToFileURL(join('/tmp', 'task.txt')));
assert.equal(basename(file), 'task.txt');
console.log('core-api: EventEmitter once; path join; file URL round-trip');
```

该程序不启动端口或读取宿主文件，只运行 `node:events`、`node:path` 与 `node:url` 的本页契约。URL 往返的具体路径分隔符由当前运行平台决定，所以只断言文件名；HTTP、权限和 Windows 路径兼容性不在本检查范围内。

## 8. node:worker_threads

### 定义
真正的多线程：每个 Worker 有独立的事件循环与 V8 实例，通过消息传递（结构化克隆）通信。CPU 密集任务的根治方案，I/O 密集用事件循环即可（对比见 [Stream 与 Worker 教程](../../basics/07-streams-workers.md)）。

### 语法与示例

```ts
import { Worker, parentPort, workerData } from "node:worker_threads";

// worker.js —— 工作线程侧
if (parentPort) {
  const result = heavyCompute(workerData.n);   // workerData 是启动时传入的数据
  parentPort.postMessage(result);              // 结构化克隆回传
}

// 主线程侧
const worker = new Worker(new URL("./worker.js", import.meta.url), {
  workerData: { n: 21 },
});
worker.on("message", (r) => console.log(r));   // 收结果
worker.on("error", (err) => console.error(err));
worker.terminate();                            // 强制终止（不等待）
```

### 陷阱
- 主线程与 Worker **不共享堆内存**——传大对象走结构化克隆（深拷贝）；真要共享用 `SharedArrayBuffer` + `Atomics`
- 线程数别超 `os.availableParallelism()`，线程切换与内存开销反而拖慢
- Worker 内抛出的异常若不监听 `error` 事件，会以未捕获异常冒泡导致**主进程崩溃退出**（exit 1）——必须注册 `worker.on("error", ...)`

## 9. 其他常用模块一览

| 模块 | 用途 | 高频 API |
|------|------|---------|
| `node:crypto` | 哈希/随机/加密 | `randomUUID()`、`createHash("sha256")`、`timingSafeEqual` |
| `node:util` | 工具 | `util.inspect`（调试打印）、`util.promisify` |
| `node:assert` | 断言（测试/内部校验） | `strict.equal`、`rejects` |
| `node:child_process` | 子进程 | `execFile`（Promise 版）、`spawn` |
| `node:zlib` | 压缩 | `createGzip()`、`gzipSync` |
| `node:timers/promises` | Promise 定时 | `setTimeout`、`setInterval` |

---

<!-- full-library-explanation -->
## 为每个资源指定创建者与清理者

前置是 Promise、ESM 与异常。文件句柄、事件监听器、HTTP 响应体和 Worker 都有生命周期：谁创建，谁负责在成功、失败和取消路径释放。readFile 适合有大小上限的小文件，流式读取用于大数据；路径拼接只能规范字符串，不能证明路径位于允许目录或不经过符号链接。删除和写入前应明确目标来自可信配置还是用户输入。

EventEmitter.emit 同步调用当前监听器，监听器不会因为返回 Promise 就自动被等待。下面是独立实验，保存为 events.mjs 后运行：

```js
import { EventEmitter } from 'node:events';
const bus = new EventEmitter();
bus.on('work', async () => {
  console.log('start');
  await Promise.resolve();
  console.log('after await');
});
bus.emit('work');
console.log('emit returned');
```

预期顺序是 start、emit returned、after await。练习：让监听器返回拒绝的 Promise，解释为什么同步包住 emit 的 try/catch 不能捕获稍后的拒绝；在监听器内处理错误，或按契约配置 captureRejections 与 error 监听。清理监听时 off 必须使用原来的函数引用，重新写一个同样的箭头函数不是同一个监听器。

## 🔗 相关文档

- 📄 **[Stream API 速查](./04-streams-api.md)** — fs 流式读写的深入条目
- 📄 **[内置模块导航表](../library-guides/01-core-modules.md)** — 全部内置模块总览
- 📄 **[Stream 与 Worker 教程](../../basics/07-streams-workers.md)** — os 核数与多线程的实战


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
