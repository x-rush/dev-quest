# useQueries：并行与动态查询列表

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

`useQueries` 在**一个 Hook 调用**里声明任意数量的查询：静态多查询（页面顶部同时拉用户、配置、公告）与动态多查询（列表长度随数据变化的 `ids.map(...)`）都适用。它解决两个问题——Hooks 规则禁止在循环里调 `useQuery`；多个独立 `useQuery` 的加载状态需要手动拼装，而 `combine` 选项能把结果聚合为一个对象、只在聚合结果变化时触发一次重渲染。

## 📖 语法 / 签名

```ts
const results = useQueries({
  queries: [ /* 每个条目与 useQuery 选项一致，queryKey/queryFn 必填 */ ],
  combine?: (results: UseQueryResult[]) => TCombined, // 聚合为单一对象，减少重渲染
})
```

| 形态 | 说明 |
|------|------|
| 静态列表 | 数组字面量直接写多个查询条目 |
| 动态列表 | `ids.map((id) => ({ queryKey: ['todo', id], queryFn: ... }))`，条目数随数据变化 |
| 不传 `combine` | 返回 `UseQueryResult[]`，**顺序与 `queries` 一一对应**，按下标取用 |
| 传 `combine` | 返回值变为聚合结果，`combine` 内可安全索引/合并 |

| 陷阱位 | 事实 |
|--------|------|
| 条目内 `placeholderData`（含 `keepPreviousData`） | `keepPreviousData` 本质就是 `(prev) => prev`，但换 key 时**同样收不到旧数据，是空操作**（与单条 `useQuery` 不同）：QueriesObserver 按 `queryHash` 匹配，新 key 必定新建 Observer，prev 恒传 `undefined`。平滑过渡需自行从缓存取（`queryClient.getQueryData`）或保留旧 key 条目 |

## 💡 示例

```tsx
import { useQueries } from '@tanstack/react-query'

// 静态列表 + combine 聚合
function ProfileCard() {
  const combined = useQueries({
    queries: [
      { queryKey: ['user', 1], queryFn: () => fetchUser(1) },
      {
        queryKey: ['todos'],
        queryFn: fetchTodos,
        staleTime: 10_000,
        select: (todos: Todo[]) => todos.filter((t) => t.completed),
      },
    ],
    combine: ([user, todos]) => ({
      isLoading: user.isPending || todos.isPending,
      userName: user.data?.name,
      doneCount: todos.data?.length ?? 0,
    }),
  })
  return combined.isLoading ? <p>...</p> : <p>{combined.userName}{combined.doneCount}</p>
}

// 动态列表：键来自上游数据
function TodoTitles({ ids }: { ids: number[] }) {
  const results = useQueries({
    queries: ids.map((id) => ({
      queryKey: ['todo', id],
      queryFn: () => fetchTodo(id),
      enabled: id > 0,
    })),
  })
  const pending = results.some((r) => r.isPending)
  return <div>{pending ? '...' : results.map((r) => r.data?.title).join(', ')}</div>
}

// placeholderData 在 useQueries 条目内：换 key 时收不到旧数据（与单条 useQuery 不同）
// 平滑过渡：自行从缓存取旧值（key 固定时），或保留旧 key 条目
const results = useQueries({
  queries: [{
    queryKey: ['todo', 1],
    queryFn: () => fetchTodo(1),
    placeholderData: queryClient.getQueryData(['todo', 1]), // ✅ 静态占位值取自缓存
  }],
})
```

## ⚠️ 常见陷阱

- ❌ 在 `map`/循环里调 `useQuery`：违反 Hooks 规则——动态数量请交给 `useQueries`
- ❌ 以为条目内的 `placeholderData: (previousData) => previousData`（或 `keepPreviousData`）能拿到旧数据：useQueries 条目中该函数签名固定 `(previousData: undefined, previousQuery: undefined)`，换 key 后永远传 `undefined`（QueriesObserver 按 queryHash 匹配，新 key 新建 Observer）——平滑过渡需自行 `queryClient.getQueryData` 取缓存或保留旧 key 条目
- ❌ 动态列表的 key 不含变量：`queryKey: ['todo']` + 固定条目数会串数据，变量必须进 key
- ❌ `combine` 里返回每次都不同的新引用（如新建数组后又在内部变化）：会把"聚合对象变化"放大成整页重渲染，聚合值尽量是原始值或稳定结构
- ✅ 结果数组顺序恒等于 `queries` 顺序，`combine` 用解构 `([user, todos])` 或下标取用
- ✅ `combine` 返回什么，Hook 就返回什么（v5 全系可用，类型自动推断），适合把多个 `isPending` 收敛成一个

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - 单条查询的完整参数与返回值
- 📄 **[条件与依赖查询](./15-enabled-conditional-queries.md)** - 条目级 `enabled` 控制并发行为
- 📄 **[占位数据](./08-placeholder-data.md)** - `keepPreviousData` 的完整语义
- 📄 **[Query 进阶](../../frameworks/02-tanstack-query-advanced.md)** - 并行策略的教程式讲解
- 📄 **[数据看板项目](../../projects/02-data-dashboard.md)** - 多面板并行取数的完整落地

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
