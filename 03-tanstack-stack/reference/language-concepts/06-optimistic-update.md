# 乐观更新：onMutate 快照与回滚

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

乐观更新是"先改缓存、后等服务端"的写操作模式：`useMutation` 的 `onMutate` 在请求发出前直接修改本地缓存让 UI 即时响应，失败时用快照回滚，最终以 `invalidateQueries` 与服务端事实对齐。解决的是高频小操作（点赞、勾选、拖拽）中"等待服务器响应导致 UI 卡顿"的感知问题。

## 📖 语法 / 签名

```ts
useMutation({
  mutationFn: (vars) => Promise<TData>,
  onMutate: async (vars) => {
    // ① 取消在途请求，防止旧响应覆盖乐观值
    await queryClient.cancelQueries({ queryKey })
    // ② 快照当前缓存
    const previous = queryClient.getQueryData<TData>(queryKey)
    // ③ 直写缓存（UI 立即变化）
    queryClient.setQueryData<TData>(queryKey, (old) => next)
    // ④ 返回值作为 context 传给 onError / onSettled
    return { previous }
  },
  onError: (error, vars, context) => context?.previous /* 回滚 */,
  onSettled: () => queryClient.invalidateQueries({ queryKey }),
})
```

| 要素 | 类型 | 说明 |
|------|------|------|
| `cancelQueries` | `(filters) => Promise` | 必须先 `await`，否则竞态会覆盖乐观值 |
| `getQueryData` | `(key) => TData \| undefined` | 同步读缓存做快照 |
| `setQueryData` | `(key, updater) => void` | updater 返回 `undefined` 会清空条目 |
| context（第 3 参数） | `onMutate` 的返回值 | 携带快照等回滚材料 |

## 💡 示例

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'

type Todo = { id: number; title: string; done: boolean }

export function useToggleTodo() {
  // 推荐：在作用域内用 useQueryClient 获取 client（v5 回调 context 中也注入了 client）
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (todo: Todo) => api.toggle(todo),
    onMutate: async (todo) => {
      await queryClient.cancelQueries({ queryKey: ['todos'] })
      const previous = queryClient.getQueryData<Todo[]>(['todos'])
      queryClient.setQueryData<Todo[]>(['todos'], (old) =>
        old?.map((t) => (t.id === todo.id ? { ...t, done: !t.done } : t)),
      )
      return { previous }
    },
    onError: (_err, _todo, context) => {
      if (context?.previous) queryClient.setQueryData(['todos'], context.previous)
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: ['todos'] }),
  })
}
```

**四步口诀**：取消在途 → 快照缓存 → 立即直写 → 出错回滚、最终对齐。

## ⚠️ 常见陷阱

- ❌ **不做** `await cancelQueries` 就直写缓存：进行中的旧请求完成后会把乐观值覆盖回旧数据
- ❌ `setQueryData` 的 updater 返回 `undefined`：该缓存条目被清空，UI 反而消失
- ❌ 在 `onSuccess` 里用 `setQueryData` 手工"缝合"所有相关列表：把自己变成缓存同步器，优先 `invalidateQueries`
- ✅ 回滚材料通过 `onMutate` 返回值（context）传递，不要依赖外部可变变量
- ✅ 高频写需聚合展示时用 `useMutationState` 订阅全局 mutation 状态（见 Mutation 状态条目）

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - setQueryData / cancelQueries 精确语义
- 📄 **[Mutation 状态与副作用](../framework-essentials/05-mutation-state.md)** - 全局 mutation 副作用挂载点
- 📄 **[Query 高级特性教程](../../basics/07-advanced-features.md)** - 同主题教程式讲解
- 📄 **[Query 进阶](../../frameworks/02-tanstack-query-advanced.md)** - 四步模式完整实战
- 📄 **[协作看板项目](../../projects/03-collaborative-kanban.md)** - 乐观更新 + 实时同步场景

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
