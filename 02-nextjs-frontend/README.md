# Next.js 全栈开发学习模块

> **文档简介**: 2024年最前沿的Next.js全栈开发学习体系，从零基础到高级应用的完整进阶路径
>
> **目标读者**: Web前端开发者、全栈开发者、React开发者
>
> **前置知识**: HTML/CSS基础、JavaScript ES6+基础、React基础概念
>
> **预计时长**: 3-6个月（根据学习进度和投入时间）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `module-overview` |
| **难度** | ⭐⭐⭐ |
| **标签** | `#模块概述` `#学习路线` `#nextjs15` `#全栈开发` |
| **更新日期** | 2025年10月 |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

完成本模块后，你将能够：

- ✅ **掌握Next.js 15**: 深入理解App Router、Server Components等核心特性
- ✅ **全栈应用开发**: 独立完成从前端到后端的完整应用开发
- ✅ **现代前端工程**: 掌握TypeScript 5、Tailwind CSS 4等现代工具链
- ✅ **性能优化**: 具备大型应用的性能分析和优化能力
- ✅ **生产部署**: 掌握Vercel、Docker等现代部署方案

## 📋 目录

- [模块概览](#模块概览)
- [学习路径](#学习路径)
- [技术栈](#技术栈)
- [文档结构](#文档结构)
- [学习建议](#学习建议)
- [相关资源](#相关资源)

---

## 🏗️ 模块概览

### 核心特色
- **📈 双路径学习**: 系统学习路径 + 快速参考路径，满足不同学习需求
- **🚀 技术前沿**: 100%基于Next.js 15 + React 19 + TypeScript 5最新技术栈
- **💼 实战导向**: 4个完整项目，从企业官网到SaaS平台
- **🧪 质量保证**: 完整的现代测试工程体系
- **⚡ 性能优先**: 深入的性能优化和监控体系

### 学习成果
- **初级开发者**: 掌握现代Next.js开发，能独立完成中小型项目
- **中级开发者**: 深入理解框架原理，具备大型应用开发能力
- **高级开发者**: 掌握性能优化和架构设计，具备技术领导能力

---

## 🎓 学习路径

### 📖 系统学习路径（初学者推荐）
```mermaid
graph TD
    A[环境搭建] --> B[第一个Next.js应用]
    B --> C[TypeScript集成]
    C --> D[布局路由设计]
    D --> E[Tailwind CSS样式]
    E --> F[数据获取基础]
    F --> G[状态管理]
    G --> H[第一个完整项目]
```

**适用对象**: 从零开始的学习者
**学习特点**: 渐进式教学，注重基础理解和实践练习
**建议时长**: 4-6周

### 🔍 快速参考路径（有经验开发者）
```mermaid
graph LR
    A[React语法速查] --> B[Next.js API参考]
    B --> C[框架实战模式]
    C --> D[开发工具]
    D --> E[性能优化]
```

**适用对象**: 有React基础的开发者
**学习特点**: 速查导向，快速上手现代Next.js开发
**建议时长**: 1-2周

---

## 🛠️ 技术栈

### 核心技术
- **Next.js 15**: React全栈框架，支持App Router和Server Components
- **React 19**: 最新React版本，并发特性和Suspense
- **TypeScript 5**: 类型安全的JavaScript超集
- **Tailwind CSS 4**: 原子化CSS框架

### 开发工具
- **Vitest**: 现代单元测试框架
- **Playwright**: 端到端测试框架
- **ESLint/Prettier**: 代码质量和格式化工具
- **Turbopack**: 快速构建工具

### 部署运维
- **Vercel**: Next.js官方云平台
- **Docker**: 容器化部署
- **GitHub Actions**: CI/CD自动化
- **Sentry**: 错误监控和性能分析

---

## 📁 目录结构

```
02-nextjs-frontend/
├── README.md                           # 模块总览（本文档）
├── 📚 knowledge-points/           # 知识点速查手册（18个文件）
│   ├── 📖 language-concepts/      # 语言核心概念（5个文件）
│   │   ├── 01-react-syntax-cheatsheet.md       # ⚛️ React语法速查表 ✅
│   │   ├── 02-nextjs-api-reference.md          # 🚀 Next.js API参考 ✅
│   │   ├── 03-typescript-types.md              # 📘 TypeScript类型速查 ✅
│   │   ├── 04-javascript-modern.md             # 💎 现代JS语法 ✅
│   │   └── 05-css-patterns.md                  # 🎨 CSS-in-JS模式 ✅
│   ├── 🛠️ framework-patterns/    # 框架应用模式（7个文件）
│   │   ├── 01-app-router-patterns.md           # 🗺️ App Router实战模式 ✅
│   │   ├── 02-server-components-patterns.md    # 🔄 服务端组件模式 ✅
│   │   ├── 03-client-components-patterns.md    # 📱 客户端组件模式 ✅
│   │   ├── 04-data-fetching-patterns.md        # 📡 数据获取模式 ✅
│   │   ├── 05-state-management-patterns.md     # 🗄️ 状态管理模式 ✅
│   │   ├── 06-form-validation-patterns.md      # 📝 表单验证模式 ✅
│   │   └── 07-authentication-flows.md          # 🔐 认证流程模式 ✅
│   ├── 🔧 development-tools/     # 开发工具生态（4个文件）
│   │   ├── 01-testing-tools.md                 # 🧪 测试工具指南 ✅
│   │   ├── 02-styling-tools.md                 # 🎨 样式工具 ✅
│   │   ├── 03-build-tools.md                   # ⚙️ 构建工具 ✅
│   │   └── 04-debugging-tools.md               # 🔍 调试工具 ✅
│   └── ⚡ performance-optimization/ # 性能优化专题（2个文件）
│       ├── 01-rendering-optimization.md        # 📈 渲染优化 ✅
│       └── 02-bundle-optimization.md           # 📦 打包优化 ✅
├── 📖 basics/                     # 渐进式学习路径（8个文件）
│   ├── 01-environment-setup.md                # 🛠️ 开发环境搭建 ✅
│   ├── 02-first-nextjs-app.md                 # 🚀 创建第一个Next.js应用 ✅
│   ├── 03-typescript-integration.md           # 📘 TypeScript集成配置 ✅
│   ├── 04-layouts-routing.md                  # 🗺️ 布局和路由设计 ✅
│   ├── 05-styling-with-tailwind.md            # 🎨 Tailwind CSS样式 ✅
│   ├── 06-data-fetching-basics.md             # 📡 基础数据获取 ✅
│   ├── 07-state-management.md                 # 🗄️ 状态管理基础 ✅
│   └── 08-first-project.md                    # 🎯 第一个完整项目 ✅
├── 🏗️ frameworks/                  # 框架深度学习（4个文件）
│   ├── 01-nextjs-15-complete.md               # 🚀 Next.js 15完整指南 ✅
│   ├── 02-react-19-integration.md             # ⚛️ React 19深度集成 ✅
│   ├── 03-full-stack-patterns.md              # 🌐 全栈开发模式 ✅
│   └── 04-performance-optimization.md         # ⚡ 性能优化最佳实践 ✅
├── 🚀 projects/                   # 实战项目（4个文件）
│   ├── 01-corporate-landing.md                # 🏢 企业官网项目 ✅
│   ├── 02-ecommerce-store.md                  # 🛒 电商应用项目 ✅
│   ├── 03-dashboard-analytics.md              # 📊 数据仪表板项目 ✅
│   └── 04-saas-platform.md                   # 💼 SaaS平台项目 ✅
├── 🧪 testing/                    # 现代测试工程（4个文件）
│   ├── 01-unit-testing.md                     # 🔬 单元测试（Vitest） ✅
│   ├── 02-component-testing.md                # 🧩 组件测试（Testing Library） ✅
│   ├── 03-e2e-testing.md                      # 🎭 端到端测试（Playwright） ✅
│   └── 04-performance-testing.md              # ⚡ 性能测试（Lighthouse） ✅
├── 🚀 deployment/                 # 现代应用部署（4个文件）
│   ├── 01-vercel-deployment.md                # ☁️ Vercel云端部署 ✅
│   ├── 02-docker-containerization.md          # 🐳 Docker容器化部署 ✅
│   ├── 03-ci-cd-pipelines.md                 # 🔄 CI/CD自动化流水线 ✅
│   └── 04-monitoring-analytics.md             # 📊 监控和分析（Sentry） ✅
└── 🎓 advanced-topics/            # 高级主题（6个文件）
    ├── ⚡ performance/            # 性能优化主题（2个文件）
    │   ├── 01-core-web-vitals.md              # 📈 Core Web Vitals优化 ✅
    │   └── 02-advanced-optimization.md        # 🚀 高级性能调优 ✅
    ├── 🔒 security/               # 安全实践主题（1个文件）
    │   └── 01-security-best-practices.md      # 🛡️ Web安全最佳实践 ✅
    ├── 🏛️ architecture/           # 架构设计主题（2个文件）
    │   ├── 01-scaling-patterns.md             # 📈 应用扩展模式 ✅
    │   └── 02-micro-frontends.md              # 🧩 微前端架构 ✅
    └── 🌐 api-integration/         # API集成主题（1个文件）
        └── 01-graphql-apollo.md               # 🔗 GraphQL + Apollo ✅
```

### 📚 Knowledge Points - 知识点速查手册（18个文件）
**定位**: 快速查找和理解核心概念，适合日常查阅
**特点**: 严格差异化设计，与basics无内容重叠

#### 📖 Language Concepts - 语言概念（5个文件）
- [`01-react-syntax-cheatsheet.md`](knowledge-points/language-concepts/01-react-syntax-cheatsheet.md) - ⚛️ React语法速查表
- [`02-nextjs-api-reference.md`](knowledge-points/language-concepts/02-nextjs-api-reference.md) - 🚀 Next.js API参考
- [`03-typescript-types.md`](knowledge-points/language-concepts/03-typescript-types.md) - 📘 TypeScript类型速查
- [`04-javascript-modern.md`](knowledge-points/language-concepts/04-javascript-modern.md) - 💎 现代JS语法
- [`05-css-patterns.md`](knowledge-points/language-concepts/05-css-patterns.md) - 🎨 CSS-in-JS模式

#### 🛠️ Framework Patterns - 框架模式（7个文件）
- [`01-app-router-patterns.md`](knowledge-points/framework-patterns/01-app-router-patterns.md) - 🗺️ App Router实战模式
- [`02-server-components-patterns.md`](knowledge-points/framework-patterns/02-server-components-patterns.md) - 🔄 服务端组件模式
- [`03-client-components-patterns.md`](knowledge-points/framework-patterns/03-client-components-patterns.md) - 📱 客户端组件模式
- [`04-data-fetching-patterns.md`](knowledge-points/framework-patterns/04-data-fetching-patterns.md) - 📡 数据获取模式
- [`05-state-management-patterns.md`](knowledge-points/framework-patterns/05-state-management-patterns.md) - 🗄️ 状态管理模式
- [`06-form-validation-patterns.md`](knowledge-points/framework-patterns/06-form-validation-patterns.md) - 📝 表单验证模式
- [`07-authentication-flows.md`](knowledge-points/framework-patterns/07-authentication-flows.md) - 🔐 认证流程模式

#### 🔧 Development Tools - 开发工具（4个文件）
- [`01-testing-tools.md`](knowledge-points/development-tools/01-testing-tools.md) - 🧪 测试工具指南
- [`02-styling-tools.md`](knowledge-points/development-tools/02-styling-tools.md) - 🎨 样式工具
- [`03-build-tools.md`](knowledge-points/development-tools/03-build-tools.md) - ⚙️ 构建工具
- [`04-debugging-tools.md`](knowledge-points/development-tools/04-debugging-tools.md) - 🔍 调试工具

#### ⚡ Performance Optimization - 性能优化（2个文件）
- [`01-rendering-optimization.md`](knowledge-points/performance-optimization/01-rendering-optimization.md) - 📈 渲染优化
- [`02-bundle-optimization.md`](knowledge-points/performance-optimization/02-bundle-optimization.md) - 📦 打包优化

### 📖 Basics - 渐进式学习路径（8个文件）
**定位**: 从零开始的完整学习体验，注重基础理解和实践

- [`01-environment-setup.md`](basics/01-environment-setup.md) - 🛠️ 开发环境搭建
- [`02-first-nextjs-app.md`](basics/02-first-nextjs-app.md) - 🚀 创建第一个Next.js应用
- [`03-typescript-integration.md`](basics/03-typescript-integration.md) - 📘 TypeScript集成配置
- [`04-layouts-routing.md`](basics/04-layouts-routing.md) - 🗺️ 布局和路由设计
- [`05-styling-with-tailwind.md`](basics/05-styling-with-tailwind.md) - 🎨 Tailwind CSS样式
- [`06-data-fetching-basics.md`](basics/06-data-fetching-basics.md) - 📡 基础数据获取
- [`07-state-management.md`](basics/07-state-management.md) - 🗄️ 状态管理基础
- [`08-first-project.md`](basics/08-first-project.md) - 🎯 第一个完整项目

### 🏗️ Frameworks - 框架深度学习（4个文件）
**定位**: 深入掌握框架和生态系统，专业能力提升

- [`01-nextjs-15-complete.md`](frameworks/01-nextjs-15-complete.md) - 🚀 Next.js 15完整指南
- [`02-react-19-integration.md`](frameworks/02-react-19-integration.md) - ⚛️ React 19深度集成
- [`03-full-stack-patterns.md`](frameworks/03-full-stack-patterns.md) - 🌐 全栈开发模式
- [`04-performance-optimization.md`](frameworks/04-performance-optimization.md) - ⚡ 性能优化最佳实践

### 🚀 Projects - 实战项目（4个文件）
**定位**: 通过真实项目巩固知识，积累实战经验

- [`01-corporate-landing.md`](projects/01-corporate-landing.md) - 🏢 企业官网项目
- [`02-ecommerce-store.md`](projects/02-ecommerce-store.md) - 🛒 电商应用项目
- [`03-dashboard-analytics.md`](projects/03-dashboard-analytics.md) - 📊 数据仪表板项目
- [`04-saas-platform.md`](projects/04-saas-platform.md) - 💼 SaaS平台项目

### 🧪 Testing - 现代测试工程（4个文件）
**定位**: 掌握测试方法，建立质量保证体系

- [`01-unit-testing.md`](testing/01-unit-testing.md) - 🔬 单元测试（Vitest）
- [`02-component-testing.md`](testing/02-component-testing.md) - 🧩 组件测试（Testing Library）
- [`03-e2e-testing.md`](testing/03-e2e-testing.md) - 🎭 端到端测试（Playwright）
- [`04-performance-testing.md`](testing/04-performance-testing.md) - ⚡ 性能测试（Lighthouse）

### 🚀 Deployment - 现代应用部署（4个文件）
**定位**: 掌握部署方法，具备生产环境运维能力

- [`01-vercel-deployment.md`](deployment/01-vercel-deployment.md) - ☁️ Vercel云端部署
- [`02-docker-containerization.md`](deployment/02-docker-containerization.md) - 🐳 Docker容器化部署
- [`03-ci-cd-pipelines.md`](deployment/03-ci-cd-pipelines.md) - 🔄 CI/CD自动化流水线
- [`04-monitoring-analytics.md`](deployment/04-monitoring-analytics.md) - 📊 监控和分析（Sentry）

### 🎓 Advanced Topics - 高级主题（6个文件）
**定位**: 深入理解高级概念，提升技术深度

#### ⚡ Performance - 性能优化（2个文件）
- [`01-core-web-vitals.md`](advanced-topics/performance/01-core-web-vitals.md) - 📈 Core Web Vitals优化
- [`02-advanced-optimization.md`](advanced-topics/performance/02-advanced-optimization.md) - 🚀 高级性能调优

#### 🔒 Security - 安全实践（1个文件）
- [`01-security-best-practices.md`](advanced-topics/security/01-security-best-practices.md) - 🛡️ Web安全最佳实践

#### 🏛️ Architecture - 架构设计（2个文件）
- [`01-scaling-patterns.md`](advanced-topics/architecture/01-scaling-patterns.md) - 📈 应用扩展模式
- [`02-micro-frontends.md`](advanced-topics/architecture/02-micro-frontends.md) - 🧩 微前端架构

#### 🌐 API Integration - API集成（1个文件）
- [`01-graphql-apollo.md`](advanced-topics/api-integration/01-graphql-apollo.md) - 🔗 GraphQL + Apollo

---

## 💡 学习建议

### 学习策略

#### 🎯 明确学习目标
- **初级目标**: 掌握基础开发，能完成简单项目
- **中级目标**: 理解框架原理，能独立开发
- **高级目标**: 具备架构能力，能指导团队

#### 📚 合理选择路径
- **零基础**: 推荐 `basics/` → `frameworks/` → `projects/` 顺序
- **有经验**: 可直接从 `knowledge-points/` 开始，结合 `projects/` 实践
- **专项提升**: 根据需要重点学习特定领域

#### 🛠️ 实践优先
- 每学完一个概念立即动手实践
- 跟随项目教程完成完整项目
- 在自己的项目中应用所学知识

### 时间安排

#### 📅 学习计划建议
- **每日投入**: 1-2小时
- **周目标**: 完成1-2个文档学习
- **月目标**: 完成一个主要领域（如basics或frameworks）
- **总体目标**: 3-6个月内完成整个模块

#### ⏰ 时间分配建议
- **理论学习**: 30%时间
- **代码实践**: 50%时间
- **项目练习**: 15%时间
- **复习总结**: 5%时间

---

## 🔗 相关资源

### 📖 官方文档
- **[Next.js 15 Docs](https://nextjs.org/docs)**: 官方权威文档
- **[React 19 Docs](https://react.dev/)**: React最新版本文档
- **[TypeScript 5 Docs](https://www.typescriptlang.org/docs/)**: TypeScript官方文档
- **[Tailwind CSS 4 Docs](https://tailwindcss.com/docs)**: CSS框架文档

### 🛠️ 开发工具
- **[Vercel Platform](https://vercel.com)**: Next.js部署平台
- **[VS Code Extensions](https://marketplace.visualstudio.com)**: 推荐扩展
- **[Chrome DevTools](https://developer.chrome.com/docs/devtools)**: 调试工具
- **[React DevTools](https://react.dev/learn/react-developer-tools)**: React调试工具

### 📹 学习资源
- **[Next.js 15 Course](https://nextjs.org/learn)**: 官方免费课程
- **[React 19 Tutorial](https://react.dev/learn)**: React官方教程
- **[TypeScript Handbook](https://www.typescriptlang.org/handbook)**: TypeScript手册
- **[Tailwind CSS Tutorial](https://tailwindcss.com/course)**: 样式框架教程

### 🌐 社区资源
- **[Next.js GitHub](https://github.com/vercel/next.js)**: 源码和问题讨论
- **[React GitHub](https://github.com/facebook/react)**: React源码仓库
- **[Stack Overflow](https://stackoverflow.com/questions/tagged/next.js)**: 问题解答
- **[Reddit r/nextjs](https://reddit.com/r/nextjs)**: 社区讨论

---

## 🤝 贡献与反馈

### 📝 内容贡献
欢迎参与文档完善：
- 🐛 **报告问题**: 发现错误或过时内容
- 💡 **建议改进**: 提出内容优化建议
- 📝 **参与贡献**: 提交PR完善文档

### 🎓 学习反馈
分享你的学习体验：
- ✅ **有用内容**: 哪些部分对你最有帮助
- ❓ **疑问点**: 哪些内容需要进一步澄清
- 🎯 **建议**: 希望增加什么内容

---

## 📊 模块统计

| 类别 | 文档数量 | 预计学习时长 |
|------|----------|--------------|
| Knowledge Points | 18个 | 20-30小时 |
| Basics | 8个 | 40-60小时 |
| Frameworks | 4个 | 30-40小时 |
| Projects | 4个 | 60-80小时 |
| Testing | 4个 | 20-30小时 |
| Deployment | 4个 | 15-25小时 |
| Advanced Topics | 6个 | 25-35小时 |
| **总计** | **48个** | **210-300小时** |

---

---

## 🔄 文档交叉引用

### 📚 核心学习资源
- 📄 **[React语法速查表](knowledge-points/language-concepts/01-react-syntax-cheatsheet.md)**: React核心语法和Hooks快速参考
- 📄 **[Next.js API参考](knowledge-points/language-concepts/02-nextjs-api-reference.md)**: Next.js完整API文档
- 📄 **[企业级认证流程](knowledge-points/framework-patterns/07-authentication-flows.md)**: 完整的认证实现指南
- 📄 **[第一个Next.js应用](basics/02-first-nextjs-app.md)**: 零基础入门指南

### 🎯 项目实践资源
- 🚀 **[企业官网项目](projects/01-corporate-landing.md)**: Next.js基础应用实践
- 🛒 **[电商应用项目](projects/02-ecommerce-store.md)**: 全栈电商开发实战
- 📊 **[数据仪表板项目](projects/03-dashboard-analytics.md)**: 数据可视化应用开发
- 💼 **[SaaS平台项目](projects/04-saas-platform.md)**: 企业级SaaS架构实践

### 🧪 质量保证体系
- 🔬 **[单元测试指南](testing/01-unit-testing.md)**: Vitest测试框架使用
- 🧩 **[组件测试指南](testing/02-component-testing.md)**: React Testing Library实践
- 🎭 **[E2E测试指南](testing/03-e2e-testing.md)**: Playwright端到端测试
- ⚡ **[性能测试指南](testing/04-performance-testing.md)**: Lighthouse性能测试

### ☁️ 部署运维资源
- ☁️ **[Vercel部署指南](deployment/01-vercel-deployment.md)**: 云端部署最佳实践
- 🐳 **[Docker容器化](deployment/02-docker-containerization.md)**: 容器化部署方案
- 🔄 **[CI/CD流水线](deployment/03-ci-cd-pipelines.md)**: 自动化部署流程
- 📊 **[监控分析](deployment/04-monitoring-analytics.md)**: 生产环境监控和分析

### 🎓 高级进阶主题
- 📈 **[Core Web Vitals优化](advanced-topics/performance/01-core-web-vitals.md)**: 性能指标优化
- 🛡️ **[Web安全最佳实践](advanced-topics/security/01-security-best-practices.md)**: 安全防护策略
- 📈 **[应用扩展模式](advanced-topics/architecture/01-scaling-patterns.md)**: 系统扩展架构
- 🔗 **[GraphQL + Apollo](advanced-topics/api-integration/01-graphql-apollo.md)**: 现代API集成

---

## 📝 总结

### 核心要点回顾
1. **现代化技术栈**: 基于2024年最新的Next.js 15 + React 19 + TypeScript 5
2. **差异化学习体系**: 快速参考路径和系统学习路径满足不同需求
3. **实战导向**: 4个完整项目覆盖从基础到企业级应用
4. **质量保证**: 完整的现代测试工程和部署运维体系
5. **高级进阶**: 涵盖性能优化、安全实践、架构设计等高级主题

### 学习成果检查
- [ ] 是否理解了模块的双路径学习体系？
- [ ] 是否选择了适合自己的学习路径？
- [ ] 是否掌握了Next.js 15的核心特性？
- [ ] 是否具备了全栈应用开发的基础能力？
- [ ] 是否了解了现代测试和部署的最佳实践？

### 🚀 下一步行动
1. **初学者**: 从 [basics/01-environment-setup.md](basics/01-environment-setup.md) 开始
2. **有经验者**: 从 [knowledge-points/language-concepts/](knowledge-points/language-concepts/) 开始快速查阅
3. **项目实践**: 选择 [projects/](projects/) 中的项目进行实战练习
4. **专项提升**: 根据需要深入学习 [testing/](testing/)、[deployment/](deployment/) 或 [advanced-topics/](advanced-topics/)

---

## 🤝 贡献与反馈

### 内容改进
如果你发现本文档有改进空间，欢迎：
- 🐛 **报告问题**: 在Issues中提出具体问题
- 💡 **建议改进**: 提出修改建议和补充内容
- 📝 **参与贡献**: 提交PR完善文档内容

### 学习反馈
分享你的学习体验：
- ✅ **有用内容**: 哪些部分对你最有帮助
- ❓ **疑问点**: 哪些内容需要进一步澄清
- 🎯 **建议**: 希望增加什么内容

---

## 🔗 外部资源

### 📖 官方文档
- 📚 **[Next.js 15 官方文档](https://nextjs.org/docs)**: 完整的框架文档
- ⚛️ **[React 19 官方文档](https://react.dev/)**: React最新版本指南
- 📘 **[TypeScript 5 官方文档](https://www.typescriptlang.org/docs/)**: 类型系统文档
- 🎨 **[Tailwind CSS 4 文档](https://tailwindcss.com/docs)**: CSS框架指南

### 🛠️ 开发工具
- ☁️ **[Vercel 平台](https://vercel.com)**: Next.js官方部署平台
- 🔧 **[VS Code](https://code.visualstudio.com/)**: 推荐的开发环境
- 🧪 **[Playwright](https://playwright.dev/)**: 现代端到端测试工具
- 📊 **[Chrome DevTools](https://developer.chrome.com/docs/devtools)**: 浏览器调试工具

---

**模块状态**: ✅ 重构完成
**最后更新**: 2025年10月
**版本**: v2.0.0

> 💡 **重构说明**:
> 本模块已于2025年10月完成重构，采用现代化的双路径学习体系，建立清晰的知识点速查手册和渐进式学习路径，100%基于Next.js 15 + React 19 + TypeScript 5最新技术栈，消除冗余内容，大幅提升学习效率和质量。

---

> 💡 **学习建议**:
> - 建议先浏览整个文档结构，了解学习路径
> - 根据自身基础选择合适的学习路径
> - 重视实践项目，理论结合实践
> - 遇到问题时积极查阅官方文档和社区资源
>
> 🎯 **下一步**: 根据你的学习目标，选择从 [basics/](basics/) 或 [knowledge-points/](knowledge-points/) 开始学习！