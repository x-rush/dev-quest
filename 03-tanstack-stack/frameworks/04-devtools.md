# 开发工具链：TanStack Devtools 与 ESLint Plugin Query

> **文档简介**: 配置 Query/Router 双 Devtools 面板与 @tanstack/eslint-plugin-query，把缓存调试和 API 误用检查变成日常开发的自动兜底。
>
> **目标读者**: 已接入 TanStack Query，希望提升调试效率与代码质量的开发者
>
> **前置知识**: [Query 基础](./01-tanstack-query-basics.md)、[环境搭建](../basics/01-environment-setup.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#devtools` `#eslint` `#调试` `#工程化` |
| **更新日期** | 2026年9月 |

## 🎯 完成后你将能够

- 在应用内挂载 Query Devtools，实时查看缓存、请求与失效状态
- 挂载 Router Devtools 查看路由树、匹配与加载状态
- 用官方 ESLint 规则在 CI 阶段拦住 Query 的常见误用

> 装好工具后排查问题，请配合 [故障排除](../reference/quick-references/02-troubleshooting.md) 的排查路径使用。

---

## 1. TanStack Query Devtools

### 1.1 安装与挂载

```bash
npm install @tanstack/react-query-devtools --save-dev
```

```tsx
// src/main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* 业务组件 */}
      <Root />
      {/* 默认为 floating 模式：角落花朵按钮，生产构建自动禁用 */}
      <ReactQueryDevtools initialIsOpen={false} buttonPosition="bottom-right" />
    </QueryClientProvider>
  )
}
```

**说明**：Devtools 包仅在开发构建生效（生产环境组件不渲染），但仍建议仅作为 devDependencies 引入。可用 `panelPosition` 改停靠方向、`initialIsOpen` 控制初始展开。

### 1.2 面板能回答的问题

| 疑问 | 在面板里看哪里 |
|------|----------------|
| 这个键的缓存多久了？ | 条目时间轴：`dataUpdatedAt` / `staleTime` 到期标记 |
| 为什么没有重新请求？ | Query Explorer 里看 `stale` / `fresh` / `fetching` 状态 |
| 失效传播到哪些键了？ | 失效动作后观察同前缀条目的状态变化 |
| 乐观更新被覆盖了？ | Query Explorer 重放 mutations 记录，检查 onMutate 时序 |
| 缓存占了多少内存？ | 观察无观察者条目在 `gcTime` 后消失 |

### 1.3 配合测试的技巧

```tsx
// 测试环境隐藏花朵按钮，避免干扰 DOM 快照
<ReactQueryDevtools initialIsOpen={false} />
// CI 中可通过环境变量整体关闭
<ReactQueryDevtools initialIsOpen={import.meta.env.MODE === 'development'} />
```

---

## 2. TanStack Router Devtools

```bash
npm install @tanstack/router-devtools --save-dev
```

```tsx
// src/components/RouterDevtools.tsx —— 仅开发环境渲染
import { TanStackRouterDevtools } from '@tanstack/router-devtools'

export function RouterDevtools() {
  if (import.meta.env.PROD) return null
  return <TanStackRouterDevtools position="bottom-left" />
}
```

面板可以直观看到：路由树结构、每个路由的匹配状态、loader 是否在执行、搜索参数的解析结果。与 Query Devtools 联动时，`defaultPreload: 'intent'` 触发的悬停预取会同时体现在两个面板里——这是排查"预取没生效"的第一现场。

---

## 3. ESLint Plugin Query

### 3.1 安装与配置

```bash
npm install @tanstack/eslint-plugin-query --save-dev
```

```js
// eslint.config.js —— Flat Config（ESLint 9+）
import js from '@eslint/js'
import tanstackQuery from '@tanstack/eslint-plugin-query'

export default [
  js.configs.recommended,
  {
    plugins: {
      '@tanstack/query': tanstackQuery,
    },
    rules: {
      ...tanstackQuery.configs.recommended.rules,
    },
  },
]
```

### 3.2 核心规则与拦住的问题

| 规则 | 拦住的错误 |
|------|-----------|
| `@tanstack/query/exhaustive-deps` | queryFn 里用了外部变量但没放进 queryKey——缓存键与实际依赖不一致 |
| `@tanstack/query/stable-query-client` | 在组件内新建 queryClient 传给 Provider——导致每轮渲染重建缓存 |
| `@tanstack/query/no-rest-destructuring` | 对 `useQuery` 返回值做剩余解构，丢失响应性追踪提示 |
| `@tanstack/query/invalidate-exhaustive-deps` | invalidate 调用中的键与外部依赖不一致 |

`exhaustive-deps` 是价值最高的一条：Query 的一切建立在"键 = 输入"的约定上，这条规则把违反约定的问题从线上 bug 提前到编辑器红线。

---

## 🎨 最佳实践速查

- ✅ Devtools 只装 devDependencies，组件挂载处做 PROD 判断
- ✅ CI 中把 ESLint plugin 作为独立 lint 步骤跑，红线不进主干
- ❌ 不要在测试环境打开 Devtools 面板（污染 DOM 快照与 user-event 定位）
- ❌ 不要只靠"刷新页面好像就好了"定位缓存问题——先用 Query Explorer 重现时序

---

## 🔗 相关文档

- 📄 **[Query 基础](./01-tanstack-query-basics.md)** - Devtools 观察对象的来源
- 📄 **[故障排除](../reference/quick-references/02-troubleshooting.md)** - 常见错误与排查路径字典
- 📄 **[五库语法速查表](../reference/quick-references/01-syntax-cheatsheet.md)** - 写码时随手对照
- 📄 **[单元测试](../testing/01-unit-testing.md)** - Devtools 之外的第二双眼睛
- 📄 **[CI/CD 流水线](../deployment/01-ci-cd-pipelines.md)** - 把 lint/测试固化到流水线
