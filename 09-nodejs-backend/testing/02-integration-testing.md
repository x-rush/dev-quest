# 集成测试：app.request() + 测试数据库

> **文档简介**: 让 API 在"真实"环境中被验证——Hono 内置测试客户端 `app.request()` 直连装配好的 app、独立 PostgreSQL 测试库 + 迁移播种，一次运行覆盖路由-校验-数据库全链路

> **目标读者**: 已有单元测试基础、需要验证模块协作的中级后端开发者

> **前置知识**: [单元测试](01-unit-testing.md)、[app 与 server 分离](../frameworks/01-hono-basics.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#app-request` `#integration-testing` `#prisma` `#test-db` |
| **更新日期** | `2026年9月` |

## 🎯 本节目标

- 用 `app.request()` 对 app 发起真实 HTTP 调用（不监听端口、零额外依赖）
- 搭建隔离的测试数据库并自动迁移
- 在用例间保持数据干净（截断策略）

## 1. 为什么 app/server 分离是集成测试的前提

```typescript
// tests/helpers/app.ts —— 直接复用装配好的 Hono 实例，无需真实端口
import { createApp } from '../../src/app.js';

export const app = createApp();

/** JSON 请求助手：app.request() 的薄封装，省去重复的 header/body 拼装 */
export function jsonRequest(path: string, method = 'GET', body?: unknown) {
  return app.request(path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}
```

与 supertest 不同，`app.request()` 是 Hono 内置能力：不需要 `pnpm add -D supertest`，也不需要把 app 包一层代理——它返回的就是 Web 标准 `Response`，断言方式与 fetch 完全一致。

## 2. 隔离的测试数据库

**关键决策**：测试永远不碰开发库。用独立的 `DATABASE_URL` + 真实迁移，保证 schema 一致。整条链路必须闭环：`.env.test` 不会被自动加载，要先用它覆盖测试进程的环境变量——且必须在任何模块求值之前（prisma 单例在 import 时就读 `process.env.DATABASE_URL`），迁移与业务代码才会都落在测试库上：

```bash
# .env.test —— 独立测试库（本地 Docker 起的 PostgreSQL）
DATABASE_URL="postgresql://postgres:postgres@localhost:5433/app_test"
REDIS_URL="redis://localhost:6380"
JWT_ACCESS_SECRET="test-secret-test-secret-test-secret-32!"
NODE_ENV="test"
```

```typescript
// tests/env.ts —— 只做一件事：把 .env.test 注入 process.env。
// ESM 按导入顺序求值——在所有文件里都把它放第一个 import，
// 后续模块（含 prisma 单例）读到的就是测试库；
// dotenv 不覆盖已存在的变量，CI 显式注入的变量优先生效
import { config } from 'dotenv';

config({ path: '.env.test' });
```

```typescript
// tests/setup.ts —— 全局前置：应用迁移，结束时断开连接
import './env.js';                       // ← 必须是第一个导入：先加载 .env.test
import { execSync } from 'node:child_process';
import { afterAll, beforeAll } from 'vitest';
import { prisma } from '../src/lib/prisma.js';

beforeAll(() => {
  // 用测试库跑迁移：schema 与生产同源。
  // v7：migrate deploy 从 prisma.config.ts 读连接串——其内部的
  // import 'dotenv/config' 只加载 .env 且不覆盖已存在的变量，
  // 子进程默认继承本进程 env，其中 DATABASE_URL 已被 env.ts
  // 指向测试库，开发库的 .env 值因此不会生效
  execSync('pnpm exec prisma migrate deploy', { stdio: 'inherit' });
});

afterAll(async () => {
  await prisma.$disconnect();
});
```

```typescript
// vitest.config.ts —— 把 setup 注册为全局前置文件：每个测试文件求值
// 之前先执行 setup（进而先执行 env.ts），保证测试文件 import 到的
// prisma 单例一定连着测试库
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    setupFiles: ['tests/setup.ts'],
  },
});
```

> CI 中的数据库用 GitHub Actions service 容器拉起，见 [`../deployment/02-ci-cd-pipelines.md`](../deployment/02-ci-cd-pipelines.md)。

## 3. 用例间数据清理：truncate 策略

集成测试需要真实读写，不能 Mock，因此每个用例前清空表（保留 schema）：

```typescript
// tests/helpers/db.ts
import { prisma } from '../../src/lib/prisma.js';

/** 按外键顺序清空所有表，比逐表 deleteMany 更稳 */
export async function resetDb() {
  await prisma.$executeRawUnsafe(`
    TRUNCATE TABLE "RefreshToken", "User", "Todo" RESTART IDENTITY CASCADE;
  `);
}
```

```typescript
// tests/auth-api.test.ts —— 完整的注册-登录链路集成测试
import { describe, it, expect, beforeEach } from 'vitest';
import { jsonRequest } from './helpers/app.js';
import { resetDb } from './helpers/db.js';

beforeEach(resetDb);

describe('POST /auth/register + /auth/login', () => {
  it('注册后可用相同凭据登录', async () => {
    const email = 'user@example.com'; // 合成数据，非真实邮箱

    const reg = await jsonRequest('/auth/register', 'POST', { email, password: 's3curePass!' });
    expect(reg.status).toBe(201);

    const login = await jsonRequest('/auth/login', 'POST', { email, password: 's3curePass!' });
    expect(login.status).toBe(200);
    expect(((await login.json()) as { accessToken: string }).accessToken).toBeDefined();
    // refresh token 必须在 HttpOnly cookie 里，而不是响应体
    expect(login.headers.get('set-cookie')).toContain('HttpOnly');
  });

  it('重复邮箱返回 400', async () => {
    const body = { email: 'dup@example.com', password: 's3curePass!' };
    await jsonRequest('/auth/register', 'POST', body);
    const again = await jsonRequest('/auth/register', 'POST', body);
    expect(again.status).toBe(400);
  });

  it('错误密码与不存在邮箱返回一致的 401', async () => {
    const wrong = await jsonRequest('/auth/login', 'POST', { email: 'nobody@example.com', password: 'whatever1!' });
    expect(wrong.status).toBe(401);
  });
});
```

## 4. CRUD 全链路示例

```typescript
// tests/todos-api.test.ts
import { describe, it, expect } from 'vitest';
import { jsonRequest } from './helpers/app.js';

describe('GET /todos', () => {
  it('分页与过滤生效', async () => {
    // 播种：直接写库比走 API 快
    await prisma.todo.createMany({
      data: [
        { title: 'a', done: false, priority: 'high' },
        { title: 'b', done: true, priority: 'low' },
      ],
    });

    const res = await jsonRequest('/todos?status=done');
    const body = (await res.json()) as { items: Array<{ title: string }> };
    expect(res.status).toBe(200);
    expect(body.items).toHaveLength(1);
    expect(body.items[0].title).toBe('b');
  });

  it('Zod 校验失败返回 422 与字段级错误', async () => {
    const res = await jsonRequest('/todos', 'POST', { title: '' });
    expect(res.status).toBe(422);
    expect(((await res.json()) as { error: string }).error).toMatch(/校验失败/);
  });

  it('不存在的 id 返回 404', async () => {
    const res = await jsonRequest('/todos/nonexistent');
    expect(res.status).toBe(404);
  });
});
```

注意 `Response` 的 body 是流式的——`json()` 只能消费一次，需要复用时先存变量。

## ✅ 最佳实践与陷阱

- ✅ 集成测试断言**状态码 + 响应结构**，避免断言易变的具体文案
- ✅ 播种用 `createMany` 直写库，验证走 API
- ❌ 在集成测试里 Mock 数据库——那只是昂贵的单元测试
- ❌ 用例间依赖执行顺序——每个用例必须能单独 `vitest run -t` 通过

## 🔗 相关文档

- 📄 [单元测试](01-unit-testing.md) — 快速反馈层
- 📄 [端到端 API 测试](03-e2e-api-testing.md) — 下一层：真实环境全链路
- 📄 [CI/CD 流水线](../deployment/02-ci-cd-pipelines.md) — 让测试自动拦截回归
- 📖 [Node 一行式速查](../reference/quick-references/01-node-cheatsheet.md) — 测试相关 CLI 命令
