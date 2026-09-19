# 进阶项目：数据看板（Table + Query 分页/排序/筛选）

## 分阶段练习与验收

**最小阶段**：先把分页参数同时传给查询键和请求。

**验收结果**：第 1、2 页不串数据，筛选后页码重置或按约定调整。

**扩展顺序**：客户端全量排序与服务端分页排序选择其一并写明数据边界。

### 开工条件与最小交付

先完成 [Todo App](01-todo-app.md)，确认 React 根节点已有 `QueryClientProvider`，Router 文件路由插件能生成 `/dashboard`。本篇使用 Query v5、Table v9、Router v1；先执行 `npm ls @tanstack/react-query @tanstack/react-table @tanstack/react-router` 并保存输出，不能把 Table v8 的 `ColumnDef<UserRow>` 与本文 v9 特性类型混用。

用下面四步收敛范围，每一步通过再继续：

1. **固定数据**：准备 25 个用户，ID 为 1～25，`name` 为 `User 01`～`User 25`；先用原生列表展示 API 返回的 `rows`，不加入 Table。
2. **请求契约**：实现同源 `GET /api/users?page=1&pageSize=20&sort=name:asc&q=`，返回 `{ rows, total }`。服务端先筛选、再排序（相同值按 ID 排序）、最后切页；`total` 是筛选后、切页前的数量。第 1 页 20 行，第 2 页 5 行。
3. **URL 状态**：将上述四项全部放进查询键和请求；打开第 2 页后刷新、后退、复制链接，各自仍得到对应数据。只展示列表和上一页/下一页按钮即可验收这一阶段。
4. **表格呈现**：加入下文 Table、排序按钮和筛选表单。筛选提交时把 `page` 重置为 1。先用提交按钮实现，确认正确后再加真正的 300ms 防抖。

本文是已有 React/Router 工程中的接线指南，不包含后端服务器。没有 API 时先用测试替身实现相同契约；不要把相对 `/api/users` 请求发送到未配置代理的 Vite 页面服务器。

