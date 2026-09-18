# 入门项目：Todo App（Query CRUD 标准范式）

## 分阶段练习与验收

**最小阶段**：先以 Query 完成列表读取与一条创建操作。

**验收结果**：空输入失败，创建成功后重取可见，错误状态可重试。

**扩展顺序**：模拟后端须明确是否保存数据；确认持久化后再加乐观更新。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> **文档简介**: 从零构建一个 Todo 应用，完整走通"读取-创建-更新-删除"四类操作在 TanStack Query v5 下的标准写法，建立 Query 项目的骨架感。
>
> **目标读者**: 刚学完 Query 基础、需要第一个完整练手项目的初级开发者
>
> **前置知识**: [Query 基础](../frameworks/01-tanstack-query-basics.md)、[环境搭建](../basics/01-environment-setup.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#实战项目` `#tanstack-query` `#crud` `#react19` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 项目目标

- 用 Vite 搭建 React 19 + TypeScript 项目并接入 Query v5
- 实现 Todo 的列表展示、新增、勾选完成、删除
- 每个写操作后缓存自动同步，UI 无需手动刷新

---

## 1. 初始化

```bash
npm create vite@latest todo-app -- --template react-ts
cd todo-app && npm install
npm install @tanstack/react-query@^5
```

入口文件接入 Provider（配置细节见 [Query 基础](../frameworks/01-tanstack-query-basics.md)）：

```tsx
// src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, gcTime: 5 * 60_000 } },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)
```

---

## 2. 数据层：类型、API 与 Query Key 工厂

把"键"集中管理，避免魔法字符串散落各处——这是大型 Query 项目的第一习惯：

```ts
// src/api/todos.ts
export interface Todo {
  id: number
  title: string
  done: boolean
}

// Query Key 工厂：键的唯一事实来源
export const todoKeys = {
  all: ['todos'] as const,
  lists: () => [...todoKeys.all, 'list'] as const,
  details: () => [...todoKeys.all, 'detail'] as const,
  detail: (id: number) => [...todoKeys.details(), id] as const,
}

const BASE = '/api/todos'
async function http<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) throw new Error(`请求失败 ${res.status}`)
  return res.json()
}

export const todoApi = {
  list: () => http<Todo[]>(BASE),
  create: (title: string) =>
    http<Todo>(BASE, { method: 'POST', body: JSON.stringify({ title }) }),
  toggle: (todo: Todo) =>
    http<Todo>(`${BASE}/${todo.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ done: !todo.done }),
    }),
  remove: (id: number) => http<void>(`${BASE}/${id}`, { method: 'DELETE' }),
}
```

**键工厂的收益**：`invalidateQueries({ queryKey: todoKeys.all })` 一行失效列表与所有详情；将来加筛选只需扩展 `lists()`。

---

## 3. Hooks 层：1 个查询 + 3 个变更

```ts
// src/hooks/use-todos.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { todoApi, todoKeys } from '../api/todos'

export function useTodos() {
  return useQuery({ queryKey: todoKeys.lists(), queryFn: todoApi.list })
}

export function useAddTodo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: todoApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: todoKeys.lists() }),
  })
}

export function useToggleTodo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: todoApi.toggle,
    onSuccess: () => qc.invalidateQueries({ queryKey: todoKeys.all }), // 列表与详情都受影响
  })
}

export function useDeleteTodo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: todoApi.remove,
    onSuccess: (_data, id) => {
      // 精确清理：先移除已删条目的详情缓存，再刷新列表
      qc.removeQueries({ queryKey: todoKeys.detail(id) })
      qc.invalidateQueries({ queryKey: todoKeys.lists() })
    },
  })
}
```

---

## 4. UI 层组装

```tsx
// src/App.tsx
import { useState } from 'react'
import { useTodos, useAddTodo, useToggleTodo, useDeleteTodo } from './hooks/use-todos'

export default function App() {
  const [title, setTitle] = useState('')
  const { isPending, isError, error, data: todos } = useTodos()
  const addTodo = useAddTodo()
  const toggleTodo = useToggleTodo()
  const deleteTodo = useDeleteTodo()

  if (isPending) return <p>加载中…</p>          // v5：isPending 时 data 类型收窄为 undefined，先判空再渲染
  if (isError) return <p role="alert">{error.message}</p>

  return (
    <main>
      <h1>Todo App</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault()
          if (!title.trim()) return
          addTodo.mutate(title, { onSuccess: () => setTitle('') })
        }}
      >
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="新任务…" />
        <button type="submit" disabled={addTodo.isPending}>添加</button>
      </form>

      <ul>
        {todos.map((todo) => (
          <li key={todo.id}>
            <label>
              <input
                type="checkbox"
                checked={todo.done}
                onChange={() => toggleTodo.mutate(todo)}
              />
              <span style={{ textDecoration: todo.done ? 'line-through' : 'none' }}>
                {todo.title}
              </span>
            </label>
            <button onClick={() => deleteTodo.mutate(todo.id)}>删除</button>
          </li>
        ))}
      </ul>
    </main>
  )
}
```

---

## ❓ 常见坑

| 现象 | 原因 | 修复 |
|------|------|------|
| 新增后列表不刷新 | onSuccess 忘记 invalidate | 检查 mutation 的 onSuccess |
| 列表闪烁 | staleTime 为 0，每次挂载都重取 | 给查询配置 staleTime |
| TS 报 `isLoading` 不存在 | 误用过时 API | 主要分支改用 `isPending` |

---

## 🔗 相关文档

- 📄 **[Query 基础](../frameworks/01-tanstack-query-basics.md)** - 本文所有写法的依据
- 📄 **[Query 核心 API](../reference/language-concepts/01-query-core-api.md)** - 参数字典
- 📄 **[第一个项目：城市天气数据面板](../basics/08-first-project.md)** - 只读版入门项目
- 📄 **[单元测试](../testing/01-unit-testing.md)** - 给本文的 hooks 补上测试
- 📄 **[数据看板](../projects/02-data-dashboard.md)** - 下一站：服务端分页表格


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
