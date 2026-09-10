# 事件循环原理与性能陷阱

> **文档简介**: 深入 Node.js 事件循环的六个阶段与微任务时序，解释"单线程为什么也能扛高并发"以及它何时会失灵——并给出阻塞检测与热路径优化的实操方法
>
> **目标读者**: 需要诊断延迟抖动、理解 QPS 上限来源的中高级后端开发者
>
> **前置知识**: [异步编程](../../basics/04-async-promises.md)、[事件循环速查](../../reference/language-concepts/02-async-api.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#event-loop` `#performance` `#libuv` `#profiling` |
| **更新日期** | `2026年9月` |

## 🎯 阅读目标

- 建立事件循环阶段的准确心智模型（而非"异步就是快"）
- 识别三类典型阻塞源并掌握检测手段
- 掌握热路径的优化优先级

## 1. 事件循环到底在循环什么

Node 进程启动后，事件循环按固定顺序轮询六个阶段，每个阶段维护一个回调队列：

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

关键细节一：**微任务不在这六个阶段里**。每执行完一个宏任务回调（含 timers 阶段的单个 timer），Node 都会清空整个微任务队列（Promise.then、queueMicrotask）才继续——这就是为什么 `await` 之后的微任务总在下一个 `setImmediate` 前执行。

关键细节二：**poll 阶段是吞吐的主战场**。它决定事件循环"睡多久、忙多久"：没有到期 timer 且队列为空时阻塞在 epoll 上等 I/O；一旦某回调执行 50ms，期间所有其他请求的回调都在排队——这就是单线程延迟抖动的来源。

**为什么单线程也能高并发**：回调本身只是"启动 I/O + 处理结果"的胶水代码，真正的 I/O 等待发生在内核与 libuv 线程池（默认 4 线程，承接 fs/DNS/加密）。线程只有一个，但**并发数不等于线程数**——取决于"等待中的连接数"，而非"执行中的回调数"。

## 2. 事件循环什么时候失灵：三类阻塞源

### 类型 A：CPU 密集的回调

```typescript
// 反例：同步加密在主线程跑，期间全部请求冻结
import crypto from 'node:crypto';

app.post('/hash', (req, res) => {
  const digest = crypto.pbkdf2Sync(req.body.pwd, salt, 600_000, 32, 'sha256');
  // pbkdf2Sync 阻塞主线程 300ms+，其余请求全部排队
  res.json({ digest: digest.toString('hex') });
});

// 正解：异步版本自动进 libuv 线程池
import { promisify } from 'node:util';

app.post('/hash', async (req, res) => {
  const digest = await promisify(crypto.pbkdf2)(req.body.pwd, salt, 600_000, 32, 'sha256');
  res.json({ digest: digest.toString('hex') });
});
```

同类陷阱：超大 `JSON.parse`、同步 zlib、复杂正则（ReDoS）、图片处理库的同步 API。CPU 密集任务的根治方案见 [`02-streaming-clustering.md`](02-streaming-clustering.md)。

### 类型 B：隐藏在"异步"背后的同步段

```typescript
// 每个 await 前后的同步代码段同样占用主线程：
router.get('/report', async (_req, res) => {
  const rows = await db.report.findMany(); // I/O 是异步的
  const html = heavyTemplateRender(rows);  // 但渲染是同步 CPU！
  res.send(html);
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

// 健康指标：p99 持续 > 100ms 即存在阻塞源，接到 metrics 系统告警
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
2. **异步化一切同步 I/O 与 CPU 回调**（`fs.promises`、`crypto` 异步版、流式替代整读）
3. **调大 libuv 线程池**：`UV_THREADPOOL_SIZE=8`（fs/DNS/crypto 密集型服务收益明显）
4. **缓存读多写少的数据**：Redis 层见 [`../../frameworks/03-ecosystem-integration.md`](../../frameworks/03-ecosystem-integration.md)
5. **仍不够再上 cluster/worker**：见 [`02-streaming-clustering.md`](02-streaming-clustering.md)——多进程是最后手段而非第一步

## 🔗 相关文档

- 📖 [异步 API 全表](../../reference/language-concepts/02-async-api.md) — 微任务/定时器字典
- 📄 [流处理与集群](02-streaming-clustering.md) — CPU 密集与多进程方案
- 📄 [异步编程](../../basics/04-async-promises.md) — 教程版的事件循环入门
- 📖 [常见故障排除](../../reference/quick-references/02-troubleshooting.md) — 阻塞症状速查
