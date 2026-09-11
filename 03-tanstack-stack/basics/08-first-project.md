# 第一个项目：城市天气数据面板

> **文档简介**: 综合实战——用 TanStack Query 取数 + TanStack Table 排序渲染，搭建一个可排序、可刷新、带乐观收藏的城市天气数据面板
>
> **目标读者**: 已完成 01-07 全部教程，准备把 Query 与 Table 串成完整链路的学习者
>
> **前置知识**: [Query 基础](./03-query-fundamentals.md)、[Table 基础](./04-table-fundamentals.md)、[高级特性](./07-advanced-features.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#综合项目` `#Query` `#Table` `#数据面板` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本项目后，你将能够：

- ✅ 独立设计 queryKey 与数据获取层
- ✅ 把 Query 的数据流接入 Table 的列模型
- ✅ 在真实组件树上运用排序状态与乐观更新

---

## 📋 需求与结构

做一个最小可用的天气面板：多城市天气（温度/湿度/风速）**点击表头排序**、手动刷新 + 聚焦自动刷新、行级"收藏"用**乐观更新**即时反馈。

文件结构：`main.tsx`（Provider，见 01 篇）→ `api.ts`（fetcher）→ `hooks.ts`（数据层）→ `columns.tsx`（列定义）→ `App.tsx`（组装）。

## 🛠️ 实现步骤

### 步骤一：fetcher 层 `api.ts`

数据用 jsonplaceholder 模拟（生产中替换为真实天气 API），用确定性伪随机生成天气值保证示例可复现：

```ts
// temp 摄氏度 / wind km/h
export type Weather = { id: number; city: string; temp: number; humidity: number; wind: number }

export async function fetchWeather(): Promise<Weather[]> {
  const res = await fetch('https://jsonplaceholder.typicode.com/users')
  if (!res.ok) throw new Error(`天气接口异常: ${res.status}`)
  const users = (await res.json()) as { id: number; name: string }[]
  return users.map((u) => ({
    id: u.id,
    city: u.name,
    temp: 10 + ((u.id * 7) % 25),
    humidity: 30 + ((u.id * 13) % 60),
    wind: (u.id % 30) + 2,
  }))
}

export async function toggleStar(cityId: number, starred: boolean) {
  await new Promise((r) => setTimeout(r, 400)) // 模拟网络延迟
  return { cityId, starred }
}
```

### 步骤二：数据层 `hooks.ts`

```tsx
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchWeather, toggleStar, Weather } from './api'

const weatherKey = ['weather'] as const

export function useWeather() {
  return useQuery({
    queryKey: weatherKey,
    queryFn: fetchWeather,
    staleTime: 60_000, // 一分钟内不重复请求
  })
}

// 乐观更新三段式：onMutate 快照先行 → onError 回滚 → onSettled 对齐事实
export function useStarCity() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ cityId, starred }: { cityId: number; starred: boolean }) =>
      toggleStar(cityId, starred),
    onMutate: async ({ cityId, starred }) => {
      await queryClient.cancelQueries({ queryKey: weatherKey })
      const previous = queryClient.getQueryData<Weather[]>(weatherKey)
      queryClient.setQueryData<Weather[]>(weatherKey, (old) =>
        old?.map((c) => (c.id === cityId ? { ...c, starred } : c)),
      )
      return { previous }
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) queryClient.setQueryData(weatherKey, context.previous)
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: weatherKey }),
  })
}
```

### 步骤三：列定义 `columns.tsx`

```tsx
import { createColumnHelper } from '@tanstack/react-table'
import { Weather } from './api'

const columnHelper = createColumnHelper<Weather>()

// v9：用 columnHelper 声明，保留每列的取值类型
export const columns = columnHelper.columns([
  { accessorKey: 'city', header: '城市' },
  {
    accessorKey: 'temp',
    header: '温度',
    cell: (info) => `${info.getValue<number>()}°C`,
  },
  { accessorKey: 'humidity', header: '湿度' },
  { accessorKey: 'wind', header: '风速' },
])
```

### 步骤四：面板组装 `App.tsx`

```tsx
import { useMemo, useState } from 'react'
import {
  createSortedRowModel, flexRender,
  rowSortingFeature, SortingState, tableFeatures, useTable,
} from '@tanstack/react-table'
import { useWeather, useStarCity } from './hooks'
import { columns as baseColumns } from './columns'

export default function App() {
  const { data, isPending, isError, refetch, isFetching } = useWeather()
  const starMutation = useStarCity()
  const [sorting, setSorting] = useState<SortingState>([])

  // 操作列在前，cell 里调用乐观 mutation
  const columns = useMemo(
    () => [
      {
        id: 'star',
        header: '★',
        cell: ({ row }) => (
          <button onClick={() => starMutation.mutate({ cityId: row.original.id, starred: true })}>
            收藏
          </button>
        ),
      },
      ...baseColumns,
    ],
    [starMutation],
  )

  // v9：排序特性与行模型注册到 tableFeatures 上，核心行模型自动内置
  const table = useTable({
    data: data ?? [],
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    features: tableFeatures({
      rowSortingFeature,
      sortedRowModel: createSortedRowModel(),
    }),
  })

  if (isPending) return <p>加载天气中...</p>
  if (isError) return <p>加载失败 <button onClick={() => refetch()}>重试</button></p>

  return (
    <main className="mx-auto max-w-2xl p-6">
      <header className="mb-4 flex justify-between">
        <h1 className="text-xl font-bold">城市天气面板</h1>
        <button onClick={() => refetch()}>刷新{isFetching ? '...' : ''}</button>
      </header>
      <table className="w-full border-collapse text-sm">
        <thead>
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((h) => (
                <th key={h.id} onClick={h.column.getToggleSortingHandler()}
                    className="cursor-pointer border-b px-3 py-2 text-left">
                  {flexRender(h.column.columnDef.header, h.getContext())}
                  {{ asc: ' ↑', desc: ' ↓' }[h.column.getIsSorted() as string] ?? ''}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="hover:bg-gray-50">
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="border-b px-3 py-2">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  )
}
```

## ✅ 完成检查清单

- [ ] 点击"温度"表头可升序/降序切换，箭头方向正确
- [ ] 点击"收藏"后 UI 立即响应，弱网下失败能回滚
- [ ] 切走再切回浏览器窗口，60 秒后数据自动重新验证
- [ ] Devtools 中能看到 `['weather']` 缓存条目的 `fresh → stale` 变化

---

## 🔗 相关文档

- 📄 **[Table 核心 API](../reference/language-concepts/02-table-core-api.md)** - 排序状态与行模型细节
- 📄 **[Query 核心 API](../reference/language-concepts/01-query-core-api.md)** - 本项目用到的缓存方法
- 📄 **[语法速查](../reference/quick-references/01-syntax-cheatsheet.md)** - 五库 API 一行式速查

---

**最后更新**: 2026年9月 | Dev Quest · 03-tanstack-stack
