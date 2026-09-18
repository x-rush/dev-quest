# 02 模块生态依赖地图（按用途分组的第三方库导览）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `library-guides`

## 📌 定义

本条目是 02 模块涉及的全部第三方库的**依赖地图**：不教任何一个库的用法（用法在对应框架条目与 `development-tools/` 详解），只回答三个问题——"这个库是干什么的"、"什么时候该用它"、"什么时候不该用"。分组依据是库在应用中的**职责**（状态/表单/样式/数据请求/测试/UI 组件/调试工具），而非流行度。所有定位描述与模块内既有条目（`framework-patterns/`、`development-tools/`）的结论保持一致。

## 📖 生态分组表

### 状态管理

| 库 | 一句话定位 | 使用建议 |
|----|-----------|----------|
| **Zustand** | 极简客户端全局状态库（一个 `create` 函数 + selector 订阅） | 购物车、主题、UI 偏好这类**纯客户端**共享状态的首选；见 [状态管理模式](../framework-patterns/05-state-management-patterns.md) |
| **TanStack Query v5** | 服务端状态管理（缓存、去重、后台重验证） | 需要客户端缓存、重取与共享的远程数据可交给它管理，**不要**把接口数据塞进 Zustand；见 [数据获取模式](../framework-patterns/04-data-fetching-patterns.md) |
| **SWR** | Vercel 出品的轻量数据请求 hooks（stale-while-revalidate） | 与 TanStack Query 职责重叠，**二选一**即可；本模块主推 TanStack Query（缓存控制粒度更细） |
| **Redux Toolkit** | 重约定、单一 store 的经典状态方案 | 存量项目维护用；新项目无强需求时不引入（模板代码量明显高于 Zustand） |

### 表单与校验

| 库 | 一句话定位 | 使用建议 |
|----|-----------|----------|
| **React Hook Form v7** | 非受控订阅式表单库（按字段注册、重渲染极少） | 复杂表单首选；简单两三个输入框用原生 `useState` 就够；见 [表单校验模式](../framework-patterns/06-form-validation-patterns.md) |
| **Zod** | schema 优先的运行时校验 + TypeScript 类型推导（`z.infer`） | 与 RHF 的 `zodResolver` 是标准组合；同一个 schema 同时产出运行时校验与静态类型；类型层参考 [TypeScript 类型速查](../language-concepts/03-typescript-types.md) |

### 样式与 UI

| 库 | 一句话定位 | 使用建议 |
|----|-----------|----------|
| **Tailwind CSS 4** | 原子化 CSS（v4 编译更快、零配置起步） | 本模块默认样式方案；见 [样式工具链](../development-tools/02-styling-tools.md) |
| **Radix UI / shadcn/ui** | 无样式的可访问组件原语 / 基于 Tailwind 的复制式组件集 | 需要弹窗、下拉、Toast 等复杂交互组件时用；shadcn/ui 把组件源码复制进项目（可自由改） |
| **lucide-react** | 单包 React 图标组件集（tree-shakable） | 默认图标库；只 import 用到的图标即可，仍有体积成本，应在生产构建中检查按需打包结果 |
| **Motion（原 Framer Motion）** | 声明式 React 动画库 | 入场/退场、手势、layout 动画；纯 CSS transition 能解决的不要上它；见 [渲染优化](../performance-optimization/01-rendering-optimization.md) |

### 数据请求

| 库 | 一句话定位 | 使用建议 |
|----|-----------|----------|
| **原生 fetch** | 平台内置请求 API（Next.js 扩展了 `next.revalidate`/`tags` 选项） | 外部 HTTP 可用 fetch；数据库与服务端 SDK 可在服务器直接调用，见 [数据获取模式](../framework-patterns/04-data-fetching-patterns.md) 与 [Cache Components](../framework-patterns/08-caching-patterns.md) |
| **axios** | 功能全的 XHR/fetch 封装（拦截器、取消、进度） | 需要拦截器、上传进度等能力时评估；也可作为 TanStack Query 的请求实现 |
| **MSW** | 用 Service Worker 拦截网络做 mock | 测试与本地开发模拟接口；见 [测试工具](../development-tools/01-testing-tools.md) |

### 测试

| 库 | 一句话定位 | 使用建议 |
|----|-----------|----------|
| **Vitest** | Vite 内核的测试框架（兼容 Jest API、秒级启动） | 本模块默认单测框架；见 [测试工具](../development-tools/01-testing-tools.md) |
| **React Testing Library** | 面向用户行为的 React 组件测试工具 | 与 Vitest 搭配做组件测试；查询按可访问性角色而非 class 定位 |
| **Playwright** | 跨浏览器 E2E 自动化（含代码生成、trace viewer） | 关键路径 E2E；配合 `@next/env` 复用 `.env` 加载 |
| **Jest** | 老牌测试框架 | 存量项目维护；Next 项目也可选 next/jest；按 ESM、插件与既有测试配置选择 |
| **Storybook** | 组件隔离开发与可视化文档 | 组件库化时引入；小型应用可先不建 |

### 调试与工程

