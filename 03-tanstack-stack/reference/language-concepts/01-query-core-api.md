# Query 核心 API

## 用一张状态表读返回值

前置：Promise、React Hooks。status 回答有没有可用的查询结果，fetchStatus 回答当前请求在做什么，它们不是同一个状态机。

| 情况 | 典型状态 | 界面决策 |
|---|---|---|
| 首次请求进行中 | pending / fetching | 首屏加载 |
| 禁用且无缓存 | pending / idle | 等待条件，而非正在联网 |
| 有结果并后台重取 | success / fetching | 保留数据，附同步提示 |
| 无结果且失败 | error / idle | 错误与重试 |
| 有旧结果但重取失败 | error / idle 且可能仍有 data | 错误提示与保留历史数据 |

自测：若先写 `if (data === undefined) return 加载中`，首次失败会怎样？错误永远被前一分支截走。请先判断请求状态，并单独设计后台失败。完整演练见[基础课](../../basics/03-query-fundamentals.md)。

## 概述

TanStack Query v5 的三大核心入口：`useQuery`（声明式读）、`useMutation`（命令式写）、`QueryClient`（缓存控制中枢）。本文条目化覆盖参数、返回值与陷阱，教程过程见 [Query 基础](../../basics/03-query-fundamentals.md)。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#useQuery` `#useMutation` `#QueryClient` `#API字典` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. useQuery

### 定义

订阅一条服务端状态缓存。组件挂载/依赖变化时自动取数，同一 queryKey 的多个订阅者共享同一请求。

### 语法

```ts
const result = useQuery({
  queryKey: ['todos', 'list', { page: 1 }], // 必填，数组，可序列化
  queryFn: ({ signal }) => fetchTodos(signal), // 必填，抛错即 isError
  enabled: true,          // false 时不自动取数
  staleTime: 0,           // 数据新鲜期（毫秒），默认 0
  gcTime: 5 * 60 * 1000,  // 无订阅后的缓存保留期，默认 5 分钟
  retry: 3,               // 失败重试次数，可为函数
  select: (data) => data.filter((t) => !t.completed), // 订阅层派生
  placeholderData: (previousData) => previousData, // v5：沿用上一键数据做占位（v4 的 keepPreviousData 选项已移除）
  refetchOnWindowFocus: true, // 窗口聚焦重取（stale 时）
  initialData: undefined, // 预置缓存数据；新鲜程度受 staleTime 与 initialDataUpdatedAt 影响
  meta: {},               // 透传给缓存与全局回调的元信息
})
```

### 返回值

| 字段 | 含义 |
|------|------|
| `data` | 查询数据，类型由 queryFn 推断；`isPending` 为 true 时收窄为 `undefined`（v5 严格类型收窄） |
| `error` | 出错对象（默认为 `Error`） |
| `status` | `'pending' \| 'error' \| 'success'` |
| `fetchStatus` | `'idle' \| 'fetching' \| 'paused'` |
| `isPending` / `isSuccess` / `isError` | status 的布尔化 |
| `isFetching` | 任何请求进行中（含后台重取） |
| `isLoading` | `isPending && isFetching`（首次加载） |
| `dataUpdatedAt` | 数据最后成功时间戳 |
| `failureCount` / `failureReason` | 重试进度 |
| `isPaused` | 网络离线暂停中 |
| `refetch` | 手动重新获取 |
| `isPlaceholderData` | 当前展示的是占位数据 |

### 陷阱

- **键须可序列化且能唯一表达结果**；函数或特殊对象可能碰撞或丢失信息，使用数组、普通对象和可序列化值
- `select` 结果引用不稳定时组件会高频重渲染，复杂派生用 `useMemo` 包在 select 外
- `enabled: false` 且没有缓存时可能是 pending/idle；已有缓存仍可显示成功数据，不能把禁用查询都视作正在请求
- v5 中 `isPending` 期间 `data` 是 `undefined`；const 解构后的判别联合控制流分析自 TS 4.6 支持——**解构后同时排除 `isPending` 与 `isError` 即把 `data` 收窄为 `TData`**（`if (isPending || isError) return ...`、顺序两条 if 或 `if (!isPending && !isError)` 均可，对象访问同样适用）；**只排除 `isPending` 不收窄**（error 分支同为 `isPending: false`），需再排除 `isError` 或判 `isSuccess`。需要"保证非空"的渲染时改用 `useSuspenseQuery`

## 2. useMutation

### 定义

