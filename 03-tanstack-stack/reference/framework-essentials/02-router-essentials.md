# Router 框架要点：守卫、预加载、嵌套布局与 SSR 集成

## 概述

TanStack Router v1 的四大生产场景：登录守卫、数据预加载、嵌套布局组织，以及 SSR/全栈集成。核心都是同一条链：`beforeLoad → loader → component`。教程见 [Router 基础](../../basics/05-router-fundamentals.md)。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#路由守卫` `#预加载` `#嵌套布局` `#SSR` |
| **更新日期** | `2026年9月` |

---

## 1. 路由守卫：beforeLoad + redirect

### 定义

`beforeLoad` 在 loader 与组件渲染之前运行，是认证/授权的唯一正确位置。用 `throw redirect(...)` 中断导航。

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
const router = createRouter({ routeTree, defaultPreload: 'intent' }) // 全局：hover 即预加载
<Link to="/posts/$postId" params={{ postId: id }} preload="viewport" /> // 单链接覆盖
```

### 与 TanStack Query 集成：loader 预取缓存

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { queryClient } from '@/lib/query-client'
import { queryKeys } from '@/lib/query-keys'

// preload 与 loader 共用一个"确保缓存"函数，命中新鲜缓存时不重复请求
function ensurePost(postId: string) {
  return queryClient.ensureQueryData({
    queryKey: queryKeys.post(postId),
    queryFn: () => fetchPost(postId),
  })
}

export const Route = createFileRoute('/posts/$postId')({
  preload: ({ params }) => ensurePost(params.postId), // hover 预加载
  loader: ({ params }) => ensurePost(params.postId),  // 正式导航
  component: PostDetail, // 组件内 useQuery 直接命中缓存，零等待
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
│   ├── _auth.dashboard.tsx  # → /dashboard
│   └── _auth.settings.tsx   # → /settings
└── posts.tsx                # 常规布局：posts 相关页共用
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
// 'use client' 组件中：服务器预取 + HydrationBoundary 注水
const [queryClient] = useState(() => new QueryClient())
await queryClient.prefetchQuery({ queryKey, queryFn }) // 服务端组件阶段
<HydrationBoundary state={dehydrate(queryClient)}>
  <ClientPage />
</HydrationBoundary>
```

> Next.js 集成的完整指南见 02-nextjs-frontend 模块相关文档。

### 陷阱

- SSR 中 `QueryClient` 必须每请求新建（闭包工厂），单例会把 A 用户缓存发给 B 用户
- 服务端 prefetch 的查询要与客户端 `useQuery` 的 key **完全一致**，否则客户端重复请求
- loader 返回值必须可序列化（Date/Map 会静默变样或报错）

## 相关文档

- 📄 **[Router 核心 API](../language-concepts/03-router-core-api.md)** - beforeLoad/loader 的完整签名
- 📄 **[Query 框架要点](./01-query-essentials.md)** - ensureQueryData 与缓存语义
- 📄 **[Router 基础](../../basics/05-router-fundamentals.md)** - 教程入口
- 📄 **[语法速查](../quick-references/01-syntax-cheatsheet.md)** - Router 一行式 API
