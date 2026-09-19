# PHP 精通之路 - 温故知新

> **本轮增强与版本核对**：学习路径及正文增强范围见 [逐文件台账](../shared-resources/tools/document-quality/reports/coverage.md)。下方技术基线中的旧核对日期属于历史记录，不表示这次已重跑所有平台；安装与升级以官方兼容要求、项目锁文件和实际构建结果为准。


第一次学习请从[理解地图与学习规划](LEARNING_GUIDE.md)开始，按其中的阶段任务和验收条件推进。先通过 CLI 脚本学习 PHP 类型、数组、函数和异常，再完成文件存储小工具，最后进入 Laravel API。不要求已有 PHP 工作经验；常驻进程与协程是后续专题。

查语法、函数或库时使用下方参考目录。文件数量与目录中的完成标记表示内容组织情况，不能替代示例运行证据；具体交付按[知识库质量基线](../shared-resources/standards/knowledge-delivery-baseline.md)验收。

> 面向会基本编程、希望学习 PHP 的读者，也供已有经验者查阅。语言部分解释脚本、类型、数组、对象与错误；应用部分逐步进入 Composer、Laravel、数据库和测试。每次围绕一个可验收的小任务推进，版本与扩展要求见下方基线。

## 🧪 技术基线

> 以下版本信息于 **2026-09-11** 经官方发布渠道核实，是本模块全部文档的编写基线。

| 技术 | 版本 | 核实日期 | 说明 |
|------|------|---------|------|
| **PHP** | 8.5（8.5.9） | 2026-09-11 | 2025-11-20 发布：管道运算符 `\|>`、URI 扩展、`#[\NoDiscard]`、`clone()` 批量覆盖（RFC clone_with_v2）等；8.4 属性钩子/非对称可见性一并纳入；8.4、8.3 仍在安全支持窗口内 |
| **Laravel** | 13 | 2026-09-11 | 2026-03-17 发布，要求 PHP 8.3-8.5；**Laravel 12**（2025-02-24）为上一个维护版，安全支持至 2027-02-24 |
| **Composer** | 2.x | 2026-09-11 | PHP 生态事实标准的依赖管理器 |
| **PHPUnit** | 13.x | 2026-09-11 | 2026-02-06 发布，要求 PHP 8.4+；PHP 8.3 项目使用 PHPUnit 12（支持至 2027-02） |
| **Pest** | 5.x | 2026-09-11 | 基于 PHPUnit 13，要求 PHP 8.4+；PHP 8.3 项目使用 Pest 4 |

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 模块总览 |
| **难度** | ⭐ 至 ⭐⭐⭐（按路径渐进） |
| **标签** | `#PHP` `#Laravel` `#Composer` `#PHPUnit` `#Pest` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- 用数组、函数和对象表达业务，解释类型转换、返回值和异常的边界。
- 从 CLI 文件小工具进入 Laravel 请求处理，验证校验失败、不存在数据和存储错误。
- 用测试记录接口与数据行为，在独立环境复现依赖安装和启动。
- 完成基础服务后比较传统请求与常驻 worker 的状态生命周期，再按需要学习队列与协程。

## 🧭 四象限导览

| 象限 | 目录 | 内容 | 访问方式 |
|------|------|------|---------|
| **教程** | [basics/](./basics/) | 8 篇教程：环境搭建 → 语言基础 → OOP → 错误处理 → 综合项目；高级特性按需补齐 | 按导读的能力顺序学习 |
| **字典** | [reference/](./reference/) | 29 篇全量参考：关键字、内置函数、类型与 OOP、数组模式、生成器、命名空间与自动加载、反射、字符串与正则、日期时间、异常体系、PHP 8.4/8.5 增量特性、弱比较与强比较、值语义与引用、超全局变量、运算符、魔术方法、常量与魔术常量、PDO/JSON、文件与流 I/O、HTTP/会话/Cookie、扩展地图、Laravel/Symfony 速查、故障排除 | 按需跳入，可独立查阅，仍有前置知识 |
| **操作指南** | [frameworks/](./frameworks/) · [projects/](./projects/) · [testing/](./testing/) · [deployment/](./deployment/) | Laravel 13 入门/进阶/生态/工具链；4 个 ⭐ 递进项目；PHPUnit/Pest/Feature 测试；Docker/服务器/CI-CD 部署 | 面向目标，照做即可 |
| **解释** | [advanced-topics/](./advanced-topics/) | 4 个专题目录：架构解析、查询优化、缓存与队列、安全实践、运行时专题（FPM vs 常驻 / Workerman / Webman / Swoole 协程） | 为什么这样设计 |

