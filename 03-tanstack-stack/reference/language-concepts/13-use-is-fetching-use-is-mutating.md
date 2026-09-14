# useIsFetching / useIsMutating / useMutationState：全局加载指示器

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

三个全局观测 Hook：`useIsFetching` / `useIsMutating` 订阅整个缓存/缓存变更区的**进行中数量**（返回数字），适合顶栏进度条、全局遮罩；`useMutationState` 返回符合条件的 mutation 实例数组，可 `select` 提取状态字段，适合"最近一次提交时间""失败列表"等观测面板。它们都是订阅——值变化即触发重渲染。

## 📖 语法 / 签名

```ts
useIsFetching(filters?: QueryFilters): number
useIsMutating(filters?: MutationFilters): number
useMutationState<TResult, TState = Mutation>(opts: {
  filters?: MutationFilters
  select?: (mutation: Mutation) => TState
}): TResult[]
```

| 筛选项 | 适用 | 说明 |
|--------|------|------|
| `queryKey` | QueryFilters | 前缀匹配（`exact: true` 精确） |
| `type: 'active' \| 'inactive' \| 'all'` | QueryFilters | active = 挂载中；默认 `'all'` |
| `predicate: (query) => boolean` | QueryFilters | 自定义过滤 |
| `mutationKey` | MutationFilters | 触发 mutation 时声明的 `mutationKey` |
| `status: 'idle' \| 'pending' \| 'success' \| 'error'` | MutationFilters | 按执行状态筛选 |

| 返回值 | 说明 |
|--------|------|
| `useIsFetching()` | 当前处于 fetching 的查询数量（含后台重取） |
| `useIsMutating()` | 当前 pending 的 mutation 数量 |
| `useMutationState(...)` | 命中的 mutation 数组；`select` 决定元素类型 |

## 💡 示例

```tsx
import {
  useIsFetching, useIsMutating, useMutationState, useMutation,
} from '@tanstack/react-query'

function GlobalIndicators() {
  const isFetching = useIsFetching()                    // 全部查询
  const todosFetching = useIsFetching({ queryKey: ['todos'] })
  const activeFetching = useIsFetching({ type: 'active' })
  const isMutating = useIsMutating()
  const addTodoMutating = useIsMutating({ mutationKey: ['add-todo'] })

  // 提取 pending mutation 的提交时间戳
  const pendingMutations = useMutationState({
    filters: { status: 'pending' },
    select: (mutation) => mutation.state.submittedAt,
  })

  if (isFetching > 0 || isMutating > 0) return <TopProgressBar />
  return null
}

// mutation 侧必须声明 mutationKey，才能被上面的 filters 命中
const mutation = useMutation({
  mutationKey: ['add-todo'],
  mutationFn: (title: string) => addTodo(title),
})
```

## ⚠️ 常见陷阱

- ❌ 用 `useIsFetching({ queryKey: ['todos'] })` 给单个按钮做 loading：单条查询请直接读 `query.isFetching`——全局 Hook 粒度太粗且多一层订阅
- ❌ 忘记这是订阅：放在渲染路径里意味着**任何**匹配的 fetch 状态翻转都会重渲染该组件，全局指示器应放在独立小组件里
- ❌ mutation 没声明 `mutationKey` 却用 `mutationKey` 过滤：永远命中 0 个
- ❌ 以为 `useIsFetching` 只算首次加载：后台重取、失效重取同样计入；要排除请用 `type: 'active'` 或按 key 过滤
- ✅ `useMutationState` 的 `select` 拿到的是 `Mutation` 实例，读 `mutation.state.variables` / `state.submittedAt` / `state.error` 做观测面板
- ✅ 全局回调（MutationCache `onSuccess` 等）适合"做副作用"，本条三个 Hook 适合"渲染 UI"

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - 单条查询的 `isFetching` 与 mutation 返回值
- 📄 **[QueryClient 配置](../framework-essentials/03-queryclient-config.md)** - 全局 MutationCache 回调
- 📄 **[Mutation 状态管理](../framework-essentials/05-mutation-state.md)** - mutation 状态机与缓存交互
- 📄 **[Query 进阶](../../frameworks/02-tanstack-query-advanced.md)** - 全局指示器的组合用法
- 📄 **[语法速查](../quick-references/01-syntax-cheatsheet.md)** - 一行式签名

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
