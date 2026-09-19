# Node.js / Hono：理解地图与学习规划

> 前置：JavaScript 函数、对象、数组和 Promise；先明确 ESM 与 CommonJS 工程格式，知道 TypeScript 类型不负责运行时校验。

## 先回答一个问题

**等待网络时可以做别的事，但为什么一次长计算仍会拖慢所有请求？**

Node.js 让 JavaScript 运行在服务端。异步 I/O 与事件循环让等待可以重叠，CPU 密集计算仍占用执行线程。Hono 提供路由与中间件，不替代运行时、数据库或输入校验。

## 先建立学习合同：运行时、产物与失败案例

默认基线为 **Node.js 24 LTS + ESM**。纯 JavaScript 示例可保存为 `.mjs` 后由 Node 直接执行；TypeScript 应通过项目的 `tsconfig`、构建工具或目标 Node 的类型擦除能力运行，不能把一台机器上“刚好可跑 `.ts`”当作跨环境承诺。依赖项目使用锁文件和一个包管理器复现，不混用全局安装与多个 lockfile。

| 阶段 | 必须亲手产出 | 必须观察的失败案例 | 进入下一阶段的条件 |
|---|---|---|---|
| 0：运行时与模块 | 输出 `process.version`、一个 ESM `import` 的小程序、项目 lockfile | CommonJS 与 ESM 混用导致的模块解析错误；缺依赖时的明确安装路径 | 能解释 Node 版本、模块格式、依赖锁定分别决定什么 |
| 1：HTTP 契约 | 一个随机端口的原生 HTTP 处理器，含 200、404、405 响应 | 未知路径、错误方法、未结束响应 | 响应有状态码、内容类型和结束信号；不依赖“服务器已监听”判断正确 |
| 2：异步与资源 | 带超时/取消或可关闭资源的业务函数 | 404 HTTP 响应、Promise rejection、重复关停分别处理 | 能说明 `await` 的等待边界，并保留失败原因而不吞掉异常 |
| 3：持久化 API | Task 项目的 schema、迁移、测试和启动入口 | 空标题、未知 ID、迁移缺失、类型/导入失败 | 重启后数据符合设计；正常、无结果、失败都可重放 |
| 4：大资源与交付 | 流或 Worker 的受限案例、测试记录、镜像/CI 构建 | 流失败、超限输入、任务取消或依赖退出 | 以输入规模、内存和耗时比较方案，且资源最终关闭 |

每个阶段保留 Node 版本、包管理器与 lockfile 状态、输入/输出、一个失败案例的状态码或退出码。它们是升级运行时、Hono 或 Prisma 前的最小回归基线。

## 概念怎样连接

HTTP 最小服务 → ESM → Promise/await → 路由与校验 → 错误与取消 → 流 → 数据库/测试

| 概念 | 必要解释 |
|---|---|
| 异步 | await 暂停当前异步流程，不是阻塞整个线程；独立任务可并发，有依赖的步骤仍要按顺序。 |
| 错误 | fetch 收到 HTTP 404 不会仅因此拒绝 Promise；需要检查 ok 或状态码。 |
| 流与背压 | 分块处理可以降低峰值内存，但必须等消费者能接收再继续生产。 |

## 从 0 到 1 的阅读顺序

先确认 JavaScript 的函数、对象、数组和 Promise 可读懂；模块篇解释文件如何相互导入。最小 HTTP 服务用于观察一次请求，之后再学习路由、错误和完整项目。Stream 与 Worker 在文件较大或计算耗时的练习中按需加入。

