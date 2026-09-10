# 五库语法速查表

## 概述

TanStack Query v5 / Table v8 / Router v1 / Form v1 / Start v1 的高频 API 一行式速查。只查签名，语义与陷阱见对应核心 API 字典。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#速查` `#API` `#五库` |
| **更新日期** | `2026年9月` |

---

## 1. Query（@tanstack/react-query）

```ts
new QueryClient({ defaultOptions: { queries: { staleTime, gcTime, retry } } })
<QueryClientProvider client={qc}>…</QueryClientProvider>

useQuery({ queryKey, queryFn, enabled, staleTime, select, placeholderData })
useQuery 返回: { data, error, status, fetchStatus, isPending, isFetching, isError, refetch }

useMutation({ mutationFn, onMutate, onSuccess, onError, onSettled })
mutation.mutate(variables) // mutateAsync 可 await

useInfiniteQuery({ queryKey, queryFn({ pageParam }), initialPageParam, getNextPageParam })
infiniteQuery 返回: { data.pages, hasNextPage, fetchNextPage, isFetchingNextPage }

useSuspenseQuery({ queryKey, queryFn })   // data 必非空，配合 <Suspense>

useQueryClient()
qc.invalidateQueries({ queryKey, exact?, refetchType? })
qc.fetchQuery({ queryKey, queryFn, staleTime? }) // 返回 Promise
qc.prefetchQuery({ queryKey, queryFn })
qc.getQueryData(key) / qc.setQueryData(key, updater)
qc.cancelQueries({ queryKey }) / qc.removeQueries({ queryKey }) / qc.clear()
dehydrate(qc) / hydrate(dehydratedState)
```

## 2. Table（@tanstack/react-table）

```tsx
const table = useReactTable({
  data, columns,
  getCoreRowModel: getCoreRowModel(),              // 必填
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  getGroupedRowModel: getGroupedRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
  state: { sorting, pagination, rowSelection },
  onSortingChange: setSorting, onPaginationChange: setPagination,
  getRowId: (row) => row.id, enableRowSelection: true,
})

// 列定义
{ accessorKey: 'name', header: '姓名' }
{ id: 'x', accessorFn: (row) => row.a + row.b, header: '', cell: (info) => info.getValue() }
{ id: 'actions', cell: ({ row }) => <Btn row={row.original} /> }

// 渲染
table.getHeaderGroups().map(hg => hg.headers.map(h => flexRender(h.column.columnDef.header, h.getContext())))
table.getRowModel().rows.map(row => row.getVisibleCells().map(c => flexRender(c.column.columnDef.cell, c.getContext())))

// 常用实例方法
table.getState() / table.setSorting(updater)
header.column.getToggleSortingHandler() / header.column.getIsSorted() // 'asc'|'desc'|false
header.column.setFilterValue(v)
table.nextPage() / table.previousPage() / table.getCanNextPage()
row.getIsSelected() / row.toggleSelected() / row.toggleExpanded()
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
<Redirect to="..." />                 // 组件内跳转

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
  .validator((id: string) => id)      // 入参校验
  .handler(async ({ data }) => db.find(data))

// 路由中调用
createFileRoute('/x')({ loader: () => getData({ data: '1' }) })

// vite.config.ts
plugins: [tanstackStart(), TanStackRouterVite()]
```

## 6. 周边一行式

```tsx
<ReactQueryDevtools initialIsOpen={false} />                 // @tanstack/react-query-devtools
<TanStackRouterDevtools position="bottom-right" />           // @tanstack/router-devtools
<PersistQueryClientProvider client persistOptions={{ persister, maxAge, buster }} />
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
