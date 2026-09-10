# Express 5 快速上手：路由、中间件与请求响应处理

> **文档简介**: 以任务为导向掌握 Express 5 的三大核心——模块化路由、中间件链与请求/响应处理，读完即可独立搭建结构清晰的 REST API 服务
>
> **目标读者**: 已完成 basics 学习路径、准备用 Express 5 编写真实后端服务的初级后端开发者
>
> **前置知识**: Node.js 基础、TypeScript 基本语法、HTTP 协议常识

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#express` `#routing` `#middleware` `#rest-api` |
| **更新日期** | `2026年9月` |

> Express 5 的完整 API 字典（路由方法、`req`/`res` 属性、v4 → v5 迁移差异）见 [`../reference/framework-essentials/01-express-essentials.md`](../reference/framework-essentials/01-express-essentials.md)，本文只讲"怎么用"。

## 🎯 本节目标

- 用 `Router` 把 API 按资源拆成模块化路由文件
- 编写并按正确顺序编排自定义中间件
- 规范地读取 params/query/body，返回一致的 JSON 响应

## 1. 初始化一个 Express 5 + TypeScript 项目

```bash
mkdir todo-api && cd todo-api
pnpm init && pnpm add express && pnpm add -D typescript tsx @types/express @types/node
pnpm exec tsc --init --module nodenext --moduleResolution nodenext \
  --outDir dist --strict --esModuleInterop --skipLibCheck
```

最小入口 `src/app.ts`——**应用实例与服务器启动分离**，方便后续集成测试直接导入 app：

```typescript
// src/app.ts —— 只组装中间件与路由，不监听端口
import express from 'express';

const app = express();

// 内置中间件：解析 JSON 请求体（Express 5 默认基于 http-errors 抛 400）
app.use(express.json());

// 健康检查：最简单的路由处理器
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

export default app;
```

```typescript
// src/server.ts —— 负责启动与监听
import app from './app.js';

const PORT = Number(process.env.PORT ?? 3000);
app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
```

## 2. 模块化路由：用 Router 按资源拆分

把每个资源的路由收敛到独立文件，避免 `app.ts` 膨胀：

```typescript
// src/routes/users.ts —— 用户资源路由
import { Router } from 'express';
import type { Request, Response } from 'express';

const router = Router(); // 独立的"路由子模块"，可独立挂载与测试

// 挂载在 /users 前缀下时，此处路径不需要重复写 /users
router.get('/', (req: Request, res: Response) => {
  res.json({ items: [], page: 1 }); // 实际项目从数据库查询
});

// Express 5 使用 path-to-regexp v8：命名参数写作 :id，
// 且 * 通配符必须具名（/*splat），裸 * 已不合法
router.get('/:id', (req, res) => {
  const { id } = req.params;
  res.json({ id, name: '示例用户' });
});

router.post('/', (req, res) => {
  res.status(201).json(req.body); // 创建成功返回 201
});

export default router;
```

```typescript
// src/app.ts 中挂载
import usersRouter from './routes/users.js';
app.use('/users', usersRouter); // 所有 /users/* 请求进入该子路由
```

## 3. 中间件：编写、挂载顺序与职责

中间件是 Express 的骨架——`(req, res, next)` 三元组，按**注册顺序**执行。

```typescript
// src/middleware/logger.ts —— 请求日志中间件
import type { Request, Response, NextFunction } from 'express';

export function requestLogger(req: Request, res: Response, next: NextFunction) {
  const start = performance.now();

  res.on('finish', () => {
    // 'finish' 事件在响应发出后触发，此时才能拿到真实状态码
    const ms = (performance.now() - start).toFixed(1);
    console.log(`${req.method} ${req.originalUrl} ${res.statusCode} ${ms}ms`);
  });

  next(); // 不调用 next 请求会永久挂起——最常见的初学者事故
}
```

```typescript
// src/app.ts —— 顺序即语义：全局中间件在前，路由在后，兜底错误处理在最后
import requestLogger from './middleware/logger.js';

app.use(requestLogger);         // 1. 记录所有请求
app.use(express.json());        // 2. 解析请求体
app.use('/users', usersRouter); // 3. 业务路由
```

**排序口诀**：解析类（json/cookie）→ 通用横切（日志/CORS）→ 认证 → 业务路由 → 404 → 错误处理。

## 4. 请求与响应处理规范

```typescript
// 组合使用 params / query / body 的典型处理器
router.get('/search', async (req, res) => {
  // query 参数都是 string | undefined，需要显式转换与默认值
  const page = Math.max(1, Number(req.query.page ?? 1));
  const keyword = String(req.query.keyword ?? '');

  res.status(200).json({ page, keyword, items: [] });
});
```

推荐给响应定义统一信封，前端处理起来一致：

```typescript
// src/lib/respond.ts —— 统一响应信封助手
import type { Response } from 'express';

export function ok(res: Response, data: unknown, status = 200) {
  res.status(status).json({ success: true, data });
}

export function fail(res: Response, message: string, status = 400) {
  res.status(status).json({ success: false, error: message });
}
```

## ✅ 最佳实践与陷阱

- ✅ app 与 server 分离文件，测试可 `import app` 而不占端口
- ✅ 路由文件只做"接请求、调服务、返响应"，业务逻辑下沉到 service 层（见 [`../advanced-topics/architecture/01-service-architecture.md`](../advanced-topics/architecture/01-service-architecture.md)）
- ❌ 中间件里忘记 `next()` 导致请求悬挂
- ❌ 在 v5 中使用裸 `*` 通配符或不合法的正则路径——启动即抛错（详见字典"陷阱"小节）

## 🔗 相关文档

- 📖 [Express 5 核心速查](../reference/framework-essentials/01-express-essentials.md) — 路由/中间件/req·res 全量字典
- 📄 [第一个 HTTP 服务器](../basics/02-first-server.md) — 原生 http 与 Express 的对照入门
- 📄 [路由、中间件与请求校验](../basics/05-http-routing.md) — basics 层面的渐进教程
- 📄 [Express 进阶：错误处理、认证与文件上传](02-express-advanced.md) — 本文的进阶续篇
