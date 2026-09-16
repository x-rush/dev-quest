# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式。

## [2.11.0] - 2026-09-16

### Added
- **知识库质量门禁 CI（`.github/workflows/verify.yml`）**：push/PR 自动跑全仓代码块 L1/L2 验证（`verify.py --strict`）+ 站内链接 0 断链（`link_check.py --strict`）。门禁语义 = **无新增未裁决失败**：FAIL 块内容哈希在 `adjudicated-fails.jsonl`（974 条 2.8.0 全仓 + 2.10.0/2.11.0 rust 全量裁决归档）中则放行，新增失败才拦截；kotlin/swift 无 runner 工具链自动 SKIP_NOTOOL 移交本地；verify.py 新增环境工具探测与 `--strict` 退出码
- **站内链接检查工具 link_check.py**（`shared-resources/tools/code-block-verify/`）：剥围栏代码块/行内代码后提取相对链接（逐行剥反引号防跨行错位拼接假链接）、模板占位符 allowlist、`--strict` 断链退出码 1；首跑全仓 6412 链接，修复 15 处历史断链后 0 断链
- **ts 项目脚手架入仓（`ts-projects/ts-02/03/04/09`）**：tsconfig + stubs 通配声明（无 node_modules 语法级验证），verify.py 在 /tmp 项目缺失时自动回退，CI 与新环境可复现；stubs-only 环境语义错误（TS2xxx）属预期噪声，门禁仅拦 TS1xxx 语法错误码
- **rust L2 第三方依赖工程（rustproj）**：workspace 脚手架入仓（`rustproj/Cargo.toml` pin 11-rust 基线：axum 0.8(+ws)/tokio 1.53/serde 1.0.229/sqlx 0.9/clap 4.6/jsonwebtoken 11 等），verify.py 按需自举到 /tmp，第三方块落 `v_b{id}` 子包 `cargo build` 编译级验证（tauri 系需系统 webkit2gtk 维持排除）
- **周报 workflow（`.github/workflows/baseline-weekly.yml`）**：周日错峰 cron，lychee 外链健康 + baseline-check registry 级版本漂移比对（CI 网络环境 + GITHUB_TOKEN 提额），均报告不门禁

### Verified
- **rust L2 第三方依赖全量复验（11-rust 188 rust 块，rustproj 实跑）**：L2 78 PASS / 13 FAIL，新增 2 处裁决入册——02753 多文件工程语义（文档明示 `src/main.rs`+`src/users.rs` 分块）、02842 拼接实证 FALSEPOSITIVE（02841 AppState 定义块 + 本块 rustfmt 解析通过；axum `ws` feature 缺失为管线 pin 问题已补）；其余 11 处沿 2.10.0 裁决（7 演示块错误码吻合 + 拆分/预期行为）；2 处 L1 拆分块 02843+02846 拼接 rustfmt 通过实证
- **全仓 strict 门禁本机彩排**：L1 PASS 2700 / FAIL 809（全部命中裁决哈希）/ SKIP_NOTOOL 937（kotlin/swift/无验证器语言），L2 PASS 236，**新增未裁决 0**，门禁退出码 0

### Fixed
- 02-nextjs 重构归档 2 文件 15 处历史断链修复（目录层级升一档 + go-backend→01-go-backend 模块改名残留）

## [2.10.0] - 2026-09-16

