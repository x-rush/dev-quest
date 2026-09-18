# Router 基础：路由树、文件式路由与导航

## 先理解，再动手

路由把位置变成可保存、可分享的状态。搜索参数来自文本，需要解析与校验，不能因 TypeScript 类型存在就信任地址栏输入。

**本节自测**：直接访问带 page=abc 的地址，并为缺少 page 设置默认值。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

非法参数应有确定降级或错误提示；刷新与页面内跳转应采用同一规则。

</details>

> **文档简介**: 上手 TanStack Router v1——理解"文件结构即路由树"，用 createFileRoute 定义路由，用类型安全的 Link 与 Outlet 搭建导航骨架
>
> **目标读者**: 已用过 React Router 或 Next.js 文件路由，想体验 100% 类型安全路由的开发者
>
> **前置知识**: [环境搭建](./01-environment-setup.md)中已配置 `TanStackRouterVite` 插件

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#TanStack-Router` `#文件路由` `#Link` `#Outlet` `#类型安全` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 说出文件命名与路由树的对应规则
- ✅ 用 `createFileRoute` / `createRootRoute` / `createRouter` 组装应用
- ✅ 用类型安全的 `<Link>` 携带 params 跳转
- ✅ 用 `<Outlet />` 渲染嵌套子路由

---

## 🔍 路由树与文件结构

**定义**: TanStack Router 把 `src/routes/` 目录结构 1:1 映射为一棵路由树，并由 Vite 插件生成 `routeTree.gen.ts`，让每个路由的 params、search、context 都有精确类型。

**文件命名约定**：

| 文件 | 路由 | 说明 |
|------|------|------|
| `__root.tsx` | 根布局 | 整个应用的壳，必须存在 |
| `index.tsx` | `/`（所在目录的索引） | 目录默认页 |
| `about.tsx` | `/about` | 普通静态路由 |
| `posts/$postId.tsx` | `/posts/:postId` | `$` 前缀 = 动态参数 |
| `posts/index.tsx` | `/posts` | posts 目录索引 |
| `_layout.tsx` | 不产生路径段 | 下划线前缀 = 仅提供布局包裹 |

## 🛠️ 实践：搭建带导航的多页应用

### 步骤一：根布局 `src/routes/__root.tsx`

```tsx
import { createRootRoute, Link, Outlet } from '@tanstack/react-router'

export const Route = createRootRoute({
  component: RootLayout,
})

function RootLayout() {
  return (
    <div className="mx-auto max-w-2xl p-6">
      <nav className="mb-6 flex gap-4">
        {/* to 的取值有类型约束，拼错路径直接编译报错 */}
        <Link to="/" activeProps={{ className: 'font-bold' }}>
          首页
        </Link>
        <Link to="/posts" activeProps={{ className: 'font-bold' }}>
          文章列表
        </Link>
      </nav>
      {/* 子路由渲染出口 */}
      <Outlet />
    </div>
  )
}
```

### 步骤二：列表页 `src/routes/posts/index.tsx`

```tsx
import { createFileRoute, Link } from '@tanstack/react-router'

export const Route = createFileRoute('/posts/')({
  component: PostList,
})

function PostList() {
  const posts = [
    { id: '1', title: 'Headless 哲学' },
    { id: '2', title: 'Query 缓存' },
  ]
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>
          {/* params 同样类型安全：缺字段或多字段都会编译报错 */}
          <Link to="/posts/$postId" params={{ postId: post.id }}>
            {post.title}
          </Link>
        </li>
      ))}
    </ul>
  )
}
```

### 步骤三：详情页 `src/routes/posts/$postId.tsx`

```tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/posts/$postId')({
  component: PostDetail,
})

function PostDetail() {
  // Route.useParams() 返回精确的 { postId: string }，自动收窄
  const { postId } = Route.useParams()
  return <h1>文章 #{postId}</h1>
}
```

### 步骤四：组装入口 `src/main.tsx`

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createRouter, RouterProvider } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'

const router = createRouter({ routeTree })

// 把路由类型注册到全局，Link/useParams 等才可获得完整类型提示
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
```

**关键点解析**：

- `routeTree.gen.ts` 由插件在 dev/build 时重新生成，新增路由文件后保存即可
- `createFileRoute('/posts/$postId')` 的路径字符串由插件校验，与文件位置不匹配会报错
- `<Link>` 的 `to`、`params`、`search` 全部受类型约束——这是 Router 与其他路由器的核心差异

## 📤 Outlet 与嵌套布局

`<Outlet />` 是子路由的渲染出口。父路由组件负责"公共外壳"，子路由负责"内容区域"：

```text
__root.tsx          → 导航栏 + <Outlet />
posts/index.tsx     → 列表内容
posts/$postId.tsx   → 详情内容
```

带目录的布局（如 `posts/_layout.tsx`）可以让 `/posts/*` 下的所有页面共享一个不占路径的包装层，详见 [Router 进阶要点](../reference/framework-essentials/02-router-essentials.md)。

## ✅ 最佳实践

路由参数属于某个路由契约。详情页读取该路由的类型化参数，导航时传入 params，能让拼错名称或漏参数更早暴露；参数在 URL 中出现仍不代表已通过业务验证。例如 id 有正确的字符串类型，也可能对应不存在的记录。

文件路由项目修改源路由，不手改生成树。用一次“列表 → 详情 → 返回 → 直接刷新详情”的实验检查地址、选中导航和返回状态是否一致，不能只验证点击后出现了页面。

---

## 🎯 练习与实践

### 练习一：三页骨架

- [ ] 实现 首页 / 关于 / 文章详情 三个路由，导航栏含当前页高亮
- [ ] 故意把 `params` 写错字段名，观察 TypeScript 报错信息

### 练习二：参数路由

- [ ] 给详情页加一个"上一篇/下一篇"按钮，用 `Link` + 递增的 `postId` 跳转
- [ ] 打开 `routeTree.gen.ts`，找到自己路由对应的节点与类型

---

## 🔗 相关文档

- 📄 **[Form 基础](./06-form-fundamentals.md)** - 下一篇：Headless 表单
- 📄 **[Router 核心 API](../reference/language-concepts/03-router-core-api.md)** - createFileRoute 与 hooks 完整字典
- 📄 **[Router 进阶要点](../reference/framework-essentials/02-router-essentials.md)** - 守卫、预加载与嵌套布局

---

**最后更新**: 2026年9月 | Dev Quest · 03-tanstack-stack


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
