# 学习路径与参考覆盖清单（机械盘点）

生成日期：2026-09-19。范围：11 个现行模块；不含 refactor-archives 和验证报告。

本清单只记录可观察的结构证据。文档存在、标题存在或关键词命中，都**不等于**内容正确、示例可运行或讲解足够；它用于排定人工深审与真实项目验证的顺序。

## 模块总览

| 模块 | basics | reference | frameworks | projects | testing | deployment | advanced | 导读 | 三阶段路径证据 | 机械缺口 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| 01-go-backend | 8 | 41 | 6 | 5 | 5 | 4 | 6 | ✓ | ✓/✓/✓ | 0 |
| 02-nextjs-frontend | 8 | 32 | 4 | 4 | 4 | 4 | 6 | ✓ | ✓/✓/× | 0 |
| 03-tanstack-stack | 8 | 32 | 4 | 4 | 4 | 3 | 4 | ✓ | ✓/✓/✓ | 0 |
| 04-multiplatform-apps | 8 | 23 | 4 | 4 | 3 | 3 | 4 | ✓ | ✓/✓/✓ | 0 |
| 05-kotlin-compose | 8 | 27 | 4 | 4 | 3 | 3 | 4 | ✓ | ✓/✓/✓ | 0 |
| 06-swift-swiftui | 8 | 29 | 4 | 4 | 3 | 3 | 4 | ✓ | ✓/✓/✓ | 0 |
| 07-php-mastery | 8 | 29 | 4 | 4 | 3 | 3 | 8 | ✓ | ✓/✓/✓ | 0 |
| 08-java-revisited | 8 | 29 | 4 | 4 | 3 | 3 | 4 | ✓ | ✓/✓/✓ | 0 |
| 09-nodejs-backend | 8 | 22 | 4 | 4 | 3 | 3 | 4 | ✓ | ✓/✓/✓ | 0 |
| 10-python-discovery | 8 | 28 | 4 | 4 | 3 | 3 | 4 | ✓ | ✓/✓/✓ | 0 |
| 11-rust-cross-platform | 10 | 17 | 7 | 5 | 3 | 4 | 4 | ✓ | ✓/×/× | 0 |

`三阶段路径证据` 的顺序是入门/进阶/精通，接受旧模块的等价名称；数字是相应目录下的 Markdown 文档数。

## 参考覆盖信号

以下信号只用来发现可能漏项。JavaScript 生态模块在根 README 明确复用 shared-resources 的 JavaScript 关键词、内置能力与标准库参考，因此单列为共享入口。

### 01-go-backend

- 关键词：01-go-backend/reference/language-concepts/01-go-keywords.md；01-go-backend/reference/language-concepts/02-go-built-in-functions.md；01-go-backend/reference/language-concepts/04-go-data-types.md；01-go-backend/reference/language-concepts/07-error-handling.md；01-go-backend/reference/language-concepts/08-concurrency-basics.md；01-go-backend/reference/quick-references/01-syntax-cheatsheet.md
- 内置能力：01-go-backend/reference/framework-essentials/01-gin-framework.md；01-go-backend/reference/framework-essentials/03-sqlc-vs-gorm.md；01-go-backend/reference/framework-essentials/04-router-selection.md；01-go-backend/reference/framework-essentials/06-go-redis.md；01-go-backend/reference/language-concepts/01-go-keywords.md；01-go-backend/reference/language-concepts/02-go-built-in-functions.md；01-go-backend/reference/language-concepts/07-error-handling.md；01-go-backend/reference/language-concepts/08-concurrency-basics.md；01-go-backend/reference/language-concepts/10-slice-semantics.md；01-go-backend/reference/language-concepts/11-map-semantics.md；01-go-backend/reference/language-concepts/13-interface-semantics.md；01-go-backend/reference/language-concepts/14-defer-panic-recover.md；01-go-backend/reference/library-guides/03-net-http.md；01-go-backend/reference/library-guides/15-log-slog.md；01-go-backend/reference/library-guides/17-std-package-map.md
- 标准库：01-go-backend/reference/framework-essentials/01-gin-framework.md；01-go-backend/reference/framework-essentials/04-router-selection.md；01-go-backend/reference/language-concepts/01-go-keywords.md；01-go-backend/reference/language-concepts/02-go-built-in-functions.md；01-go-backend/reference/language-concepts/10-slice-semantics.md；01-go-backend/reference/language-concepts/11-map-semantics.md；01-go-backend/reference/language-concepts/13-interface-semantics.md；01-go-backend/reference/language-concepts/14-defer-panic-recover.md；01-go-backend/reference/library-guides/01-go-standard-library.md；01-go-backend/reference/library-guides/02-third-party-libs.md；01-go-backend/reference/library-guides/03-net-http.md；01-go-backend/reference/library-guides/04-encoding-json.md；01-go-backend/reference/library-guides/07-database-sql.md；01-go-backend/reference/library-guides/12-testing.md；01-go-backend/reference/library-guides/13-slices-maps.md；01-go-backend/reference/library-guides/15-log-slog.md；01-go-backend/reference/library-guides/16-flag.md；01-go-backend/reference/library-guides/17-std-package-map.md；01-go-backend/reference/quick-references/01-syntax-cheatsheet.md
- basics 练习/自测信号：6 篇；projects 验收信号：4 篇。
- 完全相同的一级标题组：0 组；含易变版本/API 用语的文档：19 篇（仅表示需要随技术基线复核，不表示已过期）。

