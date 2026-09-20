# 全库文档增强与验证记录

本库持续增强覆盖 **11 个技术模块**；当前结构统计为 673 篇 Markdown（不计本目录生成的 reports）。面向的读者是“会基本编程，但不熟悉对应技术栈”。历史重构档案作为过程记录保留。

逐文件台账记录了已处理的教学文章，但不能替代最终交付的逐项证据。关键词、内置能力、标准库、框架工程、项目练习和历史代码块分别有不同的完成条件；只有正文处理、技术纠错、结构检查与实际运行证据都齐备，才可声称某一范围已完成。

## 从哪里检查成果

| 入口 | 能看到什么 |
|---|---|
| [逐文件台账](reports/coverage.md) | 全部 640 篇的处理层级与结构复核线索 |
| [全库补充与纠错原始记录](reports/full-library-pass.json) | 313 个文件的主题解释、反馈练习、原文与改文；包含补充轮次和 Go 模块入口 |
| [跨模块段落改写](reports/editorial-review.md) | 较早一轮 199 篇、278 个段落的专项重写，与全库补充有交集，不能相加当独立篇数 |
| [最后一轮语义纠错](reports/final-semantic-cleanup.json) | 请求取消、纯 reducer、退出清理、缓存回源等追加修改 |
| [测试与交付练习](reports/acceptance-exercises.json) | 26 篇文章追加具体失败演练、观察结果与通过条件 |
| [阅读前置知识](reports/reading-prerequisites.json) | 40 篇文章追加与主题对应的学习准备 |
| [最终验证汇总](reports/validation.json) | 文件链接、章节锚点、围栏、空白检查，以及保留的限定范围运行记录 |
| [知识库交付基线](../../standards/knowledge-delivery-baseline.md) | “全量基础”、渐进路线、示例身份与交付完成判据 |
| [学习路径与参考库存](reports/learning-reference-inventory.md) | 11 个模块的目录、导读、参考入口与易变表述复核队列；仅作机械盘点 |
| [基础知识覆盖缺口盘点](reports/foundation-coverage-inventory.md) | 各模块关键词、内置能力、标准库与语言围栏的机械证据；不把围栏当作已运行验证 |
| [易变事实官方来源复核队列](reports/time-sensitive-review-queue.md) | 195 篇候选文档中版本、弃用、API 与维护状态表述的逐行定位；不是事实核验结论 |
| [Go 离线运行验证](reports/go-runtime-validation.md) | 18 个标准库完整程序/测试的实际运行范围、边界与复现命令 |
| [Go 关键词与内置函数验证](reports/go-foundations-validation.md) | 25 个关键字、44 个预声明标识符和 18 个内置函数相关的 18 个完整程序、2 个编译反例的当前验证证据 |
| [前端与 Node.js 围栏复验](reports/tsjs-validation-2026-09-19.md) | 当前 TypeScript/JavaScript 纯语法解析、7 项 Web 行为检查与 7 项 Node 示例运行的范围和边界 |
| [前端基础运行验证](reports/frontend-foundations-validation.md) | JavaScript 核心语义、Web API 与 TanStack 基础页中 8 个完整 Node 程序的实际结果和边界 |
| [移动端基础运行验证](reports/mobile-foundations.md) | Kotlin、React Native 与 Swift 文档中可脱离设备验证的纯逻辑范围，以及明确保留的设备/原生构建边界 |
| [安全正文运行验证](reports/security-examples.md) | Go、PHP、Node、Python 中输入、对象授权和存储边界的 18 项隔离运行检查；不代表框架集成已运行 |
| [前端项目与测试验证](reports/testing-projects-validation.md) | Next、TanStack、React Native 教学中的纯逻辑、React/jsdom 与 SSR 存储检查范围和边界 |
| [Kotlin 与 Swift 核心验证](reports/kotlin-swift-core-validation.md) | Kotlin/JVM 与 Swift 语法、输入规则的限定运行结果；不覆盖原生 UI 与设备构建 |
| [Node 与 Python 标准库验证](reports/node-python-libraries.md) | child_process、zlib、enum、functools/subprocess 中 9 个正文完整程序的隔离运行范围 |
| [PHP 与 Java 核心边界验证](reports/php-java-core-boundaries.md) | PHP 属性/Fiber、Java 集合/泛型和资源异常的 8 个正文完整程序验证 |
| [PHP 与 Java 类型验证](reports/php-java-types-validation.md) | PHP 声明类型、Java 基本类型与 record 的 5 个正文完整程序验证 |
| [Go 与 Rust 基础验证](reports/go-rust-basics.md) | Go 并发/错误处理和 Rust 生命周期的 13 个运行案例、3 个预期编译失败案例 |
| [Rust 生态验证](reports/rust-ecosystem-validation.md) | Tokio、Serde 与错误处理库的 10 个锁定依赖、无网络运行案例 |
| [Go 复合类型与 Rust 宏验证](reports/go-composite-rust-macros.md) | Go 切片、map、接口与 Rust 宏系统的 8 个运行案例、2 个预期编译失败案例 |
| [PHP 与 Java 数据管道验证](reports/php-java-pipelines-validation.md) | PHP 数组/生成器以及 Java Stream/Optional、IO 的 12 个正文完整程序验证 |
| [Node 与 Python P1 核心验证](reports/node-python-core-p1.md) | Node 异步/核心模块与 Python 内置函数/标准库的 4 个正文完整程序验证 |
| [前端与移动端 P1 核心验证](reports/p1-frontend-mobile-core-runtime.md) | TypeScript、TanStack Query key、Kotlin Sequence、Swift Optional/Collection 的 4 个限定运行案例 |
| [Node 与 Python P1 补充验证](reports/node-python-p1-next.md) | Node util 以及 Python MRO/slots 的 2 个正文完整程序验证 |
| [Next、TanStack 与移动端 P1 补充验证](reports/p1-next-web-mobile-runtime.md) | 输入守卫、Query Core、深链参数、Kotlin collection 和 Swift enum 的 5 个限定运行案例 |
| [Node 与 Python P1 最终补充验证](reports/node-python-p1-final.md) | Node 现代语法/全局对象与 Python 关键字/os/sys 的 4 个正文完整程序验证 |
| [Node 与 Python P1 第七批验证](reports/node-python-p1-seventh.md) | Node 绑定、集合和核心 API，以及 Python 控制流关键字的 4 个正文完整程序验证 |
| [P1 运行时补充验证](reports/p1-runtime-evidence.md) | Next JavaScript 绑定、React Native 输入边界及跨端标准库案例的 5 个限定运行结果 |
| [前端与移动端 P1 合约验证](reports/frontend-mobile-p1-runtime.md) | Next URL、TanStack Query、React JSX、Kotlin 集合与 Swift 控制流的 5 个限定运行案例 |
| [Go P1 页面验证](reports/go-rust-p1-page-validation.md) | Go 内置函数和标准库页面的 2 个正文完整程序验证；报告不主张 Rust 覆盖 |
| [PHP 与 Java P1 运行验证](reports/php-java-p1-runtime-report.md) | PHP/Java 关键词、内置 API 和标准库中的 6 个正文完整程序验证 |
| [Go 第七批正文验证](reports/go-rust-seventh-body-validation.md) | Go 关键词、内置函数、context 和数据类型的 4 个正文完整程序验证；报告不主张 Rust 覆盖 |
| [Go、PHP 与 Java 第九批运行验证](reports/go-php-java-ninth-runtime.md) | Go 切片、PHP 弱比较与 Java String 的 3 个正文完整程序验证 |
| [Go、Rust 与 Node 第十批运行验证](reports/go-rust-node-tenth-runtime.md) | Go nil、Rust 所有权和 Node crypto 的 3 个正文完整程序验证 |
| [Go、Rust 与 PHP 第十二批正文验证](reports/go-rust-php-twelfth-body-validation.md) | Go 方法集、Rust trait object 与 PHP 运算符的 3 个正文完整程序验证 |
| [Go、PHP、Java 与 Python 第十一批运行验证](reports/go-php-java-python-eleventh-runtime.md) | map、不可变日期、正则与 asyncio 的 4 个正文完整程序验证 |
| [PHP、Java 与 Python 第十批正文验证](reports/php-java-python-tenth-body-validation.md) | PHP 正则、Java 日期格式和 Python dataclass 的 3 个正文完整程序验证 |
| [Java、Node 与 Python 异常验证](reports/java-node-python-exceptions-report.md) | try-with-resources、Error.cause 和 Python 异常链的 3 个正文完整程序验证 |
| [Go、Node 与 Python 第十三批运行验证](reports/go-node-python-thirteenth-runtime.md) | Go 泛型、Node ESM 公开边界与 Python 可变默认参数的 3 个正文完整程序验证 |
| [PHP、Java 与 Rust 第十四批正文验证](reports/php-java-rust-fourteenth-body-validation.md) | PHP 文件锁、Java 严格日期格式化和 Rust trait/泛型的 3 个正文完整程序验证 |
| [Go、Node 与 Python 第十五批运行验证](reports/go-node-python-fifteenth-runtime.md) | Go 控制流、Node Buffer 边界和 Python 上下文清理的 3 个正文完整程序验证 |
| [PHP、Java 与 Rust 第十六批正文验证](reports/php-java-rust-sixteenth-body-validation.md) | PHP readonly、Java ConcurrentHashMap 与 Rust const generics 的 3 个正文完整程序验证 |
| [Go、Node 与 Python 第十七批运行验证](reports/go-node-python-seventeenth-runtime.md) | Go 控制流、Node Stream 解码和 Python CLI 入口的 3 个正文完整程序验证 |
| [PHP、Java 与 Rust 第十八批运行验证](reports/php-java-rust-eighteenth-runtime.md) | PHP 会话关闭、Java JPMS 映射和 Rust Arc/Weak 生命周期的 3 个正文完整程序验证 |
| [PHP、Java 与 Rust 第二十批运行验证](reports/php-java-rust-twentieth-runtime.md) | PHP 魔术方法、Java 注解反射和 Rust unsafe 边界的 3 个正文完整程序验证 |
| [PHP、Java 与 Rust 第二十二批运行验证](reports/php-java-rust-twentytwo-runtime.md) | PHP 重复 Attribute、Java 21 sealed/record pattern 与 Rust 枚举穷尽匹配的 3 个正文完整程序验证 |
| [Go 核心基础页第二十五批运行验证](reports/go-core-twentyfive-runtime.md) | 第一个程序、值/指针接收者和错误包装链的 3 个正文完整程序验证 |
| [Gin 入门最小工程验证](reports/gin-basics-validation.md) | Gin 1.12 的具名 router、JSON 绑定和错误状态测试；不覆盖部署或外部服务 |
| [GORM 入门最小工程验证](reports/gorm-basics-validation.md) | GORM 1.31/SQLite 的迁移、读写、零记录与事务回滚测试；不覆盖其他数据库方言 |
| [Java 环境最小程序验证](reports/java-environment-validation.md) | Java 21 的正文 `Hello.java` 编译与运行；不覆盖 IDE、SDKMAN 与构建工具 |
| [Node 环境 ESM 最小程序验证](reports/node-environment-validation.md) | Node 24 的正文 ESM 模块运行；不覆盖 pnpm、TypeScript 或项目服务 |
| [Kotlin 环境 JVM 最小程序验证](reports/kotlin-environment-validation.md) | Kotlin 正文的 JVM 编译与运行；不覆盖 Android SDK、Compose 或设备 |
| [Swift 环境最小程序验证](reports/swift-environment-validation.md) | Swift 正文的 Linux 工具链运行；不覆盖 Xcode、iOS SDK 或设备 |
| [Rust 环境 Cargo 最小程序验证](reports/rust-environment-validation.md) | Rust 2024 正文的离线 check/run/test；不覆盖依赖与交叉编译 |
| [PHP 环境运行时最小程序验证](reports/php-environment-validation.md) | PHP 正文的严格类型与 JSON 运行；不覆盖 Composer、FPM 或 Xdebug |
| [Next、TanStack 与移动端第十一批报告](reports/next-tanstack-mobile-eleventh-body-validation.json) | Next/TanStack 的 2 个纯逻辑运行结果，以及 RN/Kotlin/Swift 的明确未验证边界 |
| [PHP 与 Java 参考案例验证](reports/php-java-reference-cases-report.md) | PHP/Java 关键词、内置函数和标准库的 17 个正文完整程序验证 |
| [Rust、PHP 与 Java 第八批正文验证](reports/rust-php-java-eighth-body-validation.md) | 三个此前未验证核心页面的 Rust 所有权、PHP 控制流与 Java 函数式接口案例 |
| [Next、Node 与 Python 基础验证](reports/next-node-python-basics-report.md) | 三个此前未验证基础页面的 TypeScript 边界、Node ESM 和 Python 绑定示例；Next 仅验证类型擦除执行 |
| [Next 首项目验证](reports/next-first-project-2026-09-19.json) | `/drafts` 首项目的 React/JSDOM 八项交互验证；不覆盖 Next 构建或真实浏览器 |
| [Go 与 Rust P1 基础验证](reports/go-rust-p1-basics-runtime.md) | Go 常量及 Rust 集合迭代器的 3 个通过案例；另有 1 个 Go 案例因本机执行策略受阻，未计为通过 |
| [PHP 与 Java 控制流验证](reports/php-java-control-flow.md) | PHP match/enum 与 Java 21 模式 switch 的 2 个正文完整程序验证 |
| [PHP JSON 与 Java Math 验证](reports/php-java-json-math-validation.md) | PHP JSON 编解码边界及 Java BigDecimal/BigInteger 的 2 个正文完整程序验证 |
| [Go 与 Rust 关键字正文验证](reports/go-rust-keyword-body-validation.md) | Go package 与泛型方法边界、Rust 关键字和语法案例的 2 个正文完整程序验证 |
| [验证覆盖状态台账](reports/verification-coverage.md) | 逐文件区分限定运行证据、语法检查和未验证状态，避免把验证措辞或代码围栏当成通过证明 |
| [本轮交付状态](reports/delivery-status-2026-09-19.md) | 已修复项、已验证项与仍未达到全库交付条件的范围 |
| [外部服务教学契约验证](reports/external-service-contracts-validation.md) | 支付与对象存储以供应商无关 TypeScript 端口表达；只验证契约类型，不调用外部服务 |

