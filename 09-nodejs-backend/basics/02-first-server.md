# 第一个 HTTP 服务器

## 先理解，再动手

HTTP 服务注册一个处理函数；每来一个请求，函数根据方法和地址给出响应。启动成功不证明所有路径都符合约定。

**本节自测**：请求根路径、不存在路径与错误方法，查看状态码和响应头。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

JSON 响应有合适的 Content-Type，未知资源返回明确状态，不是一律 200。

</details>

> **文档简介**: 分别用 Node 原生 `http` 模块和 Hono 4 编写第一个 Web 服务器，理解框架封装前后的差异

> **目标读者**: 初学 Node.js 后端的开发者，尤其是从其他语言 Web 框架转来的工程师

> **前置知识**: [环境搭建](./01-environment-setup.md) 已完成，了解 HTTP 请求/响应基本模型

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#http模块` `#Hono` `#HTTP服务器` `#HelloWorld` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- 用原生 `node:http` 模块写出最小可用的 HTTP 服务器
- 理解 Request/Response 回调模型与端口监听
- 用 Hono 4 重写同样的服务，体会框架抽象的价值
- 掌握开发期热重载与基本调试方式

## 🛠️ 步骤一：原生 http 模块

原生 `http` 模块是所有 Node Web 框架的底层。先写一个 15 行的服务器：

```ts
// server-native.ts
import { createServer } from "node:http";

const server = createServer((req, res) => {
  // 每个进来的请求都会触发这个回调
  console.log(`${req.method} ${req.url}`);

  res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify({ message: "Hello, Node.js!" }));
});

const PORT = 3000;
server.listen(PORT, () => {
  console.log(`服务已启动: http://localhost:${PORT}`);
});
```

运行与验证：

```bash
node server-native.ts
curl http://localhost:3000
# {"message":"Hello, Node.js!"}
```

### 关键概念解析

- **回调模型**：`createServer(handler)` 中 handler 对每个请求执行一次，Node 靠事件循环并发处理成千上万连接（原理见 [04-async-promises](./04-async-promises.md)）
- **`res.writeHead` + `res.end`**：写状态码/响应头，然后结束响应体；忘记 `end` 浏览器会一直挂起
- **没有路由**：所有路径都进同一个回调——这就是原生模块的直接体验

### 原生模块处理路由的痛苦

```ts
// 试着区分路径和查询参数
import { createServer } from "node:http";

const server = createServer((req, res) => {
  const url = new URL(req.url ?? "/", `http://${req.headers.host}`);

  if (url.pathname === "/hello" && req.method === "GET") {
    const name = url.searchParams.get("name") ?? "world";
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({ greeting: `你好, ${name}` }));
    return;
  }

  res.writeHead(404, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify({ error: "Not Found" }));
});

server.listen(3000);
```

能跑，但路径多了之后 if-else 会失控，且没有中间件、错误兜底、参数解析。这正是框架要解决的问题。

## 🛠️ 步骤二：Hono 4 版本

```bash
pnpm add hono @hono/node-server
```

```ts
// server-hono.ts
import { Hono } from "hono";
import { serve } from "@hono/node-server";

const app = new Hono();

// 路由：方法 + 路径 + 处理器（返回 Response）
app.get("/hello", (c) => {
  const name = c.req.query("name") ?? "world";
  return c.json({ greeting: `你好, ${name}` });
});

app.get("/", (c) => {
  return c.json({ message: "Hello, Node.js!" });
});

