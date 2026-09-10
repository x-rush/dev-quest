# Node.js 后端技术探索

## 📚 模块概述

本模块专为后端开发者设计，旨在系统学习 Node.js 后端开发技术，了解 JavaScript 在全栈开发中的应用，探索现代后端架构模式。属于 Dev Quest 双轨制中的**技术探索系列**，适合用零散时间渐进学习。

**技术栈基线**：Node.js 22 LTS · Express 5 · TypeScript 优先 · Prisma ORM · Vitest · pnpm

### 🎯 学习目标

- 掌握 Node.js 核心概念与异步编程模型（事件循环、Stream、Worker Threads）
- 熟练使用 Express 5 构建类型安全的后端 API 服务
- 理解现代后端工程实践：测试金字塔、容器化、CI/CD 与可观测性
- 建立性能与安全的原理级认知，能交付生产级 Node.js 服务

### 📖 学习建议

- **有后端经验**：用"概念对比"快速穿过 basics，把重心放在框架与架构层
- **零散时间**：每次吃透一个主题 + 动手跑通配套代码；reference 是你的随身字典
- **单一事实来源**：概念的完整解释只在 `reference/` 存在一处，其他文档链接过去

## 🧭 四象限导览

| 象限 | 回答的问题 | 目录 | 内容 |
|------|-----------|------|------|
| **教程** | "带我入门，走一遍" | `basics/` | 8 篇渐进教程：环境 → 服务器 → 模块 → 异步 → 路由 → 错误 → 流 → 首项目 |
| **字典** | "X 的语法/参数是什么" | `reference/` | 11 篇全量参考：语言概念 5 / 框架速查 2 / 库指南 2 / 速查排错 2 |
| **操作指南** | "怎么完成这个任务" | `frameworks/` `projects/` `testing/` `deployment/` | Express 与生态 4 篇 · 实战项目 4 个 · 测试 3 篇 · 部署 3 篇 |
| **解释** | "为什么这样设计" | `advanced-topics/` | 架构 1 · 性能 2 · 安全 1，均 ⭐⭐⭐ |

## 🛤️ 学习路径

### 入门路径（⭐）

[环境搭建](basics/01-environment-setup.md) → [第一个 HTTP 服务器](basics/02-first-server.md) → [模块系统与 ESM](basics/03-modules-esm.md) → [异步编程](basics/04-async-promises.md) → [路由与中间件](basics/05-http-routing.md) → [错误处理](basics/06-error-handling.md) → [第一个完整项目](basics/08-first-project.md) → [Express 5 基础](frameworks/01-express-basics.md) → [开发工具链](frameworks/04-devtools.md) → [入门项目：TODO API](projects/01-todo-api.md)

### 进阶路径（⭐⭐）

[Stream 与多线程](basics/07-streams-workers.md) → [Express 5 进阶](frameworks/02-express-advanced.md) → [生态集成：Prisma + Redis](frameworks/03-ecosystem-integration.md) → [项目：认证服务](projects/02-auth-service.md) → [项目：文件存储服务](projects/03-file-storage-service.md) → [单元测试](testing/01-unit-testing.md) → [集成测试](testing/02-integration-testing.md) → [端到端测试](testing/03-e2e-api-testing.md) → [容器化部署](deployment/01-docker-deployment.md) → [CI/CD 流水线](deployment/02-ci-cd-pipelines.md)

### 精通路径（⭐⭐⭐）

[服务架构与模块化单体](advanced-topics/architecture/01-service-architecture.md) → [事件循环原理](advanced-topics/performance/01-event-loop.md) → [流处理与集群](advanced-topics/performance/02-streaming-clustering.md) → [安全实践](advanced-topics/security/01-security-practices.md) → [可观测性](deployment/03-observability.md) → [精通项目：生产级 Node.js API](projects/04-production-nodejs-api.md)

> 查字典模式：不按路径走、只查条目，直接进 [reference/](reference/language-concepts/01-js-modern-syntax.md)。

## 📁 实际文件树

