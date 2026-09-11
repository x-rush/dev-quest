# Mutation 状态与副作用：useMutationState 与 MutationCache

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

mutation 的状态默认只存在于调用它的组件里；当需要"跨组件聚合展示"（全局 toast、批量进度）或"统一副作用"（失败上报、成功埋点）时，用 `useMutationState`（组件内订阅全局 mutation 状态）和 `MutationCache` 全局回调（事件式钩子）。二者互补：前者是读取，后者是监听。

## 📖 语法 / 签名

```ts
// 组件内：按过滤条件订阅全局 mutation 状态
useMutationState({
  filters: {
    mutationKey?: ['create-todo'],       // 需在 useMutation 声明 mutationKey 才可定位
    status?: 'pending' | 'success' | 'error',
    predicate?: (mutation) => boolean,   // 自定义筛选
  },
  select?: (mutation) => T,              // 只取需要的字段，缩小重渲染面
})

// 全局：在 MutationCache 上挂事件回调
new MutationCache({
  onMutate, onSuccess, onError, onSettled,
  // 签名与 useMutation 同名回调一致，但作用于全站所有 mutation
})
```

| API | 类型 | 说明 |
|-----|------|------|
| `useMutationState` | `(options) => TMutation[]` | 返回匹配的 mutation 对象数组（含 `state`） |
| `filters.status` | `MutationStatus` | 最常用：订阅所有"进行中"或"最近失败" |
| `mutation.state.variables` | `TVariables` | 触发时的入参，用于重放/提示文案 |
| `MutationCache.onError` | `(error, vars, context, mutation) => void` | 全站失败统一上报 |

## 💡 示例

```tsx
// ① 全局 toast：任何 mutation 失败都提示（入口处挂一次）
const mutationCache = new MutationCache({
  onError: (error, _vars, _ctx, mutation) => {
    toast.error(`${mutation.options.mutationKey?.[0] ?? '操作'}失败：${error.message}`)
  },
})

// ② 组件内：展示"还有几条保存中"
function SavingIndicator() {
  const saving = useMutationState({
    filters: { status: 'pending' },
    select: (m) => m.state.variables as { title: string },
  })
  if (saving.length === 0) return null
  return <span>正在保存 {saving.length} 项…</span>
}
```

## ⚠️ 常见陷阱

- ❌ 用 `filters.mutationKey` 却从未声明 `mutationKey`：永远匹配不到——想被全局筛选的 mutation 必须显式声明键
- ❌ 在 `MutationCache` 回调里引用未定义的 `queryClient` 变量：回调拿不到组件作用域的变量——v5 的 mutation 回调 context 与 MutationCache 回调入参都注入了 client（`context.client` / `mutation.client`），或闭包引用模块作用域自己创建的 client
- ❌ 依赖"组件卸载后回调仍会执行"：`useMutation` 的回调做不到；跨生命周期的副作用交给 `MutationCache` 全局回调或 `mutateAsync`
- ❌ `select` 未收窄导致全站 mutation 任一变化都重渲染：只 select 需要的字段
- ✅ 同一 mutation 高频并发时，用 `useMutationState` 聚合展示比在每个调用点各自管理 loading 更可控

## 🔗 相关条目

- 📄 **[乐观更新](../language-concepts/06-optimistic-update.md)** - onMutate 四步模式（组件内写路径）
- 📄 **[QueryClient 全局配置](./03-queryclient-config.md)** - MutationCache 的挂载位置
- 📄 **[Query 核心 API](../language-concepts/01-query-core-api.md)** - useMutation 返回值与回调签名
- 📄 **[Mutation 状态背景](./01-query-essentials.md)** - 缓存与副作用全景

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
