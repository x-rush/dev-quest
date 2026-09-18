# 五库语法速查表

> **阅读准备**：熟悉 React Hook、TypeScript 泛型和对应 TanStack 包的基本职责；片段需要所在项目的 Provider、类型与依赖上下文。

## 概述

TanStack Query v5 / Table v9 / Router v1 / Form v1 / Start v1 的高频 API 一行式速查。只查签名，语义与陷阱见对应核心 API 字典。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#速查` `#API` `#五库` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. Query（@tanstack/react-query）

```tsx
const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime, gcTime, retry } },
})

const app = <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>

const query = useQuery({
  queryKey,
  queryFn,
  enabled,
  staleTime,
  select,
  placeholderData: (previousData) => previousData,
})
const { data, error, status, fetchStatus, isPending, isFetching, isError, refetch } = query
// v5：isPending 时 data 类型收窄为 undefined；v4 的 keepPreviousData 选项已移除，占位用 placeholderData 函数式写法或内置 keepPreviousData

const suspenseQuery = useSuspenseQuery({ queryKey, queryFn })
// suspenseQuery.data 不为 undefined（业务类型仍可包含 null）（v5 标准模式），配合 <Suspense>

const mutation = useMutation({ mutationFn, onMutate, onSuccess, onError, onSettled })
mutation.mutate(variables) // mutateAsync 可 await

const infiniteQuery = useInfiniteQuery({
  queryKey,
  queryFn: ({ pageParam }) => fetchPage(pageParam),
  initialPageParam,
  getNextPageParam,
})
const { pages } = infiniteQuery.data ?? { pages: [] }
const { hasNextPage, fetchNextPage, isFetchingNextPage } = infiniteQuery

const qc = useQueryClient()
qc.invalidateQueries({ queryKey, exact, refetchType })
qc.fetchQuery({ queryKey, queryFn, staleTime }) // 返回 Promise
qc.prefetchQuery({ queryKey, queryFn })
qc.getQueryData(key)
qc.setQueryData(key, updater)
qc.cancelQueries({ queryKey })
qc.removeQueries({ queryKey })
qc.clear()
const dehydratedState = dehydrate(qc)
hydrate(qc, dehydratedState)
```

## 2. Table（@tanstack/react-table）

```tsx
// v9：useReactTable → useTable，features 必填
const features = tableFeatures({
  rowSortingFeature, columnFilteringFeature, rowPaginationFeature,
  rowSelectionFeature, columnVisibilityFeature,
  sortedRowModel: createSortedRowModel(),
  filteredRowModel: createFilteredRowModel(),
  paginatedRowModel: createPaginatedRowModel(),
})
const table = useTable({
  data, columns, features,               // 核心行模型自动内置，无需 getCoreRowModel
  state: { sorting, pagination, rowSelection },
  onSortingChange: setSorting, onPaginationChange: setPagination,
  onRowSelectionChange: setRowSelection,
  getRowId: (row) => String(row.id), enableRowSelection: true,
})

// 列定义
const columnDefinitions = [
  { accessorKey: 'name', header: '姓名' },
  { id: 'x', accessorFn: (row) => row.a + row.b, header: '', cell: (info) => info.getValue() },
  { id: 'actions', cell: ({ row }) => <Btn row={row.original} /> },
]

// 渲染
table.getHeaderGroups().map(hg => hg.headers.map(h => flexRender(h.column.columnDef.header, h.getContext())))
table.getRowModel().rows.map(row => row.getVisibleCells().map(c => flexRender(c.column.columnDef.cell, c.getContext())))  // getVisibleCells 需注册 columnVisibilityFeature（无门槛替代：getAllCells）

// 常用实例方法（v9：方法须经实例调用，解构会丢上下文）
void table.state
table.setSorting(updater)
const toggleSorting = header.column.getToggleSortingHandler()
const sortingState = header.column.getIsSorted() // 'asc' | 'desc' | false
header.column.setFilterValue(value)
table.nextPage()
table.previousPage()
const canGoToNextPage = table.getCanNextPage()
const isSelected = row.getIsSelected()
row.toggleSelected()
row.toggleExpanded() // getIsSelected/toggleSelected 需注册 rowSelectionFeature
```

