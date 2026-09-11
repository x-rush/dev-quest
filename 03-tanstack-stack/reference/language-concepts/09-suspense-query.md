# Suspense 查询：useSuspenseQuery 与数据保证

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

`useSuspenseQuery` 是 Query 的 Suspense 模式入口：查询未就绪时向最近的 `<Suspense>` 边界抛出 Promise（渲染 fallback），数据到达后组件才渲染，因此返回的 `data` **保证非空**——类型层面直接给出 `TData` 而非 `TData | undefined`，无需 `isPending` 分支。它是 v5 中"非空 data"的推荐标准模式。

## 📖 语法 / 签名

```ts
const result = useSuspenseQuery({
  queryKey,            // 必填
  queryFn,             // 必填
  staleTime,           // 建议显式设置，避免每次挂载都挂起
  select,              // 派生层，语义同 useQuery
})
// 返回值差异：
// data: TData              —— 必非空（无 undefined 收窄；isPending 恒为 false，挂起由 <Suspense> 接管）
// error: Error | null      —— 出错时非空
// fetchStatus              —— 后台重取状态仍可用
```

| 返回值 | 类型 | 说明 |
|--------|------|------|
| `data` | `TData` | 数据到达后渲染，类型必非空 |
| `error` | `Error \| null` | 错误向 ErrorBoundary 抛出 |
| `fetchStatus` | `'fetching' \| 'idle' \| 'paused'` | 后台重新验证进度 |

## 💡 示例

```tsx
import { useSuspenseQuery } from '@tanstack/react-query'

function PostDetail({ id }: { id: string }) {
  // data 类型为 Post（非 undefined），可直接解构字段
  const { data: post, fetchStatus } = useSuspenseQuery({
    queryKey: ['posts', 'detail', id],
    queryFn: () => fetchPost(id),
    staleTime: 60_000,
  })

  return (
    <article>
      <h1>{post.title}</h1>
      {/* 后台重验证不触发 Suspense，仅作视觉提示 */}
      {fetchStatus === 'fetching' && <span>同步中…</span>}
    </article>
  )
}

// 父层兜住加载与错误
<Suspense fallback={<PostSkeleton />}>
  <ErrorBoundary fallback={<p>加载失败</p>}>
    <PostDetail id="1" />
  </ErrorBoundary>
</Suspense>
```

## ⚠️ 常见陷阱

- ❌ 在 `useSuspenseQuery` 外再写 `isPending` 分支：返回值中该字段恒为 `false`，分支无意义——挂起态由 `<Suspense>` 接管
- ❌ 忘记配 ErrorBoundary：`queryFn` 抛出的错误会向上抛出，没有边界直接白屏
- ❌ `staleTime` 保持默认 0：路由间来回切换会反复挂起、反复闪 fallback
- ❌ 把"非 Suspense 组件"包进边界后假设 data 永远存在：`useQuery` 返回值仍可能是 `undefined`，两种 hook 不可混用假设
- ✅ 与路由级 `ensureQueryData` 预取组合：数据先行就位，Suspense 边界几乎不闪

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - 普通 useQuery 的 isPending/undefined 收窄对照
- 📄 **[预取与 SSR 水合](../framework-essentials/04-prefetch-ssr.md)** - ensureQueryData 与流式预取
- 📄 **[Query 基础](../../basics/03-query-fundamentals.md)** - 两种模式的入门对照

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
