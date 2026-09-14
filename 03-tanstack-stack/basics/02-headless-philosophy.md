# Headless 设计哲学

> **文档简介**: 理解 Headless（无头）设计的核心思想——状态与逻辑与渲染彻底分离，这是贯穿整个 TanStack 生态的统一设计语言
>
> **目标读者**: 用过 Ant Design / MUI 等组件库，想理解 TanStack 为何"不带 UI"的开发者
>
> **前置知识**: [环境搭建](./01-environment-setup.md)已完成，了解 React 组件渲染模型

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#Headless` `#设计哲学` `#架构思维` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用一句话说清 Headless 与组件库的本质区别
- ✅ 判断一个需求适合 Headless 库还是现成组件
- ✅ 说出 TanStack 全家桶各库的分工
- ✅ 理解"逻辑层可测试、渲染层可定制"的收益与代价

---

## 🔍 什么是 Headless

**定义**: Headless 库只提供**状态、逻辑与无障碍行为**，不提供任何 DOM 结构与样式。你拿到的是"引擎"，而不是"整车"。

TanStack Table 给你排序、筛选、分页、行选择的全部状态机，但 `<table>` 标签长什么样、用什么 CSS 框架，完全由你决定。

**核心公式**：

```text
Headless 库 = 状态机 + 行为逻辑 + 类型安全
UI 定制     = 你的 JSX + 你的样式方案（Tailwind / CSS Modules / 任意设计系统）
```

## ⚖️ Headless vs 组件库

同样是"带排序的表格"，两种哲学的实现对比：

```tsx
// 写法 A：组件库（以 Ant Design 为例）
// 一行搞定，但表格外观被锁定在组件库设计体系内
<Table<Person>
  dataSource={data}
  columns={antdColumns}
  onChange={(pagination, filters, sorter) => { /* 受控回调 */ }}
/>
```

```tsx
// 写法 B：Headless（TanStack Table v9）
// 状态逻辑全部就绪，DOM 结构完全自主
const features = tableFeatures({
  rowSortingFeature,                        // 排序特性（逻辑层）
  columnVisibilityFeature,                  // 可见性特性：row.getVisibleCells() 需注册本特性
  sortedRowModel: createSortedRowModel(),   // 排序逻辑，不是 UI
})
const table = useTable({ data, columns, features })

// 渲染层完全由你掌控——可以是 <table>，也可以是 <div> 网格
<table className="w-full border-collapse">
  <thead>
    {table.getHeaderGroups().map((hg) => (
      <tr key={hg.id}>
        {hg.headers.map((header) => (
          <th key={header.id} onClick={header.column.getToggleSortingHandler()}>
            {flexRender(header.column.columnDef.header, header.getContext())}
            {{ asc: ' ↑', desc: ' ↓' }[header.column.getIsSorted() as string] ?? ''}
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
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </td>
        ))}
      </tr>
    ))}
  </tbody>
</table>
```

**如何选择**：

| 场景 | 更适合 | 原因 |
|------|--------|------|
| 中后台标准表单、表格，赶工期 | 组件库 | 开箱即用，风格统一 |
| 设计系统自定义强、要求像素级还原 | Headless | 渲染层零锁定 |
| 需要非标准形态（虚拟滚动表格、看板） | Headless | 组件库改造成本高于自建 |
| 团队 UI 水平参差 | 组件库 | Headless 把质量责任交还给使用者 |

## 🧩 TanStack 家族一览

| 库 | 版本 | 职责 | Headless 体现在 |
|----|------|------|----------------|
| Query | v5 | 服务端状态：缓存/失效/重试/乐观更新 | 与请求库、UI 框架解耦 |
| Table | v9 | 表格状态机：排序/筛选/分组/分页 | 无任何表格 DOM |
| Router | v1 | 类型安全文件路由 | 内置方案不绑定 UI，导航与布局自定 |
| Form | v1 | 表单状态与校验 | 字段渲染完全自主 |
| Start | v1 | 基于 Router + Query 的全栈 SSR 框架 | 渲染层可配 |
| Virtual / Ranger / Store 等 | — | 虚拟滚动 / 滑块 / 全局状态 | 同样零 UI |

## 💡 为什么 TanStack 选择"无 UI"

- **关注点分离**：数据逻辑与视觉呈现的变化频率不同，分开演化互不拖累
- **样式方案自由**：Tailwind、shadcn/ui、自研设计系统都能无缝接入
- **逻辑可测试**：`useTable`、`QueryClient` 都是纯 JS 对象，可用 Vitest 单测状态机而无需渲染
- **升级独立**：UI 重构不必连带重写业务逻辑；TanStack 升级也不污染你的视觉层

**代价也要清楚**：

- ❌ 你要自己写全部 JSX 与样式，首屏产出比组件库慢
- ❌ 无障碍行为（键盘导航、ARIA）需要自己补齐或搭配 Radix UI 等方案

---

## 🎯 练习与实践

### 练习一：概念内化

- [ ] 用自己的话写 3 句话总结 Headless 哲学（不看上文）
- [ ] 在团队近期项目中找出 2 个"组件库改样式改到痛苦"的场景，判断是否适合 Headless 重写

### 练习二：对比体验

- [ ] 跑通 [环境搭建](./01-environment-setup.md) 中的排序表格代码，给 `<th>` 换成 Tailwind 类名
- [ ] 把同一个 `table` 实例的渲染改成 `<div>` 网格布局，验证"渲染层与逻辑层无关"

---

## 🔗 相关文档

- 📄 **[Query 基础](./03-query-fundamentals.md)** - 下一篇：进入 Query 的状态与缓存
- 📄 **[Table 核心 API](../reference/language-concepts/02-table-core-api.md)** - 本文中表格 API 的完整字典
- 📄 **[TypeScript 模式](../reference/language-concepts/05-typescript-patterns.md)** - Headless 库的类型设计模式

---

**最后更新**: 2026年9月 | Dev Quest · 03-tanstack-stack