### 02-nextjs-frontend

- 关键词：02-nextjs-frontend/reference/development-tools/03-package-managers.md；02-nextjs-frontend/reference/framework-patterns/01-app-router-patterns.md；02-nextjs-frontend/reference/framework-patterns/09-async-request-apis.md
- 内置能力：02-nextjs-frontend/reference/framework-patterns/06-form-validation-patterns.md；02-nextjs-frontend/reference/framework-patterns/14-env-vars.md；02-nextjs-frontend/reference/language-concepts/07-type-narrowing-guards.md；02-nextjs-frontend/reference/language-concepts/08-ts-declarations-modules.md；02-nextjs-frontend/reference/language-concepts/10-web-platform-apis.md；02-nextjs-frontend/reference/library-guides/03-ecosystem-map.md；02-nextjs-frontend/reference/performance-optimization/03-image-font-optimization.md
- 标准库：02-nextjs-frontend/reference/language-concepts/09-js-core-semantics.md；02-nextjs-frontend/reference/language-concepts/10-web-platform-apis.md
- 共享 JavaScript 基础参考（关键词、内置能力、标准库）：shared-resources/javascript-keywords.md；shared-resources/javascript-builtins.md；shared-resources/javascript-standard-library.md
- basics 练习/自测信号：8 篇；projects 验收信号：4 篇。
- 完全相同的一级标题组：0 组；含易变版本/API 用语的文档：37 篇（仅表示需要随技术基线复核，不表示已过期）。

### 03-tanstack-stack

- 关键词：03-tanstack-stack/reference/language-concepts/04-form-core-api.md；03-tanstack-stack/reference/library-guides/03-language-web-foundations.md
- 内置能力：03-tanstack-stack/reference/language-concepts/02-table-core-api.md；03-tanstack-stack/reference/language-concepts/07-infinite-query.md；03-tanstack-stack/reference/language-concepts/08-placeholder-data.md；03-tanstack-stack/reference/language-concepts/21-usefield-and-createformhook.md；03-tanstack-stack/reference/library-guides/02-related-libs.md；03-tanstack-stack/reference/library-guides/03-language-web-foundations.md；03-tanstack-stack/reference/quick-references/01-syntax-cheatsheet.md；03-tanstack-stack/reference/quick-references/02-troubleshooting.md
- 标准库：03-tanstack-stack/reference/library-guides/03-language-web-foundations.md
- 共享 JavaScript 基础参考（关键词、内置能力、标准库）：shared-resources/javascript-keywords.md；shared-resources/javascript-builtins.md；shared-resources/javascript-standard-library.md
- basics 练习/自测信号：8 篇；projects 验收信号：4 篇。
- 完全相同的一级标题组：0 组；含易变版本/API 用语的文档：40 篇（仅表示需要随技术基线复核，不表示已过期）。

### 04-multiplatform-apps

