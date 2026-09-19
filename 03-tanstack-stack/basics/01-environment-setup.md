# 环境搭建与项目初始化

## 先理解，再动手

QueryClient 保存查询缓存，Provider 让组件访问同一个实例。每次渲染都创建新实例，会让缓存身份变得不稳定。

**本节自测**：在入口提供一个稳定 QueryClient，两个组件查询相同键，观察 Devtools。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

两个组件应共享同一缓存条目；不要据此推断任何配置下都只发生一次网络请求。

</details>

> **文档简介**: 从零搭建集成 TanStack Query、Devtools 与 Vite 的 React + TypeScript 开发环境，为后续所有 TanStack 学习奠定工程基座
>
> **目标读者**: 已具备 React 基础、初次接触 TanStack 生态的前端开发者
>
> **前置知识**: React 组件与 Hooks 基础、包管理器（npm/pnpm）基本操作

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#环境搭建` `#Vite` `#pnpm` `#Devtools` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 使用 pnpm 创建 Vite + React + TypeScript 项目
- ✅ 安装 TanStack 核心库并接入 `QueryClientProvider`
- ✅ 启用 React Query Devtools 并观察缓存
- ✅ 配置 TanStack Router 的 Vite 插件，体验类型安全文件路由

---

## 🛠️ 1. 准备 Node 与 pnpm 环境

TanStack 生态（尤其 Router 与 Start）对 Node 版本要求较高，建议使用 **Node.js 20 LTS 及以上**。

```bash
# 检查 Node 版本（需 >= 20）
node -v

# 检查 pnpm 是否可用
pnpm -v
```

若没有 pnpm，通过 corepack 一键启用（Node 16.13+ 自带）：

```bash
corepack enable
# 用团队/课程约定版本替换 <pnpm-version>，并记录 packageManager 字段。
corepack prepare pnpm@<pnpm-version> --activate
```

> 💡 npm/yarn 同样可用，本模块示例统一使用 pnpm。

## 🚀 2. 创建 Vite 项目

```bash
# 初次探索可用 latest；要复现练习则固定经核对的脚手架版本。
pnpm create vite@<vite-version> tanstack-lab -- --template react-ts
cd tanstack-lab
pnpm install
pnpm dev
```

`latest` 会随时间改变，不能同时承担“开始探索”和“可重复课程”的角色。首次生成后提交 `package.json`、`pnpm-lock.yaml` 与 `packageManager`，用 `pnpm --version`、`node --version` 记录工具链；升级 Vite、pnpm 或 TanStack 包时单独提交并运行类型检查、测试和关键页面验收。

浏览器访问 `http://localhost:5173`，看到 Vite 欢迎页即成功。

## 📦 3. 安装 TanStack 核心库

```bash
# 运行时依赖（Query v5 / Table v9 为 2026 年 9 月当前大版本）
pnpm add @tanstack/react-query@^5 @tanstack/react-query-devtools@^5

# 按需安装（后续教程会用到）
pnpm add @tanstack/react-table@^9 @tanstack/react-router @tanstack/react-form

# Router 需要 Vite 插件来生成类型安全的路由树
pnpm add -D @tanstack/router-plugin
```

> 💡 TanStack Query v5 官方当前支持 TypeScript **5.6+**（v5.0 发布时最低为 4.7），低于此版本先升级 `typescript`。

| 包名 | 作用 |
|------|------|
| `@tanstack/react-query` | 服务端状态管理（缓存、失效、乐观更新） |
| `@tanstack/react-table` | Headless 表格引擎（排序/筛选/分组全逻辑） |
| `@tanstack/react-router` | 100% 类型安全的文件式路由 |
| `@tanstack/react-form` | Headless 表单状态与校验 |
| `@tanstack/react-query-devtools` | Query 缓存调试面板 |

## 🔌 4. 接入 QueryClientProvider

修改入口文件 `src/main.tsx`：

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import App from './App'

