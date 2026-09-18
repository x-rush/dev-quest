# 生态协作：Router + Table + Form 与 Query 集成

## 先看框架承担哪部分职责

**生态协作**：Router 管可分享位置，Query 管远端结果，Table 管展示变换，Form 管编辑过程。重复保存同一事实会增加同步问题。

**最小练习与预期结果**：把筛选写入 URL 和查询键，表格消费查询结果；修改筛选后刷新页面仍能恢复同一结果条件。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 一次讲清 TanStack 四件套如何互相配合：Router 预取数据、Table 消费 Query 数据、Form 提交驱动 Mutation。
>
> **目标读者**: 已分别了解 Router/Table/Form 基础用法，需要搭建完整数据流的中级开发者
>
> **前置知识**: [Query 基础](./01-tanstack-query-basics.md)、[Router 基础](../basics/05-router-fundamentals.md)、[Table 基础](../basics/04-table-fundamentals.md)、[Form 基础](../basics/06-form-fundamentals.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#tanstack-router` `#tanstack-table` `#tanstack-form` `#数据流` `#预取` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 完成后你将能够

- 在 Router 的 loader 中预取 Query 数据，消除请求瀑布
- 用 Table + Query 实现"服务端分页"的标准数据通路
- 用 Form 收集输入、驱动 Mutation，并把结果回写缓存

> 各库参数速查见 [五库语法速查表](../reference/quick-references/01-syntax-cheatsheet.md)；周边库选型见 [生态集成指南](../reference/library-guides/01-ecosystem-integrations.md)。

---

## 1. Router × Query：路由级预取

TanStack Router 的 loader 在**组件渲染之前**执行，把 Query 预取逻辑放进去，用户到达页面时数据已经（或正在）就位。

### 1.1 向 loader 注入 queryClient

通过 Router 的 context 把 queryClient 传递给每个路由：

```tsx
// src/router.tsx
import { createRouter } from '@tanstack/react-router'
import { QueryClient } from '@tanstack/react-query'
import { routeTree } from './routeTree.gen'

export const queryClient = new QueryClient()

export const router = createRouter({
  routeTree,
  context: {
    queryClient, // 注入路由上下文，所有 loader 都能拿到
  },
  defaultPreload: 'intent', // 悬停预加载：hover 链接即触发 loader
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router // 注册后全站路由获得类型推导
  }
}
```

### 1.2 在 loader 中预取

```tsx
// src/routes/posts.$postId.tsx
import { createFileRoute } from '@tanstack/react-router'

async function fetchPost(id: string) {
  const res = await fetch(`/api/posts/${id}`)
  if (!res.ok) throw new Error('文章不存在')
  return res.json()
}

export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params, context }) => {
    // ensureQueryData：缓存新鲜直接返回，过期则取回——loader 等待数据完成
    await context.queryClient.ensureQueryData({
      queryKey: ['posts', 'detail', params.postId],
      queryFn: () => fetchPost(params.postId),
    })
  },
  component: PostDetail,
})
```

### 1.3 组件中直接消费同一缓存

```tsx
function PostDetail() {
  const { postId } = Route.useParams()
  const post = Route.useLoaderData() // 类型安全的 loader 数据

  // 键与 loader 一致 → 命中同一缓存条目，不再发请求
  const { data } = useQuery({
    queryKey: ['posts', 'detail', postId],
    queryFn: () => fetchPost(postId),
    staleTime: 60_000,
  })

  return <article>{post?.title ?? data?.title}</article>
}
```

**两种等待策略**：

| 策略 | 做法 | 体验 |
|------|------|------|
| 阻塞渲染 | loader 里 `await ensureQueryData` | 进入即有数据，但首次导航稍慢 |
| 非阻塞 | loader 里 `prefetchQuery`（不 await）+ 组件处理 isPending | 立即导航，先出骨架屏 |

---

## 2. Table × Query：服务端分页数据通路

TanStack Table 是 Headless 的，数据来自哪里它不关心；做服务端分页时，把"当前页状态"放进 **URL 搜索参数（Router）**，用该状态发起 **Query**，再把结果交给 **Table**。

```tsx
import {
  createColumnHelper,
  flexRender,
  rowPaginationFeature,
  rowSortingFeature,
  tableFeatures,
  useTable,
} from '@tanstack/react-table'
import { useQuery } from '@tanstack/react-query'
import { Route } from '@/routes/users' // 搜索参数校验定义在路由文件里

interface UserRow { id: number; name: string; email: string }

// v9：createColumnHelper 需要 TFeatures 与 TData 两个泛型；manual* 选项也依赖特性注册
const features = tableFeatures({
  rowSortingFeature, // manualSorting 选项来自排序特性（核心特性自动合并，无需显式注册）
  rowPaginationFeature, // manualPagination / pageCount / state.pagination 来自分页特性
})
const columnHelper = createColumnHelper<typeof features, UserRow>()
const emptyRows: UserRow[] = [] // 模块级稳定引用，避免每次渲染产生新数组
// 用 columnHelper.columns 包一层，防止数组字面量的 TValue 类型拓宽
const columns = columnHelper.columns([
  columnHelper.accessor('name', { header: '姓名' }),
  columnHelper.accessor('email', { header: '邮箱' }),
])

export function UserTable() {
  const { pageIndex, pageSize, sortBy } = Route.useSearch() // URL 是状态的事实来源
  const queryClient = Route.useRouteContext().queryClient

  // 搜索参数变化 → 键变化 → 自动请求对应页
  const { data, isPlaceholderData, isPending } = useQuery({
    queryKey: ['users', 'list', { pageIndex, pageSize, sortBy }],
    queryFn: () =>
      fetch(`/api/users?page=${pageIndex}&size=${pageSize}&sort=${sortBy}`).then((r) => {
        if (!r.ok) throw new Error('加载用户失败')
        return r.json() as Promise<{ rows: UserRow[]; total: number }>
      }),
    placeholderData: (previousData) => previousData, // 函数式写法：翻页时保留旧数据，表格不闪空白
  })

  const table = useTable({
    data: data?.rows ?? emptyRows, // 复用模块级空数组，保持 data 引用稳定
    columns,
    manualPagination: true,   // 分页交给服务端
    manualSorting: true,      // 排序也交给服务端
    pageCount: data ? Math.ceil(data.total / pageSize) : -1,
    state: { pagination: { pageIndex, pageSize } },
    features, // 复用上方特性集；v9 必填，服务端模式同样离不开核心特性
  })

  return (
    <table>
      <thead>
        {table.getHeaderGroups().map((hg) => (
          <tr key={hg.id}>
            {hg.headers.map((h) => (
              <th key={h.id}>{flexRender(h.column.columnDef.header, h.getContext())}</th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody style={{ opacity: isPlaceholderData ? 0.5 : 1 }}>
        {table.getRowModel().rows.map((row) => (
          <tr key={row.id}>
            {row.getAllCells().map((cell) => (
              <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
```

**数据流向**：URL 搜索参数 → queryKey → 服务端请求 → 缓存 → Table state。翻页动作只改 URL（`navigate({ search })`），其余全部自动流转。

---

## 3. Form × Query：表单提交驱动 Mutation

分工一句话：**Form 管"输入是否合法"，Mutation 管"提交与缓存同步"**——`form.handleSubmit` 内调用 `mutateAsync(value)`，成功后 `invalidateQueries` 刷新列表，服务端错误（如重复邮箱）接回 Form 的错误展示即可闭环。完整代码见 [SaaS 后台](../projects/04-saas-admin-platform.md)，校验器参数见 [Form 核心 API](../reference/language-concepts/04-form-core-api.md)。

---

## 🎨 最佳实践速查

路由预取与页面查询共享同一份结果身份，键和参数不一致就无法复用。需要分享或浏览器回退恢复的筛选条件可以放 URL；临时弹窗状态或敏感输入不必全部写进地址。

翻页时保留上一页能减少空白，但须明确标记正在加载，不能让用户误以为旧数据已属于新页。loader 是否等待数据取决于首屏是否必须依赖它；次要区域可以独立加载。提交表单后验证相关缓存与 URL 表示的是同一个状态，不只检查提交按钮出现成功提示。

---

## 🔗 相关文档

- 📄 **[Router 框架要点](../reference/framework-essentials/02-router-essentials.md)** - 守卫、预加载与 SSR 集成参考
- 📄 **[Table 核心 API](../reference/language-concepts/02-table-core-api.md)** - 行模型与状态管理字典
- 📄 **[Form 核心 API](../reference/language-concepts/04-form-core-api.md)** - useForm 与校验器字典
- 📄 **[数据看板项目](../projects/02-data-dashboard.md)** - 本文 Table×Query 通路的完整落地
- 📄 **[SaaS 后台项目](../projects/04-saas-admin-platform.md)** - 四件套协作的终极实战


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
