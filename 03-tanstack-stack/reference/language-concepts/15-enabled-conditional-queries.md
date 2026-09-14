# 条件与依赖查询：enabled 与 skipToken

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

`enabled` 控制一条查询是否**自动**取数：`false` 时不挂载取数、不响应聚焦/重连/轮询等一切自动触发；`skipToken` 是等价的类型友好写法（直接放进 `queryFn` 位置，能让 `data` 类型保持 `TData | undefined` 的同时跳过请求）。典型场景：依赖查询（B 需要 A 的结果作参数）、表单编辑中暂停轮询、权限未就绪时挂起。

## 📖 语法 / 签名

```ts
// 布尔形态
useQuery({ queryKey, queryFn, enabled: boolean })

// 函数形态：收到查询实例，可读 query.state.data 做决策
useQuery({ queryKey, queryFn, enabled: (query) => boolean })

// skipToken 形态：queryFn 位置二选一
useQuery({ queryKey, queryFn: ready ? fetchTodos : skipToken })
```

| 形态 | 行为 |
|------|------|
| `enabled: false` | 不自动取数；`status` 停在 `'pending'`、`fetchStatus` 为 `'idle'`；已缓存数据照常展示 |
| `enabled: (query) => ...` | 每次取数决策前调用，可用 `query.state.data === undefined` 表达"仅有缓存才跳过" |
| `skipToken` | 与 `enabled: false` 等价；类型层面把该条结果视为 `undefined` 数据 |
| 手动 `refetch()` | **不受 `enabled` 限制**——`false` 只关闭自动触发，手动调用仍发起请求 |

## 💡 示例

```tsx
import { useQuery, skipToken } from '@tanstack/react-query'

// 依赖查询：B 的参数来自 A 的结果
function UserProjects({ email }: { email: string }) {
  const { data: user } = useQuery({
    queryKey: ['user', email],
    queryFn: () => fetchUserByEmail(email),
  })
  const userId = user?.id

  const projectsQuery = useQuery({
    queryKey: ['projects', userId],
    queryFn: () => fetchProjectsByUser(userId!), // enabled 保证非空才执行
    enabled: userId != null,
  })
  return <div>{projectsQuery.data?.length}</div>
}

// 函数形态：有缓存就不再自动取（进入页面即用缓存，需要新鲜数据再手动 refetch）
function CachedFirst() {
  const q = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    enabled: (query) => query.state.data === undefined,
  })
  return <div>{q.data?.length}</div>
}

// skipToken：条件取数的类型友好写法
function SkipWhenIdle({ ready }: { ready: boolean }) {
  const q = useQuery({
    queryKey: ['todos'],
    queryFn: ready ? fetchTodos : skipToken,
  })
  return <div>{q.data?.length}</div>
}

// 编辑中暂停自动取数，且不预置 initialData（由应用层条件控制）
function EditableTodos({ isEditing }: { isEditing: boolean }) {
  const todosQuery = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    enabled: !isEditing,
    initialData: isEditing ? undefined : fetchTodosCache(),
  })
  return <div>{todosQuery.data?.length}</div>
}

// disabled 查询的渲染分支：status 停在 pending，需自行区分"未启用"与"加载中"
function DisabledRendering({ ready }: { ready: boolean }) {
  const q = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    enabled: ready,
  })
  if (q.isPending) return <p>{ready ? '加载中' : '未启用'}</p>
  if (q.isError) return <p>{q.error.message}</p>
  return <div>{q.data.length}</div>
}
```

## ⚠️ 常见陷阱

- ❌ 依赖查询把 `userId!` 直接塞进 queryFn 却不写 `enabled`：请求带着 `undefined` 就发出去了——`enabled: userId != null` 是硬前提
- ❌ 以为 `enabled: false` 会清除数据：缓存照常保留、组件照常展示旧数据，只是不自动刷新
- ❌ 渲染分支只判 `isPending`：disabled 查询 `status` 永远停在 `pending`，会把"未启用"误显示成"加载中"——结合 `fetchStatus === 'idle'` 或业务状态区分
- ❌ 以为 `enabled: false` 连手动 `refetch()` 也禁了：手动调用不受限；需要彻底禁止请在 `queryFn` 里抛出或用 `queryClient.cancelQueries`
- ❌ 用对象解构 `const { data, isPending } = useQuery(...)` 后判 `isPending` 收窄 `data`：解构丢失判别联合，`data` 仍是 `TData | undefined`——保留对象访问并按序排除 `isPending`/`isError`（详见 [Query 核心 API](./01-query-core-api.md)）
- ✅ 键里同步带上依赖值（`['projects', userId]`），与 `enabled` 双保险：值变即新键，避免串数据
- ✅ `useQueries` 的每个条目同样支持 `enabled`，用于"部分 id 合法才取"（见 [useQueries](./12-use-queries.md)）

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - enabled 参数位置与类型收窄规则
- 📄 **[useQueries](./12-use-queries.md)** - 并行列表中的条目级 enabled
- 📄 **[占位数据](./08-placeholder-data.md)** - initialData 与 placeholderData 的语义边界
- 📄 **[缓存键、staleTime 与失效策略](../framework-essentials/01-query-essentials.md)** - 键设计与依赖联动
- 📄 **[缓存持久化](./14-query-persistence.md)** - 恢复期 `useIsRestoring` 与 enabled 的配合

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
