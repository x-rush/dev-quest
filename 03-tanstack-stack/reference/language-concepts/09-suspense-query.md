# Suspense 查询：useSuspenseQuery 与数据保证

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

`useSuspenseQuery` 是 Query 的 Suspense 模式入口：查询未就绪时向最近的 `<Suspense>` 边界抛出 Promise（渲染 fallback），数据到达后组件才渲染，因此返回的 `data` **保证不是 undefined**——类型层面直接给出 `TData` 而非 `TData | undefined`，无需 `isPending` 分支。它是 v5 中"非空 data"的推荐标准模式。

## 📖 语法 / 签名

```ts
const result = useSuspenseQuery({
  queryKey,            // 必填
  queryFn,             // 必填
  staleTime,           // 建议显式设置，控制已有缓存的后台重取频率
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
| `error` | `Error \| null` | 无可展示数据时的错误通常抛给错误边界；后台错误可保留旧数据 |
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
- ❌ 把 `staleTime: 0` 等同于反复挂起：已有缓存时通常先展示缓存并后台刷新；新键无缓存时才需要等待
- ❌ 把"非 Suspense 组件"包进边界后假设 data 永远存在：`useQuery` 返回值仍可能是 `undefined`，两种 hook 不可混用假设
- ✅ 与路由级 `ensureQueryData` 预取组合：数据先行就位，Suspense 边界几乎不闪

<!-- full-library-explanation -->
## 边界接管的是首次等待，不是所有刷新

先修：React Suspense、错误边界、查询键。已有缓存数据时，即使数据过期，也可以先渲染数据再后台重取；staleTime 为 0 不等于每次都闪 fallback。切换到完全未缓存的新键，才需要重新考虑挂起与过渡体验。

这里的“保证”是成功返回渲染路径里 data 不为 undefined，并不禁止你的业务类型是 null、空数组或空字符串。接口返回 null 时，仍须按业务含义显示“没有记录”。

useSuspenseQuery 不提供 enabled 和 placeholderData 这套普通查询控制方式。条件未满足时可让父组件先不挂载查询子组件；同一组件中依次执行多个 Suspense 查询可能形成串行等待，需要并行时研究 useSuspenseQueries 或提前预取。

错误边界的重试还需要配合 QueryErrorResetBoundary 或 useQueryErrorResetBoundary 重置查询错误。只把一个“重试”按钮放入 fallback，并不能保证下一次渲染会重新尝试。已有数据时的后台错误默认可能保留数据而不抛给边界，应检查 error 并给出提示。

**练习：** 分别测试首次慢响应、已有缓存后的慢刷新、首次失败、后台失败四种情况。验收：说明哪一种显示 Suspense，哪一种保留旧数据，重试后能恢复。参考[官方 Suspense 指南](https://tanstack.com/query/latest/docs/framework/react/guides/suspense)。

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - 普通 useQuery 的 isPending/undefined 收窄对照
- 📄 **[预取与 SSR 水合](../framework-essentials/04-prefetch-ssr.md)** - ensureQueryData 与流式预取
- 📄 **[Query 基础](../../basics/03-query-fundamentals.md)** - 两种模式的入门对照

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
