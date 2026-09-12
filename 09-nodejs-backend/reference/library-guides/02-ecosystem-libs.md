# 后端生态库精选

> **文档简介**: Node 后端当前主流三方库的精选导航——Prisma、Zod、pino、BullMQ、joi 等的核心用法与选型理由

> **目标读者**: 需要为项目挑选校验/ORM/日志/队列方案的开发者

> **前置知识**: [路由与中间件](../../basics/05-http-routing.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 字典（reference） |
| **难度** | ⭐⭐ |
| **标签** | `#Prisma` `#Zod` `#pino` `#BullMQ` `#生态` |
| **更新日期** | `2026年9月` |

## 0. 分类总览

| 类别 | 首选 | 备选 | 一句话理由 |
|------|------|------|-----------|
| 校验 | **Zod** | joi、valibot、yup | schema 即 TS 类型，前后端同构 |
| ORM | **Prisma** | Drizzle、TypeORM、Kysely | 类型安全 + 迁移工具链完整 |
| 日志 | **pino** | winston | 极低开销、JSON 结构化 |
| Redis 客户端 | ioredis | node-redis | 功能全、连接池成熟 |
| 队列 | **BullMQ** | Graphile Worker | 基于 Redis 的延迟/重试/优先级队列 |
| 出站 HTTP | 全局 fetch | axios、got、ky | Node 24 原生支持，无需依赖 |
| 限流 | rate-limiter-flexible | hono-rate-limiter（社区） | 多存储后端、分布式可用 |

## 1. Zod：Schema 校验与类型推导

### 定义
TypeScript 优先的 schema 声明库：运行时校验 + 编译期类型推导同源。

### 核心用法

```ts
import { z } from "zod";
const UserSchema = z.object({
  name: z.string().min(1).max(50),
  email: z.email(),                       // Zod 4 顶层 API
  age: z.number().int().min(0).optional(),
  role: z.enum(["admin", "member"]).default("member"),
});

type User = z.infer<typeof UserSchema>;
UserSchema.safeParse(input);    // 不抛错：{ success, data | error }
UserSchema.parse(input);        // 抛 ZodError：适合"必须合法"的边界

// 变换与派生：z.coerce.number() 强转字符串、UserSchema.partial() 全字段可选
```

### 陷阱
- `parse` 与 `safeParse` 二选一，混用导致错误处理路径不统一
- Zod 3 → 4 注意：`z.string().email()` 迁移为 `z.email()`；错误结构从 `errors` 改为 `issues`

### Zod vs joi

joi 老牌稳定但无原生类型推导；TS 新项目一律 Zod，既有 joi 代码不必强行迁移。

## 2. Prisma：类型安全 ORM

### 定义
Schema 驱动的 ORM：声明模型 → 生成类型化客户端 → 迁移管理。

### 核心用法

```prisma
model User {
  id    String  @id @default(cuid())
  email String  @unique
  posts Post[]
}

model Post {
  id       String @id @default(cuid())
  title    String
  author   User   @relation(fields: [authorId], references: [id])
  authorId String
}
```

```ts
// v7：从 generator output 目录导入（@prisma/client 不再导出客户端），
// 构造时传入 driver adapter（PostgreSQL 用 @prisma/adapter-pg，SQLite 用 @prisma/adapter-better-sqlite3）
import { PrismaClient } from "../generated/prisma/client.js";
import { PrismaPg } from "@prisma/adapter-pg";
const prisma = new PrismaClient({ adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL }) });
// 类型安全查询：字段名全部自动补全
const users = await prisma.user.findMany({
  where: { email: { contains: "@example.com" } },
  include: { posts: true }, take: 20,    // 关联预载
});

// 事务
await prisma.$transaction([
  prisma.user.update({ where: { id }, data: { name } }),
  prisma.post.deleteMany({ where: { authorId: id } }),
]);

// upsert
await prisma.user.upsert({ where: { email }, update: { name }, create: { email, name } });
```

### 陷阱
- v7 schema 的 datasource 中 `url`/`directUrl` 已 deprecated（不推荐但不报错），连接配置移到 `prisma.config.ts`；客户端构造必须传 adapter
- 修改 schema 后需显式 `prisma generate`（v7 迁移不再自动生成），否则类型与运行时不一致
- `include`/`select` 已做关联扁平化，但循环内单查仍是 N+1，注意查询模式
- 唯一键冲突抛 `P2002`，错误中间件按 `err.code` 前缀 `P` 映射 4xx

### Prisma vs Drizzle

- **Prisma**：迁移工具、Studio、文档与心智负担最低；v7 起经 driver adapters 连接数据库（客户端以 TS 源码生成到项目目录）
- **Drizzle**：纯 TS 实现、更接近 SQL、边缘运行时友好；SQL 心智要求更高

## 3. pino：结构化日志

### 定义
以性能为先的 JSON 日志库，Fastify 内置默认。

### 核心用法

```ts
import pino from "pino";

const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
  redact: ["req.headers.authorization"],   // 脱敏
});
logger.info({ userId: "u-123", action: "login" }, "用户登录");
logger.error({ err }, "支付回调失败");
// 子 logger：自动携带上下文字段
const log = logger.child({ module: "billing" });
log.info("发票已生成");    // {"module":"billing","msg":"发票已生成",...}

// Hono 集成：中间件把子 logger 挂进 Context（完整 request-log 实现见 deployment/03-observability.md）
app.use(async (c, next) => {
  c.set("log", logger.child({ requestId: c.req.header("x-request-id") ?? crypto.randomUUID() }));
  await next();
});
// 处理器内：c.get("log").info(...)
```

### 陷阱
- **不要用字符串拼接**：`log.info("用户 " + id)` 无法检索，传对象 `log.info({ id }, "msg")`
- 生产环境日志交给收集器（Loki/Datadog），本地美化用 `pino-pretty`（仅开发依赖）

## 4. BullMQ：任务队列

### 定义
基于 Redis 的任务队列：延迟执行、重试退避、优先级、速率限制、可重复任务。

### 核心用法

```ts
import { Queue, Worker } from "bullmq";

// 生产者：入队
const emailQueue = new Queue("email", { connection: redisConn });
await emailQueue.add("welcome", { userId: "u-123" }, {
  attempts: 5, backoff: { type: "exponential", delay: 1_000 }, delay: 60_000,   // 重试/退避/延迟
});
// 消费者：处理（通常独立进程部署）
new Worker("email", async (job) => {
  await sendEmail(job.data.userId);
}, { connection: redisConn });
// 可重复任务（类 cron）
await emailQueue.upsertJobRepeatable("daily-report", {}, { pattern: "0 9 * * *" });
```

### 陷阱
- 处理函数必须**幂等**：重试机制意味着同一任务可能执行多次
- 任务体只放引用 ID，不要塞大对象——Redis 存取成本与失败重放成本都高

## 5. 其他值得一提的库

- **node:test**：Node 24 内置测试框架已覆盖 mock/计时器模拟/并发，零依赖起步首选；复杂快照场景再用 Vitest/Jest
- **hono/secure-headers / arctic**：Hono 内置安全响应头一行接入；OAuth2/OIDC 客户端

---

## 🔗 相关文档

- 📄 **[内置模块导航表](./01-core-modules.md)** — 先查内置，再找三方
- 📄 **[第一个项目](../../basics/08-first-project.md)** — Prisma+Zod+pino 组合实战
- 📄 **[TypeScript 模式](../language-concepts/05-typescript-patterns.md)** — env 校验与类型守卫模式
