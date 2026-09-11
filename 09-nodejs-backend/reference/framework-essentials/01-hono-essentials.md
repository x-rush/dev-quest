# Hono 4 核心速查

> **文档简介**: Hono 4 的应用、路由、Context 对象、中间件生态与错误处理的条目式速查，含从 Express 迁移的心智模型差异

> **目标读者**: 使用 Hono 开发 Node.js 后端的开发者

> **前置知识**: [第一个服务器](../../basics/02-first-server.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐ |
| **标签** | `#Hono4` `#路由` `#中间件` `#Context` |
| **更新日期** | `2026年9月` |

## 1. 应用与路由方法

### 定义
`Hono` 实例既是应用也是"路由器"：主应用与子应用是同一类型，用 `route()` 组合，天然支持任意层级嵌套。

### 语法与示例

```ts
import { Hono } from "hono";

const app = new Hono();
const users = new Hono();

users.get("/");               // 子应用内路径不带前缀
users.get("/:id");
users.post("/");

app.route("/users", users);   // 挂载：/users、/users/:id
// 或让子应用自带前缀：users.basePath("/users")

app.all("/log", (c) => c.body(null));       // 匹配所有 HTTP 方法
app.on("GET", ["/a", "/b"], handler);       // 多路径精确声明
```

### 路径语法

```ts
app.get("/users/:id");            // ✅ 命名参数
app.get("/posts/:id{[0-9]+}");    // ✅ 带正则约束的参数（非数字不匹配）
app.get("/static/*");             // ✅ 通配符（Hono 原生支持，无需具名）
app.get("/users/:id?");           // ❌ Hono 不支持可选段——拆成两条路由
```

### 陷阱
- 通配符 `*` 与具名参数不能出现在同一段：`/files/*` 与 `/files/:id` 冲突时按注册顺序命中
- 子应用内写死 `/users/:id` 再挂到 `/users` 前缀下，会得到 `/users/users/:id`——前缀只出现在挂载处

## 2. Context：c.req 请求对象

### 定义
处理器与中间件只接触一个 `Context`（`c`）。请求侧全部挂在 `c.req` 上，返回值均为解析后的数据。

### 语法与示例

```ts
c.req.param("id");            // 路径参数（string）；无参调用返回全量对象
c.req.query("page");          // 查询参数（string | undefined）；无参调用返回全量对象
c.req.header("Content-Type"); // 请求头（名字大小写不敏感）
c.req.url;                    // 完整 URL 字符串
c.req.path;                   // 路径部分
c.req.method;

await c.req.json();           // 解析 JSON 请求体
await c.req.text();           // 纯文本请求体
await c.req.arrayBuffer();    // 二进制请求体
await c.req.parseBody();      // multipart/form-data → FormData（文件为 File 实例）
c.req.raw;                    // 底层原生 Request（Web 标准）
c.req.valid("json");          // 经 validator 校验后的类型安全数据
```

### 陷阱
- `param`/`query` 返回的都是 `string`——数字比较前必须显式转换（或用 Zod `z.coerce`）
- `c.req.json()` 在请求体不是合法 JSON 时抛错——交给 `app.onError` 统一兜住，不要裸调不接
- `parseBody()` 只处理 `multipart/form-data`；对 JSON 请求体调用会抛错

## 3. Context：响应构建方法

### 定义
`c.json()/c.text()/c.html()` 等工厂方法返回 `Response`（或作为中间件返回值）。**处理器必须返回响应**——没有 Express 式的 `res.end()` 副作用写法。

### 语法与示例

```ts
c.json(data);                 // 200 JSON，自动 Content-Type
c.json({ id }, 201);          // 第二参即状态码
c.json({ error: "x" }, 404);

c.text("pong");
c.html("<h1>ok</h1>");
c.body(null, 204);            // 自定义响应体
c.body(stream, 200, { "Content-Type": "application/octet-stream" }); // 流式响应

c.redirect("/login", 301);
c.notFound();                 // 返回内置 404 响应

c.res.status;                 // 读取当前响应（中间件在 next() 之后可用）
c.res.headers.set("Cache-Control", "no-store");
```

### 陷阱
- 处理器 `return` 了一个响应后又继续执行代码——响应不会二次生效；分支逻辑记得 `return`
- 在 `await next()` 之前读取/修改 `c.res` 得到的是空响应——改响应头的正确姿势是在 `next()` 之后操作 `c.res.headers`

## 4. 中间件注册

### 定义
`app.use(path?, handler)` 注册中间件，签名 `(c, next)`，洋葱模型：`await next()` 前是"进入"阶段，之后是"响应"阶段。

### 语法与示例

```ts
import type { MiddlewareHandler } from "hono";

// 全局
app.use(requestLogger());

// 路径前缀（* 通配必需）
app.use("/api/*", cors());

// 路由级堆叠
app.post("/upload", requireAuth, uploadLimiter, uploadHandler);

// 自定义中间件：类型标注 MiddlewareHandler
const requestLogger: MiddlewareHandler = async (c, next) => {
  const start = performance.now();
  await next();
  console.log(`${c.req.method} ${c.req.path} ${c.res.status} ${performance.now() - start}ms`);
};
```

### 陷阱
- **顺序即语义**：`bodyLimit` 必须在 `parseBody` 之前；认证在校验之前
- 中间件不 `await next()` 也不返回响应 = 请求悬挂到超时
- 在 `next()` 前抛错会跳过洋葱内侧的中间件——清理逻辑用 `try/finally`

## 5. 内置中间件生态

### 定义
全部来自 `hono/*` 子路径导出，零额外依赖——这是 Hono 相对 Express 最大的工程差异之一。

| 导入 | 用途 | 备注 |
|------|------|------|
| `hono/logger` | 开发期请求日志 | 生产换 pino 等结构化方案 |
| `hono/cors` | CORS 头 | `origin`/`allowMethods`/`credentials` 等 |
| `hono/jwt` | JWT 验签 | payload 自动写入 `c.get("jwtPayload")` |
| `hono/secure-headers` | 安全响应头 | 相当于 helmet 的默认集 |
| `hono/basic-auth`、`hono/bearer-auth` | 基础认证 | 内部工具/快速原型 |
| `hono/body-limit` | 请求体大小上限 | 解析前拦截 |
| `hono/compress` | gzip 压缩 | node-server 下可用 |
| `hono/etag` | ETag 协商 | 自动 304 |
| `hono/timing` | Server-Timing 头 | 性能观测 |
| `hono/cache` | 响应缓存头 | Cache-Control 管理 |
| `hono/cookie` | Cookie 读写 | `setCookie`/`getCookie`/`deleteCookie` |
| `hono/http-exception` | HTTPException | 快速抛带状态码的错误 |

### 语法与示例

```ts
import { cors } from "hono/cors";
import { secureHeaders } from "hono/secure-headers";

app.use(secureHeaders()); // 一次设置 CSP、HSTS 等安全头
app.use("/api/*", cors({
  origin: ["https://app.example.com"],
  allowMethods: ["GET", "POST", "PATCH", "DELETE"],
  credentials: true,
}));
```

### 陷阱
- 第三方中间件（限流、session 等）在 `@hono/*` 或社区包中，选型前确认维护状态
- `cors()` 不传 `origin` 时默认 `*`，且通配与 `credentials: true` 不能同用

## 6. 错误处理

### 定义
`app.onError` 是全站唯一错误出口：任何处理器/中间件 `throw` 的错误（含 async rejection）自动传播至此。`app.notFound` 处理未匹配路由。

### 语法与示例

```ts
import { HTTPException } from "hono/http-exception";

app.onError((err, c) => {
  if (err instanceof HTTPException) {
    return err.getResponse();        // 框架异常直接透出
  }
  if (err instanceof HttpError) {
    return c.json({ error: err.message }, err.status);
  }
  console.error("[unhandled]", err);
  return c.text("Internal Server Error", 500);
});

app.notFound((c) => c.json({ error: "路由不存在" }, 404));
```

### 陷阱
- 没注册 `onError` 时 Hono 返回默认 500 文本——生产项目必须注册并接入日志/Sentry
- `onError` 内部再抛错没有兜底——确保自身逻辑不会 throw

## 7. 测试与 Node 运行

### 定义
`app.request()` 是内置测试客户端：向 app 直接发起模拟请求，返回 Web 标准 `Response`，无需监听端口。生产运行用官方适配器 `@hono/node-server`。

### 语法与示例

```ts
// 测试：GET /health
const res = await app.request("/health");
res.status;                // 200
await res.json();          // 响应体

// 测试：POST JSON
const res = await app.request("/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "x" }),
});

// 生产启动（node-server 适配器）
import { serve } from "@hono/node-server";
const server = serve({ fetch: app.fetch, port: 3000 }); // 返回 node http.Server
server.close();          // 优雅关闭沿用 Node API
```

### 陷阱
- `serve()` 不传对象时也可 `serve(app)`，但需要自定义端口/hostname 时用 `{ fetch, port, hostname }` 形式
- `app.request()` 拿到的 `Response` 是流式 body——`json()` 只能消费一次

## 8. 从 Express 迁移的心智模型差异

| 维度 | Express | Hono 4 |
|------|---------|--------|
| 处理器签名 | `(req, res, next)` | `(c) => Response` |
| 中间件模型 | 线性管道 + 四参错误中间件 | 洋葱模型 + `app.onError` |
| 响应方式 | `res.json()` 副作用 | `return c.json()` 返回值 |
| 路由器 | `Router()` 构造器 | `new Hono()` 子应用 + `route()` |
| 请求体解析 | `express.json()` 中间件 | 内建 `c.req.json()` |
| 类型扩展 | `namespace Express { Request }` | `interface ContextVariableMap` |
| 测试 | supertest（或注入 app） | `app.request()` 内置 |
| 运行时 | Node 专属 | Web 标准 API，跨运行时 |

---

## 🔗 相关文档

- 📄 **[路由与中间件教程](../../basics/05-http-routing.md)** — 子应用组织与 Zod 校验实战
- 📄 **[框架选型对比](./02-fastify-nestjs.md)** — Fastify/NestJS/Express 与 Hono 的定位差异
- 📄 **[错误处理教程](../../basics/06-error-handling.md)** — 集中式错误处理设计
