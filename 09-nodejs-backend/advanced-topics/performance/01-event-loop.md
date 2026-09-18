# 事件循环原理与性能陷阱

> **文档简介**: 深入 Node.js 事件循环的六个阶段与微任务时序，解释"单线程为什么也能扛高并发"以及它何时会失灵——并给出阻塞检测与热路径优化的实操方法
>
> **目标读者**: 需要诊断延迟抖动、理解 QPS 上限来源的中高级后端开发者
>
> **前置知识**: [异步编程](../../basics/04-async-promises.md)、[事件循环速查](../../reference/language-concepts/02-async-api.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#event-loop` `#performance` `#libuv` `#profiling` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 阅读目标

- 建立事件循环阶段的准确心智模型（而非"异步就是快"）
- 识别三类典型阻塞源并掌握检测手段
- 掌握热路径的优化优先级

## 1. 事件循环到底在循环什么

事件循环分阶段处理工作。下图省略内部 idle/prepare 阶段，展示主要回调类别；不要把它当作所有版本的逐步执行轨迹：

```text
   ┌───────────────────────────┐
┌─▶│ timers                    │ ← setTimeout/setInterval 到期的回调
│  ├───────────────────────────┤
│  │ pending callbacks         │ ← 系统级回调（如 TCP 错误）的延迟执行
│  ├───────────────────────────┤
│  │ poll                      │ ← 轮询 I/O：取回新完成的 I/O 事件并执行其回调
│  ├───────────────────────────┤
│  │ check                     │ ← setImmediate 回调
│  ├───────────────────────────┤
│  │ close callbacks           │ ← socket.on('close') 等
│  └───────────────────────────┘
```

关键细节一：**微任务不在这六个阶段里**。每执行完一个宏任务回调（含 timers 阶段的单个 timer），Node 都会清空整个微任务队列（Promise.then、queueMicrotask）才继续。只有 Promise 已兑现后，对应继续执行才会入队；等待未完成 I/O 的 `await` 不保证先于 `setImmediate`。

关键细节二：**poll 阶段是吞吐的主战场**。它决定事件循环"睡多久、忙多久"：没有到期 timer 且队列为空时通过平台事件机制等待 I/O（Linux 通常为 epoll）；一旦某回调执行 50ms，期间所有其他请求的回调都在排队——这就是单线程延迟抖动的来源。

**为什么单线程也能高并发**：回调本身只是"启动 I/O + 处理结果"的胶水代码，真正的 I/O 等待发生在内核与 libuv 线程池（默认 4 线程，承接 fs/DNS/加密）。主 JavaScript 执行线程通常只有一个，但进程还有其他线程，且**并发数不等于线程数**——取决于"等待中的连接数"，而非"执行中的回调数"。

## 2. 事件循环什么时候失灵：三类阻塞源

### 类型 A：CPU 密集的回调

```typescript
// 反例：同步加密在主线程跑，期间全部请求冻结
import crypto from 'node:crypto';

const salt = crypto.randomBytes(16);

app.post('/hash', async (c) => {
  const { pwd } = await c.req.json();
  const digest = crypto.pbkdf2Sync(pwd, salt, 600_000, 32, 'sha256');
  // 同步计算期间阻塞此线程；耗时取决于硬件与参数。这里只比较调度，不是密码存储方案
  return c.json({ digest: digest.toString('hex') });
});

// 正解：异步版本自动进 libuv 线程池
import { promisify } from 'node:util';

app.post('/hash', async (c) => {
  const { pwd } = await c.req.json();
  const digest = await promisify(crypto.pbkdf2)(pwd, salt, 600_000, 32, 'sha256');
  return c.json({ digest: digest.toString('hex') });
});
```

同类陷阱：超大 `JSON.parse`、同步 zlib、复杂正则（ReDoS）、图片处理库的同步 API。CPU 密集任务的根治方案见 [`02-streaming-clustering.md`](02-streaming-clustering.md)。

### 类型 B：隐藏在"异步"背后的同步段

```typescript
// 每个 await 前后的同步代码段同样占用主线程：
app.get('/report', async (c) => {
  const rows = await db.report.findMany(); // I/O 是异步的
  const html = heavyTemplateRender(rows);  // 但渲染是同步 CPU！
  return c.html(html);
});
```

### 类型 C：日志/序列化的隐性成本

`console.log(巨大对象)` 的字符串化发生在主线程；pino 的核心卖点之一就是把序列化做到足够便宜。热路径上打印调试对象是延迟抖动的常见元凶。

## 3. 检测手段：让阻塞现形

```typescript
// 方法一：monitorEventLoopDelay —— 官方 API 测事件循环延迟分布
import { monitorEventLoopDelay } from 'node:perf_hooks';

const histogram = monitorEventLoopDelay({ resolution: 10 });
histogram.enable();

setInterval(() => {
  console.log({
    p99: `${(histogram.percentile(99) / 1e6).toFixed(1)}ms`, // 纳秒转毫秒
    max: `${(histogram.max / 1e6).toFixed(1)}ms`,
    mean: `${(histogram.mean / 1e6).toFixed(1)}ms`,
  });
  histogram.reset();
}, 10_000).unref();

// 结合基线与服务目标设告警；延迟升高也可能来自 CPU 争抢或 GC
```

```typescript
// 方法二：blocked-at 库定位"谁"在阻塞
import blocked from 'blocked-at';

blocked((time, stack) => {
  console.warn(`事件循环被阻塞 ${time}ms`, stack); // stack 直接指向罪魁调用栈
}, { threshold: 50 }); // 超过 50ms 才报告
```

```bash
# 方法三：CPU profile——看到每个函数的 CPU 占比
node --cpu-prof --cpu-prof-dir=./prof dist/server.js
# 复现负载后用 Chrome DevTools 打开 *.cpuprofile 分析热点
```

## 4. 优化优先级（先测后改）

1. **先量化**：没有 p99 数据的优化都是猜。接到 [`../../deployment/03-observability.md`](../../deployment/03-observability.md) 的监控再动手
2. **减少请求路径中的同步 I/O，隔离或削减重计算**（`fs.promises`、`crypto` 异步版、流式替代整读）
3. **在压测中比较线程池大小**：进程启动前设置 `UV_THREADPOOL_SIZE`，仅影响使用该池的操作；网络套接字并不都占用池线程
4. **缓存读多写少的数据**：Redis 层见 [`../../frameworks/03-ecosystem-integration.md`](../../frameworks/03-ecosystem-integration.md)
5. **仍不够再上 cluster/worker**：见 [`02-streaming-clustering.md`](02-streaming-clustering.md)——多进程是最后手段而非第一步

<!-- full-library-explanation -->
## 把响应时间拆开，再决定优化位置

一次请求的耗时可能包含排队、数据库等待、JavaScript 计算和响应写出。`await` 只让当前函数暂停，不会把它前后的计算自动搬到其他线程。若每个请求同步计算 50ms，同一个 JavaScript 线程每秒最多只能完成约 20 次这样的计算，增加连接数只会增加排队。

做一个对照实验：在测试服务加入固定计算任务，同时持续访问轻量健康接口。记录健康接口 p95、CPU、事件循环延迟和任务吞吐；再将任务交给有容量上限的线程池。若健康接口变快而总吞吐不变，说明隔离改善了响应性，CPU 总预算仍是瓶颈。不要用一次本机计时宣称框架性能排名。

**判断题**：给一个包含巨大 `JSON.parse` 的函数加 `async`，能避免阻塞吗？不能，解析仍在调用线程同步执行。把线程池从 4 增至 32 一定更快吗？也不能，排队、CPU 争抢和内存开销都可能增加。

阶段图用于理解职责，不是跨版本的精确调度契约。参见 [Node 事件循环说明](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)：libuv 1.45 起定时器主要在 poll 后处理，不应依赖顶层零延时 timer 与 immediate 的固定顺序。

## 🔗 相关文档

- 📖 [异步 API 全表](../../reference/language-concepts/02-async-api.md) — 微任务/定时器字典
- 📄 [流处理与集群](02-streaming-clustering.md) — CPU 密集与多进程方案
- 📄 [异步编程](../../basics/04-async-promises.md) — 教程版的事件循环入门
- 📖 [常见故障排除](../../reference/quick-references/02-troubleshooting.md) — 阻塞症状速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
