# useIsFetching / useIsMutating / useMutationState：全局加载指示器

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

三个全局观测 Hook：`useIsFetching` / `useIsMutating` 订阅整个缓存/缓存变更区的**进行中数量**（返回数字），适合顶栏进度条、全局遮罩；`useMutationState` 默认返回符合条件的 mutation state 数组，可 `select` 提取状态字段，适合"最近一次提交时间""失败列表"等观测面板。它们都是订阅——值变化即触发重渲染。

## 📖 语法 / 签名

```ts
// 库中导出的函数签名（QueryFilters/MutationFilters 由 @tanstack/react-query 导出）：
declare const useIsFetching: (filters?: QueryFilters) => number
declare const useIsMutating: (filters?: MutationFilters) => number
// 用法示意，不抄写或重新声明库的完整泛型签名
const pendingTimes = useMutationState({
  filters: { status: "pending" },
  select: mutation => mutation.state.submittedAt,
}) // 推断为 number[]；省略 select 时返回 state 数组
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
| `useMutationState(...)` | 命中的 mutation state 数组；`select` 决定元素类型 |

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
- ❌ 以为 `useIsFetching` 只算首次加载：后台重取、失效重取同样计入；`type: 'active'` 不能排除后台重取；应按业务条件或 predicate 判断
- ✅ `useMutationState` 的 `select` 拿到的是 `Mutation` 实例，读 `mutation.state.variables` / `state.submittedAt` / `state.error` 做观测面板
- ✅ 全局回调（MutationCache `onSuccess` 等）适合"做副作用"，本条三个 Hook 适合"渲染 UI"

<!-- full-library-explanation -->
## 数量指示器不会表达进度百分比

先修：query 与 mutation 状态。返回 2 表示匹配的两项工作正在执行，不表示完成 50%。后台同步通常适合轻量提示；若每次后台请求都遮罩整个页面，已有数据也会变得不可操作。

active/inactive 描述查询观察者是否活跃，与首次/后台请求是不同维度。若只想统计无数据的请求，可结合 predicate 检查状态和 data；若想给单个保存按钮反馈，直接读取该 mutation 的 isPending 更清楚。

这些 Hook 必须在组件或自定义 Hook 内调用，并位于对应 Provider 下。文中顶层 mutation 片段仅展示配置，实际应移动到事件组件的 Hook 调用位置。

**练习：** 首次加载后手动失效同一查询，观察 useIsFetching 两次都计数，而第二次仍有旧数据。验收：页面不因后台同步清空内容，失败提示与进度提示分别处理。

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - 单条查询的 `isFetching` 与 mutation 返回值
- 📄 **[QueryClient 配置](../framework-essentials/03-queryclient-config.md)** - 全局 MutationCache 回调
- 📄 **[Mutation 状态管理](../framework-essentials/05-mutation-state.md)** - mutation 状态机与缓存交互
- 📄 **[Query 进阶](../../frameworks/02-tanstack-query-advanced.md)** - 全局指示器的组合用法
- 📄 **[语法速查](../quick-references/01-syntax-cheatsheet.md)** - 一行式签名

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
