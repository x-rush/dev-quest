# 异步 API 全表

## 如何选择组合方式

前置：Promise 有进行中、成功和失败状态；await 在 async 函数或 ESM 顶层等待结果。Promise.all 适用于所有结果都必需，allSettled 用于逐项处理成功失败，race 等待第一个结束，any 等待第一个成功。

把“两家供应商报价”作为具体问题：要求两份都拿到才能比较，用 all；允许缺一份也展示，用 allSettled；只取最快成功报价，用 any。race 可能最先得到一个失败，不能把它称为最快成功。

边界：这些组合器不会自动取消已经启动的底层任务。超时 Promise 赢得 race 后，网络请求仍可能继续；需要把 AbortSignal 传给支持取消的 API。

自测：一个 Promise 立即拒绝，另一个稍后成功。all 与 race 会拒绝，any 可以成功，allSettled 返回两项状态。空输入时 all 和 allSettled 成功得到空数组，any 拒绝，race 保持 pending；不要用空 race 实现“无需工作”。

> **文档简介**: Node.js 异步相关 API 的字典式速查——Promise 静态方法、定时器、queueMicrotask、process.nextTick 与 AbortSignal 全集

> **目标读者**: 需要确认某个异步 API 精确语义的开发者

> **前置知识**: [异步编程教程](../../basics/04-async-promises.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#Promise` `#定时器` `#AbortSignal` `#事件循环` |
| **更新日期** | `2026年9月` |

</details>

## 1. Promise 静态方法

### 定义
`Promise` 构造函数上的组合器，把多个 Promise 按不同失败语义合并。

### 对比总表

| 方法 | 全成功 | 任一失败 | 失败时结果 |
|------|--------|---------|-----------|
| `Promise.all` | 数组按序返回 | **立即 reject**（第一个失败） | 失败原因 |
| `Promise.allSettled` | — | **永不 reject** | 每项 `{status, value/reason}` |
| `Promise.any` | 第一个成功值 | **全部失败才 reject** | `AggregateError`（含 errors 数组） |
| `Promise.race` | 第一个落定者胜 | 透传第一个落定（含失败） | 首个结果（成功或失败） |

### 语法与示例

```ts
// all：强依赖并行
const [user, orders] = await Promise.all([
  fetchUser(id),
  fetchOrders(id),
]);

// allSettled：批处理聚合，失败项单独处理
const results = await Promise.allSettled(urls.map((u) => fetch(u)));
const failed = results
  .filter((r): r is PromiseRejectedResult => r.status === "rejected")
  .map((r) => r.reason);

// any：多源容错，任一镜像可用即可
const fastest = await Promise.any([mirrorA(), mirrorB(), mirrorC()]);

// race：超时竞速（更推荐 AbortSignal.timeout）
const data = await Promise.race([fetchSlow(), rejectAfter(3_000)]);
```

### 陷阱
- `Promise.all` 一个失败会**立即 reject，但其余任务不会取消**，仍在后台运行——需要取消时必须配合 AbortSignal
- `race` 若先落定的是失败，整体就失败；想要"第一个成功"用 `any`
- `Promise.withResolvers()`（ES2024）：把 resolve/reject 拿到 Promise 外部，替代手写 new Promise 包装

## 2. 定时器 API

### 定义
全局（无需 import）的延时/周期调度函数，回调进入事件循环 timers 阶段。

### 条目一览

```ts
// 基础定时
const id = setTimeout(fn, 100, arg1, arg2);   // 第三参起为 fn 的参数
clearTimeout(id);

// 周期执行（注意：间隔不保证精确）
const pid = setInterval(fn, 1_000);
clearInterval(pid);

// 立即执行（check 阶段，晚于本轮微任务）
const iid = setImmediate(fn);
clearImmediate(iid);

// Promise 化定时（Node 15+，支持取消信号）
import { setTimeout } from "node:timers/promises";
await setTimeout(500);                        // 定时等待
await setTimeout(500, "value");               // 定时并返回值
await setTimeout(500, undefined, { signal }); // 可被 AbortSignal 取消
```

### 陷阱
- `setInterval` 回调耗时超过间隔会造成**任务堆积**；用递归 `setTimeout` 链替代
- Node 中的定时器随事件循环引用计数：未 `unref()` 的定时器会**阻止进程退出**
- 定时器回调里的异常会变成 `uncaughtException`

## 3. 微任务调度

### 定义
把函数排入微任务队列，在当前同步代码结束后、下一宏任务前执行。

### 语法与示例

```ts
queueMicrotask(() => console.log("微任务"));
process.nextTick(() => console.log("nextTick，比微任务更早"));

// 优先级：同步代码 > process.nextTick > Promise/queueMicrotask > setImmediate/setTimeout
```

### 陷阱
- `process.nextTick` 递归调用会**饿死事件循环**（永远进不了 I/O 阶段），递归场景改用 `setImmediate`
- 业务代码极少需要 `queueMicrotask`，多数场景是 Promise.then 的误用

## 4. AbortSignal 家族

### 定义
标准取消协议：`AbortController` 产生信号，订阅该信号的 API 收到取消通知。

### API 全表

```ts
const controller = new AbortController();
const signal = controller.signal;

// 三类消费方式
signal.addEventListener("abort", handler);   // 事件监听
signal.aborted;                              // 布尔：是否已取消
signal.reason;                               // 取消原因（默认 AbortError）
signal.throwIfAborted();                     // 已取消则抛 reason

// 静态工具
AbortSignal.timeout(5_000);                  // 5 秒后自动 abort（TimeoutError）
AbortSignal.any([s1, s2]);                   // 任一触发即触发
AbortSignal.abort(reason);                   // 预先取消的信号

// 支持信号的常用 API
fetch(url, { signal });
await setTimeout(ms, value, { signal });     // 仅 timers/promises 版支持；全局 setTimeout 第三参是传给回调的展开参数
eventEmitter.on(evt, fn, { signal });        // 自动解绑
fsPromises.readFile(p, { signal });
```

### 陷阱
- 取消是**协作式**的：API 收到信号后尽力中断，正在执行的同步代码无法被打断
- `AbortSignal.timeout` 每个实例都持有定时器，循环中大量创建需注意句柄释放
- fetch 收到超时取消抛 `TimeoutError`，手动取消抛 `AbortError`，两者都要捕获

## 5. 异步上下文

### 定义
`AsyncLocalStorage` 在异步调用链中传播上下文（如请求 ID），替代层层传参。

### 语法与示例

```ts
import { AsyncLocalStorage } from "node:async_hooks";

const requestContext = new AsyncLocalStorage<{ requestId: string }>();

// 中间件中绑定（Hono 中间件签名：c + next）
app.use((c, next) => {
  requestContext.run({ requestId: crypto.randomUUID() }, next);
});

// 任意深度的异步函数中读取，无需显式传参
function log(msg: string) {
  const { requestId } = requestContext.getStore() ?? {};
  console.log(`[${requestId}] ${msg}`);
}
```

### 陷阱
- 回调式（非 Promise/async）API 中上下文可能丢失，优先用 Promise 风格 API
- 不要把业务数据放进 ALS，只放横切元数据（traceId、租户 ID）

---

## 🔗 相关文档

- 📄 **[异步编程教程](../../basics/04-async-promises.md)** — 事件循环与并发控制的教学讲解
- 📄 **[现代 JS 语法速查](./01-js-modern-syntax.md)** — async/await 语法细节
- 📄 **[常见故障排除](../quick-references/02-troubleshooting.md)** — 未处理 rejection 排查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