根入口：[知识库 README](../../../README.md)。每个技术模块的 LEARNING_GUIDE 都提供渐进顺序、概念关系、练习与参考文章导航。

## 按知识库定位做了哪些修改

**基础参考**：区分语言关键词、内置函数、标准库和框架 API；补输入输出、类型与生命周期边界、反例和查阅关系。新增共用 JavaScript 关键词/内置能力，以及 Rust 关键词/标准类型/标准库三个基础入口。集合地图明确范围，不以出现名称冒充完整讲解。

**从 0 到 1**：11 个模块新增学习导读；90 篇基础课补概念提示、自测与反馈。Swift 与 Android 的独立学习路线改为按任务推进，先具备最小工具与语言能力，再做界面/接口、持久化、并发和交付。

**框架与高级主题**：49 篇框架文章补职责、数据流与验收，其余参考、进阶、测试和部署内容补主题机制与失败边界。移除多处“必须”“总是”“零开销”等无成立条件的结论；工具选型以问题和维护成本为依据。

**项目练习**：45 个项目补有限范围、分阶段产物和验收。练习要求观察结果，例如旧响应不得覆盖新查询、迁移后旧数据逐条保留、失败时仍可重试；不再把“实现缓存策略”“完善安全配置”单独当验收。

**测试与交付练习**：另为 26 篇测试、部署和监控文章补失败演练与通过条件，例如故意让测试失败以检查发布门禁、模拟更新失败以确认旧版本可用。这些是供读者执行的练习，不计入本轮实际运行通过的测试。40 篇文章补具体阅读准备，便于发现缺失的前置知识；这些篇数与上述处理记录存在交集。

