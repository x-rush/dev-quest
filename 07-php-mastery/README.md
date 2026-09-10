# PHP 精通之路 - 温故知新

> 面向在职 PHP 开发者的温故知新模块：以 **PHP 8.3+（枚举 / readonly / 一等 callable 语法）+ Composer + Laravel 11（Artisan / Eloquent / 队列）+ PHPUnit / Pest** 为技术栈基线，采用 Diátaxis 双轴框架组织内容，实现从"会用"到"精通"的跃升。本模块属**技术探索系列**，适合零散时间学习，建议每天 30 分钟到 1 小时。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 模块总览 |
| **难度** | ⭐ 至 ⭐⭐⭐（按路径渐进） |
| **标签** | `#PHP` `#Laravel` `#Composer` `#PHPUnit` `#Pest` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- 巩固 PHP 基础，系统掌握 PHP 8.x 现代特性与最佳实践
- 深入理解 Laravel 11 框架体系，从路由到生产级架构
- 建立测试工程与部署运维的完整工程能力
- 通过 4 个递进项目积累可复用的实战经验

## 🧭 四象限导览

| 象限 | 目录 | 内容 | 访问方式 |
|------|------|------|---------|
| **教程** | [basics/](./basics/) | 8 篇按序入门：环境搭建 → 语言基础 → 现代 OOP → 错误处理 → 高级特性 → 综合项目 | 按编号顺序学 |
| **字典** | [reference/](./reference/) | 11 篇全量参考：关键字、内置函数、类型与 OOP、数组模式、Laravel/Symfony 速查、故障排除 | 按需跳入，无难度门槛 |
| **操作指南** | [frameworks/](./frameworks/) · [projects/](./projects/) · [testing/](./testing/) · [deployment/](./deployment/) | Laravel 入门/进阶/生态/工具链；4 个 ⭐ 递进项目；PHPUnit/Pest/Feature 测试；Docker/服务器/CI-CD 部署 | 面向目标，照做即可 |
| **解释** | [advanced-topics/](./advanced-topics/) | 架构解析、查询优化、缓存与队列、安全实践 | 为什么这样设计 |

> **单一事实来源**：概念的完整解释只在 `reference/` 存在一份，其他目录链接过去，不重复展开。

## 🛤️ 学习路径

### 入门路径（⭐）

[环境搭建](./basics/01-environment-setup.md) → [第一个脚本](./basics/02-first-script.md) → [变量与类型](./basics/03-variables-types.md) → [函数与 OOP](./basics/04-functions-oop.md) → [控制流程](./basics/05-control-flow.md) → [错误与异常](./basics/06-error-exceptions.md) → [Laravel 入门](./frameworks/01-laravel-basics.md) → [开发工具链](./frameworks/04-devtools.md) → [TODO REST API](./projects/01-todo-api.md)

### 进阶路径（⭐⭐）

[PHP 高级特性](./basics/07-advanced-features.md) → [Laravel 进阶](./frameworks/02-laravel-advanced.md) → [生态集成](./frameworks/03-ecosystem-integration.md) → [单元测试](./testing/01-unit-testing.md) → [Pest 测试](./testing/02-pest-testing.md) → [Feature 测试](./testing/03-feature-testing.md) → [容器化部署](./deployment/01-docker-deployment.md) → [服务器部署](./deployment/02-server-deployment.md) → [博客平台](./projects/02-blog-platform.md) → [电商 API](./projects/03-ecommerce-api.md)

### 精通路径（⭐⭐⭐）

[Laravel 架构解析](./advanced-topics/architecture/01-laravel-architecture.md) → [查询优化](./advanced-topics/performance/01-query-optimization.md) → [缓存与队列调优](./advanced-topics/performance/02-caching-queues.md) → [安全实践](./advanced-topics/security/01-security-practices.md) → [CI/CD 与可观测性](./deployment/03-ci-cd-observability.md) → [生产级 Laravel 应用](./projects/04-production-laravel-app.md)

## 📁 文件树

