# Query 基础：从一次读取到写入后的同步

> 前置：React 组件与 Hooks、Promise；已完成[环境搭建](./01-environment-setup.md)。适用 TanStack Query v5。目标是亲手验证读取、错误、写入、失效四个行为。

## 先理解，再动手

Query 保存远端结果快照；queryKey 标识“哪一个问题的答案”，queryFn 负责获取。写操作成功后，需要明确哪些答案已经过期。

**本节自测**：分别查询用户 1 与用户 2 的待办；把用户 ID 加入请求和键。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

两份列表不串缓存；只改 URL 不改键仍可能复用错误结果。错误分支必须能在无 data 时显示。

</details>

## 先分清两种状态

输入框正在编辑的标题由当前组件决定，放在 useState。服务器保存的待办可能被其他客户端修改，本地只能缓存一份快照，由 Query 管理。Query 不替你存数据库，也不会自动知道写入影响哪条列表。

本课使用内存模拟 API：保留 Promise 边界和真实写入效果，去掉网络安装变量。它不是实际 HTTP 服务，刷新页面会重置数据。这样可以先证明缓存流程，再接自己的后端。公共 JSONPlaceholder 会模拟写入响应而不持久保存，不能用它证明“删除后重新查询记录消失”。参见[其使用说明](https://jsonplaceholder.typicode.com/guide/)。

## 一个文件跑通

在上一课的 React 工程中替换 `src/App.tsx`，依赖为 `react` 与 `@tanstack/react-query`。本例自己提供 QueryClientProvider；入口只渲染 App 即可。按工程 package.json 中的开发脚本启动。以下是完整组件文件，没有隐藏的 api、TodoList 或数据库定义。

```tsx
import { useState } from 'react'
import {
  QueryClient,
  QueryClientProvider,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

type Todo = { id: number; title: string }
let rows: Todo[] = [{ id: 1, title: '理解缓存的身份' }]
let nextId = 2
let failNextRead = false
const delay = () => new Promise<void>((resolve) => setTimeout(resolve, 300))

async function readTodos(): Promise<Todo[]> {
  await delay()
  if (failNextRead) {
    failNextRead = false
    throw new Error('模拟读取失败，请重试')
  }
  return rows.map((row) => ({ ...row }))
}

async function createTodo(title: string): Promise<Todo> {
  await delay()
  const normalized = title.trim()
  if (!normalized) throw new Error('标题不能为空')
  const todo = { id: nextId++, title: normalized }
  rows = [...rows, todo]
  return { ...todo }
}

// 模块级实例在这份纯客户端练习中保持稳定；SSR 需要按请求隔离。
const client = new QueryClient()

function TodoPage() {
  const [title, setTitle] = useState('')
  const queryClient = useQueryClient()
  const query = useQuery({
    queryKey: ['todos'],
    queryFn: readTodos,
    staleTime: 10_000,
    retry: false, // 练习时立即观察错误；生产环境另定重试策略
  })
  const mutation = useMutation({
    mutationFn: createTodo,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['todos'] })
      setTitle('')
    },
  })

  if (query.isPending) return <p>首次加载中...</p>
  // 无数据的失败也必须进入错误分支，不能被 data === undefined 吞掉。
  if (query.isError && query.data === undefined) {
    return <div role="alert">
      <p>{query.error.message}</p>
      <button onClick={() => void query.refetch()}>重试</button>
    </div>
  }

  return <main>
    <h1>待办</h1>
    {query.isFetching && <p>正在同步...</p>}
    {query.isError && <p role="alert">{query.error.message}；保留上次结果</p>}
    {query.data?.length === 0 && <p>还没有待办</p>}
    <ul>{query.data?.map((todo) => <li key={todo.id}>{todo.title}</li>)}</ul>
    <form onSubmit={(event) => {
      event.preventDefault()
      mutation.mutate(title)
    }}>
      <label>标题 <input value={title} onChange={(e) => setTitle(e.target.value)} /></label>
      <button disabled={mutation.isPending}>
        {mutation.isPending ? '提交并同步中...' : '添加'}
      </button>
    </form>
    {mutation.isError && <p role="alert">{mutation.error.message}</p>}
    <button disabled={query.isFetching} onClick={() => {
      failNextRead = true
      void query.refetch()
    }}>模拟下一次读取失败</button>
    <button disabled={query.isFetching} onClick={() => void query.refetch()}>重新读取</button>
  </main>
}

export default function App() {
  return <QueryClientProvider client={client}><TodoPage /></QueryClientProvider>
}
```

## 沿着一次操作理解代码

1. 组件订阅 `['todos']`，没有数据时进入 pending，queryFn 返回 Promise。
2. 读取成功后，结果进入这条键对应的缓存，界面显示初始记录。
3. 输入由 useState 保存；点击添加才调用 mutation，读取不会替你触发写入。
4. 写入成功改变模拟服务的 rows，但读取缓存不会凭空知道它已改变。
5. onSuccess 使列表失效；活跃查询重新获取数据。返回并等待这个 Promise，让 mutation 的等待阶段覆盖同步过程。

注意：写成功与随后刷新成功是两个结果。如果真实后端已经创建成功而重取失败，应允许重试读取；直接再次提交可能创建重复记录。

## 缓存的两个维度

| 问题 | 对应概念 | 本例中的含义 |
|---|---|---|
| 这份答案属于谁？ | queryKey | `['todos']`；按用户过滤时必须把用户 ID 也放进键 |
| 是否需要重新确认？ | staleTime / invalidate | 十秒内视为新鲜；显式失效可以提前要求重新确认 |
| 是否还有人使用？ | 活跃与非活跃查询 | 当前页面使用列表，所以失效后通常会重新读取 |
| 没人使用后留多久？ | gcTime | 管非活跃缓存回收，与“新鲜多久”不是同一计时器 |

不是 staleTime 一到就立即发请求；通常还需要挂载、重新聚焦等触发条件。也不是先 stale 才能回收：回收关注是否无人使用。详见[缓存参考](../reference/framework-essentials/01-query-essentials.md)。

## 类型与错误为什么这样判断

现代 TypeScript 可以保留 const 解构后的判别联合关系。`const { data, isSuccess } = useQuery(...)` 后，在 isSuccess 分支中 data 可以收窄；“解构就一定丢失收窄”是不正确的。只排除 pending 仍可能剩下 error，才是 data 可能为空的原因。[TanStack 类型说明](https://tanstack.com/query/latest/docs/framework/react/typescript)和[TypeScript 4.6 说明](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-6.html)给出了这一机制。

本例保留查询对象以便阅读。首次失败且无数据显示错误；后台失败且有历史数据则显示错误并保留结果。错误不能被统一的“没数据就加载”分支遮住。

## 换成 HTTP 时补上什么

以下是替换 readTodos 的局部片段。前提是你的后端确实实现了同源 `/api/todos`，返回符合 Todo 数组的 JSON；实际外部输入还应做运行时结构校验。

```tsx
async function readTodos(): Promise<Todo[]> {
  const response = await fetch('/api/todos')
  if (!response.ok) throw new Error(`读取失败：HTTP ${response.status}`)
  return response.json()
}
```

创建请求还要指定方法、Content-Type、请求体，检查响应状态。fetch 收到 400/500 通常仍成功得到 Response，不检查 ok 就可能把错误响应当成业务成功。

## 练习与验收

| 操作 | 预期结果 | 它验证什么 |
|---|---|---|
| 首次打开 | 加载后显示一条记录 | 读取与成功分支 |
| 输入空格并提交 | 标题不能为空，列表不增加 | mutation 错误与业务校验 |
| 添加“写一个测试” | 等待后列表增加，输入清空 | 写入、失效和重取 |
| 点击模拟读取失败 | 显示错误且保留旧列表 | 后台错误不覆盖历史结果 |
| 点击重新读取 | 恢复正常 | 可恢复错误 |
| 刷新浏览器 | 恢复初始数据 | 内存模拟服务的生命周期 |

扩展：实现删除 mutation。提示是先按 ID 修改模拟 rows，再失效同一键；验收为重取后该记录消失。完成后阅读[Table 基础](./04-table-fundamentals.md)或查[Query API](../reference/language-concepts/01-query-core-api.md)。

## 模式不变量

- 远端事实、查询快照和输入草稿的拥有者不同。
- 缓存身份必须涵盖影响结果的输入。
- 写入成功后需要确定受影响的读取范围。
- 首次失败与有历史数据的后台失败需要分别设计界面。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