**阅读体验**：615 篇原技术文章有导航，512 篇折叠长元数据。文件链接之外新增章节锚点检查，修复 406 处链接目标，并补齐 Go 速查表中目录承诺但正文缺失的 6 个小节。锚点按静态 GitHub 风格规则检查，不冒充所有渲染器的视觉测试。

## 代表性问题与具体改法

| 原问题 | 修改后的解释或行为 |
|---|---|
| Gin 中“分层架构：清晰的分层结构” | 以待办 API 解释入口、业务、存储责任；说明何时拆分、如何替换依赖与验证失败 |
| Query 先判无 data，首次失败仍显示加载 | 区分首次加载、首次失败、后台重取及保留旧数据，完整示例做 DOM 验证 |
| React 请求乱序与卸载后回写 | AbortController、请求序号、effect 清理，并用忽略 abort 的假服务验证旧结果仍被拒绝 |
| Node 先 process.exit 再“清资源” | 先停止入口、等请求、关闭依赖，再自然退出；超时为最后兜底 |
| Python、Go、PHP、Rust API 契约混淆 | 修正签名、值/引用、错误传播、锁作用域、序列化与集合形状等具体边界 |
| Android 把状态、协程或工作调度说成永久可靠 | 区分重组、视图身份、生命周期、进程恢复和系统调度条件 |
| SwiftUI 修饰符内外顺序写反 | 后写的包装前一步结果，配 frame/border 与 padding/background 对照实验 |
| SwiftData 宣称没有字段重命名映射 | 使用 @Attribute(originalName:)，给出版本化模型、迁移计划和旧库升级验收 |
| Keychain 更新先删旧凭证 | 先更新，不存在再添加；读取不存在与系统错误分别表达 |

