# Metadata API 与 next/script

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `framework-patterns`

## 📌 定义

两条"往 HTML 里注入东西"的官方通道：**Metadata API**（`export const metadata` 对象 / `generateMetadata` 函数）让 Next.js 在服务端渲染 `<title>`、`<meta>`、favicon、OG 标签，代替手写 `<head>`；**`next/script` 组件**用 `strategy` 三档加载策略（`beforeInteractive` / `afterInteractive` / `lazyOnload`）优化第三方脚本（统计、客服、Cookie 弹窗），避免第三方 JS 拖垮水合。Metadata 导出仅用于服务端组件；Script 可出现在客户端组件，事件回调需要客户端语境，行为随 Next.js 16.3 官方文档核实。

## 📖 语法/签名

### Metadata API

```tsx
// 静态元数据：layout.tsx / page.tsx（仅 Server Component）中导出
import type { Metadata } from 'next'

export const metadata: Metadata = {
  metadataBase: new URL('https://acme.com'),  // 相对 URL 字段的前缀，通常只在根 layout 设一次
  title: { default: 'Acme', template: '%s | Acme' },
  description: '...',
  icons: { icon: '/icon.png' },
  openGraph: { title: 'Acme', images: ['/og.png'] },
  robots: { index: true, follow: true },
}

// 动态元数据：函数形式，params/searchParams 是 Promise
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const post = await getPost(slug)
  return { title: post.title, openGraph: { images: [post.cover] } }
}
```

| 字段/形态 | 说明 |
|-----------|------|
| `title.template` | `'%s \| Acme'` 只作用于**子段**；配 template 必须同时给 `title.default`；写在 page.js 无效（页面是末段） |
| `metadataBase` | URL 类字段的基准前缀；字段给了绝对 URL 则被忽略；**相对路径而未设 metadataBase 会构建报错** |
| `openGraph` / `robots` | 嵌套对象，参与**浅合并**（见陷阱） |
| `viewport`/`themeColor` | 已移入 `generateViewport`（v14 起），不再写在 metadata 里 |
| 合并顺序 | 从根 layout 到最终 page 逐段求值，**同键后段覆盖前段（浅合并）** |

### next/script 加载策略

```tsx
import Script from 'next/script'

<Script src="https://example.com/script.js" strategy="..." />
```

| strategy | 语义 | 典型用途 |
|----------|------|----------|
| `beforeInteractive` | 随初始 HTML 下发，先于任何 Next.js 模块加载；**必须放在根 layout**；加载不阻塞水合；无论写在何处都注入 `<head>` | 机器人检测、Cookie 同意管理 |
| `afterInteractive`（默认） | 部分水合后在客户端注入加载；任意 page/layout 均可放 | 标签管理器、统计脚本 |
| `lazyOnload` | 浏览器空闲时、页面资源全部取完后加载 | 客服插件、社交挂件 |

## 💡 示例

### 根布局 + 子页的元数据组合

```tsx
// app/layout.tsx —— 根段
export const metadata: Metadata = {
  metadataBase: new URL('https://acme.com'),
  title: { default: 'Acme', template: '%s | Acme' },
  openGraph: { title: 'Acme', description: 'Acme is the...' },
}

// app/blog/[slug]/page.tsx —— 末段
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = await getPost(slug)
  return {
    title: post.title,                    // 实际渲染 "文章标题 | Acme"（template 作用于子段）
    openGraph: { title: post.title, description: post.excerpt, images: [post.cover] },
    // 相对路径 post.cover 由 metadataBase 拼成完整 URL
  }
}
```

### next/script 三档策略实战

```tsx
// app/layout.tsx —— 关键脚本：根 layout + beforeInteractive
import Script from 'next/script'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        {children}
        <Script src="https://static.acme.com/consent.js" strategy="beforeInteractive" />
      </body>
    </html>
  )
}
```

```tsx
// app/dashboard/page.tsx —— 统计脚本：默认 afterInteractive；低优先级用 lazyOnload
'use client'
import Script from 'next/script'
export default function Dashboard() {
  return (
    <>
      <Script src="https://analytics.example.com/t.js" strategy="afterInteractive" />
      <Script src="https://chat.example.com/widget.js" strategy="lazyOnload" onReady={() => {}} />
    </>
  )
}
```

## ⚠️ 常见陷阱

