# 单元测试：Vitest 实践

> **文档简介**: 用 Vitest 为 Node 后端建立单元测试体系——服务层测试、Prisma/Redis 的 Mock 策略与覆盖率门槛，让业务逻辑在毫秒级反馈中迭代
>
> **目标读者**: 已能独立写 API、需要建立测试习惯的后端开发者
>
> **前置知识**: [服务层解耦](../projects/01-todo-api.md) 的目录结构、TypeScript 基础

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#vitest` `#unit-testing` `#mock` `#coverage` |
| **更新日期** | `2026年9月` |

Vitest 与测试工具的条目式速查见 [`../reference/library-guides/02-ecosystem-libs.md`](../reference/library-guides/02-ecosystem-libs.md)。

## 🎯 本节目标

- 配置与 TypeScript/ESM 完全兼容的 Vitest
- 明确"哪些该测、哪些该 Mock"的单元边界
- 建立可量化的覆盖率基线

## 1. 配置

```bash
pnpm add -D vitest
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['tests/**/*.test.ts'],
    environment: 'node', // 后端固定 node，不要用 jsdom
    globals: true,        // 允许 describe/it 免导入（也可保持显式导入）
    setupFiles: ['tests/setup.ts'],
    coverage: {
      provider: 'v8',
      include: ['src/services/**/*.ts'], // 覆盖率只统计业务层
      thresholds: { lines: 70, functions: 70 }, // CI 低于此值即失败
    },
  },
});
```

```json
// package.json scripts
{ "test": "vitest run", "test:watch": "vitest", "test:cov": "vitest run --coverage" }
```

## 2. 单元边界：测服务层，Mock 仓储

**原则**：单元测试的对象是"一段业务规则的输入输出"，其外部依赖（数据库、缓存、HTTP）全部替换为受控替身。入门项目的 `todo-service` 不感知 Express，正好是理想被测对象。

```typescript
// tests/setup.ts —— 全局 Mock Prisma，测试永不触碰真实数据库
import { vi } from 'vitest';

vi.mock('../src/lib/prisma.js', () => ({
  prisma: {
    todo: {
      findMany: vi.fn(),
      findUnique: vi.fn(),
      update: vi.fn(),
      create: vi.fn(),
      deleteMany: vi.fn(),
      count: vi.fn(),
    },
    // $transaction 接收数组时并发执行各查询（与 Prisma 数组形式语义一致）
    $transaction: vi.fn((ops: Promise<unknown>[]) => Promise.all(ops)),
    $queryRaw: vi.fn(),
  },
}));
```

```typescript
// tests/todo-service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { prisma } from '../src/lib/prisma.js';
import { listTodos, toggleTodo } from '../src/services/todo-service.js';
import { HttpError } from '../src/lib/http-error.js';

const mockedTodo = vi.mocked(prisma.todo);

beforeEach(() => {
  vi.clearAllMocks(); // 隔离用例：每个测试从干净状态开始
});

describe('listTodos', () => {
  it('open 状态映射为 done:false 过滤条件', async () => {
    vi.mocked(prisma.$transaction).mockResolvedValue([
      [{ id: 'a', done: false }],
      1,
    ]);

    const result = await listTodos({ status: 'open', page: 1, pageSize: 20 });

    expect(result.items).toHaveLength(1);
    expect(mockedTodo.findMany).toHaveBeenCalledWith(
      expect.objectContaining({ where: { done: false } }),
    );
  });

  it('分页参数正确换算 skip/take', async () => {
    await listTodos({ status: 'all', page: 3, pageSize: 10 });
    expect(mockedTodo.findMany).toHaveBeenCalledWith(
      expect.objectContaining({ skip: 20, take: 10 }),
    );
  });
});

describe('toggleTodo', () => {
  it('任务不存在时抛出 404', async () => {
    mockedTodo.findUnique.mockResolvedValue(null);

    await expect(toggleTodo('missing', true)).rejects.toMatchObject({
      status: 404,
    } satisfies Partial<HttpError>);
  });
});
```

## 3. 什么值得单测，什么不值得

| 值得单测 | 不值得（交给集成测试） |
|---------|----------------------|
| 过滤/分页参数换算 | Prisma 查询语法本身 |
| 错误分支（404/403 逻辑） | 真实 SQL 行为 |
| 令牌轮换、密码比较等规则 | 中间件串接顺序 |
| 工具函数（日期、脱敏、格式化） | HTTP 状态码映射 |

判断标准：**删掉这条测试，回归时它能否拦住一个真实 Bug？** 不能就删。

## 4. 定时器与外部服务的确定性

```typescript
// 冻结时间：令牌过期逻辑测试的关键
import { vi, it, expect } from 'vitest';

it('过期的 refresh token 被拒绝', async () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date('2026-09-01T00:00:00Z'));

  const token = await issueToken({ ttlDays: 7 });
  vi.setSystemTime(new Date('2026-09-30T00:00:00Z')); // 快进 29 天

  await expect(validateToken(token)).rejects.toThrow('已过期');
  vi.useRealTimers();
});
```

## ✅ 最佳实践与陷阱

- ✅ 测试命名描述行为（"分页参数正确换算"）而非函数名
- ✅ `beforeEach` 里 `clearAllMocks`，用例之间零耦合
- ❌ Mock 了被测对象本身——只 Mock 依赖边界
- ❌ 追求 100% 覆盖率：70-80% 且断言有效，远胜注水刷满

## 🔗 相关文档

- 📄 [集成测试：Supertest + 测试数据库](02-integration-testing.md) — 下一层：真实依赖验证
- 📖 [后端生态库精选](../reference/library-guides/02-ecosystem-libs.md) — Vitest 速查
- 📄 [认证服务实战](../projects/02-auth-service.md) — 令牌逻辑是单测最佳素材
- 📖 [Node + TypeScript 常用模式](../reference/language-concepts/05-typescript-patterns.md) — 可注入设计的类型基础