## 当前实际验证范围

| 检查 | 结果 | 不代表什么 |
|---|---|---|
| 全仓相对文件链接 | 最终数量和 0 断链见 validation.json | 外网 URL 全部可访问 |
| 活跃/共享文档章节锚点 | 542 个引用，静态检查 0 缺失 | 已在所有 Markdown 渲染器点击验证 |
| Markdown 围栏、git diff --check | 通过 | 所有代码语法或语义通过 |
| 首轮语言示例 | 8 组通过，见 examples.json | 整篇参考中的全部片段已执行 |
| Python 扩展参考 | 18 组通过，其中 pytest/FastAPI 合计 8 个测试 | Python 新版本语法、所有数据库/部署已验证 |
| Node 扩展参考 | 7 组通过 | 完整框架、集群与部署通过 |
| Go 选定程序 | 13 组通过；2 组被 Windows 应用控制阻止 | 被阻止即通过，或已执行 race/真实数据库 |
| Query 入门组件 | 7 项 DOM 交互通过，保留原记录 | 完整 Next.js SSR 或浏览器布局通过 |
| 收尾 Web 示例 | 7 项通过，含 strict 类型检查与 3 项请求生命周期验证 | 所有历史大组件或所有浏览器行为通过 |

实际环境记录在对应 JSON 中：Python 3.12.14、Node 24.19.0、TypeScript 5.9.3、React 19.3.0、Query 5.103.1。TypeScript 5.9 的类型测试不能替代模块拟采用版本的完整工程构建。Swift、Kotlin/Android、Java、PHP、Rust 的完整平台工程未在本机执行；Go 的早期 Windows 阻断记录不再被当成通过，本轮可运行标准库示例改由离线 Go 1.27.1 容器实际验证，见 [Go 离线运行验证](reports/go-runtime-validation.md)。