- ❌ **以为 metadata 深合并**：多段之间是**浅合并**——子段写了自己的 `openGraph`，父段的 `openGraph.description`/`images` 整个被覆盖（官方文档明确 "Duplicate keys are replaced"）。✅ 子段需要继承时把父段字段重新展开：`openGraph: { ...parentOpenGraph, title: post.title }`。
- ❌ **在客户端组件里 export metadata / 调 generateMetadata**：`metadata` 导出与 `generateMetadata` 仅 Server Component 支持（元数据由服务端生成，动态元数据可流式追加）。✅ page.tsx 保持服务端，客户端逻辑拆成子组件再 `'use client'`。
- ❌ **OG 图片用相对路径却没设 `metadataBase`**：直接构建报错。✅ 根 layout 里设 `metadataBase: new URL('https://你的域名')`；另外启用 `'use cache'` 的 `generateMetadata` 返回值必须可序列化，`URL` 实例不支持，返回 `url.toString()` 字符串。
- ❌ **把 `beforeInteractive` 脚本写在子页面**：该策略必须放在**根 layout**（`app/layout.tsx`），且每次文档加载只执行一次——客户端导航不会重跑。✅ 全站关键脚本（合规、检测类）进根 layout；页面级脚本用默认 `afterInteractive`。
- ❌ **给 `beforeInteractive` 配 `onLoad`/`onError`**：官方明确不支持该组合。✅ 用 `onReady`（脚本加载完成且每次组件挂载后触发）。
- ❌ **在 Server Component 里用 `onLoad`/`onReady`/`onError`**：这三个回调只在客户端组件可用。✅ 放脚本的页面打 `'use client'`，或把 Script 抽进客户端子组件。
- ❌ **启用 Cache Components 后还在页面级用请求时数据渲染 metadata 却不缓存**：`generateMetadata` 访问 `cookies()`/`headers()`/未缓存数据时会推迟到请求时执行（与组件同一规则）。✅ 静态可预渲染的页面让 `generateMetadata` 保持无动态行为，或对数据用 `'use cache'`（见 [Cache Components 与 "use cache" 指令](./08-caching-patterns.md)）。

## 模式不变量

- **元数据是服务端渲染产物**：进入 HTML 头部的信息由服务端生成，是否包含在初始 HTML 取决于渲染与爬虫处理策略，因此只能由服务端组件定义（对照 `metadata` / `generateMetadata` 仅 Server Component 可用的约束）。
- **跨层级配置的合并是显式契约而非直觉继承**：配置从根到叶逐段求值、同名键整体替换，需要继承的字段必须显式展开，而不是假设深层结构自动合并（对照 `openGraph` 浅合并陷阱、`title.template` 只作用于子段）。
- **第三方脚本的加载时机按其对用户的关键度分档**：外部代码的注入时机分为"先于交互 / 交互后 / 空闲时"三档，排布原则是用户优先于第三方（对照 `beforeInteractive` / `afterInteractive` / `lazyOnload` 三档策略）。
- **文档级一次性资源与页面级资源作用域不同**：每文档生命周期只执行一次的脚本属于根布局作用域，随页面挂载的脚本属于页面作用域，客户端导航不重跑前者（对照 `beforeInteractive` 必须放根 layout 的陷阱）。
- **依赖浏览器事件时机的逻辑必须位于水合后的客户端语境**：脚本的加载/就绪/失败回调只能在客户端组件中挂载（对照 `onLoad`/`onReady`/`onError` 仅客户端可用的陷阱）。

<!-- full-library-explanation -->
## 验证最终 HTML 与脚本行为，而不只看配置对象

前置是服务端组件、HTML head 与客户端导航。同一个路由文件不能同时导出 metadata 和 generateMetadata，开头的两种写法应二选一。父子 openGraph 对象是浅合并，需要保留父级图片时显式读取并组合父级结果。

元数据在服务器生成，但不一定全部阻塞首屏：支持流式元数据时可随后追加；对只能读取 HTML 的爬虫会采用不同策略。因此用浏览器 DOM、初始响应和目标爬虫的抓取结果分别检查，不能只看 View Source 就判断完全缺失。robots noindex 是给爬虫的指令，不是访问控制。

**练习**：父布局设品牌标题、描述与图片，子页只覆写 openGraph.title，观察哪些父字段被覆盖，再显式合并修正。来回导航两次，验证统计脚本与事件订阅不会重复初始化；onReady 可在挂载时再次触发，第三方初始化需幂等并清理自建监听器。加载脚本的策略不等于用户同意策略，需按产品要求决定何时真正启用统计。

依据：[Metadata](https://nextjs.org/docs/app/api-reference/functions/generate-metadata)、[Script](https://nextjs.org/docs/app/api-reference/components/script)。

## 🔗 相关条目

- [Cache Components 与 "use cache" 指令](./08-caching-patterns.md) —— `generateMetadata` 的缓存模型
- [异步请求 APIs](./09-async-request-apis.md) —— `generateMetadata` 中 `await params` 的由来
- [App Router 实战模式](./01-app-router-patterns.md) —— layout/page 分层结构
- [性能优化：渲染优化](../performance-optimization/01-rendering-optimization.md) —— 第三方脚本对水合的影响
- 🌐 **[官方文档：generateMetadata](https://nextjs.org/docs/app/api-reference/functions/generate-metadata)** · **[官方文档：Script 组件](https://nextjs.org/docs/app/api-reference/components/script)**（本条目行为截至 Next.js 16.3 官方文档）

---
*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
