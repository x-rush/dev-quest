# Stream 管道与多线程

> **文档简介**: 掌握 Node.js 的两大性能武器——Stream 流式处理（含背压）与 Worker Threads 多线程，让 I/O 与 CPU 密集任务不再拖垮服务

> **目标读者**: 完成入门六课后，需要处理大文件、批量数据或计算密集任务的进阶学习者

> **前置知识**: [异步编程](./04-async-promises.md)，[错误处理](./06-error-handling.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐⭐ |
| **标签** | `#Stream` `#pipeline` `#背压` `#WorkerThreads` `#cluster` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- 辨认四种 Stream 类型并选择正确的组合方式
- 用 `pipeline` 串联流并处理错误与清理
- 解释背压产生的原因，识别 `pipe` 的坑
- 用 Worker Threads 隔离 CPU 密集任务，用 cluster 扩展多核 I/O

## 🔍 Stream：为什么与四种类型

一次读 2GB 文件到内存 = 服务抖动 + 内存告警。Stream 把数据切成小块（chunk）流动，内存占用恒定、首字节延迟低。

| 类型 | 方向 | 典型代表 |
|------|------|---------|
| Readable | 可读 | `fs.createReadStream`、HTTP 请求体 |
| Writable | 可写 | `fs.createWriteStream`、HTTP 响应体 |
| Duplex | 可读可写（独立） | TCP socket |
| Transform | 读入变换后写出 | `zlib.createGzip()`、csv 转换器 |

### pipeline：唯一推荐的组合方式

```ts
import { createReadStream, createWriteStream } from "node:fs";
import { createGzip } from "node:zlib";
import { pipeline } from "node:stream/promises";

// 把大日志文件压缩归档
await pipeline(
  createReadStream("app.log"),       // Readable
  createGzip(),                      // Transform
  createWriteStream("app.log.gz"),   // Writable
);
console.log("压缩完成");
```

为什么用 `pipeline` 而不是 `pipe`：

- **错误聚合**：任一环节出错，整条链收到通知并自动销毁所有流；`pipe` 只在源流上转发错误，下游错误会静默丢失
- **自动清理**：出错时关闭所有流、释放文件句柄
- **Promise 化**：`node:stream/promises` 版本可直接 await，async 函数里抛错自然传播

### 背压（backpressure）：生产快于消费怎么办

当 Writable 消费速度跟不上 Readable 产出，数据会在内存里堆积。手动处理需要检查 `write()` 返回值并监听 `drain`：

```ts
// 手动背压处理——理解原理用，实际请用 pipeline
readable.on("data", (chunk) => {
  const canContinue = writable.write(chunk);
  if (!canContinue) {
    readable.pause();                 // 暂停读取
    writable.once("drain", () => readable.resume()); // 缓冲清空后恢复
  }
});
```

`pipeline`（以及 `Readable.pipe`）内部已实现该协议。**自己写 `on('data') + write()` 而不处理背压，是最常见的流内存事故**。

## 🛠️ 实战：Transform 流

Transform 是自定义数据处理的标准姿势：

```ts
import { Transform } from "node:stream";
import { pipeline } from "node:stream/promises";

// 逐行大写转换器
function toUpperStream() {
  return new Transform({
    transform(chunk, _encoding, callback) {
      const upper = chunk.toString().toUpperCase();
      callback(null, upper);   // (err, data)：null 表示无错误
    },
  });
}

await pipeline(
  process.stdin,     // 可读：终端输入
  toUpperStream(),
  process.stdout,    // 可写：输出
);
```

## 🔍 Worker Threads：CPU 密集的出路

事件循环是单线程的：一个 200ms 的图像缩放会让所有请求排队。Worker Threads 把计算移到独立线程，主线程继续服务请求。

```ts
// worker/hash.ts —— 工作线程脚本
import { parentPort, workerData } from "node:worker_threads";

// 执行 CPU 密集计算（workerData 是主线程传入的输入）
const result = heavyHash(workerData.filePath);
parentPort.postMessage(result);
```

```ts
// main.ts —— 主线程封装成 Promise
import { Worker } from "node:worker_threads";
import { fileURLToPath } from "node:url";

export function hashInWorker(filePath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const worker = new Worker(
      fileURLToPath(new URL("./worker/hash.ts", import.meta.url)),
      { workerData: { filePath } },
    );
    worker.on("message", resolve);
    worker.on("error", reject);
    worker.on("exit", (code) => {
      if (code !== 0) reject(new Error(`Worker 异常退出: ${code}`));
    });
  });
}

// 路由中使用：主线程完全不阻塞
app.post("/files/:id/hash", async (c) => {
  const filePath = resolvePath(c.req.param("id")); // 业务侧把 id 映射为文件路径
  const hash = await hashInWorker(filePath);
  return c.json({ hash });
});
```

关键认知：

- **线程数 ≈ CPU 核数**：开太多 worker 反而争抢资源，可用池化库（piscina）管理
- **Worker 与主线程不共享堆**：通过 `postMessage` 结构化拷贝通信；大数据用 `SharedArrayBuffer` 零拷贝共享
- **每个 Worker 有独立事件循环**，内存开销约几 MB 起，不要为小任务开 worker

### cluster：多核扩展 I/O

cluster 与 Worker 定位不同——它是**复制整个进程**来利用多核：

```ts
import cluster from "node:cluster";
import { availableParallelism } from "node:os";
import { createServer } from "node:http";

if (cluster.isPrimary) {
  // 主进程：按核数 fork 子进程，退出即重启
  for (let i = 0; i < availableParallelism(); i++) {
    cluster.fork();
  }
  cluster.on("exit", () => cluster.fork());
} else {
  // 每个子进程独立运行完整的服务
  createServer(handler).listen(3000);
}
```

| 方案 | 适用 | 通信成本 |
|------|------|---------|
| Worker Threads | CPU 密集计算（压缩/图像/解析） | 结构化拷贝，低成本 |
| cluster | 多核承载大量 I/O 请求 | 进程间隔离，天然容错（崩溃不互相影响） |
| 容器多实例 | 更普遍的现代选择（K8s 副本数） | 完全进程隔离 |

云原生时代，容器编排通常取代了应用内 cluster，但理解其原理对排查端口共享与负载不均问题很有价值。

## 🎨 最佳实践

- ✅ **一律 `pipeline`，禁用裸 `pipe`**：错误处理与清理自动完成
- ✅ **HTTP 上传/下载走流**：`req`/`res` 本身就是流，别用 buffer 中转
- ✅ **CPU 任务先测量再优化**：`console.time` 或 `perf_hooks` 确认超过 ~10ms 才值得上 worker
- ❌ **不要在 worker 里访问主线程对象**：线程间只有消息传递
- ❌ **不要用 cluster 解决 CPU 瓶颈**：每个子进程照样有自己阻塞的事件循环

## ❓ 常见问题

### Q1: pipeline 中途出错，已写的部分文件怎么办？

**A**: pipeline 会销毁所有流但不会删除半成品文件。需要在 catch 里自行清理（`fs.rm`）或先写临时文件再 rename。

### Q2: Worker 里能运行 TypeScript 吗？

**A**: 与主进程相同——Node 24 类型剥离同样适用于 worker 入口文件；打包部署场景构建为 js 后再引用。

## 🎯 练习与实践

### 练习一：流式日志处理

**任务要求**:
1. 生成一个 100MB 的日志文件（每行 JSON）
2. 用 pipeline 逐行读取，仅输出 level=error 的行到新文件
3. 对比流式与 `readFile` 全量读的内存峰值（`process.memoryUsage()`）

### 练习二：CPU 基准测试

**挑战任务**:
- 写一个同步计算 fibonacci(40) 的接口，用压测工具（autocannon）记录吞吐
- 把计算移入 worker，再压测对比
- 写下两版数据的差异结论

**提示**: 对比时保持并发数一致，观察 P99 延迟变化。

---

## 🔗 相关文档

- 📄 **[Stream API 速查](../reference/language-concepts/04-streams-api.md)** — 四类流的方法与事件字典
- 📄 **[Node 核心模块](../reference/language-concepts/03-node-core-api.md)** — fs/os/child_process 配合使用
- 📄 **[第一个项目](./08-first-project.md)** — 综合运用到完整 API
