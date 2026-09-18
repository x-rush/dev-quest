# TanStack Query 基础：QueryClient 配置与核心用法

## 先看框架承担哪部分职责

**Query 配置**：QueryClient 的默认项影响一组查询，单个查询可以覆盖。需要先确定缓存生命周期与失败策略，再把参数写进配置。

**最小练习与预期结果**：同一查询键在两个组件中读取，移除一个再重新挂载；用 Devtools 区分条目保留、数据陈旧与正在请求。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 在真实项目中落地 TanStack Query v5：完成 QueryClient 的生产级配置，掌握 useQuery 与 useMutation 的标准用法与键设计。
>
> **目标读者**: 已了解 Query 基本概念、需要在项目中实际接入的 React 19 开发者
>
> **前置知识**: React Hooks 基础、TypeScript 基础、[Query 基础教程](../basics/03-query-fundamentals.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#tanstack-query` `#react19` `#queryclient` `#usequery` `#usemutation` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 完成后你将能够

- 正确创建并配置一个全局唯一的 QueryClient
- 用 useQuery 完成读取：区分 isPending / isError / isSuccess 三个分支
- 用 useMutation 完成写入，并在成功后让缓存失效
- 设计出可缓存、可失效的 Query Key

> 概念定义与参数字典见 [Query 核心 API](../reference/language-concepts/01-query-core-api.md)，本文只讲"怎么用"。

---

## 1. 安装与 QueryClient 配置

```bash
npm install @tanstack/react-query@^5
```

QueryClient 是整个应用的缓存容器，**一个应用只创建一次**，通常放在入口文件：

```tsx
// src/main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

// 生产级默认值：宁可"多调一次接口"，也不要让用户看到脏数据
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,          // 数据 60 秒内视为新鲜，不重复请求
      gcTime: 5 * 60_000,         // 无观察者后 5 分钟才回收缓存（cacheTime 已在 v5 移除）
      retry: 2,                   // 失败自动重试 2 次（指数退避）
      refetchOnWindowFocus: true, // 回到标签页时校验数据
    },
    mutations: {
      retry: 0,                   // 写操作默认不重试，避免重复创建
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* Provider 必须包裹在所有用到 Hook 的组件之外 */}
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)
```

---

## 2. useQuery：读取数据

```tsx
// src/features/todos/use-todos.ts
import { useQuery } from '@tanstack/react-query'

export interface Todo {
  id: number
  title: string
  done: boolean
}

// API 层与 Hook 层分离：queryFn 只负责"取数据"，方便测试与复用
async function fetchTodos(): Promise<Todo[]> {
  const res = await fetch('/api/todos')
  if (!res.ok) throw new Error(`加载失败: ${res.status}`) // 抛错才会进入 isError 分支
  return res.json()
}

// 键是数组：['资源名', ...参数]，后续失效与筛选都靠它
export function useTodos() {
  return useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  })
}
```

组件中按三分支渲染：

```tsx
function TodoList() {
  const { isPending, isError, error, data } = useTodos()

  if (isPending) return <p>加载中…</p>        // v5：isPending 时 data 类型收窄为 undefined，判空后再渲染
  if (isError) return <p role="alert">出错了：{error.message}</p>

  return (
    <ul>
      {data.map((todo) => (
        <li key={todo.id}>{todo.title}</li>
      ))}
    </ul>
  )
}
```

**注意 v5 命名与类型**：`isPending`（尚无数据）是主要判断分支，且此状态下 `data` 类型收窄为 `undefined`，先判空再渲染才能通过 TS 检查；`isLoading` 等价于 `isPending && isFetching`。参数上 `cacheTime` 已在 v5 移除，只有 `gcTime`。

---

## 3. useMutation：写入数据

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { Todo } from './use-todos'

async function createTodo(input: { title: string }): Promise<Todo> {
  const res = await fetch('/api/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!res.ok) throw new Error('创建失败')
  return res.json()
}

export function useCreateTodo() {
  const queryClient = useQueryClient() // 在 Hook 里拿到全局 client

  return useMutation({
    mutationFn: createTodo,
    onSuccess: () => {
      // 让 ['todos'] 缓存失效 → 活跃的 useQuery 自动重新请求
      void queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
    onError: (err) => {
      // 统一错误提示，组件里也可以再单独处理
      console.error('创建 todo 失败', err)
    },
  })
}
```

调用端永远通过 `mutate`（或异步场景用 `mutateAsync`）触发：

```tsx
function AddTodoForm() {
  const createTodo = useCreateTodo()

  return (
    <button
      onClick={() => createTodo.mutate({ title: '学习 Query v5' })}
      disabled={createTodo.isPending} // mutation 的加载态也叫 isPending
    >
      {createTodo.isPending ? '提交中…' : '添加'}
    </button>
  )
}
```

---

## 4. Query Key 设计原则

键是缓存的地址，也是失效的坐标。三条原则：

1. **自下而上**：从最粗粒度到最细粒度 —— `['todos']` → `['todos', 'list', { filter }]` → `['todos', 'detail', id]`
2. **所有影响结果的变量都要进键**：分页、筛选、排序都写进键的对象部分
3. **键做前缀失效**：`invalidateQueries({ queryKey: ['todos'] })` 会同时失效列表和所有详情

```ts
// 带参数的查询：对象放在键的最后一段
export function useTodoDetail(id: number) {
  return useQuery({
    queryKey: ['todos', 'detail', id], // id 变化 → 生成新的缓存条目
    queryFn: () => fetchTodo(id),
    enabled: id > 0, // 条件查询：id 无效时不发起请求
  })
}
```

---

## 🎨 最佳实践速查

queryKey 描述结果的身份：分页、筛选条件、租户等会改变结果的输入都应进入键。可序列化对象可以作为键的一部分，新建但内容等价的对象不会仅因引用变化就变成另一份缓存；函数等不能稳定序列化的值则不适合。见[官方查询键规则](https://tanstack.com/query/latest/docs/framework/react/guides/query-keys)。

写入成功后有两条常用路径：接口返回完整新对象时可用 setQueryData 更新对应缓存；返回信息不足或影响多份列表时，可使相关查询失效并重取。两者按结果契约选，不必禁用其中之一。将多处复用的键和请求逻辑集中维护，并验证更新详情后列表也一致；v5 的 isLoading 仍存在，其含义要与 isPending、isFetching 区分。

---

## 🔗 相关文档

- 📄 **[Query 基础教程](../basics/03-query-fundamentals.md)** - 概念入门，本文的预备阅读
- 📄 **[Query 核心 API](../reference/language-concepts/01-query-core-api.md)** - useQuery / useMutation 全量参数字典
- 📄 **[缓存键、staleTime 与失效策略](../reference/framework-essentials/01-query-essentials.md)** - 缓存机制完整参考
- 📄 **[TanStack Query 进阶](./02-tanstack-query-advanced.md)** - 无限查询与乐观更新
- 📄 **[开发工具链](./04-devtools.md)** - Devtools 与 ESLint 插件配置
- 📄 **[入门项目：Todo App](../projects/01-todo-app.md)** - 用本文内容完成的完整项目


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
