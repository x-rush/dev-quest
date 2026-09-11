# 渲染性能：重渲染治理与列表虚拟化

> **文档简介**: 治理 Query 驱动的重渲染：理解 observer 的通知粒度、用 notifyOnChangeProps/select/虚拟化把渲染成本压到必要最小，并评估 React 19 Compiler 的影响。
>
> **目标读者**: 已消除冗余请求、继续优化交互流畅度的资深开发者
>
> **前置知识**: [查询性能优化](./01-query-optimization.md)、[Table 基础](../../basics/04-table-fundamentals.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#重渲染` `#虚拟化` `#react-compiler` `#web-vitals` |
| **更新日期** | 2026年9月 |

---

## 1. 重渲染从哪来

Query 组件重渲染的三个合法来源：

1. **observer 状态变化**：isPending → success、fetching 翻转、data 更新
2. **父组件重渲染**：与 Query 无关的常规 React 传播
3. **Context 变化**：QueryClientProvider 的 value 引用不稳定（错误配置才发生）

第 1 条里最隐蔽的是 **isFetching 噪音**：每次后台 refetch 开始/结束，未做裁剪的 observer 都会通知渲染——列表页每来一个新数据就闪一下，多半是它。

---

## 2. 收窄通知：notifyOnChangeProps 与 select

```tsx
// 方式 A：只订阅关心的字段，isFetching 翻转不再触发渲染
const { data } = useQuery({
  queryKey: ['orders', { page }],
  queryFn: fetchOrders,
  notifyOnChangeProps: ['data', 'isPending', 'isError'],
})

// 方式 B（更优）：select 让组件只订阅"派生结果"
const activeCount = useQuery({
  queryKey: ['orders'],
  queryFn: fetchOrders,
  select: (orders) => orders.filter((o) => o.active).length,
})
// select 结果经结构共享比较：计数不变 → 0 次渲染
```

**结构共享（structural sharing）**：新响应与旧缓存逐引用比较，未变的节点保留旧引用——`memo` 化的子组件因此天然跳过。数据敏感场景（如测量类实时数据）可显式 `structuralSharing: false` 换取确定性。

> v5 默认开启追踪属性（tracked properties）：未读取的字段变化不通知。显式 `notifyOnChangeProps` 是在其上进一步收窄，两者不冲突。

---

## 3. 大列表：Table + TanStack Virtual

200 行以上表格的卡顿不是 Query 的问题，是 DOM 的问题。Headless 组合方案：

```bash
npm install @tanstack/react-virtual
```

```tsx
import { flexRender, tableFeatures, useTable } from '@tanstack/react-table'
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

function BigTable({ rows, columns }: { rows: Row[]; columns: ColumnDef<Row>[] }) {
  // v9：核心行模型自动内置，features 传空对象即可（无需 getCoreRowModel）
  const table = useTable({ data: rows, columns, features: tableFeatures({}) })
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 44,      // 预估行高，滚动中自动校正
    overscan: 8,                 // 视口外缓冲行数
  })

  return (
    <div ref={parentRef} style={{ height: 600, overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map((vi) => {
          const row = table.getRowModel().rows[vi.index]
          return (
            <div
              key={row.id}
              style={{
                position: 'absolute',
                top: 0,
                transform: `translateY(${vi.start}px)`,
                height: vi.size,
                display: 'flex',
              }}
            >
              {row.getVisibleCells().map((cell) => (
                <div key={cell.id} style={{ width: 160 }}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </div>
              ))}
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

**收益来源**：常驻 DOM 节点从 N 行降到视口 + overscan 行，渲染与布局成本与数据总量解耦——10 万行与 100 行同速。

---

## 4. React 19 与 Compiler 的影响

- **React Compiler**：自动 memo 化组件与 JSX，父子传播型重渲染大幅减少；Query 的 observer 通知不依赖 memo，两者叠加效果有限但无害
- **useTransition 包裹重列表更新**：筛选输入触发的表格重算放进 transition，输入框保持即时响应
- **useOptimistic**：React 19 的乐观 UI 原语适用于"表单提交型"乐观更新；拖拽/批量型场景 Query 的 onMutate 直写缓存仍更顺手——不冲突，按场景选

**决策参考**：Compiler 自动化的部分不要手工 memo 重复做；Observer 通知粒度（§2）Compiler 管不了，仍需手动治理。

---

## 5. 度量闭环

| 工具 | 看什么 |
|------|--------|
| React DevTools Profiler | 单次交互的渲染次数/耗时火焰图，定位"谁在多余渲染" |
| Chrome Performance 面板 | 长任务（>50ms）与布局抖动 |
| Web Vitals（INP/CLS） | 真实用户视角的流畅度（见 [可观测性](../../deployment/03-observability.md)） |
| TanStack Devtools | 渲染频繁时核对是否 isFetching 噪音 |

**治理顺序**：先裁通知（§2，成本最低）→ 再虚拟化（§3，针对列表）→ 最后 Compiler/transition（§4，锦上添花）。

---

## 🔗 相关文档

- 📄 **[查询性能优化](./01-query-optimization.md)** - 请求侧优化（本文的前置）
- 📄 **[Table 核心 API](../../reference/language-concepts/02-table-core-api.md)** - 行模型与 cell 渲染字典
- 📄 **[缓存架构与数据流](../architecture/01-cache-architecture.md)** - observer 通知的内部机制
- 📄 **[数据看板](../../projects/02-data-dashboard.md)** - 表格性能问题的现场
- 📄 **[可观测性](../../deployment/03-observability.md)** - INP/CLS 的采集与告警