```
09-nodejs-backend/
├── README.md                                # 本文档：四象限导览 + 三路径视图
│
├── 📖 basics/                               # 教程：按序学习入门
│   ├── 01-environment-setup.md              # ⭐   Node.js 22 开发环境搭建
│   ├── 02-first-server.md                   # ⭐   第一个 HTTP 服务器
│   ├── 03-modules-esm.md                    # ⭐   模块系统与 ESM
│   ├── 04-async-promises.md                 # ⭐   异步编程：事件循环、Promise 与取消
│   ├── 05-http-routing.md                   # ⭐   路由、中间件与请求校验
│   ├── 06-error-handling.md                 # ⭐   错误处理与进程稳定性
│   ├── 07-streams-workers.md                # ⭐⭐ Stream 管道与多线程
│   └── 08-first-project.md                  # ⭐   第一个完整项目：任务管理 REST API
│
├── 📚 reference/                            # 字典：全量参考（本模块知识字典）
│   ├── language-concepts/                   # 语言核心概念
│   │   ├── 01-js-modern-syntax.md           # 现代 JavaScript 语法速查
│   │   ├── 02-async-api.md                  # 异步 API 全表
│   │   ├── 03-node-core-api.md              # Node 核心模块 API 速查
│   │   ├── 04-streams-api.md                # Stream API 速查
│   │   └── 05-typescript-patterns.md        # Node + TypeScript 常用模式
│   ├── framework-essentials/                # 框架核心要点
│   │   ├── 01-express-essentials.md         # Express 5 核心速查
│   │   └── 02-fastify-nestjs.md             # Fastify 与 NestJS 核心速查
│   ├── library-guides/                      # 标准库与三方库
│   │   ├── 01-core-modules.md               # 内置模块导航表
│   │   └── 02-ecosystem-libs.md             # 后端生态库精选
│   └── quick-references/                    # 纯速查表
│       ├── 01-node-cheatsheet.md            # Node 一行式速查
│       └── 02-troubleshooting.md            # 常见故障排除
│
├── 🏗️ frameworks/                           # 操作指南：框架生态
│   ├── 01-express-basics.md                 # ⭐   Express 5 快速上手
│   ├── 02-express-advanced.md               # ⭐⭐ 错误处理、认证中间件与文件上传
│   ├── 03-ecosystem-integration.md          # ⭐⭐ 生态集成：Prisma + PostgreSQL 与 Redis
│   └── 04-devtools.md                       # ⭐   开发工具链：pnpm、tsx 与 ESLint
│
├── 🚀 projects/                             # 操作指南：实战项目（⭐ 递进）
│   ├── 01-todo-api.md                       # ⭐   入门项目：TODO REST API
│   ├── 02-auth-service.md                   # ⭐⭐ 进阶项目：认证服务（JWT + 刷新令牌）
│   ├── 03-file-storage-service.md           # ⭐⭐ 进阶项目：文件存储服务（S3 兼容）
│   └── 04-production-nodejs-api.md          # ⭐⭐⭐ 精通项目：生产级 Node.js API
│
├── 🧪 testing/                              # 操作指南：测试工程
│   ├── 01-unit-testing.md                   # ⭐⭐ 单元测试：Vitest 实践
│   ├── 02-integration-testing.md            # ⭐⭐ 集成测试：Supertest + 测试数据库
│   └── 03-e2e-api-testing.md                # ⭐⭐ 端到端 API 测试策略
│
├── 🚀 deployment/                           # 操作指南：部署运维
│   ├── 01-docker-deployment.md              # ⭐⭐ 容器化部署：多阶段构建
│   ├── 02-ci-cd-pipelines.md                # ⭐⭐ CI/CD 流水线：GitHub Actions
│   └── 03-observability.md                  # ⭐⭐⭐ 可观测性：pino + OpenTelemetry/Sentry
│
└── 🎓 advanced-topics/                      # 深度解释：原理与架构（均 ⭐⭐⭐）
    ├── architecture/
    │   └── 01-service-architecture.md       # 服务架构：分层架构与模块化单体
    ├── performance/
    │   ├── 01-event-loop.md                 # 事件循环原理与性能陷阱
    │   └── 02-streaming-clustering.md       # 流处理与集群
    └── security/
        └── 01-security-practices.md         # 安全实践：helmet、注入防护与密钥管理
```

## 🔗 关联模块

- 🧭 [01-go-backend](../01-go-backend/README.md) — 应用帝国矩阵的核心后端模块；Go 与 Node 的并发模型、部署形态互为镜像参照
- 🖥️ [02-nextjs-frontend](../02-nextjs-frontend/README.md) — 本模块 API 服务的天然消费方；前后端以 TypeScript 共享类型与契约
- ☕ [08-java-revisited](../08-java-revisited/README.md) — 技术探索系列的另一后端视角；Spring 生态与 Node 生态的架构模式对照

## 📋 学习资源

- 官方文档：[Node.js](https://nodejs.org/docs/) · [Express 5](https://expressjs.com/) · [Prisma](https://www.prisma.io/docs) · [Vitest](https://vitest.dev/) · [TypeScript](https://www.typescriptlang.org/docs/)
- 深度阅读：《Node.js Design Patterns》 · [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- 中文社区：[MDN Web Docs - JavaScript](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript)

## 🔄 进度跟踪

- [x] Node.js 基础（basics 8 篇）
- [x] 知识字典（reference 11 篇）
- [x] 框架与生态（frameworks 4 篇）
- [x] 实战项目（projects 4 个）
- [x] 测试工程（testing 3 篇）
- [x] 部署运维（deployment 3 篇）
- [x] 高级主题（advanced-topics 4 篇）
- [ ] 实践校验：完成精通路径并交付生产级项目

---

**模块价值**：Node.js 作为 JavaScript 的后端运行时，具有高并发、轻量级的特点。掌握 Node.js 后端开发可以让你在全栈开发中更加游刃有余。

*最后更新：2026年9月*
