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

```ts
new QueryClient({ defaultOptions: { queries: { staleTime, gcTime, retry } } })
<QueryClientProvider client={qc}>…</QueryClientProvider>

useQuery({ queryKey, queryFn, enabled, staleTime, select, placeholderData: (prev) => prev })
useQuery 返回: { data, error, status, fetchStatus, isPending, isFetching, isError, refetch }
// v5：isPending 时 data 类型收窄为 undefined；v4 的 keepPreviousData 选项已移除，占位用 placeholderData 函数式写法或内置 keepPreviousData

useSuspenseQuery({ queryKey, queryFn })   // data 不为 undefined（业务类型仍可包含 null）（v5 标准模式），配合 <Suspense>

useMutation({ mutationFn, onMutate, onSuccess, onError, onSettled })
mutation.mutate(variables) // mutateAsync 可 await

useInfiniteQuery({ queryKey, queryFn({ pageParam }), initialPageParam, getNextPageParam })
infiniteQuery 返回: { data.pages, hasNextPage, fetchNextPage, isFetchingNextPage }

useSuspenseQuery({ queryKey, queryFn })   // data 不为 undefined（业务类型仍可包含 null），配合 <Suspense>

useQueryClient()
qc.invalidateQueries({ queryKey, exact?, refetchType? })
qc.fetchQuery({ queryKey, queryFn, staleTime? }) // 返回 Promise
qc.prefetchQuery({ queryKey, queryFn })
qc.getQueryData(key) / qc.setQueryData(key, updater)
qc.cancelQueries({ queryKey }) / qc.removeQueries({ queryKey }) / qc.clear()
dehydrate(qc) / hydrate(qc, dehydratedState)
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
{ accessorKey: 'name', header: '姓名' }
{ id: 'x', accessorFn: (row) => row.a + row.b, header: '', cell: (info) => info.getValue() }
{ id: 'actions', cell: ({ row }) => <Btn row={row.original} /> }

// 渲染
table.getHeaderGroups().map(hg => hg.headers.map(h => flexRender(h.column.columnDef.header, h.getContext())))
table.getRowModel().rows.map(row => row.getVisibleCells().map(c => flexRender(c.column.columnDef.cell, c.getContext())))  // getVisibleCells 需注册 columnVisibilityFeature（无门槛替代：getAllCells）

// 常用实例方法（v9：方法须经实例调用，解构会丢上下文）
table.state / table.setSorting(updater)
header.column.getToggleSortingHandler() / header.column.getIsSorted() // 'asc'|'desc'|false
header.column.setFilterValue(v)
table.nextPage() / table.previousPage() / table.getCanNextPage()
row.getIsSelected() / row.toggleSelected() / row.toggleExpanded()  // getIsSelected/toggleSelected 需注册 rowSelectionFeature
```

## 3. Router（@tanstack/react-router）

```tsx
createFileRoute('/posts/$postId')({ component, loader, beforeLoad, validateSearch,
                                     pendingComponent, errorComponent, notFoundComponent })
createRootRoute({ component })       // src/routes/__root.tsx
createRouter({ routeTree, defaultPreload: 'intent', context })
<RouterProvider router={router} />

<Link to="/posts/$postId" params={{ postId: '1' }} search={{ page: 2 }}
      activeProps={{ className: 'active' }} preload="intent" />
<Outlet />                            // 子路由出口
throw redirect({ to: '/login' })      // beforeLoad 守卫
<Navigate to="..." />                 // 组件内跳转

Route.useParams() / Route.useSearch() / Route.useLoaderData() / Route.useNavigate()
useNavigate()({ to, params, search }) / useRouter() / useBlocker()
// 路由文件约定：index.tsx=索引、$id=参数、_layout=无路径布局、-file=非路由文件
```

## 4. Form（@tanstack/react-form）

```tsx
const form = useForm({
  defaultValues,
  onSubmit: async ({ value, formApi }) => {},
  validators: { onChange?, onBlur?, onSubmit? }, // 函数或 Standard Schema(zod)
})

<form onSubmit={(e) => { e.preventDefault(); form.handleSubmit() }}>

<form.Field name="email" validators={{ onChange: ({ value }) => bad ? '错误' : undefined }}>
  {(field) => (
    <input
      name={field.name}
      value={field.state.value}
      onBlur={field.handleBlur}
      onChange={(e) => field.handleChange(e.target.value)}
    />
  )}
</form.Field>
// field.state.meta: { errors, isValid, isTouched, isValidating }
// field.pushValue(v) / field.removeValue(i)  数组字段

<form.Subscribe selector={(s) => s.canSubmit}>
  {(canSubmit) => <button disabled={!canSubmit} />}
</form.Subscribe>

form.reset() / form.setFieldValue(name, v) / form.state.{ canSubmit, isSubmitting, isDirty }
```

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

## 6. 周边一行式

```tsx
<ReactQueryDevtools initialIsOpen={false} />                 // @tanstack/react-query-devtools
<TanStackRouterDevtools position="bottom-right" />           // @tanstack/router-devtools
<PersistQueryClientProvider client={qc} persistOptions={{ persister, maxAge, buster }}>{children}</PersistQueryClientProvider>
createSyncStoragePersister({ storage: window.localStorage })
useVirtualizer({ count, getScrollElement, estimateSize, overscan })
useRanger({ values, onChange, min, max, stepSize })
```

## 相关文档

- 📄 **[Query 核心 API](../language-concepts/01-query-core-api.md)** - Query 完整语义
- 📄 **[Table 核心 API](../language-concepts/02-table-core-api.md)** - Table 完整语义
- 📄 **[Router 核心 API](../language-concepts/03-router-core-api.md)** - Router 完整语义
- 📄 **[Form 核心 API](../language-concepts/04-form-core-api.md)** - Form 完整语义
- 📄 **[故障排除](./02-troubleshooting.md)** - 用法对了但不工作时查这里


<!-- full-library-explanation -->
## 怎样使用这份速查而不复制出错误

本页含签名记法，`exact?`、`返回:`、`...` 表示可选参数与省略项，并非完整 JavaScript。第一次学习应先跑核心 API 页的完整例子，再用这里定位参数名。

先确定版本：Query v5、Table v9、Router v1、Form v1 的名称不能与旧教程混用。再确定执行位置：Hook 在组件或自定义 Hook 中，server function handler 在服务端，构建插件放配置文件。最后补齐 Provider、导入、数据函数与错误分支。

**练习：** 从本页挑一行 useQuery，写成一个显示加载、错误、空数组和正常列表的组件；再加一个 mutation，并明确成功后失效哪个键。验收：无需 as any 绕过报错，每个未定义变量都能指向具体实现。

查错顺序是“语法是否可执行 → 类型是否匹配版本 → Provider/执行环境是否正确 → 状态和网络行为是否符合预期”，不是看到红线就不断添加断言。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
