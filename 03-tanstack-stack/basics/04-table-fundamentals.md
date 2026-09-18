# Table 基础：列模型与数据行

## 先理解，再动手

表格的 data 是原始记录，列定义描述如何读值和渲染。排序、筛选和分页应明确是在当前数据上计算还是由服务端完成。

**本节自测**：用 5 行记录、每页 2 行，排序后翻页，预测三页内容。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

应得到 2、2、1 行；只排序当前页和全表排序后分页结果可能不同，要与产品需求一致。

</details>

> **文档简介**: 掌握 TanStack Table v9 的核心三角——data、columns、table 实例，学会用 ColumnDef 声明列、用 features 注册特性，并用 flexRender 渲染出一张完整表格
>
> **目标读者**: 已理解 Headless 理念，想动手渲染第一张 TanStack 表格的开发者
>
> **前置知识**: [Headless 设计哲学](./02-headless-philosophy.md)、React 列表渲染基础

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#TanStack-Table` `#ColumnDef` `#flexRender` `#Headless` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 `accessorKey` / `accessorFn` 声明列
- ✅ 用 `useTable` + `tableFeatures()` 渲染基础表格
- ✅ 用 `flexRender` 渲染自定义单元格
- ✅ 理解"行模型（Row Model）"是表格数据的流水线

---

## 🔍 核心三角

TanStack Table 一切围绕三个概念：

1. **data**：`TData[]`，你的原始数组（通常来自 Query）
2. **columns**：`ColumnDef` 数组，列的声明（怎么取值、怎么渲染表头/单元格；v9 泛型为 `ColumnDef<TFeatures, TData, TValue>`，推荐用 `createColumnHelper<TFeatures, TData>()` 保持泛型一致）
3. **table**：`useTable` 返回的实例，持有全部状态与行模型

**定义**: 列模型把"数据字段"与"渲染方式"解耦——`accessor` 负责取值，`cell` 负责渲染，二者互不干扰。

## 🛠️ 实践：渲染第一张表格

### 步骤一：声明数据与列

```tsx
import { useMemo } from 'react'
import {
  createColumnHelper,
  flexRender,
  tableFeatures,
  useTable,
} from '@tanstack/react-table'

type Person = {
  id: number
  firstName: string
  lastName: string
  age: number
  score: number
}

// v9：createColumnHelper 需要两个泛型——TFeatures 与 TData；核心特性会自动合并，无需显式注册
const features = tableFeatures({})
const columnHelper = createColumnHelper<typeof features, Person>()

const columns = useMemo(
  () =>
    columnHelper.columns([
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
    ]),
  [],
)
```

### 步骤二：创建 table 实例并渲染

```tsx
function PersonTable({ data }: { data: Person[] }) {
  // v9：features 是必填入口，核心特性（table/column/row/header/cell 与核心行模型行为）会自动合并进来，无需显式注册
  const table = useTable({
    data, // 建议用 useMemo 稳定引用，见下方"陷阱"
    columns,
    features, // 复用上方特性集；后续按需在此注册排序/筛选等特性
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
            {row.getAllCells().map((cell) => (
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

- v9 中 `features` 为**必填项**，核心特性（table/column/row/header/cell 与核心行模型行为）会自动合并进来，无需显式注册——它把 data + columns 管道化成可渲染的行；排序/筛选等其余特性按需注册到 `tableFeatures()`
- `header` / `cell` 既可以是字符串，也可以是返回 JSX 的函数，`flexRender` 统一处理两种形态
- `info.getValue()` 返回 `accessor` 的结果；`row.original` 可拿到整行原始数据

## 🚿 行模型流水线

行模型是 Table v9 的灵魂：数据像流水线一样被逐层加工。

```text
data → 核心行模型 → 排序 → 筛选 → 分组 → 展开树 → 分页 → table.getRowModel()
```

你按需"接通"管道（v9 中特性与行模型槽位都要注册到 `tableFeatures()` 上），不接的环节自动跳过：

```tsx
const table = useTable({
  data,
  columns,
  features: tableFeatures({
    rowSortingFeature,                          // 先注册特性（核心特性自动合并，无需显式注册）
    columnFilteringFeature,
    sortedRowModel: createSortedRowModel(),     // 再接通排序行模型
    filteredRowModel: createFilteredRowModel(), // 再接通筛选行模型
  }),
})
```

各环节的完整参数与 API 见 [Table 核心 API](../reference/language-concepts/02-table-core-api.md)。

## ✅ 最佳实践

表格先从 data 和 columns 建立行、列的含义，再由行模型应用排序、筛选与分页；如果直接遍历原始 data 渲染，就可能绕过这些处理，出现“按钮变了，行顺序没变”。改变排序后检查屏幕行序，是比“已注册功能”更直接的验收。

不要在每次渲染时无条件创建相同的派生数组，导致表格重复处理；可将固定列放到组件外，把昂贵派生计算按实际依赖记忆化。Query 对符合条件的数据会做结构共享，但不是所有 data 永远引用相同。列身份要稳定，无法从 accessor 或标题推导时显式设置 id；功能注册方式按本文对应 Table 版本核对，不能把某版本配置当通用 API。

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


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