封装命令式操作（例如 POST/PUT/DELETE），由 mutate 或 mutateAsync 触发；结果和状态记录在 MutationCache，不会自动同步 QueryCache 中的查询结果。

### 语法与示例

```ts
const mutation = useMutation({
  mutationFn: (vars: { id: number; title: string }) => api.update(vars),
  mutationKey: ['update-todo'],      // 可选，配合全局回调
  onMutate: async (vars) => ({ snapshot: /* 缓存快照 */ null }),
  onSuccess: (data, vars, context) => {},
  onError: (error, vars, context) => {},
  onSettled: (data, error, vars, context) => {},
  retry: 0,                           // 写操作一般不重试
})
```

### 返回值

| 字段 | 含义 |
|------|------|
| `mutate(vars)` | 触发（错误不会抛出，交 onError） |
| `mutateAsync(vars)` | 触发并返回 Promise，可 await/try-catch |
| `isPending` / `isError` / `isSuccess` | 执行状态 |
| `data` / `error` / `variables` | 最近一次的产物与入参 |
| `reset()` | 清空回初始状态 |

### 陷阱

- 传给 mutate 的单次调用回调在组件卸载后可能不执行；与 useMutation 选项中定义的生命周期回调区分。mutateAsync 的拒绝仍需要调用者处理
- 同一组件多次快速 `mutate` 只保留最后一次结果的状态
- `onSuccess` 里手动 `setQueryData` 同步多个列表是维护噩梦，优先 `invalidateQueries`
- mutation 回调与 MutationCache 全局回调都能拿到 client——v5 两类回调的末位参数注入 `context`（`MutationFunctionContext`），`context.client` 即当前 QueryClient（MutationCache 的 `onSuccess`/`onError` 为第 5 参、`onSettled` 为第 6 参；`mutation` 实例上没有 `client` 属性）——组件内也常先 `const queryClient = useQueryClient()`（见上文示例），或用 `useMutationState` 做全局观测

## 3. QueryClient 方法全表

通过 `useQueryClient()` 获取实例。

| 方法 | 作用 | 典型用法 |
|------|------|---------|
| `invalidateQueries({ queryKey, exact?, refetchType? })` | 标记失效（可选重取） | 写成功后刷新列表 |
| `refetchQueries({ queryKey })` | 无视 stale 直接重取 | 强制刷新 |
| `fetchQuery({ queryKey, queryFn })` | 取数并返回 Promise（进缓存） | 事件回调中预取 |
| `prefetchQuery({ queryKey, queryFn })` | fetchQuery 的静默版 | 路由预加载 |
| `getQueryData(key)` | 同步读缓存 | 乐观更新读快照 |
| `setQueryData(key, updater)` | 同步写缓存（updater 返回 `undefined` 是 no-op，不写入也不清空；移除条目用 `removeQueries`） | 乐观更新写预测值 |
| `getQueryState(key)` | 读状态元信息 | 判断是否正在取数 |
| `cancelQueries({ queryKey })` | 取消进行中的请求 | 乐观更新前防覆盖 |
| `removeQueries({ queryKey })` | 物理删除缓存条目 | 登出清数据 |
| `resetQueries({ queryKey })` | 重置为初始态 | 重试一切 |
| `isFetching({ queryKey })` | 是否有请求进行中 | 全局 loading 条 |
| `clear()` | 清空整个缓存 | 退出登录 |
| `dehydrate(client)` / `hydrate(client, dehydrated)` | 缓存序列化/还原 | SSR 数据传递 |

```ts
// 前缀匹配默认是"包含式"的
queryClient.invalidateQueries({ queryKey: ['todos'] })                 // 匹配 ['todos', ...] 全部
queryClient.invalidateQueries({ queryKey: ['todos', 1], exact: true }) // 仅精确条目
```

### 陷阱

- `invalidateQueries` 默认只对**挂载中的查询**立即重取（`refetchType: 'active'`）
- `setQueryData` 的 updater 返回 `undefined` 会**清空**该缓存条目
- `initialData` 会重置 staleTime 计时；只想"占位不标鲜"用 `placeholderData`

## 相关文档

- 📄 **[缓存键、staleTime 与失效策略](../framework-essentials/01-query-essentials.md)** - 缓存设计规则
- 📄 **[Query 基础](../../basics/03-query-fundamentals.md)** - 教程入口
- 📄 **[乐观更新与失效](../../basics/07-advanced-features.md)** - 组合应用
- 📄 **[语法速查](../quick-references/01-syntax-cheatsheet.md)** - 一行式签名


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