> **文档简介**: 构建一个用户数据看板：服务端分页、排序、筛选的状态全部收敛到 URL，TanStack Table 渲染 + TanStack Query 取数，翻页不闪不抖。
>
> **目标读者**: 完成 Todo App、要挑战"URL 驱动数据表格"的中级开发者
>
> **前置知识**: [生态协作](../frameworks/03-ecosystem-integration.md)、[Router 基础](../basics/05-router-fundamentals.md)、[Table 基础](../basics/04-table-fundamentals.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#实战项目` `#tanstack-table` `#tanstack-query` `#服务端分页` `#搜索参数` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 项目目标

- 用户列表表格：服务端分页 + 点击表头排序 + 关键字筛选
- 全部表格状态编码进 URL（可分享、刷新可恢复）
- **预计时长**：4~6 小时

**数据流总览**：`URL search params → queryKey → API → Query 缓存 → Table state → UI`。

---

## 1. 路由与搜索参数校验

TanStack Router 用 `validateSearch` 把 URL 参数变成类型安全的状态：

```tsx
// src/routes/dashboard.tsx
import { createFileRoute } from '@tanstack/react-router'

export interface DashboardSearch {
  page: number
  pageSize: number
  sort: string
  q: string
}

export const Route = createFileRoute('/dashboard')({
  validateSearch: (search: Record<string, unknown>): DashboardSearch => ({
    page: Number.isSafeInteger(Number(search.page)) && Number(search.page) > 0
      ? Number(search.page) : 1,
    pageSize: [10, 20, 50].includes(Number(search.pageSize)) ? Number(search.pageSize) : 20,
    sort: typeof search.sort === 'string' && /^(name|createdAt):(asc|desc)$/.test(search.sort)
      ? search.sort : 'createdAt:desc',
    q: typeof search.q === 'string' ? search.q : '',
  }),
  component: DashboardPage,
})
```

任何组件里 `Route.useSearch()` 拿到的都是带默认值的类型化对象；`navigate({ search })` 修改即触发数据流。

---

## 2. 数据 Hook：分页 + 筛选 + 防抖

```ts
// src/hooks/use-user-table.ts
import { useQuery } from '@tanstack/react-query'
import type { DashboardSearch } from '../routes/dashboard'

export interface UserRow {
  id: number
  name: string
  email: string
  active: boolean
  createdAt: string
}

export function useUserTable(search: DashboardSearch) {
  const { page, pageSize, sort, q } = search

  return useQuery({
    // 所有影响结果的参数都必须进键
    queryKey: ['users', 'list', { page, pageSize, sort, q }],
    queryFn: async ({ signal }) => {
      const params = new URLSearchParams({
        page: String(page),
        pageSize: String(pageSize),
        sort,
        q,
      })
      const res = await fetch(`/api/users?${params}`, { signal })
      if (!res.ok) throw new Error('用户列表加载失败')
      return (await res.json()) as { rows: UserRow[]; total: number }
    },
    // 核心体验：翻页/筛选时保留旧数据，避免表格清空（placeholderData 函数式写法）
    placeholderData: (previousData) => previousData,
  })
}
```

**防抖**：搜索框先维护本地草稿，提交或 300ms 定时器结束后再 `navigate({ search: { ...search, q: draft, page: 1 } })`；卸载或草稿变化时清理旧定时器。`useDeferredValue` 延后渲染，不提供固定等待时间，也不会自动减少网络请求，不能代替防抖。服务端仍需独立校验所有参数，URL 校验只保护前端状态。

---

## 3. Table 配置：全手动模式

```tsx
// src/components/user-table.tsx
import {
  columnFilteringFeature, columnVisibilityFeature, flexRender, globalFilteringFeature,
  rowPaginationFeature, rowSortingFeature, tableFeatures, useTable,
} from '@tanstack/react-table'
import { Route } from '@/routes/dashboard'
import { useUserTable } from '../hooks/use-user-table'
import { columns } from './user-columns'

export function UserTable() {
  const search = Route.useSearch()
  const navigate = Route.useNavigate()
  const { data, isPlaceholderData, isPending, isError } = useUserTable(search)

  // v9：manual*/state.* 用到的每个能力都要注册对应特性（globalFilteringFeature 还强制要求 columnFilteringFeature）；服务端模式无需本地行模型
  const table = useTable({
    features: tableFeatures({
      globalFilteringFeature,
      rowSortingFeature,
      columnFilteringFeature,
      columnVisibilityFeature,
      rowPaginationFeature,
    }),
    data: data?.rows ?? [],
    columns,
    manualPagination: true, // 三 Manual：一切由服务端裁决
    manualSorting: true,
    manualFiltering: true,
    pageCount: data ? Math.ceil(data.total / search.pageSize) : -1,
    state: {
      pagination: { pageIndex: search.page - 1, pageSize: search.pageSize },
      sorting: [{ id: search.sort.split(':')[0], desc: search.sort.endsWith('desc') }],
      globalFilter: search.q,
    },
    onSortingChange: (updater) => {
      const current = [{ id: search.sort.split(':')[0], desc: search.sort.endsWith('desc') }]
      const next = typeof updater === 'function' ? updater(current) : updater
      const s = next[0] // 第三次点击可能取消排序，next 此时是空数组
      // 排序变化 → 只改 URL，Query 自动跟进
      void navigate({
        search: { ...search, sort: s ? `${s.id}:${s.desc ? 'desc' : 'asc'}` : 'createdAt:desc', page: 1 },
      })
    },
  })

  if (isPending) return <p role="status">正在加载用户…</p>
  if (isError) return <p role="alert">加载失败，请重试</p>

  return (
    <div style={{ opacity: isPlaceholderData ? 0.6 : 1, transition: 'opacity 150ms' }}>
      <table>
        <thead>
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((h) => (
                <th key={h.id}>
                  {h.isPlaceholder ? null : <button
                    disabled={!h.column.getCanSort()}
                    onClick={h.column.getToggleSortingHandler()}
                  >
                    {flexRender(h.column.columnDef.header, h.getContext())}
                    {h.column.getIsSorted() === 'asc' ? ' ↑' : h.column.getIsSorted() === 'desc' ? ' ↓' : ''}
                  </button>}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((c) => (
                <td key={c.id}>{flexRender(c.column.columnDef.cell, c.getContext())}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* 分页器：改 URL，不直接调 API */}
      <button
        disabled={search.page <= 1 || isPlaceholderData}
        onClick={() => void navigate({ search: { ...search, page: search.page - 1 } })}
      >
        上一页
      </button>
      <span>
        第 {search.page} / {table.getPageCount() || 1} 页
      </span>
      <button
        disabled={isPlaceholderData || search.page >= (table.getPageCount() || 1)}
        onClick={() => void navigate({ search: { ...search, page: search.page + 1 } })}
      >
        下一页
      </button>
    </div>
  )
}
```

---

## 4. 验收清单

`DashboardPage` 负责组合搜索表单与 `UserTable`；`user-columns` 至少定义 `name`、`createdAt` 两个允许排序的列。其他列配置 `enableSorting: false`，与 URL 白名单一致。v9 列类型需使用 `ColumnDef<typeof features, UserRow>`，因此把 §3 的 `tableFeatures(...)` 提取到模块级并导出，供列定义和 `useTable` 共享。此处不把未提供的应用外壳当作独立可运行工程。

| 输入或动作 | 必须观察到的输出 | 失败时回查 |
|---|---|---|
| `page=oops&pageSize=0&sort=password:asc` | 搜索状态归一为 `1/20/createdAt:desc`，请求无 `NaN` | §1 完整返回类型与白名单 |
| 第 2 页输入不存在的姓名并提交 | 页码回到 1，`rows=[]`、`total=0`；显示“没有匹配用户” | API 的 total 语义、提交时重置页码 |
| 排序按钮连续点三次 | 不访问 `undefined.id`；取消排序后恢复默认排序 | §3 空排序数组分支 |
| 第 2 页延迟 1 秒后返回 500 | 等待期间旧数据变淡；失败后给出错误和重试入口，不把旧行标成新页成功 | `isPlaceholderData`、HTTP 状态检查 |
| 请求未结束时换筛选 | 旧请求可被中止，最终行匹配最新 URL | §2 `signal` 传给 fetch、查询键完整性 |

补齐空结果提示和调用 `refetch()` 的重试按钮后，把上述操作的 URL、Network 请求及行数记录到自己的练习日志。`placeholderData` 仅改善等待体验，不保证下一页成功；服务端删除数据导致越界空页时，应提示返回第一页或依据 total 修正页码。

- [ ] 翻页、排序、筛选后 URL 同步变化，复制链接到新标签页还原同一视图
- [ ] 快速连续翻页不出现空白表格（placeholderData 生效）
- [ ] 浏览器后退能回到上一页的表格状态

---

## ❓ 常见坑

| 现象 | 原因 | 修复 |
|------|------|------|
| 翻页白屏闪一下 | 未配 `placeholderData: (prev) => prev` | 在 useQuery 中补上 |
| 排序后请求发了但表头无箭头 | `state.sorting` 未与 URL 双向映射 | 按 §3 显式传入 state |
| 筛选每敲一键发一次请求 | 无防抖 | 输入防抖后再 navigate |

---

## 🔗 相关文档

**下一步**：完成本页每项检查后再进入 [SaaS 后台](04-saas-admin-platform.md)，为同一查询键加入账号和租户作用域；发现问题时先回到 Router/Table 基础，避免增加权限层后掩盖数据错位。

**官方回查（2026-09-19）**：[Table v9 Quick Start](https://tanstack.com/table/latest/docs/framework/react/quick-start)、[Query 请求取消](https://tanstack.com/query/latest/docs/framework/react/guides/query-cancellation)、[React useDeferredValue](https://react.dev/reference/react/useDeferredValue)。这些资料支持 API 边界核对；本文项目的运行检查仍需由学习者执行。

- 📄 **[生态协作](../frameworks/03-ecosystem-integration.md)** - Table×Query 数据通路的原理
- 📄 **[Table 核心 API](../reference/language-concepts/02-table-core-api.md)** - manual 模式参数字典
- 📄 **[Router 核心 API](../reference/language-concepts/03-router-core-api.md)** - validateSearch 与导航
- 📄 **[查询性能优化](../advanced-topics/performance/01-query-optimization.md)** - 占位数据的成本账
- 📄 **[SaaS 后台](../projects/04-saas-admin-platform.md)** - 把看板扩成完整平台


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
