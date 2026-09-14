# Table 核心 API

## 概述

TanStack Table v9 的三个 API 层：`ColumnDef`（列声明）、`useTable` + `features`（实例配置，v9 新增必填选项）、Table/Row/Column 实例方法（读取状态与行模型）。教程见 [Table 基础](../../basics/04-table-fundamentals.md)。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#ColumnDef` `#RowModel` `#features` `#Table状态` `#API字典` |
| **更新日期** | `2026年9月` |

---

## 1. ColumnDef 列定义

### 定义

描述"一列如何取值、如何渲染"的声明对象。带 `accessor` 的列参与数据处理，只有展示字段的列为纯展示列。v9 的泛型形状为 `ColumnDef<TFeatures, TData, TValue>`（`TFeatures` 由 `features` 选项推断），推荐用 `createColumnHelper().columns([...])` 声明以保留每列的取值类型。

### 语法

```ts
type Person = { id: number; name: string; age: number; tags: string[] }

const columnHelper = createColumnHelper<CoreFeatures, Person>()  // v9 双泛型：特性集 + 数据类型（basics/04 有完整写法）

const columns = columnHelper.columns([
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
    filterFn: (row, id, value) => row.getValue<string>(id).includes(value), // v9 传函数更省事；字符串名（'includesString'）需先在 features 的 filterFns 槽位注册
    sortFn: 'basic',                  // v9 更名：v8 的 sortingFn → sortFn（字符串名同理需经 sortFns 槽位注册）
    size: 150,                        // 列宽提示
    meta: { align: 'left' },          // 自定义元信息，渲染层读取
    columns: [],                      // 子列（表头分组用）
  },
  { id: 'actions', header: '操作', cell: (ctx) => <EditBtn row={ctx.row.original} /> },
])
```

### 示例：分组表头

```tsx
const columns = columnHelper.columns([
  {
    header: '基本信息',
    columns: [
      { accessorKey: 'name', header: '姓名' },
      { accessorKey: 'age', header: '年龄' },
    ],
  },
])
// 渲染时用 table.getHeaderGroups() 遍历多层
```

### 陷阱

- 用了 `accessorFn` 而没有 `id` 时运行时报错——函数无法推出字段名
- `cell` 里读整行数据用 `ctx.row.original`，不要 `getValue()` 强转对象
- v9 中列宽/列尺寸与"列拖拽调整"拆成两个特性：只要静态宽度注册 `columnSizingFeature`，要拖拽再加 `columnResizingFeature`

## 2. useTable 与 features（v9 核心）

### 定义

v9 中 `useReactTable` 更名 **`useTable`**，且新增必填 `features` 选项：特性（Feature）、行模型（Row Model）与处理函数注册表都显式声明在 `tableFeatures()` 上，按需打包、可摇树。想保持"全都要"的 v8 习惯，用 `stockFeatures` 一把梭。

### 语法

```tsx
import {
  useTable,
  tableFeatures,
  stockFeatures,
  rowSortingFeature,
  columnFilteringFeature,
  createSortedRowModel,
  createFilteredRowModel,
  createPaginatedRowModel,
} from '@tanstack/react-table'

// 方式 A：按需注册（推荐，产物更小）
const features = tableFeatures({
  rowSortingFeature,                          // 先声明特性
  columnFilteringFeature,
  sortedRowModel: createSortedRowModel(),     // 再声明行模型槽位（类型检查有顺序要求）
  filteredRowModel: createFilteredRowModel(),
})

// 方式 B：等价 v8 行为（打包全部内置特性）
const stock = tableFeatures({ ...stockFeatures })

const table = useTable({
  data,        // TData[]，引用需稳定
  columns,     // 引用需稳定
  features,    // 必填
  // 受控状态：state + onChange 成对出现
  state: { sorting, columnFilters, pagination },
  onSortingChange: setSorting,
  onColumnFiltersChange: setColumnFilters,
  onPaginationChange: setPagination,
  getRowId: (row) => row.id,     // 稳定行 id，行选择/展开强烈推荐
  enableRowSelection: true,
  initialState: { sorting: [{ id: 'age', desc: true }] },
})
```

### v8 → v9 行模型映射