```text
07-php-mastery/
├── README.md                                # 本文档
├── basics/                                  # 教程：按序学习
│   ├── 01-environment-setup.md              # ⭐ 环境搭建
│   ├── 02-first-script.md                   # ⭐ 第一个脚本
│   ├── 03-variables-types.md                # ⭐ 变量与类型
│   ├── 04-functions-oop.md                  # ⭐ 函数与 OOP
│   ├── 05-control-flow.md                   # ⭐ 控制流程
│   ├── 06-error-exceptions.md               # ⭐ 错误与异常
│   ├── 07-advanced-features.md              # ⭐⭐ 高级特性
│   └── 08-first-project.md                  # ⭐ 综合练习：CLI 任务工具
├── reference/                               # 字典：全量参考
│   ├── language-concepts/
│   │   ├── 01-php-keywords.md               # 关键字详解
│   │   ├── 02-built-in-functions.md         # 内置函数
│   │   ├── 03-types-oop-modern.md           # 类型系统与现代 OOP
│   │   ├── 04-control-flow.md               # 控制流程
│   │   └── 05-arrays-patterns.md            # 数组与常用模式
│   ├── framework-essentials/
│   │   ├── 01-laravel-essentials.md         # Laravel 核心速查
│   │   └── 02-symfony-essentials.md         # Symfony 核心速查
│   ├── library-guides/
│   │   ├── 01-standard-library-spl.md       # 标准库 SPL
│   │   └── 02-composer-ecosystem.md         # Composer 生态
│   └── quick-references/
│       ├── 01-php-cheatsheet.md             # PHP 快速速查表
│       └── 02-troubleshooting.md            # 故障排除
├── frameworks/                              # 操作指南：框架生态
│   ├── 01-laravel-basics.md                 # ⭐ Laravel 入门
│   ├── 02-laravel-advanced.md               # ⭐⭐ Laravel 进阶
│   ├── 03-ecosystem-integration.md          # ⭐⭐ 生态集成
│   └── 04-devtools.md                       # ⭐ 开发工具链
├── projects/                                # 操作指南：实战项目（⭐ 递进）
│   ├── 01-todo-api.md                       # ⭐ TODO REST API
│   ├── 02-blog-platform.md                  # ⭐⭐ 博客平台
│   ├── 03-ecommerce-api.md                  # ⭐⭐ 电商 API
│   └── 04-production-laravel-app.md         # ⭐⭐⭐ 生产级 Laravel 应用
├── testing/                                 # 操作指南：测试工程
│   ├── 01-unit-testing.md                   # ⭐⭐ PHPUnit 单元测试
│   ├── 02-pest-testing.md                   # ⭐⭐ Pest 测试
│   └── 03-feature-testing.md                # ⭐⭐ Feature 测试与数据库测试
├── deployment/                              # 操作指南：部署运维
│   ├── 01-docker-deployment.md              # ⭐⭐ Docker 容器化部署
│   ├── 02-server-deployment.md              # ⭐⭐ Nginx + PHP-FPM 服务器部署
│   └── 03-ci-cd-observability.md            # ⭐⭐⭐ CI/CD 与可观测性
└── advanced-topics/                         # 解释：高级主题（⭐⭐⭐）
    ├── architecture/
    │   └── 01-laravel-architecture.md       # 服务容器与服务提供者
    ├── performance/
    │   ├── 01-query-optimization.md         # 查询优化
    │   └── 02-caching-queues.md             # 缓存策略与队列调优
    └── security/
        └── 01-security-practices.md         # 安全实践
```

## 💡 学习建议

- **温故知新**：从熟悉的 PHP 基础开始，对照 [PHP 8.3 特性](./reference/language-concepts/03-types-oop-modern.md) 找知识盲点
- **实战导向**：每完成一个阶段，用 [projects/](./projects/) 的对应项目验证
- **碎片学习**：概念疑难点直接查 [reference/](./reference/) 字典，不必按顺序
- **定期回顾**：每周末用 [快速速查表](./reference/quick-references/01-php-cheatsheet.md) 自测记忆

## 🔗 关联模块

- [01-go-backend](../01-go-backend/README.md) — Go 后端：与 PHP 后端对比学习并发模型与部署方式
- [08-java-revisited](../08-java-revisited/README.md) — Java 温故：同为运行时大厂栈，对照框架生态与工程实践

---

*最后更新：2026年9月*