- 关键词：04-multiplatform-apps/reference/library-guides/03-storage-options.md
- 内置能力：04-multiplatform-apps/reference/framework-essentials/01-expo-essentials.md；04-multiplatform-apps/reference/framework-essentials/02-navigation-essentials.md；04-multiplatform-apps/reference/framework-essentials/04-dev-client-and-updates.md；04-multiplatform-apps/reference/language-concepts/01-rn-core-api.md；04-multiplatform-apps/reference/language-concepts/03-hooks-reference.md；04-multiplatform-apps/reference/language-concepts/13-platform-api-map.md；04-multiplatform-apps/reference/library-guides/01-state-and-data.md；04-multiplatform-apps/reference/library-guides/04-animation-gesture-libs.md
- 标准库：未找到机械信号
- 共享 JavaScript 基础参考（关键词、内置能力、标准库）：shared-resources/javascript-keywords.md；shared-resources/javascript-builtins.md；shared-resources/javascript-standard-library.md
- basics 练习/自测信号：8 篇；projects 验收信号：4 篇。
- 完全相同的一级标题组：0 组；含易变版本/API 用语的文档：23 篇（仅表示需要随技术基线复核，不表示已过期）。

### 05-kotlin-compose

- 关键词：05-kotlin-compose/reference/language-concepts/01-kotlin-keywords.md；05-kotlin-compose/reference/language-concepts/06-extension-functions.md；05-kotlin-compose/reference/language-concepts/07-scope-functions.md；05-kotlin-compose/reference/language-concepts/08-lambdas-higher-order.md；05-kotlin-compose/reference/language-concepts/12-kotlin-built-in-functions.md
- 内置能力：05-kotlin-compose/reference/language-concepts/09-collections-operations.md；05-kotlin-compose/reference/language-concepts/12-kotlin-built-in-functions.md
- 标准库：05-kotlin-compose/reference/language-concepts/07-scope-functions.md；05-kotlin-compose/reference/language-concepts/09-collections-operations.md；05-kotlin-compose/reference/language-concepts/10-sequences.md；05-kotlin-compose/reference/language-concepts/11-text-and-regex.md；05-kotlin-compose/reference/language-concepts/12-kotlin-built-in-functions.md
- basics 练习/自测信号：8 篇；projects 验收信号：4 篇。
- 完全相同的一级标题组：0 组；含易变版本/API 用语的文档：21 篇（仅表示需要随技术基线复核，不表示已过期）。

### 06-swift-swiftui

- 关键词：06-swift-swiftui/reference/language-concepts/01-swift-keywords.md；06-swift-swiftui/reference/language-concepts/13-keywords-completion.md；06-swift-swiftui/reference/language-concepts/17-swift-built-in-functions.md
- 内置能力：06-swift-swiftui/reference/language-concepts/03-concurrency-api.md；06-swift-swiftui/reference/language-concepts/17-swift-built-in-functions.md
- 标准库：06-swift-swiftui/reference/language-concepts/07-enums-pattern-matching.md；06-swift-swiftui/reference/language-concepts/10-value-types-arc.md；06-swift-swiftui/reference/language-concepts/16-stdlib-foundation-map.md；06-swift-swiftui/reference/language-concepts/17-swift-built-in-functions.md；06-swift-swiftui/reference/library-guides/01-foundation-and-stdlib.md
- basics 练习/自测信号：8 篇；projects 验收信号：4 篇。
- 完全相同的一级标题组：0 组；含易变版本/API 用语的文档：7 篇（仅表示需要随技术基线复核，不表示已过期）。

### 07-php-mastery

