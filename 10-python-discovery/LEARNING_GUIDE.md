# Python / FastAPI：理解地图与学习规划

> 前置：函数、条件与循环；区分解释器、虚拟环境和包管理器。会阅读 traceback 中自己代码对应的文件与行号。

## 先回答一个问题

**代码很短时，怎样仍能说清类型、可变对象与错误的边界？**

Python 用对象和协议组织行为：名字绑定对象，迭代器负责逐项产生值，上下文管理器负责资源清理。FastAPI 在函数与类型注解上建立 HTTP 边界；普通函数的注解本身不做运行时检查。

## 先建立学习合同：版本、产物与失败案例

默认语言基线是 **Python 3.14**；练习工程以自己的 `pyproject.toml`、锁文件和指定解释器为准。先在一个项目内用 `uv` 建立虚拟环境，再安装第三方包；不要把全局解释器里“恰好能 import”当成项目可复现。FastAPI/Pydantic 的请求校验是框架边界能力，不能反过来推断普通函数注解也会校验输入。

| 阶段 | 只需完成的阅读 | 必须亲手产出 | 必须观察的失败案例 | 可以进入下一阶段的条件 |
|---|---|---|---|---|
| 0：解释器闭环 | [环境搭建](basics/01-environment-setup.md) → [第一个脚本](basics/02-first-script.md) | 一个能以 `uv run` 或已激活虚拟环境执行的 `main.py` | 在错误目录或错误环境执行，能从 `sys.executable`、模块缺失信息定位原因 | 能说明解释器、虚拟环境、项目依赖文件分别负责什么 |
| 1：函数与数据 | 变量/类型 → 函数与类 → 控制流 | 输入固定数据后返回稳定结果的纯函数 | 空白输入或错误类型；不能用“返回空字符串”吞掉本应报告的错误 | 能写出正常返回值、异常类型和调用方处理方式 |
| 2：文件与资源 | 异常 → [标准库](reference/library-guides/01-standard-library.md) | 使用 `with` 读取或写入临时数据文件的小工具 | 不存在或损坏的数据文件；失败时不能覆盖原文件 | 能解释为什么解析成功不等于业务数据有效，且资源会在异常时关闭 |
| 3：控制台项目 | [书签管理器](basics/08-first-project.md) | 书签数据文件、命令记录和至少一个测试 | 新进程重读新增数据；损坏文件或重复 URL 的处理 | 正常命令、无结果和失败命令都有可复现输入、输出和退出码 |
| 4：HTTP 边界 | FastAPI 入门 → [Todo API](projects/01-todo-api.md) | 使用项目锁定依赖启动的 API 与接口测试 | 错误类型、缺必填字段、未知 ID；区分 422 校验与业务 4xx | 能从 HTTP 响应追到普通函数，再说明在哪一层执行了校验 |
| 5：工程与交付 | pytest → 集成测试 → 容器化与可观测性 | 针对真实依赖边界的测试和一次镜像构建记录 | 依赖失败、数据库或外部服务异常；测试不能只断言 mock 被调用 | 先通过测试与构建，再讨论并发、性能与部署扩缩容 |

每次阶段验收保留四项：Python 解释器路径与版本、依赖锁定状态、实际输入及输出、一个失败案例的异常或退出码。它们是升级解释器或依赖前的对照证据。

## 概念怎样连接

脚本与模块 → 名字/对象 → 容器与函数 → 异常/with → 迭代器/装饰器 → 类型提示 → Web/数据处理

| 概念 | 必要解释 |
|---|---|
| 可变对象 | 赋值通常绑定同一个对象；列表修改与重新绑定变量不同，复制也分浅层与深层。 |
| 迭代器 | next 消耗一次结果，遍历完可能不能重来；惰性减少预先工作但把失败推迟到消费时。 |
| 类型注解 | 注解提供分析和框架读取的信息；Pydantic 才在指定边界执行校验，不能把两者混为一谈。 |

## 从 0 到 1 的阅读顺序

先在虚拟环境运行一个脚本，完成类型、控制流、函数和异常，再做命令行书签。首项目若使用装饰器，先读清该装饰器接收什么、注册什么；生成器和 asyncio 不必在此时全部学完。

