# 查询性能优化：请求成本与感知速度

> **文档简介**: 系统梳理 Query 的性能旋钮：staleTime 策略、预取时机、placeholderData 与 select——在不牺牲正确性的前提下降低请求数、提升感知速度。
>
> **目标读者**: 网络面板里请求满天飞、或用户抱怨"每次切页都转圈"的开发者
>
> **前置知识**: [缓存架构与数据流](../architecture/01-cache-architecture.md)、[Query 基础](../../frameworks/01-tanstack-query-basics.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#性能优化` `#staleTime` `#prefetch` `#placeholderdata` |
| **更新日期** | 2026年9月 |

</details>

---

## 1. 优化决策树

```
请求太多？
├─ 同一数据在多个页面重复请求 → staleTime 太小（§2）
├─ 每次挂载都重新请求 → 理解触发器（§2）
├─ 键里的参数变化频繁 → 防抖 / 参数收敛（§4）
└─ 列表页 → 详情页来回跳 → 路由级预取（§3）

感觉太慢？
├─ 进入页面白屏 → 非阻塞预取 + placeholderData（§3、§4）
├─ 翻页表格闪空白 → placeholderData（§4）
└─ 单行更新整表重取 → 乐观更新直写（§5）
```

---

## 2. staleTime：最大的一个杠杆

`staleTime: 0`（默认）表示数据立即可被视为过期；是否请求还取决于 enabled、缓存、在途去重和 refetchOnMount 等。按数据变化频率分配策略：

| 数据类型 | staleTime 建议 | 理由 |
|----------|----------------|------|
| 公开配置/稳定枚举（权限策略另行设计） | 30min ~ Infinity | 几乎不变 |
| 用户资料、看板结构 | 5~10min | 低频变化 |
| 业务列表（订单/用户） | 30s~2min | 中频变化 |
| 实时行情/协作文档 | 0 + 定向失效 | 靠失效与订阅，不靠 staleTime |

```ts
// 全局兜底 + 按查询覆盖
const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000 } },
})

useQuery({
  queryKey: ['enums', 'order-status'],
  queryFn: fetchOrderStatus,
  staleTime: Infinity, // 不会因时间自然过期；失效、回收后重新挂载等仍可能取数
})
```

**同时收敛触发器**：默认聚焦重取通常只针对过期数据；若业务连过期数据也不希望聚焦刷新，再考虑关闭 refetchOnWindowFocus。先调 staleTime，再动触发器。

---

## 3. 路由级预取：把等待移出视口

```tsx
// 悬停即预取（Router 配置 defaultPreload: 'intent' 后自动生效）
// loader 内对"次关键数据"做非阻塞预取：
export const Route = createFileRoute('/orders')({
  loader: ({ context }) => {
    void context.queryClient.prefetchQuery({
      queryKey: ['orders', 'stats'],
      queryFn: fetchOrderStats,
      staleTime: 60_000,
    })
    // 关键数据仍由组件内 useQuery 渲染骨架屏，不阻塞导航
  },
})
```

**策略矩阵**：

| 数据 | 是否 await | 时机 |
|------|-----------|------|
| 首屏必须的骨架数据 | 是（ensureQueryData） | loader |
| 折叠区/弹窗可能用到的数据 | 否（prefetchQuery） | loader 或 hover |
| 大而慢的报表 | 否 + staleTime 加大 | 进入应用后空闲时 |

---

## 4. placeholderData：占位数据策略

```ts
import { useQuery } from '@tanstack/react-query'

const { data, isPlaceholderData } = useQuery({
  queryKey: ['orders', { page }],
  queryFn: () => fetchOrders(page),
  placeholderData: (previousData) => previousData, // 函数式写法：新页数据到达前，继续展示旧页
})
```

- **placeholderData: (prev) => prev**：翻页/切筛选时沿用上一键数据，UI 不闪空白，配合 `isPlaceholderData` 做半透明过渡（v4 的 `keepPreviousData` 选项在 v5 已移除，统一用本写法或内置 `keepPreviousData` 帮助函数）
- **placeholderData: 常量/估算值**：用本地估算值先行渲染（如骨架计数）

**成本注意**：placeholder 只是视觉占位，请求照发。它优化的是**感知速度**，不是网络成本——两者别混淆。

---

## 5. select 与去重：让派生不触发多余工作

```ts
const { data: todoCount } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  select: (data) => data.filter((t) => !t.done).length, // 组件只订阅"数量"
})
```

`select` 的结果被结构共享比较：只有计算结果变化才重渲染。配合：

- **请求去重**：同键并发调用共享同一个 Promise（架构层免费赠送）
- **字段裁剪 vs select**：select 省的是渲染，不省网络/内存——大列表瘦身要在 queryFn 或服务端做
- **乐观更新替代 invalidate 抖动**：高频写场景用 [onMutate 直写](../../frameworks/02-tanstack-query-advanced.md)，把"等待服务端确认"从感知路径里移除

---

## 6. 验证优化的仪表

- Network 面板：优化前后同路径请求次数对比（目标：减少无用请求且维持所需新鲜度）
- TanStack Devtools：观察条目 fresh/stale 占比与 gcTime 后消失的时机
- Web Vitals：LCP/INP 变化（见 [可观测性](../../deployment/03-observability.md)）

**一次只动一个旋钮**：staleTime → 预取 → placeholderData 的顺序做完再测，避免归因混乱。

---

<!-- full-library-explanation -->
## 一次优化先定义正确性预算

先修：查询键、新鲜度、失效。商品介绍可以允许一分钟陈旧，库存与权限判定可能不能。前端 staleTime 只影响刷新策略，服务器仍要在下单或授权时检查最新事实。

先记录用户路径、请求数、等待时间与显示内容，再选择一个变化。预取可能减少点击后的等待，却增加未访问页面的请求；placeholder 可以减少空白，却暂时显示旧页。收益与成本应分别记录。

**练习：** 对列表→详情→返回列表路径做三轮测量：默认配置、延长 staleTime、增加详情预取。验收：解释每个请求为何发生，并测试写入后读到新结果。目标是删除无用工作，不能为了请求数为零牺牲新鲜度。

乐观更新还要验证失败回滚和并发写入顺序。用户看到即时结果只代表预测已显示，不代表服务器已经接受；失败时必须有可理解的反馈。

## 🔗 相关文档

- 📄 **[缓存架构与数据流](../architecture/01-cache-architecture.md)** - staleTime/gcTime 的内部语义
- 📄 **[缓存键、staleTime 与失效策略](../../reference/framework-essentials/01-query-essentials.md)** - 参数级速查表
- 📄 **[渲染性能](./02-rendering-performance.md)** - 请求优化之后的前端瓶颈
- 📄 **[数据看板](../../projects/02-data-dashboard.md)** - placeholderData 的完整应用
- 📄 **[协作看板](../../projects/03-collaborative-kanban.md)** - 乐观更新的高频写场景


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
