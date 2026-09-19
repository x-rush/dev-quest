# Query 框架要点：缓存键、staleTime/gcTime、失效与重试

## 概述

TanStack Query 用得好不好，取决于四件事：缓存键怎么设计、新鲜度怎么定、失效怎么触发、失败怎么重试。本篇是这四件事的学习速查。教程见 [Query 基础](../../basics/03-query-fundamentals.md)。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#缓存键` `#staleTime` `#gcTime` `#失效` `#重试` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. 缓存键设计

### 定义

`queryKey` 是缓存的唯一地址，Query 默认用确定性序列化哈希识别 key：`['todos', { page: 1 }]` 与 `['todos', { page: 1 }]` 命中同一条目，键内对象字段顺序无关。

### 规则

- **层级化**：从粗到细排列，`['entity', scope, params]`，让失效能按前缀截取
- **变量全部进 key**：queryFn 用到的任何动态值都必须出现在 key 中，否则会串数据
- **只放可序列化值**：string/number/boolean/plain object/array；避免函数、循环引用与语义不稳定的类实例；日期宜显式转换为一致的字符串

### 示例：键工厂

```ts
export const queryKeys = {
  todos: {
    all: ['todos'] as const,
    list: (filters: { page: number; status?: string }) =>
      ['todos', 'list', filters] as const,
    detail: (id: number) => ['todos', 'detail', id] as const,
  },
  user: (email: string) => ['user', email] as const,
}

useQuery({ queryKey: queryKeys.todos.list({ page: 1 }), queryFn })
```

### 陷阱

- key 里漏了变量：`['todos']` + `queryFn` 内部读 state → 切换分页后永远展示首条缓存
- key 里放不稳定引用：`['todos', new Date()]` 的时间值不断变化会产生新键；普通对象仅引用变化但内容相同，不会因此产生新键

## 2. staleTime vs gcTime

### 定义

| 参数 | 默认值 | 控制什么 |
|------|--------|---------|
| `staleTime` | `0` | 数据多久内算"新鲜"：通常避免因过期触发的自动重取；手动 refetch、轮询或 always 配置需另判断 |
| `gcTime` | `浏览器通常 5 分钟，SSR 默认 Infinity` | 查询无任何订阅者后，缓存条目保留多久再被垃圾回收 |

### 时间线示例

```text
t0    useQuery 挂载，无缓存 → fetch → 成功，数据 fresh（staleTime=60s）
t10   组件卸载 → 条目无订阅者，gcTime 倒计时开始
t30   组件重新挂载 → 条目仍在（gcTime 未到）、仍 fresh（staleTime 未过）→ 直接用缓存
t70   组件挂载 → 数据已 stale → 先展示缓存，后台重取
t600+ 组件重新挂载（此前一直无人订阅）→ gcTime 已过 → 缓存清除，重新 pending
```

```ts
useQuery({
  queryKey: queryKeys.todos.all,
  queryFn: fetchTodos,
  staleTime: 60_000,      // 业务上"一分钟内不需要新数据"
  gcTime: 10 * 60_000,    // 离开页面后缓存多留一会儿（返回快）
})
```

### 陷阱

- `staleTime: Infinity` 只是不因挂载/聚焦重取，`refetch()` 与 `invalidateQueries` 依然生效
- `gcTime: 0` 会导致卸载即丢缓存，返回页面闪加载态——配合 `placeholderData` 也难救
- 两者都在 QueryClient `defaultOptions.queries` 中设全局默认，按查询覆盖

## 3. 失效（invalidateQueries）

### 定义

失效 = 把匹配的缓存条目标记为 stale 并（默认）触发挂载中的查询后台重取。失效是"写之后同步读"的标准答案。

### 作用域语法

```ts
queryClient.invalidateQueries()                                        // 全部
queryClient.invalidateQueries({ queryKey: ['todos'] })                 // 前缀：todos 及其所有子键
queryClient.invalidateQueries({ queryKey: ['todos', 1], exact: true }) // 精确单条
queryClient.invalidateQueries({ predicate: (q) => q.queryKey[0] === 'todos' }) // 自定义谓词
```

### refetchType 控制

| 值 | 行为 |
|----|------|
| `'active'`（默认） | 仅挂载中的失效查询立即重取 |
| `'none'` | 只标记 stale，下次挂载/触发时才取 |
| `'all'` | 未挂载的也立即重取 |

### 陷阱

