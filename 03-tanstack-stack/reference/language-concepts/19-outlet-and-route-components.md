# Outlet 与路由组件：notFoundComponent / errorComponent / pendingComponent

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

Router 的 UI 挂载点分两层：`<Outlet />` 渲染下一层匹配到的子路由组件，是布局嵌套的枢纽；三类"状态组件"——`notFoundComponent`（404）、`errorComponent`（渲染异常兜底）、`pendingComponent`（loader/beforeLoad 挂起占位）——可在单个路由上声明，也可在 `createRouter` 上用 `default*` 全局兜底。`beforeLoad` 抛 `notFound()` 会向上冒泡到最近一层的 `notFoundComponent`。

## 📖 语法 / 签名

```tsx
// 路由级
createRootRoute({
  component: () => (<><nav /><Outlet /></>),  // 不渲染 Outlet 子路由不出现
  notFoundComponent: NotFound,           // 匹配不到/抛 notFound() 时
  errorComponent: ErrorCard,             // 组件树抛错时（false 可关闭兜底 UI）
})
createRoute({
  getParentRoute: () => rootRoute,
  path: '/$postId',
  pendingComponent: Pending,             // 本路由 loader/beforeLoad 挂起时
  loader: ({ params }) => fetchPost(params.postId),
  beforeLoad: () => { if (bad) throw notFound() },
})

// 全局兜底
createRouter({
  routeTree,
  defaultPendingComponent: Pending,
  defaultErrorComponent: ErrorCard,
  defaultNotFoundComponent: NotFound,
  defaultPendingMs: 1000,     // 挂起超过该毫秒才显示 pending UI（默认 1000）
  defaultPendingMinMs: 500,   // pending UI 最少停留毫秒（默认 500），防闪烁
})
```

| 组件 props | 说明 |
|------------|------|
| `ErrorComponentProps` | `{ error, info?, reset }`——`error` 是抛出的对象（不一定是 Error 实例），`reset()` 清除错误重试渲染 |
| NotFound 组件 | 无必填 props；路由上声明即自动接管子树 404 |

## 💡 示例

```tsx
import {
  createRootRoute, createRoute, createRouter, Outlet, notFound,
} from '@tanstack/react-router'
import type { ErrorComponentProps } from '@tanstack/react-router'

function NotFound() {
  return <p>页面不存在</p>
}

function ErrorCard({ error, reset }: ErrorComponentProps) {
  return (
    <div>
      {/* error 类型是 unknown：先收窄再取 message */}
      <p>{error instanceof Error ? error.message : String(error)}</p>
      <button onClick={reset}>重试</button>
    </div>
  )
}

function Pending() {
  return <p>加载中…</p>
}

// Outlet：布局路由的核心——导航常驻，内容区随 URL 切换
const rootRoute = createRootRoute({
  component: () => (
    <div>
      <nav>站点导航</nav>
      <Outlet />
    </div>
  ),
  notFoundComponent: NotFound,
  errorComponent: ErrorCard,
})

const postsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/posts',
  pendingComponent: Pending,
})

const postRoute = createRoute({
  getParentRoute: () => postsRoute,
  path: '/$postId',
  loader: ({ params }) => fetchPost(params.postId),
  // loader 前置校验：抛 notFound() 交给最近一层的 notFoundComponent
  beforeLoad: ({ params }) => {
    if (params.postId === '0') throw notFound()
  },
})

const routeTree = rootRoute.addChildren([postsRoute.addChildren([postRoute])])

const router = createRouter({
  routeTree,
  defaultPendingComponent: Pending,   // 未显式声明 pendingComponent 的路由走这里
  defaultErrorComponent: ErrorCard,
  defaultNotFoundComponent: NotFound,
  defaultPendingMs: 300,              // 显式调小：更快出现占位
  defaultPendingMinMs: 500,
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
```

## ⚠️ 常见陷阱

- ❌ 布局组件忘了渲染 `<Outlet />`：子路由匹配成功也无处渲染，页面空白
- ❌ `errorComponent` 里直接 `error.message`：`error` 类型是 unknown（任何值都可 throw）——先 `instanceof Error` 收窄
- ❌ 忽略路由 errorComponent：loader/beforeLoad 抛错可由它处理；在该错误界面提供数据重载，而不是依赖未挂载的成功组件（见 [useMatch 系列](./20-use-match-hooks.md)）
- ❌ 以为 `notFound()` 只影响当前路由：它向上冒泡到**最近一层**声明了 `notFoundComponent` 的路由
- ❌ 每个路由都重复写三个状态组件：先给 `createRouter` 配 `default*`，个别路由再覆写
- ❌ pending UI 无延迟直接闪现：`defaultPendingMs` 默认 1000ms 内不显示；`defaultPendingMinMs` 保证最短停留防抖动
- ✅ `errorComponent: false` 可显式关闭某路由的错误兜底 UI

<!-- full-library-explanation -->
## 区分不存在、失败和等待

先修：父子路由与 Promise。不存在表示目标资源或路径无法提供；失败表示本来可能存在，但加载或渲染发生异常；等待表示工作尚未完成。分别用 notFoundComponent、errorComponent、pendingComponent 表达，便于用户采取正确操作。

父组件写了自定义布局却省略 Outlet，子页面没有渲染位置。状态组件也应保留适当导航，让用户能返回其他页面。pendingMs 是显示等待界面的延迟，pendingMinMs 是显示后的最短时间，两者不改变接口本身的速度。

errorComponent 的 reset 主要重置错误边界；loader 失败后需要重新加载路由数据时，应使用 router.invalidate 等对应机制。不要把失败入口藏在只有成功页面才会挂载的组件中。

**练习：** 为同一路由模拟慢响应、抛 Error、抛 notFound，记录三种 UI。验收：重试后可恢复，父导航仍可用，404 不显示内部堆栈。参考[数据加载错误处理](https://tanstack.com/router/latest/docs/framework/react/guide/data-loading)。

## 🔗 相关条目

- 📄 **[Router 核心 API](./03-router-core-api.md)** - createRoute/createRouter 选项总表
- 📄 **[useMatch 系列](./20-use-match-hooks.md)** - 组件内读取匹配状态与触发刷新
- 📄 **[Router 基础教程](../../basics/05-router-fundamentals.md)** - 布局嵌套入门
- 📄 **[Router 要点](../framework-essentials/02-router-essentials.md)** - 路由数据流要点
- 📄 **[SaaS 管理平台项目](../../projects/04-saas-admin-platform.md)** - 布局与兜底组件的工程化组织

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
