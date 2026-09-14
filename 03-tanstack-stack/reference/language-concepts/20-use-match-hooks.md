# useMatch / useMatches / router.invalidate：匹配读取与刷新重校验

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

`useMatch` 订阅一条路由匹配（必须传 options——要么 `from` 指定路由，要么 `strict: false` 取最近匹配）；`useMatches` 订阅当前 URL 的整条匹配链（面包屑、进度条场景）；`router.invalidate()`（经 `useRouter` 取实例）重跑当前 URL 全部匹配路由的 loader/beforeLoad——这是 Router 的"刷新数据"，与 Query 的 `invalidateQueries` 是两套机制。

## 📖 语法 / 签名

```ts
useMatch({ from: '/posts/$postId' })              // from 指定路由；不匹配则抛错
useMatch({ from: '/posts/$postId', select: (m) => m.status })  // 只订阅 select 结果
useMatch({ strict: false })                       // 最近匹配，找不到也不抛错

useMatches()                                      // RouteMatch[]，匹配链
useMatches({ select: (ms) => ms.map((m) => m.routeId) })

const router = useRouter()
router.invalidate()                               // 重跑全部匹配路由 loader/beforeLoad
router.invalidate({ filter: (m) => m.routeId === '/posts/$postId' })  // 只失效部分匹配
```

| RouteMatch 字段 | 说明 |
|-----------------|------|
| `routeId` / `id` | 路由标识（filter 常用 routeId） |
| `status` | `'pending' \| 'success' \| 'error' \| 'notFound'` |
| `isFetching` | `false \| 'beforeLoad' \| 'loader'` |
| `loaderData` | loader 返回值（from 指定时按路由类型收窄） |
| `invalid` | 该匹配是否处于"待失效重跑"状态 |

## 💡 示例

```tsx
import { useMatch, useMatches, useRouter } from '@tanstack/react-router'

// useMatch：读取指定路由的匹配（loaderData 按路由类型收窄）
function PostHeader() {
  const match = useMatch({ from: '/posts/$postId' })
  const matchStatus = useMatch({ from: '/posts/$postId', select: (m) => m.status })
  const nearest = useMatch({ strict: false }) // 不关心具体路由时取"最近匹配"
  const currentRouter = useRouter()

  return (
    <div>
      <h1>{match.loaderData?.title}</h1>
      <span>{matchStatus}</span>
      <span>{nearest.routeId}</span>
      {/* 重跑当前 URL 全部匹配路由的 loader/beforeLoad（≠ Query 的 invalidateQueries） */}
      <button onClick={() => void currentRouter.invalidate()}>刷新数据</button>
      {/* filter 只失效部分匹配 */}
      <button
        onClick={() =>
          void currentRouter.invalidate({ filter: (m) => m.routeId === '/posts/$postId' })
        }
      >
        刷新本页
      </button>
    </div>
  )
}

// useMatches：面包屑 / 全局加载条
function Breadcrumbs() {
  const matches = useMatches()
  const routeIds = useMatches({ select: (ms) => ms.map((m) => m.routeId) })
  const anyLoading = useMatches({
    select: (ms) => ms.some((m) => m.isFetching !== false),
  })
  return (
    <div>
      {matches.map((m) => (
        <span key={m.id}>{m.routeId}</span>
      ))}
      {routeIds.join(' / ')}
      {anyLoading ? '加载中' : null}
    </div>
  )
}
```

## ⚠️ 常见陷阱

- ❌ 无参调用 `useMatch()`：options 是必填——取最近匹配写 `useMatch({ strict: false })`
- ❌ `useMatch({ from: '/other' })` 在非该路由下渲染：默认 strict 模式直接抛错（找不到匹配）——跨路由读取用 `strict: false`
- ❌ 把 `router.invalidate()` 当 Query 缓存失效：它只重跑**当前 URL 匹配到的路由**的 loader/beforeLoad；Query 缓存要用 `queryClient.invalidateQueries`
- ❌ `loaderData` 解构后判空收窄：与 Query 同理，保留对象访问或判 `status === 'success'`
- ❌ `select` 返回不稳定新对象：`useMatches({ select: (ms) => ms.map(...) })` 每次映射都生成新数组会放大重渲染——select 出原始值或稳定结构
- ❌ 判断加载用 `m.isFetching === true`：其类型是 `false | 'beforeLoad' | 'loader'`，判断"没在加载"应为 `=== false`
- ✅ `filter` 按 `routeId` 精确圈定要重跑的匹配，避免整页 loader 重放

## 🔗 相关条目

- 📄 **[Outlet 与路由组件](./19-outlet-and-route-components.md)** - 状态组件与匹配状态的分工
- 📄 **[Router 核心 API](./03-router-core-api.md)** - 路由创建与 loader 上下文
- 📄 **[Query 核心 API](./01-query-core-api.md)** - router.invalidate 与 invalidateQueries 的边界
- 📄 **[Router 基础教程](../../basics/05-router-fundamentals.md)** - loader 数据流的入门讲解
- 📄 **[Router 要点](../framework-essentials/02-router-essentials.md)** - 失效与重校验策略

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
