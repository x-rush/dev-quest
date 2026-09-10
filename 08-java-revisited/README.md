# Java 知识回顾与现代化

## 📚 模块简介

本模块面向**有 Java 开发经验的学习者**，旨在回顾 Java 核心知识、掌握 Java 21 LTS 与 Spring Boot 3.x 的现代化开发模式，并将 Java 设计思想与其他技术栈进行对比迁移。

- **技术栈基线**：Java 21 LTS（虚拟线程、Record、模式匹配、Sealed 类）· Spring Boot 3.x（Jakarta EE 命名空间）· Maven/Gradle · JUnit 5
- **模块定位**：从"Java 8 时代经验"升级到现代 Java 全栈能力，覆盖语言特性、Spring 生态、测试工程、容器化部署与生产级架构

### 🎯 学习目标

- 回顾 Java 核心概念和最佳实践
- 掌握 Java 17/21 新特性与现代化开发模式（Record、模式匹配、虚拟线程）
- 系统化掌握 Spring Boot 3.x 全栈：数据访问、安全、消息、测试、部署
- 将 Java 设计思想应用到其他技术栈，建立跨语言的知识体系

## 🧭 四象限导览

| 象限 | 目录 | 内容 | 用法 |
|------|------|------|------|
| **教程** | [basics/](basics/) | 8 篇按序学习：环境 → 语法 → OOP/Record → 控制流 → 异常 → 现代特性 → 项目 | 零散时间按序过一遍 |
| **字典** | [reference/](reference/) | 11 篇全量参考：语言概念、Spring/JPA 速查、标准库、故障排除 | 查字典，任意跳入 |
| **操作指南** | [frameworks/](frameworks/) [projects/](projects/) [testing/](testing/) [deployment/](deployment/) | Spring Boot 生态 4 篇 · 实战项目 4 个 · 测试工程 3 篇 · 部署运维 3 篇 | 面向任务，照做即成 |
| **解释** | [advanced-topics/](advanced-topics/) | 架构演进 · JVM/GC · 虚拟线程 · 安全实践 | 深挖"为什么" |

## 🛤️ 学习路径

### 入门路径（⭐）

[环境搭建](basics/01-environment-setup.md) → [第一个程序](basics/02-first-program.md) → [变量与类型](basics/03-variables-types.md) → [类、接口与 Record](basics/04-classes-records.md) → [控制流程](basics/05-control-flow.md) → [异常处理](basics/06-exceptions.md) → [第一个项目](basics/08-first-project.md) → [Spring Boot 入门](frameworks/01-spring-boot-basics.md) → [开发工具链](frameworks/04-devtools.md) → [TODO API 项目](projects/01-todo-api.md)

### 进阶路径（⭐⭐）

[现代 Java 特性](basics/07-modern-features.md) → [Spring Boot 进阶](frameworks/02-spring-boot-advanced.md) → [生态集成](frameworks/03-ecosystem-integration.md) → [单元测试](testing/01-unit-testing.md) → [集成测试](testing/02-integration-testing.md) → [API 测试](testing/03-api-testing.md) → [Docker 部署](deployment/01-docker-deployment.md) → [图书管理系统](projects/02-library-management.md) → [订单系统](projects/03-order-system.md)

### 精通路径（⭐⭐⭐）

[分层与六边形架构](advanced-topics/architecture/01-layered-architecture.md) → [JVM 调优与 GC 基础](advanced-topics/performance/01-jvm-tuning.md) → [虚拟线程并发模型](advanced-topics/performance/02-virtual-threads.md) → [安全最佳实践](advanced-topics/security/01-security-practices.md) → [K8s 部署](deployment/02-kubernetes-deployment.md) → [CI/CD 与可观测性](deployment/03-ci-cd-observability.md) → [生产级 Spring Boot 应用](projects/04-production-spring-app.md)

> 概念疑问随时跳转 [reference/](reference/) 字典：概念解释只此一份，全模块共享。

## 📁 实际文件树

