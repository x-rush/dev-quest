# 第一个完整项目：任务管理 REST API

## 先理解，再动手

最小 REST API 是一组有一致规则的操作，不只是若干返回 JSON 的函数。创建、查询、更新和删除必须对同一资源身份工作。

**本节自测**：依次创建、查询、完成、删除同一 ID，再查询。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

最后得到不存在；非法输入不创建记录，内存版重启清空应写明。

</details>

> **文档简介**: 综合运用前七课知识，从零构建任务管理 REST API——Hono 4 + Prisma + Zod，含分页、校验、错误处理与测试

> **目标读者**: 完成入门路径全部课程的学习者，需要一次"真刀真枪"的综合演练

> **前置知识**: [路由与中间件](./05-http-routing.md)、[错误处理](./06-error-handling.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 教程（basics） |
| **难度** | ⭐ |
| **标签** | `#REST API` `#Hono` `#Prisma` `#Zod` `#综合项目` |
| **更新日期** | `2026年9月` |

</details>

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

本页给出带 SQLite 持久化的完整基线。若先改成内存存储，还必须同步替换测试的清理/断开连接逻辑与事务查询，不能仅把 `prisma.task.*` 改成数组方法。先按本页通过完整测试，再练习替换存储。

## 🛠️ 步骤一：初始化与依赖

```bash
mkdir quest-api
cd quest-api
pnpm init
pnpm pkg set type=module
pnpm add hono@4 @hono/node-server @prisma/client@7 zod@4 dotenv
pnpm add @prisma/adapter-better-sqlite3@7 better-sqlite3
pnpm add -D prisma@7 typescript @types/node tsx
```

使用模块 README 的 Node 基线，提交生成的 `pnpm-lock.yaml` 固定依赖组合。若 pnpm 提示跳过 SQLite 的安装脚本，运行 `pnpm approve-builds`，只允许刚安装且已核对来源的原生依赖，再执行 `pnpm rebuild`；无法加载原生模块时先解决 Node ABI/本地构建环境，不要把报错当成路由错误。

新建 `tsconfig.json`：

```json
{
  "compilerOptions": {
    "target": "ES2022", "module": "NodeNext", "moduleResolution": "NodeNext",
    "strict": true, "noEmit": true, "skipLibCheck": true,
    "types": ["node"]
  },
  "include": ["src/**/*.ts", "test/**/*.ts", "generated/**/*.ts"]
}
```

本页用 `tsx` 运行 TypeScript 并解析源码中 `.js` 导入，用 `tsc --noEmit` 独立检查类型。不要直接执行 `node --test` 后把“发现 0 个测试”当作通过。

目录规划：`src/lib/`（prisma 单例、HttpError）、`src/middleware/`（错误出口）、`src/routes/`（按资源拆分子应用）、`test/`。`app.ts` 只装配不监听，`server.ts` 负责监听——测试直接复用 Hono 实例，不占端口。

## 🛠️ 步骤二：数据模型（Prisma）

```bash
pnpm exec prisma init --datasource-provider sqlite
```

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client"
  output   = "../generated/prisma" // v7：客户端生成到项目目录（TypeScript 源码）
}

datasource db {
  provider = "sqlite"              // 演练用 SQLite，零配置；生产换 postgresql
  // v7 起 schema 不再写连接串——连接配置移到 prisma.config.ts
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
// prisma.config.ts —— v7：CLI 与迁移从这里读取连接配置
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
// src/lib/prisma.ts —— 一个进程内的模块实例复用同一个客户端
import "dotenv/config";
import { PrismaClient } from "../../generated/prisma/client.js"; // 不再来自 @prisma/client，output 相对 prisma/ 目录 → 项目根 generated/prisma
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";

export const prisma = new PrismaClient({
  adapter: new PrismaBetterSqlite3({ url: process.env.DATABASE_URL ?? "file:./prisma/dev.db" }),
});
```

## 🛠️ 步骤三：校验与错误基建

先保存下面的错误类型，再注册统一出口。处理器里直接 `Schema.parse()`，`ZodError` 会沿 async rejection 传播到 `onError`：

```ts
// src/lib/errors.ts
import type { ContentfulStatusCode } from "hono/utils/http-status";

export class HttpError extends Error {
  constructor(public status: ContentfulStatusCode, message: string, public code: string) {
    super(message);
  }
}
```

```ts
// src/middleware/error-handler.ts
import type { ErrorHandler } from "hono";
import { ZodError } from "zod";
import { HttpError } from "../lib/errors.js";
import { Prisma } from "../../generated/prisma/client.js";

export const errorHandler: ErrorHandler = (err, c) => {
  if (err instanceof ZodError) {
    return c.json({ error: { code: "VALIDATION_ERROR", issues: err.issues } }, 400);
  }
  if (err instanceof HttpError) {
    return c.json({ error: { code: err.code, message: err.message } }, err.status);
  }
  if (err instanceof Prisma.PrismaClientKnownRequestError && err.code === "P2025") {
    return c.json({ error: { code: "TASK_NOT_FOUND", message: "任务不存在" } }, 404);
  }
  console.error(err); // 500 及以上记日志，响应不泄露内部细节
  return c.json({ error: { code: "INTERNAL_ERROR" } }, 500);
};
```

## 🛠️ 步骤四：任务路由

```ts
// src/routes/tasks.ts
import { Hono } from "hono";
import type { Context } from "hono";
import { z } from "zod";
import { prisma } from "../lib/prisma.js";
import { HttpError } from "../lib/errors.js";

export const tasksApp = new Hono();

const TaskStatus = z.enum(["todo", "doing", "done"]);
const CreateTaskSchema = z.strictObject({ title: z.string().trim().min(1).max(100), status: TaskStatus.default("todo") });
const UpdateTaskSchema = z.strictObject({ title: z.string().trim().min(1).max(100).optional(), status: TaskStatus.optional() })
  .refine((value) => Object.keys(value).length > 0, "至少提供一个更新字段");
const ListQuerySchema = z.object({
  status: TaskStatus.optional(), page: z.coerce.number().int().min(1).default(1),
  size: z.coerce.number().int().min(1).max(100).default(20),   // 查询串全是字符串，z.coerce 强转
});

async function readJson(c: Context): Promise<unknown> {
  try {
    return await c.req.json();
  } catch (error) {
    if (error instanceof SyntaxError) throw new HttpError(400, "JSON 格式错误", "INVALID_JSON");
    throw error;
  }
}

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
  const data = CreateTaskSchema.parse(await readJson(c));
  return c.json(await prisma.task.create({ data }), 201);
});

