# 入门项目：TODO REST API

## 分阶段练习与验收

**最小阶段**：先完成内存 CRUD，再接数据库。

**验收结果**：非法输入失败、未知 ID 为 404、删除后无法查询。

**扩展顺序**：每个 Promise 失败可追踪，HTTP 与存储测试分开。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> **文档简介**: 独立完成第一个完整的 TODO REST API——Hono 4 + Prisma + Zod + Vitest 的最小组合，覆盖 CRUD、过滤、分页与测试的全流程
>
> **目标读者**: 完成 basics 路径、希望第一次独立交付完整 API 的初学者
>
> **前置知识**: [第一个完整项目](../basics/08-first-project.md)、[Hono 基础](../frameworks/01-hono-basics.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#rest-api` `#hono` `#crud` `#prisma` `#zod` `#入门项目` |
| **更新日期** | `2026年9月` |

</details>

> basics 的任务管理项目已带你走过一遍全流程；本项目是它的**独立拓展练习**——从空白仓库出发，完成带标签、优先级与过滤能力的 TODO API。步骤只给关键代码与决策点，细节自行查字典补齐。

## 🎯 项目目标

- 独立完成"设计 → 建模 → 实现 → 测试"的完整闭环
- 实践统一错误信封与 Zod 请求校验
- 用 Vitest 写出第一批服务层单元测试

## 1. 需求清单

| 能力 | 方法与路径 | 说明 |
|------|-----------|------|
| 建任务 | `POST /todos` | title 必填，priority ∈ low/mid/high，默认 low |
| 查列表 | `GET /todos` | 支持 `?status=&priority=&page=&pageSize=` 过滤分页 |
| 查单个 | `GET /todos/:id` | 不存在返回 404 |
| 改状态 | `PATCH /todos/:id` | 部分更新，只校验提供的字段 |
| 删除 | `DELETE /todos/:id` | 返回 204 |

## 2. 数据建模

```prisma
// prisma/schema.prisma
model Todo {
  id        String    @id @default(cuid())
  title     String
  done      Boolean   @default(false)
  priority  String    @default("low") // low | mid | high，取值校验交给应用层 Zod
  createdAt DateTime  @default(now())

  @@index([done, priority, createdAt]) // 覆盖列表页的过滤+排序
}
```

```bash
pnpm exec prisma migrate dev --name todo-init
```

## 3. 校验层：Zod schema 即文档

```typescript
// src/schemas/todo.ts —— 扁平 schema：处理器里对哪个来源（json/query）调用 parse，
// schema 就描述哪个来源的形状；body/query 分组信封是 zValidator 中间件方案的形态
import { z } from 'zod';

export const createTodoSchema = z.object({
  title: z.string().min(1).max(100),
  priority: z.enum(['low', 'mid', 'high']).default('low'),
});

export const listQuerySchema = z.object({
  status: z.enum(['all', 'open', 'done']).default('all'),
  priority: z.enum(['low', 'mid', 'high']).optional(),
  page: z.coerce.number().int().min(1).default(1),   // query 是 string，自动转型
  pageSize: z.coerce.number().int().min(1).max(50).default(20),
});

export const updateTodoSchema = z.object({
  title: z.string().min(1).max(100).optional(),
  done: z.boolean().optional(),
  priority: z.enum(['low', 'mid', 'high']).optional(),
});
```

## 4. 服务层：业务与框架解耦

```typescript
// src/services/todo-service.ts —— 只依赖 prisma，不感知 Hono
import { prisma } from '../lib/prisma.js';
import { notFound } from '../lib/http-error.js';

interface ListFilter {
  status: 'all' | 'open' | 'done';
  priority?: 'low' | 'mid' | 'high';
  page: number;
  pageSize: number;
}

export async function listTodos(f: ListFilter) {
  const where = {
    ...(f.status !== 'all' && { done: f.status === 'done' }),
    ...(f.priority && { priority: f.priority }),
  };

  const [items, total] = await prisma.$transaction([
    prisma.todo.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      skip: (f.page - 1) * f.pageSize,
      take: f.pageSize,
    }),
    prisma.todo.count({ where }),
  ]);

  return { items, total, page: f.page, pageSize: f.pageSize };
}

export async function toggleTodo(id: string, done: boolean) {
  const todo = await prisma.todo.findUnique({ where: { id } });
  if (!todo) throw notFound(`任务 ${id} 不存在`);
  return prisma.todo.update({ where: { id }, data: { done } });
}

export async function deleteTodo(id: string) {
  const { count } = await prisma.todo.deleteMany({ where: { id } });
  if (count === 0) throw notFound(`任务 ${id} 不存在`);
}
```

## 5. 路由装配

```typescript
// src/routes/todos.ts —— 子应用即路由模块，async rejection 自动进 app.onError
import { Hono } from 'hono';
import * as svc from '../services/todo-service.js';
import {
  createTodoSchema,
  listQuerySchema,
  updateTodoSchema,
} from '../schemas/todo.js';

export const todosApp = new Hono();

todosApp.post('/', async (c) => {
  const { title, priority } = createTodoSchema.parse(await c.req.json());
  return c.json(await svc.createTodo(title, priority), 201);
});

todosApp.get('/', async (c) => {
  const q = listQuerySchema.parse(c.req.query()); // ZodError → 422
  return c.json(await svc.listTodos(q));
});

todosApp.get('/:id', async (c) => {
  return c.json(await svc.getTodo(c.req.param('id')));
});

todosApp.patch('/:id', async (c) => {
  const patch = updateTodoSchema.parse(await c.req.json());
  return c.json(await svc.updateTodo(c.req.param('id'), patch));
});

todosApp.delete('/:id', async (c) => {
  await svc.deleteTodo(c.req.param('id'));
  return c.body(null, 204); // 删除成功无响应体
});

// 装配：app.route('/todos', todosApp)
```

## 6. 验收与测试

```bash
curl -X POST localhost:3000/todos -H 'Content-Type: application/json' \
  -d '{"title":"写周报","priority":"high"}'
curl 'localhost:3000/todos?status=open&priority=high&page=1'
```

用 Vitest 给服务层写第一批测试（不启 HTTP，直连测试库）：

```typescript
// tests/todo-service.test.ts
import { describe, it, expect } from 'vitest';
import { listTodos } from '../src/services/todo-service.js';

describe('listTodos', () => {
  it('按 status=done 过滤', async () => {
    const result = await listTodos({ status: 'done', page: 1, pageSize: 20 });
    expect(result.items.every((t) => t.done)).toBe(true);
  });
});
```

完整测试方法见 [`../testing/01-unit-testing.md`](../testing/01-unit-testing.md)。

## ✅ 完成自检

- [ ] 全部 5 个端点通过 curl 手工验收
- [ ] 非法 priority 返回 422 而非 500
- [ ] 删除不存在的 id 返回 404
- [ ] 至少 3 条服务层测试通过

## 🔗 相关文档

- 📄 [第一个完整项目：任务管理 REST API](../basics/08-first-project.md) — 本项目的教学版原型
- 📄 [Hono 基础](../frameworks/01-hono-basics.md) — 路由与中间件写法
- 📄 [生态集成](../frameworks/03-ecosystem-integration.md) — Prisma 连接与事务细节
- 📄 [认证服务实战](02-auth-service.md) — 下一个难度⭐⭐项目


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