| v8 | v9 |
|----|----|
| `getCoreRowModel: getCoreRowModel()` | 移除——核心行模型自动内置 |
| `getSortedRowModel: getSortedRowModel()` | `sortedRowModel: createSortedRowModel()` |
| `getFilteredRowModel: getFilteredRowModel()` | `filteredRowModel: createFilteredRowModel()` |
| `getPaginationRowModel: getPaginationRowModel()` | `paginatedRowModel: createPaginatedRowModel()` |
| `getGroupedRowModel: getGroupedRowModel()` | `groupedRowModel: createGroupedRowModel()` |
| `getExpandedRowModel: getExpandedRowModel()` | `expandedRowModel: createExpandedRowModel()` |
| `getFacetedRowModel: getFacetedRowModel()` | `facetedRowModel: createFacetedRowModel()` |
| `sortingFns` / `filterFns` 表选项 | `sortFns` / `filterFns` 槽位（注册在 `tableFeatures()` 上） |

其他高频更名：`sortingFn` → `sortFn`、`column.getSortingFn()` → `column.getSortFn()`、固定列 `left`/`right` → `start`/`end`、`columnSizingInfo` → `columnResizing`。

### 陷阱

- v9 中行/单元格/列/表头的方法挂在**原型**上——解构方法或把它们当裸回调传递会丢失实例上下文；始终通过实例调用（`row.getValue('name')`、`column.getCanSort()`）
- `data` 或 `columns` 每次渲染都是新引用 → 行模型反复重算 → "Maximum update depth" 报错
- 用非受控模式时排序等状态默认存在实例内部，组件外无法读取

## 3. 状态类型与读取

### 状态切片（概念与 v8 一致）

| 状态 | 类型 | 说明 |
|------|------|------|
| SortingState | `{ id: string; desc: boolean }[]` | 多列排序，数组顺序即优先级 |
| ColumnFiltersState | `{ id: string; value: unknown }[]` | 每列一个筛选值 |
| PaginationState | `{ pageIndex: number; pageSize: number }` | 从 0 开始 |
| RowSelectionState | `Record<string, boolean>` | key 为 `getRowId` 的返回值 |
| GroupingState | `string[]` | 分组列 id 列表 |
| ExpandedState | `true \| Record<string, boolean>` | 展开的行 |

### 状态读取（v9 变化）

v9 的状态系统构建在 TanStack Store 之上，`table.getState()` 更换为：

```tsx
table.state                  // 全量状态（等价 v8 的 getState()）
table.store.state            // store 视图
table.atoms.sorting.get()    // 单切片原子订阅（细粒度渲染）
// 顶层 onStateChange 选项移除：用 onSortingChange 等逐切片回调，
// 或 table.store.subscribe() 订阅全部变化
```

## 4. 实例 API 速查

### Table 级

```tsx
table.getHeaderGroups()          // 表头分组（含多层）
table.getFooterGroups()          // 表尾
table.getRowModel()              // 最终行模型（流水线终点）
table.getPrePaginatedRowModel()  // 分页前的行
table.getSelectedRowModel()      // 选中的行
table.state                      // 全部状态（v9）
table.setSorting(updater)        // 编程式排序
table.reset()                    // 重置全部状态
```

### Row 级

```tsx
row.id                    // getRowId 的结果
row.original              // 原始数据
row.getAllCells()         // 全部单元格（核心 API，无特性门槛）
row.getVisibleCells()     // 可见单元格（需注册 columnVisibilityFeature）
row.getIsSelected()       // 是否选中（需注册 rowSelectionFeature）
row.toggleSelected()      // 切换选中（需注册 rowSelectionFeature）
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
- 分面方法需在 `features` 中注册对应分面特性与行模型后才可用
- 服务端分页/排序用 `manualPagination` / `manualSorting` + `pageCount`，不注册本地行模型即可

## 相关文档

- 📄 **[Table 基础](../../basics/04-table-fundamentals.md)** - 教程入口
- 📄 **[TypeScript 模式](./05-typescript-patterns.md)** - ColumnDef 泛型推断
- 📄 **[生态集成：Virtual](../library-guides/01-ecosystem-integrations.md)** - 大数据量虚拟滚动
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)** - 表格空白/无限重渲染排查