## 3. Router（@tanstack/react-router）

下面用代码路由构造最小路由树，不依赖文件路由生成器。`loader` 返回值由库推导到 `useLoaderData`，不要自行声明简化版 Router API 来绕过真实类型检查。

```tsx
import {
  createRootRoute, createRoute, createRouter,
  Link, Outlet, RouterProvider,
} from '@tanstack/react-router'

const rootRoute = createRootRoute({ component: () => <Outlet /> })
const postRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/posts/$postId',
  validateSearch: (search: Record<string, unknown>) => ({
    page: Number.isInteger(Number(search.page)) && Number(search.page) > 0
      ? Number(search.page) : 1,
  }),
  loader: ({ params }) => ({ id: params.postId, title: `文章 ${params.postId}` }),
  component: PostPage,
  pendingComponent: () => <p>加载中</p>,
  errorComponent: ({ error }) => <p role="alert">{error.message}</p>,
  notFoundComponent: () => <p>文章不存在</p>,
})
const router = createRouter({
  routeTree: rootRoute.addChildren([postRoute]),
  defaultPreload: 'intent',
})
declare module '@tanstack/react-router' {
  interface Register { router: typeof router }
}
function PostPage() {
  const { postId } = postRoute.useParams()
  const { page } = postRoute.useSearch()
  const post = postRoute.useLoaderData()
  const navigate = postRoute.useNavigate()
  return <>
    <h1>{post.title}</h1>
    <Link to="/posts/$postId" params={{ postId }} search={{ page: page + 1 }}
      activeProps={{ className: 'active' }} preload="intent">下一页</Link>
    <button onClick={() => void navigate({ search: { page: 1 } })}>第一页</button>
  </>
}
export function RouterApp() { return <RouterProvider router={router} /> }
```

这里的 `declare module` 是库支持的路由注册扩展：关联真实推导出的 `typeof router`，不是编造第三方函数签名。已有项目只保留其统一注册，不能重复注册另一棵路由树。

| 查阅项 | 用法与位置 |
|---|---|
| 文件路由 | 路由文件中用 `createFileRoute('/posts/$postId')({...})`，类型依赖生成的 `routeTree.gen.ts`；不用上例的手工树同时注册同一路由。 |
| 根路由与上下文 | 普通根用 `createRootRoute`；注入认证等有类型上下文时查 `createRootRouteWithContext`，在 `createRouter` 提供对应 `context`。 |
| 加载前守卫 | `beforeLoad` 在 loader 前检查上下文；需要跳转时抛出库的 `redirect(...)`，服务端仍需独立授权。 |
| 导航 | `Link` 声明链接；事件中调用 `useNavigate` 返回的函数；组件需要声明式重定向时使用 `Navigate`。 |
| 实例与阻止离开 | `useRouter` 取实例；`useBlocker` 处理未保存修改，回调与选项以所用版本 API 为准。 |
| 文件命名 | 默认约定 `index.tsx` 为索引、`$id` 为参数、`_layout` 为无路径布局、`-file` 从生成路由中排除。 |