// QueryClient 是整个缓存的"大脑"，应用生命周期内只创建一次
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000, // 数据 30 秒内视为新鲜，不重复请求
      retry: 1,          // 失败后重试 1 次
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      {/* 开发环境专属调试面板，不会进入生产构建 */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </StrictMode>,
)
```

**关键点解析**：

- `QueryClient` 必须挂在模块顶层或 `useState` 工厂中，避免每次渲染重建导致缓存丢失
- `defaultOptions.queries` 作为所有 `useQuery` 的默认值，可被单个查询覆盖
- `ReactQueryDevtools` 必须渲染在 `QueryClientProvider` 内部才能访问缓存

## 🧭 5. 配置 Router 的 Vite 插件

TanStack Router 依赖代码生成获得 100% 类型安全的路由树。修改 `vite.config.ts`：

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { TanStackRouterVite } from '@tanstack/router-plugin/vite'

export default defineConfig({
  // 注意：TanStackRouterVite 必须放在 react() 之前
  plugins: [TanStackRouterVite(), react()],
})
```

创建第一个路由文件 `src/routes/index.tsx`：

```tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  component: Home,
})

function Home() {
  return <h1>Hello TanStack!</h1>
}
```

重启 `pnpm dev` 后，插件会自动生成 `src/routeTree.gen.ts`——这就是类型安全路由树的来源，请勿手动编辑。

## ✅ 最佳实践

同一工程的开发机与 CI 应使用约定的 Node 和包管理器版本，并实际配置安装流程读取该约定；只写一个版本字段不会自动改变所有人的环境。生成的路由树由插件重建，路由修改应落在源文件，否则下次生成会覆盖手工更改。

浏览器中保持 QueryClient 实例稳定，避免重渲染时丢缓存；SSR 则要隔离不同请求，不能让全局客户端把用户数据混在一起。staleTime 表示数据多久仍被视为新鲜，实验时可以比较 0 与 30 秒下返回页面的请求次数，再按业务容忍的旧数据时间决定。[官方 SSR 说明](https://tanstack.com/query/latest/docs/framework/react/guides/ssr)给出了客户端作用域的区别。

## ❓ 常见问题

### Q1: 启动时报错 `Cannot find module './routeTree.gen'`？

**A**: 路由树文件由 Vite 插件生成。确认 `vite.config.ts` 中已注册 `TanStackRouterVite()` 且位于 `react()` 之前，并确认 `src/routes/` 目录存在，然后重启 dev server。

### Q2: Devtools 打不开？

**A**: 检查 `<ReactQueryDevtools />` 是否渲染在 `QueryClientProvider` **内部**，且当前是开发模式构建。

---

## 🎯 练习与实践

### 练习一：跑通最小闭环

- [ ] 创建项目并安装全部核心库
- [ ] 在 `App.tsx` 中用 `useQuery` 请求 `https://jsonplaceholder.typicode.com/todos/1` 并渲染标题
- [ ] 打开 Devtools，找到对应的缓存条目并观察其状态变化

### 练习二：环境进阶

- [ ] 把 `staleTime` 改成 `0`，切换浏览器窗口观察数据自动重新获取
- [ ] 创建 `src/routes/about.tsx`，重启后观察 `routeTree.gen.ts` 中新增的路由节点

---

## 🔗 相关文档

- 📄 **[Headless 设计哲学](./02-headless-philosophy.md)** - 理解 TanStack 与传统组件库的本质区别
- 📄 **[Query 基础](./03-query-fundamentals.md)** - 下一篇：上手 useQuery/useMutation
- 📄 **[Query 核心 API](../reference/language-concepts/01-query-core-api.md)** - QueryClient 完整方法字典
- 📄 **[生态集成指南](../reference/library-guides/01-ecosystem-integrations.md)** - Devtools 与周边工具详解

---

**最后更新**: 2026年9月 | Dev Quest · 03-tanstack-stack


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
