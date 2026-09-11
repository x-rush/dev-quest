# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式。

## [2.4.0] - 2026-09-11

### Added
- 全仓四维审计（虚构 API / projects 最佳实践 / 渐进式学习 / 字典覆盖）：5 组并行审计 agent 按技术栈分工，有工具链的语言实测运行（go build/vet/-race、php -r 逐字回放、tsc --noEmit、hono/prisma 实装验证），Kotlin/Swift 静态审读并标注"待核实"
- 5 路修复 agent 补齐缺口：01 模块新增 basics/04-composite-types、basics/07-concurrency-basics 两篇教程与 `reference/library-guides/03-net-http.md` 字典；02 模块补 RSC/metadata/React 19 Hooks 字典（`reference/language-concepts/06-react-19-hooks.md`）；05 模块补 `07-compose-testing.md`、`03-ksp-configuration.md`；06 模块补 `06-swift-charts.md`、`07-swiftdata-migration.md`；09 模块补 `06-esm-module-resolution.md`；10 模块补 `13-dataclasses.md`、`14-comprehensions.md`
- 01 模块 basics 教程重排为 8 篇（新增复合类型与并发基础，编号 git mv 保留历史）

### Fixed
- **并发安全类**：05/06 模块 `runCatching`/`onFailure`/`recoverCatching` 吞掉 `CancellationException` 共 3 处（取消异常必须放行，否则协程无法取消）；06 模块 `Task{}` 误述为"结构化并发"改为非结构化（结构化应使用 `async let` / `TaskGroup`）
- **类型系统类**：03 模块 TanStack Query v5 判别联合误用——解构 `isPending` 会丢失联合类型导致 `data` 无法收窄，共 4 处改为判 `data === undefined` 或保留对象访问；TanStack Table v9 API 名修正（`createPaginatedRowModel`、`createColumnHelper<TFeatures, TData>` 双泛型、`getPrePaginatedRowModel`）共 4 处
- **版本基线类**：04 模块 TypeScript 7.0 GA 基线（npm latest 7.0.2）；Next.js 16 `revalidateTag(tag, profile)` 双参必填共 17 处代码位补齐，Server Action 内改用 `updateTag(tag)`；`unstable_cache` 定性改为"不推荐新项目使用"；09 模块 Prisma v6 语法残留全量迁移至 v7（prisma.config.ts、generator prisma-client + output、driver adapter）；Hono jwt 中间件补必填 `alg` 参数；PHP 8.5 实测修复 5 处（Fiber resume 返 NULL 用 `getReturn()` 取值、常量表达式允许一等公民 callable 引用但禁止闭包字面量等 10 项，php8.5.10 逐字回放）
- **内容回填类**：05 模块笔记应用编辑屏补 `LaunchedEffect(noteId)` 回填逻辑；06 模块 @Model/@ModelActor 关系澄清；05 模块 `mutableStateOf` 类型推断陷阱条件修正（仅无初值时报错）
- 根级索引与进度同步：document-index / learning-progress 各模块篇数与 01 basics 新编号对齐，修复全部死链（全仓 3769 条链接 0 断链）
- 根级规范对齐：难度评级统一为 3 级（⭐/⭐⭐/⭐⭐⭐），54 篇文档 4-5 星折叠；100 文件日期元数据"2025年10月"→"2026年9月"

## [2.3.0] - 2026-09-11

### Added
- 全仓版本基线刷新至 2026-09 实况（exa 实时核实）：Next.js 16.3 + React 19.3、TanStack Query v5 / Table v9、Laravel 13 + PHP 8.5、Spring Boot 4.1（Framework 7 / Jackson 3）、Node.js 24 LTS + Hono 4、Python 3.14（t-string / free-threading 转正）、FastAPI 0.141、Kotlin 2.4.20、Swift 6.3（官方 Android SDK）、RN 0.87 + Expo SDK 57、Go 1.25 + Gin 1.12 + GORM 1.31
- 各模块 README 顶部新增"技术基线"区块（技术 / 版本 / 核实日期），作为该模块版本号的单一事实来源
- 基础知识字典补齐：各模块 `reference/` 达 18-20 篇（basics 教程核心概念全覆盖 + 高频标准库 API），共新增字典约 50 篇
- 09 模块新增框架选型对比：`02-fastify-nestjs.md`（性能定位 + 架构哲学，写透"何时选它"）
- 01 模块新增数据层与路由选型对比：`sqlc-vs-gorm.md`、`router-selection.md`（chi/echo）
- 07 模块新增"常驻内存与协程"专题（`advanced-topics/runtime/` 4 篇）：FPM vs 常驻内存模型、Workerman 原理、Webman 实战、Swoole 生态
- 抗过时三层原则固化为写作规范（`documentation-guidelines.md`）：稳定层禁写版本号、易变层指向模块基线区块；`CONTRIBUTING.md` 新增"技术基线年度复核"惯例

### Changed
- `09-nodejs-backend` 框架主角从 Express 5 迁移至 Hono 4（30 篇重写/修订，git mv 保留历史，测试模式换用 `app.request()`）
- 同步修订各版本 breaking changes：Next.js 16（Turbopack 默认、Async Request APIs 移除兼容层、middleware→proxy、'use cache'）、TanStack Query v5 数据获取语义校准（placeholderData、useSuspenseQuery）、Spring Boot 4（starter 改名、`spring.web.error.*`、Jackson 3）、PHP 8.5（pipe operator、URI 扩展）等
- 根级 README / document-index / learning-progress 技术栈行与篇数统计同步至刷新后实况

