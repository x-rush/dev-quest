# Go：理解地图与学习规划

> 前置：函数参数与返回值；能在终端运行程序。学习 HTTP 前补齐请求方法、路径、状态码与 JSON。

## 先回答一个问题

**一次请求如何经过函数、结构体和错误返回，变成可预测的响应？**

Go 负责在服务端执行程序。先用普通函数处理数据，再把函数接到 HTTP 上；Gin 负责路由与中间件，GORM 负责对象与 SQL 的转换。它们不能替代 Go 的值、接口和错误语义。

## 概念怎样连接

值与零值 → 切片/映射/结构体 → 方法与接口 → 显式错误 → 标准库小项目 → goroutine 与同步 → HTTP → 数据库

| 概念 | 必要解释 |
|---|---|
| 值与引用效果 | 把结构体传给函数通常复制值；切片的值包含对底层数组的引用。不要从“都是赋值”推断它们修改后影响相同。 |
| 接口 | 接口描述方法能力。接受小接口可替换依赖；不是先为每个结构体建立同名接口。 |
| 并发 | goroutine 让任务可并发推进；完成通知、共享数据保护和取消需要另行设计。 |

## 从 0 到 1 的阅读顺序

以下按能力依赖排序，文件编号保留原有位置。先完成显式错误处理和标准库小项目，再进入并发；网络与数据库知识在实际接入时补齐。版本以[模块 README](README.md)的基线和练习工程配置为准。

