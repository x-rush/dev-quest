# 预取与 SSR 水合：prefetch、dehydrate 与流式预取

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

预取与 SSR 水合解决"首屏白屏与请求瀑布"：服务端（或路由 loader）用 `prefetchQuery`/`ensureQueryData` 提前取数，`dehydrate` 把缓存序列化后随 HTML 下发，客户端 `hydrate` 还原进新的 `QueryClient`——组件首帧 `useQuery` 直接命中缓存，不再发起重复请求。TanStack Start 场景下还支持流式水合：关键数据先到先渲染，慢数据随流补齐。

## 📖 语法 / 签名

```ts
// 服务端 / loader 侧
await queryClient.prefetchQuery({ queryKey, queryFn })   // 静默预取（出错不抛）
await queryClient.ensureQueryData({ queryKey, queryFn }) // 新鲜直接返回，否则取回（可 await 阻塞）
const dehydratedState = dehydrate(queryClient)           // 序列化缓存

// 客户端侧
const queryClient = new QueryClient()
hydrate(queryClient, dehydratedState)                    // 还原进客户端缓存
```

| API | 签名 | 说明 |
|-----|------|------|
| `prefetchQuery` | `(options) => Promise<void>` | 不抛错、不返回数据，适合"能取就取" |
| `ensureQueryData` | `(options) => Promise<TData>` | 返回数据、抛出错误，适合"必须就位"的关键数据 |
| `dehydrate` | `(client) => DehydratedState` | 默认不包含已过 `gcTime` 的条目 |
| `hydrate` | `(client, state) => void` | 客户端须用**新建的** client 接收 |

## 💡 示例

```tsx
// TanStack Start / Next.js App Router 的请求级预取
export async function loader({ context }: LoaderArgs) {
  // 关键数据：阻塞渲染
  await context.queryClient.ensureQueryData({
    queryKey: ['post', id],
    queryFn: () => fetchPost(id),
  })
  // 次要数据：不阻塞，随流补齐
  void context.queryClient.prefetchQuery({
    queryKey: ['comments', id],
    queryFn: () => fetchComments(id),
  })
  return { dehydratedState: dehydrate(context.queryClient) }
}

// 客户端入口
const [queryClient] = useState(() => {
  const client = new QueryClient({ defaultOptions: { queries: { staleTime: 60_000 } } })
  return client
})
hydrate(queryClient, serverState)
```

## ⚠️ 常见陷阱

- ❌ SSR 中使用模块级单例 QueryClient：A 请求的缓存渲染进 B 的 HTML，数据串页且水合报错——每请求新建
- ❌ 服务端 prefetch 的 key 与客户端 `useQuery` 的 key 不一致：白取一次，水合后立刻重新请求并跳变——两端共用键工厂
- ❌ 以为 `hydrate` 后数据永远新鲜：记得同步设 `staleTime`，否则水合完成即触发重取
- ❌ `dehydrate` 大缓存全量下发：HTML 体积膨胀，只预取首屏真正需要的键
- ✅ 预取分层：关键数据 `ensureQueryData` 阻塞、次要数据 `prefetchQuery` 非阻塞、慢数据交给流式水合

## 🔗 相关条目

- 📄 **[Query 核心 API](../language-concepts/01-query-core-api.md)** - prefetchQuery/ensureQueryData 所在方法全表
- 📄 **[Suspense 查询](../language-concepts/09-suspense-query.md)** - 与流式预取组合的标准渲染模式
- 📄 **[Router 框架要点](./02-router-essentials.md)** - loader/beforeLoad 中的预取时机
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)** - 水合不匹配的排查路径

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
