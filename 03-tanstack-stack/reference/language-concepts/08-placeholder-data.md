# 占位数据：placeholderData 与 isPlaceholderData

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

`placeholderData` 是查询的真实数据到达前用于渲染的"占位值"。v5 统一采用函数式写法 `placeholderData: (previousData) => previousData` 来实现"键变化时沿用上一键数据"（v4 的 `keepPreviousData` 选项已移除，v5 另内置同名帮助函数 `keepPreviousData`）。它优化的是**感知速度**而非网络成本，配合 `isPlaceholderData` 标志可做半透明过渡等视觉暗示。

## 📖 语法 / 签名

```ts
useQuery({
  queryKey,
  queryFn,
  placeholderData:
    | TData                                  // 静态占位值（会绕过结构共享）
    | ((previousData: TData | undefined, previousQuery) => TData | undefined),
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
- ❌ 混淆 `placeholderData` 与 `initialData`：`initialData` 会把数据视为真实新鲜数据并重置 staleTime 计时，只想要"占位不标鲜"就用 `placeholderData`
- ❌ updater 类占位函数返回 `undefined`：等价于不设占位；返回值需满足 `TData | undefined` 类型（v5 类型要求）
- ✅ 翻页/筛选型表格"必配"函数式占位 + `isPlaceholderData` 降透明度，是消除表格闪烁的标准组合

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - useQuery 全参数字典
- 📄 **[无限查询](./07-infinite-query.md)** - 追加页场景的组合使用
- 📄 **[查询性能优化](../../advanced-topics/performance/01-query-optimization.md)** - 占位数据的成本账
- 📄 **[数据看板项目](../../projects/02-data-dashboard.md)** - 服务端分页表格的完整应用
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)** - gcTime/占位相关的闪现排查

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
