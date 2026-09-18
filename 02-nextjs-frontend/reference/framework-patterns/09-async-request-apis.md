# 异步请求 APIs（params / searchParams / cookies / headers）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `framework-patterns`

## 📌 定义

异步请求 APIs 指 App Router 中与当前请求相关的动态数据源：动态路由段 `params`、查询串 `searchParams`，以及 `cookies()`、`headers()`、`draftMode()`。这些 API 均为 Promise/异步形态——页面组件收到的 `params`/`searchParams` 是 Promise，函数式 API 返回 Promise。Next.js 15 开始引入该形态并提供临时同步兼容层，Next.js 16 起同步访问**完全移除**，服务端用 await，客户端读取下传 Promise 可用 React use。

## 📖 语法/签名

```tsx
// 页面组件：params / searchParams 为 Promise props
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ q?: string | string[] }>;
}) {
  const { slug } = await params;
  const { q } = await searchParams;
}

// 函数式请求 APIs
import { cookies, headers, draftMode } from 'next/headers';

const cookieStore = await cookies();   // ReadonlyRequestCookies
const headerList = await headers();    // ReadonlyHeaders
const draft = await draftMode();       // { isEnabled, ... }
```

Route handler 中的 `params` 同样是 Promise：

```typescript
export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
}
```

## 💡 示例

```tsx
// app/search/page.tsx —— 读取查询参数
export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ keyword?: string | string[]; page?: string | string[] }>;
}) {
  const { keyword = '', page = '1' } = await searchParams;
  if (typeof keyword !== 'string') throw new Error('keyword must be a single value');
  const results = await searchProducts(keyword, parsePage(page)); // parsePage 见下方，实际项目放入可导入模块
  return <ResultList items={results} />;
}
```

```tsx
// 在 generateMetadata 中读取动态参数
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return { title: `文章：${slug}` };
}
```

## ⚠️ 常见陷阱

- 同步访问 `params.id` / `cookies()` 在 Next.js 16 直接报错（15 中只是警告），升级时务必全量 `await`
- 在客户端组件中调用 `cookies()`/`headers()` 会抛错——它们只能在 Server Components、Server Actions 与 route handler 中使用
- 解构必须先 `await` 再解构：`const { slug } = await params`，而不是 `{ params: { slug } }` 形式的参数解构
- 同一 Promise 可多次 `await`（幂等），无需担心重复消费
- 官方提供 codemod 迁移：`npx @next/codemod@canary next-async-request-api .`

## 模式不变量

- **请求上下文只存在于服务端**：与当前请求绑定的数据源（cookie、header、路由参数、草稿模式）只能由服务端语境读取，客户端也可用路由 Hooks 读取 URL 状态，但不能调用服务端 cookies()/headers()（对照 `cookies()`/`headers()` 在客户端组件中抛错的限制）。
- **请求相关输入以待决形态呈现**：凡随请求变化的输入在类型与访问上都表现为"必须等待"的值，使动态数据在编译期即与静态内容区分（对照 `params`/`searchParams` 的 Promise 形态与"先 await 再解构"）。
- **对请求值的等待是读取而非消费**：同一请求值可多次等待且结果幂等，读取动作不产生副作用（对照"同一 Promise 可多次 await"陷阱条目）。
- **请求 API 暴露只读视图**：Server Component 渲染时读取 cookies/headers；Cookie 修改只能在支持写响应的 Server Action 或 Route Handler 等上下文进行，不能概括为所有上下文都只读（对照 `cookies()`/`headers()` 的返回类型）。

<!-- full-library-explanation -->
## 异步读取之后仍是不可信输入

前置是 Promise、URL 查询参数和类型验证。await 只取得值，不会把用户输入变成业务需要的类型。相同查询键可以出现多次，所以 searchParams 的值应考虑 string[]；Number('') 为 0、Number('abc') 为 NaN，都不能直接当成合法页码。

```ts
export function parsePage(raw: string | string[] | undefined): number {
  if (raw === undefined) return 1;
  if (typeof raw !== 'string' || !/^[1-9]\d*$/.test(raw)) {
    throw new Error('invalid page');
  }
  const page = Number(raw);
  if (!Number.isSafeInteger(page) || page > 10000) throw new Error('page out of range');
  return page;
}
```

**练习**：对缺省、'1'、'0'、'abc'、['1','2'] 验证函数，只有前两项返回 1。页码上限是该练习的产品约束，真实项目按分页成本设定。客户端可通过 useParams/useSearchParams 读取路由状态，或用 React use 解包下传 Promise；这与服务器 cookies()/headers() 的请求上下文 API 不同。

依据：[page props](https://nextjs.org/docs/app/api-reference/file-conventions/page)、[cookies](https://nextjs.org/docs/app/api-reference/functions/cookies)。

## 🔗 相关条目

- [Cache Components 与 "use cache" 指令](./08-caching-patterns.md) —— 缓存与请求时执行的边界
- [App Router 实战模式](./01-app-router-patterns.md)
- [数据获取模式](./04-data-fetching-patterns.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
