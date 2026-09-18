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

- ❌ 以为占位能省请求：占位只是视觉层，键变化后请求照发——省请求靠 `staleTime` 与预取
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