- 关键词：07-php-mastery/reference/language-concepts/01-php-keywords.md；07-php-mastery/reference/language-concepts/03-types-oop-modern.md；07-php-mastery/reference/quick-references/02-troubleshooting.md
- 内置能力：07-php-mastery/reference/language-concepts/02-built-in-functions.md；07-php-mastery/reference/language-concepts/03-types-oop-modern.md；07-php-mastery/reference/language-concepts/06-generators-iterators.md；07-php-mastery/reference/language-concepts/08-reflection-attributes.md；07-php-mastery/reference/language-concepts/09-strings-regex.md；07-php-mastery/reference/language-concepts/12-modern-php-85.md；07-php-mastery/reference/language-concepts/15-superglobals.md；07-php-mastery/reference/library-guides/01-standard-library-spl.md；07-php-mastery/reference/library-guides/02-composer-ecosystem.md；07-php-mastery/reference/library-guides/03-pdo.md；07-php-mastery/reference/library-guides/04-json.md；07-php-mastery/reference/library-guides/07-extension-map.md
- 标准库：07-php-mastery/reference/library-guides/01-standard-library-spl.md；07-php-mastery/reference/library-guides/07-extension-map.md
- basics 练习/自测信号：8 篇；projects 验收信号：4 篇。
- 完全相同的一级标题组：0 组；含易变版本/API 用语的文档：18 篇（仅表示需要随技术基线复核，不表示已过期）。

### 08-java-revisited

- 关键词：08-java-revisited/reference/framework-essentials/02-jpa-essentials.md；08-java-revisited/reference/language-concepts/01-java-keywords.md；08-java-revisited/reference/language-concepts/06-exceptions-resources.md
- 内置能力：08-java-revisited/reference/framework-essentials/06-spring-security-essentials.md；08-java-revisited/reference/language-concepts/01-java-keywords.md；08-java-revisited/reference/language-concepts/08-enums.md；08-java-revisited/reference/language-concepts/09-annotations.md；08-java-revisited/reference/library-guides/05-java-util-function.md；08-java-revisited/reference/library-guides/09-jdk-package-map.md
- 标准库：08-java-revisited/reference/language-concepts/01-java-keywords.md；08-java-revisited/reference/library-guides/01-standard-library.md；08-java-revisited/reference/library-guides/03-java-lang.md；08-java-revisited/reference/library-guides/04-java-io.md；08-java-revisited/reference/library-guides/05-java-util-function.md；08-java-revisited/reference/library-guides/06-java-math.md；08-java-revisited/reference/library-guides/07-java-text-and-time-format.md；08-java-revisited/reference/library-guides/08-java-util-regex.md；08-java-revisited/reference/library-guides/09-jdk-package-map.md
- basics 练习/自测信号：8 篇；projects 验收信号：4 篇。
- 完全相同的一级标题组：0 组；含易变版本/API 用语的文档：9 篇（仅表示需要随技术基线复核，不表示已过期）。

### 09-nodejs-backend

- 关键词：09-nodejs-backend/reference/language-concepts/01-js-modern-syntax.md；09-nodejs-backend/reference/language-concepts/07-js-core-semantics.md
- 内置能力：09-nodejs-backend/reference/framework-essentials/01-hono-essentials.md；09-nodejs-backend/reference/framework-essentials/02-fastify-nestjs.md；09-nodejs-backend/reference/language-concepts/03-node-core-api.md；09-nodejs-backend/reference/language-concepts/06-esm-module-resolution.md；09-nodejs-backend/reference/language-concepts/08-type-coercion-collections.md；09-nodejs-backend/reference/language-concepts/09-globals-reference.md；09-nodejs-backend/reference/library-guides/01-core-modules.md；09-nodejs-backend/reference/library-guides/02-ecosystem-libs.md；09-nodejs-backend/reference/library-guides/03-crypto.md；09-nodejs-backend/reference/library-guides/06-util.md；09-nodejs-backend/reference/library-guides/08-test-runner.md；09-nodejs-backend/reference/library-guides/09-zlib.md；09-nodejs-backend/reference/quick-references/01-node-cheatsheet.md
- 标准库：09-nodejs-backend/reference/library-guides/01-core-modules.md；09-nodejs-backend/reference/library-guides/09-zlib.md
- 共享 JavaScript 基础参考（关键词、内置能力、标准库）：shared-resources/javascript-keywords.md；shared-resources/javascript-builtins.md；shared-resources/javascript-standard-library.md
- basics 练习/自测信号：8 篇；projects 验收信号：4 篇。
- 完全相同的一级标题组：0 组；含易变版本/API 用语的文档：16 篇（仅表示需要随技术基线复核，不表示已过期）。

### 10-python-discovery

