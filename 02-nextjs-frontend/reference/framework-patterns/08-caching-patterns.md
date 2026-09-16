# Cache Components 与 "use cache" 指令

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（无难度门槛）
> **分类**: `framework-patterns`

## 📌 定义

Cache Components 是 Next.js 16 引入的显式缓存编程模型，核心是 `"use cache"` 指令：在函数、组件或页面级声明缓存意图，由编译器自动生成缓存键。启用后（`cacheComponents: true`），所有动态代码默认在请求时执行，缓存完全变为**选择性行为（opt-in）**，取代了 App Router 早期"默认缓存 + 手动绕过"的隐式模型。实验性的 Partial Prerendering（PPR）也已并入该模型：使用 `"use cache"` 的部分构成静态外壳，访问请求时 API 的部分成为流式注入的动态空洞。

## 📖 语法/签名

```typescript
// next.config.ts —— 开启 Cache Components
const nextConfig: NextConfig = {
  cacheComponents: true,
};
```

```typescript
// 函数级缓存
import { cacheLife, cacheTag } from 'next/cache';

async function getPosts() {
  'use cache'
  cacheLife('hours');            // 缓存时长 profile：seconds/minutes/hours/days/max 或自定义
  cacheTag('posts');             // 缓存标签，用于按需失效
  return db.post.findMany();
}
```

相关 API：

| API | 签名 | 用途 |
|-----|------|------|
| `"use cache"` | 指令，置于函数体首行 | 声明该函数/组件/页面可缓存 |
| `cacheLife(profile)` | `cacheLife(profile: string)` | 指定缓存时长 profile |
| `cacheTag(...tags)` | `cacheTag(...tags: string[])` | 打标签，配合失效 API 使用 |
| `revalidateTag(tag, profile)` | 第二参数为 `cacheLife` profile | 服务端按标签失效（stale-while-revalidate） |
| `updateTag(tag)` | 仅限 Server Actions | 写后读（read-your-owns-writes）一致性失效 |
| `refresh()` | 仅限 Server Actions | 刷新当前页面所有未缓存数据 |

## 💡 示例

```tsx
// app/blog/page.tsx —— 页面级缓存
export default async function BlogPage() {
  'use cache'
  cacheLife('days')

  const posts = await getPosts()
  return <PostList posts={posts} />
}

// Server Action 中：写入后立即看到新数据
'use server'

export async function createPost(formData: FormData) {
  await db.post.create({ data: { title: formData.get('title') as string } })
  updateTag('posts') // 写后读：让本请求立即反映新写入
}
```

## ⚠️ 常见陷阱

- `"use cache"` 必须是函数体第一条语句，且只能用于服务端（Server Components、Server Actions、route handler）
- 缓存函数的参数与返回值必须可序列化；传入 Date/Map 等非序列化类型会静默出错或报错
- 忘记 `cacheTag` 会导致数据无法精准失效，只能整体过期
- Next.js 16 中 `revalidateTag(tag)` 单参数调用已被弃用，必须传 `cacheLife` profile 作为第二参数
- `unstable_cache` 官方已标记为**不推荐新项目使用**（16.3 中仍可导入，但生态方向是 `"use cache"` 模型，新代码直接采用后者）；Next.js 16 已**移除** experimental PPR 标志与 `experimental_ppr` 段配置，如需 PPR 语义请关注后续版本的 `"use cache"` 生态
- 旧的隐式缓存（`fetch` 默认缓存、路由段默认静态）在 16 中不再存在，升级后页面可能"突然变动态"，应主动为热点页面补上 `"use cache"`

## 模式不变量

- **缓存是显式契约而非默认行为**：缓存意图必须逐处显式声明、缓存键由声明处的输入推导，未声明即按请求时执行（对照 `"use cache"` 指令与 `cacheComponents` 开关的 opt-in 模型）。
- **缓存边界归服务端所有**：缓存声明只存在于服务端语境（Server Components / Server Actions / route handler），客户端只消费缓存结果而不参与失效决策（对照 `"use cache"` 的适用范围限制）。
- **可缓存的必须可失效**：缓存条目必须携带失效标识才能被精准作废，否则只能等待整体过期（对照 `cacheTag` 配合 `revalidateTag` / `updateTag` 的按需失效）。
- **进入缓存边界的数据必须可序列化**：参数与返回值以可序列化为前提，非序列化类型无法跨越缓存边界（对照 "use cache" 的序列化陷阱）。
- **写后读一致性由写入方负责**：写操作完成后的读取一致性由写入动作显式触发失效或刷新，而非被动等待缓存过期（对照 Server Actions 中的 `updateTag` / `refresh`）。

## 🔗 相关条目

- [异步请求 APIs](./09-async-request-apis.md) —— 动态数据如何以请求时执行方式接入
- [数据获取模式](./04-data-fetching-patterns.md)
- [服务端组件模式](./02-server-components-patterns.md)
- [Next.js API 参考](../language-concepts/02-nextjs-api-reference.md)
