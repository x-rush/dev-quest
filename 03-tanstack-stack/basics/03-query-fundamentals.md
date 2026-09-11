# Query 基础：useQuery 与 useMutation

> **文档简介**: 上手 TanStack Query v5 的三大入口——useQuery 声明式取数、useMutation 写操作、useQueryClient 缓存控制，并建立"服务端状态缓存"的心智模型
>
> **目标读者**: 已完成环境搭建，第一次接触服务端状态管理的 React 开发者
>
> **前置知识**: React Hooks 基础、fetch/Promise 基本用法、[QueryClientProvider 已接入](./01-environment-setup.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#useQuery` `#useMutation` `#缓存` `#服务端状态` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 区分"服务端状态"与"客户端状态"
- ✅ 用 `useQuery` 声明式获取并渲染远程数据
- ✅ 用 `useMutation` 提交写操作并触发列表刷新
- ✅ 解释 queryKey 如何决定缓存的存与取

---

## 🔍 服务端状态是一种特殊的状态

`useState` 管理的是**客户端状态**（主题、弹窗开关），特征是：应用是唯一事实来源。

接口返回的是**服务端状态**，特征是：事实来源在远端，本地持有的只是一份**随时会过期的快照**。手写 `useEffect + useState` 取数会陷入三大泥潭：缓存、去重、重新同步。TanStack Query 就是为此而生。

## 📥 useQuery：声明式取数

```tsx
import { useQuery } from '@tanstack/react-query'

type Todo = { userId: number; id: number; title: string; completed: boolean }

async function fetchTodos(): Promise<Todo[]> {
  const res = await fetch('https://jsonplaceholder.typicode.com/todos')
  if (!res.ok) throw new Error(`请求失败: ${res.status}`)
  return res.json()
}

function TodoList() {
  // queryKey 是缓存的"地址"，queryFn 是"取货方式"
  const { data, isPending, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  })

  if (isPending) return <p>加载中...</p>       // 首次加载且无缓存
  if (isError) return <p>出错了: {error.message}</p>

  return (
    <section>
      {/* isFetching 表示后台正在重新验证，可与内容并存 */}
      <button onClick={() => refetch()}>刷新{isFetching ? '...' : ''}</button>
      <ul>
        {data.map((todo) => (
          <li key={todo.id}>{todo.title}</li>
        ))}
      </ul>
    </section>
  )
}
```

**关键点解析**：

- `isPending`：还没有数据；v5 中此状态下 `data` 类型收窄为 `undefined`，先判空再渲染才能通过类型检查（`isLoading` 现在等于 `isPending && isFetching`，即首次加载）
- `data` 类型由 `fetchTodos` 的返回值**自动推断**，无需手写泛型
- 挂载即取数；组件卸载后缓存仍在，再次挂载**瞬间命中缓存**

## 🗄️ 缓存心智模型

每个 `queryKey` 对应一条缓存条目，核心三阶段：

```text
fresh（新鲜） --staleTime 到期--> stale（陈旧） --gcTime 无组件使用--> 垃圾回收
```

- **fresh**：组件挂载直接用缓存，不发请求
- **stale**：默认任何"触发时机"（重新挂载、窗口聚焦、断网重连）都会后台重新请求，旧数据先展示（stale-while-revalidate）
- **gcTime**：没有任何组件使用该查询后，缓存保留 5 分钟（默认）再被清除

> 参数细节（默认值、覆盖方式）见 [缓存键、staleTime 与失效策略](../reference/framework-essentials/01-query-essentials.md)。

## ✍️ useMutation：写操作

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'

function AddTodo() {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (title: string) =>
      fetch('https://jsonplaceholder.typicode.com/todos', {
        method: 'POST',
        body: JSON.stringify({ title }),
      }).then((res) => res.json()),
    onSuccess: () => {
      // 让 ['todos'] 前缀下的所有查询失效并重新获取
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })

  return (
    <button
      disabled={mutation.isPending}
      onClick={() => mutation.mutate('新任务')}
    >
      {mutation.isPending ? '提交中...' : '添加任务'}
    </button>
  )
}
```

**关键点解析**：

- mutation 不会自动执行，必须调用 `mutate(variables)`；variables 类型由 `mutationFn` 参数推断
- 写操作完成后**手动失效**受影响的读查询——Query 不会自动猜你要刷新什么
- `isError` / `error` 可用于渲染提交失败提示

## 🎛️ useQueryClient：缓存的遥控器

`useQueryClient()` 返回顶层的 `QueryClient` 实例，常用方法：

```tsx
const queryClient = useQueryClient()

queryClient.invalidateQueries({ queryKey: ['todos'] })        // 失效并重取
queryClient.getQueryData<Todo[]>(['todos'])                   // 只读缓存
queryClient.setQueryData<Todo[]>(['todos'], (old) => old ?? []) // 直接写入（updater 返回 undefined 会清空条目）
```

完整方法表见 [Query 核心 API](../reference/language-concepts/01-query-core-api.md)。

## ✅ 最佳实践

- ✅ **key 用数组层级**：`['todos', 'list', { page: 2 }]`，让失效可以按前缀批量命中
- ✅ **读与写分开**：列表用 `useQuery`，创建/更新/删除用 `useMutation`
- ✅ **把非请求逻辑放进 queryFn**：token 注入、错误归一化都在 fetcher 里处理
- ❌ **避免** 用 `useEffect` 手动同步 Query 的结果到 `useState`，直接渲染 `data` 即可
- ❌ **避免** 在 `queryFn` 里吞掉错误——抛出异常才能让 `isError` 生效

---

## 🎯 练习与实践

### 练习一：读操作

- [ ] 实现 `useQuery` 请求 `/todos?_limit=10`，渲染列表并处理加载/错误态
- [ ] 给查询加 `staleTime: 10_000`，10 秒内来回切换页面，观察 Devtools 中缓存状态从 `fresh` 到 `stale`

### 练习二：写操作

- [ ] 实现删除按钮：`useMutation` 调用 `DELETE /todos/:id`，成功后失效列表
- [ ] 在 Devtools 中确认失效后列表自动重新获取

---

## 🔗 相关文档

- 📄 **[Table 基础](./04-table-fundamentals.md)** - 下一篇：把 Query 取到的数据装进表格
- 📄 **[Query 核心 API](../reference/language-concepts/01-query-core-api.md)** - 参数与返回值完整字典
- 📄 **[缓存键、staleTime 与失效策略](../reference/framework-essentials/01-query-essentials.md)** - 缓存设计进阶
- 📄 **[高级特性](./07-advanced-features.md)** - 乐观更新、无限查询、依赖查询

---

**最后更新**: 2026年9月 | Dev Quest · 03-tanstack-stack
