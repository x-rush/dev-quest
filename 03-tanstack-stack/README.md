# TanStack 全家桶学习

## 📚 模块概述

本模块系统学习 TanStack 生态的核心库（Query、Table、Router、Form、Start），掌握现代 React 应用的服务端状态管理、数据表格、类型安全路由与全栈框架开发能力。TanStack 是 Headless（无头）设计哲学的代表，与 02-nextjs-frontend 的框架学习互补，重点在于可组合、可定制的数据层技术。

### 🎯 学习目标

- 掌握 **TanStack Query**：服务端状态管理、缓存、失效与乐观更新
- 掌握 **TanStack Table**：Headless 表格构建、排序、筛选、分页、行内编辑
- 掌握 **TanStack Router**：100% 类型安全的文件式路由、搜索参数状态管理
- 掌握 **TanStack Form**：Headless 表单状态管理与校验集成
- 了解 **TanStack Start**：基于 Router 与 Query 的全栈 SSR 框架
- 理解 Headless 库设计模式，能与任意 UI 体系（Tailwind、shadcn/ui 等）组合

### 📁 规划目录结构

> 本模块尚未完成内容建设，以下为目标结构（参照 [shared-resources/standards/module-structure-guide.md](../shared-resources/standards/module-structure-guide.md)），内容将随后续重构逐步补齐。

```
03-tanstack-stack/
├── README.md                       # 本文档
├── basics/                          # 基础入门
│   ├── 01-environment-setup.md     # 环境搭建与项目初始化
│   ├── 02-headless-philosophy.md   # Headless设计哲学
│   ├── 03-query-fundamentals.md    # Query基础：useQuery/useMutation
│   ├── 04-table-fundamentals.md   # Table基础：核心列模型
│   ├── 05-router-fundamentals.md  # Router基础：路由树与类型安全
│   └── 06-form-fundamentals.md    # Form基础：表单状态管理
├── advanced-topics/                # 高级主题
│   ├── query-advanced/             # Query进阶（缓存策略、乐观更新、无限查询）
│   ├── table-advanced/             # Table进阶（虚拟化、行分组、可编辑表格）
│   ├── router-advanced/            # Router进阶（搜索参数、预加载、嵌套布局）
│   └── start-framework/            # Start全栈框架（SSR、API路由、服务端函数）
├── reference/               # 知识字典（全量参考）
│   ├── query-recipes/              # Query常见模式速查
│   ├── table-recipes/              # Table常见模式速查
│   └── router-recipes/             # Router常见模式速查
├── frameworks/                     # 生态集成
│   ├── 01-react-integration.md    # 与React/Vite集成
│   ├── 02-nextjs-integration.md    # 在Next.js中使用TanStack库
│   ├── 03-ui-integration.md       # 与Tailwind/shadcn/ui组合
│   └── 04-devtools.md              # TanStack Devtools
├── projects/                       # 实战项目
│   ├── 01-data-dashboard.md        # 数据仪表板（Query+Table）
│   ├── 02-admin-crud.md            # 管理后台CRUD（Table+Form）
│   ├── 03-typed-app.md             # 类型安全应用（Router+Query）
│   └── 04-fullstack-start.md       # Start全栈应用
├── testing/                        # 测试工程
│   ├── 01-query-testing.md         # Query测试（Mock、msw）
│   └── 02-router-testing.md       # Router测试
└── deployment/                     # 部署运维
    └── 01-deployment.md            # 部署与性能优化
```

### 🗺️ 学习路径

```mermaid
graph LR
    A[Headless理念] --> B[Query基础]
    B --> C[Table基础]
    C --> D[Router基础]
    D --> E[Form基础]
    E --> F[项目实战]
    F --> G[Start全栈]
```

### 🔗 关联模块

- **前置**: [02-nextjs-frontend](../02-nextjs-frontend/) - React/Next.js 基础
- **后续**: [04-multiplatform-apps](../04-multiplatform-apps/) - React Native（可复用 Query 等库）

---

**模块状态**: 📋 规划中（结构已建立，内容待建设）
**最后更新**: 2026年9月
