# Query 缓存架构与数据流

> **文档简介**: 深入 TanStack Query 缓存内部：QueryCache/QueryObserver 的分层结构、键哈希机制、条目生命周期与失效传播的数据流，解释"缓存为什么能当事实来源"。
>
> **目标读者**: 已熟练使用 Query、想理解内部机制以驾驭复杂场景的资深开发者
>
> **前置知识**: [Query 进阶](../../frameworks/02-tanstack-query-advanced.md)、[缓存键与失效参考](../../reference/framework-essentials/01-query-essentials.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#缓存架构` `#querycache` `#observer` `#数据流` |
| **更新日期** | 2026年9月 |

</details>

---

## 1. 三层结构：Client → Cache → Observer

```
组件层   useQuery(...) / useMutation(...)
            │ 订阅/取消订阅
观察者层   QueryObserver（每个 useQuery 调用一个）
            │ 读取结果、聚合状态、通知渲染
缓存层    QueryCache（QueryClient 持有）
            │ Map<hashedKey, Query>（每个缓存键一个 Query 实例）
网络层    Query.fetch() → queryFn → Promise 去重
```

**关键区分**：同一 queryKey 的多个组件**共享一个 Query 实例**，但各自持有独立的 **QueryObserver**。这解释了两个常见现象：

- 同一 client 的同键在途查询通常共享 Promise；先后挂载、失效与重试仍可能产生后续请求
- 一个组件用 `select` 派生、另一个不用 → 各自的 observer 通知时机独立，互不拖累

---

## 2. 键哈希：数组如何变成 Map 的键

```ts
// queryKey: ['todos', 'list', { page: 1, sort: 'desc' }]
// 内部哈希（JSON.stringify 的确定性变体，对象键排序后序列化）：
// '["todos","list",{"page":1,"sort":"desc"}]'
```

推论：

1. **键序敏感**：`['a', 'b']` 与 `['b', 'a']` 是两个缓存条目
2. **对象键序不敏感**：`{ page: 1, sort: 'desc' }` 与 `{ sort: 'desc', page: 1 }` 哈希一致——Query 会对对象键做规范化排序
3. **不可序列化的值不可靠**：函数、class 实例哈希后无意义，禁止进键
4. **版本号进键**：接口结构升级时把版本段写进键（`['todos', 'v2']`），为新旧结构共存与迁移留出口

`invalidateQueries({ queryKey: ['todos'] })` 默认对原始 queryKey 做结构化部分匹配，不是对哈希字符串做 startsWith。

---

## 3. 单个条目的生命周期

```
add（首个 observer 挂载或 prefetch）
  → fetch（若无新鲜数据）
    → 状态机：pending → success / error
      → idle（staleTime 内 fresh，无请求）
        → 过期（staleTime 后标记 stale，触发时机：挂载/聚焦/重连/失效）
          → GC 候选（所有 observer 卸载后计时 gcTime）
            → remove（gcTime 到期，缓存条目销毁）
```

两个计时器驱动一切：

| 计时器 | 起点 | 含义 |
|--------|------|------|
| `staleTime` | 数据成功写入时 | 数据多久内"可信"，期内复用不重取 |
| `gcTime` | 最后一个 observer 卸载 | 无人使用的条目在缓存里活多久 |

**stale ≠ 重新请求**：stale 只是一个标记，真正发起请求要等触发器（组件挂载、`refetchOnWindowFocus`、`invalidateQueries`、`refetchQueries`）。理解这一点，[失效策略](../../frameworks/02-tanstack-query-advanced.md) 的行为就全部可预测。

---

## 4. 失效与重取的传播路径

```
invalidateQueries(['todos'])
  → QueryCache 按 queryKey 结构匹配过滤条件
    → 逐条目标记 invalidated + stale
      → 活跃 observer（refetchType: 'active' 默认）→ 立即触发 fetch
      → 非活跃条目 → 仅标记，等下次挂载
        → fetch 完成 → 通知所有 observer → 各组件按需重渲染
```

**为什么乐观更新前要 `cancelQueries`**：在途 fetch 完成后会用**旧快照**覆盖缓存。乐观写发生在"旧请求尚未返回"的窗口里，如果不先取消，旧响应落地的瞬间就把乐观结果冲掉——这是 [协作看板](../../projects/03-collaborative-kanban.md) 版本号守卫的同一族问题。

---

## 5. 多标签页与内存账单

- **跨标签页无内建缓存广播**：query-core 不含 BroadcastChannel——各标签页独立持缓存，仅在窗口聚焦时经 focusManager 重取 stale 查询（`refetchOnWindowFocus`）；需要真同步得自建 BroadcastChannel 方案（对端收消息后失效或 `setQueryData`）
- **内存账单**：同一时刻各保留条目的实际大小之和；保留时长影响能积累多少条目。无限列表用 `maxPages` 封顶；大对象列表瘦身要在 queryFn 或服务端做（`select` 只省渲染不省内存，数据仍在缓存里）
- **多租户隔离**：租户 ID 进键（`['projects', { tenant: 'acme' }]`）之外，登出时 `queryClient.clear()` 是最后的保险丝

---

## 💡 设计启示

1. **缓存是事实来源，组件是投影**——服务器快照尽量统一管理；未保存草稿与纯 UI 状态仍可有独立所有者
2. **键即坐标**——键设计决定了失效、预取、GC 的一切粒度
3. **两个计时器一个触发器**——staleTime/gcTime + 触发时机，是理解新鲜度与保留期的重要参数，重试、订阅、并发等仍需另行考虑
4. **失效即事件**——把"数据可能过期"当事件广播给缓存，而不是让组件轮询比较时间戳

---

<!-- full-library-explanation -->
## 观察者选项与缓存身份不是同一层

先修：两个组件共享查询的例子。相同 client、相同键指向同一缓存查询；每个观察者可以选择不同 select 与展示状态。不同 client 即使键相同仍是两份缓存，不能跨 Provider 自动共享。

缓存是客户端对服务器数据的一份快照。离线、失败、权限变更、另一用户写入都会让它过期，所以“事实来源”应限定为客户端当前展示来源，而不是业务权威来源。编辑草稿也不应被后台快照无条件覆盖。

默认键哈希用于精确身份，失效过滤则对 queryKey 做结构化部分匹配。比如 `['todos', {status:'open'}]` 可以匹配带相同 status 和额外 page 字段的键；它不是简单字符串 startsWith。

**练习：** 同时挂载一个任务标题列表和任务计数组件，共享键但使用不同 select。更新一个标题且不改变数量，观察缓存与两个组件各自的结果；再用对象部分键失效。验收：能指出 Query、Observer、client 的边界，而不是只背“缓存去重”。

## 🔗 相关文档

- 📄 **[Query 核心 API](../../reference/language-concepts/01-query-core-api.md)** - 文中各机制的参数入口
- 📄 **[缓存键、staleTime 与失效策略](../../reference/framework-essentials/01-query-essentials.md)** - 参数层面的速查
- 📄 **[查询性能优化](../performance/01-query-optimization.md)** - 把本文的旋钮调到最优
- 📄 **[协作看板](../../projects/03-collaborative-kanban.md)** - 缓存直写与版本守卫的实战
- 📄 **[SaaS 后台](../../projects/04-saas-admin-platform.md)** - 多租户隔离的工程落地


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