### Fixed
- **纠正 PHP 8.5 clone with 的虚构语法**（07 模块 4 文件）：本机 PHP 8.5.10 实测 + php.net 官方核实——`clone($obj, ['prop' => val])` 为 8.5 新增（RFC clone_with_v2，并非文档所称 8.3+），`clone($obj)->with()` 链式语法不存在（实测 parse error），readonly 覆盖须在作用域可见内（8.4 起 promoted readonly 默认 protected(set)），URI 扩展 WhatWg 类无 `getHost`/`getUserInfo`（实际为 `getAsciiHost`/`getUnicodeHost`/`getUsername`）
- **纠正虚构的 TanStack Query v6 版本声明**（03 模块 18 文件 + 02 模块基线区块 + CHANGELOG）：npm registry 证实 v6 不存在（latest 为 5.102.8），早期检索结果被污染；同步证伪并修复 "keepPreviousData 已移除"、"mutation 回调不再注入 client"、"最低 TypeScript 5.5" 等虚假 breaking changes 声明
- TanStack Table v9 示例修复（basics/04、frameworks/03、reference/09）：`createColumnHelper` 泛型、`tableFeatures({ coreFeatures })`、`columnHelper.columns()` 类型安全、特性作用域选项注册
- 代码抽查验证（本机工具链实际运行：go run / npm i hono / tsc --noEmit / @tanstack/react-query@5 类型检查）发现的其余示例错误
- 修复 07 模块 2 处无效语法示例（`(clone $x)->with(...)` → `clone($x, [...])`）
- 修复 02 模块 next.config 虚构配置键（`experimental.turbo` 等 4 类）、09 模块错误处理示例 2 处（interface instanceof、`c.json` 状态码类型收窄）

## [2.2.0] - 2026-09-10

### Added
- 标准体系升级为 Diátaxis 双轴框架：内容四象限（教程/操作指南/字典/解释）+ 三级难度标记（⭐/⭐⭐/⭐⭐⭐）
- `knowledge-points/` 全局更名为 `reference/`（模块知识字典，单一事实来源）
- 补齐 03-10 模块知识库内容约 300 篇：basics/ 教程 8 篇、reference/ 字典 11 篇、frameworks/projects/testing/deployment 工程域指南、advanced-topics 高级主题
- 03-10 模块 README 重写为四象限导览 + 入门/进阶/精通三路径视图

### Changed
- `document-index.md` 03-10 章节从"规划中"占位更新为实际文档目录索引（v3.0.0）
- `learning-progress.md` 为 02-10 模块补充模块入口链接并修正过时技术基线（Node 22/Express 5 等）
- 模块结构指南重写为 v2.0.0（双轴设计原则、README 三路径视图格式、结构适配原则）

### Fixed
- 全仓 Markdown 相对链接校验（3269 条真实链接，0 断链）：修复 document-index/cross-reference-system 的层级错误、02 模块指向旧仓库结构的 61 处死链、learning-progress 与各 README 的陈旧文件名引用

## [2.1.0] - 2026-09-10

### Added
- 新增 `03-tanstack-stack` 模块规划（TanStack Query/Table/Router/Form/Start）
- 新增根级工程文档：`CLAUDE.md`、`CONTRIBUTING.md`、`CHANGELOG.md`、`LICENSE`（MIT）

### Changed
- 模块布局重组为双轨制 10 模块：核心矩阵 01-06 + 技术探索系列 07-10
- `05-kotlin-compose`、`06-swift-swiftui` 聚焦 Kotlin Jetpack Compose 与 Swift SwiftUI 官方原生开发
- 根 README 目录结构树重写，与 01/02 模块实际结构对齐
- `document-index.md`、`learning-progress.md` 按实际文件全量重写
- `refactor-archives/README.md` 对齐实际归档结构，补充 02 模块归档条目

### Removed
- 移除 `03-taro-miniprogram` 模块（Taro 框架已不再活跃维护）
- 移除 `10-nuxtjs-exploration`、`11-sveltekit-journey` 模块（调整兴趣技术栈范围）
- 删除根级空目录 `development-tools/`、`framework-patterns/`、`performance-optimization/`

### Fixed
- 修复 `02-nextjs-frontend/{deployment,projects,testing}` 目录权限（700 → 755）
- 修复根 README 中指向不存在文件的 `shared-resources/` 链接
- 修复 `01-go-backend/README.md` 跨模块引用路径
- 清理全部文档中的 Taro 引用与旧模块编号残留

## [2.0.0] - 2025-10

### Added
- 建立 `shared-resources/` 标准体系：模块结构指南、开发标准、文档规范、交叉引用系统
- 建立重构归档系统（`refactor-archives/`）
- 完成 `02-nextjs-frontend` 模块现代化重构（App Router、React 19、Next.js 15）

### Changed
- 移除所有学习路线文档中的固定时间规划，改为灵活学习模式
- `01-go-backend` 模块内容对齐修复

## [1.0.0] - 2025-10-24

### Added
- 初始提交：dev-quest 学习路线图
- 完成 `01-go-backend` 模块重构（basics/frameworks/projects/testing/deployment 标准结构）
- 创建技术探索系列模块，建立双轨制学习体系

[2.4.0]: https://github.com/x_rush/dev-quest/compare/2.3.0...2.4.0
[2.3.0]: https://github.com/x_rush/dev-quest/compare/2.2.0...2.3.0
[2.2.0]: https://github.com/x_rush/dev-quest/compare/2.1.0...2.2.0
[2.1.0]: https://github.com/x_rush/dev-quest/compare/2.0.0...2.1.0
[2.0.0]: https://github.com/x_rush/dev-quest/compare/1.0.0...2.0.0
[1.0.0]: https://github.com/x_rush/dev-quest/releases/tag/1.0.0
