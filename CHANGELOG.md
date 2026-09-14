# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式。

## [2.7.0] - 2026-09-14

### Fixed
- **全仓收尾审计**（对基线 d9def1d 之前写就、从未全量审过的 459 篇老文档做最后一轮全审：2 波 13 路并行 agent 逐篇通读 + 工具链实测/官方文档比对，产出约 197 项确认级问题；6 路修复 agent 修复约 194 项，1 项审计建议被官方文档否决保留原文、2 项经复核超范围/已正确）：老文档错误密度（约 197 项）显著高于 2.6.0 新增文档（38 项），印证"写于工具链时代之前、断言从未实测"的根因判断；至此全仓文档均经至少一轮全量审计
  - 01-go（64 项，go 1.25.14 全部编译验证）：gqlgen 定性纠为 schema-first（SDL 生成代码）并按 gqlparser/v2 ast 重写深度限制示例、dataloader `WithMaxBatch`→`WithBatchCapacity`、gin 可选参数/gorm `ChangedFields`/prometheus `Observe` 等虚构 API 修正、批量补缺失 import
  - 02-nextjs（59 项，37 文件）：next-auth v5 全面迁移（`NextAuthOptions`→`NextAuthConfig`、Prisma 适配器改 `@auth/prisma-adapter`、`handlers/auth/signIn/signOut` 解构导出、signIn 回调无 request 参数）；历史扩展清零：artifact@v3（10 处）、zod `.errors`（17 处）、web-vitals onFID→onINP
  - 03-tanstack + 09-node（18 项）：`setQueryData` updater 返回 undefined 实为 no-op 非清空（query-core 源码短路）、MutationCache 回调末位注入 `context.client`（`mutation` 实例无 `client` 属性）、node API 语义 3 处
  - 04-rn + 10-python（11+3 项）：react-native-mmkv v4 值导出为 `createMMKV()` 工厂且 `delete` 改名 `remove`（tsc TS2339 实证，审计"仍存在"结论被纠偏）、httpx 默认 5 秒超时、Pydantic 校验器深拷贝语义、match-case 死分支
  - 06-swift（6 项）：`MetricReport` 实为 iOS 27 引入非 26、`VersionedSchema.models` 与 `SchemaMigrationPlan.schemas` 辨析（均经 Apple 官方文档实证，2 项审计建议被否决保留原文）
  - 07-php + 08-java（26 项）：PHP `int|null` 反射归一化为 `ReflectionNamedType`（8.5.10 实测改写）、Mockito 默认返回空 Optional/集合（2.x 起）、ZGC JDK 15 转正、`case null` 与 default 可共存
  - **05-kotlin 零确认级问题**（10 模块中唯一）
- **README 索引滞后补齐**（5 模块）：2.6.0 扩展后 document-index 已同步而模块 README 目录树/篇数声明漏更——01 21→41、02 24→32（含统计表 Knowledge Points 23→32、总计 53→62）、03 补 11 篇（含 17-flexrender）、07 18→29、10 22→28
- 全仓 4392 条本地链接 0 断链

## [2.6.1] - 2026-09-14

