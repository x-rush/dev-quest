# Python 发现之旅

## 📚 模块概述

本模块专为有其他编程语言经验的开发者设计，旨在系统学习 Python 编程语言，探索其在 **Web 后端开发、数据处理和自动化**领域的应用。

**技术栈基线**：Python 3.14（类型注解、match 语句）· uv 包管理 · FastAPI · Pydantic v2 · pytest · ruff

### 🧰 技术基线（核实日期：2026-09-11）

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.14（维护版 3.14.7） | 语言基线：类型注解、结构化模式匹配、t-string 模板字符串（PEP 750） |
| uv | 0.11+ | 包管理 + Python 解释器管理 |
| FastAPI | 0.141.1 | Web 框架主线（Pydantic v2 数据层） |
| Pydantic | v2（2.13.5） | 运行时数据校验 |
| Ruff | 0.16.6 | lint + format 一体化工具链 |

> 版本随时间推进，安装时以 `uv add` 解析到的最新稳定版为准；教程代码不依赖具体补丁版本。

### 🎯 学习目标

- 掌握 Python 3.14 基础语法与现代语言特性（类型注解、结构化模式匹配、模板字符串、异步）
- 熟练使用 uv / ruff / pytest / mypy 现代工具链
- 能独立构建、测试并部署 FastAPI 服务
- 理解 asyncio 并发模型、性能剖析与安全实践等生产级主题

### 💡 学习建议（针对有编程经验的学习者）

- **对比学习**：将 Python 概念与已知语言对照（如 Go struct vs dataclass、npm vs uv、goroutine vs asyncio），复用已有编程思维
- **零散时间**：每天精读一篇 reference 字典条目或一个速查表；周末推进一个项目
- **字典无等级，学习有路径**：概念解释统一住在 `reference/`，按难度走下面的三条路径

## 🧭 四象限导览

| 象限 | 目录 | 定位 | 文档 |
|------|------|------|------|
| 教程 | [basics/](basics/) | 按序学习入门（8 篇） | 环境搭建 → 第一个脚本 → 变量与类型 → 函数与 OOP → 控制流 → 异常 → 高级特性 → 第一个项目 |
| 字典 | [reference/](reference/) | 全量参考，任意跳入（28 篇） | 关键字 / 内置函数 / 数据结构 / OOP 协议 / 类型注解 / 装饰器 / 生成器与迭代器 / 上下文管理器 / asyncio / 异常体系 / 模块与导入 / 字符串格式化 / dataclass / 推导式 · FastAPI / Django&Flask / uv · 标准库 / 生态库 / pytest · 语法速查 / 故障排除 |
| 操作指南 | [frameworks/](frameworks/) | 框架与工具链 | [FastAPI 入门 ⭐](frameworks/01-fastapi-basics.md) · [FastAPI 进阶 ⭐⭐](frameworks/02-fastapi-advanced.md) · [生态集成 ⭐⭐](frameworks/03-ecosystem-integration.md) · [开发工具链 ⭐](frameworks/04-devtools.md) |
| 操作指南 | [projects/](projects/) | 实战项目（⭐ 递进） | [TODO API ⭐](projects/01-todo-api.md) · [短链接服务 ⭐⭐](projects/02-url-shortener.md) · [数据管道 ⭐⭐](projects/03-data-pipeline.md) · [生产级应用 ⭐⭐⭐](projects/04-production-fastapi-app.md) |
| 操作指南 | [testing/](testing/) | 测试工程 | [单元测试](testing/01-unit-testing.md) · [集成测试](testing/02-integration-testing.md) · [Mock 测试](testing/03-mocking-testing.md) |
| 操作指南 | [deployment/](deployment/) | 部署运维 | [容器化 ⭐⭐](deployment/01-docker-deployment.md) · [CI/CD ⭐⭐](deployment/02-ci-cd-pipelines.md) · [可观测性 ⭐⭐⭐](deployment/03-observability.md) |
| 解释 | [advanced-topics/](advanced-topics/) | 架构 / 性能 / 安全 | [项目架构 ⭐⭐⭐](advanced-topics/architecture/01-project-architecture.md) · [asyncio ⭐⭐⭐](advanced-topics/performance/01-async-python.md) · [性能剖析 ⭐⭐⭐](advanced-topics/performance/02-profiling-optimization.md) · [安全实践 ⭐⭐⭐](advanced-topics/security/01-security-practices.md) |

## 🛤️ 学习路径

### 入门路径（⭐）

[环境搭建](basics/01-environment-setup.md) → [第一个脚本](basics/02-first-script.md) → [变量与类型](basics/03-variables-types.md) → [函数与 OOP](basics/04-functions-oop.md) → [控制流](basics/05-control-flow.md) → [异常处理](basics/06-exceptions.md) → [开发工具链](frameworks/04-devtools.md) → [FastAPI 入门](frameworks/01-fastapi-basics.md) → [项目：TODO API](projects/01-todo-api.md) → [实战收束：第一个完整项目](basics/08-first-project.md)

### 进阶路径（⭐⭐）

[高级特性](basics/07-advanced-features.md) → [实战收束：第一个完整项目](basics/08-first-project.md) → [FastAPI 进阶](frameworks/02-fastapi-advanced.md) → [生态集成](frameworks/03-ecosystem-integration.md) → [单元测试](testing/01-unit-testing.md) → [Mock 测试](testing/03-mocking-testing.md) → [集成测试](testing/02-integration-testing.md) → [项目：短链接服务](projects/02-url-shortener.md) → [项目：数据管道](projects/03-data-pipeline.md) → [容器化部署](deployment/01-docker-deployment.md) → [CI/CD 流水线](deployment/02-ci-cd-pipelines.md)