const PORT = Number(process.env.PORT) || 3000;
serve({ fetch: app.fetch, port: PORT }, (info) => {
  console.log(`服务已启动: http://localhost:${info.port}`);
});
```

```bash
node --watch server-hono.ts
curl "http://localhost:3000/hello?name=Node"
# {"greeting":"你好, Node"}
```

### 框架带来了什么

| 能力 | 原生 http | Hono 4 |
|------|-----------|--------|
| 路由匹配 | 手写 if-else | `app.get("/users/:id")` 模式匹配 |
| 请求体解析 | 手动收集 chunk + JSON.parse | `await c.req.json()` 内建 |
| 中间件链 | 自己实现 | `app.use` 洋葱模型 |
| 错误处理 | try/catch 到处写 | `app.onError` 集中处理 |
| 响应工具 | writeHead/end | `c.json()` `c.text()` 直接返回 |
| 请求注入测试 | 手写构造 | `app.request()` 内置 |

注意请求体解析是**内建**的——Hono 不需要像老框架那样先挂一个 `json()` 中间件，处理器里 `await c.req.json()` 即得。

## 🔍 Hono 值得知道的特性

- **运行时无关**：app 基于 Web 标准 API（Request/Response），同一段代码可跑 Node、Bun、Deno、Cloudflare Workers——换运行时只改 `@hono/node-server` 这一层
- **处理器返回值即响应**：`return c.json(data, 201)`，第二参就是状态码，没有 `.status()` 链
- **零依赖中间件生态**：`hono/cors`、`hono/logger`、`hono/jwt`、`hono/secure-headers` 全部内置（清单见 [Hono 核心速查](../reference/framework-essentials/01-hono-essentials.md)）
- **自带测试客户端**：`await app.request("/hello")` 直接拿到 Response，不需要第三方 HTTP 测试库

## 💻 改造练习代码：带优雅退出

```ts
// server-hono.ts 最终版
import { Hono } from "hono";
import { serve } from "@hono/node-server";

const app = new Hono();
app.get("/", (c) => c.json({ ok: true }));

const server = serve({ fetch: app.fetch, port: 3000 }, () => {
  console.log("listening on :3000");
});

// 优雅退出：收到信号先停止接收新请求，再处理存量请求
process.on("SIGTERM", () => {
  server.close(() => {
    console.log("服务已优雅退出");
    process.exit(0);
  });
});
```

`serve()` 返回的就是 Node 原生 `http.Server` 实例——`server.close()`、`server.on()` 等 API 与原生模块完全一致。

## 🎨 最佳实践

服务器启动时解析并校验端口等配置，给出缺失或非法值的明确错误。开发监听用于缩短反馈，生产由部署平台或监督器管理进程生命周期；重点是退出、重启和日志行为，而不是禁止命令本身。

关闭时先停止接收新请求，再等待在途工作并设置最长等待时间，最后释放资源。请求处理中的长同步计算会阻塞事件循环，用一个慢请求和一个轻请求同时测试即可观察影响。

## ❓ 常见问题

### Q1: `EADDRINUSE: address already in use :3000`？

**A**: 端口被占用。`lsof -i :3000`（macOS/Linux）找到进程并结束，或换端口 `PORT=3001 node server-hono.ts`。

### Q2: curl 请求 404，但路径明明写对了？

**A**: 检查请求方法是否匹配（GET vs POST）；子应用挂载前缀重复（`/users` 里又写了 `/users/:id`）也会导致路径对不上。

## 🎯 练习与实践

### 练习一：原生 vs 框架

**任务要求**:
1. 实现原生版本 `/time` 接口，返回当前 ISO 时间
2. 在 Hono 版本中复刻同样功能
3. 对比两份代码行数与可读性，写下 3 条观察

### 练习二：迷你路由器

**挑战任务**:
- 在原生 http 版本上实现一个支持 `/users/:id` 的极简路由函数（约 20 行）
- 思考：参数解析、404 兜底、嵌套路由分别如何处理？

**提示**: 可用 `URLPattern` 或正则提取路径参数。

---

## 🔗 相关文档

- 📄 **[路由与中间件](./05-http-routing.md)** — 深入 Hono 路由与中间件模式
- 📄 **[错误处理](./06-error-handling.md)** — 给服务器加上集中式错误兜底
- 📄 **[Hono 4 核心速查](../reference/framework-essentials/01-hono-essentials.md)** — API 字典式参考


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
