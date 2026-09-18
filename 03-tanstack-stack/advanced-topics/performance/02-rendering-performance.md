# 渲染性能：重渲染治理与列表虚拟化

> **文档简介**: 治理 Query 驱动的重渲染：理解 observer 的通知粒度、用 notifyOnChangeProps/select/虚拟化把渲染成本压到必要最小，并评估 React 19 Compiler 的影响。
>
> **目标读者**: 已消除冗余请求、继续优化交互流畅度的资深开发者
>
> **前置知识**: [查询性能优化](./01-query-optimization.md)、[Table 基础](../../basics/04-table-fundamentals.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#重渲染` `#虚拟化` `#react-compiler` `#web-vitals` |
| **更新日期** | 2026年9月 |

</details>

---

## 1. 重渲染从哪来

Query 组件重渲染的三个合法来源：

1. **observer 状态变化**：isPending → success、fetching 翻转、data 更新
2. **父组件重渲染**：与 Query 无关的常规 React 传播
3. **Context 变化**：QueryClientProvider 的 value 引用不稳定（错误配置才发生）

第 1 条里最隐蔽的是 **isFetching 噪音**：每次后台 refetch 开始/结束，读取了相关状态的 observer 才可能因此通知；默认属性追踪会过滤未使用字段——列表页每来一个新数据就闪一下，多半是它。

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
// select 结果经结构共享比较：仅就 data 投影而言，计数不变可避免由该值变化引起的通知；其他状态和父组件仍可能触发渲染
```

**结构共享（structural sharing）**：新响应与旧缓存逐引用比较，未变的节点保留旧引用——`memo` 化的子组件因此天然跳过。默认共享不会吞掉有变化的普通 JSON 数据；特殊非 JSON 结构才需评估自定义比较或关闭共享。

> v5 默认开启追踪属性（tracked properties）：未读取的字段变化不通知。显式 `notifyOnChangeProps` 是在其上进一步收窄，两者不冲突。

---

## 3. 大列表：Table + TanStack Virtual

没有通用的 200 行阈值；表格卡顿可能来自 DOM、单元格计算、行模型或更新频率。Headless 组合方案：

```bash
npm install @tanstack/react-virtual
```

```tsx
import { flexRender, tableFeatures, useTable } from '@tanstack/react-table'
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

const coreFeatures = tableFeatures({}) // v9：核心行模型自动内置，features 传空对象即可（无需 getCoreRowModel）

function BigTable({ rows, columns }: { rows: Row[]; columns: ColumnDef<typeof coreFeatures, Row>[] }) {
  const table = useTable({ data: rows, columns, features: coreFeatures })
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 44,      // 固定行高估算；动态行高需额外接入测量
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
              {row.getAllCells().map((cell) => (
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

**收益来源**：常驻 DOM 节点从 N 行降到视口 + overscan 行，可见 DOM 成本下降，但下载、内存、排序与筛选仍可能随总量增长，不能保证 10 万行与 100 行同速。

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

<!-- full-library-explanation -->
## 渲染次数、单次成本与 DOM 规模分别测量

先修：React Profiler、Table 行模型。减少一次极便宜的渲染未必比缩短一次昂贵计算更有价值。先录制一个具体动作，例如输入筛选词，查看耗时落在请求、派生计算、React 渲染还是浏览器布局。

默认 Query 属性追踪已经避免对未读取字段的变化通知。显式 notifyOnChangeProps 是替代自动判断的配置，不是永远更好的第二层过滤；漏掉 UI 使用的 error/isFetching 会造成显示过期。

虚拟化示例采用固定行高。多行文字导致真实高度变化时，要接入测量或维持固定尺寸；只写 estimateSize 不会神奇发现所有 DOM 高度。用 div 替代表格布局时还需补足语义、键盘与焦点行为。

**练习：** 先增加行数，再增加每个 cell 的计算成本，分别记录两种卡顿来源。验收：虚拟化降低 DOM 节点数，但不能声称消除了全量排序与下载成本；失败与空状态仍正确。

## 🔗 相关文档

- 📄 **[查询性能优化](./01-query-optimization.md)** - 请求侧优化（本文的前置）
- 📄 **[Table 核心 API](../../reference/language-concepts/02-table-core-api.md)** - 行模型与 cell 渲染字典
- 📄 **[缓存架构与数据流](../architecture/01-cache-architecture.md)** - observer 通知的内部机制
- 📄 **[数据看板](../../projects/02-data-dashboard.md)** - 表格性能问题的现场
- 📄 **[可观测性](../../deployment/03-observability.md)** - INP/CLS 的采集与告警


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
