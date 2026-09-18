# Router 框架要点：守卫、预加载、嵌套布局与 SSR 集成

## 概述

TanStack Router v1 的四大生产场景：登录守卫、数据预加载、嵌套布局组织，以及 SSR/全栈集成。核心都是同一条链：`beforeLoad → loader → component`。教程见 [Router 基础](../../basics/05-router-fundamentals.md)。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#路由守卫` `#预加载` `#嵌套布局` `#SSR` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. 路由守卫：beforeLoad + redirect

### 定义

`beforeLoad` 在 loader 与组件渲染之前运行，适合导航前的登录检查；服务端资源授权仍须在 API/server function 中执行。用 `throw redirect(...)` 中断导航。

### 语法与示例

```tsx
import { createFileRoute, redirect } from '@tanstack/react-router'

export const Route = createFileRoute('/_auth/dashboard')({
  beforeLoad: ({ context, location }) => {
    // context 在 RouterProvider 时注入，根路由 beforeLoad 中统一装配
    if (!context.auth.user) {
      throw redirect({ to: '/login', search: { redirect: location.href } }) // 登录后跳回
    }
  },
  component: Dashboard,
})
```

```tsx
// 根路由装配 context
const router = createRouter({ routeTree, context: { auth: undefined! } })

function App() {
  const auth = useAuthStore()
  return <RouterProvider router={router} context={{ auth }} />
}
```

### 陷阱

- `beforeLoad` 里**禁止** setState 等副作用——它可能在渲染周期外运行
- 守卫抛出的错误默认进 `errorComponent`；想静默跳转就用 `throw redirect`，想展示提示就抛 `Error`

## 2. 数据预加载

### 定义

Router 的 `preload` 让导航目标在**用户感知之前**就开始加载 loader 数据：hover（intent）、接近视口（viewport）、渲染即取（render）。

### 语法

```tsx
const router = createRouter({ routeTree, defaultPreload: 'intent' }); // 全局：hover 即预加载
<Link to="/posts/$postId" params={{ postId: id }} preload="viewport" /> // 单链接覆盖
```

### 与 TanStack Query 集成：loader 预取缓存

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { queryClient } from '@/lib/query-client'
import { queryKeys } from '@/lib/query-keys'

// intent 预加载与正式导航均运行 loader；ensureQueryData 默认复用已有缓存
function ensurePost(postId: string) {
  return queryClient.ensureQueryData({
    queryKey: queryKeys.post(postId),
    queryFn: () => fetchPost(postId),
  })
}

export const Route = createFileRoute('/posts/$postId')({
  loader: ({ params }) => ensurePost(params.postId),  // 正式导航
  component: PostDetail, // 相同键可复用缓存；新鲜度与后台重取仍需配置
})
```

### 陷阱

- 预加载只对 **loader / Query 预取**生效，不会预渲染组件
- 全开 `defaultPreload: 'intent'` 在列表页会产生大量请求，列表项可用 `preload={false}` 抑制

## 3. 嵌套布局

### 定义

目录嵌套 = 路由嵌套。父路由组件中的 `<Outlet />` 是子路由渲染点；`_` 前缀布局提供"包裹但不占路径"的层。

### 示例

```text
src/routes/
├── __root.tsx               # 根壳：导航 + <Outlet/>
├── _auth.tsx                # 布局路由：登录态壳（不占路径）
├── _auth.dashboard.tsx  # → /dashboard
├── _auth.settings.tsx   # → /settings
├── posts.tsx                # 常规布局：posts 相关页共用
├── posts.index.tsx      # → /posts
└── posts.$postId.tsx    # → /posts/:postId
```

```tsx
// posts.tsx：父布局
export const Route = createFileRoute('/posts')({
  component: () => (
    <>
      <TabsNav />       {/* posts 专属页签 */}
      <Outlet />        {/* index / $postId 渲染在这里 */}
    </>
  ),
})
```

### 陷阱

- 父路由组件重渲染会连带子路由——布局组件保持轻量，重逻辑放子路由
- 只有 `posts.$postId.tsx` 而没有 `posts.tsx` 时，Router 会自动跳过布局层直连根路由

## 4. SSR 集成

### 定义

Router 是同构友好的：loader 在服务端与客户端同签名执行；配合 TanStack Start 或 Next.js 时，loader 数据/Query 缓存经序列化传给客户端。

### TanStack Start 模式

```tsx
import { createServerFn } from '@tanstack/react-start'

// 服务端执行，客户端透明调用
const getWeather = createServerFn({ method: 'GET' }).handler(async () =>
  db.weather.list(), // 服务端代码，不进客户端包
)

export const Route = createFileRoute('/weather')({
  loader: () => getWeather(), // loader 中直接调用
})
```

### Next.js App Router 中使用 Query

```tsx
// 服务器组件片段；需导入 QueryClient/dehydrate/HydrationBoundary
// queryKey、queryFn 与 ClientPage 由具体页面提供
const queryClient = new QueryClient()
await queryClient.prefetchQuery({ queryKey, queryFn })
return <HydrationBoundary state={dehydrate(queryClient)}>
  <ClientPage />
</HydrationBoundary>
```

> Next.js 集成的完整指南见 02-nextjs-frontend 模块相关文档。

### 陷阱

- SSR 中 `QueryClient` 必须每请求新建（闭包工厂），单例会把 A 用户缓存发给 B 用户
- 服务端 prefetch 的查询要与客户端 `useQuery` 的 key **完全一致**，否则客户端重复请求
- 跨 SSR 边界的数据必须符合所用序列化器规则；Start 支持的类型不等同于裸 JSON，不能笼统禁止 Date/Map

## 相关文档

- 📄 **[Router 核心 API](../language-concepts/03-router-core-api.md)** - beforeLoad/loader 的完整签名
- 📄 **[Query 框架要点](./01-query-essentials.md)** - ensureQueryData 与缓存语义
- 📄 **[Router 基础](../../basics/05-router-fundamentals.md)** - 教程入口
- 📄 **[语法速查](../quick-references/01-syntax-cheatsheet.md)** - Router 一行式 API


<!-- full-library-explanation -->
## 预加载与正式导航走同一套依赖

先修：路由树、Promise 和 QueryClient。intent 预加载会提前运行目标路由的数据加载流程，不需要额外发明路由选项 preload 回调。loader 可通过参数中的 preload 标志识别这次调用的来源。

如果 loader 使用 Query，路由上下文应携带本次应用/请求的 client，避免 SSR 导入一个跨请求全局单例。Router 的 loader 缓存与 Query 缓存各有新鲜度；可用集成配置明确谁负责数据缓存，不能以为 router.invalidate 会自动使 Query 数据过期。

beforeLoad 适合在导航开始前检查登录状态并重定向，但它可能在客户端执行，也可能因预加载被调用。写操作不能放进 loader 或 beforeLoad，否则用户只是悬停链接就可能触发副作用。服务端接口仍须自行认证授权。

**练习：** 悬停文章链接后再点击，记录 loader 调用来源与接口次数；让数据仍在 Query 缓存中，观察 ensureQueryData 的返回。验收：解释两层缓存、确认悬停没有写入数据，并让未登录者直接访问接口也被拒绝。参考[路由数据加载](https://tanstack.com/router/latest/docs/framework/react/guide/data-loading)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
