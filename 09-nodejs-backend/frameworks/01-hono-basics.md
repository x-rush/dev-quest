# Hono 4 快速上手：路由、中间件与请求响应处理

## 先看框架承担哪部分职责

**Hono 入门**：Hono 面向 Request/Response 契约组织路由与中间件，具体监听端口由运行时适配层承担。框架对象与网络服务器不是同一个职责。

**最小练习与预期结果**：只用一条 GET 与一条 POST 验证 JSON、状态码与错误输入；然后解释适配器如何让请求进入 app。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 以任务为导向掌握 Hono 4 的三大核心——子应用路由拆分、中间件链与请求/响应处理，读完即可独立搭建结构清晰的 REST API 服务
>
> **目标读者**: 已完成 basics 学习路径、准备用 Hono 编写真实后端服务的初级后端开发者
>
> **前置知识**: Node.js 基础、TypeScript 基本语法、HTTP 协议常识

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#hono` `#routing` `#middleware` `#rest-api` |
| **更新日期** | `2026年9月` |

</details>

> Hono 的完整 API 字典（Context 方法、内置中间件清单、路径语法）见 [`../reference/framework-essentials/01-hono-essentials.md`](../reference/framework-essentials/01-hono-essentials.md)，本文只讲"怎么用"。

## 🎯 本节目标

- 用子应用（`new Hono()` + `route`）把 API 按资源拆成模块化路由文件
- 编写并按正确顺序编排自定义中间件，理解洋葱模型
- 规范地读取 params/query/body，返回一致的 JSON 响应

## 1. 初始化一个 Hono 4 + TypeScript 项目

```bash
mkdir todo-api && cd todo-api
pnpm init && pnpm add hono @hono/node-server
pnpm add -D typescript tsx @types/node
pnpm exec tsc --init --module nodenext --moduleResolution nodenext \
  --outDir dist --strict --esModuleInterop --skipLibCheck
```

注意两件事：Hono 自带完整 TypeScript 类型，**不需要** `@types/*` 包；它跑在 Node 上靠的是官方适配器 `@hono/node-server`。

最小入口 `src/app.ts`——**应用实例与服务器启动分离**，方便后续集成测试直接导入 app：

```typescript
// src/app.ts —— 只组装中间件与路由，不监听端口
import { Hono } from 'hono';

const app = new Hono();

// 健康检查：最简单的路由处理器
app.get('/health', (c) => {
  return c.json({ status: 'ok', uptime: process.uptime() });
});

export default app;
```

```typescript
// src/server.ts —— 负责启动与监听（node-server 适配器）
import { serve } from '@hono/node-server';
import app from './app.js';

const PORT = Number(process.env.PORT ?? 3000);
serve({ fetch: app.fetch, port: PORT }, (info) => {
  console.log(`Server listening on http://localhost:${info.port}`);
});
```

`app.fetch` 是 Hono 暴露的 Web 标准 fetch 处理函数——**应用本身与运行时无关**，同一份 app 代码可以跑在 Node、Bun、Deno、Cloudflare Workers 上，换运行时只改适配器这一行。

## 2. 模块化路由：用子应用按资源拆分

Hono 没有 Express 式的 `Router` 构造器——**每个路由模块就是一个 `Hono` 实例**，用 `app.route()` 挂载到主应用：

```typescript
// src/routes/users.ts —— 用户资源子应用
import { Hono } from 'hono';

const usersApp = new Hono(); // 独立的"路由子模块"，可独立挂载与测试

// 挂载在 /users 前缀下时，此处路径不需要重复写 /users
usersApp.get('/', (c) => {
  return c.json({ items: [], page: 1 }); // 实际项目从数据库查询
});

// 命名参数写作 :id，读取用 c.req.param('id')
usersApp.get('/:id', (c) => {
  const id = c.req.param('id');
  return c.json({ id, name: '示例用户' });
});

usersApp.post('/', async (c) => {
  const body = await c.req.json(); // 解析 JSON 请求体
  return c.json(body, 201);        // 创建成功返回 201
});