参考：[官方导航指南](https://tanstack.com/router/latest/docs/framework/react/guide/navigation)。

## 4. Form（@tanstack/react-form）

这是组件级片段：由真实 `useForm` 推导字段和验证器类型，提交行为通过项目传入的 `onSave` 实现。

```tsx
import { useForm } from '@tanstack/react-form'

export function EmailForm({ onSave }: { onSave: (email: string) => Promise<void> }) {
  const form = useForm({
    defaultValues: { email: '' },
    onSubmit: async ({ value }) => { await onSave(value.email) },
  })
  return <form onSubmit={event => {
    event.preventDefault()
    event.stopPropagation()
    void form.handleSubmit()
  }}>
    <form.Field name="email" validators={{
      onChange: ({ value }) => value.includes('@') ? undefined : '请输入有效邮箱',
    }}>
      {field => <label>邮箱
        <input value={field.state.value} onBlur={field.handleBlur}
          onChange={event => field.handleChange(event.target.value)} />
        <span role="alert">{field.state.meta.errors.join(', ')}</span>
      </label>}
    </form.Field>
    <form.Subscribe selector={state => [state.canSubmit, state.isSubmitting]}>
      {([canSubmit, isSubmitting]) => <button type="submit" disabled={!canSubmit || isSubmitting}>
        {isSubmitting ? '保存中' : '保存'}
      </button>}
    </form.Subscribe>
    <button type="button" onClick={() => form.reset()}>重置</button>
    <button type="button" onClick={() => form.setFieldValue('email', 'learner@example.com')}>填入示例</button>
  </form>
}
```

这里只演示简单字段校验，`includes('@')` 不是完整邮箱规则。实际业务还需呈现 `onSave` 的失败状态。`form.Subscribe` 会订阅状态变化；仅在组件渲染时读取 `form.state` 不能代替订阅。

| 查阅项 | 用途 |
|---|---|
| `validators.onChange/onBlur/onSubmit` | 在字段或整个表单的不同生命周期验证；验证器入参和返回值交给库推导。 |
| `field.state.meta` | 读取 errors、isTouched、isValidating 等元数据；不要假定所有错误都是字符串。 |
| `field.pushValue/removeValue` | 在数组字段中增删元素，先用数组类型的 defaultValues 和对应数组 Field。 |
| `form.reset/setFieldValue` | 在事件或提交逻辑中重置/更新；不要在每次组件渲染时无条件调用。 |
| `isDirty/canSubmit/isSubmitting` | 通过 Subscribe 或库提供的 store 订阅机制驱动 UI。 |

参考：[官方 Form 基本概念](https://tanstack.com/form/latest/docs/framework/react/guides/basic-concepts)。

## 5. Start（@tanstack/react-start）

```ts
// 服务端函数：服务端执行，客户端透明调用
const getData = createServerFn({ method: 'GET' })
  .validator((id: unknown) => {
    if (typeof id !== 'string' || id.length === 0) throw new Error('无效 ID')
    return id
  })
  .handler(async ({ data }) => db.find(data))

// 路由中调用
createFileRoute('/x')({ loader: () => getData({ data: '1' }) })

// vite.config.ts
plugins: [tanstackStart(), viteReact()] // Start 已集成路由生成；补齐对应导入，避免重复安装 Router 插件
```

## 6. 周边常用接口

虚拟列表与 Ranger 都是 Hook，必须放在组件或自定义 Hook 内。以下两个组件分别示范滚动容器和滑块轨道如何关联 DOM。

```tsx
import { useRef, useState } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRanger } from '@tanstack/react-ranger'

export function VirtualRows() {
  const scrollRef = useRef<HTMLDivElement>(null)
  const list = useVirtualizer({
    count: 100, getScrollElement: () => scrollRef.current,
    estimateSize: () => 32, overscan: 5,
  })
  return <div ref={scrollRef} style={{ height: 240, overflow: 'auto' }}>
    <div style={{ height: list.getTotalSize(), position: 'relative' }}>
      {list.getVirtualItems().map(item => <div key={item.key} style={{
        position: 'absolute', top: 0, left: 0, height: item.size,
        transform: `translateY(${item.start}px)`,
      }}>第 {item.index + 1} 行</div>)}
    </div>
  </div>
}

export function RangeSlider() {
  const trackRef = useRef<HTMLDivElement>(null)
  const [values, setValues] = useState<ReadonlyArray<number>>([25])
  const ranger = useRanger({
    getRangerElement: () => trackRef.current,
    values, min: 0, max: 100, stepSize: 1,
    onChange: instance => setValues(instance.sortedValues),
  })
  return <div ref={trackRef} style={{ position: 'relative', height: 24, width: 240 }}>
    {ranger.handles().map((handle, index) => <button key={index} type="button"
      role="slider" aria-label="百分比" aria-valuemin={0} aria-valuemax={100}
      aria-valuenow={handle.value}
      onKeyDown={handle.onKeyDownHandler} onMouseDown={handle.onMouseDownHandler}
      onTouchStart={handle.onTouchStart}
      style={{ position: 'absolute', left: `${ranger.getPercentageForValue(handle.value)}%` }}>
      {handle.value}
    </button>)}
  </div>
}
```

Ranger 的 `onChange` 收到的是 **Ranger 实例**，从 `instance.sortedValues` 取值；不是数组参数。必须提供 `getRangerElement`。这个片段示范 API 连接，产品还需要按无障碍要求测试键盘行为、焦点样式与触摸手势。依据：[Ranger 官方 React 示例](https://github.com/TanStack/ranger/tree/main/examples/react/basic)、[官方 React Hook 实现](https://github.com/TanStack/ranger/blob/main/packages/react-ranger/src/index.tsx)。

开发工具和持久化接口按所在项目接入，不在模块顶层直接读取 `window`：

| 包与导出 | 接入方式 |
|---|---|
| `@tanstack/react-query-devtools` 的 `ReactQueryDevtools` | 在 Query Provider 内渲染 `<ReactQueryDevtools initialIsOpen={false} />`。 |
| `@tanstack/router-devtools` 的 `TanStackRouterDevtools` | 在路由上下文内渲染，可传 `position="bottom-right"`。 |
| `@tanstack/query-sync-storage-persister` 的 `createSyncStoragePersister` | 浏览器初始化阶段传 `{ storage: window.localStorage }`；SSR 不能直接访问 window，存储也可能被浏览器策略禁用。 |
| `@tanstack/react-query-persist-client` 的 `PersistQueryClientProvider` | 传 `client` 及 `persistOptions={{ persister, maxAge, buster }}`，将应用作为 children；别把令牌等敏感数据持久化。 |

## 相关文档

- 📄 **[Query 核心 API](../language-concepts/01-query-core-api.md)** - Query 完整语义
- 📄 **[Table 核心 API](../language-concepts/02-table-core-api.md)** - Table 完整语义
- 📄 **[Router 核心 API](../language-concepts/03-router-core-api.md)** - Router 完整语义
- 📄 **[Form 核心 API](../language-concepts/04-form-core-api.md)** - Form 完整语义
- 📄 **[故障排除](./02-troubleshooting.md)** - 用法对了但不工作时查这里


<!-- full-library-explanation -->
## 怎样使用这份速查而不复制出错误

本页混合参数摘录、组件片段和配置片段，不能拼成一个文件直接执行。Query/Table 摘录中的业务变量要由所在组件和项目提供；Router、Form 与周边示例展示真实导入及 Hook 调用位置。第一次学习先跑核心 API 页的完整例子，再用这里定位参数名。

先确定版本：Query v5、Table v9、Router v1、Form v1 的名称不能与旧教程混用。再确定执行位置：Hook 在组件或自定义 Hook 中，server function handler 在服务端，构建插件放配置文件。最后补齐 Provider、导入、数据函数与错误分支。

**练习：** 从本页挑一行 useQuery，写成一个显示加载、错误、空数组和正常列表的组件；再加一个 mutation，并明确成功后失效哪个键。验收：无需 as any 绕过报错，每个未定义变量都能指向具体实现。

查错顺序是“语法是否可执行 → 类型是否匹配版本 → Provider/执行环境是否正确 → 状态和网络行为是否符合预期”，不是看到红线就不断添加断言。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
