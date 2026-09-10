# TanStack 全家桶学习

## 📚 模块概述

本模块系统学习 TanStack 生态的核心库（Query、Table、Router、Form），掌握现代 React 应用的服务端状态管理、数据表格、类型安全路由与表单管理能力。TanStack 是 Headless（无头）设计哲学的代表，与 [02-nextjs-frontend](../02-nextjs-frontend/README.md) 的框架学习互补，重点在于可组合、可定制的数据层技术。

**技术栈基线**：React 19 + TypeScript + TanStack Query v5（v5 命名：`isPending` / `gcTime`）+ TanStack Router + TanStack Table + TanStack Form

### 🎯 学习目标

- 掌握 **TanStack Query**：服务端状态管理、缓存、失效与乐观更新
- 掌握 **TanStack Table**：Headless 表格构建、排序、筛选、分页、行内编辑
- 掌握 **TanStack Router**：100% 类型安全的文件式路由、搜索参数状态管理
- 掌握 **TanStack Form**：Headless 表单状态管理与校验集成
- 理解 Headless 库设计模式，能与任意 UI 体系（Tailwind、shadcn/ui 等）组合

---

## 🧭 四象限导览

| 象限 | 目录 | 内容 | 说明 |
|------|------|------|------|
| **教程** | [basics/](basics/) | 8 篇按序入门 | 从环境搭建到第一个完整项目，按编号顺序学习 |
| **字典** | [reference/](reference/) | 11 篇全量参考 | 概念的唯一权威出处，无难度门槛，随时跳入查阅 |
| **操作指南** | [frameworks/](frameworks/) · [projects/](projects/) · [testing/](testing/) · [deployment/](deployment/) | 15 篇任务式指南 | "怎么完成这个任务"：框架实操、实战项目、测试工程、部署运维 |
| **深度解释** | [advanced-topics/](advanced-topics/) | 4 篇原理剖析 | "为什么这样设计"：缓存架构、性能与安全 |

> **单一事实来源**：概念的完整解释只在 `reference/` 存在一分，其他目录以链接引用，不重复展开。

---

## 🛤️ 学习路径

> 字典（reference/）不设难度门槛，不进入路径；三条路径覆盖其余 27 篇文档。

### 入门路径（⭐）

[环境搭建](basics/01-environment-setup.md) → [Headless 设计哲学](basics/02-headless-philosophy.md) → [Query 基础：useQuery 与 useMutation](basics/03-query-fundamentals.md) → [Table 基础：列模型与数据行](basics/04-table-fundamentals.md) → [Router 基础：路由树、文件式路由与导航](basics/05-router-fundamentals.md) → [Form 基础：useForm 与字段绑定](basics/06-form-fundamentals.md) → [第一个项目：城市天气数据面板](basics/08-first-project.md) → [Query 实操：QueryClient 配置与核心用法](frameworks/01-tanstack-query-basics.md) → [开发工具链](frameworks/04-devtools.md) → [入门项目：Todo App](projects/01-todo-app.md)

### 进阶路径（⭐⭐）

[Query 高级特性](basics/07-advanced-features.md) → [Query 进阶：无限查询、乐观更新与失效策略](frameworks/02-tanstack-query-advanced.md) → [生态协作：Router + Table + Form 与 Query 集成](frameworks/03-ecosystem-integration.md) → [进阶项目：数据看板](projects/02-data-dashboard.md) → [高级项目：协作看板](projects/03-collaborative-kanban.md) → [单元测试](testing/01-unit-testing.md) → [Mock 服务：MSW](testing/02-mocking-server.md) → [集成测试](testing/03-integration-testing.md) → [端到端测试](testing/04-e2e-testing.md) → [CI/CD 流水线](deployment/01-ci-cd-pipelines.md) → [Vercel 部署](deployment/02-vercel-deployment.md)

### 精通路径（⭐⭐⭐）

[Query 缓存架构与数据流](advanced-topics/architecture/01-cache-architecture.md) → [查询性能优化](advanced-topics/performance/01-query-optimization.md) → [渲染性能：重渲染治理与列表虚拟化](advanced-topics/performance/02-rendering-performance.md) → [安全实践](advanced-topics/security/01-security-practices.md) → [可观测性](deployment/03-observability.md) → [生产级项目：SaaS 后台平台](projects/04-saas-admin-platform.md)

---

## 📁 目录结构

