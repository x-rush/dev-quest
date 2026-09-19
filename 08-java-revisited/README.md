# Java 知识回顾与现代化

> **本轮增强与版本核对**：学习路径及正文增强范围见 [逐文件台账](../shared-resources/tools/document-quality/reports/coverage.md)。下方技术基线中的旧核对日期属于历史记录，不表示这次已重跑所有平台；安装与升级以官方兼容要求、项目锁文件和实际构建结果为准。


第一次学习请从[理解地图与学习规划](LEARNING_GUIDE.md)开始，按其中的阶段任务和验收条件推进。先从 javac、普通对象、集合和异常开始，完成控制台图书管理，再接 Spring 的对象装配与 HTTP。已有 Java 经验可以用阶段自测决定跳过哪些基础。

查语法、函数或库时使用下方参考目录。文件数量与目录中的完成标记表示内容组织情况，不能替代示例运行证据；具体交付按[知识库质量基线](../shared-resources/standards/knowledge-delivery-baseline.md)验收。

## 📚 模块简介

本模块面向会基本编程、初次接触 Java 的读者，也供已有经验者查阅。先理解类、接口、集合和异常，再用 Spring 组织请求与依赖；不会其他后端框架也可以沿导读入门。

- **技术栈基线**：Java 21 LTS 是教程默认编译基线；需要验证最新 LTS 特性时再选择 Java 25。框架示例采用 Spring Boot 4.1.x（Spring Framework 7 / Jakarta EE 11 命名空间）与 Maven 或 Gradle Wrapper。测试章节以项目锁定的 JUnit Jupiter 版本为准，不能从本文假定某个测试库版本已经可用。
- **模块定位**：语言参考与渐进实践并行，先完成普通 Java 小程序，再逐项接入 Spring、持久化、测试和部署

## 🧱 技术基线与升级动作（2026-09 核对）

“最新版本”不是课程的稳定知识。这里固定教学所需的语言基线，把会变化的框架和库版本交给构建文件、BOM 与官方兼容矩阵决定。创建或升级项目时，应先查看 [Spring Boot 系统要求](https://docs.spring.io/spring-boot/system-requirements.html) 和 [Spring Boot 当前发布线](https://spring.io/projects/spring-boot)，再修改 Wrapper 与依赖版本。

| 项目 | 教学默认 | 创建或升级时要验证什么 |
|------|------|------|
| Java | **21 LTS**；Java 25 用于额外的 LTS 对照 | `java -version`、`javac --release 21` 与项目 CI 使用同一 toolchain；不要因框架要求“至少 17”就误以为所有源码可使用更高版本 API。 |
| Spring Boot | **4.1.x** | 当前 4.1.1 要求 Java 17+、兼容至 Java 26；以生成项目的 BOM 管理 Spring Framework、Security、Jackson 等传递版本，避免手工拼一张会过期的版本表。 |
| Maven / Gradle | Maven **3.6.3+**；Gradle **8.14+ 或 9.x** | 只运行 `./mvnw` 或 `./gradlew`；将 Wrapper 文件提交进仓库，并在升级后执行完整测试。 |
| JUnit、Testcontainers、数据库驱动 | 由项目的 BOM 或显式锁文件决定 | 用实际的 `test` 任务和测试容器验证版本组合；版本号本身不证明迁移完成。 |
| GraalVM Native Image | 按目标 Boot 版本的系统要求选择 | 当前 Boot 4.1 文档要求 GraalVM 25+；先让 JVM 构建、测试、镜像构建都通过，再评估 native image。 |

本表只说明兼容与选择动作，不替代每个项目的依赖锁定与实际构建记录。

### 🎯 学习目标

- 解释值、引用、接口、集合和异常，并用普通对象完成一个可测试的业务功能。
- 比较手动传入依赖与 Spring 装配，知道对象从哪里产生、由谁调用。
- 将业务结果映射成 HTTP 响应；在后续练习中用真实测试数据库检查约束与事务。
- 按运行问题学习线程、JVM 与部署，区分语言版本特性与框架能力。

## 🧭 四象限导览

| 象限 | 目录 | 内容 | 用法 |
|------|------|------|------|
| **教程** | [basics/](basics/) | 8 篇按序学习：环境 → 语法 → OOP/Record → 控制流 → 异常 → 现代特性 → 项目 | 零散时间按序过一遍 |
| **字典** | [reference/](reference/) | 29 篇全量参考：语言核心概念（含字符串常量池/枚举/注解/接口语义）、Spring 核心（IoC/DI、AOP、事务、Security、REST 客户端）、Boot 3→4 迁移速查、标准库包导览与 JDK 包地图、故障排除 | 查字典，任意跳入 |
| **操作指南** | [frameworks/](frameworks/) [projects/](projects/) [testing/](testing/) [deployment/](deployment/) | Spring Boot 生态 4 篇 · 实战项目 4 个 · 测试工程 3 篇 · 部署运维 3 篇 | 先确认前置环境，再按任务实施与验收 |
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
├── reference/                         # 字典：全量参考，可独立查阅，仍有前置知识
│   ├── language-concepts/
│   │   ├── 01-java-keywords.md        # Java 关键字详解
│   │   ├── 02-collections-generics.md # 集合与泛型
│   │   ├── 03-streams-optional.md     # Stream 与 Optional
│   │   ├── 04-concurrency-api.md      # 并发 API
│   │   ├── 05-records-sealed-patterns.md # Record / Sealed / 模式匹配
│   │   └── 06-exceptions-resources.md # 异常体系与资源管理
│   ├── framework-essentials/
│   │   ├── 01-spring-boot-essentials.md # Spring Boot 核心速查
│   │   ├── 02-jpa-essentials.md         # JPA 核心速查
│   │   ├── 03-ioc-di-essentials.md      # IoC/DI 与 Bean 生命周期速查
│   │   ├── 04-aop-essentials.md         # AOP 速查
│   │   ├── 05-transaction-essentials.md # 事务传播与隔离速查
│   │   ├── 06-spring-security-essentials.md # Spring Security 7 速查
│   │   └── 07-rest-client-essentials.md # RestClient/HTTP 客户端速查
│   ├── library-guides/
│   │   ├── 01-standard-library.md     # 标准库
│   │   └── 02-third-party-libs.md     # 第三方库
│   └── quick-references/
│       ├── 01-java-cheatsheet.md      # 语法速查
│       ├── 02-troubleshooting.md      # 故障排除
│       └── 03-spring-boot4-migration.md # Boot 3→4 迁移速查
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
│   ├── 01-unit-testing.md             # ⭐⭐ JUnit 6 + Mockito
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
| [09-nodejs-backend](../09-nodejs-backend/README.md) | 事件循环 vs 虚拟线程、NPM vs Maven/Gradle、Hono vs Spring MVC |

## 📋 学习资源

- **官方文档**: [OpenJDK](https://openjdk.org/) · [Spring](https://spring.io/projects/spring-framework) · [Oracle Java Documentation](https://docs.oracle.com/en/java/)
- **推荐书籍**: 《Effective Java》(第3版) · 《Java 并发编程实战》 · 《Spring 实战》(第6版)
- **在线资源**: [Baeldung](https://www.baeldung.com/java) · [Spring Guides](https://spring.io/guides)

---

**学习价值**: 通过 Java 知识回顾与现代化，不仅能重温经典技术，更能建立跨语言的知识体系，提升技术选型和架构设计能力。

*最后更新: 2026年9月*