tasksApp.get("/:id", async (c) => {
  const task = await prisma.task.findUnique({ where: { id: c.req.param("id") } });
  if (!task) throw new HttpError(404, "任务不存在", "TASK_NOT_FOUND");
  return c.json(task);
});

tasksApp.patch("/:id", async (c) => {
  const data = UpdateTaskSchema.parse(await readJson(c));
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
  const app = new Hono({ strict: false }); // 本练习同时接受集合路径末尾有/无斜杠
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

if (process.env.DATABASE_URL !== "file:./prisma/test.db") {
  throw new Error("测试只能使用 test.db，禁止清理开发数据库");
}
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
  const res = await req("/?page=2&size=5");
  assert.equal(res.status, 200);
});

test("不存在的更新/删除都返回 404", async () => {
  const updated = await req("/missing", { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: "done" }) });
  assert.equal(updated.status, 404);
  assert.equal((await req("/missing", { method: "DELETE" })).status, 404);
});

test("损坏 JSON 和无效更新都返回 400", async () => {
  const headers = { "Content-Type": "application/json" };
  assert.equal((await req("/", { method: "POST", headers, body: "{" })).status, 400);
  for (const payload of [{}, { title: "   " }, { status: null }, { unexpected: 1 }]) {
    assert.equal((await req("/missing", { method: "PATCH", headers, body: JSON.stringify(payload) })).status, 400);
  }
});
```

```bash
pnpm exec tsc --noEmit
# 下列环境变量写法适用于 Bash；PowerShell 用 $env:DATABASE_URL = 'file:./prisma/test.db'
export DATABASE_URL="file:./prisma/test.db"
pnpm exec prisma migrate deploy
pnpm exec tsx --test test/tasks.test.ts
```

测试预期 4 项通过。独立测试文件在 `beforeEach` 清空专用数据库；禁止让多个并行测试文件共享同一个 SQLite 文件。测试完在 Bash `unset DATABASE_URL`，PowerShell `Remove-Item Env:DATABASE_URL`，随后运行 `pnpm exec tsx src/server.ts`，开发服务才会恢复使用 `.env` 中的 `dev.db`。`GET /api/tasks/` 应返回带 `items/total/page/size` 的对象，新增后重启服务仍能查回。

Prisma 7 的驱动适配器与显式客户端生成规则参见 [官方升级说明](https://docs.prisma.io/docs/guides/upgrade-prisma-orm/v7)。换成 PostgreSQL 时须重新选择适配器、连接配置和迁移方案，不能只改 `provider` 后复用 SQLite 迁移。

验证状态（2026-09-19）：已补齐本页文件、执行命令和四项行为断言；本轮容器两次安装真实 Prisma/SQLite 依赖均因 npm 网络 `ECONNRESET` 中断，尚未完成类型检查、迁移和运行验收。上述 4 项为预期结果，不能作为已通过的报告。按锁文件完成这些命令后，再将自己的依赖版本和实际结果记录到练习仓库。

## 🎨 最佳实践

应用路由与监听端口分离后，可以在测试中注入请求检查 HTTP 行为，再用少量真实端口测试覆盖服务器集成。查询参数转换后仍要验证上下限，例如空字符串被转成 0 是否符合分页规则。

数据库错误只按已识别语义映射，例如唯一约束冲突可以对应冲突响应；不能把所有带 P 前缀的 Prisma 错误都变成客户端 4xx，连接和内部故障仍需服务端处理。数据库结构通过可审阅迁移演进，发布前验证旧数据兼容。

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


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