```
08-java-revisited/
├── README.md                          # 本文档
├── basics/                            # 教程：按序学习
│   ├── 01-environment-setup.md        # ⭐ 环境搭建
│   ├── 02-first-program.md            # ⭐ 第一个程序
│   ├── 03-variables-types.md          # ⭐ 变量与类型
│   ├── 04-classes-records.md          # ⭐ 类、接口与 Record
│   ├── 05-control-flow.md             # ⭐ 控制流程
│   ├── 06-exceptions.md               # ⭐ 异常处理
│   ├── 07-modern-features.md          # ⭐⭐ 现代 Java 特性（Lambda/Stream/虚拟线程）
│   └── 08-first-project.md            # ⭐ 第一个项目
├── reference/                         # 字典：全量参考，无难度门槛
│   ├── language-concepts/
│   │   ├── 01-java-keywords.md        # Java 关键字详解
│   │   ├── 02-collections-generics.md # 集合与泛型
│   │   ├── 03-streams-optional.md     # Stream 与 Optional
│   │   ├── 04-concurrency-api.md      # 并发 API
│   │   └── 05-records-sealed-patterns.md # Record / Sealed / 模式匹配
│   ├── framework-essentials/
│   │   ├── 01-spring-boot-essentials.md # Spring Boot 核心速查
│   │   └── 02-jpa-essentials.md         # JPA 核心速查
│   ├── library-guides/
│   │   ├── 01-standard-library.md     # 标准库
│   │   └── 02-third-party-libs.md     # 第三方库
│   └── quick-references/
│       ├── 01-java-cheatsheet.md      # 语法速查
│       └── 02-troubleshooting.md      # 故障排除
├── frameworks/                        # 操作指南：框架生态
│   ├── 01-spring-boot-basics.md       # ⭐ 依赖注入、自动配置、REST Controller
│   ├── 02-spring-boot-advanced.md     # ⭐⭐ Spring Data JPA、事务、AOP
│   ├── 03-ecosystem-integration.md    # ⭐⭐ Security、Redis、消息队列
│   └── 04-devtools.md                 # ⭐ Maven/Gradle、DevTools、Actuator
├── projects/                          # 操作指南：实战项目（⭐ 递进）
│   ├── 01-todo-api.md                 # ⭐ TODO REST API
│   ├── 02-library-management.md       # ⭐⭐ 图书管理系统（JPA + 认证）
│   ├── 03-order-system.md             # ⭐⭐ 订单系统（事务 + 消息队列）
│   └── 04-production-spring-app.md    # ⭐⭐⭐ 生产级 Spring Boot 应用
├── testing/                           # 操作指南：测试工程
│   ├── 01-unit-testing.md             # ⭐⭐ JUnit 5 + Mockito
│   ├── 02-integration-testing.md      # ⭐⭐ @SpringBootTest + Testcontainers
│   └── 03-api-testing.md              # ⭐⭐ MockMvc + REST Assured
├── deployment/                        # 操作指南：部署运维
│   ├── 01-docker-deployment.md        # ⭐⭐ 容器化与分层镜像
│   ├── 02-kubernetes-deployment.md    # ⭐⭐⭐ K8s 部署概览
│   └── 03-ci-cd-observability.md      # ⭐⭐⭐ GitHub Actions + 可观测性
└── advanced-topics/                   # 解释：高级主题（均 ⭐⭐⭐）
    ├── architecture/01-layered-architecture.md  # 分层与六边形架构、DDD
    ├── performance/01-jvm-tuning.md             # JVM 调优与 GC 基础
    ├── performance/02-virtual-threads.md        # Java 21 虚拟线程并发模型
    └── security/01-security-practices.md        # Spring Security 最佳实践
```

## 💡 学习建议

### 🎯 针对有 Java 经验的学习者
- **经验复用**：利用已有的 Java 经验快速推进 basics，把时间投给 frameworks 与 projects
- **对比学习**：将 Spring Boot 与其他技术栈（Go/Node.js）的对应能力对照理解
- **思想迁移**：虚拟线程 vs Go goroutine、JVM 调优 vs 运行时内存模型——模式是相通的

### ⏰ 零散时间利用
- **概念回顾**：每次从 [reference/](reference/) 抽一个字典条目
- **特性追踪**：关注 Java LTS 节奏与 Spring Boot 版本列车
- **实战对比**：同一需求（如 TODO API）用不同语言实现，体会取舍

## 🔗 关联模块

| 模块 | 关联点 |
|------|--------|
| [01-go-backend](../01-go-backend/README.md) | 虚拟线程 vs goroutine、JVM vs Go 运行时、Spring Boot vs Go Web 框架 |
| [07-php-mastery](../07-php-mastery/README.md) | JVM 生态 vs PHP 生态、强类型 vs 动态类型工程化对比 |
| [09-nodejs-backend](../09-nodejs-backend/README.md) | 事件循环 vs 虚拟线程、NPM vs Maven/Gradle、Express vs Spring MVC |

## 📋 学习资源

- **官方文档**: [OpenJDK](https://openjdk.org/) · [Spring](https://spring.io/projects/spring-framework) · [Oracle Java Documentation](https://docs.oracle.com/en/java/)
- **推荐书籍**: 《Effective Java》(第3版) · 《Java 并发编程实战》 · 《Spring 实战》(第6版)
- **在线资源**: [Baeldung](https://www.baeldung.com/java) · [Spring Guides](https://spring.io/guides)

---

**学习价值**: 通过 Java 知识回顾与现代化，不仅能重温经典技术，更能建立跨语言的知识体系，提升技术选型和架构设计能力。

*最后更新: 2026年9月*
