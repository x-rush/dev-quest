# QueryClient 全局配置：defaultOptions 与网络模式

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

`QueryClient` 的构造选项是全站查询/变更行为的**单点配置**：`defaultOptions` 给所有 `useQuery`/`useMutation` 提供默认值（可被单条覆盖），`queryCache`/`mutationCache` 挂载全局回调（错误上报、成功埋点）。生产项目的第一件事就是把它配好，而不是在每个 hook 里重复传参。

## 📖 语法 / 签名

```ts
new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,          // 新鲜期，期内不重发请求
      gcTime: 5 * 60_000,         // 无观察者后缓存保留期（cacheTime 已在 v5 移除）
      retry: 2,                   // 失败重试次数，可为函数
      refetchOnWindowFocus: true, // 聚焦重取（仅 stale 数据）
      refetchOnReconnect: true,   // 断网恢复重取
      networkMode: 'online',      // 离线行为，见网络模式条目
    },
    mutations: {
      retry: 0,                   // 写操作默认不重试
      networkMode: 'online',
    },
  },
  queryCache: new QueryCache({ onError, onSuccess }),
  mutationCache: new MutationCache({ onError, onSuccess, onMutate }),
})
```

| 选项 | 类型 | 说明 |
|------|------|------|
| `defaultOptions.queries` | `QueryObserverOptions` | 单条 `useQuery` 传同名选项即覆盖 |
| `defaultOptions.mutations` | `MutationOptions` | 同上 |
| `queryCache.onError` | `(error, query) => void` | 全局错误兜底（接 Sentry 等） |
| `mutationCache.onSuccess` | `(data, vars, context) => void` | 变更成功统一副作用 |

## 💡 示例

```ts
// src/shared/query-client.ts
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,          // 生产默认：宁可"多调一次"也别闪 loading
      gcTime: 10 * 60_000,
      retry: 2,
      refetchOnWindowFocus: true,
    },
    mutations: { retry: 0 },
  },
  queryCache: new QueryCache({
    onError: (error, query) => {
      Sentry.captureException(error, { tags: { queryKey: JSON.stringify(query.queryKey) } })
    },
  }),
})
```

## ⚠️ 常见陷阱

- ❌ 使用 `cacheTime` 选项：v5 已移除该别名，只有 `gcTime`
- ❌ 以为全局 `staleTime` 会覆盖单条配置：单条显式传参总是优先，顺序是"单条 > 全局 > 内置默认"
- ❌ SSR 环境共享单例 QueryClient：A 请求的缓存会渲染进 B 的 HTML——必须每请求/每组件树新建（`useState(() => new QueryClient())`）
- ❌ 全局 `retry: 3` 对所有查询一刀切：404/401 不该重试，用函数形式按 `error` 状态分流
- ✅ 全局回调只做"横切关注点"（上报、埋点），业务副作用留在具体 hook 里

## 🔗 相关条目

- 📄 **[Query 核心 API](../language-concepts/01-query-core-api.md)** - QueryClient 方法全表
- 📄 **[网络模式与离线支持](../language-concepts/10-network-mode.md)** - networkMode 三种取值详解
- 📄 **[Query 框架要点](./01-query-essentials.md)** - staleTime/gcTime 与键设计权威参考
- 📄 **[Query 实操](../../frameworks/01-tanstack-query-basics.md)** - 同主题任务式指南

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
