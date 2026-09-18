# 异步编程：事件循环、Promise 与取消

## 先理解，再动手

Promise 表示以后得到的结果，await 暂停当前异步流程。两个独立操作可以重叠等待，但依赖前一步结果的操作必须保持顺序。

**本节自测**：用两个延迟 Promise 比较连续 await 与 Promise.all，并让其中一个失败。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

并发完成更接近较长等待；all 遇到失败会拒绝，但不会自动取消另一个已经启动的操作。

</details>

> **文档简介**: 系统掌握 Node.js 异步模型——事件循环阶段、Promise/async-await、超时与 AbortController 取消模式

> **目标读者**: 有回调/Promise 使用经验但对其原理模糊的开发者

> **前置知识**: [模块系统与 ESM](./03-modules-esm.md)，基本的 JS 函数概念

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#事件循环` `#Promise` `#async-await` `#AbortController` |
| **更新日期** | `2026年9月` |

</details>

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

先分清执行上下文：`process.nextTick` 使用 Node 特有队列，Promise.then 与 queueMicrotask 使用微任务队列。不能背诵“nextTick 永远在 Promise 前面”；ESM 顶层求值与普通 CommonJS 顶层有差别。

完整示例：保存为 `order.cjs`，再把相同内容保存为 `order.mjs`，分别用 `node order.cjs` 与 `node order.mjs` 运行。这里没有 import，所以两种模块格式都合法。

```js
console.log('sync')
process.nextTick(() => console.log('nextTick'))
queueMicrotask(() => console.log('microtask'))
Promise.resolve().then(() => console.log('promise'))
```

在本文所讨论的现代 Node 版本中，CJS 顶层的预期顺序为 sync、nextTick、microtask、promise；ESM 顶层通常为 sync、microtask、promise、nextTick，因为模块求值本身已在异步处理上下文中。不要把任意回调内部的顺序也直接套成这两个列表。官方解释见 [process 队列说明](https://nodejs.org/api/process.html#when-to-use-queuemicrotask-vs-processnexttick)。

setTimeout(0) 表示到期后可被调度，不是立刻执行；与 setImmediate 在主模块中的先后不作为可靠业务约定。任务顺序应通过 await、回调或明确依赖建立。

## 🛠️ Promise 与 async/await

### 从回调到 Promise

Node 核心模块提供回调式与 Promise 式两套 API，优先用后者：

```ts
import { readFile } from "node:fs/promises";      // ✅ Promise 版
// 回调式 readFile 同样是合法选择，但不是流式读取；本课统一使用 Promise 风格。

const content = await readFile("config.json", "utf-8");
```

### async/await 的本质

`async` 函数返回 Promise；`await` 暂停当前函数（不阻塞线程），把后续代码变为微任务。

```ts
// 两种传播策略：有本地上下文时包装错误，否则自然向上传播；fetchUser 由业务工程提供
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

// ✅ 并行：等待可重叠，理想耗时接近最长请求；仍受服务端与连接资源限制
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
  if (!Number.isInteger(limit) || limit < 1) {
    throw new RangeError("limit 必须是正整数");
  }
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

// 接入片段：urls 与 fetchPage 由调用工程提供
const pages = await mapPool(urls, 5, (u) => fetchPage(u));
// 也可用 p-limit 等成熟库，原理相同
```

## 🛠️ 超时与取消：AbortController

Node 24 中 `AbortController` 是取消异步操作的标准协议，原生 fetch、定时器、事件监听均支持：

```ts
// 模式一：手动取消
const controller = new AbortController();
const resp = await fetch("http://localhost:3000/api/heavy", { signal: controller.signal });
// 任意时刻: controller.abort() → fetch 抛 AbortError

// 模式二：超时自动取消（最常用）
const resp2 = await fetch("http://localhost:3000/api/data", { signal: AbortSignal.timeout(3_000) });

// 模式三：组合多个信号——任一触发即取消（node:timers/promises 的 setTimeout 也支持 { signal } 取消）
const combined = AbortSignal.any([
  controller.signal,
  AbortSignal.timeout(5_000),
]);
```

以上是接入已有本地服务的片段，需先启动 localhost:3000 对应接口。Node 中没有浏览器页面地址可供相对 URL 解析。

给自定义异步函数接入取消协议：

```ts
import { setTimeout } from "node:timers/promises"; // 全局 setTimeout 的第三参是传给回调的展开参数，不支持 { signal }

async function poll(check: () => boolean, signal: AbortSignal): Promise<void> {
  signal.throwIfAborted(); // 若已取消，立即抛出
  while (!check()) {
    await setTimeout(1_000, undefined, { signal }); // 取消时以 AbortError 拒绝
  }
}
```

## 🎨 最佳实践

async 函数可以把失败传播给调用方，不需要每一层重复 try/catch；只有能恢复、补充上下文或转换边界语义时再捕获。独立任务可以并发，但仍要控制并发量、超时与取消，Promise.all 拒绝并不会自动取消其他任务。

已经返回 Promise 的函数通常直接 await 即可；回调 API 才可能需要包装。CPU 重活是否交给 worker 由任务成本、传输开销和延迟预算共同决定，不设通用毫秒门槛。

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

**提示**: 用 `node:timers/promises` 的 `setTimeout(delay, value, { signal })`——全局 `setTimeout` 不支持 `{ signal }`。

---

## 🔗 相关文档

- 📄 **[异步 API 全表](../reference/language-concepts/02-async-api.md)** — Promise 静态方法与定时器字典
- 📄 **[Stream 与 Worker](./07-streams-workers.md)** — CPU 密集任务的出路
- 📄 **[TypeScript 异步模式](../reference/language-concepts/05-typescript-patterns.md)** — 类型安全的异步封装


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
