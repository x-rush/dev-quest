# 第一个 HTTP 服务器

> **文档简介**: 分别用 Node 原生 `http` 模块和 Express 5 编写第一个 Web 服务器，理解框架封装前后的差异

> **目标读者**: 初学 Node.js 后端的开发者，尤其是从其他语言 Web 框架转来的工程师

> **前置知识**: [环境搭建](./01-environment-setup.md) 已完成，了解 HTTP 请求/响应基本模型

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#http模块` `#Express5` `#HTTP服务器` `#HelloWorld` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- 用原生 `node:http` 模块写出最小可用的 HTTP 服务器
- 理解 Request/Response 回调模型与端口监听
- 用 Express 5 重写同样的服务，体会框架抽象的价值
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

## 🛠️ 步骤二：Express 5 版本

```bash
pnpm add express
```

```ts
// server-express.ts
import express from "express";

const app = express();

// 中间件：解析 JSON 请求体（Express 5 内置）
app.use(express.json());

// 路由：方法 + 路径 + 处理函数
app.get("/hello", (req, res) => {
  const name = req.query.name ?? "world";
  res.json({ greeting: `你好, ${name}` });
});

app.get("/", (_req, res) => {
  res.json({ message: "Hello, Node.js!" });
});

const PORT = Number(process.env.PORT) || 3000;
app.listen(PORT, () => {
  console.log(`服务已启动: http://localhost:${PORT}`);
});
```

```bash
node --watch server-express.ts
curl "http://localhost:3000/hello?name=Node"
# {"greeting":"你好, Node"}
```

### 框架带来了什么

| 能力 | 原生 http | Express 5 |
|------|-----------|-----------|
| 路由匹配 | 手写 if-else | `app.get("/users/:id")` 模式匹配 |
| 请求体解析 | 手动收集 chunk + JSON.parse | `express.json()` 一行 |
| 中间件链 | 自己实现 | `app.use` 顺序执行 |
| 错误处理 | try/catch 到处写 | 集中式错误中间件 |
| 响应工具 | writeHead/end | `res.json()` `res.status()` |

## 🔍 Express 5 值得注意的变化

从 Express 4 升级时（以及网上老教程）要留意：

- **Promise 拒绝自动转发**：async 处理函数中 `await` 抛错会自动进入错误中间件，不再需要 `express-async-errors` 或手动 `next(err)`
- **通配符语法变更**：`app.get("*")` 已失效，改用 `app.get("/{*splat}")` 或 `app.use(...)` 兜底
- **移除废弃 API**：`res.sendfile`、`app.del` 等彻底删除
- **路由参数正则更严格**：旧版可选参数写法需逐一核对迁移

## 💻 改造练习代码：带优雅退出

```ts
// server-express.ts 最终版
import express from "express";

const app = express();
app.use(express.json());

app.get("/", (_req, res) => res.json({ ok: true }));

const server = app.listen(3000, () => {
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

## 🎨 最佳实践

- ✅ **开发用 `node --watch`**：Node 22 内置监听，省去 nodemon 依赖
- ✅ **端口从 `process.env.PORT` 读取**：容器与云平台会注入该变量
- ✅ **生产环境绝不裸跑 node**：交给 systemd / 容器编排 / PM2 等进程守护
- ❌ **不要忽略优雅退出**：`server.close` 处理存量连接后才能真正安全下线
- ❌ **不要在请求回调里写同步阻塞代码**（如大文件同步读），会卡住整个事件循环

## ❓ 常见问题

### Q1: `EADDRINUSE: address already in use :3000`？

**A**: 端口被占用。`lsof -i :3000`（macOS/Linux）找到进程并结束，或换端口 `PORT=3001 node server-express.ts`。

### Q2: curl 请求 404，但路径明明写对了？

**A**: 检查请求方法是否匹配（GET vs POST）；Express 5 中通配符写法变化也可能导致旧路由失效。

## 🎯 练习与实践

### 练习一：原生 vs 框架

**任务要求**:
1. 实现原生版本 `/time` 接口，返回当前 ISO 时间
2. 在 Express 版本中复刻同样功能
3. 对比两份代码行数与可读性，写下 3 条观察

### 练习二：迷你路由器

**挑战任务**:
- 在原生 http 版本上实现一个支持 `/users/:id` 的极简路由函数（约 20 行）
- 思考：参数解析、404 兜底、嵌套路由分别如何处理？

**提示**: 可用 `URLPattern` 或正则提取路径参数。

---

## 🔗 相关文档

- 📄 **[路由与中间件](./05-http-routing.md)** — 深入 Express 路由与中间件模式
- 📄 **[错误处理](./06-error-handling.md)** — 给服务器加上集中式错误兜底
- 📄 **[Express 5 核心速查](../reference/framework-essentials/01-express-essentials.md)** — API 字典式参考
