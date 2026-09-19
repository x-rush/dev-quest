# 全局对象速查

> **文档简介**: Node 24 无需 import 即可使用的全局成员字典——globalThis、console 全方法、structuredClone、定时器、atob/btoa、fetch 家族与 Web 标准全局，附 process 对象索引

> **目标读者**: 需要判断"这个 API 是不是全局、要不要 import"的开发者

> **前置知识**: [Node 核心模块 API 速查](./03-node-core-api.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐ |
| **标签** | `#globalThis` `#console` `#fetch` `#structuredClone` `#定时器` |
| **更新日期** | `2026年9月` |

</details>

## 1. 全局成员总表

### 定义
Node 24 已把大量 Web 标准 API 提升为全局（对标浏览器环境），加上 Node 特有的 process/console/Buffer，绝大多数日常调用无需 import。

### 总表

| 全局成员 | 用途 | 备注 |
|---------|------|------|
| `globalThis` | 标准的"全局对象"访问入口 | 与 Node 的 `global` 同一对象 |
| `console` | 标准输出/诊断 | 方法见第 2 节 |
| `setTimeout` / `setInterval` / `setImmediate` | 定时器 | 返回对象带 `ref()/unref()` |
| `queueMicrotask` | 微任务调度 | 语义见 [异步 API 全表](./02-async-api.md) |
| `structuredClone` | 结构化深拷贝 | 见第 3 节 |
| `fetch` / `Headers` / `Request` / `Response` | HTTP 客户端（undici） | Node 18+ 全局，见第 5 节 |
| `AbortController` / `AbortSignal` | 取消协议 | 见 [异步 API 全表](./02-async-api.md) |
| `crypto`（WebCrypto） | `crypto.randomUUID()`、`getRandomValues` | 注意与 `node:crypto` 是两套 |
| `atob` / `btoa` | Base64 编解码 | Latin1 字节字符串范围，见第 4 节 |
| `Buffer` | 二进制数据 | Node 特有，见 [Buffer 速查](../library-guides/05-buffer.md) |
| `process` | 进程信息与控制 | 详见 [核心模块速查](./03-node-core-api.md) 第 4 节 |
| `TextEncoder` / `TextDecoder` | UTF-8 与字节互转 | |
| `URL` / `URLSearchParams` / `URLPattern` | URL 解析 | |
| `Blob` / `File` / `FormData` | Web 二进制/表单类型 | |
| `performance` | 高精度计时 | `performance.now()` |
| `navigator` / `WebSocket` | 环境探测 / WebSocket 客户端 | Node 21+ |

## 2. console 全方法

### 定义
输出到 stdout/stderr 的诊断工具集；输出目标可用 `new Console({ stdout, stderr })` 重定向（如写日志文件）。

### 方法表

```ts
console.log/info/warn/error("msg", obj);  // error/warn 走 stderr
console.dir(obj, { depth: 4 });           // 以 util.inspect 格式化，可控深度
console.table([{ a: 1 }, { a: 2 }]);      // 表格输出数组/对象
console.time("db");  console.timeEnd("db");   // 计时：db: 12.345ms
console.count("hit");  console.countReset("hit");  // 计数器
console.group("组");  console.groupEnd(); // 缩进分组
console.trace("标记");                     // 打印到当前位置的调用栈
console.assert(cond, "失败信息");          // cond 为假才输出（不抛错）
```

### 陷阱
- ❌ 生产环境留大量 `console.log`——写入的同步或异步行为依平台与输出目标而异，高频输出可能影响事件循环
- ✅ 服务端日志用 pino 等异步日志库；`console.*` 留给 CLI 与排障

## 3. structuredClone 与 queueMicrotask

### 定义
`structuredClone(value)` 按结构化克隆算法深拷贝（浏览器同源算法），循环引用、Date、Map、Set、TypedArray 都能正确拷贝。

```ts
const src = { d: new Date(0), m: new Map([[1, "a"]]), self: null };
src.self = src;
const copy = structuredClone(src);
copy.d instanceof Date;   // true（不再是字符串/普通对象）
copy.self === copy;       // true（循环引用保持）

structuredClone(() => {});      // DOMException: 数据不可克隆（函数）
structuredClone(Symbol("x"));   // DOMException: Symbol 不可克隆
```

- 与 `JSON.parse(JSON.stringify(x))` 的区别：不丢 Date/Map/Set 类型、支持循环引用、不会把 undefined 键悄悄丢掉
- 不能克隆函数与 DOM 类对象；深拷贝带函数的对象需自行实现或用 deep clone 库
- `queueMicrotask(fn)` 把 fn 排入微任务队列（与 Promise 回调进入微任务队列；和 nextTick 的顺序需要区分 CJS/ESM 及调度上下文），业务代码极少需要

## 4. 定时器与 atob/btoa

### 定义
全局定时器返回 **Timeout 对象**（不是浏览器里的数字 ID），可用其实例方法控制事件循环引用计数。

```ts
const t = setTimeout(fn, 1_000);
t.ref();      // 默认：阻止进程退出
t.unref();    // 不阻止退出（心跳、缓存清理类任务常用）
t.refresh();  // 重置为完整时长（实现防抖很方便）

setInterval(fn, ms);          // 间隔调度，阻塞会推迟触发；async 回调若未完成，下一次触发可能产生重叠任务
setImmediate(fn);             // check 阶段执行，晚于微任务
```

```ts
btoa("hi");                   // "aGk="：仅 Latin1 范围
btoa("你好");                 // ❌ DOMException：InvalidCharacterError
Buffer.from("你好").toString("base64");        // "5L2g5aW9" ✅
Buffer.from("5L2g5aW9", "base64").toString();  // "你好" ✅
```

### 陷阱
- ❌ 用 `btoa` 编码含中文的字符串——直接抛错（它只接受 Latin1）
- ✅ UTF-8 安全的 Base64 一律走 `Buffer`（或先 `TextEncoder` 成字节再交给 WebCrypto）
- 未 `unref()` 的定时器会让脚本"挂住不退出"，后台任务记得 unref 或 clear

## 5. fetch / Headers / Request / Response

### 定义
Node 18 起内置的 Web 标准 fetch 全家桶（undici 实现），出站请求不再需要 axios/node-fetch；`Response`/`Request` 对象在服务端同样可用（Hono 等 Web 标准框架的基石）。

```ts
const res = await fetch("https://example.com/api", {
  method: "POST",
  headers: new Headers({ "content-type": "application/json" }),
  body: JSON.stringify({ a: 1 }),
  signal: AbortSignal.timeout(5_000),     // 内建超时
});
res.ok;                  // status 200-299
await res.json();        // 只能读一次 body
res.status; res.headers.get("x-a");

// 服务端构造响应（框架无关的返回值）
const r = new Response(JSON.stringify({ ok: true }), {
  headers: { "content-type": "application/json" },
});
await r.json();
```

### 陷阱
- `fetch` **不会因 4xx/5xx 抛错**，只有网络层失败才 reject——先查 `res.ok`
- body（`json()/text()`）是流，**只能消费一次**，要复用先 `res.clone()`
- 默认无超时，生产必配 `AbortSignal.timeout()` 或自管取消

<!-- full-library-explanation -->
## Web 风格 API 不代表浏览器运行环境

前置是 HTTP、Promise 与流。Node 提供 fetch、URL 和 AbortController，方便共享部分 Web API 使用方式，但没有浏览器页面的默认来源和完整 DOM。相对 URL 需要明确基址，Cookie 管理、代理、证书和权限边界也要按服务端环境设计。用户提供 URL 时还必须考虑能否访问内部地址，不能因为 fetch 可用就直接做代理。

取消是协作协议，AbortController 只通知支持该 signal 的操作；不能自动停止任意 Promise、撤销已完成的写入或清除自建定时器。Response body 只能消费一次，clone 会为两个消费者分流数据，某个消费者太慢时可能带来额外缓冲，不是免费的任意次数重读。

下面的程序只使用本地 Response，不发出网络请求；保存为 `globals-lab.mjs` 后运行 `node globals-lab.mjs`。它证明 body 的单次消费限制，以及 clone 必须发生在第一次消费之前：

<!-- node-python-p1-final-case: node-globals-response-contracts -->
```js
const response = new Response(JSON.stringify({ ok: true }));
const copy = response.clone();
const first = await response.json();
const second = await copy.json();

let consumedTwice = false;
try {
  await response.text();
} catch (error) {
  consumedTwice = error instanceof TypeError;
}

if (!first.ok || !second.ok || !consumedTwice) {
  throw new Error('Response body contract was not met');
}
console.log('globals-response: clone reads twice; original body locks after read');
```

预期输出 `globals-response: clone reads twice; original body locks after read`。再用 structuredClone 复制带 Date、Map、循环引用的对象，与 JSON 往返比较；函数不可克隆，类实例的自定义原型与私有状态也不能假定完整保留。console.assert 仅输出诊断，不应代替 node:assert 在测试中触发失败。

## 🔗 相关文档

- 📄 **[Node 核心模块 API 速查](./03-node-core-api.md)** — `process`、`fs`、`path` 等模块级 API 细节
- 📄 **[异步 API 全表](./02-async-api.md)** — 定时器、微任务与 AbortSignal 深入语义
- 📄 **[内置模块导航表](../library-guides/01-core-modules.md)** — 判断"该 import 什么"
- 🌐 **[Node.js 官方文档: Globals](https://nodejs.org/docs/latest/api/globals.html)** — 全局成员权威清单

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