## 维护者如何重跑

仓库根目录运行：

```bash
python shared-resources/tools/document-quality/finalize_validation.py
python shared-resources/tools/document-quality/refresh_coverage.py
```

前者重跑结构、文件链接、锚点和 diff 空白，并汇总已有运行记录；**不会重新执行那些运行示例**。后者保留人工审查状态，新出现的文档标为待审，不根据关键词自动发合格证。

选择性运行脚本：verify_learning_examples.py、verify_reference_examples.py、verify_node_reference_examples.py 和 verify_go_reference_examples.py。使用各脚本 --help 查看解释器及报告参数。收尾 Web 示例使用：

```bash
node shared-resources/tools/document-quality/verify_final_web_examples.mjs /path/to/dependency-workspace
```

该独立 workspace 需安装 React、React DOM、其类型声明、TypeScript、TanStack Query、jsdom 与 Testing Library，避免向文档仓库混入应用依赖。脚本直接提取限定文档片段，记录来源 SHA-256；不会执行全仓任意代码。

## 审查边界与后续维护

保留 [before.json](reports/before.json) 原始基线；[after.json](reports/after.json) 的线索用于人工复核，不是质量分数。剩余“短条目重复”分别是项目选型映射，“无门槛”出现在审核条件语境，不为清零指标刻意改写。

长期维护仍需按目标语言版本逐项核对有限名称集合、给完整工程配置对应工具链 CI、跟踪版本迁移与外链。旧文档中的历史“已核实/实测”不能自动当成本轮证据。具体完成范围与维护事项见 [交付与持续验证记录](../../../refactor-archives/pending/2026-09-18-document-quality-plan.md)。