### Fixed
- **终极审计修复**（2.6.0 新增 74 篇全量审 + 老文档高风险子集抽审，4 路并行审计约 690 条实测断言产出 38 个确认级问题，4 路修复全部实测验证）：10 模块 32 文件，按语言工具链实测（Swift 6.3.3 首次纳入、RN 经 tsc 类型层、kotlinc/php/jshell/tsc/go 回放）
  - 01-go：`sync.Once` panic 后不重试语义反转（源码 + 实测：done 照样置位），附 mutex 可重试模式；`flag.Value` 实测输出
  - 02-nextjs：`dynamicParams` 归组（旧缓存模型已被移除）、TS2664→TS2436 适用域、`JSON.parse(null)` 返回 null 不抛
  - 03-tanstack：`useQueries` 条目 `placeholderData`（含 `keepPreviousData`）换 key 收不到旧数据是空操作（QueriesObserver 按 queryHash 匹配，query-core 运行时实测），平滑过渡改 `queryClient.getQueryData` 缓存取值法；`persistQueryClient` `onError` 签名
  - 04-rn：`InteractionManager` 已从 0.87 核心移除——reference 迁移指引重写（requestIdleCallback / startTransition）+ advanced-topics 两篇同根因残留 4 处同步；FlashList v1 `estimatedItemSize` 写法按 v2 重写（该 prop 已不存在，JS-only 实现）
  - 05-kotlin：`detectTransformGestures` `onGesture` 返回 Unit；硬关键字补 `as?`（30→31）
  - 06-swift：正则替换与贪婪语义归属、`Optional` 调试输出、`mutating pop`、手势速度类型、`Map` 版本门槛等 10 项（Swift 6.3.3 Linux 工具链首次全量实测）
  - 07-php：弱比较矩阵 49 格全量重测后修正 `"0" == false` 两格
  - 08-java：正则 `lookingAt` 结论 / `quoteReplacement` 输出 / 裸 `$` 抛异常、时间格式 `S` 位数、`DecimalFormat` 边界、`getRecordComponents` Java 16+ 等（JDK 21 实测）
  - 09-node：`crypto.hash` 第三参实为 `outputEncoding` 字符串非 options 对象（实测纠偏）；`String(Symbol)` 2026 规范行为
  - 10-python：仅位置参数语法示例；`__slots__` 内存数据按 3.14.7 实测改写
- 全仓 4384 条本地链接 0 断链

## [2.6.0] - 2026-09-14

### Added
- **reference 三层标尺补齐工程**（三波 10 模块）：以"语言核心全量自写 → 高频标准库一包一篇导览 → 中低频包一句话包地图"为标尺，10 模块并行审计产出缺口清单后分三波补齐，共新增约 74 篇字典条目与多处既有条目扩写；每模块 reference 达 23-31 篇
  - 第一波（01-go / 07-php / 10-python）：01 补核心语义 6 篇 + 包导览 13 篇 + 85 包地图（go 1.25 实测切片扩容序列）；07 补语言核心 6 篇 + 高频域导览 4 篇 + 扩展地图（php 8.5.10 回放，弱比较矩阵实测修正）；10 补闭包/类继承/函数参数 3 篇 + os-sys/enum/functools-subprocess 导览 + 内置函数扩写 18 条
  - 第二波（02-nextjs / 03-tanstack / 09-node）：02 补 TS 收窄（实测 tsc 7.0.2 纠正主线过时断言）/声明与模块/JS 核心语义/Web 平台 API 4 篇 + Hooks 补遗 + Metadata/段配置/环境变量 + 生态地图；03 补 useQueries 等 10 篇 + Start 服务端函数首篇；09 补 JS 核心语义/类型强制转换 3 篇 + node: 标准库导览 7 篇
  - 第三波（04-rn / 05-kotlin / 06-swift / 08-java）：04 补新架构术语/列表性能模型/平台 API 地图 3 篇 + 核心API/组件Props/Hooks/动画库 4 处增补（Expo SDK 基线纠正 57）；05 补集合/序列/文本正则 3 篇 + 组合模型/手势/画布 3 篇 + 关键字总索引扩至 666 行（kotlinc 2.4.20 实测）；06 补构造/关键字/正则/URLSession/包地图 6 篇 + 手势篇；08 补字符串常量池/枚举/注解/接口语义 4 篇 + JDK 包导览 7 篇（JDK 21 实测修正 4 处）

### Fixed
- **抽查裁决修正**：06 模块 `replacing(_:with:)` 替换模板写法纠正——SE-0357 官方签名证实 `with:` 参数为闭包或同 Output 的 `RegexComponent`，原生 Regex API 不支持 `$1` 模板字符串（Swift 论坛正则团队确认），示例改闭包形式并新增陷阱条目
- **主线指令过时断言由 agent 实测纠正**："解构破坏判别联合收窄"实为 TS 4.4 前历史行为（tsc 7.0.2/5.9.3/4.4.4 对照实测）、Kotlin `pagerCount`→`pageCount`、Expo SDK 56→57
- document-index 与各模块 README 四象限导览的篇数同步（01 74 / 02 62 / 03 58 / 04 49 / 05 52 / 06 54 / 07 59 / 08 55 / 09 48 / 10 54）；全仓 4381 条本地链接 0 断链

## [2.5.0] - 2026-09-12