### 精通路径（⭐⭐⭐）

[实战收束：第一个完整项目](basics/08-first-project.md) → [项目分层与领域建模](advanced-topics/architecture/01-project-architecture.md) → [asyncio 异步并发模型](advanced-topics/performance/01-async-python.md) → [性能剖析与优化](advanced-topics/performance/02-profiling-optimization.md) → [安全实践](advanced-topics/security/01-security-practices.md) → [可观测性](deployment/03-observability.md) → [项目：生产级 FastAPI 应用](projects/04-production-fastapi-app.md)

> 📖 字典随时可查：[语言概念](reference/language-concepts/) · [框架要点](reference/framework-essentials/) · [库指南](reference/library-guides/) · [速查表](reference/quick-references/)

## 📁 实际文件树

```text
10-python-discovery/
├── README.md                        # 本文档：四象限导览 + 三路径视图
├── basics/                          # 教程（8 篇）
│   ├── 01-environment-setup.md      # ⭐ uv 与现代工具链
│   ├── 02-first-script.md           # ⭐ 第一个脚本
│   ├── 03-variables-types.md        # ⭐ 变量与类型
│   ├── 04-functions-oop.md          # ⭐ 函数与面向对象
│   ├── 05-control-flow.md           # ⭐ 控制流程
│   ├── 06-exceptions.md             # ⭐ 异常处理
│   ├── 07-advanced-features.md      # ⭐⭐ 高级特性（含异步基础）
│   └── 08-first-project.md          # ⭐ 第一个项目
├── reference/                       # 字典（28 篇，无难度门槛）
│   ├── language-concepts/           # 01 关键字 · 02 内置函数 · 03 数据结构 · 04 OOP 协议 · 05 类型注解
│   │                                # 06 装饰器 · 07 生成器与迭代器 · 08 上下文管理器 · 09 asyncio · 10 异常体系
│   │                                # 11 模块与导入 · 12 字符串格式化 · 13 dataclass · 14 推导式
│   │                                # 15 闭包与作用域 · 16 类与继承 · 17 函数参数
│   ├── framework-essentials/        # 01 FastAPI · 02 Django/Flask · 03 uv 包管理器
│   ├── library-guides/              # 01 标准库 · 02 生态库 · 03 pytest · 04 os/sys · 05 enum · 06 functools/subprocess
│   └── quick-references/            # 01 语法速查 · 02 故障排除
├── frameworks/                      # 操作指南：框架生态
│   ├── 01-fastapi-basics.md         # ⭐ 路由、Pydantic 与自动文档
│   ├── 02-fastapi-advanced.md       # ⭐⭐ 依赖注入、后台任务、中间件
│   ├── 03-ecosystem-integration.md  # ⭐⭐ SQLAlchemy 2.0 + 数据库 + Redis
│   └── 04-devtools.md               # ⭐ uv、ruff、mypy、IPython
├── projects/                        # 操作指南：实战项目（⭐ 递进）
│   ├── 01-todo-api.md               # ⭐ TODO REST API
│   ├── 02-url-shortener.md          # ⭐⭐ 短链接服务（Redis + 统计）
│   ├── 03-data-pipeline.md          # ⭐⭐ 数据处理管道（解析 + 定时）
│   └── 04-production-fastapi-app.md # ⭐⭐⭐ 生产级 FastAPI 应用
├── testing/                         # 操作指南：测试工程
│   ├── 01-unit-testing.md           # ⭐⭐ pytest + fixture
│   ├── 02-integration-testing.md    # ⭐⭐ TestClient + 测试数据库
│   └── 03-mocking-testing.md        # ⭐⭐ monkeypatch / mocker
├── deployment/                      # 操作指南：部署运维
│   ├── 01-docker-deployment.md      # ⭐⭐ uv 镜像多阶段构建
│   ├── 02-ci-cd-pipelines.md        # ⭐⭐ GitHub Actions
│   └── 03-observability.md          # ⭐⭐⭐ structlog + Sentry/Prometheus
└── advanced-topics/                 # 解释：高级主题（均 ⭐⭐⭐）
    ├── architecture/01-project-architecture.md   # 分层与领域建模
    ├── performance/01-async-python.md            # asyncio 并发模型
    ├── performance/02-profiling-optimization.md  # 性能剖析与优化
    └── security/01-security-practices.md         # 依赖、注入与密钥
```

## 🔗 关联模块

- [01-go-backend](../01-go-backend/README.md) — 应用帝国矩阵·Go 后端：对比两语言的 Web 服务与并发模型（goroutine vs asyncio、net/http vs FastAPI）
- [09-nodejs-backend](../09-nodejs-backend/README.md) — 技术探索系列·Node.js 后端：对比 npm 生态与 uv、Hono 与 FastAPI 的异步模型

## 📖 学习资源

- 官方文档：[Python 3.14](https://docs.python.org/3/) · [FastAPI](https://fastapi.tiangolo.com/) · [uv](https://docs.astral.sh/uv/) · [pytest](https://docs.pytest.org/) · [ruff](https://docs.astral.sh/ruff/)
- 推荐书籍：《流畅的 Python》（深入语言机制）、《Python 编程：从入门到实践》（零散时间补基础）
- 社区：[Real Python](https://realpython.com/) · [Awesome Python](https://github.com/vinta/awesome-python)

---

**学习价值**: Python 具有简洁易学、生态丰富的特点，在 Web 开发、数据科学、自动化等领域应用广泛。以现代工具链为基线系统学习，将为你的技术栈增添重要一环。

*最后更新: 2026年9月*
