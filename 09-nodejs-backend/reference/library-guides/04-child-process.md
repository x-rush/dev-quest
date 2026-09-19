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
| `execFile` | 默认不走（参数数组） | 回调（整体缓冲） | **1 MiB**（maxBuffer） | 调已知可执行文件，仍需校验参数语义 |
| `fork` | 不走 | 默认继承 stdio + IPC；`silent: true` 才将标准流改为管道 | 无 maxBuffer | 跑另一个 Node 模块，可双向通信 |

### 平台相关片段（Node 24，需外部命令）

以下 echo/wc 以 POSIX 命令环境为前提，ffmpeg 还需安装并准备输入文件；不是跨平台的完整程序。只依赖 Node 的命名运行验证在文末。

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
`exec`/`execFile` 收集子进程 stdout/stderr；stdout 或 stderr 超过各自默认 **1 MiB** 上限时报告错误并终止子进程，输出可能被截断。上限按字节而非字符数计算。

```ts
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const pExecFile = promisify(execFile);

async function demonstrateMaxBuffer() {
// 预期：2 MiB 输出超过默认上限
try {
  await pExecFile("node", ["-e", 'process.stdout.write("x".repeat(2*1024*1024))']);
} catch (e) {
  if (e instanceof Error && "code" in e) {
    console.log(e.code); // 预期 ERR_CHILD_PROCESS_STDIO_MAXBUFFER
  } else throw e;
}

// 已知输出较大时显式上调（内存自担）
await pExecFile("pandoc", ["doc.md"], { maxBuffer: 10 * 1024 * 1024 });
}
```

- 对大小有界的小报告可提高 maxBuffer 并承担内存成本；持续日志或大型产物宜使用流或直接写文件。
- `spawn` 没有 maxBuffer，但管道和流仍有缓冲。如果调用方把 chunk 全部放进数组，内存仍随输出总量增长。

## 3. shell 注入风险

### 定义
`exec` 与启用 shell 的 `spawn` 会把命令交给平台 shell 解释，Unix 默认 `/bin/sh`，Windows 使用对应命令解释器。用户输入拼进命令串时，分号、命令替换等语法可能变成额外命令。

```ts
// ❌ 注入：用户输入 "a.jpg; cat /etc/passwd" 直接进 shell
exec(`convert ${userFile} out.png`);

// 默认无 shell：这是一个参数，但 convert 仍会解析自己的选项和路径
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
import { fork } from 'node:child_process';
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
| CPU 密集且要共享内存 | 比较 worker_threads 与进程池的实测成本；共享内存需额外同步 |

### 陷阱
- 每个请求都 fork 会重复付出进程启动与独立运行时内存成本，负载增大时容易耗尽资源；先测量任务成本并设置并发上限，再考虑复用进程池。
- ✅ 重计算任务先考虑 `worker_threads` 或任务队列 + 常驻 fork 进程池
- 不能依赖父进程退出自动清理整棵进程树。`child.kill()` 表示发送信号，不保证退出，更不保证终止孙进程；要等待关闭并设计平台相关的超时升级策略。
- 孤儿进程是父进程已结束而仍在运行的子进程；僵尸进程已退出但退出状态尚未回收。两者不同。
- exit 说明进程退出，close 还说明 stdio 已关闭；拿到 ChildProcess 对象不代表启动或任务成功。
- Windows 的 `.bat`/`.cmd` 不能当普通可执行文件直接通过无 shell 的 execFile 启动；优先选真实可执行文件，特殊入口按平台规则处理。

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

## 可复现验证：参数、失败与管道

下面两个完整程序保存为 `.mjs` 后用 Node 24 执行。它们只调用当前 `process.execPath`，不依赖外部命令。报告不覆盖上面的 ffmpeg、pandoc、fork IPC 或 Windows 批处理。

### 小输出：区分成功、非零退出与超限

<!-- library-case: node-child-buffer -->
```js
import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const run = promisify(execFile);
const options = { timeout: 5000, maxBuffer: 1024, encoding: 'utf8' };
const literal = await run(process.execPath, [
  '-e', 'process.stdout.write(process.argv[1])', 'a b; c',
], options);
assert.equal(literal.stdout, 'a b; c');
assert.equal(literal.stderr, '');
await assert.rejects(
  run(process.execPath, ['-e', "process.stderr.write('bad input'); process.exitCode = 2"], options),
  error => error.code === 2 && error.stderr === 'bad input',
);
await assert.rejects(
  run(process.execPath, ['-e', "process.stdout.write('x'.repeat(4096))"], options),
  error => error.code === 'ERR_CHILD_PROCESS_STDIO_MAXBUFFER',
);
console.log('child-buffer: literal, nonzero, maxBuffer');
```

输出为 `child-buffer: literal, nonzero, maxBuffer`。非零退出必须拒绝，不能只检查有没有 stdout；超限错误携带的部分输出不能作为完整产物发布。断言具体错误能避免“捕获任意异常都算正确”的误判。

### 大输出：同时消费两条流并等待 close

<!-- library-case: node-child-stream -->
```js
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';

const child = spawn(process.execPath, ['-e',
  "process.stdout.write('x'.repeat(128 * 1024)); process.stderr.write('y'.repeat(96 * 1024));",
], { stdio: ['ignore', 'pipe', 'pipe'], timeout: 5000 });
const closed = once(child, 'close');
async function countBytes(stream) {
  let size = 0;
  for await (const chunk of stream) size += chunk.length;
  return size;
}
const [outBytes, errBytes, [code, signal]] = await Promise.all([
  countBytes(child.stdout), countBytes(child.stderr), closed,
]);
assert.equal(code, 0);
assert.equal(signal, null);
assert.equal(outBytes, 128 * 1024);
assert.equal(errBytes, 96 * 1024);
console.log('child-stream: 131072 stdout, 98304 stderr, exit 0');
```

输出为 `child-stream: 131072 stdout, 98304 stderr, exit 0`。同时读取 stdout/stderr 避免一侧管道填满后阻塞进程。这里只累计字节数，不保存全部输出。通用服务还需在消费失败时终止任务、回收其它流。

练习：改为退出码 3，保留字节数断言并验证退出码；再换成不存在的可执行文件，确认启动失败进入 error 路径。不要把启动失败和业务程序返回非零退出码混为一类。

命名证据见 [Node/Python 标准库验证](../../../shared-resources/tools/document-quality/reports/node-python-libraries.md)。

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
