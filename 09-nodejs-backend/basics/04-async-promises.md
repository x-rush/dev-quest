# 异步编程：事件循环、Promise 与取消

> **文档简介**: 系统掌握 Node.js 异步模型——事件循环阶段、Promise/async-await、超时与 AbortController 取消模式

> **目标读者**: 有回调/Promise 使用经验但对其原理模糊的开发者

> **前置知识**: [模块系统与 ESM](./03-modules-esm.md)，基本的 JS 函数概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#事件循环` `#Promise` `#async-await` `#AbortController` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- 画出事件循环的六大阶段并解释宏/微任务的执行顺序
- 用 async/await 编写健壮的异步流程（含并发与错误处理）
- 用 AbortController 实现超时控制与请求取消
- 识别阻塞事件循环的代码模式

## 🔍 事件循环：Node 并发的心脏

Node 是单线程执行 JS 的，靠事件循环调度 I/O 回调实现并发。每轮循环经过六个阶段：

```
┌─ timers          执行 setTimeout / setInterval 到期回调
├─ pending         执行延迟到下一轮的 I/O 回调
├─ idle/prepare    内部使用
├─ poll            获取新 I/O 事件，执行 I/O 回调
├─ check           执行 setImmediate 回调
└─ close           执行 close 事件回调（如 socket.on('close')）
     ↓ 进入下一轮（tick）
```

两个关键插队规则：

- **微任务**（Promise 回调、`queueMicrotask`、`process.nextTick`）在**每个阶段之间**全部清空后才进入下一阶段
- `process.nextTick` 优先级高于 Promise 微任务

用一段代码验证执行顺序：

```ts
// order.ts —— 预测输出后再运行
console.log("1: 同步代码");

setTimeout(() => console.log("4: setTimeout (timers 阶段)"), 0);
setImmediate(() => console.log("5: setImmediate (check 阶段)"));

queueMicrotask(() => console.log("3: queueMicrotask (微任务)"));
process.nextTick(() => console.log("2: nextTick (插队王)"));

Promise.resolve().then(() => console.log("3.5: Promise.then (微任务)"));
```

输出顺序：同步 → nextTick → 微任务 → timers/check → 下一轮。**`setTimeout(0)` 与 `setImmediate` 在主模块中顺序不确定，但在 I/O 回调内 setImmediate 恒先执行**。

## 🛠️ Promise 与 async/await

### 从回调到 Promise

Node 核心模块提供回调式与 Promise 式两套 API，优先用后者：

```ts
import { readFile } from "node:fs/promises";      // ✅ Promise 版
import { readFile as cbReadFile } from "node:fs"; // ❌ 回调版，仅在流式场景使用

const content = await readFile("config.json", "utf-8");
```

### async/await 的本质

`async` 函数返回 Promise；`await` 暂停当前函数（不阻塞线程），把后续代码变为微任务。

```ts
// 三种错误处理写法，等价且都正确
async function loadUser(id: string) {
  // 1) try/catch
  try {
    return await fetchUser(id);
  } catch (err) {
    throw new Error(`加载用户失败: ${id}`, { cause: err });
  }
}

// 2) 让错误自然向上传播（推荐：无本地处理逻辑时）
async function getUser(id: string) {
  return fetchUser(id);
}
```

### 并发控制：并行 ≠ 串行

```ts
// ❌ 串行：总耗时 = sum(每个请求)
const a = await fetchUser("1");
const b = await fetchUser("2");

// ✅ 并行：总耗时 = max(每个请求)
const [userA, userB] = await Promise.all([
  fetchUser("1"),
  fetchUser("2"),
]);

// ✅ 部分容错：一个失败不影响其他成功的结果
const results = await Promise.allSettled([fetchUser("1"), fetchConfig()]);
const ok = results.filter((r) => r.status === "fulfilled");
```

各静态方法（all/allSettled/any/race）的失败语义详见 [异步 API 全表](../reference/language-concepts/02-async-api.md)。

### 并发上限控制

大量任务全量并行会打爆下游，需要限流：

```ts
// 简单并发池：同时最多 5 个任务
async function mapPool<T, R>(
  items: T[],
  limit: number,
  fn: (item: T) => Promise<R>,
): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let next = 0;

  async function worker() {
    while (next < items.length) {
      const i = next++;
      results[i] = await fn(items[i]!);
    }
  }

  await Promise.all(Array.from({ length: limit }, worker));
  return results;
}

const pages = await mapPool(urls, 5, (u) => fetchPage(u));
// 也可用 p-limit 等成熟库，原理相同
```

## 🛠️ 超时与取消：AbortController

Node 22 中 `AbortController` 是取消异步操作的标准协议，原生 fetch、定时器、事件监听均支持：

```ts
// 模式一：手动取消
const controller = new AbortController();
const resp = await fetch("/api/heavy", { signal: controller.signal });
// 任意时刻: controller.abort() → fetch 抛 AbortError

// 模式二：超时自动取消（最常用）
const resp2 = await fetch("/api/data", { signal: AbortSignal.timeout(3_000) });

// 模式三：组合多个信号——任一触发即取消（定时器也支持 { signal } 取消）
const combined = AbortSignal.any([
  controller.signal,
  AbortSignal.timeout(5_000),
]);
```

给自定义异步函数接入取消协议：

```ts
async function poll(check: () => boolean, signal: AbortSignal): Promise<void> {
  signal.throwIfAborted(); // 若已取消，立即抛出
  while (!check()) {
    await new Promise((r) => setTimeout(r, 1_000, { signal }));
  }
}
```

## 🎨 最佳实践

- ✅ **async 函数内必须处理错误**：要么 try/catch 要么向上抛，禁止吞掉
- ✅ **独立任务用 `Promise.all` 并行**：串行 await 是最常见的性能 bug
- ✅ **所有出站请求加 `AbortSignal.timeout`**：没有超时的请求是事故温床
- ❌ **不要用 `new Promise` 包装已返回 Promise 的函数**（Promise 反模式）
- ❌ **不要在热路径回调里做 CPU 重活**：会阻塞事件循环，超过 ~10ms 的计算考虑 Worker Threads（见 [07-streams-workers](./07-streams-workers.md)）

## ❓ 常见问题

### Q1: `for...of` 里 `await` 数组怎么变成并行？

**A**: 把 `await fn(x)` 收集为 Promise 数组再 `Promise.all`，或用上面的 `mapPool` 限流版本。`for...of + await` 永远是串行。

### Q2: `AbortError` 和普通错误怎么区分？

**A**: `err.name === "AbortError"`（超时场景为 `TimeoutError`）。通常应把取消视为正常流程，不记录为 error 日志。

## 🎯 练习与实践

### 练习一：事件循环推理

**任务要求**:
1. 先手写本文事件循环示例的预期输出
2. 运行验证，逐行解释偏差
3. 把 `setTimeout` 回调里再加一个 `Promise.then`，预测其时机

### 练习二：带取消的轮询器

**挑战任务**:
- 实现 `pollUntil(checkFn, intervalMs, signal)`：按间隔轮询，signal 触发时立即停止
- 再加一个全局超时：`AbortSignal.any` 组合 30s 超时信号

**提示**: `setTimeout` 的第三参可传 `{ signal }`。

---

## 🔗 相关文档

- 📄 **[异步 API 全表](../reference/language-concepts/02-async-api.md)** — Promise 静态方法与定时器字典
- 📄 **[Stream 与 Worker](./07-streams-workers.md)** — CPU 密集任务的出路
- 📄 **[TypeScript 异步模式](../reference/language-concepts/05-typescript-patterns.md)** — 类型安全的异步封装
