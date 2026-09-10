# 第一个完整项目：任务管理 REST API

> **文档简介**: 综合运用前七课知识，从零构建任务管理 REST API——Express 5 + Prisma + Zod，含分页、校验、错误处理与测试

> **目标读者**: 完成入门路径全部课程的学习者，需要一次"真刀真枪"的综合演练

> **前置知识**: [路由与中间件](./05-http-routing.md)、[错误处理](./06-error-handling.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#REST API` `#Express5` `#Prisma` `#Zod` `#综合项目` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本项目后，你将能够：

- 独立搭建含数据库的分层 Node 后端项目
- 用 Prisma 完成建模、迁移与类型安全查询
- 把校验、错误处理、日志组织成可复用的骨架
- 为 API 编写基于原生 Test Runner 的测试

## 📋 项目需求

实现任务管理 API，资源为 Task：

| 方法 | 路径 | 功能 | 成功状态码 |
|------|------|------|-----------|
| GET | `/api/tasks?status=&page=&size=` | 分页筛选列表 | 200 |
| POST | `/api/tasks` | 创建任务 | 201 |
| GET/PATCH/DELETE | `/api/tasks/:id` | 查询/更新/删除 | 200 / 404 / 204 |

字段约束：`title` 1-100 字符；`status` ∈ `todo | doing | done`，默认 `todo`。

## 🛠️ 步骤一：初始化与依赖

```bash
pnpm init && pnpm pkg set type=module
pnpm add express @prisma/client zod pino-http
pnpm add -D prisma typescript @types/node @types/express supertest
```

目录规划：`src/lib/`（prisma 单例、HttpError）、`src/middleware/`（校验、错误处理）、`src/routes/`（按资源拆分）、`test/`。`app.ts` 只装配不监听，`server.ts` 负责监听——便于测试直接注入 app。

## 🛠️ 步骤二：数据模型（Prisma）

```bash
pnpm exec prisma init
```

```prisma
// prisma/schema.prisma
generator client { provider = "prisma-client-js" }

datasource db {
  provider = "sqlite"          // 演练用 SQLite，零配置；生产换 postgresql
  url      = env("DATABASE_URL")
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

```bash
pnpm exec prisma migrate dev --name init   # 迁移并生成类型化客户端
```

客户端统一从 `src/lib/prisma.ts` 导出单例：`export const prisma = new PrismaClient()`，避免热重载创建多个连接池。

## 🛠️ 步骤三：校验与错误基建

复用 [06 课](./06-error-handling.md) 的 `HttpError` 类与集中式 `errorHandler`（四参中间件，注册在路由之后）。校验中间件复用 [05 课](./05-http-routing.md) 的 `validateBody` 泛型封装，仅把失败分支改为 `next({ status: 400, code: "VALIDATION_ERROR", issues: parsed.error.issues })`，交给统一错误中间件输出。

## 🛠️ 步骤四：任务路由

```ts
// src/routes/tasks.ts
import { Router } from "express";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";
import { HttpError } from "../lib/errors.js";
import { validateBody } from "../middleware/validate.js";

export const tasksRouter = Router();

const TaskStatus = z.enum(["todo", "doing", "done"]);
const CreateTaskSchema = z.object({ title: z.string().min(1).max(100), status: TaskStatus.default("todo") });
const UpdateTaskSchema = z.object({ title: z.string().min(1).max(100).optional(), status: TaskStatus.optional() });
const ListQuerySchema = z.object({
  status: TaskStatus.optional(), page: z.coerce.number().int().min(1).default(1),
  size: z.coerce.number().int().min(1).max(100).default(20),   // 查询串全是字符串，z.coerce 强转
});

tasksRouter.get("/", async (req, res) => {
  const q = ListQuerySchema.parse(req.query);          // 失败自动进错误中间件
  const where = q.status ? { status: q.status } : undefined;

  const [items, total] = await prisma.$transaction([
    prisma.task.findMany({ where, orderBy: { createdAt: "desc" }, skip: (q.page - 1) * q.size, take: q.size }),
    prisma.task.count({ where }),
  ]);

  res.json({ items, total, page: q.page, size: q.size });
});

tasksRouter.post("/", validateBody(CreateTaskSchema), async (req, res) => {
  res.status(201).json(await prisma.task.create({ data: req.body }));
});

tasksRouter.get("/:id", async (req, res) => {
  const task = await prisma.task.findUnique({ where: { id: req.params.id } });
  if (!task) throw new HttpError(404, "TASK_NOT_FOUND", "任务不存在");
  res.json(task);
});

tasksRouter.patch("/:id", validateBody(UpdateTaskSchema), async (req, res) => {
  const task = await prisma.task.update({ where: { id: req.params.id }, data: req.body }); // 不存在抛 P2025 → 404
  res.json(task);
});

tasksRouter.delete("/:id", async (req, res) => {
  await prisma.task.delete({ where: { id: req.params.id } });
  res.sendStatus(204);
});
```

## 🛠️ 步骤五：装配入口

```ts
// src/app.ts —— 不监听端口，便于测试注入
import express from "express";
import { pinoHttp } from "pino-http";
import { tasksRouter } from "./routes/tasks.js";
import { errorHandler } from "./middleware/error-handler.js";

export function createApp() {
  const app = express();
  app.use(pinoHttp());              // 结构化访问日志
  app.use(express.json());
  app.use("/api/tasks", tasksRouter);
  app.use((_req, res) => res.status(404).json({ error: { code: "NOT_FOUND" } }));
  app.use(errorHandler);            // 必须最后注册
  return app;
}

// src/server.ts —— 独立监听入口
const port = Number(process.env.PORT) || 3000;
createApp().listen(port, () => console.log(`quest-api listening on :${port}`));
```

## 🛠️ 步骤六：集成测试（原生 Test Runner）

```ts
// test/tasks.test.ts
import { test, beforeEach, after } from "node:test";
import assert from "node:assert/strict";
import request from "supertest";
import { createApp } from "../src/app.js";
import { prisma } from "../src/lib/prisma.js";

const app = createApp();

beforeEach(async () => { await prisma.task.deleteMany(); });
after(async () => { await prisma.$disconnect(); });   // 否则连接池挂住测试进程

test("创建任务返回 201 且补全默认状态", async () => {
  const res = await request(app).post("/api/tasks").send({ title: "写周报" });
  assert.equal(res.status, 201);
  assert.equal(res.body.status, "todo");
});
```

```bash
node --test test/    # 原生测试命令，无需额外测试框架
```

## 🎨 最佳实践

- ✅ **app 与 listen 分离**：测试注入 app 而不占端口
- ✅ **查询串用 `z.coerce`**：`req.query` 的值全是字符串
- ✅ **Prisma 错误映射为 4xx**：错误中间件按 `err.code` 前缀 `P` 转换（P2002→409、P2025→404）
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
- [ ] 给列表接口加 ETag + 304 缓存，验证命中

---

## 🔗 相关文档

- 📄 **[错误处理](./06-error-handling.md)** — HttpError 与 errorHandler 完整设计
- 📄 **[生态库精选](../reference/library-guides/02-ecosystem-libs.md)** — Prisma/Zod/pino 深入参考
- 📄 **[Node 一行式速查](../reference/quick-references/01-node-cheatsheet.md)** — 测试与调试命令
