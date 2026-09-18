# 单元测试：Vitest 实践

> **文档简介**: 用 Vitest 为 Node 后端建立单元测试体系——服务层测试、Prisma/Redis 的 Mock 策略与覆盖率门槛，让业务逻辑在毫秒级反馈中迭代
>
> **目标读者**: 已能独立写 API、需要建立测试习惯的后端开发者
>
> **前置知识**: [服务层解耦](../projects/01-todo-api.md) 的目录结构、TypeScript 基础

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#vitest` `#unit-testing` `#mock` `#coverage` |
| **更新日期** | `2026年9月` |

</details>

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

**原则**：单元测试的对象是"一段业务规则的输入输出"，其外部依赖（数据库、缓存、HTTP）全部替换为受控替身。入门项目的 `todo-service` 不感知 Hono（路由层之外的纯 TS 模块），正好是理想被测对象。

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

测试断言参数如何变成结果，例如分页输入被正确校验与换算。mock 清理要区分调用历史、实现和恢复原函数，clearAllMocks 不会替你清理数据库、全局状态或所有实现。

覆盖率用于发现未触及的代码，不设通用 70–80% 合格线；高风险分支仍应有有效断言。让一个故意的业务错误能使测试失败，比为了数字执行更多无断言代码有意义。

## 🔗 相关文档

- 📄 [集成测试：app.request() + 测试数据库](02-integration-testing.md) — 下一层：真实依赖验证
- 📖 [后端生态库精选](../reference/library-guides/02-ecosystem-libs.md) — Vitest 速查
- 📄 [认证服务实战](../projects/02-auth-service.md) — 令牌逻辑是单测最佳素材
- 📖 [Node + TypeScript 常用模式](../reference/language-concepts/05-typescript-patterns.md) — 可注入设计的类型基础


<!-- acceptance-exercise -->
## 练习与验收：检查断言是否会拒绝错误行为

为输入验证或状态转换写正常、边界和失败三个案例。先让被测函数始终返回成功，至少失败案例必须变红；恢复后全部通过。异步测试必须等待 Promise，故意延后一次拒绝仍应被测试框架捕获。验收中测试不访问真实网络、不依赖当前时间和随机值，且单独执行与整套执行一致。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
