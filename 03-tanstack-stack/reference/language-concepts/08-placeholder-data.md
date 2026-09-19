# 占位数据：placeholderData 与 isPlaceholderData

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

`placeholderData` 是查询的真实数据到达前用于渲染的"占位值"。v5 使用函数式写法 `placeholderData: (previousData) => previousData` 来实现"键变化时沿用上一键数据"（v4 的 `keepPreviousData` 选项已移除，v5 另内置同名帮助函数 `keepPreviousData`）。它优化的是**感知速度**而非网络成本，配合 `isPlaceholderData` 标志可做半透明过渡等视觉暗示。

## 📖 语法 / 签名

```ts
type PlaceholderData<TData> =
  | TData
  | ((previousData: TData | undefined, previousQuery: unknown) => TData | undefined);

const placeholderData: PlaceholderData<unknown> = (previousData) => previousData;
useQuery({
  queryKey,
  queryFn,
  placeholderData, // 静态值或函数；占位值不会写入查询缓存
})
// 返回值额外提供：
// isPlaceholderData: boolean —— 当前展示的 data 是占位值而非真实缓存
```

| 参数/属性 | 类型 | 说明 |
|-----------|------|------|
| `previousData` | `TData \| undefined` | 上一条成功查询的数据；首查时为 `undefined` |
| `isPlaceholderData` | `boolean` | 渲染分支与透明度动画的判断依据 |

## 💡 示例

```tsx
const { data, isPlaceholderData } = useQuery({
  queryKey: ['users', 'list', { page }],
  queryFn: () => fetchUsers(page),
  // v5：新页数据到达前继续展示旧页，表格不清空
  placeholderData: (previousData) => previousData,
})

return (
  <div style={{ opacity: isPlaceholderData ? 0.6 : 1, transition: 'opacity 150ms' }}>
    <UserTable data={data?.rows ?? []} />
  </div>
)
```

## ⚠️ 常见陷阱

- ❌ 以为占位能省请求：占位本身不减少请求；复用新鲜缓存需要合理的 `staleTime`，预取主要把请求提前，并不保证总请求数减少
- ❌ 继续使用 `keepPreviousData: true` 选项：v4 的该选项在 v5 已移除——改用函数式写法，或用 v5 内置的同名帮助函数（`import { keepPreviousData }` 后写 `placeholderData: keepPreviousData`）
- ❌ 混淆 `placeholderData` 与 `initialData`：`initialData` 会写入真实缓存；是否新鲜取决于 staleTime 与 initialDataUpdatedAt，只想要"占位不标鲜"就用 `placeholderData`
- ❌ updater 类占位函数返回 `undefined`：等价于不设占位；返回值需满足 `TData | undefined` 类型（v5 类型要求）
- ✅ 翻页表格可选择沿用旧数据并提示过渡；跨账号或语义变化很大的筛选应避免误展示旧内容

<!-- full-library-explanation -->
## 占位不等于缓存中的事实

先修：queryKey 与查询状态。页码从 1 变到 2 时，如果页 2 尚未缓存，旧页内容可以暂时留在当前观察者中；这不意味着页 2 已获取成功，也不把旧页写成页 2 的真实缓存。

如果新筛选代表完全不同的账号或资源，继续展示旧内容可能误导用户，应明确提示或选择清空。占位期间禁用依赖当前页真实结果的“下一页”判断和批量操作，避免用旧页 ID 执行新页操作。

initialData 写入查询缓存，适合已有可信数据；默认 staleTime 为 0 时它仍可立即被视为过期。可用 initialDataUpdatedAt 传入真实更新时间，不能把恢复的旧数据一律当成刚获取。

**练习：** 将页 2 响应延迟，打印 queryKey、isPlaceholderData、dataUpdatedAt，观察占位与真实结果切换。验收：能解释为何 UI 有内容但缓存检查中页 2 还没有真实数据，并处理页 2 请求失败。

**自测：** 占位会减少 HTTP 请求吗？它本身不会。initialData 默认永远新鲜吗？不会。参考[占位数据](https://tanstack.com/query/latest/docs/framework/react/guides/placeholder-query-data)。

## 实作：给分页结果标明真实来源

前置：已有 React 工程及 Query v5 Provider，能写 `useState` 与异步函数。产物是两页项目列表，必须同时显示“请求页码”和响应中的 `page`；这样旧页暂留不会被误认为新页结果。

练习接口约定：`fetchPage(page)` 返回 `Promise<{ page: number; rows: { id: string; title: string }[]; hasMore: boolean }>`。第 1 页立即返回两条数据、`hasMore: true`；第 2 页延迟 1500ms 返回另一组 ID、`hasMore: false`。它是本地模拟函数，随后才替换为真实 fetch，并检查 `response.ok`。下面配置放在组件内部，`page` 初始为 1。

```tsx
const result = useQuery({
  queryKey: ['page-lab', page],
  queryFn: () => fetchPage(page),
  placeholderData: keepPreviousData,
  retry: false, // 练习时让失败直接显现
})
// 从 @tanstack/react-query 导入 useQuery、keepPreviousData。
// fetchPage 采用上述接口；此片段不包含 Provider 与模拟函数实现。
```

渲染先处理 `isPending` 和 `isError`，成功分支显示 `result.data.page` 与 rows；`isPlaceholderData` 为 true 时明确标注“正在读取新页，当前为旧页预览”。只有真实结果允许“下一页”：按钮禁用条件为 `result.isPlaceholderData || !result.data.hasMore`，并保留“上一页”恢复入口。不要依靠半透明颜色作为唯一提示。分页控制依据见[官方分页示例](https://tanstack.com/query/latest/docs/framework/react/guides/paginated-queries)。

| 操作 | 预期观察 | 不符合时回查 |
|---|---|---|
| 首次进入 | 无 previousData，先等待，再显示响应 page=1 | 是否已有同键缓存或配置了 initialData |
| 从 1 翻到 2 | 请求页=2，响应页暂为1，isPlaceholderData=true | 是否重新挂载整个查询组件；是否返回 previousData |
| 第 2 页成功 | 响应页变2，占位标志为false，下一页禁用 | queryFn 是否使用当前 page；key 是否含页码 |
| 清空练习缓存后，让第2页抛错 | 显示错误且仍能返回第1页 | 错误是否被吞成空数组；是否遗漏错误分支 |

占位生效时观察者可处于 success，所以 `isSuccess` 不足以证明新页已到达。可用 `queryClient.getQueryData(['page-lab', 2])` 与当前界面比较：首次第2页的占位值不写入该键缓存。上述失败场景与“已有真实缓存后后台刷新失败”需分别验证，不能假定所有错误都会保留上一页占位。

通过此练习后再接表格选择功能：翻页时清除选择，或按实际记录 ID 管理选择，避免对旧页预览执行批量修改。继续阅读 [无限查询](./07-infinite-query.md) 时注意其产物是追加 pages，并非替换当前页。本轮只完成官方资料与静态审阅，未运行 React、分页接口或浏览器验收。

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - useQuery 全参数字典
- 📄 **[无限查询](./07-infinite-query.md)** - 追加页场景的组合使用
- 📄 **[查询性能优化](../../advanced-topics/performance/01-query-optimization.md)** - 占位数据的成本账
- 📄 **[数据看板项目](../../projects/02-data-dashboard.md)** - 服务端分页表格的完整应用
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)** - gcTime/占位相关的闪现排查

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
