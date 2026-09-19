# 渲染优化：select、notifyOnChangeProps 与 structuralSharing

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

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
      // 演示保守策略：不因数组等长就丢弃新内容。
      // 普通 JSON 数据优先删除此自定义配置，使用默认结构共享。
      return newData
    },
  })
  return <div>{q.data?.length}</div>
}

// 关闭结构共享：特殊非 JSON 数据需自行评估；仅关心长度并不是关闭理由
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
- ✅ 复杂派生保持纯函数并测量成本；queryKey 放查询身份与输入，不应塞入整份派生结果

<!-- full-library-explanation -->
## 派生显示不能丢掉新事实

先修：对象引用、不可变更新。两份数组长度相同，元素仍可能完全不同；用“长度相同就返回旧数组”实现 structuralSharing 会把真实更新吃掉。默认结构共享更适合普通 JSON 数据，特殊数据结构才需要完整自定义比较。

select 在观察者层转换，缓存仍保存 queryFn 的原始结果。因此一个组件订阅任务数量，另一个订阅任务标题，可以共享请求却展示不同投影。select 函数引用改变时可能重新计算，必要时使用稳定函数或 useCallback，同时保留正确依赖。

默认属性追踪已经能发现 dataUpdatedAt 被读取，不需要仅为了显示这个字段就改成 notifyOnChangeProps:'all'。对象 rest 解构会读取更多属性，可能扩大订阅范围。

**练习：** 缓存两个任务，保持数组长度不变但修改其中一个标题。验收：标题组件更新，数量组件显示仍为 2；getQueryData 中包含新标题。然后故意使用长度比较反例，说明数据为何错误。

参考[官方渲染优化说明](https://tanstack.com/query/latest/docs/framework/react/guides/render-optimizations)。

## 渐进实作：先保证数据正确，再测量渲染

前置：已配置 Query v5 Provider，理解不可变更新与 React Profiler。产物是共享 `['render-lab']` 查询的标题列表和数量组件；模拟接口返回 JSON 数组，包含稳定 id、title、completed。上文 `fetchTodos` 为项目提供的函数，签名段是概念伪代码，不能复制为可编译配置。

先保留默认属性追踪与结构共享，数量组件用稳定的模块级 `selectCount` 函数返回数组长度；随后加入 Profiler，最后才尝试手动通知白名单。默认结构共享适用于 JSON 兼容数据，`select` 只改变观察者获得的数据，详见[官方渲染优化](https://tanstack.com/query/latest/docs/framework/react/guides/render-optimizations)。

| 操作 | 应观察结果 | 失败回查 |
|---|---|---|
| 返回两条数据 | 列表两条，数量为 2，缓存仍为完整数组 | 是否误把 select 派生值写入缓存 |
| 返回同长度但修改标题的新数组 | 标题更新，数量仍为 2 | 是否原地修改数据；自定义共享是否错误复用旧数组 |
| 保持内容相同并重新取数 | 比较 Profiler 的提交原因，不要求固定渲染次数 | StrictMode、父组件和读取的状态字段是否引入更新 |
| 在练习副本只订阅 data，再加入错误显示 | 对比默认追踪能否及时展示错误 | 手动白名单是否遗漏 error；queryFn 是否吞错 |

回滚实验白名单后，用相同输入重新测量；只有正确性保留且提交成本下降，才保留优化。函数引用稳定减少 select 重算，不保证组件永不渲染。完成后再进入[渲染性能](../../advanced-topics/performance/02-rendering-performance.md)分析昂贵子组件。本轮只核对官方资料并静态审阅，未运行 TypeScript 编译、Profiler 或性能基准；没有实测收益结论。

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - select 参数与返回值字段总表
- 📄 **[useQueries](./12-use-queries.md)** - combine 聚合与重渲染收敛
- 📄 **[无限查询](./07-infinite-query.md)** - 多页数据的 select 派生
- 📄 **[渲染性能](../../advanced-topics/performance/02-rendering-performance.md)** - 组件层性能全景
- 📄 **[Query 优化](../../advanced-topics/performance/01-query-optimization.md)** - 缓存层与网络层优化

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