### Added
- **11-rust 正文全量建成（47 篇）**：basics 10 / reference 14（language-concepts 8 + framework-essentials 3 + library-guides 3）/ frameworks 7 / projects 5 / testing 3 / deployment 4 / advanced-topics 4，与 README 四象限规划一一对应。版本纪律全程执行：正文只引用模块基线表（Rust 1.98.1 / Tauri 2.11 / Axum 0.8 / Tokio 1.53 / SQLx 0.9 等），基线外库一律不落版本号；关键 API 经 docs.rs / 官方文档核证（Axum 0.8 `{param}` 语法、SQLx 0.9 SqlSafeStr 破坏性变化、Tauri capabilities/updater 配置字段等）
- **写作期本机实测**：10 路并行写作 agent 对自包含 rust 块 `rustc --edition 2024` 编译运行后才入文（含错误码演示块逐字复核 E0382/E0502/E0038/E0597/E0106 等）；Clap 用真装 4.6 端到端实测、serde/tokio/thiserror/anyhow crates.io 实拉断言级验证；实测纠错入文（edition 2024 `static_mut_refs` 硬错误、`#[should_panic]` 对 Result 风格函数必失败、`tests/common.rs` 会被当测试执行等）
- **code-block-verify 管线新增 rust 验证器**：L1 rustfmt 解析校验 + `fn main` 包装梯（纯语法层，编译失败演示块不误报）；L2 自包含块编译运行（use/attribute/extern crate 三路第三方探测）。管线用法与环境依赖同步更新 README

### Verified
- **11-rust 全量代码块机器验证（无抽样，管线当次实跑）**：345 围栏块中 39 非代码（mermaid/text/markdown）+ 6 无标注块目检（均为目录树/错误信息摘录/权限映射表，标注正确）+ dockerfile 2 / sql 1 目检通过；其余 **297 块 100% 取得终态**——L1 295 PASS / 2 FAIL（同函数跨块拆分，拼接后 rustfmt 通过证实，FALSEPOSITIVE）；rust L2 74 PASS / 12 FAIL（7 处为文档明确标注的编译失败演示且错误码吻合，5 处 ENV/拆分裁决，**0 REAL**）；ts 族 17 / bash 49 / toml 26 / json 14 / yaml 4 全部 PASS
- **链接 0 断链**：模块内 402 条 + 全仓指向 11-rust 链接，新增篇目 10 处文件名/层级断链当日修复复检归零

### Changed
- 模块 README 四象限状态 ⬜→✅；document-index 11-rust 节改实链形态、根 README/CLAUDE.md 口径更新（11-rust 由"规划中"转建设层）；learning-progress 补第 11 模块完成度项

## [2.9.0] - 2026-09-16

### Added
- **第 11 模块立项：Rust 跨平台开发**（`11-rust-cross-platform/`）：以 Rust 全量参考为根基、Tauri 2 跨端应用为旗舰方向、Axum 后端为辅线；47 篇四象限规划（basics 10 / reference 14 / frameworks 7 / projects 5 / testing 3 / deployment 4 / advanced 4，全部未建设）。技术基线 9 行经 crates.io API 与 rust-lang 官方 stable channel 实核（Rust 1.98.1 / Tauri 2.11 / Tokio 1.53 / Axum 0.8 等，2026-09-16）
- **AI 协议层沉淀**（`shared-resources/ai-protocols/`）：AI/LLM 应用层框架竞争未收敛，只收协议与模式层、不收框架教程——01 MCP 协议精要（2026-07-28 规范实核：无状态自包含请求、MRTR、Roots 弃用、官方扩展体系）+ 02 Agent 模式语言（7 核心模式 + 跨框架不变量）+ 03 Agent Skills 规范精要（agentskills.io 开放标准实核：SKILL.md 格式、渐进式披露、与 MCP 互补；2025-12-18 开放标准 + 40+ 工具采用实证收录，Claude Code 插件/marketplace 等单一产品机制不收录）
- **baseline-check 基线版本漂移检查工具**（`shared-resources/tools/baseline-check/`）：解析各模块 README「技术基线」区块批量比对 registry 最新版（go proxy / GitHub API / npm / PyPI / crates.io / Google Maven），输出 OK/DRIFT/UNKNOWN/NOTE 报告；2026-09-16 首跑 10 模块 46 行，漂移 5 处并**当日完成处置**（见 Changed）
- **技术收录 Checklist**（`shared-resources/standards/tech-adoption-checklist.md`）：收录判据清单（半衰期 / registry 与 GitHub 实核 / 模块关系 / 协议优先于框架 / 维护成本）+ 拒绝项记录表（Actix / Rocket / Yew-Leptos / AI SDK 教程）

