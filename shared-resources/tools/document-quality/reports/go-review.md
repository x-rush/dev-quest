# Go L1 失败复核（第一轮容器结果）

审查日期：2026-09-18。

## 范围与方法

本复核读取第一轮容器 `results.jsonl` 快照，以及仓库中的 `shared-resources/tools/code-block-verify/adjudicated-fails.jsonl`。没有重新运行全库扫描，也没有执行文档示例。

筛选条件为 `lang == "go"` 且 `l1.status == "FAIL"`。结果共 55 个失败块：

- 51 个的 `legacy_hash_exception` 为 `true`。该字段来自 manifest 用块内容哈希的短前缀匹配历史 adjudicated 名单；完整 `source_sha256` 只用于本报告逐项定位。
- 4 个的 `legacy_hash_exception` 为 `false`，均是本轮前已定位的首围栏伪签名块；本次任务已经把它们改为独立 `package main` 示例并逐块 `go build` 成功。

历史名单只保存短哈希，不能证明代码质量。本报告已逐项复核全部 51 个块：失败分别来自签名速查、框架接入上下文、HTTP/GraphQL 协议文本、多个独立 package 文件和故意错误对照。发现并修复了一个真实 import 问题；其余各项的片段性质和所需上下文列于后表。

## 已修复的四个非基线失败

第一轮快照记录的 SHA 和报错如下；这些 SHA 对应修复前内容，不能用于判断当前工作树。

| 文件 | 快照范围 | 修复前 SHA-256 | 当前复核 |
|---|---:|---|---|
| `01-go-backend/reference/language-concepts/12-channel-semantics.md` | 11–24 | `80ad93ede0290643ed00c84f5ed7971c0d148d3489769f3ca9da72aa131a961a` | 改为有缓冲关闭/range、无缓冲配对与单向 channel 的完整示例；`go build` 通过。 |
| `01-go-backend/reference/library-guides/09-errors.md` | 11–27 | `c262e4d6ad5df8b2048e1f6a755061880097a7d720925f229c1a45a04515bb0f` | 使用真实自定义 error，并保留 Is、As、Unwrap、Join；`go build` 通过。 |
| `01-go-backend/reference/library-guides/10-io-bufio.md` | 11–35 | `42f028c16a01f2e9da4dbd60d2cf109f3f0814a217526227ae1ca92285f87a14` | 使用内存 Reader/Writer、MultiReader、TeeReader、Scanner 和检查 Flush；`go build` 通过。 |
| `01-go-backend/reference/library-guides/13-slices-maps.md` | 11–42 | `a99d9b4d523b9acbeaeab42e6b7adf33d53834a836b524ca84969bbd2f71ab10` | 使用具体数据与比较函数，保留 EqualFunc、Compare 和 maps API；`go build` 通过。 |

构建工具为 `C:\Users\77958\Documents\ChatGPT\技术栈探索路径\verification-lab\go-toolchain\go\bin\go.exe`。仅执行了 `go build`，没有运行示例。

## 已知边界

- 此报告已经逐项分类 51 个历史基线，但不把 `legacy_hash_exception` 当作质量通过证明。
- 结果来自变更前的第一轮容器快照。四个已修复块必须由后续全库扫描刷新状态和 source hash。
- 外部依赖示例（Gin、GORM、gqlgen、数据库与服务端项目）未在这次有界审查中安装依赖或构建；本文只判断了其失败是否符合可见的片段上下文。

## 51 个历史基线的逐项分类

以下每行均为第一轮 `results.jsonl` 中 `legacy_hash_exception=true` 的一个失败块。SHA-256 为结果快照的块内容哈希；分类说明 L1 不能把该块作为孤立 Go 文件编译的原因。除下述微服务 import 修复外，逐项复核未发现可在不改变片段教学性质下确定修复的真实实现错误。

