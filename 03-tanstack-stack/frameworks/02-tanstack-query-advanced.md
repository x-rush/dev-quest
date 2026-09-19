# TanStack Query 进阶：无限查询、乐观更新与失效策略

## 从两页数据走到一次可回滚修改

前置是能启动的 React + TypeScript 工程、稳定的 `QueryClientProvider`，以及一次成功的 `useQuery`。先用 `npm ls @tanstack/react-query` 记录实际版本；本文按 Query v5 对象参数写法说明。这里的 `/api/feed`、`/api/todos` 是需要你提供的接口契约，本文不包含服务器，不能把片段直接当作完整工程。

本次产物是一个保留已加载内容的信息流和一个能恢复失败修改的待办列表。不要同时接入 WebSocket、筛选和无限滚动观察器：先用按钮触发，才能把一次用户动作对应到一次请求。

1. **准备确定的两页输入。** 让 `cursor=0` 返回 `{ items: [{ id: 1, title: '第一页' }], nextCursor: 1 }`，`cursor=1` 返回 `{ items: [{ id: 2, title: '第二页' }], nextCursor: null }`。先从浏览器 Network 确认响应形状，再接下面的 Hook；HTML 错误页不能交给 `res.json()` 当数据。
2. **只读取，观察页结构。** 首屏应只有 id 1；点一次加载更多后应有 id 1、2，`data.pages` 和 `data.pageParams` 各有两项。若重复 id，先回查请求游标和后端排序，不要先用前端去重掩盖接口问题。
3. **让第二页返回一次 500。** 本练习临时关闭自动重试，使一次点击的结果易观察。第一页应继续显示，页面底部提示失败；恢复接口后再点加载更多，第二页只追加一次。首次加载失败则显示整页错误，两种情况必须分开。
4. **再接待办修改。** GET 返回 `Todo[]`，PATCH 输入 `{ done: boolean }`、输出更新后的完整 `Todo`。先一次只允许一笔修改：按钮在 mutation 的 `isPending` 期间禁用。让 PATCH 失败，记录“原值 → 预测值 → 原值 → 重取结果”；下面的整表快照回滚只适合这个串行练习。

完成后保留请求参数、界面状态和失败恢复步骤三项记录，再进入并发修改。2026-09-20 已按官方文档核对 API；本篇未启动 React 工程或真实 API，以上均为待执行验收，不能据此标记运行通过。

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
    retry: false, // 本次故障练习关闭自动重试；产品中按错误类型另定策略
  })
}
```

组件中拼接所有页并触发加载：

```tsx
function Feed() {
  const { data, isPending, isError, fetchNextPage, hasNextPage, isFetching, isFetchingNextPage } = useFeed()

  if (isPending) return <p>加载中…</p>
  if (!data) return <p role="alert">首次加载失败，请恢复接口后刷新</p>

  // data.pages 是按请求顺序排列的每页结果
  const items = data.pages.flatMap((page) => page.items)

  return (
    <div>
      {items.map((item) => (
        <article key={item.id}>{item.title}</article>
      ))}
      {isError && <p role="alert">更新失败，已加载内容保留；可再次加载更多</p>}
      <button
        onClick={() => fetchNextPage()}
        disabled={!hasNextPage || isFetching}
      >
        {isFetchingNextPage ? '加载中…' : hasNextPage ? '加载更多' : '没有更多了'}
      </button>
    </div>
  )
}
```

**回查数据契约**：`getNextPageParam` 返回 `null` 或 `undefined` 表示结束；合法游标 `0` 不能用 `||` 吃掉。偏移量接口需要“上次偏移量 + 本页数量”和结束条件，单凭本页长度不能推导累计偏移量。这里用 `isFetching` 禁用按钮，避免后台刷新时又抢着加载下一页。先完成两页练习，再考虑 `maxPages`；限制页数会移除旧页，若产品允许回看，还要设计前一页游标和滚动体验。[官方无限查询指南](https://tanstack.com/query/latest/docs/framework/react/guides/infinite-queries)

---

## 2. 乐观更新：onMutate 四步模式

适用场景：拖拽排序、点赞、勾选等"用户预期立即生效"的操作。标准四步：**取消在途 → 快照缓存 → 立即写入 → 出错回滚**。

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'

// 实际项目放到 src/types/todo.ts；不要从教程 Markdown 路径导入类型。
type Todo = { id: number; title: string; done: boolean }

export function useToggleTodo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (todo: Todo) =>
      fetch(`/api/todos/${todo.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
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

      // 返回值是 onMutateResult，由后续回调接收
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
      return queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}
```

**何时不要乐观更新**：结果依赖服务端计算（价格、库存校验）、失败成本高（支付）、或 UI 无法表达"待确认"状态的写操作。这些场景使用 invalidate + loading 态即可。

`onSettled` 返回失效 Promise，让这次 mutation 等待重取阶段结束；消费 Hook 的按钮应使用同一个 mutation 实例的 `isPending`。这只约束当前界面，不会阻止别的标签页写入。若要允许并发，不应继续用整表快照覆盖缓存，应按实体处理冲突并以服务端结果对齐。回查 [官方乐观更新指南](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates)。

---

## 3. Invalidation 策略

`invalidateQueries` 有两个可调维度：**作用域**（哪些键）与 **活跃度**（是否立即重取）。

### 3.1 按作用域收窄

```ts
await queryClient.invalidateQueries({ queryKey: ['todos'] })              // 前缀匹配：todos 全家
await queryClient.invalidateQueries({ queryKey: ['todos', 'detail', 7], exact: true }) // 只匹配这个完整键
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

下一步先做失效范围实验：同时缓存 `['todos']`、`['todos', 'detail', 7]`、`['profile']`，修改待办后记录前两项是否重取、第三项是否保持。默认前缀匹配不会只命中列表；如果详情也共享这个前缀，它也会失效。把不活跃查询单独标出，避免把“没有立即发请求”误判为失效未发生。完成这份记录后，再进入协作看板的并发与实时同步。

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
