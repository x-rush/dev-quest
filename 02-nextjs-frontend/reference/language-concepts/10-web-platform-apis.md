# Web 平台 API 速查（fetch / URL / FormData / Storage / Blob / structuredClone / BroadcastChannel）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `language-concepts`

## 📌 定义

本页介绍不依赖 React、Next.js 的 Web 标准 API。JavaScript 语言标准的 Array、Map、Promise 等内置能力见[共享内置参考](../../../shared-resources/javascript-builtins.md)；TypeScript 的类型工具在编译后通常被擦除，不是额外的运行时标准库。URL、fetch、DOM、存储来自宿主平台，必须分别检查运行环境；Node 的同名 API 不意味着拥有浏览器的 Cookie、DOM 或同源策略。前置：Promise、异常、JSON。学完应能区分 HTTP 失败、结构错误、取消，以及服务端执行与浏览器副作用。

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
// 浏览器集成片段：错误由调用者 await/catch，避免遗留 rejected Promise。
async function search(signal: AbortSignal): Promise<unknown> {
  const response = await fetch('/api/search?q=ts', { signal })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json() // JSON 解析后还需按业务结构校验
}
const controller = new AbortController()
const result = search(controller.signal)
controller.abort()
try {
  await result
} catch (error) {
  if (controller.signal.aborted && error === controller.signal.reason) {
    console.log('请求已取消')
  } else {
    console.error('搜索失败', error)
  }
}
// 需要超时时，可由调用者改传 AbortSignal.timeout(5000)。
// timeout/any 等 API 的可用性要根据目标浏览器或 Node 版本检查。
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

### localStorage：读写失败与数据损坏必须可区分

```ts
// 浏览器集成片段；应从 effect 或事件中调用。
type DraftResult =
  | { status: 'ready'; text: string }
  | { status: 'missing' | 'unavailable' | 'invalid' }

function loadDraft(key: string): DraftResult {
  if (typeof window === 'undefined') return { status: 'unavailable' }
  let raw: string | null
  try { raw = window.localStorage.getItem(key) }
  catch { return { status: 'unavailable' } }
  if (raw === null) return { status: 'missing' }
  try {
    const value: unknown = JSON.parse(raw)
    if (typeof value !== 'object' || value === null ||
        !('text' in value) || typeof value.text !== 'string') {
      return { status: 'invalid' }
    }
    return { status: 'ready', text: value.text }
  } catch { return { status: 'invalid' } }
}
function saveDraft(key: string, text: string): boolean {
  if (typeof window === 'undefined') return false
  try {
    window.localStorage.setItem(key, JSON.stringify({ text }))
    return true
  } catch { return false } // UI 应显示保存失败，而不是清空编辑器
}
```

这两个函数只负责存储边界。组件应根据结果展示“无草稿”“草稿损坏”“存储不可用”，而不是把它们都当作成功读取了空文本。存储可因用户策略或额度抛错，写入同样需要处理；本地明文存储不适合保存会话密钥。