| 路径：起始行 | 快照 SHA-256 | 失败类别 | 所需上下文／复核结论 |
|---|---|---|---|
| `01-go-backend/projects/02-microservices-demo.md:415` | `92bca0555a7d85347422cb58d73b6a020bd9d4c82168d09b21c282eb90d7f967` | 多文件外部依赖示例 | 注释标出独立文件；需 Redis/Gin 等模块。1539 已修正实际 time import |
| `01-go-backend/projects/02-microservices-demo.md:1539` | `d1f0749b405f9603d6411164dd6b6181a5aa99e89ed4bcc6fe2c3dbc52a769ed` | 多文件外部依赖示例 | 注释标出独立文件；需 Redis/Gin 等模块。1539 已修正实际 time import |
| `01-go-backend/reference/language-concepts/01-go-keywords.md:161` | `030f98c4ba95aabd796ffe00705c317417003eb94dbd99c0b7350801dd6aafba` | 包名枚举 | 每个 package 属于独立文件，子包路径不是 package 标识符 |
| `01-go-backend/reference/language-concepts/01-go-keywords.md:1189` | `dc584a942c2e18451e5277ab95d5c10338e46b872f0a73a2f593ca7b0e95a1a6` | 局部教学片段 | 缺 package/import/main 或将示例调用置于顶层；需嵌入完整程序 |
| `01-go-backend/reference/language-concepts/02-go-built-in-functions.md:71` | `02b959648fcb54dc3cc1f5452a15c93964d445654b79dda46f43b0aef2c0ebdf` | 内建函数伪签名 | 签名占位符 T/Type，不是可编译声明 |
| `01-go-backend/reference/language-concepts/02-go-built-in-functions.md:99` | `45c98b25bbc38bf521802405b5fb4f73624da1f2775f05743935801f909fd4f8` | 内建函数伪签名 | 签名占位符 T/Type，不是可编译声明 |
| `01-go-backend/reference/language-concepts/02-go-built-in-functions.md:125` | `f432bdc7933532e3429b65069eaf837e4540a1a8e7ffe196496f8a3511e283b9` | 内建函数伪签名 | 签名占位符 T/Type，不是可编译声明 |
| `01-go-backend/reference/language-concepts/02-go-built-in-functions.md:158` | `e4803a25442e2806fc5f3464ef593601d180b16c4ef7be28c23d0fad910e752c` | 内建函数伪签名 | 签名占位符 T/Type，不是可编译声明 |
| `01-go-backend/reference/language-concepts/02-go-built-in-functions.md:183` | `923a1502646b5197a4d67f2824b2fdd80ef8d28444bb85c6011ca44fa4271fba` | 内建函数伪签名 | 签名占位符 T/Type，不是可编译声明 |
| `01-go-backend/reference/language-concepts/02-go-built-in-functions.md:243` | `b1373eefdf3770b71b44763d5e074064fd94736d2ff94c32ce21c0ef4f6652df` | 内建函数伪签名 | 签名占位符 T/Type，不是可编译声明 |
| `01-go-backend/reference/language-concepts/02-go-built-in-functions.md:274` | `8f74318354c4ba7f19920589aebec4e8885f4e7d9c403af6c9e3d12deeaf7ad8` | 内建函数伪签名 | 签名占位符 T/Type，不是可编译声明 |
| `01-go-backend/reference/language-concepts/02-go-built-in-functions.md:307` | `0ba8101a4c3618ede591adeb26a92dc972ad129915c340fa907cf6bc42a02851` | 内建函数伪签名 | 签名占位符 T/Type，不是可编译声明 |
| `01-go-backend/reference/language-concepts/02-go-built-in-functions.md:341` | `571bbebc7aaf23d4481331866eae79df02d874e7e6b47460dbe18db48846b082` | 内建函数伪签名 | 签名占位符 T/Type，不是可编译声明 |
| `01-go-backend/reference/language-concepts/02-go-built-in-functions.md:347` | `659c9934c40c35920ffe4b3cc82c0d853431fdd5480f56c14c06e60de37d2ab4` | 内建函数伪签名 | 签名占位符 T/Type，不是可编译声明 |
| `01-go-backend/reference/language-concepts/02-go-built-in-functions.md:385` | `5c3dd42fb03610e63001c73f5df478a872e3fc8aa2023a16b93cafc2dd551729` | 内建函数伪签名 | 签名占位符 T/Type，不是可编译声明 |
| `01-go-backend/reference/language-concepts/03-go-programming-essentials.md:292` | `0cd32d4a4b8276776caaafc3da6f33031e514aca578f9a03d301d3eb4991805b` | 局部教学片段 | 缺 package/import/main 或将示例调用置于顶层；需嵌入完整程序 |
| `01-go-backend/reference/language-concepts/03-go-programming-essentials.md:421` | `74e52f743c7853f24f06d0c3595fed3b9d48818450ad917b41da870233c6f2f7` | 局部教学片段 | 缺 package/import/main 或将示例调用置于顶层；需嵌入完整程序 |
| `01-go-backend/reference/language-concepts/03-go-programming-essentials.md:764` | `792aa927eede3dbc7cfd58cc7a7c9b3a6429d852fad8383b9aa07cdf2306b883` | 局部教学片段 | 缺 package/import/main 或将示例调用置于顶层；需嵌入完整程序 |
| `01-go-backend/reference/language-concepts/03-go-programming-essentials.md:2790` | `a1cf2a71b5115a8b1db4cd55049d28f48ea1029f37c24965ac6160cec1f521e8` | go.mod 清单 | 需由 Go module 工具解析，不是 .go 源码 |
| `01-go-backend/reference/language-concepts/03-go-programming-essentials.md:2867` | `b0f96e8d045836a7097153c0fbeffa129ba457e21ce7a2e25ce3515b998bc795` | go.mod 清单 | 需由 Go module 工具解析，不是 .go 源码 |
| `01-go-backend/reference/language-concepts/04-go-data-types.md:145` | `d3407311eb275345eca387f9147a2352cba984f78edb3575ec07999aff2b398a` | 局部教学片段 | 缺 package/import/main 或将示例调用置于顶层；需嵌入完整程序 |
| `01-go-backend/reference/language-concepts/07-error-handling.md:11` | `d3f8dedcd506c6c43628302b7ce4873ff898c117639c5612603336d2cfbc0e30` | 局部教学片段 | 缺 package/import/main 或将示例调用置于顶层；需嵌入完整程序 |
| `01-go-backend/reference/language-concepts/08-concurrency-basics.md:17` | `4c1feab003ab64ddb9d7a4462e8edcd38f4999d10a23b5d0e371788112d37872` | 局部教学片段 | 缺 package/import/main 或将示例调用置于顶层；需嵌入完整程序 |
| `01-go-backend/reference/language-concepts/09-generics.md:11` | `080019b82fe56ff1e35f793296ea7fdb894898b58472457e0b338b45b33cd6ca` | 局部教学片段 | 缺 package/import/main 或将示例调用置于顶层；需嵌入完整程序 |
| `01-go-backend/reference/language-concepts/13-interface-semantics.md:11` | `d7c1195749800d22d3526c846408bd54f2c66c307bb2abd7fb2f9d91b6387a68` | 局部教学片段 | 缺 package/import/main 或将示例调用置于顶层；需嵌入完整程序 |
| `01-go-backend/reference/quick-references/01-syntax-cheatsheet.md:135` | `ba19b822aae43126b784466027e8f876d3e259703ea0adee09e73aa3f186749b` | 速查伪签名/配置 | 展示签名或 go.mod，不是独立程序 |
| `01-go-backend/reference/quick-references/02-web-tools.md:66` | `e8b973fcec92541dfa9fdbbed5da79e279a9f689da86cb536d964bacd3871431` | 速查伪签名/配置 | 展示签名或 go.mod，不是独立程序 |
| `01-go-backend/reference/framework-essentials/01-gin-framework.md:147` | `224462e18570844717001bc49c95ca56ae8657544af2f6a94e31a19adf3f19e1` | Gin 上下文片段 | 需 gin/router/handler/imports 的完整应用 |
| `01-go-backend/reference/framework-essentials/01-gin-framework.md:271` | `ab9dcc385e93e7d2f90dc19aa3e18f561f59aa2b7bdb739bba8f7f1f949b0d2a` | Gin 上下文片段 | 需 gin/router/handler/imports 的完整应用 |
| `01-go-backend/reference/framework-essentials/01-gin-framework.md:375` | `229b23c7ab73ea72970d482576461d78fde4389f5cdcfc548afe150fe126666d` | Gin 上下文片段 | 需 gin/router/handler/imports 的完整应用 |
| `01-go-backend/reference/framework-essentials/01-gin-framework.md:429` | `c22d80ea419a12be128c654eb75d62620e1138e3a446251a040a2ac76de8e477` | Gin 上下文片段 | 需 gin/router/handler/imports 的完整应用 |
| `01-go-backend/reference/framework-essentials/01-gin-framework.md:614` | `7436f881b5d063decff12ff9b4e14fc0b5bbb87a6656200560a6dbb254ce4dcc` | Gin 上下文片段 | 需 gin/router/handler/imports 的完整应用 |
| `01-go-backend/reference/framework-essentials/02-gorm-orm.md:1578` | `0f5bf2e1778b02488f94f0a89918b3f7314e4c512cf37e4f8835a7660091a9ef` | GORM 上下文片段 | 需模型、db 与 GORM 模块 |
| `01-go-backend/reference/framework-essentials/03-sqlc-vs-gorm.md:112` | `c88c648d4da2ba3594049346fc5ecd114afd329c8a4693ddee31730715535e62` | 驱动 API 速查 | 顶层调用与 imports 是接入片段，需 client/context/外部模块 |
| `01-go-backend/reference/framework-essentials/05-mongo-driver.md:15` | `752ec93bc912e39e66aca6b7a1fd4a93b8e39d40b0ade5b7c80d83985f39c0a8` | 驱动 API 速查 | 顶层调用与 imports 是接入片段，需 client/context/外部模块 |
| `01-go-backend/reference/framework-essentials/06-go-redis.md:15` | `fad288cc61d4a4e4306e25803d79277a31156020fd53f80562a3ab947607d431` | 驱动 API 速查 | 顶层调用与 imports 是接入片段，需 client/context/外部模块 |
| `01-go-backend/reference/library-guides/03-net-http.md:87` | `a30646f2faf3c595cc616581309a7e33934c8065e95370e8ac6d3af79e7c3c93` | 中间件组装片段 | 声明与组装语句需放入完整服务及 imports |
| `01-go-backend/advanced-topics/api-advanced/01-restful-patterns.md:105` | `6871904dbe4687cd0aebf4954391173e689c4f68d40749547d0b22416d818029` | HTTP 协议文本 | HTTP 方法、状态码或 URI，需按协议阅读 |
| `01-go-backend/advanced-topics/api-advanced/01-restful-patterns.md:132` | `19ca58e998ec52e01d1a3d0ec002657eedc024d505de83c5fef675ae8ef5f0c1` | HTTP 协议文本 | HTTP 方法、状态码或 URI，需按协议阅读 |
| `01-go-backend/advanced-topics/api-advanced/01-restful-patterns.md:751` | `69480f6e5ba93e794f21c8263abfef1275fde1a76223480a39b798592fd4c09f` | HTTP 协议文本 | HTTP 方法、状态码或 URI，需按协议阅读 |
| `01-go-backend/advanced-topics/api-advanced/02-graphql-apis.md:415` | `85ea77792d511df28654879e304e7579cdb96796755834006cd355d0801bbbcb` | Go + GraphQL SDL 混合 | directive 行须交给 GraphQL schema，不是 Go |
| `01-go-backend/advanced-topics/api-advanced/02-graphql-apis.md:510` | `75c1f6a790b5726c6a2be5ba9f5048fcf2e7c706ea0201538278f4df9dad7e7c` | 多文件框架示例 | database/services 为独立包，需模块、GORM 与模型 |
| `01-go-backend/basics/02-first-program.md:454` | `f503d3b08dee3b25956d12404831834c93d46ed329f4d6a64d3db22f0aefb6c4` | 故意错误对照 | 同时展示错误与正确版本，不能合并编译 |
| `01-go-backend/basics/02-first-program.md:463` | `11ef346257af2daf2d4217b4bca3a4447daf8d6bc80fc718cfc822c000dcdef3` | 故意错误对照 | 同时展示错误与正确版本，不能合并编译 |
| `01-go-backend/basics/02-first-program.md:504` | `58d567c390cacb0023a1af702fef0a418a1a39d900170251bb71b07cafa87105` | 故意错误对照 | 同时展示错误与正确版本，不能合并编译 |
| `01-go-backend/basics/03-variables-constants.md:269` | `56d9bd353761c6c43ddbd6cec1ff93dc746809e7099b054e68d2e0d8af7e0d4c` | 局部教学片段 | 缺 package/import/main 或将示例调用置于顶层；需嵌入完整程序 |
| `01-go-backend/basics/05-functions-methods.md:746` | `5e3b312fa46ab7689112fbb104c0b9a5878febf03910502dbc5623dfb37f15c2` | 局部教学片段 | 缺 package/import/main 或将示例调用置于顶层；需嵌入完整程序 |
| `01-go-backend/testing/01-unit-testing.md:984` | `de12683dc2b7b573f8a1365885567c13e7020e9032e24c128389c82cb28c2830` | 测试命名签名 | 函数声明省略函数体，t.Run 需位于测试函数内 |
| `01-go-backend/frameworks/01-gin-framework-basics.md:94` | `5bafd610f80e0088eea9cbd85cf36ea681f5ddff7cfd68ae65081db49878352d` | Gin 上下文片段 | 需 gin/router/handler/imports 的完整应用 |
| `01-go-backend/frameworks/03-gorm-orm-complete.md:219` | `a967c311c0d214bec6b1ddb1ca95be60cb01dc26f95d3d863de244a97946a76e` | GORM 上下文片段 | 需模型、db 与 GORM 模块 |
| `01-go-backend/frameworks/06-grpc-service-development.md:295` | `0b094780f3ad0d3180c45bd58878e06caad360a70bd2015c156d7d75e406265f` | 中间件组装片段 | 声明与组装语句需放入完整服务及 imports |

## 输入边界与 HTTP 的补充复验

最终扫描的两个交互超时确认为 EOF 处理缺失：`basics/06-control-structures.md` 的输入验证与计算器现已处理关闭输入、非法菜单和非法数字，并复用输入缓冲区；输入长度按 Unicode 码点计数。隔离容器验证了空输入正常退出、正常输入、过长输入、加法与错误分支。

`reference/library-guides/03-net-http.md` 是持续运行的服务，不以自行退出为成功条件。新增隔离请求探测实际验证 `/health` 返回 200/ok、`/users/42` 返回预期 JSON、POST 请求返回 405。三个原始超时均已由具体复验结果替代。记录见最终证据包的 `go-recheck`，不通过新增豁免消除超时。