- 关键词：10-python-discovery/reference/language-concepts/01-python-keywords.md；10-python-discovery/reference/language-concepts/02-built-in-functions.md；10-python-discovery/reference/language-concepts/11-modules-imports.md；10-python-discovery/reference/language-concepts/13-dataclasses.md；10-python-discovery/reference/language-concepts/17-functions-parameters.md；10-python-discovery/reference/library-guides/06-functools-subprocess.md
- 内置能力：10-python-discovery/reference/framework-essentials/02-django-flask.md；10-python-discovery/reference/language-concepts/02-built-in-functions.md；10-python-discovery/reference/language-concepts/03-data-structures.md；10-python-discovery/reference/language-concepts/05-typing-annotations.md；10-python-discovery/reference/language-concepts/09-asyncio-concurrency.md；10-python-discovery/reference/language-concepts/11-modules-imports.md；10-python-discovery/reference/language-concepts/15-closures-and-scope.md；10-python-discovery/reference/library-guides/01-standard-library.md；10-python-discovery/reference/library-guides/02-ecosystem-libs.md；10-python-discovery/reference/quick-references/01-python-cheatsheet.md
- 标准库：10-python-discovery/reference/language-concepts/02-built-in-functions.md；10-python-discovery/reference/language-concepts/03-data-structures.md；10-python-discovery/reference/language-concepts/06-decorators.md；10-python-discovery/reference/language-concepts/09-asyncio-concurrency.md；10-python-discovery/reference/language-concepts/12-string-formatting.md；10-python-discovery/reference/library-guides/01-standard-library.md；10-python-discovery/reference/library-guides/04-os-sys.md
- basics 练习/自测信号：8 篇；projects 验收信号：4 篇。
- 完全相同的一级标题组：0 组；含易变版本/API 用语的文档：6 篇（仅表示需要随技术基线复核，不表示已过期）。

### 11-rust-cross-platform

- 关键词：11-rust-cross-platform/reference/language-concepts/05-macros.md；11-rust-cross-platform/reference/language-concepts/06-unsafe.md；11-rust-cross-platform/reference/language-concepts/09-keywords-and-syntax.md；11-rust-cross-platform/reference/library-guides/13-serde-guide.md
- 内置能力：11-rust-cross-platform/reference/language-concepts/03-const-generics.md；11-rust-cross-platform/reference/language-concepts/10-standard-types-and-methods.md；11-rust-cross-platform/reference/library-guides/15-standard-library-map.md
- 标准库：11-rust-cross-platform/reference/language-concepts/05-macros.md；11-rust-cross-platform/reference/language-concepts/09-keywords-and-syntax.md；11-rust-cross-platform/reference/library-guides/15-standard-library-map.md
- basics 练习/自测信号：10 篇；projects 验收信号：5 篇。
- 完全相同的一级标题组：0 组；含易变版本/API 用语的文档：14 篇（仅表示需要随技术基线复核，不表示已过期）。

## 待人工确认的结构缺口

这些是待办线索，不是自动判定的质量缺陷。不同技术栈可以按结构适配原则省略或合并目录，但需要在模块 README 或导读中写出理由与替代入口。

## 重复与过期风险的机械线索

- `duplicate_h1_groups` 只统计同一模块内完全相同的一级标题，便于人工判断是否是重复文章或同名但不同语境的内容。
- `time_sensitive_claim_documents` 匹配“最新 / latest / 当前版本 / 弃用”等用语。它标示版本、维护状态或 API 变化的复核队列，不能单凭文字命中断言内容过期。
- 本次结构盘点没有发现空目录或缺失的一级模块目录；这只说明骨架齐全，不能证明目录内的解释已达到交付标准。

## 下一轮人工验收的固定口径

1. 先确认结构缺口是有意适配还是实际缺失；确认后更新模块 README 和本清单。
2. 对每个 reference 条目核对定义、签名/输入输出、边界、反例、版本来源和可执行最小示例。
3. 对每个 basics 链路核对前置知识、可观察结果与练习反馈；对每个 project 核对需求、运行方式、阶段产物和验收标准。
4. 框架与平台内容按真实最小项目安装依赖并构建；无法在当前平台验证的内容明确标为待验证，不以目录或静态检查代替。
