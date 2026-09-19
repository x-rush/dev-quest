# 开发工具链：TanStack Devtools 与 ESLint Plugin Query

## 先产出一份能复现的缓存诊断记录

前置是已经能运行的 React 工程、一个成功的 Query，以及能读取浏览器 Network 请求。如果还没有这条链路，先完成 [Query 基础](./01-tanstack-query-basics.md)。本篇按 Query v5、Router v1 和 ESLint flat config 说明；先运行 `npm ls @tanstack/react-query @tanstack/react-router eslint` 记录实际安装版本。只用 Query 的工程可跳过 Router 章节。

最终产物不是“装好两个面板”，而是一份记录：用户动作、queryKey、请求 URL、响应状态、缓存数据和页面显示。按以下顺序操作，每一步仅改一个变量：

1. **连接一个已有查询。** 把 Query Devtools 放进应用原有 Provider，打开含 `['todos']` 查询的页面。预期面板能找到该键，数据对应 Network 响应；面板为空时先检查是不是挂到了另一个 QueryClient，不要再创建第二个 Provider 包业务页面。
2. **制造一次可解释的失败。** 临时把该查询设为 `retry: false`，让测试接口返回 500，且 queryFn 检查 `res.ok` 后抛错。输入是一次刷新动作；输出应是错误状态和错误界面。若面板显示 success 而数据是错误 JSON，回查 queryFn 是否把 HTTP 错误当普通数据返回。已有缓存时要另测后台刷新失败，旧内容不应无条件消失。
3. **恢复同一请求。** 恢复 200 后点页面的重试按钮或面板 Refetch，记录同一个键如何恢复以及数据更新时间。不要靠清空全部缓存“修好”，否则无法分辨是键错误还是请求错误。
4. **加入静态规则并故意触发一次。** 完成第三节后运行 lint，临时让 queryFn 使用 `userId` 而 queryKey 漏掉它，确认报 `exhaustive-deps`；补回键后重新运行。若没有报错，用 `--print-config` 检查目标 TSX 文件是否真的启用了规则。

2026-09-20 已核对下文官方 API 和规则名称。本篇没有安装依赖、运行 lint、构建或操作实际面板；这些步骤是读者待执行的验收，不是已通过的工程测试。