### structuredClone：复制受支持的数据，不复制任意对象行为

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
    if (e.data && typeof e.data === 'object' && e.data.type === 'logout') {
      location.reload() // 提示其他标签页刷新；服务端仍须验证身份
    }
}
channel.postMessage({ type: 'logout' })  // 广播给同源同存储分区、同 name 的其他 channel；不是向发送对象自身回送
// 组件卸载或监听不再需要时调用 channel.close()，释放资源。
```

## ⚠️ 常见陷阱

- ❌ **以为 fetch 在 404/500 时 reject**：`fetch` 会因网络失败、取消、无效请求参数等原因 reject；HTTP 错误状态会正常 resolve——`await fetch(...)` 后不检查 `res.ok` 就 `.json()`，错误响应体被当成功数据。✅ 每次请求后先 `if (!res.ok) throw ...` 或封装统一请求函数。
- ❌ **忘接 `AbortSignal` 导致请求无法取消**：快速切换筛选条件时旧请求后返回覆盖新结果（race condition）。✅ 每次 useEffect 发请求创建 `AbortController`，清理函数里 `abort()`；或直接用 `AbortSignal.timeout(ms)` 限超时。
- ❌ **手拼查询串不编码**：`'/search?q=' + keyword` 遇到 `&`、`+`、中文直接坏。✅ 一律用 `new URL(...)` 或 `new URLSearchParams(...)` 生成。
- ❌ **服务端代码里调 `localStorage`/`window`**：Server Component / route handler / `next build` 预渲染阶段没有 `window`，直接引用即抛 `ReferenceError`。✅ 客户端组件的 effect 或事件中使用，因为客户端组件也可能预渲染；环境判断用 `typeof window === 'undefined'` 守卫。
- ❌ **给 localStorage 存对象没序列化**：值会被强转成 `"[object Object]"`；读取不判空直接 `JSON.parse` 有两种坑——空串/`undefined` 抛 SyntaxError，而 `null` 静默返回 `null` 不抛，两种情形都需防御。✅ 写入 `JSON.stringify`，读取 `try/catch` + 判空；敏感信息不要进 localStorage（XSS 可读）。
- ❌ **用 `JSON.parse(JSON.stringify(obj))` 深拷贝**：`Date` 变字符串、`Map/Set` 变空对象、`undefined` 字段丢失、循环引用直接抛错。✅ 用 `structuredClone`（函数与 DOM 节点仍不可克隆，需自行处理）。
- ❌ **手设 FormData 的 `Content-Type`**：手动写 `multipart/form-data` 会丢失 boundary，服务端解析失败。✅ 交给浏览器自动生成，什么都不写。
- ❌ **在 Server Component 里 new BroadcastChannel**：它是浏览器跨标签页机制；Node 里虽有同名构造器，语义完全不同。✅ 只在客户端组件/事件处理器中使用，并做 SSR 守卫。

<!-- full-library-explanation -->
## 同名 API 仍要检查运行环境和生命周期

前置是 Promise、组件副作用和请求响应。fetch、URL、FormData、Blob、structuredClone 在现代 Node 中也有实现；浏览器的 origin、Cookie、DOM 表单和存储分区却不能直接搬到服务端。服务器 fetch 常需绝对 URL，也不会自动代替用户转发浏览器会话。

取消只表达调用方不再等待或继续读取，不保证服务器没有执行写操作。提交订单超时后应查询状态或用幂等键重试，不能简单认定创建失败。Response 的正文通常只能消费一次，先 json 再 text 会失败；需要两份消费时事先 clone，并注意缓冲成本。

**练习**：用两个同源标签页广播普通消息，确认发送该消息的 channel 对象不会收到自己的广播，关闭页面组件时调用 close。测试浏览器禁止存储和额度耗尽，读取与写入都要处理异常。structuredClone 能复制多种内建数据，但不会完整保留自定义类原型与属性描述符；以类方法是否仍存在验证这一边界。

依据：[Node 全局 API](https://nodejs.org/api/globals.html)、[HTML 结构化克隆与广播](https://html.spec.whatwg.org/multipage/structured-data.html)。

## 无外部服务的完整实验

以下围栏可分别保存为 `.mjs`，用 Node 24 运行。它们验证 Node 实现的标准对象和解析行为；不替代浏览器 Cookie、CORS、DOM 表单或存储权限验证。

### URL 与表单的重复键不会自动变数组

保存为 `url-form.mjs`，预期四行：`a+b & 中`、`js,ts`、`2`、`3`。URLSearchParams 和 FormData 都可保存同名多值；`get` 只取首个值，`getAll` 才返回全部值。FormData 不自动验证类型或业务规则；数字 append 后成为字符串。

<!-- foundation-case: url-form -->
```js
const url = new URL('/search', 'https://example.com');
url.searchParams.set('q', 'a+b & 中');
url.searchParams.append('tag', 'js');
url.searchParams.append('tag', 'ts');
const restored = new URL(url.href);
console.log(restored.searchParams.get('q'));
console.log(restored.searchParams.getAll('tag').join(','));
const form = new FormData();
form.append('quantity', '2');
form.append('quantity', '3');
console.log(form.get('quantity'));
form.set('quantity', '3');
console.log(form.getAll('quantity').join(','));
```

根据 [URL 标准](https://url.spec.whatwg.org/)，参数值应交给 URLSearchParams 序列化。不要先 encodeURIComponent 再传给 set，否则 `%` 会被再次编码；不要把 URL 路径片段和查询参数混用同一套拼接逻辑。

### HTTP 成功、JSON 有效和业务结构正确是三次检查

保存为 `response-contract.mjs`，预期四行：`Learn`、`Error:HTTP 404`、`TypeError:invalid task`、`TypeError`。本例创建 Response 对象以隔离解析契约，无需启动服务器；真实请求时把 `await fetch(...)` 得到的 Response 交给相同函数。

<!-- foundation-case: response-contract -->
```js
async function readTask(response) {
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const value = await response.json();
  if (typeof value !== 'object' || value === null ||
      !Number.isSafeInteger(value.id) || value.id <= 0 ||
      typeof value.title !== 'string' || value.title.trim() === '') {
    throw new TypeError('invalid task');
  }
  return { id: value.id, title: value.title.trim() };
}
const cases = [
  Response.json({ id: 1, title: ' Learn ' }),
  Response.json({ message: 'missing' }, { status: 404 }),
  Response.json({ id: '1', title: 'Learn' }),
];
for (const response of cases) {
  try { console.log((await readTask(response)).title); }
  catch (error) { console.log(`${error.name}:${error.message}`); }
}
const once = Response.json({ id: 1 });
await once.json();
try { await once.text(); }
catch (error) { console.log(error.name); }
```

Response 正文通常只能消费一次；先 json 再 text 会失败。事先 clone 可以取得第二条消费路径，但会带来缓冲成本。204 等无正文响应不应该无条件调用 json。fetch 的具体请求、响应和 body 契约见 [Fetch 标准](https://fetch.spec.whatwg.org/)。

### 克隆对象与转移二进制资源是不同操作

保存为 `clone.mjs`，预期四行：`1`、`true`、`0,3`、`DataCloneError`。

<!-- foundation-case: clone -->
```js
const original = { tags: new Set(['js']), nested: { value: 1 } };
original.self = original;
const copy = structuredClone(original);
copy.nested.value = 2;
console.log(original.nested.value);
console.log(copy.self === copy && copy.tags.has('js'));
const bytes = new Uint8Array([1, 2, 3]);
const moved = structuredClone(bytes, { transfer: [bytes.buffer] });
console.log([bytes.byteLength, moved.byteLength].join(','));
try { structuredClone({ action() {} }); }
catch (error) { console.log(error.name); }
```

transfer 将可转移资源移交给新对象，原 ArrayBuffer 脱离，不能再当原数据继续使用。普通 clone 则保留原数据；两种方式都不复制函数、自定义类行为或任意属性描述符。依据：[HTML 结构化数据](https://html.spec.whatwg.org/multipage/structured-data.html)。

## 从实验到页面的验收

1. 响应测试再加入无效 JSON、204 和 500，分别说明失败在哪一层；不要让错误响应进入成功渲染。
2. 页面切换时取消旧请求，并验证旧响应即使晚到也不能覆盖新页面；取消不保证服务器尚未处理写操作。
3. 用两个同源标签页验证 BroadcastChannel，并在组件移除时 close；确认广播没有被当作认证授权的依据。
4. 浏览器禁止存储或写入失败时，编辑器仍保留未保存文本，并显示失败状态。Server Component 不读取 window；Client Component 的初次预渲染同样需要遵守这个边界。

## 🔗 相关条目

- [JavaScript 核心语义](./09-js-core-semantics.md) —— 事件循环：fetch 回调与定时器的排队规则
- [现代 JavaScript 语法速查](./04-javascript-modern.md) —— Promise/async-await 基础
- [数据获取模式](../framework-patterns/04-data-fetching-patterns.md) —— Next.js 场景下 fetch 的缓存与重验证
- [异步请求 APIs](../framework-patterns/09-async-request-apis.md) —— 服务端读取请求参数的正确方式
- 🌐 **[MDN: fetch()](https://developer.mozilla.org/zh-CN/docs/Web/API/fetch)** —— 官方语义（含"HTTP 错误不 reject"）

---
*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
