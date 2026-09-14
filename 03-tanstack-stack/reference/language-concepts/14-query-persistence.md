# 缓存持久化：PersistQueryClientProvider 与按条目持久化

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

把 Query 缓存写入 localStorage / IndexedDB 等存储，冷启动秒开、离线可读。两条路线：**整缓存方案**——`PersistQueryClientProvider` 包装根组件，dehydrate/hydrate 整个缓存（配 `useIsRestoring` 控制恢复期渲染）；**按条目方案**——`experimental_createQueryPersister` 逐条持久化，通过 `persister` 选项挂进单条查询。整缓存实现简单但恢复是全量阻塞；按条目恢复渐进、可与 `staleTime` 精细配合。

## 📖 语法 / 签名

```ts
// —— 整缓存：Provider 形态 ——
<PersistQueryClientProvider
  client={queryClient}
  persistOptions={{
    persister,            // Persister 接口：persistClient / restoreClient / removeClient
    maxAge?: number,      // 过期毫秒数，默认 24 小时
    buster?: string,      // 版本戳，与存储值不符则丢弃缓存
    dehydrateOptions?: { shouldDehydrateQuery?: (query) => boolean, /* ... */ },
    hydrateOptions?: object,
  }}
  onSuccess?: () => void  // 恢复完成后
  onError?: (e) => void
/>

// —— 整缓存：存储层 ——
createSyncStoragePersister({ storage: localStorage, key?, throttleTime?, serialize?, deserialize? })
createAsyncStoragePersister({ storage: { getItem, setItem, removeItem }, key?, throttleTime? })

// —— 按条目：experimental_createQueryPersister ——
experimental_createQueryPersister({
  storage: localStorage,
  maxAge?: number,          // 默认 24 小时
  buster?: string,          // 默认沿用当前 clientVersion 体系
  prefix?: string,          // 存储键前缀，默认 'tanstack-query'
  refetchOnRestore?: boolean, // 恢复后是否后台重取，默认 true
})
// 返回：{ persisterFn, persistQuery, persistQueryByKey, retrieveQuery, persisterGc, restoreQueries, removeQueries }
```

`useIsRestoring(): boolean`——仅在 `PersistQueryClientProvider` 树内有意义，恢复期间为 `true`。

## 💡 示例

```tsx
import {
  QueryClient, useQuery, useIsRestoring,
} from '@tanstack/react-query'
import {
  PersistQueryClientProvider, removeOldestQuery,
} from '@tanstack/react-query-persist-client'
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister'
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister'
import { experimental_createQueryPersister } from '@tanstack/query-persist-client-core'

const queryClient = new QueryClient()

// 同步存储（localStorage）——serialize/deserialize 可省略，默认 JSON.stringify/parse
const syncPersister = createSyncStoragePersister({
  storage: typeof window !== 'undefined' ? window.localStorage : undefined,
  key: 'app-query-cache',
  throttleTime: 1000,
})

// 异步存储（IndexedDB 封装）——三个方法都返回 Promise
const asyncPersister = createAsyncStoragePersister({
  storage: {
    getItem: async (key) => (await idbGet(key)) ?? null,
    setItem: async (key, value) => { await idbSet(key, value) },
    removeItem: async (key) => { await idbRemove(key) },
  },
  key: 'app-query-cache-idb',
})

function AppRoot() {
  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{
        persister: syncPersister,
        maxAge: 1000 * 60 * 60 * 24,
        buster: 'v1',
        // meta 值类型是 unknown，需显式比较而不是 ?? 兜底
        dehydrateOptions: {
          shouldDehydrateQuery: (query) => query.meta?.persist === true,
        },
      }}
      onSuccess={() => {
        // 恢复后先重放离线期间暂停的 mutation，再整体失效刷新
        queryClient.resumePausedMutations().then(() => {
          queryClient.invalidateQueries()
        })
      }}
    >
      <PersistedApp />
    </PersistQueryClientProvider>
  )
}

function PersistedApp() {
  const isRestoring = useIsRestoring()
  return isRestoring ? <Splash /> : <TodoList /> // 恢复完成前不依赖缓存的 UI 先行渲染
}

// —— 按条目方案：挂进单条 query 的 persister 选项 ——
const perQueryPersister = experimental_createQueryPersister({
  storage: window.localStorage,
  maxAge: 1000 * 60 * 60 * 24 * 7,
  refetchOnRestore: true,
})

function PerQueryPersisted() {
  const q = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    persister: perQueryPersister.persisterFn, // 恢复失败/过期则回落到 queryFn
    staleTime: 5_000,
  })
  // 应用启动时批量还原整批条目（可选）
  void perQueryPersister.restoreQueries(queryClient)
  // removeOldestQuery：存储写满时的重试策略（丢最旧条目），可配给 persister 的重试逻辑
  void removeOldestQuery
  return <div>{q.data?.length}</div>
}
```

## ⚠️ 常见陷阱

- ❌ SSR 环境直接引用 `window.localStorage`：构建/服务端阶段无 `window`，须 `typeof window !== 'undefined'` 守卫（或仅在客户端组件挂载后创建 persister）
- ❌ `shouldDehydrateQuery: (q) => q.meta?.persist ?? false`：`meta` 值类型是 `unknown`，`??` 编译不通过——用 `=== true` 显式比较
- ❌ 忽略恢复期：恢复完成前自动取数会发出多余请求——用 `useIsRestoring` 渲染占位，恢复完成再放行
- ❌ 整缓存方案把敏感数据一并序列化进 localStorage：XSS 可读——用 `dehydrateOptions.shouldDehydrateQuery` 白名单过滤
- ❌ mutation 离线排队后不处理：仅恢复缓存不重放请求——`onSuccess` 里先 `resumePausedMutations()` 再 `invalidateQueries()`
- ❌ 版本升级后读到旧结构缓存：schema 变化时改 `buster` 旧缓存即整体作废
- ✅ 按条目方案 `persister: perQueryPersister.persisterFn` 挂在 `queryFn` 同级，恢复失败自动回落网络请求

## 🔗 相关条目

- 📄 **[Query 核心 API](./01-query-core-api.md)** - dehydrate/hydrate 与 QueryClient 方法
- 📄 **[条件与依赖查询](./15-enabled-conditional-queries.md)** - 恢复期禁用自动取数的另一写法
- 📄 **[生态集成](../library-guides/01-ecosystem-integrations.md)** - 各存储 persister 的选型与接入
- 📄 **[缓存架构](../../advanced-topics/architecture/01-cache-architecture.md)** - 缓存分层与序列化边界
- 📄 **[SSR 与预取](../framework-essentials/04-prefetch-ssr.md)** - 服务端数据传递与持久化的边界

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
