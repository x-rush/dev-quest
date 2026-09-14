# 渲染优化：select、notifyOnChangeProps 与 structuralSharing

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

Query 数据进缓存后，组件渲染层有三层阀门：`select` 只把需要的派生结果订阅进组件；`notifyOnChangeProps` 控制哪些结果字段变化才触发重渲染；`structuralSharing` 决定新数据与旧数据做引用复用（deep-equal 的部分保持旧引用），下游 `memo`/依赖数组不因等值新对象而失效。三者都在 useQuery/useInfiniteQuery/useQueries 条目上配置。

## 📖 语法 / 签名

```ts
useQuery({
  queryKey,
  queryFn,
  select?: (data: TData) => TResult,   // 只影响本订阅，不影响缓存内容
  notifyOnChangeProps?: Array<keyof 结果对象> | 'all',
  structuralSharing?: boolean | ((oldData: unknown | undefined, newData: unknown) => unknown),
})
```

| 选项 | 默认 | 语义 |
|------|------|------|
| `select` | 无 | 缓存层之上做转换/过滤/映射；组件只重渲染 select 结果变化的部分 |
| `notifyOnChangeProps` | 属性追踪 | v5 默认只对**渲染中读取过的属性**通知；`'all'` 关闭追踪、任何字段变化都重渲染 |
| `structuralSharing` | `true` | 新旧数据 deep-equal 的部分复用旧引用；`false` 每次都用新引用；函数形态完全接管比较 |

## 💡 示例

```tsx
import { useQuery } from '@tanstack/react-query'

// select：订阅层派生（原始值结果引用稳定，重渲染最少）
function DoneCount() {
  const q = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    select: (data) => data.filter((t) => t.completed).length, // 返回 number
  })
  return <span>{q.data}</span>
}

// select 按外部 prop 派生：保持引用稳定交给 select 比较即可
function OptimizedList({ showDone }: { showDone: boolean }) {
  const doneTodos = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    select: (data) => (showDone ? data.filter((t) => t.completed) : data),
    notifyOnChangeProps: ['data', 'error'], // 只在这两项变化时重渲染
  })
  return <ul>{doneTodos.data?.map((t) => <li key={t.id}>{t.title}</li>)}</ul>
}

// notifyOnChangeProps: 'all'——关闭属性追踪，任何字段变化都重渲染（如依赖 dataUpdatedAt 的时钟）
function AllProps() {
  const q = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    notifyOnChangeProps: 'all',
  })
  return <div>{q.dataUpdatedAt}</div>
}

// 自定义结构共享：参数均为 unknown，需自行断言类型
function CustomStructuralSharing() {
  const q = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    structuralSharing: (oldData, newData) => {
      return Array.isArray(oldData) && Array.isArray(newData) && oldData.length === newData.length
        ? oldData
        : newData
    },
  })
  return <div>{q.data?.length}</div>
}

// 关闭结构共享：列表总长度变化等"只关心新引用"的场景
function DisableStructuralSharing() {
  const q = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    structuralSharing: false,
  })
  return <div>{q.data?.length}</div>
}
```

## ⚠️ 常见陷阱

- ❌ `select` 返回每次新建的数组/对象且内部比较失效：select 结果引用不稳定会让组件高频重渲染——优先返回原始值；必须返回对象时保证其值稳定（Query 对 select 结果做缓存比较，引用不变则不重渲染）
- ❌ `notifyOnChangeProps: ['data']` 却渲染了 `error`/`isFetching`：漏列的字段变化不再触发重渲染，UI 停在旧值——用默认属性追踪而不是手动白名单，除非确有热点
- ❌ 以为默认行为是"任何字段变化都重渲染"：v5 默认是属性追踪（渲染中没读取的字段不通知），`'all'` 才是关闭追踪
- ❌ 自定义 `structuralSharing` 里把参数当具体类型用：两个参数类型是 `unknown | undefined` / `unknown`，需 `Array.isArray` 等断言后才能操作
- ❌ `structuralSharing: false` 误以为是性能优化：它让每次结果都换新引用，下游 `memo`/`useEffect` 依赖全部失效，默认 `true` 才是常态
- ❌ 在 `select` 里做副操作（写 store、打日志）：select 时机跟随订阅重算，不是稳定副作用点
- ✅ 复杂派生先在缓存外算好（写进 queryKey/数据层），或 select 返回原始标量

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - select 参数与返回值字段总表
- 📄 **[useQueries](./12-use-queries.md)** - combine 聚合与重渲染收敛
- 📄 **[无限查询](./07-infinite-query.md)** - 多页数据的 select 派生
- 📄 **[渲染性能](../../advanced-topics/performance/02-rendering-performance.md)** - 组件层性能全景
- 📄 **[Query 优化](../../advanced-topics/performance/01-query-optimization.md)** - 缓存层与网络层优化

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