> **单一事实来源**：完整参考以 `reference/` 为主；教程就地解释当前步骤所需概念，再链接完整条目。

## 🛤️ 学习路径

### 入门路径（⭐）

[环境搭建](./basics/01-environment-setup.md) → [第一个脚本](./basics/02-first-script.md) → [变量与类型](./basics/03-variables-types.md) → [函数与 OOP](./basics/04-functions-oop.md) → [控制流程](./basics/05-control-flow.md) → [错误与异常](./basics/06-error-exceptions.md) → [CLI 任务工具](./basics/08-first-project.md) → [Laravel 入门](./frameworks/01-laravel-basics.md) → [开发工具链](./frameworks/04-devtools.md) → [TODO REST API](./projects/01-todo-api.md)

> 枚举前置：[TODO REST API](./projects/01-todo-api.md) 直接使用 Backed Enum 与 `enum:` 校验规则，开工前先读 [高级特性](./basics/07-advanced-features.md) 的"枚举"一节（⭐⭐ 文档按需单读即可，不必整篇学完）。

### 进阶路径（⭐⭐）

[PHP 高级特性](./basics/07-advanced-features.md) → [Laravel 进阶](./frameworks/02-laravel-advanced.md) → [生态集成](./frameworks/03-ecosystem-integration.md) → [单元测试](./testing/01-unit-testing.md) → [Pest 测试](./testing/02-pest-testing.md) → [Feature 测试](./testing/03-feature-testing.md) → [容器化部署](./deployment/01-docker-deployment.md) → [服务器部署](./deployment/02-server-deployment.md) → [博客平台](./projects/02-blog-platform.md) → [电商 API](./projects/03-ecommerce-api.md)

### 精通路径（⭐⭐⭐）

[Laravel 架构解析](./advanced-topics/architecture/01-laravel-architecture.md) → [查询优化](./advanced-topics/performance/01-query-optimization.md) → [缓存与队列调优](./advanced-topics/performance/02-caching-queues.md) → [安全实践](./advanced-topics/security/01-security-practices.md) → [FPM vs 常驻内存](./advanced-topics/runtime/01-fpm-vs-resident.md) → [Workerman 原理](./advanced-topics/runtime/02-workerman-principles.md) → [Webman 实战](./advanced-topics/runtime/03-webman-practice.md) → [Swoole 协程生态](./advanced-topics/runtime/04-swoole-ecosystem.md) → [CI/CD 与可观测性](./deployment/03-ci-cd-observability.md) → [生产级 Laravel 应用](./projects/04-production-laravel-app.md)

## 📁 文件树

