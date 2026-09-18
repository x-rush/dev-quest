# 集成测试：Testing Library 与 renderHook

> **文档简介**: 用 Testing Library + renderHook 验证"Hook + 组件 + 缓存"的协作行为：每个测试独享 QueryClient、关闭重试、等待异步收敛。
>
> **目标读者**: 已会用 MSW，需要验证用户可见行为的开发者
>
> **前置知识**: [Mock 服务](./02-mocking-server.md)、[单元测试](./01-unit-testing.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#testing-library` `#renderhook` `#集成测试` `#react19` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 完成后你将能够

- 为 Hook 测试搭一个"每测试独立 QueryClient"的 Wrapper
- 测试 useQuery/useMutation 驱动的完整组件交互
- 避免测试间缓存泄漏与 act 警告

> 测试环境三原则：**独立 client、关掉 retry、关掉 refetchOnWindowFocus**——否则用例互相污染且随机变慢。

---

## 1. 环境与工具安装

```bash
npm install -D vitest jsdom @testing-library/react @testing-library/user-event @testing-library/dom @testing-library/jest-dom
```

```ts
// vitest.config.ts（增量修改）
import { defineConfig } from 'vitest/config'
export default defineConfig({
  // ...
  test: {
    environment: 'jsdom', // 集成测试需要 DOM
    setupFiles: ['src/test/setup.ts'], // MSW server + cleanup 都在这
    globals: true,
  },
})
```

---

## 2. Wrapper：每测试一个新 QueryClient

```tsx
// src/test/utils.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, renderHook, type RenderOptions } from '@testing-library/react'
import type { ReactElement, ReactNode } from 'react'

export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: Infinity, staleTime: 0, refetchOnWindowFocus: false }, // 测试不重试；gcTime Infinity 防意外回收
      mutations: { retry: false },
    },
  })
}

export function createWrapper(client: QueryClient) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>
  }
}

// 组件渲染的便捷封装：自动带上独立 client
export function renderWithClient(ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) {
  const client = createTestQueryClient()
  return { client, ...render(ui, { wrapper: createWrapper(client), ...options }) }
}

// Hook 渲染同理
export function renderHookWithClient<TResult>(
  callback: () => TResult,
) {
  const client = createTestQueryClient()
  return { client, ...renderHook(callback, { wrapper: createWrapper(client) }) }
}
```

**为什么必须每测试新建 client**：QueryClient 内部有缓存与订阅状态。复用会让上一个用例的缓存/失效影响下一个用例，产生"单跑过、全跑挂"的经典问题。

---

## 3. 测试自定义 Query Hook

```tsx
// src/hooks/use-todos.test.tsx
import { describe, it, expect } from 'vitest'
import { waitFor } from '@testing-library/react'
import { useTodos } from './use-todos'
import { server } from '@/mocks/server'
import { http, HttpResponse } from 'msw'
import { renderHookWithClient } from '@/test/utils'

describe('useTodos', () => {
  it('加载成功：isPending 先为 true，随后返回数据', async () => {
    const { result } = renderHookWithClient(() => useTodos())

    // MSW handlers 带 delay(50)，首轮渲染应处于 isPending
    expect(result.current.isPending).toBe(true)

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toHaveLength(1)
  })

  it('错误分支：断言 error 携带状态码信息', async () => {
    server.use(http.get('/api/todos', () => new HttpResponse(null, { status: 500 })))
    const { result, client, unmount } = renderHookWithClient(() => useTodos())
    try {
      await waitFor(() => expect(result.current.isError).toBe(true))
      expect(result.current.error).toBeInstanceOf(Error)
    } finally { unmount(); client.clear() }
  })
})
```

在 `src/test/setup.ts` 加入 `import '@testing-library/jest-dom/vitest'`，让后文 toHaveStyle 等匹配器可用。

**断言要点**：永远 `await waitFor(...)` 收敛后再断言数据；不要在 isPending 阶段断言 `data === undefined` 之外的太多东西。

---

## 4. 测试组件级交互（查询 + 变更闭环）

```tsx
// src/App.test.tsx
import { describe, it, expect } from 'vitest'
import userEvent from '@testing-library/user-event'
import { screen, waitFor } from '@testing-library/react'
import App from './App'
import { renderWithClient } from '@/test/utils'

describe('Todo App 集成', () => {
  it('添加 todo 后列表自动出现新条目（mutation → invalidate → refetch）', async () => {
    const user = userEvent.setup()
    renderWithClient(<App />)

    // 初始列表来自 MSW 种子数据
    await screen.findByText('写周报')

    await user.type(screen.getByPlaceholderText('新任务…'), '学集成测试')
    await user.click(screen.getByRole('button', { name: '添加' }))

    // invalidate 触发重新请求 → MSW 内存库返回两条
    await screen.findByText('学集成测试')
  })

  it('勾选 todo 划线显示（乐观 UI 不需要等网络）', async () => {
    const user = userEvent.setup()
    renderWithClient(<App />)
    await screen.findByText('写周报')

    await user.click(screen.getByRole('checkbox'))
    await waitFor(() => expect(screen.getByText('写周报')).toHaveStyle({ textDecoration: 'line-through' }))
  })
})
```

---

## 5. 常见报错速修

| 报错 | 原因 | 修复 |
|------|------|------|
| "No QueryClient set" | 渲染没包 Wrapper | 用 renderWithClient / renderHookWithClient |
| 用例间缓存串数据 | 复用了全局 client | 每测试 createTestQueryClient |
| act(...) 警告 | 断言发生在状态收敛前 | 用 waitFor/findBy 包住 |
| 测试莫名超时 | retry 默认 3 次叠加 delay | 测试 client 配 retry: false |

---

<!-- full-library-explanation -->
## 验证协作行为，而不只验证一个成功画面

先修：MSW handlers、QueryClientProvider、Testing Library。一次“添加后出现新任务”测试应覆盖输入→mutation→服务端替身状态变化→失效→列表更新。若只是提前把新任务塞进缓存，无法证明这条链成立。

每个用例独立 client，结束时卸载组件并清理 client；MSW handler 与模拟数据库也分别重置。测试特定重试策略时可以在该用例打开 retry，其他错误测试关闭重试以减少等待。

findBy 等待元素出现，waitFor 重试断言。不要在 waitFor 回调中反复点击或输入，否则每次重试都会重复执行用户动作。act 警告也可能来自未结束的定时器、卸载后的任务或漏 await，不能只靠把全部代码包 waitFor 消除。

**练习：** 在新增成功后补充新增失败用例，确认错误提示、输入保留、重复提交控制；再补勾选失败回滚。验收：用户看到的状态与模拟后端最终状态一致，所有错误用例都有实际断言。

本文 App/useTodos 由项目实现提供；没有这些实现时，这些是集成用例模板，不能宣称已直接执行通过。相关缓存行为已有本库验证脚本单独记录，二者范围不同。

## 🔗 相关文档

- 📄 **[Mock 服务](./02-mocking-server.md)** - 本文所有请求的来源
- 📄 **[单元测试](./01-unit-testing.md)** - 更底层的纯逻辑验证
- 📄 **[端到端测试](./04-e2e-testing.md)** - 真实浏览器层的最后一道关
- 📄 **[协作看板](../projects/03-collaborative-kanban.md)** - 拖拽/SSE 行为的本层测法
- 📄 **[Query 核心 API](../reference/language-concepts/01-query-core-api.md)** - isPending 等状态语义字典


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
