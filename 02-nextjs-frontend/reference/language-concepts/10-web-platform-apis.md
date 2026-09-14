# Web 平台 API 速查（fetch / URL / FormData / Storage / Blob / structuredClone / BroadcastChannel）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（无难度门槛）
> **分类**: `language-concepts`

## 📌 定义

七个不依赖任何框架、写前端必用的浏览器内置 API。它们与 Next.js 有一个共同交汇点：**全部只在客户端环境可用**（部分在 Node 24 也有同名全局实现，但语义以浏览器为准）——在 Server Component / 服务器代码里直接调用会在构建或运行时出错，是本模块最常见的 SSR 陷阱来源。

## 📖 语法 / API 表

| API | 一句话定位 | 关键签名 |
|-----|-----------|---------|
| `fetch` | 发起 HTTP 请求（基于 Promise） | `fetch(url, { signal?, method?, headers?, body? }): Promise<Response>` |
| `AbortController` | 取消 fetch/监听器 | `controller.abort(reason?)`；`signal` 传入 fetch |
| `AbortSignal.timeout` | 超时自动取消的 signal | `AbortSignal.timeout(ms): AbortSignal` |
| `URL` / `URLSearchParams` | 解析与构造 URL / 查询串 | `new URL(str, base?)`；`url.searchParams.get/set/...` |
| `FormData` | 键值对容器（表单/文件上传） | `fd.append/get/getAll/set/has/delete` |
| `localStorage` / `sessionStorage` | 持久 / 会话级键值存储（仅客户端） | `getItem/setItem/removeItem/clear`，值一律字符串 |
| `Blob` / `File` | 二进制数据容器 / 带元数据的 Blob | `new Blob(parts, { type })`；`blob.text()/arrayBuffer()/stream()` |
| `structuredClone` | 深拷贝（支持循环引用、Date/Map/Set） | `structuredClone(value, { transfer? })` |
| `BroadcastChannel` | 同源跨标签页广播 | `new BroadcastChannel(name)`；`postMessage/onmessage` |

## 💡 示例

### fetch + AbortController：取消与超时（两种标准写法）

```ts
// 写法一：手动取消（如组件卸载时）
const controller = new AbortController()
fetch('/api/search?q=ts', { signal: controller.signal })
  .then((res) => res.json())
  .catch((err) => {
    if (err.name === 'AbortError') return // 主动取消不算错误，静默处理
    throw err
  })
controller.abort()

// 写法二：超时自动取消（现代标准 API）
const res = await fetch('/api/slow', { signal: AbortSignal.timeout(5000) })
```

### fetch：必须手动检查 HTTP 状态（404 不 reject！）

```ts
const res = await fetch('/api/posts/1')
if (!res.ok) {
  // res.ok = status 在 200-299；404/500 都会走这里
  throw new Error(`请求失败：${res.status}`)
}
const data = await res.json()
```

### URL / URLSearchParams：别再手拼查询串

```ts
const url = new URL('/v1/posts', 'https://api.example.com')
url.searchParams.set('q', 'héllo wörld')   // 自动 URL 编码
url.searchParams.set('page', '3')
console.log(url.href)                       // https://api.example.com/v1/posts?q=h%C3%A9llo+w%C3%B6rld&page=3
console.log(url.searchParams.get('q'))      // 'héllo wörld'（自动解码）
```

### FormData + Blob/File：文件上传

```ts
const fd = new FormData()
fd.append('name', 'dev')
const file = new File([new Blob(['hello'])], 'a.txt', { type: 'text/plain' })
fd.append('file', file)
await fetch('/api/upload', { method: 'POST', body: fd })
// 注意：用 FormData 时不要手动设 Content-Type，浏览器自动带 multipart 边界
```

### localStorage：带 JSON 序列化的安全读写

```ts
function loadDraft(key: string): unknown | null {
  if (typeof window === 'undefined') return null // SSR 保护
  const raw = window.localStorage.getItem(key)
  if (raw == null) return null
  try { return JSON.parse(raw) } catch { return null }
}
window.localStorage.setItem('draft', JSON.stringify({ text: 'hi' }))
```