### Changed
- **基线漂移 5 处全部处置**（registry/官方源当日实核）：02-nextjs TypeScript 5.x→**7.0**（npm + GitHub Releases 实核：Go 原生编译器 GA，2026-08-20；散文引用 41 处同步 7，"新特性"节标题改版本中立——const 断言/satisfies 等实为 4.9+ 特性不可绑 7）；01-go 1.25→**1.27.1**（go.dev/dl 实核，1.25/1.26 已出支持窗口；"1.25 引入"类事实陈述与实测记录保留）；05-kotlin Compose BOM→**2026.09.00**（Google Maven 实核）；06-swift→**6.4.0**（swift.org API 实核 2026-09-14，Linux 工具链可用，正文注明"基于 6.3 编写仍成立"）；04-rn React 判定**依赖锁版本**不升级（随 Expo SDK 57 锁 19.2.3，加注解待 SDK 58 一并刷新）
- **模式不变量层工程化**：`documentation-guidelines.md` 新增「模式不变量小结」规范条款（框架/版本绑定类文档文末必附 3-5 条框架无关架构原则，版本升级只核 API 层）；02-nextjs `reference/framework-patterns/` 全部 14 篇首批落地
- **维护强度分层**：`module-development-standards.md` 新增冻结策略——01-06 + 11 为建设层全速建设，07-10 探索系列维护冻结（只修确认级错误，不主动扩展）
- 根 README / CLAUDE.md / document-index / learning-progress 同步 11 模块口径与 AI 协议层、baseline-check 登记

## [2.8.0] - 2026-09-15

### Added
- **全仓代码块全量机器验证（无抽样）**：4263 个围栏块中 125 个非代码块（text/mermaid/markdown/txt）跳过，其余 **4138 个代码块 100% 取得终态**——L1 语法层（可验证语言全覆盖）→ L2 运行层（自包含块，go/python/php 过安全三道闸实际执行）→ L3 agent 裁决（全部机器失败块 17+1 路并行逐块裁决）。终态矩阵：PASS_L1L2 245 / PASS_L1 2409 / GATED_L2 291 / L2_TIMEOUT 2 / TEACHING 705 / ENV 279 / FALSEPOSITIVE 129 / REAL_FIXED 78。验证管线沉淀入仓 `shared-resources/tools/code-block-verify/`（提取器+主驱动+Go 语法 runner，ts/go 第三方依赖按各模块技术基线 pin 拉取全量验证）；报告与 manifest/results 归档 `refactor-archives/completed/code-block-verification/`
- 至此"实测覆盖"从抽样背书升级为 **100% 机器验证 + 逐块 agent 裁决**，方法学限制（TSX-as-TS 伪影/kotlin 包装梯盲区/jshell 无桩等）在报告中如实声明

### Fixed
- **78 处 REAL 真实错误全修复**（全部本机工具链实证：tsc 零错/go run+vet/kotlinc+coroutines 1.11.0/jshell/php 实跑/prisma validate/node --check）：02-nextjs 44（MSW v1 API 过时、App Router 缺 'use client'、Docker --omit=dev 缺 devDeps、虚构 API 等）/ 01-go 10（bufio Split advance=0 死循环、gin 路由写法等）/ 03-tanstack 7（enableColumnFilter 命名等）/ 04-rn 4 / 05-kotlin 3 / 07-php 3 / 10-python 3 / shared-resources 3 / 08-java 1；另含裁决遗漏追加修复 13 处（02373 bing 验证键、03532 @OptIn 等）
- 06-swift / 09-node 零 REAL；05-kotlin 延续零确认级问题标杆

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