解释器与库版本见[模块 README](README.md)，练习环境按项目依赖清单及锁文件建立。官方补课入口：[Python Tutorial](https://docs.python.org/3/tutorial/)，切换到与你的解释器一致的文档版本，先读控制流、数据结构和异常章节。

1. [Python 环境搭建 — uv 与现代工具链](basics/01-environment-setup.md)
2. [第一个 Python 脚本 — REPL 与 `__main__` 惯用法](basics/02-first-script.md)
3. [变量与类型 — 动态类型、基本类型与 f-string](basics/03-variables-types.md)
4. [函数与类 — 函数、dataclass 与魔术方法入门](basics/04-functions-oop.md)
5. [控制流与推导式 — 条件、循环、推导式与 match-case](basics/05-control-flow.md)
6. [异常处理 — 异常体系与上下文管理器](basics/06-exceptions.md)
7. [综合项目 — 命令行书签管理器（typer + rich）](basics/08-first-project.md)
8. 按需补课：[装饰器、生成器、类型进阶与 asyncio](basics/07-advanced-features.md)，首项目先补 CLI 注册使用的装饰器，其余特性按任务引入。

## 三个阶段如何验收

| 阶段与入口 | 练习输入与动作 | 通过条件 |
| --- | --- | --- |
| 纯函数：[函数与类](basics/04-functions-oop.md)、[异常](basics/06-exceptions.md) | 清理首尾空白，并输入全空白和不合法类型 | 返回值和异常符合自己写出的契约；能解释类型注解为何不会自动拒绝输入 |
| 本地工具：[书签管理器](basics/08-first-project.md) | 新增并重读书签，再提供损坏数据文件 | 正常内容可保存；错误有提示，不覆盖损坏文件。测试使用临时数据，附一个独立变体如重复 URL 处理 |
| Web 服务：[Todo API](projects/01-todo-api.md) | 分别提交合法数据、错误类型和不存在 ID | 请求校验与业务错误能区分；能从接口测试追到普通 Python 函数，再决定是否需要异步 I/O |

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

## 框架与高级主题怎么选

FastAPI 是 API 主线，Django/Flask 用来理解全栈约束和轻量组合。uv/ruff/pytest 是工程工具，学习协议、异常、迭代与资源管理更能跨版本迁移。

## 全量参考怎么查

关键词解决“语法是什么意思”，内置函数解决“直接能调用什么”，标准库解决“导入以后能做什么”。框架 API 另列，避免把库函数误当成语言本身。以下是现有文章的完整导航，不代表每个 API 都已充分讲解；具体覆盖缺口进入审查台账。

### framework-essentials

- [FastAPI 核心速查 — 路由 / 依赖 / Pydantic / 异步](reference/framework-essentials/01-fastapi-essentials.md)
- [Django 与 Flask 核心对比速查](reference/framework-essentials/02-django-flask.md)
- [uv 包管理器 — 项目、依赖与解释器一站式工具](reference/framework-essentials/03-uv-package-manager.md)

### language-concepts

- [Python 关键字与软关键字详解](reference/language-concepts/01-python-keywords.md)
- [内置函数全表（分类速查）](reference/language-concepts/02-built-in-functions.md)
- [数据结构速查 — list / dict / set / tuple](reference/language-concepts/03-data-structures.md)
- [魔术方法与协议 — 迭代器 / 上下文 / 描述符](reference/language-concepts/04-oop-protocols.md)
- [typing 注解全表 — 泛型 / Protocol / TypedDict / Pydantic 配合](reference/language-concepts/05-typing-annotations.md)
- [装饰器 — 函数包装与元编程入口](reference/language-concepts/06-decorators.md)
- [生成器与迭代器 — 迭代协议与惰性求值](reference/language-concepts/07-generators-iterators.md)
- [上下文管理器 — with 语句与资源生命周期](reference/language-concepts/08-context-managers.md)
- [asyncio 并发 — 事件循环、协程与任务](reference/language-concepts/09-asyncio-concurrency.md)
- [异常体系 — 层级、异常链与 except*](reference/language-concepts/10-exceptions-system.md)
- [模块与导入系统 — import、包结构与 `__main__`](reference/language-concepts/11-modules-imports.md)
- [字符串格式化 — f-string 全语法与 t-string](reference/language-concepts/12-string-formatting.md)
- [dataclass 数据类 — field / frozen / order / slots](reference/language-concepts/13-dataclasses.md)
- [推导式 — 列表 / 字典 / 集合 / 生成器表达式](reference/language-concepts/14-comprehensions.md)
- [闭包与作用域 — LEGB、global/nonlocal、late binding](reference/language-concepts/15-closures-and-scope.md)
- [类与继承 — MRO、super 与 __slots__](reference/language-concepts/16-classes-and-inheritance.md)
- [函数参数 — 位置/关键字、*args/**kwargs 与默认值时机](reference/language-concepts/17-functions-parameters.md)

### library-guides

- [标准库导航 — collections / itertools / pathlib / json / logging 等](reference/library-guides/01-standard-library.md)
- [生态库精选 — requests / httpx / pandas / pydantic / typer / rich](reference/library-guides/02-ecosystem-libs.md)
- [pytest 测试指南 — fixture、参数化与常用插件](reference/library-guides/03-pytest-testing.md)
- [os 与 sys — 系统接口与解释器接口](reference/library-guides/04-os-sys.md)
- [enum — 枚举类型](reference/library-guides/05-enum-module.md)
- [functools 与 subprocess — 函数工具与子进程](reference/library-guides/06-functools-subprocess.md)

### quick-references

- [Python 一行式速查](reference/quick-references/01-python-cheatsheet.md)
- [常见错误排查 — 可变默认参数 / GIL / 循环导入](reference/quick-references/02-troubleshooting.md)

## 卡住时

先判断是术语不懂、输入输出不清、代码上下文缺失，还是运行环境不同。返回[学习方法](../shared-resources/learning-guide.md)按证据排查；通用术语见[术语解释](../shared-resources/glossary.md)。
