# Mutation 状态与副作用：useMutationState 与 MutationCache

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

useMutation 暴露调用处的观察状态，底层 mutation 保存在 MutationCache 中；当需要"跨组件聚合展示"（全局 toast、批量进度）或"统一副作用"（失败上报、成功埋点）时，用 `useMutationState`（组件内订阅全局 mutation 状态）和 `MutationCache` 全局回调（事件式钩子）。二者互补：前者是读取，后者是监听。

## 📖 语法 / 签名

```ts
import { MutationCache, useMutationState } from '@tanstack/react-query'

type CreateTodoVariables = { title: string }

// 组件内：按过滤条件订阅全局 mutation 状态
function PendingTodoMutations() {
  const pendingTodos = useMutationState({
    filters: {
      mutationKey: ['create-todo'], // 需在 useMutation 声明 mutationKey 才可定位
      status: 'pending',
    },
    // 只取展示待保存项所需字段，避免订阅整个 Mutation 对象。
    select: (mutation) => ({
      submittedAt: mutation.state.submittedAt,
      variables: mutation.state.variables as CreateTodoVariables,
    }),
  })

  return pendingTodos
}

// 全局：在 MutationCache 上挂事件回调
const mutationCache = new MutationCache({
  onMutate: () => {}, onSuccess: () => {}, onError: () => {}, onSettled: () => {},
  // 全局回调额外收到 mutation 等上下文，签名与 useMutation 并非完全相同；以安装版本类型为准
})
```

| API | 类型 | 说明 |
|-----|------|------|
| `useMutationState` | `(options) => TMutation[]` | 默认返回匹配的 mutation state 数组；select 可改变元素类型 |
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
- ❌ 在 `MutationCache` 回调里引用未定义的 `queryClient` 变量：回调拿不到组件作用域的变量——v5 的 MutationCache 回调在末位注入 `context`（`onSuccess`/`onError` 为第 5 参、`onSettled` 为第 6 参），`context.client` 即当前 client，或闭包引用模块作用域自己创建的 client
- ❌ 混淆 useMutation 配置回调与 mutate 调用时的附加回调：后者可能因卸载或观察者替换而不执行；跨页面业务一致性不能依赖临时 UI 回调
- ❌ `select` 未收窄导致全站 mutation 任一变化都重渲染：只 select 需要的字段
- ✅ 同一 mutation 高频并发时，用 `useMutationState` 聚合展示比在每个调用点各自管理 loading 更可控

<!-- full-library-explanation -->
## 同一个 mutationKey 不是同一次操作

先修：useMutation 与回调。两次点击可以创建两次 mutation，即使键相同，也不会像 query 一样自动合并为一次请求。因此 useMutationState 返回数组，需要用 submittedAt 或业务操作 ID 区分。

useMutation 的观察结果聚焦当前调用状态；底层操作存在 MutationCache 中。未传 select 时 useMutationState 返回匹配操作的 state，传 select 后返回选中的值，而不是默认返回 Mutation 实例本身。

全局回调适合统一日志，但不应无差别把内部异常原文弹给用户。useMutation 配置中的生命周期回调与 mutate 调用时传入的附加回调也不同：后者依赖观察者，卸载或连续调用时行为不同，不能统一断言全部回调都会丢失。

**练习：** 连续提交两条不同标题，延迟第二条，让一条成功、一条失败。验收：全局状态能区分两项，失败提示不会覆盖成功结果；重复提交仍由业务幂等处理。参考[mutation 回调语义](https://tanstack.com/query/latest/docs/framework/react/guides/mutations)。

## 🔗 相关条目

- 📄 **[乐观更新](../language-concepts/06-optimistic-update.md)** - onMutate 四步模式（组件内写路径）
- 📄 **[QueryClient 全局配置](./03-queryclient-config.md)** - MutationCache 的挂载位置
- 📄 **[Query 核心 API](../language-concepts/01-query-core-api.md)** - useMutation 返回值与回调签名
- 📄 **[Mutation 状态背景](./01-query-essentials.md)** - 缓存与副作用全景

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
