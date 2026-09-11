# Query 高级特性：乐观更新、无限查询与失效策略

> **文档简介**: 进入 TanStack Query v5 的进阶模式——乐观更新、无限滚动加载、依赖查询，以及生产环境最关键的查询失效策略设计
>
> **目标读者**: 已熟练使用 useQuery/useMutation，想让交互体验与数据一致性更上一层楼的开发者
>
> **前置知识**: [Query 基础](./03-query-fundamentals.md)、[缓存键与失效策略](../reference/framework-essentials/01-query-essentials.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#乐观更新` `#useInfiniteQuery` `#依赖查询` `#失效策略` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 `onMutate` 快照 + 回滚实现乐观更新
- ✅ 用 `useInfiniteQuery` 实现游标分页加载
- ✅ 用 `enabled` 实现依赖前序查询结果的链式取数
- ✅ 设计"精确失效、按需刷新"的失效策略

---

## 🚀 乐观更新：先改界面，后等服务器

**场景**：点赞、勾选待办等高频小操作。等待服务器响应再刷新会让 UI 卡顿；乐观更新先假设成功，失败再回滚。

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'

type Todo = { id: number; title: string; completed: boolean }

function useToggleTodo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (todo: Todo) => api.updateTodo(todo.id, { completed: !todo.completed }),

    // 1. mutation 发起前：取消相关查询 + 写入缓存快照
    onMutate: async (todo) => {
      await queryClient.cancelQueries({ queryKey: ['todos'] })

      const previousTodos = queryClient.getQueryData<Todo[]>(['todos'])

      // 直接改缓存，UI 立即响应
      queryClient.setQueryData<Todo[]>(['todos'], (old) =>
        old?.map((t) => (t.id === todo.id ? { ...t, completed: !t.completed } : t)),
      )

      // 返回值会成为 onError 的第三个参数 context
      return { previousTodos }
    },

    // 2. 失败：用快照回滚
    onError: (_error, _todo, context) => {
      if (context?.previousTodos) {
        queryClient.setQueryData(['todos'], context.previousTodos)
      }
    },

    // 3. 无论成败：失效重取，让本地缓存向服务器事实对齐
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}
```

**三段式口诀**：`onMutate` 快照并先行 → `onError` 回滚 → `onSettled` 对齐事实。

## ♾️ 无限查询：useInfiniteQuery

```tsx
import { useInfiniteQuery } from '@tanstack/react-query'

type Page = { items: string[]; nextCursor: number | null }

function Feed() {
  const { data, isPending, hasNextPage, isFetchingNextPage, fetchNextPage } =
    useInfiniteQuery({
      queryKey: ['feed'],
      queryFn: ({ pageParam }) => api.fetchFeed(pageParam as number),
      initialPageParam: 0, // v5 起必填：必须显式声明首页游标
      getNextPageParam: (lastPage) => lastPage.nextCursor, // 返回 null/undefined 即无更多
    })

  if (isPending) return <p>加载中...</p>

  return (
    <>
      {/* data.pages 是所有已加载页的数组，需要 flat 摊平 */}
      {data.pages.flatMap((page) => page.items).map((item, i) => (
        <p key={i}>{item}</p>
      ))}
      <button
        onClick={() => fetchNextPage()}
        disabled={!hasNextPage || isFetchingNextPage}
      >
        {isFetchingNextPage
          ? '加载中...'
          : hasNextPage
            ? '加载更多'
            : '没有更多了'}
      </button>
    </>
  )
}
```

**关键点解析**：

- v5 起 `initialPageParam` 为**必填**，游标语义一目了然
- 缓存按 `pageParams` 完整记忆已加载的页，失效时整链重取
- 每页渲染去重要自己处理（或配合 `select` 收敛）

## ⛓️ 依赖查询：enabled 开关

当前一个查询的结果是后一个查询的输入时，用 `enabled` 控制执行时机：

```tsx
const { data: user } = useQuery({
  queryKey: ['user', email],
  queryFn: () => api.fetchUser(email),
})

const { data: projects } = useQuery({
  queryKey: ['projects', user?.id],
  queryFn: () => api.fetchProjects(user!.id),
  // user.id 就绪前该查询保持 idle，不发请求
  enabled: !!user?.id,
})
```

`enabled: false` 的查询不会因挂载/聚焦而取数，只能靠 `refetch()` 或依赖变化重新激活。

## 🎯 查询失效策略

写操作之后刷新什么、怎么刷，是 Query 使用中最需要"设计"的部分。三个层次：

| 层次 | 写法 | 适用场景 |
|------|------|---------|
| 精确失效 | `invalidateQueries({ queryKey: ['todo', id], exact: true })` | 只改了一条详情 |
| 前缀失效 | `invalidateQueries({ queryKey: ['todos'] })` | 改动影响整个列表域 |
| 全局失效 | `invalidateQueries()` | 登录/登出、权限切换 |

```tsx
// refetchType 控制失效对象是否立即重取
queryClient.invalidateQueries({
  queryKey: ['todos'],
  refetchType: 'active', // 仅正在挂载的查询立即重取（默认）
  // 'none'：只标记失效，下次挂载才重取
  // 'all'：连后台未挂载的也重取
})
```

**设计原则**：

- ✅ 失效范围**宁大勿小**：缓存可以多刷新一次，但不能留着脏数据
- ✅ 乐观更新与失效配合：先 `setQueryData` 给即时反馈，再 `invalidateQueries` 对齐事实
- ❌ **避免** 在 `onSuccess` 里 `setQueryData` 手工"缝合"所有列表——那是把自己变成缓存同步器

更多模式见 [Query 核心 API](../reference/language-concepts/01-query-core-api.md) 与 [缓存键、staleTime 与失效策略](../reference/framework-essentials/01-query-essentials.md)。

---

## 🎯 练习与实践

### 练习一：乐观更新

- [ ] 给待办列表实现"勾选完成"乐观更新，用浏览器 DevTools 网络限速观察回滚
- [ ] 故意在 `onMutate` 里删掉 `cancelQueries`，观察并发请求覆盖缓存的问题

### 练习二：无限列表

- [ ] 用 `/comments?_page=N&_limit=5` 实现"加载更多"，`nextCursor` 取 `page < 10 ? page + 1 : null`
- [ ] 在 Devtools 中查看该查询缓存里的 `pageParams` 结构

---

## 🔗 相关文档

- 📄 **[第一个项目](./08-first-project.md)** - 下一篇：综合实战数据面板
- 📄 **[Query 核心 API](../reference/language-concepts/01-query-core-api.md)** - 本篇用到的 API 完整签名
- 📄 **[缓存键、staleTime 与失效策略](../reference/framework-essentials/01-query-essentials.md)** - 失效与重试的完整规则

---

**最后更新**: 2026年9月 | Dev Quest · 03-tanstack-stack
