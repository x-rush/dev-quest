# 进阶项目：数据看板（Table + Query 分页/排序/筛选）

> **文档简介**: 构建一个用户数据看板：服务端分页、排序、筛选的状态全部收敛到 URL，TanStack Table 渲染 + TanStack Query 取数，翻页不闪不抖。
>
> **目标读者**: 完成 Todo App、要挑战"URL 驱动数据表格"的中级开发者
>
> **前置知识**: [生态协作](../frameworks/03-ecosystem-integration.md)、[Router 基础](../basics/05-router-fundamentals.md)、[Table 基础](../basics/04-table-fundamentals.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#实战项目` `#tanstack-table` `#tanstack-query` `#服务端分页` `#搜索参数` |
| **更新日期** | 2026年9月 |

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

interface DashboardSearch {
  page: number
  pageSize: number
  sort: string
  q: string
}

export const Route = createFileRoute('/dashboard')({
  validateSearch: (search: Record<string, unknown>): Partial<DashboardSearch> => ({
    page: Number(search.page ?? 1),
    pageSize: Number(search.pageSize ?? 20),
    sort: typeof search.sort === 'string' ? search.sort : 'createdAt:desc',
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
    queryFn: async () => {
      const params = new URLSearchParams({
        page: String(page),
        pageSize: String(pageSize),
        sort,
        q,
      })
      const res = await fetch(`/api/users?${params}`)
      if (!res.ok) throw new Error('用户列表加载失败')
      return (await res.json()) as { rows: UserRow[]; total: number }
    },
    // 核心体验：翻页/筛选时保留旧数据，避免表格清空（placeholderData 函数式写法）
    placeholderData: (previousData) => previousData,
  })
}
```

**防抖**：搜索框输入直接改 URL 会每键发请求。用 300ms 防抖后再 `navigate`，或用 `useDeferredValue` 包装 `q` 再拼键。

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
      const s = next[0]
      // 排序变化 → 只改 URL，Query 自动跟进
      void navigate({
        search: { ...search, sort: `${s.id}:${s.desc ? 'desc' : 'asc'}`, page: 1 },
      })
    },
  })

  if (isPending) return <TableSkeleton rows={search.pageSize} />
  if (isError) return <p role="alert">加载失败，请重试</p>

  return (
    <div style={{ opacity: isPlaceholderData ? 0.6 : 1, transition: 'opacity 150ms' }}>
      <table>
        <thead>
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((h) => (
                <th key={h.id} onClick={h.column.getToggleSortingHandler()}>
                  {flexRender(h.column.columnDef.header, h.getContext())}
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

- 📄 **[生态协作](../frameworks/03-ecosystem-integration.md)** - Table×Query 数据通路的原理
- 📄 **[Table 核心 API](../reference/language-concepts/02-table-core-api.md)** - manual 模式参数字典
- 📄 **[Router 核心 API](../reference/language-concepts/03-router-core-api.md)** - validateSearch 与导航
- 📄 **[查询性能优化](../advanced-topics/performance/01-query-optimization.md)** - 占位数据的成本账
- 📄 **[SaaS 后台](../projects/04-saas-admin-platform.md)** - 把看板扩成完整平台
