# 第一个完整项目：任务管理 REST API

> **文档简介**: 综合运用前七课知识，从零构建任务管理 REST API——Hono 4 + Prisma + Zod，含分页、校验、错误处理与测试

> **目标读者**: 完成入门路径全部课程的学习者，需要一次"真刀真枪"的综合演练

> **前置知识**: [路由与中间件](./05-http-routing.md)、[错误处理](./06-error-handling.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#REST API` `#Hono` `#Prisma` `#Zod` `#综合项目` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本项目后，你将能够：

- 独立搭建含数据库的分层 Node 后端项目
- 用 Prisma 完成建模、迁移与类型安全查询
- 把校验、错误处理、日志组织成可复用的骨架
- 为 API 编写基于原生 Test Runner 与 `app.request()` 的集成测试

## 📋 项目需求

实现任务管理 API，资源为 Task：

| 方法 | 路径 | 功能 | 成功状态码 |
|------|------|------|-----------|
| GET | `/api/tasks?status=&page=&size=` | 分页筛选列表 | 200 |
| POST | `/api/tasks` | 创建任务 | 201 |
| GET/PATCH/DELETE | `/api/tasks/:id` | 查询/更新/删除 | 200 / 404 / 204 |

字段约束：`title` 1-100 字符；`status` ∈ `todo | doing | done`，默认 `todo`。

> 💡 **渐进路线（可选）**：如果想先跑通路由逻辑，可先用内存数组实现——跳过步骤二，把步骤四中的 `prisma.task.*` 换成对数组变量的 `find/filter/slice` 操作即可，步骤一、三、五、六完全不受影响。等路由、校验、错误处理都绿了，再回来补 Prisma 建模与迁移，把持久化换成真实现。

## 🛠️ 步骤一：初始化与依赖

```bash
pnpm init && pnpm pkg set type=module
pnpm add hono @hono/node-server @prisma/client zod
pnpm add @prisma/adapter-better-sqlite3 better-sqlite3   # Prisma v7：SQLite 经 driver adapter 连接
pnpm add -D prisma typescript @types/node dotenv
```

目录规划：`src/lib/`（prisma 单例、HttpError）、`src/middleware/`（错误出口）、`src/routes/`（按资源拆分子应用）、`test/`。`app.ts` 只装配不监听，`server.ts` 负责监听——测试直接复用 Hono 实例，不占端口。

## 🛠️ 步骤二：数据模型（Prisma）

```bash
pnpm exec prisma init   # 生成 schema 与 prisma7.config.ts 骨架（v7 默认 generator 为 prisma-client）
```

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client"
  output   = "../generated/prisma" // v7：客户端生成到项目目录（TypeScript 源码）
}

datasource db {
  provider = "sqlite"              // 演练用 SQLite，零配置；生产换 postgresql
  // v7 起 schema 不再写连接串——连接配置移到 prisma7.config.ts
}

model Task {
  id        String   @id @default(cuid())
  title     String
  status    String   @default("todo")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  @@map("tasks")
}
```

```ts
// prisma7.config.ts —— v7：CLI 与迁移从这里读取连接配置
import "dotenv/config";
import { defineConfig } from "prisma/config";

export default defineConfig({
  schema: "prisma/schema.prisma",
  migrations: { path: "prisma/migrations" },
  datasource: { url: process.env.DATABASE_URL ?? "file:./prisma/dev.db" },
});
```

```bash
# .env
DATABASE_URL="file:./prisma/dev.db"
```

```bash
pnpm exec prisma migrate dev --name init   # 生成迁移并应用
pnpm exec prisma generate                  # v7 迁移不自动生成客户端，需显式执行
```

客户端单例从 generator 的 output 目录导入，且 v7 构造时必须传入 driver adapter：

```ts
// src/lib/prisma.ts —— 单例，避免热重载创建多个连接
import { PrismaClient } from "../generated/prisma/client.js"; // 不再来自 @prisma/client
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";

export const prisma = new PrismaClient({
  adapter: new PrismaBetterSqlite3({ url: process.env.DATABASE_URL ?? "file:./prisma/dev.db" }),
});
```

## 🛠️ 步骤三：校验与错误基建

复用 [06 课](./06-error-handling.md) 的 `HttpError` 类，并把集中式 `app.onError` 落地为独立模块。校验不需要单独的中间件：处理器里直接 `Schema.parse()`，`ZodError` 会沿 async rejection 自动传播到 `onError`（想要类型收窄的中间件方案可改用 zValidator，见 [05 课](./05-http-routing.md)）：

```ts
// src/middleware/error-handler.ts
import type { ErrorHandler } from "hono";
import { ZodError } from "zod";
import { HttpError } from "../lib/errors.js";

export const errorHandler: ErrorHandler = (err, c) => {
  if (err instanceof ZodError) {
    return c.json({ error: { code: "VALIDATION_ERROR", issues: err.issues } }, 400);
  }
  if (err instanceof HttpError) {
    return c.json({ error: { code: err.code, message: err.message } }, err.status);
  }
  console.error(err); // 500 及以上记日志，响应不泄露内部细节
  return c.json({ error: { code: "INTERNAL_ERROR" } }, 500);
};
```

## 🛠️ 步骤四：任务路由

```ts
// src/routes/tasks.ts
import { Hono } from "hono";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";
import { HttpError } from "../lib/errors.js";

export const tasksApp = new Hono();