```text
07-php-mastery/
├── README.md                                # 本文档
├── basics/                                  # 教程：按序学习
│   ├── 01-environment-setup.md              # ⭐ 环境搭建（PHP 8.5+）
│   ├── 02-first-script.md                   # ⭐ 第一个脚本
│   ├── 03-variables-types.md                # ⭐ 变量与类型
│   ├── 04-functions-oop.md                  # ⭐ 函数与 OOP
│   ├── 05-control-flow.md                   # ⭐ 控制流程
│   ├── 06-error-exceptions.md               # ⭐ 错误与异常
│   ├── 07-advanced-features.md              # ⭐⭐ 高级特性（含 8.4/8.5 增量）
│   └── 08-first-project.md                  # ⭐ 综合练习：CLI 任务工具
├── reference/                               # 字典：全量参考
│   ├── language-concepts/
│   │   ├── 01-php-keywords.md               # 关键字详解
│   │   ├── 02-built-in-functions.md         # 内置函数
│   │   ├── 03-types-oop-modern.md           # 类型系统与现代 OOP
│   │   ├── 04-control-flow.md               # 控制流程
│   │   ├── 05-arrays-patterns.md            # 数组与常用模式
│   │   ├── 06-generators-iterators.md       # 生成器与迭代器
│   │   ├── 07-namespaces-autoloading.md     # 命名空间与自动加载
│   │   ├── 08-reflection-attributes.md      # 反射与属性注解
│   │   ├── 09-strings-regex.md              # 字符串与正则
│   │   ├── 10-datetime.md                   # 日期时间
│   │   ├── 11-errors-exceptions.md          # 异常体系与错误处理
│   │   ├── 12-modern-php-85.md              # PHP 8.4/8.5 增量特性
│   │   ├── 13-weak-comparison.md            # 弱比较与强比较（== / ===）
│   │   ├── 14-references-value-semantics.md # 值语义与引用（&）
│   │   ├── 15-superglobals.md               # 超全局变量
│   │   ├── 16-operators.md                  # 运算符全表与优先级
│   │   ├── 17-magic-methods.md              # 魔术方法全表
│   │   └── 18-constants-magic-constants.md  # 常量与魔术常量
│   ├── framework-essentials/
│   │   ├── 01-laravel-essentials.md         # Laravel 核心速查
│   │   └── 02-symfony-essentials.md         # Symfony 核心速查
│   ├── library-guides/
│   │   ├── 01-standard-library-spl.md       # 标准库 SPL
│   │   ├── 02-composer-ecosystem.md         # Composer 生态
│   │   ├── 03-pdo.md                        # PDO 数据库访问层
│   │   ├── 04-json.md                       # JSON 编解码
│   │   ├── 05-file-stream-io.md             # 文件与流 I/O
│   │   ├── 06-http-session-cookie.md        # HTTP、会话与 Cookie
│   │   └── 07-extension-map.md              # 内置扩展地图
│   └── quick-references/
│       ├── 01-php-cheatsheet.md             # PHP 快速速查表
│       └── 02-troubleshooting.md            # 故障排除
├── frameworks/                              # 操作指南：框架生态
│   ├── 01-laravel-basics.md                 # ⭐ Laravel 13 入门
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
    ├── security/
    │   └── 01-security-practices.md         # 安全实践
    └── runtime/
        ├── 01-fpm-vs-resident.md            # FPM vs 常驻内存模型
        ├── 02-workerman-principles.md       # Workerman 事件驱动与多进程
        ├── 03-webman-practice.md            # Webman 实战
        └── 04-swoole-ecosystem.md           # Swoole 协程生态
```

## 💡 学习建议

- **温故知新**：从熟悉的 PHP 基础开始，对照 [类型系统与现代 OOP](./reference/language-concepts/03-types-oop-modern.md) 与 [PHP 8.4/8.5 增量特性](./reference/language-concepts/12-modern-php-85.md) 找知识盲点
- **实战导向**：每完成一个阶段，用 [projects/](./projects/) 的对应项目验证
- **碎片学习**：概念疑难点直接查 [reference/](./reference/) 字典，不必按顺序
- **定期回顾**：每周末用 [快速速查表](./reference/quick-references/01-php-cheatsheet.md) 自测记忆
- **拓宽视野**：写惯 FPM + Laravel 后，读一读 [运行时专题](./advanced-topics/runtime/01-fpm-vs-resident.md)，理解 PHP 的另一种打开方式

## 🔗 关联模块

- [01-go-backend](../01-go-backend/README.md) — Go 后端：与 PHP 后端对比学习并发模型与部署方式
- [08-java-revisited](../08-java-revisited/README.md) — Java 温故：同为运行时大厂栈，对照框架生态与工程实践

---

*最后更新：2026年9月*
