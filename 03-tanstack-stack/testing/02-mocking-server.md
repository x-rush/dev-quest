# Mock 服务：用 MSW 模拟后端

> **文档简介**: 用 MSW v2 在测试与本地开发中拦截网络请求：同一份 handlers 既服务 Vitest 也服务浏览器 worker，让"没有后端"也能完整联调。
>
> **目标读者**: 需要脱离真实后端测试/开发前端功能的开发者
>
> **前置知识**: [单元测试](./01-unit-testing.md)、[Query 基础](../frameworks/01-tanstack-query-basics.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#msw` `#mock` `#测试` `#服务模拟` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 完成后你将能够

- 编写 MSW v2 handlers 并接入 Vitest
- 用 `server.use` 覆盖单测的错误场景
- 在本地开发启动 Service Worker，前端先行

> MSW 的价值：应用仍走 fetch 等请求代码，MSW 在请求边界返回模拟响应；可以覆盖 Query 与请求层协作，但不能证明真实后端和线上网络行为。

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

export function resetTodos() {
  todos.splice(0, todos.length, { id: 1, title: '写周报', done: false })
  nextId = 2
}

export const handlers = [
  http.get('/api/todos', async () => {
    await delay(50) // 模拟网络延迟，触发 isPending 可见期
    return HttpResponse.json(todos)
  }),

  http.post('/api/todos', async ({ request }) => {
    const body = (await request.json()) as { title: string }
    if (typeof body.title !== 'string' || !body.title.trim()) {
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
    if (typeof patch.done === 'boolean') todo.done = patch.done
    if (typeof patch.title === 'string' && patch.title.trim()) todo.title = patch.title.trim()
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
import { resetTodos } from '../mocks/handlers'

beforeAll(() => server.listen({ onUnhandledRequest: 'error' })) // 未匹配请求直接报错，防止测试悄悄打到真后端
afterEach(() => { server.resetHandlers(); resetTodos() })
afterAll(() => server.close())
```

### 覆盖错误场景

```ts
// src/hooks/use-todos.test.ts
import { server } from '@/mocks/server'
import { http, HttpResponse } from 'msw'
import { it, expect, vi } from 'vitest'
import { QueryClient } from '@tanstack/react-query'

it('500 时重试 2 次后停止', async () => {
  const spy = vi.fn(() => new HttpResponse(null, { status: 500 }))
  server.use(http.get('http://localhost/api/todos', spy)) // 局部覆盖，仅本用例生效

  const client = new QueryClient({ defaultOptions: { queries: { retry: 2, retryDelay: 0 } } })
  try {
    await expect(client.fetchQuery({
      queryKey: ['retry-demo'],
      queryFn: async () => {
        const response = await fetch('http://localhost/api/todos')
        if (!response.ok) throw new Error(`请求失败 ${response.status}`)
        return response.json()
      },
    })).rejects.toThrow('请求失败 500')
    expect(spy).toHaveBeenCalledTimes(3)
  } finally { client.clear() }
})
```

`server.use` 的覆盖在 `resetHandlers` 后自动消失——覆盖的 handler 被移除；内存数据库还需要显式 resetTodos。

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

```tsx
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
VITE_ENABLE_MOCK=true npm run dev  # Bash；PowerShell 用下方写法
```

PowerShell：`$env:VITE_ENABLE_MOCK = 'true'` 后执行 `npm run dev`。

**收益**：同一份 handlers 同时服务测试与开发；联调日切真实后端只需去掉环境变量。

---

## 4. handlers 设计建议

- ✅ 内存数据库 + 自增 id：POST 后 GET 能看到新数据，支撑"新增后列表刷新"类集成断言
- ✅ `delay(50~200)`：让 isPending 状态真实可见，可测 loading UI
- ✅ 每个资源独立文件（handlers/todos.ts、handlers/users.ts），按资源组织
- ❌ 不要在 handler 里做复杂业务计算——mock 只要"形状正确 + 状态可控"

---

<!-- full-library-explanation -->
## 网络替身与业务数据的重置边界

先修：fetch、HTTP 状态、测试生命周期。MSW 拦截请求并提供替身响应，使应用继续使用真实请求代码；它不代表请求经过了真实服务器、TLS、数据库或生产网络。

resetHandlers 只恢复 handler 列表，不重置模块中的 todos/nextId。每个用例还应调用 resetTodos；并发用例不要共用可变的内存数据库，必要时按测试创建独立状态。

相对 URL 在浏览器有页面 origin，在纯 Node fetch 中通常需要绝对地址。测试应固定服务基址，并让应用请求和 handler 使用同一契约。未匹配请求设 error，有助于发现路径拼错；开发模式 bypass 则允许明确不模拟的请求通过。

**练习：** 第一个用例新增任务，第二个用例仍断言初始只有一条；去掉 resetTodos 后应能复现污染。再覆盖 GET 返回 500，确认请求层因 response.ok 为 false 抛错。验收：失败分支确实执行断言，未匹配请求不会悄悄访问真实业务服务。

运行示例前需要实际 Todo 类型、Query Hook 与 Vitest 配置；本文是这些模块的接入说明，不把省略实现的片段算作通过测试。参考 [MSW resetHandlers](https://mswjs.io/docs/api/setup-server/reset-handlers/)。

## 🔗 相关文档

- 📄 **[单元测试](./01-unit-testing.md)** - 无网络的更底层测试
- 📄 **[集成测试](./03-integration-testing.md)** - MSW + Testing Library 的组合拳
- 📄 **[端到端测试](./04-e2e-testing.md)** - 真实后端或复用 MSW 的浏览器级验证
- 📄 **[Query 基础](../frameworks/01-tanstack-query-basics.md)** - retry/staleTime 等被测行为出处
- 📄 **[故障排除](../reference/quick-references/02-troubleshooting.md)** - 请求不匹配等问题的排查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
