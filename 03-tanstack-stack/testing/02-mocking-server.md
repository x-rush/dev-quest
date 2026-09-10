# Mock 服务：用 MSW 模拟后端

> **文档简介**: 用 MSW v2 在测试与本地开发中拦截网络请求：同一份 handlers 既服务 Vitest 也服务浏览器 worker，让"没有后端"也能完整联调。
>
> **目标读者**: 需要脱离真实后端测试/开发前端功能的开发者
>
> **前置知识**: [单元测试](./01-unit-testing.md)、[Query 基础](../frameworks/01-tanstack-query-basics.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#msw` `#mock` `#测试` `#服务模拟` |
| **更新日期** | 2026年9月 |

## 🎯 完成后你将能够

- 编写 MSW v2 handlers 并接入 Vitest
- 用 `server.use` 覆盖单测的错误场景
- 在本地开发启动 Service Worker，前端先行

> MSW 的价值：fetch 发出的是**真实 HTTP 请求**，Query 的重试、缓存键序列化等行为与线上完全一致——这是 vi.stubGlobal 做不到的。

---

## 1. 安装与 handlers

```bash
npm install -D msw
```

```ts
// src/mocks/handlers.ts
import { http, HttpResponse, delay } from 'msw'
import type { Todo } from '@/api/todos'

// 模块级内存数据库：多个 handler 之间共享状态
const todos: Todo[] = [{ id: 1, title: '写周报', done: false }]
let nextId = 2

export const handlers = [
  http.get('/api/todos', async () => {
    await delay(50) // 模拟网络延迟，触发 isPending 可见期
    return HttpResponse.json(todos)
  }),

  http.post('/api/todos', async ({ request }) => {
    const body = (await request.json()) as { title: string }
    if (!body.title?.trim()) {
      return HttpResponse.json({ message: '标题不能为空' }, { status: 422 })
    }
    const todo = { id: nextId++, title: body.title, done: false }
    todos.push(todo)
    return HttpResponse.json(todo, { status: 201 })
  }),

  http.patch('/api/todos/:id', async ({ params, request }) => {
    const todo = todos.find((t) => t.id === Number(params.id))
    if (!todo) return HttpResponse.json({ message: 'not found' }, { status: 404 })
    const patch = (await request.json()) as Partial<Todo>
    Object.assign(todo, patch)
    return HttpResponse.json(todo)
  }),

  http.delete('/api/todos/:id', ({ params }) => {
    const i = todos.findIndex((t) => t.id === Number(params.id))
    if (i === -1) return new HttpResponse(null, { status: 404 })
    todos.splice(i, 1)
    return new HttpResponse(null, { status: 204 })
  }),
]
```

**v2 语法要点**：`http.get` 取代 v1 的 `rest.get`；`HttpResponse.json()` 取代 `ctx.json()`；路径参数从 `params` 解构。

---

## 2. 接入 Vitest

```ts
// src/mocks/server.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)
```

```ts
// src/test/setup.ts —— vitest.config.ts 里以 setupFiles 挂载
import { beforeAll, afterEach, afterAll } from 'vitest'
import { server } from '../mocks/server'

beforeAll(() => server.listen({ onUnhandledRequest: 'error' })) // 未匹配请求直接报错，防止测试悄悄打到真后端
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

### 覆盖错误场景

```ts
// src/hooks/use-todos.test.ts
import { server } from '@/mocks/server'
import { http, HttpResponse } from 'msw'
import { it, expect, vi } from 'vitest'

it('500 时重试 2 次后停止', async () => {
  const spy = vi.fn(() => new HttpResponse(null, { status: 500 }))
  server.use(http.get('/api/todos', spy)) // 局部覆盖，仅本用例生效

  // ...渲染 hook 后断言 error.message === '请求失败 500'
  // 顺便断言重试次数：1 次原始 + 2 次重试
  expect(spy).toHaveBeenCalledTimes(3)
})
```

`server.use` 的覆盖在 `resetHandlers` 后自动消失——每个测试拿到干净的网络环境。

---

## 3. 浏览器 Worker：本地开发先行

```bash
npx msw init public --save
```

```ts
// src/mocks/browser.ts
import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

export const worker = setupWorker(...handlers)
```

```ts
// src/main.tsx —— 仅在 mock 模式启用
async function enableMocking() {
  if (import.meta.env.VITE_ENABLE_MOCK !== 'true') return
  const { worker } = await import('./mocks/browser')
  await worker.start({ onUnhandledRequest: 'bypass' })
}

enableMocking().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(<App />)
})
```

```bash
VITE_ENABLE_MOCK=true npm run dev  # 前端先行：后端未就绪也能开发全部页面
```

**收益**：同一份 handlers 同时服务测试与开发；联调日切真实后端只需去掉环境变量。

---

## 4. handlers 设计建议

- ✅ 内存数据库 + 自增 id：POST 后 GET 能看到新数据，支撑"新增后列表刷新"类集成断言
- ✅ `delay(50~200)`：让 isPending 状态真实可见，可测 loading UI
- ✅ 每个资源独立文件（handlers/todos.ts、handlers/users.ts），按资源组织
- ❌ 不要在 handler 里做复杂业务计算——mock 只要"形状正确 + 状态可控"

---

## 🔗 相关文档

- 📄 **[单元测试](./01-unit-testing.md)** - 无网络的更底层测试
- 📄 **[集成测试](./03-integration-testing.md)** - MSW + Testing Library 的组合拳
- 📄 **[端到端测试](./04-e2e-testing.md)** - 真实后端或复用 MSW 的浏览器级验证
- 📄 **[Query 基础](../frameworks/01-tanstack-query-basics.md)** - retry/staleTime 等被测行为出处
- 📄 **[故障排除](../reference/quick-references/02-troubleshooting.md)** - 请求不匹配等问题的排查
