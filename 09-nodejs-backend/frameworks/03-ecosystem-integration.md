# 生态集成：Prisma + PostgreSQL 与 Redis

> **文档简介**: 手把手把 Prisma ORM 接入 PostgreSQL、把 Redis 作为缓存层接入 Express 5 服务，覆盖连接管理、事务与迁移的工程化实践
>
> **目标读者**: 已会写基础路由、需要接入持久化与缓存的中级后端开发者
>
> **前置知识**: SQL 基础、[Express 基础](01-express-basics.md)、环境变量管理

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#prisma` `#postgresql` `#redis` `#cache` |
| **更新日期** | `2026年9月` |

> Prisma 与生态库的条目式速查见 [`../reference/library-guides/02-ecosystem-libs.md`](../reference/library-guides/02-ecosystem-libs.md)。

## 🎯 本节目标

- 建立单例化的 Prisma Client，正确处理连接生命周期
- 掌握迁移命令与交互式事务
- 用 ioredis 实现带 TTL 的读缓存并接入 Express

## 1. Prisma 接入 PostgreSQL

```bash
pnpm add prisma @prisma/client
pnpm exec prisma init --datasource-provider postgresql
```

```prisma
// prisma/schema.prisma —— 模型即数据库表的单一事实来源
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
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

**连接管理**：Prisma Client 内部维护连接池，进程内只应实例化一次。开发时 `tsx watch` 反复重启模块会泄漏连接，用全局缓存解决：

```typescript
// src/lib/prisma.ts —— 开发热重载安全的单例模式
import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['warn', 'error'] : ['error'],
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
```

### 迁移与事务

```bash
pnpm exec prisma migrate dev --name init   # 开发：生成迁移并应用
pnpm exec prisma migrate deploy            # 生产/CI：只应用不生成
```

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
router.get('/posts/:id', async (req, res) => {
  const post = await getPost(req.params.id);
  if (!post) throw notFound();
  res.json(post);
});
```

## 3. 集成健康检查

```typescript
// src/app.ts —— 探活同时覆盖数据库与 Redis，供容器/负载均衡探测
app.get('/health', async (_req, res) => {
  const checks: Record<string, string> = {};

  await Promise.all([
    prisma.$queryRaw`SELECT 1`.then(() => (checks.postgres = 'ok')).catch(() => (checks.postgres = 'down')),
    redis.ping().then(() => (checks.redis = 'ok')).catch(() => (checks.redis = 'down')),
  ]);

  const healthy = Object.values(checks).every((v) => v === 'ok');
  res.status(healthy ? 200 : 503).json({ status: healthy ? 'ok' : 'degraded', checks });
});
```

## ✅ 最佳实践与陷阱

- ✅ `prisma migrate deploy` 用于生产，`migrate dev` 只在开发使用
- ✅ 缓存写路径"更新后失效"而非"更新缓存"，避免并发写不一致
- ❌ 每次请求 `new PrismaClient()`——连接池迅速耗尽（症状见 [`../reference/quick-references/02-troubleshooting.md`](../reference/quick-references/02-troubleshooting.md)）
- ❌ 把 Redis 当强一致存储：TTL 内读到旧数据是特性不是 Bug

## 🔗 相关文档

- 📖 [后端生态库精选](../reference/library-guides/02-ecosystem-libs.md) — Prisma/ioredis 等库速查
- 📄 [第一个完整项目：任务管理 REST API](../basics/08-first-project.md) — Prisma 在入门项目中的首次实践
- 📖 [Node 核心模块 API 速查](../reference/language-concepts/03-node-core-api.md) — 进程与事件相关 API
- 📄 [生产级 Node.js API](../projects/04-production-nodejs-api.md) — 生态集成的完整生产化应用
