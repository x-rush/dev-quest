# Cache Components 与 "use cache" 指令

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `framework-patterns`

## 📌 定义

Cache Components 是 Next.js 16 引入的显式缓存编程模型，核心是 `"use cache"` 指令：在函数、组件或页面级声明缓存意图，由编译器自动生成缓存键。启用后（`cacheComponents: true`），所有动态代码默认在请求时执行，缓存完全变为**选择性行为（opt-in）**，取代了 App Router 早期"默认缓存 + 手动绕过"的隐式模型。实验性的 Partial Prerendering（PPR）也已并入该模型：使用 `"use cache"` 的部分构成静态外壳，访问请求时 API 的部分成为流式注入的动态空洞。

## 📖 语法/签名

```typescript
// next.config.ts —— 开启 Cache Components
import type { NextConfig } from 'next';
const nextConfig: NextConfig = {
  cacheComponents: true,
};
export default nextConfig;
```

```typescript
// 函数级缓存
import { cacheLife, cacheTag } from 'next/cache';

async function getPosts() {
  'use cache'
  cacheLife('hours');            // 缓存时长 profile：seconds/minutes/hours/days/weeks/max 或自定义
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
| `revalidateTag(tag, profile)` | 第二参数为 profile 或 { expire: number } | 服务端按标签失效（stale-while-revalidate） |
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

```

```tsx
// app/actions.ts —— 独立文件，指令必须在文件顶部
'use server'
import { updateTag } from 'next/cache';

export async function createPost(formData: FormData) {
  // 此处还需项目的认证与授权；db 为项目数据访问依赖
  const title = formData.get('title');
  if (typeof title !== 'string' || !title.trim() || title.length > 200) {
    throw new Error('invalid title');
  }
  await db.post.create({ data: { title: title.trim() } })
  updateTag('posts') // 写后读：让本请求立即反映新写入
}
```

## ⚠️ 常见陷阱

- `"use cache"` 必须是函数体第一条语句，且只能用于服务端（Server Components、Server Actions、route handler）
- 缓存函数的参数与返回值必须可序列化；Date/Map/Set 等内建类型受协议支持，任意类实例或 URL 等不能据此推断为可序列化
- 忘记 `cacheTag` 会导致数据无法精准失效，只能整体过期
- Next.js 16 中 `revalidateTag(tag)` 单参数调用已被弃用，必须传 `cacheLife` profile 作为第二参数
- `unstable_cache` 官方已标记为**不推荐新项目使用**（16.3 中仍可导入，但生态方向是 `"use cache"` 模型，新代码直接采用后者）；Next.js 16 已**移除** experimental PPR 标志与 `experimental_ppr` 段配置，PPR 能力通过 cacheComponents 与 Suspense 组织动态区域
- 必须区分 cacheComponents 开关；未启用时仍有旧路由缓存模型，fetch 默认不缓存也不等于页面绝不预渲染，升级后页面可能"突然变动态"，应主动为热点页面补上 `"use cache"`

## 模式不变量

- **缓存是显式契约而非默认行为**：缓存意图必须逐处显式声明、缓存键由声明处的输入推导，未声明即按请求时执行（对照 `"use cache"` 指令与 `cacheComponents` 开关的 opt-in 模型）。
- **缓存边界归服务端所有**：缓存声明只存在于服务端语境（Server Components / Server Actions / route handler），客户端只消费缓存结果而不参与失效决策（对照 `"use cache"` 的适用范围限制）。
- **可缓存的必须可失效**：缓存条目必须携带失效标识才能被精准作废，否则只能等待整体过期（对照 `cacheTag` 配合 `revalidateTag` / `updateTag` 的按需失效）。
- **进入缓存边界的数据必须可序列化**：参数与返回值以可序列化为前提，非序列化类型无法跨越缓存边界（对照 "use cache" 的序列化陷阱）。
- **写后读一致性由写入方负责**：写操作完成后的读取一致性由写入动作显式触发失效或刷新，而非被动等待缓存过期（对照 Server Actions 中的 `updateTag` / `refresh`）。

<!-- full-library-explanation -->
## 把缓存命中与数据正确性分开验证

前置是服务端渲染、请求参数与数据库写入。缓存键回答“哪些调用可以复用结果”，标签回答“哪些结果受这次写入影响”。若结果与租户、语言或权限有关，输入与授权必须正确建模；标签不能代替权限隔离。不要缓存写操作，缓存命中可能直接跳过函数执行。

普通 use cache 作用域不能读取 cookies/headers，包括间接调用读取它们的 helper。先在外部读取并验证所需值，再把最少的可序列化数据传入缓存函数。Next 的序列化协议不是 JSON：Date、Map、Set 等受支持，而任意类实例、URL 实例等有不同限制。

**练习**：准备两个用户访问同一路径，验证响应不串用私有数据；写入文章后比较 updateTag 与 revalidateTag('posts','max') 的首个读取结果。后者允许先返回陈旧内容并触发重验证，不能用在要求立即看到写入的流程。用生产构建后的 next start 观察多次请求，开发模式和单次 build 成功不足以证明运行期缓存正确。

依据：[use cache](https://nextjs.org/docs/app/api-reference/directives/use-cache)、[revalidateTag](https://nextjs.org/docs/app/api-reference/functions/revalidateTag)。

## 🔗 相关条目

- [异步请求 APIs](./09-async-request-apis.md) —— 动态数据如何以请求时执行方式接入
- [数据获取模式](./04-data-fetching-patterns.md)
- [服务端组件模式](./02-server-components-patterns.md)
- [Next.js API 参考](../language-concepts/02-nextjs-api-reference.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