```
03-tanstack-stack/
├── README.md                                      # 本文档
├── basics/                                        # 教程：按序入门
│   ├── 01-environment-setup.md                    #   ⭐ 环境搭建与项目初始化
│   ├── 02-headless-philosophy.md                  #   ⭐ Headless 设计哲学
│   ├── 03-query-fundamentals.md                   #   ⭐ Query 基础：useQuery 与 useMutation
│   ├── 04-table-fundamentals.md                   #   ⭐ Table 基础：列模型与数据行
│   ├── 05-router-fundamentals.md                  #   ⭐ Router 基础：路由树、文件式路由与导航
│   ├── 06-form-fundamentals.md                    #   ⭐ Form 基础：useForm 与字段绑定
│   ├── 07-advanced-features.md                    #   ⭐⭐ Query 高级特性：乐观更新、无限查询与失效
│   └── 08-first-project.md                        #   ⭐ 第一个项目：城市天气数据面板
├── reference/                                     # 字典：全量参考（无难度门槛）
│   ├── framework-essentials/
│   │   ├── 01-query-essentials.md                 #   Query 框架要点：缓存键、staleTime/gcTime
│   │   └── 02-router-essentials.md                #   Router 框架要点：守卫、预加载、SSR
│   ├── language-concepts/
│   │   ├── 01-query-core-api.md                   #   Query 核心 API
│   │   ├── 02-table-core-api.md                   #   Table 核心 API
│   │   ├── 03-router-core-api.md                  #   Router 核心 API
│   │   ├── 04-form-core-api.md                    #   Form 核心 API
│   │   └── 05-typescript-patterns.md              #   TypeScript 模式
│   ├── library-guides/
│   │   ├── 01-ecosystem-integrations.md           #   生态集成：官方周边库指南
│   │   └── 02-related-libs.md                     #   相关库搭配：Zustand、Jotai、Axios 等
│   └── quick-references/
│       ├── 01-syntax-cheatsheet.md                #   五库语法速查表
│       └── 02-troubleshooting.md                  #   故障排除：常见错误与排查路径
├── frameworks/                                    # 操作指南：框架生态
│   ├── 01-tanstack-query-basics.md                #   ⭐ Query 实操：QueryClient 配置与核心用法
│   ├── 02-tanstack-query-advanced.md              #   ⭐⭐ Query 进阶：无限查询、乐观更新、失效策略
│   ├── 03-ecosystem-integration.md                #   ⭐⭐ 生态协作：Router/Table/Form 与 Query 集成
│   └── 04-devtools.md                             #   ⭐ 开发工具链：Devtools 与 ESLint plugin
├── projects/                                      # 操作指南：实战项目（⭐ 递进）
│   ├── 01-todo-app.md                             #   ⭐ Todo App：Query CRUD 标准范式
│   ├── 02-data-dashboard.md                       #   ⭐⭐ 数据看板：Table + Query 分页/排序/筛选
│   ├── 03-collaborative-kanban.md                 #   ⭐⭐ 协作看板：乐观更新 + 实时同步
│   └── 04-saas-admin-platform.md                  #   ⭐⭐⭐ SaaS 后台：生产级平台
├── testing/                                       # 操作指南：测试工程
│   ├── 01-unit-testing.md                         #   ⭐⭐ 单元测试（Vitest）
│   ├── 02-mocking-server.md                       #   ⭐⭐ Mock 服务（MSW）
│   ├── 03-integration-testing.md                  #   ⭐⭐ 集成测试（Testing Library + renderHook）
│   └── 04-e2e-testing.md                          #   ⭐⭐ 端到端测试（Playwright）
├── deployment/                                    # 操作指南：部署运维
│   ├── 01-ci-cd-pipelines.md                      #   ⭐⭐ CI/CD 流水线（GitHub Actions）
│   ├── 02-vercel-deployment.md                    #   ⭐⭐ Vercel 部署：SPA 与 SSR 双路径
│   └── 03-observability.md                        #   ⭐⭐⭐ 可观测性（Sentry / Web Vitals）
└── advanced-topics/                               # 深度解释：原理与架构（均 ⭐⭐⭐）
    ├── architecture/
    │   └── 01-cache-architecture.md               #   Query 缓存架构与数据流
    ├── performance/
    │   ├── 01-query-optimization.md               #   查询性能优化
    │   └── 02-rendering-performance.md            #   渲染性能：重渲染治理与虚拟化
    └── security/
        └── 01-security-practices.md               #   安全实践
```

---

## 🔗 关联模块

- **前置**：[02-nextjs-frontend](../02-nextjs-frontend/README.md) - React/Next.js 基础与本模块互补
- **后端对接**：[01-go-backend](../01-go-backend/README.md) - Query 消费的 API 由 Go 后端提供
- **后续**：[04-multiplatform-apps](../04-multiplatform-apps/README.md) - React Native 可复用 Query 等库

---

**模块状态**: ✅ 内容建设中（basics/reference/frameworks/projects/testing/deployment/advanced-topics 均已有内容）
**最后更新**: 2026年9月
