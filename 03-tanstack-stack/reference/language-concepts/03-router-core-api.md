# Router 核心 API

## 概述

TanStack Router v1 的核心构建块：`createFileRoute` / `createRootRoute`（路由定义）、`createRouter`（实例）、`Link` / hooks（导航与读取）。文件式路由通过生成的 `routeTree.gen.ts` 串联类型；代码式路由也支持类型推断。教程见 [Router 基础](../../basics/05-router-fundamentals.md)。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#createFileRoute` `#RouteTree` `#params` `#searchParams` |
| **更新日期** | `2026年9月` |

</details>

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

- 默认动态路径参数是字符串；配置 params.parse 后可得到转换类型，仍需验证非法输入
- validateSearch 输出形状取决于校验函数或 schema 的行为；不能假定所有校验器都自动丢弃未知字段
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
- 没有索引页时 `/posts` 的表现还取决于是否存在父路由与其组件；应检查生成树，不能只凭缺 index 断定 404

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


<!-- full-library-explanation -->
## 从文件名走到页面内容

先修：React 组件、URL 路径和查询参数。文件式路由由生成器维护路由树；代码式路由也可以获得类型安全，并不强制依赖 Vite 插件。不要手改生成文件来绕过真实文件结构问题。

一条 `/posts/3?page=2` 的路径参数来自 `$postId`，搜索状态来自 validateSearch，loader 的搜索依赖应通过 loaderDeps 声明。三者类型不同：URL 是可被用户修改的输入，TypeScript 不能替代运行时检查。

根路由 context 类型应通过 createRootRouteWithContext 等机制定义；`auth: undefined!` 只是为稍后注入占位，不是认证实现。调用 RouterProvider 时必须提供真实状态，服务端还需按请求构造。

**练习：** 新建文章详情与列表索引，分别直接访问、刷新、客户端跳转。验收：能从生成树找到父子关系，解释 Outlet 的位置，并处理非法参数。参考[路由概念](https://tanstack.com/router/latest/docs/framework/react/routing/routing-concepts)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
