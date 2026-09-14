# FlexRender：Table 渲染入口与单元格上下文

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

`FlexRender`（组件形式）/ `flexRender`（函数形式）是 Table 把列定义里的 `header`/`cell`/`footer` 渲染物（string | JSX | 函数组件）落到 React 节点的唯一入口。v9 起它脱离 `createTableHook` 变为直接可导入的顶层 API，且实例上还挂了 `table.FlexRender` 便捷形态。渲染单元格时拿到的 `CellContext`（即 `cell.getContext()`）携带 `getValue`/`row`/`column`/`table` 等完整上下文。

## 📖 语法 / 签名

```tsx
// 组件形式：cell / header / footer 三个 prop 三选一（类型为判别联合，其余 prop 是 never）
<FlexRender header={header} />          // 渲染 header.column.columnDef.header
<FlexRender cell={cell} />              // 渲染 cell.column.columnDef.cell
<FlexRender footer={footer} />          // 渲染 footer.column.columnDef.footer

// 函数形式（组件形式的底层）：
flexRender(cell.column.columnDef.cell, cell.getContext())
flexRender(header.column.columnDef.header, header.getContext())

// 实例便捷形态（等价组件形式，无需再导入）：
<table.FlexRender cell={cell} />
```

| CellContext 成员 | 说明 |
|------------------|------|
| `getValue<T>()` | 当前列的原始值（配合泛型收窄） |
| `renderValue()` | 经 `accessorFn` 处理后的展示值（`undefined` 时返回 null） |
| `row` | 行对象：`row.original` 原始数据、`row.id`、`row.getVisibleCells()` |
| `column` | 列实例：`column.id`、`columnDef`、排序/筛选等 feature 方法 |
| `cell` / `table` | 单元格与表实例 |

| 渲染位 | 前提 |
|--------|------|
| `header.isPlaceholder` | 分组列的占位 header，为 true 时渲染 null |
| `header.colSpan` | 表头 `<th>` 必须透传，否则列对不齐 |
| `row.getVisibleCells()` | 需要 `columnVisibilityFeature`（core 行只有 `getAllCells()`） |

## 💡 示例

```tsx
import {
  useTable, tableFeatures, rowSortingFeature, columnVisibilityFeature,
  createColumnHelper, FlexRender, flexRender,
} from '@tanstack/react-table'

const features = tableFeatures({
  rowSortingFeature,       // getToggleSortingHandler 来自排序特性
  columnVisibilityFeature, // getVisibleCells 需要此特性
})
const columnHelper = createColumnHelper<typeof features, Person>()

const columns = columnHelper.columns([
  {
    accessorKey: 'name',
    header: '姓名',
    // CellContext：info.getValue / info.renderValue / info.row / info.column / info.table
    cell: (info) => <b>{info.getValue<string>()}</b>,
  },
  {
    accessorKey: 'age',
    header: ({ column }) => (   // header 也可以是函数，拿 column 上下文
      <button onClick={column.getToggleSortingHandler()}>年龄</button>
    ),
  },
])

// 组件形式：全表渲染
function FlexTable() {
  const table = useTable({ data: people, columns, features })
  return (
    <table>
      <thead>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map((header) => (
              <th key={header.id} colSpan={header.colSpan}>
                {header.isPlaceholder ? null : <FlexRender header={header} />}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map((row) => (
          <tr key={row.id}>
            {row.getVisibleCells().map((cell) => (
              <td key={cell.id}>
                <FlexRender cell={cell} />
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

// 函数形式：headless 完全自定义；core 场景（无可见性特性）用 getAllCells
function FlexRenderFnTable() {
  const coreFeatures = tableFeatures({})
  const coreHelper = createColumnHelper<typeof coreFeatures, Person>()
  const coreColumns = coreHelper.columns([
    { accessorKey: 'name', header: '姓名', cell: (info) => info.getValue<string>() },
  ])
  const table = useTable({ data: people, columns: coreColumns, features: coreFeatures })
  return (
    <tbody>
      {table.getRowModel().rows.map((row) => (
        <tr key={row.id}>
          {row.getAllCells().map((cell) => (
            <td key={cell.id}>
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  )
}

// 实例便捷形态
function InstanceFlexTable() {
  const table = useTable({ data: people, columns, features })
  return (
    <tbody>
      {table.getRowModel().rows.map((row) => (
        <tr key={row.id}>
          {row.getVisibleCells().map((cell) => (
            <td key={cell.id}>
              <table.FlexRender cell={cell} />
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  )
}
```

## ⚠️ 常见陷阱

- ❌ 直接渲染 `{cell.getValue()}`：列定义里写的是 JSX/组件时不会被执行——凡自定义渲染一律过 `FlexRender`/`flexRender`
- ❌ `<FlexRender cell={cell} header={header} />` 同传：类型判别联合直接报错，一次只渲一个渲染位
- ❌ 表头漏 `header.isPlaceholder` 判断与 `colSpan`：分组表头错位、多余空 `<th>`
- ❌ core 场景调 `row.getVisibleCells()`：没有 `columnVisibilityFeature` 时该成员不存在，用 `row.getAllCells()`
- ❌ 以为 `FlexRender` 只能配 `createTableHook` 生成的表：顶层导入即可用于任何 `useTable` 实例
- ✅ 函数形式适合封装自定义 `<CellRenderer>`，组件形式/实例形式适合直接写表体

## 🔗 相关条目

- 📄 **[Table 核心 API](./02-table-core-api.md)** - useTable/columnHelper/feature 体系
- 📄 **[受控状态](./18-controlled-state.md)** - FlexRender 渲染的状态从哪来
- 📄 **[Table 基础教程](../../basics/04-table-fundamentals.md)** - 从零组装一张表的教程
- 📄 **[生态集成](../../frameworks/03-ecosystem-integration.md)** - 与 UI 库集成的渲染实践
- 📄 **[语法速查](../quick-references/01-syntax-cheatsheet.md)** - 一行式渲染签名

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