export default usersApp;
```

```typescript
// src/app.ts 中挂载
import usersApp from './routes/users.js';
app.route('/users', usersApp); // 所有 /users/* 请求进入该子应用
```

一个应用可以任意层级嵌套：子应用还能继续 `route()` 孙应用。若想让子应用"自带前缀"（单独导出时路径完整），用 `usersApp.basePath('/users')`。

## 3. 中间件：编写、挂载顺序与洋葱模型

中间件是 Hono 的骨架——签名 `(c, next)`，按**注册顺序**执行。与 Express 的线性管道不同，Hono 中间件是**洋葱模型**：`await next()` 之前的代码在"进入"阶段执行，之后的代码在"响应返回"阶段执行。

```typescript
// src/middleware/logger.ts —— 请求日志中间件
import type { MiddlewareHandler } from 'hono';

export const requestLogger: MiddlewareHandler = async (c, next) => {
  const start = performance.now();

  await next(); // 不调用 next，请求会悬挂——最常见的初学者事故

  // next() 之后的代码拿到的是"响应已生成"的状态
  const ms = (performance.now() - start).toFixed(1);
  console.log(`${c.req.method} ${c.req.path} ${c.res.status} ${ms}ms`);
};
```

```typescript
// src/app.ts —— 顺序即语义：通用中间件在前，路由在后
import { logger } from 'hono/logger';
import { cors } from 'hono/cors';
import requestLogger from './middleware/logger.js';

app.use(requestLogger);              // 1. 自定义：记录所有请求
app.use(logger());                   // 2. 内置：开发期请求日志
app.use('/api/*', cors());           // 3. 内置：CORS（可按路径作用域）
app.route('/users', usersApp);       // 4. 业务路由
```

**排序口诀**：解析与横切（body-limit/CORS/日志）→ 认证 → 业务路由 → `notFound` → `onError`。错误处理在 Hono 中不是"四参中间件"而是 `app.onError`，无需排在链尾（详见 [Hono 进阶](02-hono-advanced.md)）。

## 4. 请求与响应处理规范

```typescript
// 组合使用 params / query / body 的典型处理器
usersApp.get('/search', async (c) => {
  // query 参数都是 string | undefined，需要显式转换与默认值
  const page = Math.max(1, Number(c.req.query('page') ?? 1));
  const keyword = c.req.query('keyword') ?? '';

  return c.json({ page, keyword, items: [] });
});
```

`c.json()` 第二参直接传状态码，无需链式 `.status()`：

```typescript
return c.json(data, 200);   // 默认 200
return c.json({ id }, 201);
return c.text('pong', 200); // 纯文本
return c.html('<h1>ok</h1>');
return c.body(null, 204);   // 无响应体
return c.redirect('/new-path', 301);
```

推荐给响应定义统一信封，前端处理起来一致：

```typescript
// src/lib/respond.ts —— 统一响应信封助手
import type { Context } from 'hono';
import type { ContentfulStatusCode } from 'hono/utils/http-status';

export function ok<T>(c: Context, data: T, status: ContentfulStatusCode = 200) {
  return c.json({ success: true, data }, status);
}

export function fail(c: Context, message: string, status: ContentfulStatusCode = 400) {
  return c.json({ success: false, error: message }, status);
}
```

`ContentfulStatusCode` 表达“允许带响应体的状态码”。它能避免把任意 `number` 传给 Hono 的重载签名；204 则应走 `c.body(null, 204)`，不要套 JSON 信封。分页参数也要验证是有限正整数并设上限，`Number()` 本身不执行这些业务检查。

## ✅ 最佳实践与陷阱

app 与运行适配器分开，路由测试可以直接调用请求入口；依赖 Node 特有资源的功能仍需相应运行环境测试，不能声称业务永远只依赖框架主包。

中间件应明确选择继续执行并等待 next，或直接返回响应。需要观察最终响应的逻辑放在下游完成后，设置某些响应头则可以按框架约定提前声明，不是所有修改都只能在 next 之后。通过日志记录前后顺序并测试提前拒绝分支。

## 🔗 相关文档

- 📖 [Hono 核心速查](../reference/framework-essentials/01-hono-essentials.md) — Context/中间件/内置生态全量字典
- 📄 [第一个 HTTP 服务器](../basics/02-first-server.md) — 原生 http 与 Hono 的对照入门
- 📄 [路由、中间件与请求校验](../basics/05-http-routing.md) — basics 层面的渐进教程
- 📄 [Hono 进阶：错误处理、认证与文件上传](02-hono-advanced.md) — 本文的进阶续篇


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