### Added
- **终极审计**（五轮）：6 路审计 agent 分模块执行五个方面——修复回归、单一事实来源一致性、未实测域（RN/Spring Boot/Swift）、结构一致性、渐进式学习路径；以"问题密度 ≤ 2/模块"为收敛判据，本轮实测确认级问题 65 个（10 模块全部超标），据此定位了历轮审计问题的三大来源：修复本身是新错源、概括性论断比代码示例更易错、最早编写的模块未经实测

### Fixed
- **修复的修复（本轮重点）**：05 模块 `recoverCatching` 内重抛 `CancellationException` 的上轮"修复"经 kotlinc 2.4.20 实测无效（transform 内 throw 被内部 runCatching 捕获，取消仍被吞）——重写为 `runCatching` + `exceptionOrNull()` 检查先放行取消的模式并附旧写法对照实证；03 模块上轮 v9 修复引入的"核心特性必须显式注册"方向性误判（官方源码证实核心特性总是自动合并）4 处纠正；02 模块 next.config 虚构键修复不彻底的残留 10 余处全量清理（`experimental.turbopack` 布尔形态、`experimental.appDir`、`serverComponentsExternalPackages`→顶层、`images.domains`→`remotePatterns` 共 11 文件）
- **01 模块 basics 编译级错误 8 处**（本机 go 1.25.14 逐条实测）：未导入包（runtime/math/cmplx/net/http）、iota 从块首计数、`strings.ReplaceAll` 参数不足、"缺少分号"与"switch 缺少 break"两节按 C 语义误教 Go、"4 4 4"输出值、`blog.golang.org` 404 链接、GrpcClientPool 代码块补齐依赖后离线编译通过；`errors.Wrapped()` 笔误改 `Unwrap()`；projects/02 `grpc.Dial` 残留改 `NewClient`
- **学习路径前跳**：01 模块 basics/02-04 在正式讲解前使用循环/结构体/函数等概念，补 10 处前向标注链接 + 常用格式化动词速览；04 模块 README 入门路径与 basics/08 前置声明矛盾的最小闭环修法；10 模块三档路径补入收官篇 basics/08
- **虚构细节**：06 模块"@Model 属性名 body 会冲突"虚构约束删除（真实陷阱为 description）、`inMemory:` 虚构参数标签 ×2 改 `isStoredInMemoryOnly:`、`Task.value` 虚构同步变体改 async throws 语义；07 模块 PHP 8.5 概括句 5 处按 php.net + 本机 8.5.10 实测纠正（static 闭包允许进常量仅 fn 禁入、属性钩子不递归、backed 有 get 无 set 仍可写、URI 构造即校验、管道优先级高于比较）+ webman 3 处（安装包名、视图插件、虚构 `breakReconnect` 配置删除）；09 模块 Prisma v7 落地细节（`prisma7.config.ts` 虚构文件名、generator output 与 import 路径不匹配、v6 产物术语、url deprecated 而非报 P1012）与测试库隔离自赋值 no-op 重构为 dotenv + setupFiles 闭环
- **版本断言与基线**：04 模块"新架构自 0.83 起唯一"系统性偏晚一版改 0.82（官方 0.82 已禁旧架构，7 文件）；08 模块基线快照漂移对齐 Boot 4.1 BOM（Hibernate 7.4 / Security 7.1 / Gradle 8.14+ / Jackson 3.1）；06 模块 Swift Build 集成定性改为 preview 非默认；10 模块软关键字 3→4（本机 3.14.7 实测补 `type`）；04 模块导航教学线随 Expo SDK 56 expo-router fork 调整（basics/05 加 bare 工程边界声明、basics/08 改 expo-router 主线）
- **结构一致性**：09 模块基线声明从内联单行对齐为标准"技术基线"表格；document-index 补 01/02 模块篇数声明；全仓 3797 条链接 0 断链

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
- 01 模块 gRPC 教程 protoc 命令实测修正：`paths=source_relative` 按 proto 目录镜像输出会落错位置，`module=` 需配 `--go_out=.`（实测两处坑）；示例工程全链路验证（protoc 36.1 生成 → go build/vet → 服务端+客户端冒烟，一元 RPC 与 NotFound 错误码往返成功）
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
