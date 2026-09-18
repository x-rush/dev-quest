# 生态集成：Prisma + PostgreSQL 与 Redis

## 先看框架承担哪部分职责

**Prisma 与 Redis**：Prisma 连接数据库事实，Redis 通常保存副本；一次写入后的失效顺序决定可能看见什么旧数据。连接池和迁移是运行条件。

**最小练习与预期结果**：写入后立即读取，再模拟缓存不可用；说明一致性与降级策略，不把缓存失败误判成数据库写入失败。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 手把手把 Prisma ORM 接入 PostgreSQL、把 Redis 作为缓存层接入 Hono 4 服务，覆盖连接管理、事务与迁移的工程化实践
>
> **目标读者**: 已会写基础路由、需要接入持久化与缓存的中级后端开发者
>
> **前置知识**: SQL 基础、[Hono 基础](01-hono-basics.md)、环境变量管理

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#prisma` `#postgresql` `#redis` `#cache` |
| **更新日期** | `2026年9月` |

</details>

> Prisma 与生态库的条目式速查见 [`../reference/library-guides/02-ecosystem-libs.md`](../reference/library-guides/02-ecosystem-libs.md)。

## 🎯 本节目标

- 建立单例化的 Prisma Client，正确处理连接生命周期
- 掌握迁移命令与交互式事务
- 用 ioredis 实现带 TTL 的读缓存并接入 Hono 路由

## 1. Prisma 接入 PostgreSQL

```bash
pnpm add @prisma/client @prisma/adapter-pg pg   # v7：PostgreSQL 经 driver adapter 连接
pnpm add -D prisma dotenv
pnpm exec prisma init --datasource-provider postgresql
```

```prisma
// prisma/schema.prisma —— 模型即数据库表的单一事实来源
generator client {
  provider = "prisma-client"
  output   = "../src/generated/prisma" // v7：客户端生成到项目目录（TypeScript 源码）
}

datasource db {
  provider = "postgresql"
  // v7 起连接串写在 prisma.config.ts，schema 不再写 url
}

model Post {
  id        String   @id @default(cuid())
  title     String
  published Boolean  @default(false)
  authorId  String
  createdAt DateTime @default(now())

  @@index([authorId, createdAt]) // 高频查询字段建复合索引
}
```

```ts
// prisma.config.ts —— v7：CLI 与迁移从这里读取连接串（dotenv 负责加载 .env）
import "dotenv/config";
import { defineConfig } from "prisma/config";

export default defineConfig({
  schema: "prisma/schema.prisma",
  migrations: { path: "prisma/migrations" },
  datasource: { url: process.env.DATABASE_URL },
});
```

**连接管理**：Prisma Client 内部维护连接池，进程内只应实例化一次。开发时 `tsx watch` 反复重启模块会泄漏连接，用全局缓存解决：

```typescript
// src/lib/prisma.ts —— 开发热重载安全的单例模式
// v7：@prisma/client 仍需安装作为运行时依赖，但不再从它导入 PrismaClient，而是从生成的 output 目录导入；构造时传入 adapter
import { PrismaClient } from '../generated/prisma/client.js';
import { PrismaPg } from '@prisma/adapter-pg';

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL });

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    adapter,
    log: process.env.NODE_ENV === 'development' ? ['warn', 'error'] : ['error'],
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
```

### 迁移与事务

```bash
pnpm exec prisma migrate dev --name init   # 开发：生成迁移并应用
pnpm exec prisma generate                  # v7：迁移不再自动生成客户端，显式执行
pnpm exec prisma migrate deploy            # 生产/CI：只应用不生成
```

> v7 的两条 migrate 命令都从 `prisma.config.ts` 读取连接串；`schema.prisma` 的 datasource 中写 `url`/`directUrl` 已被官方标记为 deprecated（不推荐，连接串应统一在 `prisma.config.ts` 提供），但并不报错。

```typescript
// 交互式事务：转账类"读-改-写"必须包在事务里
import { HttpError } from '../lib/http-error.js';

export async function publishPost(id: string) {
  return prisma.$transaction(async (tx) => {
    const post = await tx.post.findUnique({ where: { id } });
    if (!post) throw new HttpError(404, '文章不存在');
    return tx.post.update({
      where: { id },
      data: { published: true },
    });
  }); // 回调抛错自动回滚
}
```

## 2. Redis 缓存层

```bash
pnpm add ioredis
```

```typescript
// src/lib/redis.ts —— 单例连接与失败容忍
import Redis from 'ioredis';

export const redis = new Redis(process.env.REDIS_URL ?? 'redis://localhost:6379', {
  maxRetriesPerRequest: 2,   // 限制重试，避免缓存故障拖垮请求
  enableOfflineQueue: false, // Redis 离线时快速失败而不是排队
});

redis.on('error', (err) => console.error('[redis]', err.message)); // 必须监听，否则 unhandled error
```

**Cache-Aside 模式**（读路径最常用的缓存策略）：

```typescript
// src/services/post-service.ts —— 先查缓存，未命中回源并写入
import { redis } from '../lib/redis.js';
import { prisma } from '../lib/prisma.js';

const TTL_SECONDS = 60;

export async function getPost(id: string) {
  const cacheKey = `post:${id}`;

  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const post = await prisma.post.findUnique({ where: { id } });
  if (post) await redis.set(cacheKey, JSON.stringify(post), 'EX', TTL_SECONDS);
  return post;
}

export async function updatePost(id: string, data: { title?: string }) {
  const post = await prisma.post.update({ where: { id }, data });
  await redis.del(`post:${id}`); // 写操作后失效缓存，下个读请求回源最新数据
  return post;
}
```

```typescript
// 路由接入
postsApp.get('/:id', async (c) => {
  const post = await getPost(c.req.param('id'));
  if (!post) throw notFound();
  return c.json(post);
});
```

## 3. 集成健康检查

```typescript
// src/app.ts —— 探活同时覆盖数据库与 Redis，供容器/负载均衡探测
app.get('/health', async (c) => {
  const checks: Record<string, string> = {};

  await Promise.all([
    prisma.$queryRaw`SELECT 1`.then(() => (checks.postgres = 'ok')).catch(() => (checks.postgres = 'down')),
    redis.ping().then(() => (checks.redis = 'ok')).catch(() => (checks.redis = 'down')),
  ]);

  const healthy = Object.values(checks).every((v) => v === 'ok');
  return c.json({ status: healthy ? 'ok' : 'degraded', checks }, healthy ? 200 : 503);
});
```

## ✅ 最佳实践与陷阱

数据库客户端按其生命周期复用，避免每次请求创建新连接池；不同租户或环境的隔离需求另行设计。迁移在受控发布步骤执行，失败时停止后续依赖新结构的部署。

缓存中的旧数据通常来自应用缓存协议，而不是 Redis 天生只能弱一致。删除缓存与更新缓存各有竞态，先明确写入顺序、失效策略和可接受延迟，再测试并发读写。TTL 只能限制部分旧值持续时间，不能独自证明一致性。

## 🔗 相关文档

- 📖 [后端生态库精选](../reference/library-guides/02-ecosystem-libs.md) — Prisma/ioredis 等库速查
- 📄 [第一个完整项目：任务管理 REST API](../basics/08-first-project.md) — Prisma 在入门项目中的首次实践
- 📖 [Node 核心模块 API 速查](../reference/language-concepts/03-node-core-api.md) — 进程与事件相关 API
- 📄 [生产级 Node.js API](../projects/04-production-nodejs-api.md) — 生态集成的完整生产化应用


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
