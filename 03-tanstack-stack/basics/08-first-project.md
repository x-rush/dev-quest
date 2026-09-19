# 第一个项目：城市天气数据面板

## 先理解，再动手

本篇首先交付一次获取全部城市、可排序和手动刷新的只读面板。当前 `fetchWeather()` 没有城市参数，查询键是 `['weather']`；本阶段验收的是同一列表的读取与排序，不包含按城市切换查询。

**前置与产物**：完成 [环境搭建](./01-environment-setup.md)、[Query 基础](./03-query-fundamentals.md) 和 [Table 基础](./04-table-fundamentals.md)，能解释数组 `map` 与 Promise 拒绝。保存下述五个文件、锁文件和一份验收记录。Router、Form 可留待下一项目；`useStarCity` 是后续扩展片段，最小阶段不要求接入。

**本节自测**：点击温度表头两次，观察行顺序与箭头，再点击刷新并比较网络请求。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

排序由 Table 的本地状态决定，不需要为了排序重新请求天气；手动刷新才调用 `refetch()`。模拟温度由 ID 确定，同一响应在刷新后不必发生数值变化，应以网络请求判断刷新是否执行。

</details>

> **文档简介**: 用 TanStack Query 取数 + TanStack Table 排序渲染，搭建可排序、可刷新的模拟天气面板；收藏数据层作为后续扩展草图
>
> **目标读者**: 已完成环境、Query 和 Table 基础，准备把读取与排序串成完整链路的学习者（进阶写法可对照 [高级特性](./07-advanced-features.md)）
>
> **前置知识**: [Query 基础](./03-query-fundamentals.md)、[Table 基础](./04-table-fundamentals.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#综合项目` `#Query` `#Table` `#数据面板` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本项目后，你将能够：

- ✅ 独立设计 queryKey 与数据获取层
- ✅ 把 Query 的数据流接入 Table 的列模型
- ✅ 在真实组件树上运用排序状态，并指出收藏草图还缺少哪些实现

---

## 📋 需求与结构

做一个最小可用的天气面板：多城市天气（温度/湿度/风速）**点击表头排序**、手动刷新和数据过期后的聚焦刷新。收藏是后续扩展：正文提供了数据层草图，但未提供收藏按钮和持久化服务，不属于最小成品。

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
import {
  createColumnHelper, columnVisibilityFeature, createSortedRowModel,
  rowSortingFeature, tableFeatures,
} from '@tanstack/react-table'
import { Weather } from './api'

// v9：createColumnHelper 需要两个泛型（TFeatures、TData），且 TFeatures 要与 App.tsx 中 useTable 注册的 features 一致
const features = tableFeatures({
  rowSortingFeature,
  columnVisibilityFeature,
  sortedRowModel: createSortedRowModel(),
})
const columnHelper = createColumnHelper<typeof features, Weather>()

// 用 columnHelper 声明，保留每列的取值类型
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
  columnVisibilityFeature, createSortedRowModel, flexRender,
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
      columnVisibilityFeature, // row.getVisibleCells() 需注册本特性
      sortedRowModel: createSortedRowModel(),
    }),
  })

  if (isPending) return <p>加载天气中...</p>
  if (isError) return <p>加载失败 <button onClick={() => refetch()}>重试</button></p>  // 同时排除 isPending 与 isError 后，data 收窄为 Weather[]

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

按下面顺序操作，每一步保存实际结果。临时改变 fetcher 的练习结束后恢复原实现；失败与空列表检查前刷新页面，避免把上一次成功缓存当成当前结果。

1. 启动工程，记录列表行数；点击“温度”表头两次，确认升序、降序及箭头一致，排序不新增天气请求。
2. 点击“刷新”，在网络面板确认产生请求。温度不变仍可能是成功，因为示例使用确定性模拟值。
3. 临时让 `fetchWeather()` 抛出错误，重新载入后等待查询重试结束，确认出现“加载失败”；恢复函数后点击“重试”，列表恢复。通过慢速网络观察初次加载提示。
4. 临时让 fetcher 返回 `[]`，确认页面不崩溃；自行补上“暂无城市”提示，区分空结果与仍在加载，然后恢复函数。
5. 数据成功返回后等待超过 60 秒，切走再切回窗口，观察过期查询重新请求。未安装 Devtools 时，浏览器网络面板即可留证。

**收藏扩展的边界**：`toggleStar` 只延迟后返回参数，不保存收藏；`fetchWeather` 也不读取收藏。当前片段不能证明收藏持久化，且默认不会失败。下一步先读 [乐观更新与回滚](../reference/language-concepts/06-optimistic-update.md)，补充收藏字段、按钮、能够读回的存储和可控失败，再验收“立即反馈 → 失败还原 → 成功后重取仍保留”。

读取与排序通过后进入 [Todo 写入项目](../projects/01-todo-app.md)；按 [学习导读](../LEARNING_GUIDE.md) 先准备其 `/api/todos` 接口。需要城市筛选时再改成参数化查询，并同时让请求参数与 queryKey 包含城市值，之后才验收城市 A/B 隔离。

---

## 🔗 相关文档

- 📄 **[Table 核心 API](../reference/language-concepts/02-table-core-api.md)** - 排序状态与行模型细节
- 📄 **[Query 核心 API](../reference/language-concepts/01-query-core-api.md)** - 本项目用到的缓存方法
- 📄 **[语法速查](../reference/quick-references/01-syntax-cheatsheet.md)** - 五库 API 一行式速查

---

**最后更新**: 2026年9月 | Dev Quest · 03-tanstack-stack


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
