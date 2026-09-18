# 受控状态：state 切片与 OnChangeFn 回调

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

Table 的状态（排序、分页、筛选、列可见性…）既可以内部托管（uncontrolled，配 `initialState`），也可以提升到组件 state（controlled）：把要控制的切片放进 `state` 选项，并为**每个受控切片**提供对应的 `on<切片>Change` 回调——成对出现是硬约定。回调收到的是 `Updater<T>`（值或函数式更新），React `setState` 天然兼容。服务端分页/排序用 `manual*` 选项关闭本地计算。

## 📖 语法 / 签名

```ts
type Updater<T> = T | ((old: T) => T)
type OnChangeFn<T> = (updaterOrValue: Updater<T>) => void

useTable({
  data, columns, features,
  state: { sorting, pagination, columnFilters },  // 受控切片集中传入
  onSortingChange,                                // 与 state.sorting 成对
  onPaginationChange,
  onColumnFiltersChange,
  initialState: {},                               // 仅非受控切片的初值
  autoResetPageIndex: true,                       // 数据变化后重置页码
  manualPagination: false,                        // 关闭本地分页计算
  manualSorting: false,                            // 关闭本地排序计算
  pageCount: 1,                                   // manualPagination 时的总页数
})
```

| 状态类型 | 形状 |
|----------|------|
| `SortingState` | `{ id: string; desc: boolean }[]` |
| `PaginationState` | `{ pageIndex: number; pageSize: number }` |
| `ColumnFiltersState` | `{ id: string; value: unknown }[]` |

> v8→v9：顶层 `onStateChange` 已移除，改为**逐切片回调**（`onSortingChange` 等）。

## 💡 示例

```tsx
import * as React from 'react'
import {
  useTable, tableFeatures, rowSortingFeature, rowPaginationFeature,
  columnFilteringFeature, columnVisibilityFeature,
  createSortedRowModel, createPaginatedRowModel, createFilteredRowModel,
} from '@tanstack/react-table'
import type { SortingState, PaginationState, ColumnFiltersState } from '@tanstack/react-table'

const features = tableFeatures({
  rowSortingFeature,
  rowPaginationFeature,
  columnFilteringFeature,
  columnVisibilityFeature,
  sortedRowModel: createSortedRowModel(),
  paginatedRowModel: createPaginatedRowModel(),
  filteredRowModel: createFilteredRowModel(),
})

// 全受控：state 与 onChange 成对出现
function ControlledTable() {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [pagination, setPagination] = React.useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  })
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])

  const table = useTable({
    data: people,
    columns,
    features,
    state: { sorting, pagination, columnFilters },
    onSortingChange: setSorting,      // OnChangeFn 与 setState 签名兼容
    onPaginationChange: setPagination,
    onColumnFiltersChange: setColumnFilters,
    autoResetPageIndex: false,        // 服务端分页时防翻页后被重置
  })

  return <button onClick={() => table.setPagination({ pageIndex: 0, pageSize: 20 })}>
    每页 20 条
  </button>
}

// 服务端分页/排序：manual* + pageCount
function ServerTable({ totalCount, onFetch }: {
  totalCount: number
  onFetch: (p: PaginationState, s: SortingState) => void
}) {
  const [pagination, setPagination] = React.useState<PaginationState>({ pageIndex: 0, pageSize: 10 })
  const [sorting, setSorting] = React.useState<SortingState>([])

  React.useEffect(() => {
    onFetch(pagination, sorting)      // 状态变化后请求服务端
  }, [pagination, sorting, onFetch])

  const table = useTable({
    data: people,                     // 服务端返回的当前页数据
    columns,
    features,
    state: { pagination, sorting },
    onPaginationChange: setPagination,
    onSortingChange: setSorting,
    manualPagination: true,           // 关闭本地分页计算
    manualSorting: true,              // 关闭本地排序计算
    pageCount: Math.ceil(totalCount / pagination.pageSize),
    autoResetPageIndex: false,
  })
  return <div>{table.getRowModel().rows.length}</div>
}

// 手动处理 Updater 双形态（不用 setState 时）
function ManualUpdater() {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const table = useTable({
    data: people,
    columns,
    features,
    state: { sorting },
    onSortingChange: (updaterOrValue) => {
      if (typeof updaterOrValue === 'function') {
        setSorting((previous) => updaterOrValue(previous)) // 使用实际前态
      } else {
        setSorting(updaterOrValue)            // 值形态：直接采用
      }
    },
  })
  return <div>{table.state.sorting.length}</div>
}
```

## ⚠️ 常见陷阱

- ❌ 只传 `state` 不传回调（或反之）：受控切片没有 `on<切片>Change` 时用户操作无法正确更新外部状态——逐切片成对出现
- ❌ 仍写 v8 的顶层 `onStateChange`：v9 已移除，类型直接报错
- ❌ 受控切片又配 `initialState` 同名键：受控后 `initialState` 不生效——初值放在自己的 `useState` 里
- ❌ 服务端分页漏 `pageCount`：`getCanNextPage`/翻页按钮判定失灵
- ❌ 未确认当前版本与 manualPagination 下的自动重置默认值：显式表达所需行为，并自行处理筛选后的页码合法性
- ❌ 自己写的回调只处理值形态：`Updater` 可能是 `(old) => next` 函数，漏判函数形态会丢排序请求
- ✅ `table.state.*` 读当前状态、`table.setPagination(...)` 等实例方法直接驱动更新（值或函数均可）

<!-- full-library-explanation -->
## 受控的含义是明确状态归谁保存

先修：React useState 与函数式更新。state 给 Table 当前值，onChange 把下一次变化交回外部。缺少其中一半会导致表格显示与用户操作脱节。这与“写入数据库”无关，是否持久化由应用另行决定。

更新只能在事件或合适副作用中执行，不能在渲染函数里无条件 table.setPagination。否则一次渲染引发状态更新，状态更新又引发渲染，可能形成循环。

服务端模式的状态变化还要映射到 Query 的键与请求参数。排序或筛选变化后通常回到第一页；仅关闭自动重置后不处理这个规则，可能停在超出新结果范围的页码。

**练习：** 在第 3 页改变筛选，使结果只剩 1 页。验收：页码回到有效范围，HTTP 参数与 UI 一致；快速连续翻页不会让旧响应覆盖新页。通过函数式 setState 应用 Updater，避免读取闭包中的过时值。

## 🔗 相关条目

- 📄 **[Table 核心 API](./02-table-core-api.md)** - useTable 选项总表与 v8→v9 迁移
- 📄 **[FlexRender](./17-flexrender.md)** - 受控状态如何落到渲染
- 📄 **[Table 基础教程](../../basics/04-table-fundamentals.md)** - 受控/非受控的入门讲解
- 📄 **[数据看板项目](../../projects/02-data-dashboard.md)** - 服务端分页完整落地
- 📄 **[语法速查](../quick-references/01-syntax-cheatsheet.md)** - 一行式签名

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
