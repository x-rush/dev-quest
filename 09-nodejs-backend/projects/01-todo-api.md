# 入门项目：TODO REST API

## 分阶段练习与验收

**最小阶段**：在已验收的基础项目上追加 Todo 模型，先完成创建与查询，再补更新、删除和过滤。

**验收结果**：非法输入失败、未知 ID 为 404、删除后无法查询。

**扩展顺序**：每个 Promise 失败可追踪，HTTP 与存储测试分开。

本练习复用 [基础项目](../basics/08-first-project.md) 的 Prisma 配置、数据库客户端、错误类型、错误出口与 TypeScript 执行配置。保留原有 Task 作为练习对照，在 schema 中追加本页 Todo，新增 `/todos` 子应用，再执行迁移和客户端生成。先通过基础项目测试，才开始本扩展。

### 从基础工程进入本项目

- **前置验收**：在自己的练习环境完成基础项目的客户端生成、迁移与 4 项测试，并保存实际结果；基础项目中的预期结果或安装失败记录不能代替这一步。
- **本次产物**：保留 `Task` 与 `/api/tasks`，新增 Todo 迁移、schema、服务、`/todos` 路由及独立测试。沿用 Prisma 客户端和 `app.onError`；将基础项目 `readJson` 提取为共用函数后供两个路由使用。
- **边界变化**：Task 的字符串状态与 Todo 的 `done` 布尔值是两套模型；不要复制 Task 数据后直接改字段名。正文直接使用 Prisma，内存实现不属于本页必做阶段。
- **通过条件**：原有 4 项测试继续通过；第 6 节专用测试库检查通过；创建后按返回 ID 查回，非法 priority、损坏 JSON、空 PATCH 返回 400 且数据不变，未知 ID 返回 404。将命令、状态码和输出保存在练习仓库。
- **失败回查**：客户端缺少 `todo` 时回到本页迁移与生成步骤；路由 404 时核对 `createApp` 的挂载位置；错误变成 500 时回查[基础项目](../basics/08-first-project.md)的 JSON 边界和错误出口。
- **下一步**：以上验收完成后进入[认证服务](./02-auth-service.md)，先完成登录与受保护资源访问，再加刷新令牌轮换。

这些是需要在目标练习环境执行的验收要求；补充桥接说明本身不代表本页工程已经运行通过。

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

> basics 的任务管理项目已带你走过一遍全流程；本项目是在该工程上完成的**拓展练习**，新增优先级、完成状态过滤与分页。步骤只给关键代码与决策点，细节自行查字典补齐；标签不在本页的数据模型和验收范围内。

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
pnpm exec prisma generate
pnpm add -D vitest
```

## 3. 校验层：Zod schema 即文档

```typescript
// src/schemas/todo.ts —— 扁平 schema：处理器里对哪个来源（json/query）调用 parse，
// schema 就描述哪个来源的形状；body/query 分组信封是 zValidator 中间件方案的形态
import { z } from 'zod';

export const createTodoSchema = z.object({
  title: z.string().trim().min(1).max(100),
  priority: z.enum(['low', 'mid', 'high']).default('low'),
});

export const listQuerySchema = z.object({
  status: z.enum(['all', 'open', 'done']).default('all'),
  priority: z.enum(['low', 'mid', 'high']).optional(),
  page: z.coerce.number().int().min(1).default(1),   // query 是 string，自动转型
  pageSize: z.coerce.number().int().min(1).max(50).default(20),
});

export const updateTodoSchema = z.strictObject({
  title: z.string().trim().min(1).max(100).optional(),
  done: z.boolean().optional(),
  priority: z.enum(['low', 'mid', 'high']).optional(),
}).refine((value) => Object.keys(value).length > 0, '至少提供一个更新字段');
```

## 4. 服务层：业务与框架解耦

```typescript
// src/services/todo-service.ts —— 只依赖 prisma，不感知 Hono
import { prisma } from '../lib/prisma.js';
import { HttpError } from '../lib/errors.js';

const notFound = (message: string) => new HttpError(404, message, 'TODO_NOT_FOUND');

export function createTodo(title: string, priority: 'low' | 'mid' | 'high') {
  return prisma.todo.create({ data: { title, priority } });
}

export async function getTodo(id: string) {
  const todo = await prisma.todo.findUnique({ where: { id } });
  if (!todo) throw notFound(`任务 ${id} 不存在`);
  return todo;
}

export function updateTodo(id: string, data: { title?: string; done?: boolean; priority?: 'low' | 'mid' | 'high' }) {
  return prisma.todo.update({ where: { id }, data }); // 原子更新；P2025 由共用错误出口映射 404
}

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
  return updateTodo(id, { done });
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
  const q = listQuerySchema.parse(c.req.query()); // 沿用基础项目：ZodError → 400
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

// 在 src/app.ts 导入 todosApp，并在 createApp 内调用 app.route('/todos', todosApp)
```

本页路由里的 `c.req.json()` 也应换成基础项目的 `readJson`（提取为 `src/lib/read-json.ts` 后导入），让损坏 JSON 明确返回 400。不要全局把任意 `SyntaxError` 改成客户端错误，因为内部 JSON 处理缺陷也可能抛出同类异常。

## 6. 验收与测试

```bash
curl -X POST localhost:3000/todos -H 'Content-Type: application/json' \
  -d '{"title":"写周报","priority":"high"}'
curl 'localhost:3000/todos?status=open&priority=high&page=1'
```

用 Vitest 给服务层写第一批测试（不启 HTTP，直连测试库）：

```typescript
// tests/todo-service.test.ts
import { describe, it, expect, beforeEach, afterAll } from 'vitest';
import { listTodos } from '../src/services/todo-service.js';
import { prisma } from '../src/lib/prisma.js';

if (process.env.DATABASE_URL !== 'file:./prisma/test.db') throw new Error('仅允许使用专用测试库');
beforeEach(async () => {
  await prisma.todo.deleteMany();
  await prisma.todo.createMany({ data: [
    { title: '完成项', done: true, priority: 'low' },
    { title: '未完成项', done: false, priority: 'high' },
  ] });
});
afterAll(() => prisma.$disconnect());

describe('listTodos', () => {
  it('按 status=done 过滤', async () => {
    const result = await listTodos({ status: 'done', page: 1, pageSize: 20 });
    expect(result.total).toBe(1);
    expect(result.items.map((t) => t.title)).toEqual(['完成项']);
  });
});
```

完整测试方法见 [`../testing/01-unit-testing.md`](../testing/01-unit-testing.md)。

先设置基础项目中的专用 `DATABASE_URL`，运行 `pnpm exec prisma migrate deploy` 与 `pnpm exec vitest run tests/todo-service.test.ts --no-file-parallelism`。断言“所有返回项都完成”会让空数组误通过，因此必须同时断言结果数量和已知样本。继续补充未知 ID 更新/删除、无效 PATCH、分页上限与创建后重启可查回的测试。

## ✅ 完成自检

- [ ] 全部 5 个端点通过 curl 手工验收
- [ ] 非法 priority、损坏 JSON 与空 PATCH 返回 400，且不改变数据库
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