运行时及框架版本见[模块 README](README.md)，安装按工程锁文件复现。官方入口：[Node.js Introduction](https://nodejs.org/en/learn/getting-started/introduction-to-nodejs)。浏览器与 Node.js 的宿主 API 要分别查证。

1. [Node.js 24 开发环境搭建](basics/01-environment-setup.md)
2. [第一个 HTTP 服务器](basics/02-first-server.md)
3. [模块系统与 ESM](basics/03-modules-esm.md)
4. [异步编程：事件循环、Promise 与取消](basics/04-async-promises.md)
5. [路由、中间件与请求校验](basics/05-http-routing.md)
6. [错误处理与进程稳定性](basics/06-error-handling.md)
7. [第一个完整项目：任务管理 REST API](basics/08-first-project.md)
8. 选学：[Stream 管道与多线程](basics/07-streams-workers.md)，在处理大文件或计算瓶颈时使用。

## 三个阶段如何验收

| 阶段与入口 | 练习输入与动作 | 通过条件 |
| --- | --- | --- |
| 最小请求：[HTTP 服务器](basics/02-first-server.md) | 请求已定义路径，再请求不存在路径 | 状态码、响应头与 JSON 一致；响应能结束，没有一直等待的连接 |
| 基础业务：[Task 首项目](basics/08-first-project.md)，通过后再做 [Todo 扩展](projects/01-todo-api.md) | 首先完成 Task 创建、读取、空标题和未知 ID 检查，并保留一条记录重启读取 | Task 首项目使用 SQLite，必须完成迁移、客户端生成、类型检查和 4 项测试；扩展保留 Task，新增 Todo 模型与路由，不能把两页当成可互换的起点 |
| 资源边界：[流与 Worker](basics/07-streams-workers.md)、[文件服务](projects/03-file-storage-service.md) | 测试超时、超限文件和中断上传 | 有错误结果和资源清理；记录输入规模、内存与耗时，比较方案使用相同条件。此阶段在基础 API 之后进行 |

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

进入 Task 首项目之前，完成 [ESM](basics/03-modules-esm.md)、[Promise](basics/04-async-promises.md)、[路由与校验](basics/05-http-routing.md)及[错误处理](basics/06-error-handling.md)。交付锁文件、Prisma schema 与迁移、生成客户端、应用/监听入口和测试。按[首项目](basics/08-first-project.md)先生成客户端，再在专用测试库应用迁移，执行 `pnpm exec tsc --noEmit` 与 `pnpm exec tsx --test test/tasks.test.ts`；4 项为需实际执行的预期，不能用文中的依赖安装失败记录代替通过证据。

测试后按正文移除测试用 `DATABASE_URL` 覆盖，恢复开发库，再启动服务。正常验收为创建后按返回 ID 查回，保留另一条记录重启仍可读；失败验收为空白标题返回 400、未知 ID 返回 404，非法请求不新增记录。类型/导入失败回查客户端生成与 ESM；缺表回查迁移及当前数据库路径；错误变 500 回查统一错误出口。通过后进入 [Todo API 扩展](projects/01-todo-api.md)，保留 `/api/tasks` 及原有 4 项测试，再新增 `/todos`、迁移与独立测试；此后才继续认证服务。

## 框架与高级主题怎么选

Hono 主线，Fastify/NestJS 用于比较不同的约束与组织方式。先理解 node: 内置模块和 Web 全局 API 的区别，再判断是否真的需要第三方库。

## 共用的 JavaScript 基础参考

[关键词与完整语法实验](../shared-resources/javascript-keywords.md)解释语言语法；[内置对象、方法与边界](../shared-resources/javascript-builtins.md)解释数组、字符串、对象、集合和 Promise。先区分语言、宿主 API 与框架函数，再查本模块特有内容。

## 全量参考怎么查

关键词解决“语法是什么意思”，内置函数解决“直接能调用什么”，标准库解决“导入以后能做什么”。框架 API 另列，避免把库函数误当成语言本身。以下是现有文章的完整导航，不代表每个 API 都已充分讲解；具体覆盖缺口进入审查台账。

### framework-essentials

- [Hono 4 核心速查](reference/framework-essentials/01-hono-essentials.md)
- [框架选型对比：Fastify、NestJS 与 Express](reference/framework-essentials/02-fastify-nestjs.md)

### language-concepts

- [现代 JavaScript 语法速查](reference/language-concepts/01-js-modern-syntax.md)
- [异步 API 全表](reference/language-concepts/02-async-api.md)
- [Node 核心模块 API 速查](reference/language-concepts/03-node-core-api.md)
- [Stream API 速查](reference/language-concepts/04-streams-api.md)
- [Node + TypeScript 常用模式](reference/language-concepts/05-typescript-patterns.md)
- [ESM 与模块解析速查](reference/language-concepts/06-esm-module-resolution.md)
- [JS 核心语义：原型链、this、闭包与生成器](reference/language-concepts/07-js-core-semantics.md)
- [类型转换、相等性与内置集合](reference/language-concepts/08-type-coercion-collections.md)
- [全局对象速查](reference/language-concepts/09-globals-reference.md)

### library-guides

- [内置模块导航表](reference/library-guides/01-core-modules.md)
- [后端生态库精选](reference/library-guides/02-ecosystem-libs.md)
- [node:crypto 加密速查](reference/library-guides/03-crypto.md)
- [node:child_process 子进程速查](reference/library-guides/04-child-process.md)
- [node:buffer 二进制速查](reference/library-guides/05-buffer.md)
- [node:util 工具集速查](reference/library-guides/06-util.md)
- [进程生命周期与信号速查](reference/library-guides/07-process-lifecycle.md)
- [node:test 测试运行器速查](reference/library-guides/08-test-runner.md)
- [node:zlib 压缩速查](reference/library-guides/09-zlib.md)

### quick-references

- [Node 一行式速查](reference/quick-references/01-node-cheatsheet.md)
- [常见故障排除](reference/quick-references/02-troubleshooting.md)

## 卡住时

先判断是术语不懂、输入输出不清、代码上下文缺失，还是运行环境不同。返回[学习方法](../shared-resources/learning-guide.md)按证据排查；通用术语见[术语解释](../shared-resources/glossary.md)。