官方补课入口：[Go 教程与语言参考](https://go.dev/doc/)。首次学习先读 Getting Started 和 Create a module，遇到具体语法再查规范；教程目录不需要一次读完。

1. [Go 环境搭建和工具配置](basics/01-environment-setup.md)
2. [第一个Go程序 - 从零开始](basics/02-first-program.md)
3. [变量、常量和基础数据类型](basics/03-variables-constants.md)
4. [复合数据类型：数组、切片、映射与结构体](basics/04-composite-types.md)
5. [函数定义与方法调用](basics/05-functions-methods.md)
6. [条件语句与循环控制](basics/06-control-structures.md)
7. [Go 错误处理机制](basics/08-error-handling.md)
8. [标准库待办命令行项目](projects/00-stdlib-todo-cli.md)：把输入、验证、状态、输出和测试连成一个程序。
9. [并发编程基础：goroutine、channel 与 sync](basics/07-concurrency-basics.md)

## 三个阶段如何验收

| 阶段与入口 | 练习输入与动作 | 通过条件 |
| --- | --- | --- |
| 函数与错误：[错误处理](basics/08-error-handling.md) | 分别传入普通标题和全空白标题 | 正常输入返回业务值；空白输入返回可判断的错误，不创建记录 |
| 标准库项目：[待办 CLI](projects/00-stdlib-todo-cli.md) | 运行 `go run . demo`，再为 `Store.Delete(99)` 补失败测试 | demo 输出 `#2 写 Go 测试`；删除未知 ID 返回错误且列表不变。CLI 只有 `add` 与 `demo`，没有按 ID 查询命令；每次启动状态清空 |
| HTTP 与持久化：[HTTP 参考](reference/library-guides/03-net-http.md)、[REST 项目](projects/01-rest-api-server.md) | 先做内存 CRUD，再切换数据库 | 请求状态、JSON 及错误一致；接数据库后单独验证重启和写入失败，不提前加入缓存与微服务 |

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

进入首项目之前，完成[复合类型](basics/04-composite-types.md)、[函数与方法](basics/05-functions-methods.md)和[错误处理](basics/08-error-handling.md)。产物是独立目录内的 `go.mod`、`main.go`、`main_test.go` 与实际验收记录；先执行 `go test ./...` 和 `go run . demo`，再执行 `go run . add "   "`，应非零退出且不输出添加成功消息。未知 ID 的失败验收直接调用 `Store.Delete`，不要尝试正文未提供的 CLI 子命令。

编译失败回查[环境搭建](basics/01-environment-setup.md)，状态或错误不符回查[首项目](projects/00-stdlib-todo-cli.md)的 `Store` 与测试。通过后补[并发基础](basics/07-concurrency-basics.md)与 [net/http](reference/library-guides/03-net-http.md)，进入 [CLI → HTTP 桥接](projects/01-rest-api-server.md)：交付共享且受同步保护的 Store、创建/列表 handler 和 `httptest` 测试，验收创建后查回、非法输入不写入，再继续 Gin 与数据库阶段。

## 框架与高级主题怎么选

先 Gin，再根据持久化需求选 SQL 工具。Redis、消息队列和微服务放到有明确缓存、一致性或部署需求时；不要把基础 API 练习变成基础设施安装清单。

## 全量参考怎么查

关键词解决“语法是什么意思”，内置函数解决“直接能调用什么”，标准库解决“导入以后能做什么”。框架 API 另列，避免把库函数误当成语言本身。以下是现有文章的完整导航，不代表每个 API 都已充分讲解；具体覆盖缺口进入审查台账。

### framework-essentials

- [Gin框架知识点详解](reference/framework-essentials/01-gin-framework.md)
- [GORM ORM知识点详解](reference/framework-essentials/02-gorm-orm.md)
- [sqlc vs GORM vs ent：Go 数据访问层选型](reference/framework-essentials/03-sqlc-vs-gorm.md)
- [Gin vs chi vs echo：Go HTTP 路由器选型](reference/framework-essentials/04-router-selection.md)
- [MongoDB Go Driver（官方驱动）速查](reference/framework-essentials/05-mongo-driver.md)
- [go-redis（Redis Go 客户端）速查](reference/framework-essentials/06-go-redis.md)

### language-concepts

- [Go语言25个关键字详解](reference/language-concepts/01-go-keywords.md)
- [Go内置函数详解](reference/language-concepts/02-go-built-in-functions.md)
- [Go编程精华 - 企业级开发核心技巧](reference/language-concepts/03-go-programming-essentials.md)
- [Go 数据类型速查手册](reference/language-concepts/04-go-data-types.md)
- [Go 控制流程速查手册](reference/language-concepts/05-go-control-flow.md)
- [Go 面向对象概念速查手册](reference/language-concepts/06-go-oop-concepts.md)
- [Go 错误处理](reference/language-concepts/07-error-handling.md)
- [Go 并发基础（goroutine / channel / select / sync）](reference/language-concepts/08-concurrency-basics.md)
- [Go 泛型（Type Parameters）](reference/language-concepts/09-generics.md)
- [切片（Slice）语义](reference/language-concepts/10-slice-semantics.md)
- [map 语义](reference/language-concepts/11-map-semantics.md)
- [channel 语义](reference/language-concepts/12-channel-semantics.md)
- [接口（Interface）语义](reference/language-concepts/13-interface-semantics.md)
- [defer / panic / recover 语义](reference/language-concepts/14-defer-panic-recover.md)
- [nil 语义汇总](reference/language-concepts/15-nil-semantics.md)

### library-guides

- [Go标准库详解](reference/library-guides/01-go-standard-library.md)
- [Go流行常用库详解](reference/library-guides/02-third-party-libs.md)
- [net/http - HTTP 服务端与客户端](reference/library-guides/03-net-http.md)
- [encoding/json - JSON 序列化与反序列化](reference/library-guides/04-encoding-json.md)
- [context - 跨 API 的取消与超时控制](reference/library-guides/05-context.md)
- [sync - 同步原语工具箱](reference/library-guides/06-sync.md)
- [database/sql - SQL 数据库访问层](reference/library-guides/07-database-sql.md)
- [time - 时间、时长与定时器](reference/library-guides/08-time.md)
- [errors - 错误值工程](reference/library-guides/09-errors.md)
- [io / bufio - 流式读写接口层](reference/library-guides/10-io-bufio.md)
- [os - 进程环境与文件系统](reference/library-guides/11-os.md)
- [testing - 测试与基准框架](reference/library-guides/12-testing.md)
- [slices / maps - 泛型集合工具](reference/library-guides/13-slices-maps.md)
- [strconv - 字符串与基本类型互转](reference/library-guides/14-strconv.md)
- [log/slog - 结构化日志](reference/library-guides/15-log-slog.md)
- [flag - 命令行参数解析](reference/library-guides/16-flag.md)
- [Go 标准库全包地图](reference/library-guides/17-std-package-map.md)

### quick-references

- [Go 语法速查表](reference/quick-references/01-syntax-cheatsheet.md)
- [Go Web开发工具速查](reference/quick-references/02-web-tools.md)
- [Go 常见问题排查手册](reference/quick-references/03-troubleshooting.md)

## 卡住时

先判断是术语不懂、输入输出不清、代码上下文缺失，还是运行环境不同。返回[学习方法](../shared-resources/learning-guide.md)按证据排查；通用术语见[术语解释](../shared-resources/glossary.md)。
