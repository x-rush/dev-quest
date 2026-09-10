# Table 基础：列模型与数据行

> **文档简介**: 掌握 TanStack Table v8 的核心三角——data、columns、table 实例，学会用 ColumnDef 声明列并用 flexRender 渲染出一张完整表格
>
> **目标读者**: 已理解 Headless 理念，想动手渲染第一张 TanStack 表格的开发者
>
> **前置知识**: [Headless 设计哲学](./02-headless-philosophy.md)、React 列表渲染基础

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#TanStack-Table` `#ColumnDef` `#flexRender` `#Headless` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 `accessorKey` / `accessorFn` 声明列
- ✅ 用 `useReactTable` + `getCoreRowModel()` 渲染基础表格
- ✅ 用 `flexRender` 渲染自定义单元格
- ✅ 理解"行模型（Row Model）"是表格数据的流水线

---

## 🔍 核心三角

TanStack Table 一切围绕三个概念：

1. **data**：`TData[]`，你的原始数组（通常来自 Query）
2. **columns**：`ColumnDef<TData>[]`，列的声明（怎么取值、怎么渲染表头/单元格）
3. **table**：`useReactTable` 返回的实例，持有全部状态与行模型

**定义**: 列模型把"数据字段"与"渲染方式"解耦——`accessor` 负责取值，`cell` 负责渲染，二者互不干扰。

## 🛠️ 实践：渲染第一张表格

### 步骤一：声明数据与列

```tsx
import { useMemo } from 'react'
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table'

type Person = {
  id: number
  firstName: string
  lastName: string
  age: number
  score: number
}

const columns = useMemo<ColumnDef<Person>[]>(
  () => [
    // 简单取值：accessorKey 直接读字段
    { accessorKey: 'firstName', header: '名' },
    { accessorKey: 'lastName', header: '姓' },
    { accessorKey: 'age', header: '年龄' },
    // 自定义取值：accessorFn 派生数据 + 自定义渲染
    {
      id: 'fullName',
      accessorFn: (row) => `${row.lastName}${row.firstName}`,
      header: '全名',
      cell: (info) => <strong>{info.getValue<string>()}</strong>,
    },
    {
      accessorKey: 'score',
      header: '评分',
      cell: (info) => {
        const score = info.getValue<number>()
        return <span>{score >= 60 ? `✅ ${score}` : `❌ ${score}`}</span>
      },
    },
  ],
  [],
)
```

### 步骤二：创建 table 实例并渲染

```tsx
function PersonTable({ data }: { data: Person[] }) {
  const table = useReactTable({
    data, // 建议用 useMemo 稳定引用，见下方"陷阱"
    columns,
    getCoreRowModel: getCoreRowModel(), // 必填：核心行模型
  })

  return (
    <table className="w-full border-collapse text-sm">
      <thead>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map((header) => (
              <th key={header.id} className="border-b px-3 py-2 text-left">
                {/* flexRender 会同时处理纯文本与 JSX 两种 header */}
                {header.isPlaceholder
                  ? null
                  : flexRender(header.column.columnDef.header, header.getContext())}
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
  )
}
```

**关键点解析**：

- `getCoreRowModel()` 是**必须传入**的行模型——它把 data + columns 管道化成可渲染的行
- `header` / `cell` 既可以是字符串，也可以是返回 JSX 的函数，`flexRender` 统一处理两种形态
- `info.getValue()` 返回 `accessor` 的结果；`row.original` 可拿到整行原始数据

## 🚿 行模型流水线

行模型是 Table v8 的灵魂：数据像流水线一样被逐层加工。

```text
data → 核心行模型 → 排序 → 筛选 → 分组 → 展开树 → 分页 → table.getRowModel()
```

你按需"接通"管道，不接的环节自动跳过：

```tsx
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),     // 接通排序
  getFilteredRowModel: getFilteredRowModel(), // 接通筛选
})
```

各环节的完整参数与 API 见 [Table 核心 API](../reference/language-concepts/02-table-core-api.md)。

## ✅ 最佳实践

- ✅ **columns 定义在组件外或 useMemo 中**，避免每次渲染生成新引用
- ✅ **data 引用要稳定**：来自 `useQuery` 的 `data` 天然稳定，本地拼接需 `useMemo`
- ✅ **派生列必须给 `id`**：没有 `accessorKey` 时 id 是唯一标识
- ❌ **避免** 忘传 `getCoreRowModel()`——表格会静默渲染空白
- ❌ **避免** 手动遍历 `data` 渲染行——一切渲染都应经过 `table.getRowModel()`

---

## 🎯 练习与实践

### 练习一：基础渲染

- [ ] 用 jsonplaceholder 的 `/users` 接口作为 data，渲染姓名/邮箱/公司三列
- [ ] 给"邮箱"列加 `cell` 自定义渲染，用 `<a>` 链接展示

### 练习二：接入 Query

- [ ] 用 `useQuery` 取数并渲染表格，完整跑通"Query → Table"链路
- [ ] 加载中时渲染骨架占位行（提示：判断 `isPending`）

---

## 🔗 相关文档

- 📄 **[Router 基础](./05-router-fundamentals.md)** - 下一篇：类型安全路由
- 📄 **[Table 核心 API](../reference/language-concepts/02-table-core-api.md)** - ColumnDef 与行模型完整字典
- 📄 **[TypeScript 模式](../reference/language-concepts/05-typescript-patterns.md)** - ColumnDef 泛型推断技巧

---

**最后更新**: 2026年9月 | Dev Quest · 03-tanstack-stack
