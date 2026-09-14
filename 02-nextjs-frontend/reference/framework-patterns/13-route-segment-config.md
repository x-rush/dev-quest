# 路由段配置（Route Segment Config）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（无难度门槛）
> **分类**: `framework-patterns`

## 📌 定义

路由段配置是从 `page.tsx`/`layout.tsx`/`route.ts` 直接 `export const` 的常量，用来声明该段的渲染与缓存行为（`dynamic`、`revalidate`、`fetchCache` 等）。**它们属于 Next.js 16 之前的"隐式缓存模型"**：未启用 `cacheComponents` 时仍可用（官方文档已将其移入"Caching and Revalidating (Previous Model)"指南）；而启用 Cache Components（`cacheComponents: true`，16 的缓存新方向）后，`dynamic`/`dynamicParams`/`revalidate`/`fetchCache` 四项**被移除**，缓存一律改由 `"use cache"` 显式声明。运行环境类配置（`runtime`、`dynamicParams`、`maxDuration`）不受此影响。

## 📖 语法/签名

### 与缓存无关、始终可用的段配置（Next.js 16.3 官方文档）

| 选项 | 类型 | 默认 | 语义 |
|------|------|------|------|
| `dynamicParams` | `boolean` | `true` | 配合 `generateStaticParams`：未预生成的动态段参数，`true` 按需动态渲染，`false` 直接 404 |
| `runtime` | `'nodejs' \| 'edge'` | `'nodejs'` | 段的运行时；**`'edge'` 已弃用** |
| `preferredRegion` | `'auto' \| 'global' \| 'home' \| string \| string[]` | `'auto'` | 部署区域偏好；**已弃用** |
| `maxDuration` | `number`（秒） | 由部署平台设定 | 服务端执行最大时长（serverless 超时上限） |
| `instant` / `prefetch` | — | — | 16 新增段配置，见官方 API 参考 |

### 旧缓存模型段配置（未启用 cacheComponents 时；启用后此四项被移除）

| 选项 | 取值 | 默认 | 语义 |
|------|------|------|------|
| `dynamic` | `'auto'` | `'auto'` | 尽可能缓存，不阻止组件选择动态行为 |
| | `'force-dynamic'` | | 强制每请求动态渲染，等效于所有 fetch `cache: 'no-store'` + `revalidate: 0` + `fetchCache = 'force-no-store'` |
| | `'error'` | | 强制预渲染：任何组件用了请求时 API 或未缓存数据即报错（等效 pages 时代的 `getStaticProps`） |
| | `'force-static'` | | 强制静态：`cookies()`/`headers()`/`useSearchParams()` 返回空值 |
| `revalidate` | `false` | `false` | 语义≈`Infinity`：fetch 缓存不过期（个别 fetch 仍可自行绕过） |
| | `0` | | 该段始终动态渲染 |
| | `number`（秒） | | 该段默认重验证周期；**取全路由最小值**；必须静态可分析（`600` 合法，`60 * 10` 不合法）；开发模式永远按需渲染 |
| `fetchCache` | `'auto'` 等 7 值：`'default-cache'`/`'only-cache'`/`'force-cache'`/`'default-no-store'`/`'only-no-store'`/`'force-no-store'` | `'auto'` | 统一覆盖段内所有 fetch 的默认缓存行为；同一路由内各段取值须兼容（`'only-cache'` 与 `'only-no-store'` 同路不允许） |

## 💡 示例

### 旧模型：整页 ISR + 精细控制

```tsx
// app/products/page.tsx（未启用 cacheComponents）
export const revalidate = 3600        // 每小时重验证
export const dynamicParams = true     // generateStaticParams 之外的参数按需渲染

export default async function ProductsPage() {
  const products = await fetch('https://api.acme.com/products', {
    cache: 'force-cache',             // 与段配置配合
  }).then((r) => r.json())
  return <ProductList products={products} />
}
```

### 运行环境：serverless 超时上限

```tsx
// app/generate-report/route.ts
export const runtime = 'nodejs'   // 默认值；'edge' 已弃用
export const maxDuration = 60     // 长任务显式放宽执行时长（上限由平台决定）
```

### 新模型：同样的意图改用 "use cache"

```tsx
// 启用 cacheComponents: true 后，上面的旧模型写法改为：
import { cacheLife } from 'next/cache'

export default async function ProductsPage() {
  'use cache'
  cacheLife('hours')               // 取代 export const revalidate = 3600
  const products = await fetch('https://api.acme.com/products').then((r) => r.json())
  return <ProductList products={products} />
}
```

## ⚠️ 常见陷阱

- ❌ **启用 `cacheComponents: true` 后还写 `dynamic`/`revalidate`/`fetchCache`/`dynamicParams`**：Next.js 16.0 官方版本历史明确这四项在 Cache Components 启用时**被移除**，构建报错。✅ 缓存意图全部改写为 `"use cache"` + `cacheLife`/`cacheTag`（见 [Cache Components 与 "use cache" 指令](./08-caching-patterns.md)）。
- ❌ **以为 `revalidate = 60 * 10` 没问题**：段配置值必须静态可分析，表达式直接报错。✅ 写字面量 `600`。
- ❌ **以为子段设大 `revalidate` 就能用大周期**：全路由按**最小值**生效——父 layout 的 `revalidate = 60` 会让子页面的 `3600` 失效为 60。✅ 调周期时把整条路由链的段配置一起检查。
- ❌ **同一路由混用不兼容的 `fetchCache`**：`'only-cache'` + `'only-no-store'`、`'force-cache'` + `'force-no-store'` 都会报错；父段 `'default-no-store'` 与子段 `'auto'`/`'*-cache'` 也不允许。✅ 共享父 layout 保持 `'auto'`，在分歧的子段定制。
- ❌ **继续给新段选 `runtime = 'edge'`**：官方文档已标记弃用（且 `revalidate` 在 edge 运行时不可用）。✅ 默认 `'nodejs'`；确有边缘需求关注官方后续替代方案。
- ❌ **把段配置当新缓存模型的开关学**：这组常量是过渡期工具，16 的学习重点是 `"use cache"` 编程模型。✅ 新项目直接启用 `cacheComponents`，旧代码迁移时再对照本条目查语义。

## 🔗 相关条目

- [Cache Components 与 "use cache" 指令](./08-caching-patterns.md) —— 新缓存模型的正解，与本条目互为新旧对照
- [异步请求 APIs](./09-async-request-apis.md) —— 请求时 API 如何让 `dynamic = 'auto'` 走向动态渲染
- [数据获取模式](./04-data-fetching-patterns.md) —— fetch 级 `cache`/`next.revalidate` 与段配置的配合
- [环境变量](./14-env-vars.md) —— 构建期内联与运行时读取的边界
- 🌐 **[官方文档：Route Segment Config](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config)** · **[官方文档：旧缓存模型指南](https://nextjs.org/docs/app/guides/caching-without-cache-components)**（本条目语义截至 Next.js 16.3 官方文档）

---
*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