### structuredClone：真正的深拷贝

```ts
const orig = { d: new Date(), m: new Map([['k', 1]]), nested: { a: [1, [2]] } }
const copy = structuredClone(orig)
copy.nested.a[1] !== orig.nested.a[1]  // true —— 逐层复制
copy.d instanceof Date                  // true —— Date/Map/Set 类型保留
structuredClone({ fn: () => {} })       // 抛 DataCloneError —— 函数/DOM 节点不可克隆
```

### BroadcastChannel：跨标签页同步（如登出广播）

```ts
const channel = new BroadcastChannel('auth')
channel.onmessage = (e) => {
  if (e.data.type === 'logout') location.reload() // 其他标签页收到登出通知
}
channel.postMessage({ type: 'logout' })  // 广播给所有同源、同 name 的标签页
```

## ⚠️ 常见陷阱

- ❌ **以为 fetch 在 404/500 时 reject**：`fetch` 只在网络层失败（断网、DNS、CORS 拦截）时 reject；HTTP 错误状态会正常 resolve——`await fetch(...)` 后不检查 `res.ok` 就 `.json()`，错误响应体被当成功数据。✅ 每次请求后先 `if (!res.ok) throw ...` 或封装统一请求函数。
- ❌ **忘接 `AbortSignal` 导致请求无法取消**：快速切换筛选条件时旧请求后返回覆盖新结果（race condition）。✅ 每次 useEffect 发请求创建 `AbortController`，清理函数里 `abort()`；或直接用 `AbortSignal.timeout(ms)` 限超时。
- ❌ **手拼查询串不编码**：`'/search?q=' + keyword` 遇到 `&`、`+`、中文直接坏。✅ 一律用 `new URL(...)` 或 `new URLSearchParams(...)` 生成。
- ❌ **服务端代码里调 `localStorage`/`window`**：Server Component / route handler / `next build` 预渲染阶段没有 `window`，直接引用即抛 `ReferenceError`。✅ 客户端组件内使用；确需顶层判断时用 `typeof window === 'undefined'` 守卫。
- ❌ **给 localStorage 存对象没序列化**：值会被强转成 `"[object Object]"`；读取不判空直接 `JSON.parse` 有两种坑——空串/`undefined` 抛 SyntaxError，而 `null` 静默返回 `null` 不抛，两种情形都需防御。✅ 写入 `JSON.stringify`，读取 `try/catch` + 判空；敏感信息不要进 localStorage（XSS 可读）。
- ❌ **用 `JSON.parse(JSON.stringify(obj))` 深拷贝**：`Date` 变字符串、`Map/Set` 变空对象、`undefined` 字段丢失、循环引用直接抛错。✅ 用 `structuredClone`（函数与 DOM 节点仍不可克隆，需自行处理）。
- ❌ **手设 FormData 的 `Content-Type`**：手动写 `multipart/form-data` 会丢失 boundary，服务端解析失败。✅ 交给浏览器自动生成，什么都不写。
- ❌ **在 Server Component 里 new BroadcastChannel**：它是浏览器跨标签页机制；Node 里虽有同名构造器，语义完全不同。✅ 只在客户端组件/事件处理器中使用，并做 SSR 守卫。

## 🔗 相关条目

- [JavaScript 核心语义](./09-js-core-semantics.md) —— 事件循环：fetch 回调与定时器的排队规则
- [现代 JavaScript 语法速查](./04-javascript-modern.md) —— Promise/async-await 基础
- [数据获取模式](../framework-patterns/04-data-fetching-patterns.md) —— Next.js 场景下 fetch 的缓存与重验证
- [异步请求 APIs](../framework-patterns/09-async-request-apis.md) —— 服务端读取请求参数的正确方式
- 🌐 **[MDN: fetch()](https://developer.mozilla.org/zh-CN/docs/Web/API/fetch)** —— 官方语义（含"HTTP 错误不 reject"）

---
*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
