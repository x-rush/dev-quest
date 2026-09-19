# 条件与依赖查询：enabled 与 skipToken

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

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
| `enabled: false` | 不自动取数；无缓存时 pending + idle，有缓存时可为 success |
| `enabled: (query) => ...` | 根据查询实例计算是否允许自动取数；`query.state.data === undefined` 表达“没有数据才启用” |
| `skipToken` | 类型安全地省略 queryFn；保留已有缓存，但不能用普通 refetch 执行缺失的函数 |
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
    queryFn: () => {
      if (userId == null) throw new Error('缺少用户 ID');
      return fetchProjectsByUser(userId);
    }, // 手动 refetch 也可能调用，因此保留运行时检查
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

// 编辑中暂停自动取数；不会删除已有缓存，也不是取消在途请求
function EditableTodos({ isEditing }: { isEditing: boolean }) {
  const todosQuery = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    enabled: !isEditing,
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
  if (q.isPending) return <p>{!ready ? '未启用' : q.isFetching ? '加载中' : '等待网络'}</p>
  if (q.isError) return <p>{q.error.message}</p>
  return <div>{q.data.length}</div>
}
```

## ⚠️ 常见陷阱

- ❌ 依赖查询把 `userId!` 直接塞进 queryFn 却不写 `enabled`：请求带着 `undefined` 就发出去了——`enabled: userId != null` 是硬前提
- ❌ 以为 `enabled: false` 会清除数据：缓存照常保留、组件照常展示旧数据，只是不自动刷新
- ❌ 渲染分支只判 `isPending`：没有缓存的 disabled 查询常处于 `pending`，会把"未启用"误显示成"加载中"——结合 `fetchStatus === 'idle'` 或业务状态区分
- ❌ 以为 `enabled: false` 连手动 `refetch()` 也禁了：手动调用不受限；应保护 queryFn 参数或使用 skipToken；cancelQueries 取消当前工作，不是永久禁止之后的调用
- ❌ 用对象解构 `const { data, isPending } = useQuery(...)` 后判 `isPending` 收窄 `data`：只排除 pending 仍可能留下 error；现代 TypeScript 的 const 解构支持关联收窄，应同时处理失败分支（详见 [Query 核心 API](./01-query-core-api.md)）
- ✅ 键里同步带上依赖值（`['projects', userId]`），与 `enabled` 双保险：值变即新键，避免串数据
- ✅ `useQueries` 的每个条目同样支持 `enabled`，用于"部分 id 合法才取"（见 [useQueries](./12-use-queries.md)）

<!-- full-library-explanation -->
## 禁用自动调度与参数有效性分别保证

先修：undefined 收窄、查询状态。enabled 为 false 时，如果缓存已有数据，状态可以是 success；没有数据时才常见 pending + idle。isLoading 结合 pending 与 fetching，更接近“正在首次加载”。

enabled 不是运行时参数验证。手动 refetch 可绕过 enabled，因此 queryFn 内仍应保护必需参数，或在缺少参数时用 skipToken。skipToken 不提供可执行的 queryFn，不能像普通 disabled 查询那样直接 refetch；它也不保证缓存 data 一定是 undefined。

```tsx
// 参数部分示例，fetchProjectsByUser 由项目提供
const projects = useQuery({
  queryKey: ['projects', userId],
  queryFn: userId == null ? skipToken : () => fetchProjectsByUser(userId),
});
```

现代 TypeScript 能对未重新赋值的 const 解构判别联合进行关联收窄。是否收窄还取决于排除的是 pending 还是 error；不要把所有类型问题都归因于“解构必定丢类型”。

**练习：** 先禁用一个已有缓存的查询，再禁用一个空缓存查询，比较 status/data/fetchStatus。随后比较普通 enabled:false 的 refetch 与 skipToken。验收：界面区分未开始、请求中、失败与已有数据，缺少 ID 时不会调用接口。参考[禁用与暂停查询](https://tanstack.com/query/latest/docs/framework/react/guides/disabling-queries)。

## 实作：提交筛选后才读取项目

前置：在现有 React 工程中安装 Query v5，并在根部使用稳定的 `QueryClient` 和 `QueryClientProvider`；掌握 `useState`、Promise 与 `queryKey`。这里的示例函数由练习工程提供，不能把上面的片段直接当作完整应用。

产物是一个筛选面板：文本框保存草稿，提交后将经过 trim 的 ID 写入 `submittedId`，查询键为 `['projects', submittedId]`。模拟接口接收非空 ID，延迟 500ms 后返回 `{ id: 'p1', name: '项目 A' }[]`，输入 `fail` 时抛出 Error。先用本地 Promise 排除服务端因素，再接真实 API。

| 输入或动作 | 应观察的输出 | 失败回查 |
|---|---|---|
| 初始 ID 缺失，用 `skipToken` | 提示输入 ID；空缓存是 pending + idle，接口计数为 0 | 是否误调用 `fetchProjects()` 而非传函数；是否读到同键缓存 |
| 只编辑草稿，不提交 | 查询键和请求次数均不变 | 是否把草稿直接放入 key |
| 提交有效 ID | 首次 fetching 后显示项目；换 ID 对应新缓存条目 | key 是否包含 submittedId；接口是否确实返回数据 |
| 提交 `fail`，练习中设置 `retry: false` | 显示错误和重新提交入口 | Promise 是否抛错；是否被默认重试延后错误展示 |
| 成功后改为 `enabled: false` | 已有结果仍可显示，自动刷新停止 | 不要把禁用当作清缓存或退出登录 |

另建一个空缓存查询对照：普通 `enabled: false` 加有效 `queryFn` 时，Hook 返回的 `refetch()` 可以执行；`skipToken` 不具备可执行函数。不要向 `refetch` 传入新的业务 ID，更新状态和 key 才能保留缓存身份。禁用也不代替取消在途请求；需要取消时单独设计 `cancelQueries` 和 AbortSignal。官方行为依据见[禁用查询](https://tanstack.com/query/latest/docs/framework/react/guides/disabling-queries)。

完成后再读 [useQueries](./12-use-queries.md)，把一个 ID 扩展为动态 ID 列表；不要在循环中调用 `useQuery`。本轮只核对官方资料并静态审阅，未运行 React、Query Provider、网络或浏览器交互；表格是待执行的验收步骤。

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - enabled 参数位置与类型收窄规则
- 📄 **[useQueries](./12-use-queries.md)** - 并行列表中的条目级 enabled
- 📄 **[占位数据](./08-placeholder-data.md)** - initialData 与 placeholderData 的语义边界
- 📄 **[缓存键、staleTime 与失效策略](../framework-essentials/01-query-essentials.md)** - 键设计与依赖联动
- 📄 **[缓存持久化](./14-query-persistence.md)** - 恢复期 `useIsRestoring` 与 enabled 的配合

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