| 库/工具 | 一句话定位 | 使用建议 |
|---------|-----------|----------|
| **React DevTools** | 组件树与 props/hook 状态检查 | 排查渲染数据的必备品；见 [调试工具](../development-tools/04-debugging-tools.md) |
| **TanStack Query Devtools** | Query 缓存可视化（键、状态、重试） | 引入 Query 就该顺手挂上 `<ReactQueryDevtools />` |
| **pnpm / npm** | 包管理器 | 本模块示例统一 npm，pnpm 等价可换；见 [包管理器](../development-tools/03-package-managers.md) |

## 💡 示例：按场景反查依赖

```txt
"购物车数据要全站共享"        → Zustand（05-state-management-patterns）
"列表数据来自 /api/posts"     → TanStack Query（客户端）或 Server Component + fetch（服务端）
"表单 + 后端校验规则复用"     → React Hook Form + Zod（zodResolver 一份 schema 两端复用）
"下拉菜单要无障碍 + 键盘导航"  → Radix UI 原语（shadcn/ui 封装）
"页面标题/OG 图动态生成"      → 不装库！Metadata API 内置（12-metadata-and-script）
"第三方统计/客服脚本"        → 不装库！next/script 内置（12-metadata-and-script）
"环境变量读取"              → 不装库！内置 .env 机制（14-env-vars）
```

## ⚠️ 常见陷阱

- ❌ **把接口数据写进 Zustand 再手动刷新**：服务端状态的缓存/失效/重验证逻辑全部要自己重造一遍。✅ 服务端数据归 TanStack Query（或 Server Component 直取），Zustand 只管纯客户端状态。
- ❌ **同时引入 TanStack Query 和 SWR**：两套缓存并存，同一数据两处真相。✅ 团队统一选一个；本模块条目以 TanStack Query 为准。
- ❌ **简单表单也上 React Hook Form + Zod**：两个输入框的订阅表单不值得引入依赖与样板。✅ 简单流程可用原生表单；按动态行为与验证需求决定，不以字段数机械划线。
- ❌ **能用平台内置能力的地方装第三方库**：metadata、脚本加载、环境变量、图片优化（`next/image`）Next.js 全部内置，装库只会增加维护面。✅ 先查 `framework-patterns/` 与 `language-concepts/02-nextjs-api-reference.md` 再决定是否引入依赖。
- ❌ **新项目沿用 Jest 是因为"大家都用"**：本模块已统一 Vitest（使用 Vite 转换链，不等同 Next 的 Turbopack 构建），Jest 仍是可选方案，不能仅凭新旧项目划分。✅ 新项目 `npm i -D vitest @testing-library/react` 起步。
- ❌ **图标/动画库整包引入**：`import * as Icons` 或全量 motion API 会拖累 bundle。✅ lucide 按名具名导入（tree-shake 生效），动画先试 CSS transition；bundle 影响评估见 [Bundle 优化](../performance-optimization/02-bundle-optimization.md)。

<!-- full-library-explanation -->
## 按需求证明引入依赖的价值

前置是客户端状态、服务器数据和包管理。先写出当前缺少的能力：跨页面共享、后台重取、复杂校验、键盘交互，还是打包分析，再选负责这项能力的工具。同一数据在 Query、Zustand 和组件 state 各存一份时，要明确谁是权威来源以及如何同步，否则库越多越容易出现旧值。

React Server Components 直接读取数据库或调用服务端 SDK 是合理路径，不必绕回本应用的 HTTP 接口。Query 负责客户端异步状态生命周期，并不自带 HTTP 传输；fetch/axios 才是请求层。表单库也不能代替服务端校验与授权，字段数量不是唯一选型标准，动态字段、错误反馈和复杂交互同样重要。

**练习**：用“公开文章页”和“实时筛选管理台”分别画出数据流，说明为何前者可以主要在服务端取数，后者可能受益于客户端缓存。只引入一个工具解决当前问题，比较包体积、配置、失败恢复和测试复杂度。没有框架能保证永不过时，长期保留的学习重点是状态所有权、请求协议、可访问性与测试边界。

依据：[Next 测试工具选择](https://nextjs.org/docs/app/guides/testing)、[TanStack Query 概览](https://tanstack.com/query/latest/docs/framework/react/overview)。

## 🔗 相关条目

- [状态管理模式](../framework-patterns/05-state-management-patterns.md) —— Zustand + TanStack Query 分工详解
- [表单校验模式](../framework-patterns/06-form-validation-patterns.md) —— RHF + Zod 标准组合
- [数据获取模式](../framework-patterns/04-data-fetching-patterns.md) —— fetch 与服务端/客户端数据边界
- [Cache Components 与 "use cache" 指令](../framework-patterns/08-caching-patterns.md) —— 服务端缓存层
- [测试工具](../development-tools/01-testing-tools.md) —— Vitest/RTL/Playwright/MSW 配置实战
- [样式工具链](../development-tools/02-styling-tools.md) —— Tailwind 4 工程化
- [包管理器](../development-tools/03-package-managers.md) —— 依赖安装与锁文件
- [调试工具](../development-tools/04-debugging-tools.md) —— DevTools 全家桶
- [渲染优化](../performance-optimization/01-rendering-optimization.md) —— 引入客户端库对水合的影响
- [Bundle 优化](../performance-optimization/02-bundle-optimization.md) —— 依赖体积分析与按需加载
- [图片字体优化](../performance-optimization/03-image-font-optimization.md) —— `next/image`/`next/font` 内置方案

---
*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
