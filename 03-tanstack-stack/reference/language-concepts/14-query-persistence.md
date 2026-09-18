# Query 缓存持久化：恢复体验与数据边界

先修：QueryClient、浏览器存储、缓存新鲜度。持久化把部分内存缓存写入 localStorage 或其他存储，在下一次启动恢复；它不保证接口可离线写入，也不等于服务器的权威数据库。

## 1. 三种时间分别控制什么

| 配置 | 控制的问题 |
|---|---|
| staleTime | 恢复的数据是否需要重新获取 |
| gcTime | 不活跃查询在内存中保留多久 |
| maxAge | 磁盘快照允许恢复的最大年龄 |

使用整缓存持久化时，gcTime 通常应不小于 maxAge，否则缓存可能比预期更早被回收。schema 改变时使用 buster 丢弃旧结构。[官方持久化指南](https://tanstack.com/query/latest/docs/framework/react/plugins/persistQueryClient)

## 2. 浏览器 SPA 的最小 Provider

安装与 Query v5 兼容的 @tanstack/react-query-persist-client 和 @tanstack/query-sync-storage-persister。本例用于浏览器 SPA；SSR 应使用框架支持的初始化流程，不能跨请求共享该模块的 client。

```tsx
// src/persisted-provider.tsx
import type { ReactNode } from 'react';
import { QueryClient } from '@tanstack/react-query';
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';

const day = 24 * 60 * 60 * 1000;
const client = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, gcTime: day } },
});

function getStorage(): Storage | undefined {
  try { return typeof window === 'undefined' ? undefined : window.localStorage; }
  catch { return undefined; }
}

const persister = createSyncStoragePersister({
  storage: getStorage(),
  key: 'public-query-cache',
});

export function PersistedProvider({ children }: { children: ReactNode }) {
  return <PersistQueryClientProvider
    client={client}
    persistOptions={{
      persister,
      maxAge: day,
      buster: 'public-schema-v1',
      dehydrateOptions: {
        shouldDehydrateQuery: (query) =>
          query.state.status === 'success' && query.meta?.persist === true,
      },
    }}
  >{children}</PersistQueryClientProvider>;
}
```

只有明确设置 meta.persist:true 的成功查询才进入快照。示例没有实际查询，需用 Provider 包裹应用并在允许持久化的查询中声明 meta。不要用布尔开关代替对敏感字段的审查。

Provider 协调恢复与订阅，恢复期间避免查询抢先自动执行；需要独立恢复提示时可使用 @tanstack/react-query 导出的 useIsRestoring。恢复中可以显示不依赖数据的外壳，不必阻塞整个应用。

## 3. 存储失败与账号切换

localStorage 访问可能被浏览器限制，写入也可能因配额失败。缓存不可用时应允许正常联网查询，不能让启动过程永久卡住。序列化结果可能被用户或扩展修改，恢复数据不能成为授权依据。

私有数据应尽量不持久化。确需按账号保存时，设计账号隔离的键、登出清除内存与磁盘的流程，并处理仍在进行的旧账号请求，避免清理后又写回旧数据。

## 4. 离线 mutation 是另一项设计

函数本身不能随缓存序列化。恢复暂停 mutation 时，需要为对应 mutationKey 提供默认 mutationFn，再按流程 resumePausedMutations，并处理失败、重试和服务端幂等。不能只加一个 onSuccess 回调就宣称拥有可靠离线队列。

按条目 persister 是另一种方案，适合按访问恢复较大缓存。其 API 可能带 experimental 标识，应锁定版本并验证升级；先掌握整缓存流程，再评估是否需要更复杂的恢复策略。

## 5. 练习与验收

只对一条公开列表启用持久化。首次加载后等待写入，刷新并观察恢复与后台请求；修改 buster 后再次刷新，应忽略旧快照。再清空存储或模拟写入失败，应用仍应可联网使用。

验收：能分别解释 staleTime、gcTime、maxAge，磁盘没有秘密数据，恢复失败有回退路径。不要仅凭刷新后“内容还在”就认定离线一致性已经完成。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
