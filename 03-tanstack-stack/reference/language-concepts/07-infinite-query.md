# 无限查询：useInfiniteQuery 与游标分页

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

`useInfiniteQuery` 用于"一次键、多页数据"的场景：把已加载的所有页缓存进同一条查询条目（`data.pages` + `data.pageParams`），并通过 `fetchNextPage` 追加加载。解决"加载更多"/无限滚动中分页状态与缓存的管理问题。

## 📖 语法 / 签名

```ts
useInfiniteQuery({
  queryKey,
  queryFn: ({ pageParam, signal }) => fetchPage(pageParam),
  initialPageParam: 0,            // 必填（v5 起）
  getNextPageParam: (lastPage, allPages, lastPageParam) => nextCursor | undefined | null,
  getPreviousPageParam?: (firstPage, allPages, firstPageParam) => prevCursor,
  maxPages?: 10,                  // 限制保留页数，防内存膨胀（v5 起）
})
```

| 返回值 | 类型 | 说明 |
|--------|------|------|
| `data.pages` | `TPage[]` | 按请求顺序排列的每页数据 |
| `data.pageParams` | `unknown[]` | 每页使用的游标 |
| `hasNextPage` | `boolean` | `getNextPageParam` 返回非空即 true |
| `fetchNextPage` | `() => Promise` | 追加下一页 |
| `isFetchingNextPage` | `boolean` | 仅下一页请求进行中 |
| `isPending` | `boolean` | 首页尚未到达（v5 中此时 `data` 为 `undefined`） |

## 💡 示例

```tsx
function Feed() {
  const { data, isPending, isError, error, isFetching, hasNextPage, isFetchingNextPage, fetchNextPage } =
    useInfiniteQuery({
      queryKey: ['feed'],
      queryFn: ({ pageParam }) => api.fetchFeed(pageParam as number),
      initialPageParam: 0,
      getNextPageParam: (lastPage) => lastPage.nextCursor, // 返回 null/undefined 即无更多
    })

  if (isPending) return <p>加载中...</p>
  if (isError && !data) return <p>{error.message}</p>
  if (!data) return null

  return (
    <>
      {/* 多页数组需要 flatMap 摊平渲染 */}
      {data.pages.flatMap((page) => page.items).map((item, i) => (
        <p key={i}>{item}</p>
      ))}
      <button onClick={() => fetchNextPage()} disabled={!hasNextPage || isFetching}>
        {isFetchingNextPage ? '加载中...' : hasNextPage ? '加载更多' : '没有更多了'}
      </button>
    </>
  )
}
```

## ⚠️ 常见陷阱

- ❌ 漏掉 `initialPageParam`：类型报错——自 v5 起它是必填项
- ❌ 以为缓存只存最后一页：全部已加载页都在同一条目里，失效时整链重取（大列表注意 `maxPages`）
- ❌ 直接 `data.map(...)`：`data` 是 `{ pages, pageParams }` 结构，可用原生 `flatMap` 摊平一层；`flatMapDeep` 不是数组内置方法
- ❌ 页内不去重：游标重发或并发追加会产生重复项，用 `select` 阶段或渲染层按 id 收敛
- ✅ 双向滚动（聊天记录向上翻页）需同时声明 `getPreviousPageParam` 并用 `fetchPreviousPage`

<!-- full-library-explanation -->
## 把游标看作下一次请求的输入

先修：普通 useQuery、数组与 Promise。假设第一页返回 `{items: ['A', 'B'], nextCursor: 2}`，第二页返回 `{items: ['C'], nextCursor: null}`。缓存应包含两份 pages 和对应的 `[0, 2]` pageParams；null 表示停止，不能当作一个还要发送的游标。

上面的 API 签名是说明记法，带 `?:` 的对象字段不能原样作为 JavaScript 执行。Feed 还需要 QueryClientProvider 与实际 api.fetchFeed 实现。真实接口应把 signal 传给 fetch，检查 response.ok，并验证返回的 items 与游标结构。

分页筛选条件也必须进入 queryKey，例如 `['feed', {category}]`；pageParam 则描述同一列表里的页。不要让普通 useQuery 与 useInfiniteQuery 共用同一个键，两者缓存形状不同。

**练习：** 用两页固定响应实现 api.fetchFeed，连续加载到末页，确认按钮禁用且 pages.length 为 2；再让第二页失败，保留已加载内容并允许重试。验收时区分首次失败、追加失败和后台刷新失败，不能把全部情况变成空列表。

**边界：** maxPages 限制保留页数，会影响被移除方向的历史内容；不是只限制单次请求大小。无限列表重取时需要维护游标链，不能假定各页天然相互独立。[官方无限查询指南](https://tanstack.com/query/latest/docs/framework/react/guides/infinite-queries)

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - useQuery 家族共享的参数与返回值
- 📄 **[占位数据](./08-placeholder-data.md)** - 追加页时的过渡体验
- 📄 **[Query 高级特性教程](../../basics/07-advanced-features.md)** - 同主题教程式讲解
- 📄 **[Query 进阶](../../frameworks/02-tanstack-query-advanced.md)** - 偏移量分页与 maxPages 实战
- 📄 **[数据看板项目](../../projects/02-data-dashboard.md)** - 大数据量列表的完整落地

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
