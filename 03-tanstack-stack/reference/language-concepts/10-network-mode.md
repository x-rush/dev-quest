# 网络模式与离线支持：networkMode

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

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
// 点赞类操作：离线也能点，联网后重试队列自动重放
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
- ❌ 想离线重放却用默认 `online`：mutation 会一直挂起不动，需显式 `offlineFirst`（或 `always`）+ 合理 `retry`
- ❌ 用 `offlineFirst` 处理写操作却无幂等保障：重放可能造成重复提交，服务端需幂等键
- ❌ Devtools 里切"offline"后以为代码有 bug：`always` 模式感知不到该模拟，行为差异先查配置
- ✅ 只想让"轮询本地服务/缓存计算"不受网络摆布，才用 `always`；常规 API 查询保持默认即可

## 🔗 相关条目

- 📄 **[QueryClient 全局配置](../framework-essentials/03-queryclient-config.md)** - defaultOptions 全局挂载点
- 📄 **[Query 核心 API](./01-query-core-api.md)** - fetchStatus / status 双轴状态模型
- 📄 **[乐观更新](./06-optimistic-update.md)** - 离线场景下的写操作组合

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
