# 网络模式与离线支持：networkMode

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

`networkMode` 决定浏览器**网络不可用时**查询与变更的行为：是暂停等待联网（`online`，默认）、还是先执行再由重试兜底（`offlineFirst`）、还是完全无视网络状态照常运行（`always`）。配合 `isPaused` / `onlineManager` 可构建"离线排队、联网重放"的体验。

## 📖 语法 / 签名

```ts
// 全局或单查询/单变更均可配置
new QueryClient({
  defaultOptions: {
    queries:   { networkMode: 'online' },      // 默认
    mutations: { networkMode: 'offlineFirst' } // 离线也先发一次，失败进重试
  },
})

// 三种取值
// 'online'       —— 离线时暂停：fetchStatus 变 'paused'，联网后自动继续
// 'offlineFirst' —— 离线时照发第一次请求，只有重试（第 2 次起）受网络状态限制
// 'always'       —— 完全不感知网络状态（含手动 devtools 离线模拟）
```

| 相关 API | 类型 | 说明 |
|----------|------|------|
| `isPaused` | `boolean` | 查询/变更因离线而暂停中 |
| `fetchStatus` | `'paused'` | 与 `'fetching'`/`'idle'` 并列的第三态 |
| `onlineManager.isOnline()` | `() => boolean` | 读取当前网络状态 |
| `onlineManager.subscribe(cb)` | `(cb) => unsubscribe` | 订阅联网/离线切换 |

## 💡 示例

```tsx
// 点赞调度示意：需要 api.like、Provider、导入与服务端幂等实现；内存暂停任务不等于持久化队列
const likeMutation = useMutation({
  mutationFn: api.like,
  networkMode: 'offlineFirst',
  retry: 3,
})

function OfflineBanner() {
  const [online, setOnline] = useState(onlineManager.isOnline())
  useEffect(() => onlineManager.subscribe((isOnline) => setOnline(isOnline)), [])
  if (online) return null
  return <div role="status">离线中——操作会在恢复联网后自动同步</div>
}
```

## ⚠️ 常见陷阱

- ❌ 混淆 `fetchStatus: 'paused'` 与 `status: 'pending'`：前者是"网络暂停"，后者是"尚无数据"；离线重连后 `paused` 会自动恢复取数
- ❌ 想离线重放却用默认 `online` 就不能恢复：online 模式离线时暂停，恢复联网后可以继续；offlineFirst 的区别是允许离线时先尝试一次
- ❌ 用 `offlineFirst` 处理写操作却无幂等保障：重放可能造成重复提交，服务端需幂等键
- ❌ Devtools 里切"offline"后以为代码有 bug：`always` 模式感知不到该模拟，行为差异先查配置
- ✅ 只想让"轮询本地服务/缓存计算"不受网络摆布，才用 `always`；常规 API 查询保持默认即可

<!-- full-library-explanation -->
## 网络模式决定调度，不提供离线数据库

先修：查询与 mutation、浏览器 online/offline 事件。online 模式会在离线时暂停需要网络的工作，恢复后继续；offlineFirst 允许首次尝试，适合请求可能被 Service Worker 或本地缓存满足的情况；always 适合不依赖网络状态的任务。

networkMode 不会自动把任务持久化到磁盘。页面关闭后仍想恢复 mutation，需要持久化方案、可恢复的默认 mutationFn 和服务端幂等设计。普通 mutation 默认不重试；显式配置 retry 时还要判断业务错误是否值得重试。

示例 OfflineBanner 只描述当前网络判断。浏览器认为在线也可能访问不到目标服务器；“恢复后自动同步”还取决于任务是否仍保留、重试策略与接口结果。生产界面最好展示每项操作的待同步、失败和已确认状态。

**练习：** 在在线/离线切换时观察 status 与 fetchStatus，再刷新页面确认内存任务是否保留。验收：能解释“暂停”与“正在发请求”的区别，重复点赞不会产生重复业务效果。参考[网络模式](https://tanstack.com/query/latest/docs/framework/react/guides/network-mode)。

## 🔗 相关条目

- 📄 **[QueryClient 全局配置](../framework-essentials/03-queryclient-config.md)** - defaultOptions 全局挂载点
- 📄 **[Query 核心 API](./01-query-core-api.md)** - fetchStatus / status 双轴状态模型
- 📄 **[乐观更新](./06-optimistic-update.md)** - 离线场景下的写操作组合

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
