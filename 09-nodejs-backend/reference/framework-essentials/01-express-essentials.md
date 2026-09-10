# Express 5 核心速查

> **文档简介**: Express 5 的路由、中间件、请求/响应对象与错误处理的条目式速查，含 v4 → v5 迁移差异

> **目标读者**: 使用或迁移到 Express 5 的开发者

> **前置知识**: [第一个服务器](../../basics/02-first-server.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐ |
| **标签** | `#Express5` `#路由` `#中间件` `#迁移` |
| **更新日期** | `2026年9月` |

## 1. 应用与路由方法

### 定义
`app` 与 `Router` 共享同一套路由注册 API；Router 是可挂载的迷你 app。

### 语法与示例

```ts
import express, { Router } from "express";

const app = express();
const r = Router();

r.route("/items")          // 同一路径集中声明多方法
  .get(listItems)
  .post(createItem);

r.all("/log", handler);    // 匹配所有 HTTP 方法

app.use("/api/v1", r);     // 挂载：/api/v1/items
```

### Express 5 路径语法（path-to-regexp v8）

```ts
app.get("/users/:id");          // ✅ 参数（不变）
app.get("/file/:name.png");     // ✅ 参数 + 后缀
app.get("/{*splat}");           // ✅ 通配符（新语法）
app.get("*");                   // ❌ v5 报错
app.get("/posts?");             // ❌ v5 移除 ? 可选修饰
```

### 陷阱
- v5 中 `:id?` 可选参数写法变化，改用 `{id}` 或分开注册两条路由
- 通配符必须命名：`{*path}` 而不是裸 `*`

## 2. 中间件注册

### 定义
`app.use` 注册到所有方法/路径；`app.METHOD(path, ...mw, handler)` 注册到特定路由，可堆叠多个中间件。

### 语法与示例

```ts
// 全局
app.use(express.json());                          // 解析 application/json

// 路径前缀 + 多中间件
app.use("/admin", requireAuth, requireRole("admin"), adminLog);

// 路由级堆叠
app.post("/upload", requireAuth, uploadLimiter, uploadHandler);

// 错误中间件（4 参签名，最后注册）
app.use((err, req, res, _next) => { /* ... */ });
```

### 陷阱
- **顺序即语义**：`express.json()` 必须在读 body 的逻辑之前；错误中间件必须最后
- 中间件不调 `next()` 也不结束响应 = 请求悬挂到超时
- `express.static` 需绝对路径：`express.static(path.resolve("public"))`

## 3. Request 对象

### 定义
请求的封装，本节列出后端最常读的属性。

### 语法与示例

```ts
req.params.id;               // 路径参数（string）
req.query.page;              // 查询参数（string | string[] | ParsedQs…）
req.body;                    // 经 json/urlencoded 解析后的请求体
req.headers["content-type"]; // 全小写的头部名
req.method; req.url; req.originalUrl;
req.ip;                      // 客户端 IP（信任代理见下）
req.cookies;                 // 需 cookie-parser 中间件
req.fresh; req.stale;        // 缓存协商（ETag/If-None-Match）
```

### 陷阱
- `req.query` 类型全是 string 或数组，数字比较前必须转换（或 Zod `z.coerce`）
- 反向代理后 `req.ip` 是代理 IP：`app.set("trust proxy", 1)` 才拿真实客户端

## 4. Response 对象

### 定义
响应构建 API，多数方法返回 `res` 本身可链式。

### 语法与示例

```ts
res.status(201).json(data);          // 设置状态 + JSON（自动 Content-Type）
res.sendStatus(204);                 // 状态码 + 标准文案，结束响应
res.set("Cache-Control", "no-store");

res.redirect(301, "/new-path");
res.download("/files/report.pdf");          // 附件下载
res.sendFile(path.resolve("a.png"));        // 发送文件（流式，需绝对路径）

res.cookie("token", jwt, { httpOnly: true, secure: true, sameSite: "strict", maxAge: 7 * 864e5 });
res.clearCookie("token");

res.format({ json: () => res.json(data), text: () => res.send(textView(data)) }); // 内容协商

res.on("finish", () => logAccess());       // 响应发送完毕（日志场景）
```

### 陷阱
- 一个响应只能 `send/json/end` 一次，二次调用报 `ERR_HTTP_HEADERS_SENT`——分支逻辑记得 `return`
- `res.sendFile` 用相对路径会相对进程 cwd，必须传绝对路径

## 5. 错误处理

### 定义
四参数中间件集中处理所有 `next(err)` 与 async 处理器抛出的错误（v5 原生自动转发 rejection，v4 需手写 `.catch(next)` 或包装器；升级后不要再保留 `express-async-errors` 类补丁）。

### 语法与示例

```ts
import type { ErrorRequestHandler } from "express";

const errorHandler: ErrorRequestHandler = (err, req, res, _next) => {
  if (err instanceof HttpError) {
    res.status(err.status).json({ error: { code: err.code, message: err.message } });
    return;
  }
  if (err instanceof z.ZodError) {
    res.status(400).json({ error: { code: "VALIDATION_ERROR", issues: err.issues } });
    return;
  }
  req.log?.error({ err });
  res.status(500).json({ error: { code: "INTERNAL_ERROR" } });
};
```

### 陷阱
- 错误中间件里再抛错会进入 Express 内置兜底，返回 HTML——确保自身逻辑不会 throw

## 6. v4 → v5 迁移清单

| 变更 | v4 | v5 |
|------|----|----|
| 通配符 | `app.get("*")` | `app.get("/{*splat}")` |
| 可选参数 | `/a/:id?` | `/a/{id}` 或拆分路由 |
| 正则路由 | `app.get(/re/)` | 移除 |
| async rejection | 需手动 catch | 自动转发 |
| Node 最低版本 | 0.10+ | 18+ |
| path-to-regexp | v0.x/v6 | v8（语法收紧） |

---

## 🔗 相关文档

- 📄 **[路由与中间件教程](../../basics/05-http-routing.md)** — Router 组织与 Zod 校验实战
- 📄 **[Fastify 与 NestJS 速查](./02-fastify-nestjs.md)** — 替代框架对比
- 📄 **[错误处理教程](../../basics/06-error-handling.md)** — 集中式错误处理设计
