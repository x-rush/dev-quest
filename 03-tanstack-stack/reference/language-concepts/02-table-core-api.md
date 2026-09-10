# Table 核心 API

## 概述

TanStack Table v8 的三个 API 层：`ColumnDef`（列声明）、Table Options（实例配置）、Table/Row/Column 实例方法（读取状态与行模型）。教程见 [Table 基础](../../basics/04-table-fundamentals.md)。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#ColumnDef` `#RowModel` `#Table状态` `#API字典` |
| **更新日期** | `2026年9月` |

---

## 1. ColumnDef 列定义

### 定义

描述"一列如何取值、如何渲染"的声明对象。带 `accessor` 的列参与数据处理，只有展示字段的列为纯展示列。

### 语法

```ts
type Person = { id: number; name: string; age: number; tags: string[] }

const columns: ColumnDef<Person>[] = [
  {
    id: 'name',                       // 唯一标识（有 accessorKey 时可省略）
    accessorKey: 'name',              // 字段路径取值
    accessorFn: (row, index) => row.name.toUpperCase(), // 函数取值（与上二选一）
    header: '姓名',                   // string | JSX | (ctx) => JSX
    cell: (info) => info.getValue<string>(), // 自定义单元格渲染
    footer: '合计',
    enableSorting: true,              // 是否可排序
    enableFiltering: true,            // 是否可筛选
    enableHiding: false,              // 是否可隐藏
    enablePinning: true,              // 是否可固定
    filterFn: 'includesString',       // 内置筛选函数或自定义
    sortingFn: 'basic',               // 排序比较器
    size: 150,                        // 列宽提示
    meta: { align: 'left' },          // 自定义元信息，渲染层读取
    columns: [],                      // 子列（表头分组用）
  },
  { id: 'actions', header: '操作', cell: (ctx) => <EditBtn row={ctx.row.original} /> },
]
```

### 示例：分组表头

```tsx
const columns: ColumnDef<Person>[] = [
  {
    header: '基本信息',
    columns: [
      { accessorKey: 'name', header: '姓名' },
      { accessorKey: 'age', header: '年龄' },
    ],
  },
]
// 渲染时用 table.getHeaderGroups() 遍历多层
```

### 陷阱

- 用了 `accessorFn` 而没有 `id` 时运行时报错——函数无法推出字段名
- `cell` 里读整行数据用 `ctx.row.original`，不要 `getValue()` 强转对象

## 2. Table Options 实例配置

### 语法

```tsx
const table = useReactTable({
  data,                 // TData[]，引用需稳定
  columns,              // 引用需稳定
  // 行模型流水线：按需接通
  getCoreRowModel: getCoreRowModel(),             // 必填
  getSortedRowModel: getSortedRowModel(),         // 排序
  getFilteredRowModel: getFilteredRowModel(),     // 筛选
  getGroupedRowModel: getGroupedRowModel(),       // 分组
  getExpandedRowModel: getExpandedRowModel(),     // 展开树
  getPaginationRowModel: getPaginationRowModel(), // 分页
  getFacetedRowModel: getFacetedRowModel(),       // 分面统计
  // 受控状态：state + onChange 成对出现
  state: { sorting, columnFilters, pagination },
  onSortingChange: setSorting,
  onColumnFiltersChange: setColumnFilters,
  onPaginationChange: setPagination,
  // 其他
  getRowId: (row) => row.id,     // 稳定行 id，行选择/展开强烈推荐
  enableRowSelection: true,
  autoResetPageIndex: true,      // 筛选变化后重置到第一页
  initialState: { sorting: [{ id: 'age', desc: true }] },
})
```

### 陷阱

- `data` 或 `columns` 每次渲染都是新引用 → 行模型反复重算 → "Maximum update depth" 报错
- 用非受控模式时排序等状态默认存在实例内部，组件外无法读取

## 3. 状态类型

| 状态 | 类型 | 说明 |
|------|------|------|
| SortingState | `{ id: string; desc: boolean }[]` | 多列排序，数组顺序即优先级 |
| ColumnFiltersState | `{ id: string; value: unknown }[]` | 每列一个筛选值 |
| PaginationState | `{ pageIndex: number; pageSize: number }` | 从 0 开始 |
| RowSelectionState | `Record<string, boolean>` | key 为 `getRowId` 的返回值 |
| GroupingState | `string[]` | 分组列 id 列表 |
| ExpandedState | `true \| Record<string, boolean>` | 展开的行 |

## 4. 实例 API 速查

### Table 级

```tsx
table.getHeaderGroups()          // 表头分组（含多层）
table.getFooterGroups()          // 表尾
table.getRowModel()              // 最终行模型（流水线终点）
table.getPrePaginationRowModel() // 分页前的行
table.getSelectedRowModel()      // 选中的行
table.getState()                 // 全部状态
table.setSorting(updater)        // 编程式排序
table.reset()                    // 重置全部状态
```

### Row 级

```tsx
row.id                    // getRowId 的结果
row.original              // 原始数据
row.getVisibleCells()     // 可见单元格
row.getIsSelected()       // 是否选中
row.toggleSelected()      // 切换选中
row.getCanExpand() / row.toggleExpanded()  // 树形展开
row.subRows               // 子行（分组/树形时存在）
```

### Column / Header 级

```tsx
header.column.getToggleSortingHandler()  // 表头点击处理器
header.column.getIsSorted()              // 'asc' | 'desc' | false
header.column.setFilterValue(value)      // 设置筛选值
header.column.getCanSort() / getCanHide()
header.isPlaceholder                     // 分组表头占位，需跳过渲染
```

### 陷阱

- 排序图标要自己根据 `getIsSorted()` 渲染，库不提供 UI
- `getFacetedUniqueValues` 等分面方法需配套传入对应 faceted 行模型

## 相关文档

- 📄 **[Table 基础](../../basics/04-table-fundamentals.md)** - 教程入口
- 📄 **[TypeScript 模式](./05-typescript-patterns.md)** - ColumnDef 泛型推断
- 📄 **[生态集成：Virtual](../library-guides/01-ecosystem-integrations.md)** - 大数据量虚拟滚动
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)** - 表格空白/无限重渲染排查
