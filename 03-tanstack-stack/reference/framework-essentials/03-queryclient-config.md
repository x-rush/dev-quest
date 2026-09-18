# QueryClient 全局配置：defaultOptions 与网络模式

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

`QueryClient` 的构造选项是全站查询/变更行为的**单点配置**：`defaultOptions` 给所有 `useQuery`/`useMutation` 提供默认值（可被单条覆盖），`queryCache`/`mutationCache` 挂载全局回调（错误上报、成功埋点）。生产项目的第一件事就是把它配好，而不是在每个 hook 里重复传参。

## 📖 语法 / 签名

```ts
new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,          // 新鲜期，通常避免基于过期判断的自动重取
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
      staleTime: 60_000,          // 示例新鲜期；按业务允许的陈旧程度调整
      gcTime: 10 * 60_000,
      retry: 2,
      refetchOnWindowFocus: true,
    },
    mutations: { retry: 0 },
  },
  queryCache: new QueryCache({
    onError: (error, query) => {
      Sentry.captureException(error, { tags: { queryGroup: String(query.queryKey[0]) } }) // 仅用确认无敏感信息的分组名
    },
  }),
})
```

## ⚠️ 常见陷阱

- ❌ 使用 `cacheTime` 选项：v5 已移除该别名，只有 `gcTime`
- ❌ 以为全局 `staleTime` 会覆盖单条配置：单条显式传参总是优先，还需考虑 setQueryDefaults 的按键默认值；调用处显式值优先
- ❌ SSR 环境共享单例 QueryClient：A 请求的缓存会渲染进 B 的 HTML——必须每请求/每组件树新建（`useState(() => new QueryClient())`）
- ❌ 全局 `retry: 3` 对所有查询一刀切：404/401 不该重试，用函数形式按 `error` 状态分流
- ✅ 全局回调只做"横切关注点"（上报、埋点），业务副作用留在具体 hook 里

<!-- full-library-explanation -->
## QueryClient 的生命周期比默认值更基础

先修：React Provider 和缓存键。浏览器中应让同一应用区域复用稳定 client；每次组件渲染都 new 会不断换缓存。服务器中应按请求隔离，避免一个用户的缓存进入另一个请求。

useState 初始化适合有正确边界的组件树，但首次渲染在提交前挂起且下方没有 Suspense 边界时，React 可能丢弃该次状态。SSR 与流式场景应采用框架集成或官方推荐的 server/browser client 工厂，不能仅机械套一行 useState。

全局默认值、按键 setQueryDefaults、调用处选项共同组成配置。建议在 Query Devtools 中查看实际结果，避免只读全局配置就推断每个查询的行为。错误日志也不应直接发送完整 queryKey，键里可能包含邮箱、搜索词或其他敏感参数。

**练习：** 两个组件观察相同键，确认共享数据；再给不同 Provider 使用不同 client，观察两份缓存。验收：能解释为什么查询键相同还可能不共享，并能指出服务器请求隔离的位置。参考[SSR 初始化](https://tanstack.com/query/latest/docs/framework/react/guides/advanced-ssr)。

## 🔗 相关条目

- 📄 **[Query 核心 API](../language-concepts/01-query-core-api.md)** - QueryClient 方法全表
- 📄 **[网络模式与离线支持](../language-concepts/10-network-mode.md)** - networkMode 三种取值详解
- 📄 **[Query 框架要点](./01-query-essentials.md)** - staleTime/gcTime 与键设计权威参考
- 📄 **[Query 实操](../../frameworks/01-tanstack-query-basics.md)** - 同主题任务式指南

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