- `await invalidateQueries(...)` 等待本次操作所触发的重取；并非所有匹配查询都会被重取，只想排队不等结果用 `refetchType: 'none'` 或不 await
- 失效后组件内的 `data` 不会变 undefined——旧数据持续展示直到新数据到达

## 4. 重试（retry）

### 定义

请求失败后的自动重试策略，客户端默认 3 次、服务端默认 0 次；通常采用指数退避。读查询应按错误类型重试，mutation 默认不重试。

### 语法

```ts
useQuery({
  queryKey: queryKeys.todos.all,
  queryFn: fetchTodos,
  retry: 3, // 或 false 或函数
  retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30_000), // 1s/2s/4s...
})
```

```ts
// 函数形式：按错误类型决定是否重试
retry: (failureCount, error) => {
  if (error instanceof HttpError && error.status === 404) return false
  return failureCount < 3
}
```

### 陷阱

- 401/403/422 这类"重试也不会好"的错误要显式短路，否则用户白等三个来回
- 重试期间的中间态用 `failureCount` 渲染"第 N 次重试"提示

## 5. 重取触发时机总表

| 选项 | 默认 | 触发条件 |
|------|------|---------|
| `refetchOnMount` | `true` | 组件挂载且数据 stale |
| `refetchOnWindowFocus` | `true` | 窗口重新聚焦且 stale |
| `refetchOnReconnect` | `true` | 断网恢复且 stale |
| `refetchInterval` | `false` | 轮询（数字=毫秒，可函数） |

## 相关文档

- 📄 **[Query 核心 API](../language-concepts/01-query-core-api.md)** - 方法与返回值字典
- 📄 **[TypeScript 模式](../language-concepts/05-typescript-patterns.md)** - 键工厂类型化
- 📄 **[乐观更新与失效](../../basics/07-advanced-features.md)** - 失效策略的实战组合


<!-- full-library-explanation -->
## 用一次写入串起四个机制

先修：Promise、数组和对象。列表键 `['todos', 'list', {status: 'open'}]` 与详情键 `['todos', 'detail', 3]` 分别代表两份查询。完成任务 3 后，详情和“未完成列表”都可能需要更新；只失效详情会让列表继续显示旧状态。

staleTime 到期本身不是定时器触发请求：它改变“是否过期”的判断，后续挂载、聚焦等事件才可能触发。gcTime 针对不活跃缓存保留，不能用它表达接口每隔多久刷新。需要固定轮询时单独考虑 refetchInterval。

键应表达影响结果的业务输入，而不是所有运行细节。例如页码、排序、租户影响结果；AbortSignal 和组件函数不应进入键。普通对象每次新建但序列化内容相同，仍可以命中同一缓存。

**练习：** 预置两个列表和一个详情，调用一次前缀失效，观察哪些查询被标记、哪些立即请求。验收：解释 active 与 inactive 的差异，并确认权限错误不会反复重试。参考[查询键](https://tanstack.com/query/latest/docs/framework/react/guides/query-keys)与[重要默认值](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults)。

<!-- full-library-explanation -->
## 查询键的相等性与失效范围

查询键应由会改变结果的输入组成。不要把函数、`AbortSignal` 或每次变化的 UI 临时对象塞进键；它们既不描述服务器结果，也会使缓存边界难以解释。以下工厂把列表和详情分开，并保留租户这个会影响授权结果的维度：

```ts
export const todoKeys = {
  all: ['todos'] as const,
  list: (tenantId: string, status: 'open' | 'done') =>
    [...todoKeys.all, 'list', { tenantId, status }] as const,
  detail: (tenantId: string, id: string) =>
    [...todoKeys.all, 'detail', { tenantId, id }] as const,
};
```

完成一个待办后，失效 `todoKeys.all` 是较保守的正确起点；若只失效详情，已挂载列表可能保持旧状态。范围越小，越需要证明所有受影响视图都被覆盖。`invalidateQueries` 把匹配项标为 stale；是否立即请求还取决于 `refetchType`、观察者和网络状态，不能把“失效”理解为“已经拿到新数据”。

练习：预置两个租户各一条 list，完成 A 租户任务后只失效 A 的键前缀。验收：B 的查询不被影响；离线时 A 被标 stale，恢复网络后才可能重取。键数组构造已在仓库的提取用例中执行并比较输出；该用例不运行 TanStack Query 本身，也不证明缓存策略适合实际产品。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
