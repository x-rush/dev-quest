# Router 核心 API

## 概述

TanStack Router v1 的核心构建块：`createFileRoute` / `createRootRoute`（路由定义）、`createRouter`（实例）、`Link` / hooks（导航与读取）。类型安全来自 Vite 插件生成的 `routeTree.gen.ts`。教程见 [Router 基础](../../basics/05-router-fundamentals.md)。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#createFileRoute` `#RouteTree` `#params` `#searchParams` |
| **更新日期** | `2026年9月` |

---

## 1. createFileRoute

### 定义

在 `src/routes/` 下的文件中声明一个路由节点。路径字符串必须与文件位置匹配（由插件校验），导出的 `Route` 对象自带该路由的全部类型。

### 语法

```tsx
export const Route = createFileRoute('/posts/$postId')({
  component: PostDetail,        // 页面组件
  loader: ({ params }) => fetchPost(params.postId),   // 数据加载器
  beforeLoad: ({ params, search, context }) => {      // 守卫：先于 loader
    if (!context.auth.user) throw redirect({ to: '/login' })
  },
  validateSearch: z.object({ page: z.number().optional() }), // search 类型来源
  pendingComponent: Skeleton,   // loader 挂起时的 UI
  errorComponent: ErrorCard,    // loader/beforeLoad 抛错时的 UI
  notFoundComponent: NotFound,  // 404 专用 UI
  staleTime: 30_000,            // loader 数据的新鲜期
  gcTime: 5 * 60 * 1000,
})
```

### 示例：在组件中读取 Route 能力

```tsx
function PostDetail() {
  const { postId } = Route.useParams()   // { postId: string }，类型精确
  const search = Route.useSearch()       // { page?: number }，来自 validateSearch
  const data = Route.useLoaderData()     // loader 返回值的精确类型
  const navigate = Route.useNavigate()   // 预绑定本路由的跳转函数
}
```

### 陷阱

- params **永远是 string**（URL 语义），数字比较前要转换
- `validateSearch` 未声明的 search 字段会被丢弃——这是特性不是 bug
- 忘记 `declare module` 全局注册时，`<Link to>` 会退化成宽泛类型

## 2. RouteTree 与文件约定

### 定义

路由树是全部路由的嵌套结构，由 `@tanstack/router-plugin` 扫描 `src/routes/` 后生成 `routeTree.gen.ts`。

### 文件命名约定

| 模式 | 示例 | 语义 |
|------|------|------|
| `index.tsx` | `posts/index.tsx` | 索引路由 `/posts` |
| `about.tsx` | `about.tsx` | 静态路由 `/about` |
| `$param.tsx` | `posts/$postId.tsx` | 动态参数段 |
| `_*.tsx` | `posts/_layout.tsx` | 无路径布局路由（包裹子路由） |
| `-*.tsx` | `posts/-components.tsx` | 非 Route 文件（工具组件） |
| `__root.tsx` | — | 根路由（必须） |
| `[escape].tsx` | `[.well-known].tsx` | 字面量转义 |

### createRouter 组装

```tsx
import { createRouter } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'

const router = createRouter({
  routeTree,
  defaultPreload: 'intent', // hover 时预加载，见进阶篇
  context: { auth: undefined! }, // beforeLoad 中注入
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router // 全局类型注册
  }
}
```

### 陷阱

- `routeTree.gen.ts` 未及时生成（新建文件后没保存/没重启）导致类型找不到路由
- 目录下**只有** `$id.tsx` 没有 `index.tsx` 时，访问 `/posts` 会 404

## 3. 导航与读取 API

### Link 关键 props

```tsx
<Link
  to="/posts/$postId"          // 类型约束的路径
  params={{ postId: '1' }}     // 类型约束的参数
  search={{ page: 2 }}         // 类型约束的搜索参数
  activeProps={{ className: 'active' }} // 匹配当前路由时附加 props
  activeOptions={{ exact: false }}      // 前缀匹配即算激活
  preload="intent"             // hover/焦点预加载
  replace                      // 用 history.replaceState
  resetScroll={false}          // 关闭滚动重置
/>
```

### Hooks 速查

| Hook | 作用 |
|------|------|
| `useParams({ from: Route.id })` | 读路径参数（`from` 限定来源路由） |
| `useSearch({ from: Route.id })` | 读搜索参数 |
| `useNavigate()` | 编程式跳转（同样类型安全） |
| `useRouter()` | 拿 router 实例（history/state） |
| `useLoaderData({ from: Route.id })` | 读 loader 数据 |
| `useMatchRoute()` | 返回匹配函数（做自定义高亮） |
| `useBlocker()` | 离开页面拦截（未保存提醒） |

```tsx
// 编程式跳转：类型同样受 routeTree 约束
const navigate = useNavigate()
navigate({ to: '/posts/$postId', params: { postId: '3' }, search: { page: 1 } })
```

### 陷阱

- `strict` 模式（默认）下 `useParams({ from })` 要求当前组件确实渲染在该路由内，否则抛错；跨路由读取需 `strict: false` 并处理 `undefined`
- search 支持任意 JSON 可序列化值：嵌套对象/数组经 JSON 编码进 URL，解析后结构完整保留（defaultStringifySearch/defaultParseSearch 的 round-trip）

## 相关文档

- 📄 **[Router 进阶要点](../framework-essentials/02-router-essentials.md)** - 守卫/预加载/SSR
- 📄 **[Router 基础](../../basics/05-router-fundamentals.md)** - 教程入口
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)** - 路由类型报错排查
