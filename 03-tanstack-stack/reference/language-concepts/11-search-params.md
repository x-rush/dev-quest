# URL 搜索参数状态：validateSearch 与类型化 search

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

TanStack Router 的 `validateSearch` 把 URL 查询参数解析为**类型安全的搜索状态**：路由声明解析/校验函数后，`Route.useSearch()` 在任何组件里都返回带类型的对象。它是"表格状态放进 URL"（可分享、可回退、刷新可恢复）的核心机制，也是 Router × Query 数据通路的起点。

## 📖 语法 / 签名

```tsx
createFileRoute('/path')({
  validateSearch: (search: Record<string, unknown>) => SearchSchema
  // search：原始 URL 参数（值均为 string | string[] | undefined）
  // 返回值：类型化的搜索状态对象；抛出 ZodError 等即导航被拒绝
})

// 读取与写入
Route.useSearch()                       // 组件内读取（类型化）
Route.useNavigate()({ search: next })   // 编程式写入（触发数据流）
<Link to="." search={{ page: 2 }} />    // 声明式写入
```

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
    page: Number(search.page ?? 1),
    pageSize: Number(search.pageSize ?? 20),
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

- ❌ 直接信任原始参数类型：`search.page` 是 string，不 `Number()` 转换会让 queryKey 与预期错位
- ❌ 返回值不留默认值：首次进入无参数时字段为 `undefined`，下游全部要判空
- ❌ 在 `validateSearch` 里抛错却不处理：导航被拒绝且用户看到的是"链接无效"，需配 `notFoundComponent`/错误页兜底
- ❌ 期望 search 变化不触发 loader：search 是路由依赖的一部分，默认会重跑（配合 `staleTime` 命中缓存即可无感）
- ✅ 数组参数自行归一化（`string[]` 与 `string` 两种形态都要接住），写入时统一格式

## 🔗 相关条目

- 📄 **[Router 核心 API](./03-router-core-api.md)** - 路由选项与类型注册全表
- 📄 **[生态协作](../../frameworks/03-ecosystem-integration.md)** - Router × Query 数据通路
- 📄 **[数据看板项目](../../projects/02-data-dashboard.md)** - URL 驱动表格的完整实战
- 📄 **[Router 基础](../../basics/05-router-fundamentals.md)** - 文件式路由入门

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
