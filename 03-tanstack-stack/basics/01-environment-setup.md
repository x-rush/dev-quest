# 环境搭建与项目初始化

> **文档简介**: 从零搭建集成 TanStack Query、Devtools 与 Vite 的 React + TypeScript 开发环境，为后续所有 TanStack 学习奠定工程基座
>
> **目标读者**: 已具备 React 基础、初次接触 TanStack 生态的前端开发者
>
> **前置知识**: React 组件与 Hooks 基础、包管理器（npm/pnpm）基本操作

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#环境搭建` `#Vite` `#pnpm` `#Devtools` |
| **更新日期** | `2026年9月` |

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
corepack prepare pnpm@latest --activate
```

> 💡 npm/yarn 同样可用，本模块示例统一使用 pnpm。

## 🚀 2. 创建 Vite 项目

```bash
pnpm create vite@latest tanstack-lab -- --template react-ts
cd tanstack-lab
pnpm install
pnpm dev
```

浏览器访问 `http://localhost:5173`，看到 Vite 欢迎页即成功。

## 📦 3. 安装 TanStack 核心库

```bash
# 运行时依赖
pnpm add @tanstack/react-query @tanstack/react-query-devtools

# 按需安装（后续教程会用到）
pnpm add @tanstack/react-table @tanstack/react-router @tanstack/react-form

# Router 需要 Vite 插件来生成类型安全的路由树
pnpm add -D @tanstack/router-plugin
```

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

- ✅ **统一包管理器**：在 `package.json` 中用 `packageManager` 字段锁定 pnpm 版本
- ✅ **QueryClient 单例**：应用生命周期内只创建一次
- ✅ **staleTime 从小值起步**：先设 30 秒感受缓存行为，再按业务调优
- ❌ **避免** 手动编辑 `routeTree.gen.ts`，它是插件生成的产物
- ❌ **避免** 在 `QueryClientProvider` 之外调用 `useQuery`

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