> **文档简介**: 配置 Query/Router 双 Devtools 面板与 @tanstack/eslint-plugin-query，把缓存调试和 API 误用检查变成日常开发的自动兜底。
>
> **目标读者**: 已接入 TanStack Query，希望提升调试效率与代码质量的开发者
>
> **前置知识**: [Query 基础](./01-tanstack-query-basics.md)、[环境搭建](../basics/01-environment-setup.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#devtools` `#eslint` `#调试` `#工程化` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 完成后你将能够

- 在应用内挂载 Query Devtools，实时查看缓存、请求与失效状态
- 挂载 Router Devtools 查看路由树、匹配与加载状态
- 用官方 ESLint 规则在 CI 阶段拦住 Query 的常见误用

> 装好工具后排查问题，请配合 [故障排除](../reference/quick-references/02-troubleshooting.md) 的排查路径使用。

---

## 1. TanStack Query Devtools

### 1.1 安装与挂载

```bash
npm install @tanstack/react-query-devtools@5 --save-dev
```

```tsx
// 在已有应用 Provider 中加入面板；Root 指已有业务根组件，按项目路径导入。
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

**说明**：默认导入按开发环境启用；面板停靠方向的 prop 是 `position`，入口按钮位置是 `buttonPosition`，不要混用。`initialIsOpen` 控制初始展开。依赖放进 devDependencies 后，构建阶段仍需安装开发依赖才能解析导入。[官方 Query Devtools](https://tanstack.com/query/latest/docs/framework/react/devtools)

### 1.2 面板能回答的问题

| 疑问 | 在面板里看哪里 |
|------|----------------|
| 这个键的缓存多久了？ | 选择查询，查看数据更新时间，并结合实际 staleTime 配置判断 |
| 为什么没有重新请求？ | Query Explorer 里看 `stale` / `fresh` / `fetching` 状态 |
| 失效传播到哪些键了？ | 失效动作后观察同前缀条目的状态变化 |
| 乐观更新被覆盖了？ | 观察 mutation 状态，并用回调日志与 Network 时间顺序对照；不依赖自动重放 |
| 无观察者的缓存是否回收？ | 离开页面后观察条目是否在 gcTime 后消失；条目数不等于内存字节数 |

### 1.3 配合测试的技巧

```tsx
// initialIsOpen 只控制面板初始展开状态，不会隐藏入口按钮
const closedPanel = <ReactQueryDevtools initialIsOpen={false} />;
// Vite 项目只在开发环境挂载整个组件，测试/生产环境不渲染入口
const developmentPanel = import.meta.env.MODE === 'development'
  ? <ReactQueryDevtools initialIsOpen={false} />
  : null;
```

---

## 2. TanStack Router Devtools

```bash
npm install @tanstack/react-router-devtools@1 --save-dev
```

```tsx
// src/components/RouterDevtools.tsx —— 仅开发环境渲染
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'

export function RouterDevtools() {
  if (import.meta.env.PROD) return null
  return <TanStackRouterDevtools position="bottom-left" />
}
```

将这个组件放在已有根路由组件的 `<Outlet />` 旁边，使它能取得路由上下文；如果放在 `RouterProvider` 外，需给 Devtools 显式传入同一个 `router` 实例。[官方 Router Devtools](https://tanstack.com/router/latest/docs/devtools)

先访问列表再点详情，核对面板中的匹配路由和实际 URL。随后悬停设置了 intent 预加载的链接，观察 loader 是否触发。只有 loader 调用了同一个 QueryClient 的查询预取/确保数据方法时，Query 面板才会出现对应条目；Router 预加载本身不会自动创建 Query 缓存。没有条目时先回查 loader，再查 queryKey 与客户端实例，最后查看 Network 是否被缓存策略省略了请求。

---

## 3. ESLint Plugin Query

### 3.1 安装与配置

```bash
npm install @tanstack/eslint-plugin-query@5 --save-dev
```

```js
// eslint.config.js —— 在已有 TS/TSX flat config 数组中加入下面的展开项。
import tanstackQuery from '@tanstack/eslint-plugin-query'

export default [
  ...tanstackQuery.configs['flat/recommended'],
]
```

这是 Query 插件部分，不是完整 TypeScript ESLint 配置：保留项目原有的 `typescript-eslint` parser、TS/TSX 文件匹配和 React 规则。不要把既有配置整份覆盖。官方 flat config 使用 `flat/recommended` 数组；规则可能随插件小版本变化，精确依赖由 lockfile 固定。[官方 ESLint 配置源码](https://github.com/TanStack/query/blob/main/docs/eslint/eslint-plugin-query.md)

在项目中用真实文件路径执行 `npx eslint src/实际查询组件.tsx`；若出现 “File ignored”，先修正文件匹配，再判断 Query 规则是否有效。`npx eslint --print-config src/实际查询组件.tsx` 应包含 `@tanstack/query/exhaustive-deps`。若提示语法解析错误，先补齐 TSX parser 配置，Query 插件不会代替 TypeScript 解析器。

### 3.2 核心规则与拦住的问题

| 规则 | 拦住的错误 |
|------|-----------|
| `@tanstack/query/exhaustive-deps` | queryFn 里用了外部变量但没放进 queryKey——缓存键与实际依赖不一致 |
| `@tanstack/query/stable-query-client` | 在组件内新建 queryClient 传给 Provider——导致每轮渲染重建缓存 |
| `@tanstack/query/no-rest-destructuring` | 对 `useQuery` 返回值做剩余解构，丢失响应性追踪提示 |
| `@tanstack/query/no-unstable-deps` | 把整个 Query Hook 返回对象放进 React Hook 依赖数组，而不是所需字段 |

`exhaustive-deps` 是价值最高的一条：Query 的一切建立在"键 = 输入"的约定上，这条规则把违反约定的问题从线上 bug 提前到编辑器红线。

---

## 🎨 最佳实践速查

完成失败—恢复记录后，再测一次离开页面与返回：区分数据 stale 后后台重取、缓存 gc 后首次加载以及页面重新挂载。把实际 staleTime、gcTime 和观察时间写进记录；只写“重复请求了”无法定位原因。下一步进入 [单元测试](../testing/01-unit-testing.md)，把这次失败恢复行为变成断言，再把已生效的 lint 命令接入 CI。

调试缓存时先记录查询键、数据更新时间和触发请求的操作，再用 Devtools 观察状态变化。例如“返回页面重复请求”可能是数据已过期，不一定是缓存没有生效。保留可重复步骤比反复刷新更能定位原因。

开发工具是否进入生产包由导入方式和构建流程共同决定，写进 devDependencies 不自动保证不会打包。检查生产产物及网络请求；测试中按需关闭调试面板，避免额外节点干扰定位。CI 的 lint 负责检查已配置规则，不能证明缓存语义正确。

---

## 🔗 相关文档

- 📄 **[Query 基础](./01-tanstack-query-basics.md)** - Devtools 观察对象的来源
- 📄 **[故障排除](../reference/quick-references/02-troubleshooting.md)** - 常见错误与排查路径字典
- 📄 **[五库语法速查表](../reference/quick-references/01-syntax-cheatsheet.md)** - 写码时随手对照
- 📄 **[单元测试](../testing/01-unit-testing.md)** - Devtools 之外的第二双眼睛
- 📄 **[CI/CD 流水线](../deployment/01-ci-cd-pipelines.md)** - 把 lint/测试固化到流水线


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
