# URL 搜索参数状态：validateSearch 与类型化 search

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

TanStack Router 的 `validateSearch` 把 URL 查询参数解析为**类型安全的搜索状态**：路由声明解析/校验函数后，`Route.useSearch()` 在任何组件里都返回带类型的对象。它是"表格状态放进 URL"（可分享、可回退、刷新可恢复）的核心机制，也是 Router × Query 数据通路的起点。

## 📖 语法 / 签名

```tsx
import { Link, createFileRoute } from '@tanstack/react-router'

function validateDashboardSearch(search: Record<string, unknown>) {
  if (search.page === undefined) return { page: 1 }

  const page = typeof search.page === 'string' || typeof search.page === 'number'
    ? Number(search.page)
    : Number.NaN
  if (!Number.isInteger(page) || page < 1) {
    throw new Error('page 必须是正整数')
  }

  return { page }
}

// 文件路由模块：由 TanStack Router 插件/CLI 生成 routeTree.gen.ts 后才会被应用加载。
export const Route = createFileRoute('/dashboard')({
  validateSearch: validateDashboardSearch,
  component: DashboardPage,
  // search：解析后的未验证参数（可以是数字、布尔值、数组等）
  // 返回值：类型化的搜索状态对象；抛出错误即导航被拒绝
})

function DashboardPage() {
  const search = Route.useSearch() // 组件内读取（类型化）
  const navigate = Route.useNavigate()

  return (
    <>
      <p>当前第 {search.page} 页</p>
      <button onClick={() => void navigate({ search: (prev) => ({ ...prev, page: prev.page + 1 }) })}>
        下一页
      </button>
      <Link to="/dashboard" search={{ page: 1 }}>回到第一页</Link>
    </>
  )
}
```

此片段是文件路由模块，必须由 TanStack Router 的文件路由插件或 CLI 生成 `routeTree.gen.ts` 并接入 `createRouter`；在普通组件文件中单独复制 `createFileRoute` 不能形成可访问的路由。

| 要素 | 类型 | 说明 |
|------|------|------|
| `search` 入参 | `Record<string, unknown>` | 未经处理的原始参数，需自行 `Number()`/判型 |
| 返回值字段 | 业务自定义 | 建议全部给默认值，保证"带默认值的类型化对象" |
| `navigate({ search })` | `(options) => Promise` | 传函数 `(prev) => next` 可基于旧值更新 |

## 💡 示例

```tsx
// src/routes/dashboard.tsx
export const Route = createFileRoute('/dashboard')({
  validateSearch: (search: Record<string, unknown>) => ({
    page: pageNumber(search.page, 1, 10000),
    pageSize: pageNumber(search.pageSize, 20, 100),
    sort: typeof search.sort === 'string' ? search.sort : 'createdAt:desc',
    q: typeof search.q === 'string' ? search.q : '',
  }),
  component: DashboardPage,
})

// 任意组件
const search = Route.useSearch()
// search.page / search.sort 均有类型与默认值

// 排序变化 → 只改 URL，Query 自动跟进
void navigate({ search: (prev) => ({ ...prev, sort: 'name:asc', page: 1 }) })
```

## ⚠️ 常见陷阱

- ❌ 直接信任原始参数类型：search.page 类型是未知输入，不能假定一定是字符串；应检查类型与整数范围
- ❌ 返回值不留默认值：首次进入无参数时字段为 `undefined`，下游全部要判空
- ❌ 在 `validateSearch` 里抛错却不处理：导航被拒绝且用户看到的是"链接无效"，应由 errorComponent 等错误边界处理；验证失败不等于资源不存在
- ❌ 期望 search 变化不触发 loader：应通过 loaderDeps 明确哪些搜索字段影响加载与缓存身份，不能假定所有 search 字段天然属于 loader 依赖
- ✅ 数组参数自行归一化（`string[]` 与 `string` 两种形态都要接住），写入时统一格式

<!-- full-library-explanation -->
## URL 状态需要业务范围验证

先修：unknown、Number、对象更新。Router 默认搜索解析支持 JSON 风格的值，因此输入可能已经是数字、布尔值、数组或对象，不只是字符串。

```ts
// 可独立测试的输入归一化函数
function pageNumber(value: unknown, fallback: number, max: number): number {
  if (typeof value !== 'string' && typeof value !== 'number') return fallback;
  const number = Number(value);
  return Number.isInteger(number) && number >= 1 && number <= max
    ? number : fallback;
}
```

将它用于 page 与 pageSize，避免 NaN、负数、无限大和过大的分页请求。sort 应限定为服务端支持的值，而不是任意字符串直接拼入 SQL。

loader 读取分页时显式声明 `loaderDeps: ({search}) => ({page: search.page, pageSize: search.pageSize})`，再从 loader 的 deps 读取。仅改变展示模式的搜索参数不一定需要重取数据；不要把整个 search 无差别作为加载依赖。

**练习：** 分别输入缺失页码、`-1`、`abc`、`2` 和超大数，确认最终状态符合约束；复制 URL 到新标签，状态一致。排序变化时重置页码，浏览器后退应恢复旧状态。参考[搜索参数](https://tanstack.com/router/latest/docs/framework/react/guide/search-params)。

## 🔗 相关条目

- 📄 **[Router 核心 API](./03-router-core-api.md)** - 路由选项与类型注册全表
- 📄 **[生态协作](../../frameworks/03-ecosystem-integration.md)** - Router × Query 数据通路
- 📄 **[数据看板项目](../../projects/02-data-dashboard.md)** - URL 驱动表格的完整实战
- 📄 **[Router 基础](../../basics/05-router-fundamentals.md)** - 文件式路由入门

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