const TaskStatus = z.enum(["todo", "doing", "done"]);
const CreateTaskSchema = z.object({ title: z.string().min(1).max(100), status: TaskStatus.default("todo") });
const UpdateTaskSchema = z.object({ title: z.string().min(1).max(100).optional(), status: TaskStatus.optional() });
const ListQuerySchema = z.object({
  status: TaskStatus.optional(), page: z.coerce.number().int().min(1).default(1),
  size: z.coerce.number().int().min(1).max(100).default(20),   // 查询串全是字符串，z.coerce 强转
});

tasksApp.get("/", async (c) => {
  const q = ListQuerySchema.parse(c.req.query());      // 失败自动进 onError
  const where = q.status ? { status: q.status } : undefined;

  const [items, total] = await prisma.$transaction([
    prisma.task.findMany({ where, orderBy: { createdAt: "desc" }, skip: (q.page - 1) * q.size, take: q.size }),
    prisma.task.count({ where }),
  ]);

  return c.json({ items, total, page: q.page, size: q.size });
});

tasksApp.post("/", async (c) => {
  const data = CreateTaskSchema.parse(await c.req.json());
  return c.json(await prisma.task.create({ data }), 201);
});

tasksApp.get("/:id", async (c) => {
  const task = await prisma.task.findUnique({ where: { id: c.req.param("id") } });
  if (!task) throw new HttpError(404, "TASK_NOT_FOUND", "任务不存在");
  return c.json(task);
});

tasksApp.patch("/:id", async (c) => {
  const data = UpdateTaskSchema.parse(await c.req.json());
  const task = await prisma.task.update({ where: { id: c.req.param("id") }, data }); // 不存在抛 P2025 → 404
  return c.json(task);
});

tasksApp.delete("/:id", async (c) => {
  await prisma.task.delete({ where: { id: c.req.param("id") } });
  return c.body(null, 204);
});
```

## 🛠️ 步骤五：装配入口

```ts
// src/app.ts —— 只装配不监听，测试直接复用
import { Hono } from "hono";
import { logger } from "hono/logger";
import { tasksApp } from "./routes/tasks.js";
import { errorHandler } from "./middleware/error-handler.js";

export function createApp() {
  const app = new Hono();
  app.use(logger());                 // 起步用内置日志；生产换 pino 等结构化方案（见部署篇）
  app.route("/api/tasks", tasksApp);
  app.notFound((c) => c.json({ error: { code: "NOT_FOUND" } }, 404));
  app.onError(errorHandler);         // 注册位置无关，全站唯一错误出口
  return app;
}
```

```ts
// src/server.ts —— 独立监听入口
import { serve } from "@hono/node-server";
import { createApp } from "./app.js";

const port = Number(process.env.PORT) || 3000;
serve({ fetch: createApp().fetch, port }, (info) =>
  console.log(`quest-api listening on :${info.port}`),
);
```

## 🛠️ 步骤六：集成测试（原生 Test Runner + app.request）

```ts
// test/tasks.test.ts
import { test, beforeEach, after } from "node:test";
import assert from "node:assert/strict";
import { createApp } from "../src/app.js";
import { prisma } from "../src/lib/prisma.js";

const app = createApp();
// 小助手：统一拼路径——app.request() 无需监听端口
const req = (path: string, init?: RequestInit) => app.request(`/api/tasks${path}`, init);

beforeEach(async () => { await prisma.task.deleteMany(); });
after(async () => { await prisma.$disconnect(); });   // 否则连接池挂住测试进程

test("创建任务返回 201 且补全默认状态", async () => {
  const res = await req("/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: "写周报" }),
  });
  assert.equal(res.status, 201);
  assert.equal((await res.json()).status, "todo");
});

test("分页查询串自动强转", async () => {
  const res = await req("?page=2&size=5");
  assert.equal(res.status, 200);
});
```

```bash
node --test test/    # 原生测试命令，无需额外测试框架
```

## 🎨 最佳实践

- ✅ **app 与 serve 分离**：`app.request()` 直接注入请求，测试零端口开销
- ✅ **查询串用 `z.coerce`**：`c.req.query()` 的值全是字符串
- ✅ **Prisma 错误映射为 4xx**：onError 按 `err.code` 前缀 `P` 转换（P2002→409、P2025→404）
- ❌ **不要跳过 migrate 直接 `db push` 上生产**：迁移文件是数据库变更的历史依据

## ❓ 常见问题

### Q1: Prisma Client 报字段不存在/类型不匹配？

**A**: 改过 `schema.prisma` 但没重新生成。执行 `pnpm exec prisma generate` 即可。

## 🎯 练习与实践

### 基础扩展

- [ ] 增加 `dueAt` 截止日期字段（含迁移）并在列表支持 `before` 过滤
- [ ] PATCH 加状态机约束：`done` 不可回退 `todo`（违反返回 409）
- [ ] 补充 404 与非法分页参数的测试用例

### 进阶挑战

- [ ] 用 Worker Threads 实现批量导入接口（上传 CSV，流式解析）
- [ ] 给列表接口加 `hono/etag` + 304 缓存，验证命中

---

## 🔗 相关文档

- 📄 **[错误处理](./06-error-handling.md)** — HttpError 与 app.onError 完整设计
- 📄 **[生态库精选](../reference/library-guides/02-ecosystem-libs.md)** — Prisma/Zod/pino 深入参考
- 📄 **[Node 一行式速查](../reference/quick-references/01-node-cheatsheet.md)** — 测试与调试命令
