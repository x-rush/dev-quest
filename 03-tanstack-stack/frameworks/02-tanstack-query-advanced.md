# TanStack Query 进阶：无限查询、乐观更新与失效策略

## 先看框架承担哪部分职责

**Query 进阶**：无限查询管理一组页，乐观更新管理暂时预测，失效管理与事实重新同步。它们需要各自清楚的身份和错误恢复。

**最小练习与预期结果**：先实现两页，再让第二页失败；已有第一页保持可读，重试不会重复插入同一页。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 掌握 Query v5 的三大进阶能力——useInfiniteQuery 分页加载、onMutate 乐观更新与系统化的 query invalidation 策略。
>
> **目标读者**: 已熟练使用 useQuery/useMutation，正在构建列表型、协作型应用的进阶开发者
>
> **前置知识**: [Query 基础](./01-tanstack-query-basics.md)、[Query 高级特性教程](../basics/07-advanced-features.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#tanstack-query` `#useinfinitequery` `#乐观更新` `#invalidation` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 完成后你将能够

- 用 useInfiniteQuery 实现"加载更多"与游标分页
- 用 onMutate 四步模式实现可回滚的乐观更新
- 按作用域与活跃度设计失效策略，避免全量刷新

> 参数字典见 [Query 核心 API](../reference/language-concepts/01-query-core-api.md)；缓存生命周期原理见 [Query 缓存架构与数据流](../advanced-topics/architecture/01-cache-architecture.md)。

---

## 1. useInfiniteQuery：无限滚动与游标分页

```tsx
import { useInfiniteQuery } from '@tanstack/react-query'

interface Page {
  items: { id: number; title: string }[]
  nextCursor: number | null // 后端返回下一页游标；null 表示没有更多
}

async function fetchFeed({ pageParam }: { pageParam: number }): Promise<Page> {
  const res = await fetch(`/api/feed?cursor=${pageParam}&limit=20`)
  if (!res.ok) throw new Error('加载信息流失败')
  return res.json()
}

export function useFeed() {
  return useInfiniteQuery({
    queryKey: ['feed'],
    queryFn: fetchFeed,
    initialPageParam: 0, // v5 起必填：显式提供初始页参
    getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
    maxPages: 10, // v5 起支持：最多保留 10 页，防止无限滚动撑爆内存
  })
}
```

组件中拼接所有页并触发加载：

```tsx
function Feed() {
  const { data, isPending, isError, fetchNextPage, hasNextPage, isFetchingNextPage } = useFeed()

  if (isPending) return <p>加载中…</p>
  if (isError) return <p role="alert">加载失败</p>

  // data.pages 是按请求顺序排列的每页结果
  const items = data.pages.flatMap((page) => page.items)

  return (
    <div>
      {items.map((item) => (
        <article key={item.id}>{item.title}</article>
      ))}
      <button
        onClick={() => fetchNextPage()}
        disabled={!hasNextPage || isFetchingNextPage}
      >
        {isFetchingNextPage ? '加载中…' : hasNextPage ? '加载更多' : '没有更多了'}
      </button>
    </div>
  )
}
```

**要点**：`getNextPageParam` 返回 `undefined` 即告知没有下一页；偏移量分页把 `nextCursor` 换成基于 `lastPage.items.length` 的计算即可。

---

## 2. 乐观更新：onMutate 四步模式

适用场景：拖拽排序、点赞、勾选等"用户预期立即生效"的操作。标准四步：**取消在途 → 快照缓存 → 立即写入 → 出错回滚**。

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { Todo } from '../basics/03-query-fundamentals'

export function useToggleTodo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (todo: Todo) =>
      fetch(`/api/todos/${todo.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ done: !todo.done }),
      }).then((res) => {
        if (!res.ok) throw new Error('切换失败')
        return res.json() as Promise<Todo>
      }),

    onMutate: async (todo) => {
      // ① 取消该键的所有在途请求，防止旧响应覆盖乐观数据
      await queryClient.cancelQueries({ queryKey: ['todos'] })

      // ② 快照当前缓存，用于回滚
      const previous = queryClient.getQueryData<Todo[]>(['todos'])

      // ③ 立即把乐观结果写入缓存（UI 即时变化）
      queryClient.setQueryData<Todo[]>(['todos'], (old = []) =>
        old.map((t) => (t.id === todo.id ? { ...t, done: !t.done } : t)),
      )

      // 返回的 context 会传给 onError 与 onSettled
      return { previous }
    },

    onError: (_err, _todo, context) => {
      // ④ 出错时用快照回滚
      if (context?.previous) {
        queryClient.setQueryData(['todos'], context.previous)
      }
    },

    onSettled: () => {
      // 无论成败，最终与服务端对齐一次
      void queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}
```

**何时不要乐观更新**：结果依赖服务端计算（价格、库存校验）、失败成本高（支付）、或 UI 无法表达"待确认"状态的写操作。这些场景使用 invalidate + loading 态即可。

---

## 3. Invalidation 策略

`invalidateQueries` 有两个可调维度：**作用域**（哪些键）与 **活跃度**（是否立即重取）。

### 3.1 按作用域收窄

```ts
await queryClient.invalidateQueries({ queryKey: ['todos'] })              // 前缀匹配：todos 全家
await queryClient.invalidateQueries({ queryKey: ['todos', 'detail', 7] }) // 只失效 id=7 的详情
await queryClient.invalidateQueries({
  predicate: (q) => q.queryKey[0] === 'todos' && (q.state.dataUpdatedAt ?? 0) < Date.now() - 3_600_000,
}) // 自定义谓词：只失效超过 1 小时未更新的 todos 查询
```

### 3.2 按活跃度控制重取行为

```ts
// 默认：失效 + 立即重新请求活跃查询（inactive 只标记为 stale）
await queryClient.invalidateQueries({ queryKey: ['todos'] })

// 失效但不发起请求：等下次挂载/聚焦时再取
await queryClient.invalidateQueries({
  queryKey: ['todos'],
  refetchType: 'none',
})

// 连不活跃的缓存也强制重取
await queryClient.invalidateQueries({ queryKey: ['todos'], refetchType: 'all' })
```

### 3.3 失效 vs 直写的选择

| 场景 | 首选 |
|------|------|
| 列表增删改（服务端是权威） | invalidate |
| 服务端返回了完整新实体 | `setQueryData` 直写（省一次请求） |
| 用户即时操作（勾选/排序） | 乐观更新 + onSettled 对齐 |
| 登出/切换租户 | `queryClient.clear()` |

---

## 🎨 最佳实践速查

乐观更新先显示预测结果，因此要处理尚未返回的旧请求、写入失败和同时发生的第二次写入。取消相关查询能减少旧响应覆盖，但简单恢复整个旧快照仍可能抹掉后续成功修改；并发写入时应限定回滚范围或最终与服务端重新对齐。

无限列表是否限制页数取决于内存预算与回看需求，移除旧页可能需要再次请求。gcTime 主要控制无活跃观察者的缓存回收，不是活跃页面的页数限制。练习同时发起两次修改并让第一条失败，检查第二条结果没有被回滚掉。

---

## 🔗 相关文档

- 📄 **[Query 高级特性教程](../basics/07-advanced-features.md)** - 同主题的教程式讲解
- 📄 **[Query 核心 API](../reference/language-concepts/01-query-core-api.md)** - useInfiniteQuery / invalidateQueries 参数字典
- 📄 **[Query 缓存架构与数据流](../advanced-topics/architecture/01-cache-architecture.md)** - 为什么乐观更新要 cancelQueries
- 📄 **[协作看板项目](../projects/03-collaborative-kanban.md)** - 乐观更新 + 实时同步的完整实战
- 📄 **[查询性能优化](../advanced-topics/performance/01-query-optimization.md)** - invalidation 频率与网络成本权衡


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
