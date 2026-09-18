# node:child_process 子进程速查

> **文档简介**: `node:child_process` 四个创建子进程 API 的字典式速查——spawn/exec/execFile/fork 对比、shell 语义与注入风险、maxBuffer 上限与流式处理，附与 node:cluster 的分工说明

> **目标读者**: 需要调用外部命令（ffmpeg、pandoc、构建工具）或拆分重任务的开发者

> **前置知识**: [Stream API 速查](../language-concepts/04-streams-api.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#child_process` `#spawn` `#exec` `#shell 注入` `#fork` |
| **更新日期** | `2026年9月` |

</details>

## 1. 四 API 对比总表

### 定义
`node:child_process` 提供"创建子进程"的四个入口，差别在三个维度：**走不走 shell**、**流式还是缓冲**、**返回什么**。

| API | shell 语义 | 输出方式 | 默认上限 | 典型场景 |
|-----|-----------|---------|---------|---------|
| `spawn` | ❌ 不走（参数数组） | **流**（stdio 流式读取） | 无 | 大输出、长驻、边跑边处理 |
| `spawn(..., { shell: true })` | ✅ 走 | 流 | 无 | 需要管道/通配符时 |
| `exec` | ✅ 走平台 shell（Unix 常为 /bin/sh，Windows 常为 ComSpec） | 回调（整体缓冲） | **1 MiB**（maxBuffer） | 快捷跑一行 shell |
| `execFile` | ❌ 不走（参数数组） | 回调（整体缓冲） | **1 MiB**（maxBuffer） | 调已知可执行文件，最安全 |
| `fork` | ❌ 不走 | 流 + IPC 通道 | 无 | 跑另一个 Node 模块，可双向通信 |

### 实测对照（Node 24）

```ts
import { exec, execFile, spawn, fork } from "node:child_process";
import { promisify } from "node:util";

const pExec = promisify(exec);
const pExecFile = promisify(execFile);
// exec 走 shell：管道生效
(await pExec("echo a | wc -c")).stdout.trim();        // "2"

// execFile 不走 shell：管道符只是普通字符
(await pExecFile("echo", ["a | wc -c"])).stdout.trim();  // "a | wc -c"（字面输出）

// spawn 流式：适合大输出
import { once } from "node:events";
const p = spawn("ffmpeg", ["-i", "in.mp4", "out.webm"], { stdio: ["ignore", "pipe", "inherit"] });
const closed = once(p, "close"); // 先登记等待，并立即处理拒绝避免暂时未处理
const result = closed.then(([code, signal]) => ({ code, signal }), error => ({ error }));
for await (const chunk of p.stdout!) { /* 边跑边收 */ }
const outcome = await result; // 检查 error、code、signal
```

## 2. maxBuffer 上限

### 定义
`exec`/`execFile` 把子进程 stdout/stderr 全量缓冲进内存，超过程度默认 **1 MiB** 即抛错终止——这是它们与流式 `spawn` 的根本分野。

```ts
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const pExecFile = promisify(execFile);

async function demonstrateMaxBuffer() {
// 实测：2MB 输出触发错误
try {
  await pExecFile("node", ["-e", 'process.stdout.write("x".repeat(2*1024*1024))']);
} catch (e) {
  e.code;   // "ERR_CHILD_PROCESS_STDIO_MAXBUFFER"
}

// 已知输出较大时显式上调（内存自担）
await pExecFile("pandoc", ["doc.md"], { maxBuffer: 10 * 1024 * 1024 });
}
```

- 输出可能超过几 MB → 不调 maxBuffer，**直接改用 `spawn` 流式处理**
- `spawn` 没有此选项——它本来就不过度缓冲

## 3. shell 注入风险

### 定义
`exec` 与 `spawn(..., { shell: true })` 会把整条命令交给 `/bin/sh` 解释；用户输入拼进命令串时，攻击者可用 `; rm -rf /`、`$(...)` 等元字符执行任意命令。

```ts
// ❌ 注入：用户输入 "a.jpg; cat /etc/passwd" 直接进 shell
exec(`convert ${userFile} out.png`);

// ✅ execFile：用户输入永远是"一个参数"，不进 shell 解释
execFile("convert", [userFile, "out.png"]);
```

### 陷阱
- ❌ 用 `exec` + 模板字符串拼接任何含用户输入的命令
- ✅ 默认 `execFile`/`spawn`（参数数组）；确需 shell 时固定脚本与语法，并按平台核对引用规则；环境变量和 argv0 本身不是安全保证
- ✅ fork 的模块路径必须可信，传入参数仍需按子程序规则验证，不能声称不存在任何注入面

## 4. fork 与 node:cluster 分工

### 定义
`fork` 是 `spawn` 的 Node 专属特化：子进程是另一个 JS 模块，父子之间自动建立 **IPC 消息通道**。

```ts
// 父进程
const child = fork("./heavy-task.mjs", ["--file", "big.csv"]);
child.send({ type: "start" });
child.on("message", (msg) => console.log(msg));

// heavy-task.mjs（子进程）
process.on("message", (msg) => { /* ... */ process.send({ done: true }); });
```

| 需求 | 选型 |
|------|------|
| 并行跑同一个 HTTP 服务的多份实例、分摊端口 | `node:cluster`（它内部也用 child_process） |
| 一次性把 CPU 密集任务丢出去 | `fork` 或 `worker_threads` |
| 调外部非 Node 程序 | `spawn`/`execFile` |
| CPU 密集且要共享内存、开销要小 | `worker_threads`（线程）优于 `fork`（进程） |

### 陷阱
- ❌ 每个请求都 fork 一个子进程——进程创建开销远大于线程，高并发下打爆机器
- ✅ 重计算任务先考虑 `worker_threads` 或任务队列 + 常驻 fork 进程池
- 子进程不会随父进程自动终止，退出前记得 `child.kill()`；孤儿进程是僵尸容器内存的常见来源

<!-- full-library-explanation -->
## 参数数组、输出消费与退出结果分别负责什么

前置是 Promise、事件和流。参数数组避免 shell 对分号、替换表达式等进行解释，但被调用程序仍会解析选项、路径和自己的表达式语言。固定可执行文件、限制允许参数，支持时用 -- 分隔选项与位置参数；argv0 只是改变进程看见的名称，不是注入防护。shell:false 也不能阻止用户指定危险文件路径。

独立实验保存为 child.mjs，运行 node child.mjs：

```js
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
const run = promisify(execFile);
const { stdout } = await run(process.execPath, [
  '-e', 'console.log(process.argv[1])', 'a b; c',
], { timeout: 2000, maxBuffer: 1024 });
console.log(stdout.trim());
```

预期完整输出 `a b; c`，没有把分号当作第二个命令。练习：让子进程以 2 退出，Promise 应拒绝并保留退出信息。spawn 的 stdout 和 stderr 都要消费或明确重定向，未读取的一侧可能填满管道使进程卡住；在处理输出前就登记 close/error 等待，避免错过事件。超时后还要确认子进程是否真正退出，kill 发出信号不等于等待完成。

## 🔗 相关文档

- 📄 **[Stream API 速查](../language-concepts/04-streams-api.md)** — spawn 流输出的消费方式
- 📄 **[进程生命周期](./07-process-lifecycle.md)** — 退出码、信号与优雅退出（父子进程联动）
- 📄 **[Stream 与 Worker](../../basics/07-streams-workers.md)** — 多线程与多进程的教学讲解
- 🌐 **[Node.js 官方文档: child_process](https://nodejs.org/docs/latest/api/child_process.html)** — 选项与 stdio 配置权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
