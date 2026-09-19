# 验证覆盖状态台账

这是一份证据台账，不是把含有“实测”“通过”等措辞的文章自动判为正确。一个运行记录只覆盖报告中命名的完整示例或检查用例，**不覆盖整篇文档、框架工程或部署环境**。

## 汇总

| 指标 | 数量 |
|---|---:|
| 纳入模块文档 | 642 |
| 主状态：not_verified | 467 |
| 主状态：runtime | 175 |
| 验证措辞出现次数 | 142 |
| 措辞分类：source_has_limited_runtime_evidence | 88 |
| 措辞分类：unbound_verification_wording | 54 |

## 语法级覆盖（不能当作运行覆盖）

| 检查 | 数量 | 范围 |
|---|---:|---|
| `PASS_SYNTAX` | 1,165 | TS/JS 围栏纯语法解析；不验证类型、Hook、依赖版本或框架工程。 |
| `NOT_VERIFIED_ARKTS` | 1 | ArkTS 壳工程示意，缺少 OpenHarmony 工具链。 |

## 状态定义

| 状态 | 含义 |
|---|---|
| `runtime` | 存在命名的实际运行记录；范围由该记录的 `scope` 限定。 |
| `not_verified` | 没有找到与此文件绑定的命名运行记录。不是技术错误结论。 |

历史 Web 报告 `final-web-examples.json` 的结果混合运行与 TypeScript 编译检查，未逐用例绑定来源。其结果与来源集合保留在 JSON 的 `corpus_checks`，不能据此给来源文档自动赋予 `runtime/PASS`。


## 文档级证据

| 模块 | 文档 | 主状态 | 命名运行记录数 | 验证措辞数 |
|---|---|---|---:|---:|
| Go | [01-go-backend/LEARNING_GUIDE.md](../../../../01-go-backend/LEARNING_GUIDE.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/README.md](../../../../01-go-backend/README.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/advanced-topics/api-advanced/01-restful-patterns.md](../../../../01-go-backend/advanced-topics/api-advanced/01-restful-patterns.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/advanced-topics/api-advanced/02-graphql-apis.md](../../../../01-go-backend/advanced-topics/api-advanced/02-graphql-apis.md) | `not_verified` | 0 | 1 |
| Go | [01-go-backend/advanced-topics/architecture/01-microservices-design.md](../../../../01-go-backend/advanced-topics/architecture/01-microservices-design.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/advanced-topics/performance/01-concurrency-patterns.md](../../../../01-go-backend/advanced-topics/performance/01-concurrency-patterns.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/advanced-topics/performance/02-performance-tuning.md](../../../../01-go-backend/advanced-topics/performance/02-performance-tuning.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/advanced-topics/security/01-security-best-practices.md](../../../../01-go-backend/advanced-topics/security/01-security-best-practices.md) | `runtime` | 1 | 1 |
| Go | [01-go-backend/basics/01-environment-setup.md](../../../../01-go-backend/basics/01-environment-setup.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/basics/02-first-program.md](../../../../01-go-backend/basics/02-first-program.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/basics/03-variables-constants.md](../../../../01-go-backend/basics/03-variables-constants.md) | `runtime` | 2 | 0 |
| Go | [01-go-backend/basics/04-composite-types.md](../../../../01-go-backend/basics/04-composite-types.md) | `runtime` | 4 | 0 |
| Go | [01-go-backend/basics/05-functions-methods.md](../../../../01-go-backend/basics/05-functions-methods.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/basics/06-control-structures.md](../../../../01-go-backend/basics/06-control-structures.md) | `runtime` | 2 | 1 |
| Go | [01-go-backend/basics/07-concurrency-basics.md](../../../../01-go-backend/basics/07-concurrency-basics.md) | `runtime` | 4 | 0 |
| Go | [01-go-backend/basics/08-error-handling.md](../../../../01-go-backend/basics/08-error-handling.md) | `runtime` | 5 | 0 |
| Go | [01-go-backend/deployment/01-containerization.md](../../../../01-go-backend/deployment/01-containerization.md) | `not_verified` | 0 | 1 |
| Go | [01-go-backend/deployment/02-ci-cd-pipelines.md](../../../../01-go-backend/deployment/02-ci-cd-pipelines.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/deployment/03-kubernetes-deployment.md](../../../../01-go-backend/deployment/03-kubernetes-deployment.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/deployment/04-observability.md](../../../../01-go-backend/deployment/04-observability.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/frameworks/01-gin-framework-basics.md](../../../../01-go-backend/frameworks/01-gin-framework-basics.md) | `not_verified` | 0 | 1 |
| Go | [01-go-backend/frameworks/02-gin-framework-advanced.md](../../../../01-go-backend/frameworks/02-gin-framework-advanced.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/frameworks/03-gorm-orm-complete.md](../../../../01-go-backend/frameworks/03-gorm-orm-complete.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/frameworks/04-mongodb-go-driver.md](../../../../01-go-backend/frameworks/04-mongodb-go-driver.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/frameworks/05-go-redis-complete.md](../../../../01-go-backend/frameworks/05-go-redis-complete.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/frameworks/06-grpc-service-development.md](../../../../01-go-backend/frameworks/06-grpc-service-development.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/projects/00-stdlib-todo-cli.md](../../../../01-go-backend/projects/00-stdlib-todo-cli.md) | `runtime` | 1 | 1 |
| Go | [01-go-backend/projects/01-rest-api-server.md](../../../../01-go-backend/projects/01-rest-api-server.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/projects/02-microservices-demo.md](../../../../01-go-backend/projects/02-microservices-demo.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/projects/03-real-time-app.md](../../../../01-go-backend/projects/03-real-time-app.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/projects/04-cli-tool.md](../../../../01-go-backend/projects/04-cli-tool.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/reference/framework-essentials/01-gin-framework.md](../../../../01-go-backend/reference/framework-essentials/01-gin-framework.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/reference/framework-essentials/02-gorm-orm.md](../../../../01-go-backend/reference/framework-essentials/02-gorm-orm.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/reference/framework-essentials/03-sqlc-vs-gorm.md](../../../../01-go-backend/reference/framework-essentials/03-sqlc-vs-gorm.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/reference/framework-essentials/04-router-selection.md](../../../../01-go-backend/reference/framework-essentials/04-router-selection.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/reference/framework-essentials/05-mongo-driver.md](../../../../01-go-backend/reference/framework-essentials/05-mongo-driver.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/reference/framework-essentials/06-go-redis.md](../../../../01-go-backend/reference/framework-essentials/06-go-redis.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/reference/language-concepts/01-go-keywords.md](../../../../01-go-backend/reference/language-concepts/01-go-keywords.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/language-concepts/02-go-built-in-functions.md](../../../../01-go-backend/reference/language-concepts/02-go-built-in-functions.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/language-concepts/03-go-programming-essentials.md](../../../../01-go-backend/reference/language-concepts/03-go-programming-essentials.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/reference/language-concepts/04-go-data-types.md](../../../../01-go-backend/reference/language-concepts/04-go-data-types.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/language-concepts/05-go-control-flow.md](../../../../01-go-backend/reference/language-concepts/05-go-control-flow.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/language-concepts/06-go-oop-concepts.md](../../../../01-go-backend/reference/language-concepts/06-go-oop-concepts.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/language-concepts/07-error-handling.md](../../../../01-go-backend/reference/language-concepts/07-error-handling.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/language-concepts/08-concurrency-basics.md](../../../../01-go-backend/reference/language-concepts/08-concurrency-basics.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/language-concepts/09-generics.md](../../../../01-go-backend/reference/language-concepts/09-generics.md) | `runtime` | 2 | 0 |
| Go | [01-go-backend/reference/language-concepts/10-slice-semantics.md](../../../../01-go-backend/reference/language-concepts/10-slice-semantics.md) | `runtime` | 2 | 0 |
| Go | [01-go-backend/reference/language-concepts/11-map-semantics.md](../../../../01-go-backend/reference/language-concepts/11-map-semantics.md) | `runtime` | 2 | 0 |
| Go | [01-go-backend/reference/language-concepts/12-channel-semantics.md](../../../../01-go-backend/reference/language-concepts/12-channel-semantics.md) | `runtime` | 1 | 1 |
| Go | [01-go-backend/reference/language-concepts/13-interface-semantics.md](../../../../01-go-backend/reference/language-concepts/13-interface-semantics.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/language-concepts/14-defer-panic-recover.md](../../../../01-go-backend/reference/language-concepts/14-defer-panic-recover.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/language-concepts/15-nil-semantics.md](../../../../01-go-backend/reference/language-concepts/15-nil-semantics.md) | `runtime` | 2 | 0 |
| Go | [01-go-backend/reference/library-guides/01-go-standard-library.md](../../../../01-go-backend/reference/library-guides/01-go-standard-library.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/library-guides/02-third-party-libs.md](../../../../01-go-backend/reference/library-guides/02-third-party-libs.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/reference/library-guides/03-net-http.md](../../../../01-go-backend/reference/library-guides/03-net-http.md) | `runtime` | 1 | 1 |
| Go | [01-go-backend/reference/library-guides/04-encoding-json.md](../../../../01-go-backend/reference/library-guides/04-encoding-json.md) | `runtime` | 1 | 1 |
| Go | [01-go-backend/reference/library-guides/05-context.md](../../../../01-go-backend/reference/library-guides/05-context.md) | `runtime` | 2 | 0 |
| Go | [01-go-backend/reference/library-guides/06-sync.md](../../../../01-go-backend/reference/library-guides/06-sync.md) | `runtime` | 2 | 2 |
| Go | [01-go-backend/reference/library-guides/07-database-sql.md](../../../../01-go-backend/reference/library-guides/07-database-sql.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/library-guides/08-time.md](../../../../01-go-backend/reference/library-guides/08-time.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/library-guides/09-errors.md](../../../../01-go-backend/reference/library-guides/09-errors.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/library-guides/10-io-bufio.md](../../../../01-go-backend/reference/library-guides/10-io-bufio.md) | `runtime` | 2 | 0 |
| Go | [01-go-backend/reference/library-guides/11-os.md](../../../../01-go-backend/reference/library-guides/11-os.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/library-guides/12-testing.md](../../../../01-go-backend/reference/library-guides/12-testing.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/library-guides/13-slices-maps.md](../../../../01-go-backend/reference/library-guides/13-slices-maps.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/library-guides/14-strconv.md](../../../../01-go-backend/reference/library-guides/14-strconv.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/library-guides/15-log-slog.md](../../../../01-go-backend/reference/library-guides/15-log-slog.md) | `runtime` | 1 | 0 |
| Go | [01-go-backend/reference/library-guides/16-flag.md](../../../../01-go-backend/reference/library-guides/16-flag.md) | `runtime` | 1 | 1 |
| Go | [01-go-backend/reference/library-guides/17-std-package-map.md](../../../../01-go-backend/reference/library-guides/17-std-package-map.md) | `runtime` | 1 | 1 |
| Go | [01-go-backend/reference/quick-references/01-syntax-cheatsheet.md](../../../../01-go-backend/reference/quick-references/01-syntax-cheatsheet.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/reference/quick-references/02-web-tools.md](../../../../01-go-backend/reference/quick-references/02-web-tools.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/reference/quick-references/03-troubleshooting.md](../../../../01-go-backend/reference/quick-references/03-troubleshooting.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/testing/01-unit-testing.md](../../../../01-go-backend/testing/01-unit-testing.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/testing/02-mocking-stubbing.md](../../../../01-go-backend/testing/02-mocking-stubbing.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/testing/03-integration-testing.md](../../../../01-go-backend/testing/03-integration-testing.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/testing/04-benchmarking.md](../../../../01-go-backend/testing/04-benchmarking.md) | `not_verified` | 0 | 0 |
| Go | [01-go-backend/testing/05-test-driven-development.md](../../../../01-go-backend/testing/05-test-driven-development.md) | `not_verified` | 0 | 2 |
| Next.js / TypeScript | [02-nextjs-frontend/LEARNING_GUIDE.md](../../../../02-nextjs-frontend/LEARNING_GUIDE.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/README.md](../../../../02-nextjs-frontend/README.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/advanced-topics/api-integration/01-graphql-apollo.md](../../../../02-nextjs-frontend/advanced-topics/api-integration/01-graphql-apollo.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/advanced-topics/architecture/01-scaling-patterns.md](../../../../02-nextjs-frontend/advanced-topics/architecture/01-scaling-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/advanced-topics/architecture/02-micro-frontends.md](../../../../02-nextjs-frontend/advanced-topics/architecture/02-micro-frontends.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/advanced-topics/performance/01-core-web-vitals.md](../../../../02-nextjs-frontend/advanced-topics/performance/01-core-web-vitals.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/advanced-topics/performance/02-advanced-optimization.md](../../../../02-nextjs-frontend/advanced-topics/performance/02-advanced-optimization.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/advanced-topics/security/01-security-best-practices.md](../../../../02-nextjs-frontend/advanced-topics/security/01-security-best-practices.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/basics/01-environment-setup.md](../../../../02-nextjs-frontend/basics/01-environment-setup.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/basics/02-first-nextjs-app.md](../../../../02-nextjs-frontend/basics/02-first-nextjs-app.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/basics/03-typescript-integration.md](../../../../02-nextjs-frontend/basics/03-typescript-integration.md) | `runtime` | 1 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/basics/04-layouts-routing.md](../../../../02-nextjs-frontend/basics/04-layouts-routing.md) | `runtime` | 1 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/basics/05-styling-with-tailwind.md](../../../../02-nextjs-frontend/basics/05-styling-with-tailwind.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/basics/06-data-fetching-basics.md](../../../../02-nextjs-frontend/basics/06-data-fetching-basics.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/basics/07-state-management.md](../../../../02-nextjs-frontend/basics/07-state-management.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/basics/08-first-project.md](../../../../02-nextjs-frontend/basics/08-first-project.md) | `runtime` | 1 | 1 |
| Next.js / TypeScript | [02-nextjs-frontend/deployment/01-vercel-deployment.md](../../../../02-nextjs-frontend/deployment/01-vercel-deployment.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/deployment/02-docker-containerization.md](../../../../02-nextjs-frontend/deployment/02-docker-containerization.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/deployment/03-ci-cd-pipelines.md](../../../../02-nextjs-frontend/deployment/03-ci-cd-pipelines.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/deployment/04-monitoring-analytics.md](../../../../02-nextjs-frontend/deployment/04-monitoring-analytics.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/frameworks/01-nextjs-16-complete.md](../../../../02-nextjs-frontend/frameworks/01-nextjs-16-complete.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/frameworks/02-react-19-integration.md](../../../../02-nextjs-frontend/frameworks/02-react-19-integration.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/frameworks/03-full-stack-patterns.md](../../../../02-nextjs-frontend/frameworks/03-full-stack-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/frameworks/04-performance-optimization.md](../../../../02-nextjs-frontend/frameworks/04-performance-optimization.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/projects/01-corporate-landing.md](../../../../02-nextjs-frontend/projects/01-corporate-landing.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/projects/02-ecommerce-store.md](../../../../02-nextjs-frontend/projects/02-ecommerce-store.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/projects/03-dashboard-analytics.md](../../../../02-nextjs-frontend/projects/03-dashboard-analytics.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/projects/04-saas-platform.md](../../../../02-nextjs-frontend/projects/04-saas-platform.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/development-tools/01-testing-tools.md](../../../../02-nextjs-frontend/reference/development-tools/01-testing-tools.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/development-tools/02-styling-tools.md](../../../../02-nextjs-frontend/reference/development-tools/02-styling-tools.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/development-tools/03-package-managers.md](../../../../02-nextjs-frontend/reference/development-tools/03-package-managers.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/development-tools/04-debugging-tools.md](../../../../02-nextjs-frontend/reference/development-tools/04-debugging-tools.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/01-app-router-patterns.md](../../../../02-nextjs-frontend/reference/framework-patterns/01-app-router-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/02-server-components-patterns.md](../../../../02-nextjs-frontend/reference/framework-patterns/02-server-components-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/03-client-components-patterns.md](../../../../02-nextjs-frontend/reference/framework-patterns/03-client-components-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/04-data-fetching-patterns.md](../../../../02-nextjs-frontend/reference/framework-patterns/04-data-fetching-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/05-state-management-patterns.md](../../../../02-nextjs-frontend/reference/framework-patterns/05-state-management-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/06-form-validation-patterns.md](../../../../02-nextjs-frontend/reference/framework-patterns/06-form-validation-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/07-authentication-flows.md](../../../../02-nextjs-frontend/reference/framework-patterns/07-authentication-flows.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/08-caching-patterns.md](../../../../02-nextjs-frontend/reference/framework-patterns/08-caching-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/09-async-request-apis.md](../../../../02-nextjs-frontend/reference/framework-patterns/09-async-request-apis.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/10-proxy-patterns.md](../../../../02-nextjs-frontend/reference/framework-patterns/10-proxy-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/11-error-loading-patterns.md](../../../../02-nextjs-frontend/reference/framework-patterns/11-error-loading-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/12-metadata-and-script.md](../../../../02-nextjs-frontend/reference/framework-patterns/12-metadata-and-script.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/13-route-segment-config.md](../../../../02-nextjs-frontend/reference/framework-patterns/13-route-segment-config.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/framework-patterns/14-env-vars.md](../../../../02-nextjs-frontend/reference/framework-patterns/14-env-vars.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/language-concepts/01-react-syntax-cheatsheet.md](../../../../02-nextjs-frontend/reference/language-concepts/01-react-syntax-cheatsheet.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/language-concepts/02-nextjs-api-reference.md](../../../../02-nextjs-frontend/reference/language-concepts/02-nextjs-api-reference.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/language-concepts/03-typescript-types.md](../../../../02-nextjs-frontend/reference/language-concepts/03-typescript-types.md) | `runtime` | 1 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/language-concepts/04-javascript-modern.md](../../../../02-nextjs-frontend/reference/language-concepts/04-javascript-modern.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/language-concepts/05-css-patterns.md](../../../../02-nextjs-frontend/reference/language-concepts/05-css-patterns.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/language-concepts/06-react-19-hooks.md](../../../../02-nextjs-frontend/reference/language-concepts/06-react-19-hooks.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/language-concepts/07-type-narrowing-guards.md](../../../../02-nextjs-frontend/reference/language-concepts/07-type-narrowing-guards.md) | `runtime` | 1 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/language-concepts/08-ts-declarations-modules.md](../../../../02-nextjs-frontend/reference/language-concepts/08-ts-declarations-modules.md) | `not_verified` | 0 | 1 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/language-concepts/09-js-core-semantics.md](../../../../02-nextjs-frontend/reference/language-concepts/09-js-core-semantics.md) | `runtime` | 4 | 1 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/language-concepts/10-web-platform-apis.md](../../../../02-nextjs-frontend/reference/language-concepts/10-web-platform-apis.md) | `runtime` | 3 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/library-guides/03-ecosystem-map.md](../../../../02-nextjs-frontend/reference/library-guides/03-ecosystem-map.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/performance-optimization/01-rendering-optimization.md](../../../../02-nextjs-frontend/reference/performance-optimization/01-rendering-optimization.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/performance-optimization/02-bundle-optimization.md](../../../../02-nextjs-frontend/reference/performance-optimization/02-bundle-optimization.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/reference/performance-optimization/03-image-font-optimization.md](../../../../02-nextjs-frontend/reference/performance-optimization/03-image-font-optimization.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/testing/01-unit-testing.md](../../../../02-nextjs-frontend/testing/01-unit-testing.md) | `runtime` | 2 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/testing/02-component-testing.md](../../../../02-nextjs-frontend/testing/02-component-testing.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/testing/03-e2e-testing.md](../../../../02-nextjs-frontend/testing/03-e2e-testing.md) | `not_verified` | 0 | 0 |
| Next.js / TypeScript | [02-nextjs-frontend/testing/04-performance-testing.md](../../../../02-nextjs-frontend/testing/04-performance-testing.md) | `not_verified` | 0 | 2 |
| TanStack / TypeScript | [03-tanstack-stack/LEARNING_GUIDE.md](../../../../03-tanstack-stack/LEARNING_GUIDE.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/README.md](../../../../03-tanstack-stack/README.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/advanced-topics/architecture/01-cache-architecture.md](../../../../03-tanstack-stack/advanced-topics/architecture/01-cache-architecture.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/advanced-topics/performance/01-query-optimization.md](../../../../03-tanstack-stack/advanced-topics/performance/01-query-optimization.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/advanced-topics/performance/02-rendering-performance.md](../../../../03-tanstack-stack/advanced-topics/performance/02-rendering-performance.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/advanced-topics/security/01-security-practices.md](../../../../03-tanstack-stack/advanced-topics/security/01-security-practices.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/basics/01-environment-setup.md](../../../../03-tanstack-stack/basics/01-environment-setup.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/basics/02-headless-philosophy.md](../../../../03-tanstack-stack/basics/02-headless-philosophy.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/basics/03-query-fundamentals.md](../../../../03-tanstack-stack/basics/03-query-fundamentals.md) | `runtime` | 1 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/basics/04-table-fundamentals.md](../../../../03-tanstack-stack/basics/04-table-fundamentals.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/basics/05-router-fundamentals.md](../../../../03-tanstack-stack/basics/05-router-fundamentals.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/basics/06-form-fundamentals.md](../../../../03-tanstack-stack/basics/06-form-fundamentals.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/basics/07-advanced-features.md](../../../../03-tanstack-stack/basics/07-advanced-features.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/basics/08-first-project.md](../../../../03-tanstack-stack/basics/08-first-project.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/deployment/01-ci-cd-pipelines.md](../../../../03-tanstack-stack/deployment/01-ci-cd-pipelines.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/deployment/02-vercel-deployment.md](../../../../03-tanstack-stack/deployment/02-vercel-deployment.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/deployment/03-observability.md](../../../../03-tanstack-stack/deployment/03-observability.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/frameworks/01-tanstack-query-basics.md](../../../../03-tanstack-stack/frameworks/01-tanstack-query-basics.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/frameworks/02-tanstack-query-advanced.md](../../../../03-tanstack-stack/frameworks/02-tanstack-query-advanced.md) | `not_verified` | 0 | 1 |
| TanStack / TypeScript | [03-tanstack-stack/frameworks/03-ecosystem-integration.md](../../../../03-tanstack-stack/frameworks/03-ecosystem-integration.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/frameworks/04-devtools.md](../../../../03-tanstack-stack/frameworks/04-devtools.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/projects/01-todo-app.md](../../../../03-tanstack-stack/projects/01-todo-app.md) | `runtime` | 1 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/projects/02-data-dashboard.md](../../../../03-tanstack-stack/projects/02-data-dashboard.md) | `not_verified` | 0 | 1 |
| TanStack / TypeScript | [03-tanstack-stack/projects/03-collaborative-kanban.md](../../../../03-tanstack-stack/projects/03-collaborative-kanban.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/projects/04-saas-admin-platform.md](../../../../03-tanstack-stack/projects/04-saas-admin-platform.md) | `not_verified` | 0 | 1 |
| TanStack / TypeScript | [03-tanstack-stack/reference/framework-essentials/01-query-essentials.md](../../../../03-tanstack-stack/reference/framework-essentials/01-query-essentials.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/framework-essentials/02-router-essentials.md](../../../../03-tanstack-stack/reference/framework-essentials/02-router-essentials.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/framework-essentials/03-queryclient-config.md](../../../../03-tanstack-stack/reference/framework-essentials/03-queryclient-config.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/framework-essentials/04-prefetch-ssr.md](../../../../03-tanstack-stack/reference/framework-essentials/04-prefetch-ssr.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/framework-essentials/05-mutation-state.md](../../../../03-tanstack-stack/reference/framework-essentials/05-mutation-state.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/framework-essentials/06-start-server-functions.md](../../../../03-tanstack-stack/reference/framework-essentials/06-start-server-functions.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/01-query-core-api.md](../../../../03-tanstack-stack/reference/language-concepts/01-query-core-api.md) | `runtime` | 1 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/02-table-core-api.md](../../../../03-tanstack-stack/reference/language-concepts/02-table-core-api.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/03-router-core-api.md](../../../../03-tanstack-stack/reference/language-concepts/03-router-core-api.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/04-form-core-api.md](../../../../03-tanstack-stack/reference/language-concepts/04-form-core-api.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/05-typescript-patterns.md](../../../../03-tanstack-stack/reference/language-concepts/05-typescript-patterns.md) | `runtime` | 2 | 1 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/06-optimistic-update.md](../../../../03-tanstack-stack/reference/language-concepts/06-optimistic-update.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/07-infinite-query.md](../../../../03-tanstack-stack/reference/language-concepts/07-infinite-query.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/08-placeholder-data.md](../../../../03-tanstack-stack/reference/language-concepts/08-placeholder-data.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/09-suspense-query.md](../../../../03-tanstack-stack/reference/language-concepts/09-suspense-query.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/10-network-mode.md](../../../../03-tanstack-stack/reference/language-concepts/10-network-mode.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/11-search-params.md](../../../../03-tanstack-stack/reference/language-concepts/11-search-params.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/12-use-queries.md](../../../../03-tanstack-stack/reference/language-concepts/12-use-queries.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/13-use-is-fetching-use-is-mutating.md](../../../../03-tanstack-stack/reference/language-concepts/13-use-is-fetching-use-is-mutating.md) | `not_verified` | 0 | 1 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/14-query-persistence.md](../../../../03-tanstack-stack/reference/language-concepts/14-query-persistence.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/15-enabled-conditional-queries.md](../../../../03-tanstack-stack/reference/language-concepts/15-enabled-conditional-queries.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/16-render-optimization.md](../../../../03-tanstack-stack/reference/language-concepts/16-render-optimization.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/17-flexrender.md](../../../../03-tanstack-stack/reference/language-concepts/17-flexrender.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/18-controlled-state.md](../../../../03-tanstack-stack/reference/language-concepts/18-controlled-state.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/19-outlet-and-route-components.md](../../../../03-tanstack-stack/reference/language-concepts/19-outlet-and-route-components.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/20-use-match-hooks.md](../../../../03-tanstack-stack/reference/language-concepts/20-use-match-hooks.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/language-concepts/21-usefield-and-createformhook.md](../../../../03-tanstack-stack/reference/language-concepts/21-usefield-and-createformhook.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/library-guides/01-ecosystem-integrations.md](../../../../03-tanstack-stack/reference/library-guides/01-ecosystem-integrations.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/library-guides/02-related-libs.md](../../../../03-tanstack-stack/reference/library-guides/02-related-libs.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/library-guides/03-language-web-foundations.md](../../../../03-tanstack-stack/reference/library-guides/03-language-web-foundations.md) | `runtime` | 2 | 2 |
| TanStack / TypeScript | [03-tanstack-stack/reference/quick-references/01-syntax-cheatsheet.md](../../../../03-tanstack-stack/reference/quick-references/01-syntax-cheatsheet.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/reference/quick-references/02-troubleshooting.md](../../../../03-tanstack-stack/reference/quick-references/02-troubleshooting.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/testing/01-unit-testing.md](../../../../03-tanstack-stack/testing/01-unit-testing.md) | `runtime` | 1 | 1 |
| TanStack / TypeScript | [03-tanstack-stack/testing/02-mocking-server.md](../../../../03-tanstack-stack/testing/02-mocking-server.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/testing/03-integration-testing.md](../../../../03-tanstack-stack/testing/03-integration-testing.md) | `not_verified` | 0 | 0 |
| TanStack / TypeScript | [03-tanstack-stack/testing/04-e2e-testing.md](../../../../03-tanstack-stack/testing/04-e2e-testing.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/LEARNING_GUIDE.md](../../../../04-multiplatform-apps/LEARNING_GUIDE.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/README.md](../../../../04-multiplatform-apps/README.md) | `not_verified` | 0 | 1 |
| React Native / Multi-platform | [04-multiplatform-apps/React Native三端原生应用学习路线.md](../../../../04-multiplatform-apps/React Native三端原生应用学习路线.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/advanced-topics/architecture/01-new-architecture.md](../../../../04-multiplatform-apps/advanced-topics/architecture/01-new-architecture.md) | `not_verified` | 0 | 1 |
| React Native / Multi-platform | [04-multiplatform-apps/advanced-topics/performance/01-rendering-performance.md](../../../../04-multiplatform-apps/advanced-topics/performance/01-rendering-performance.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/advanced-topics/performance/02-startup-optimization.md](../../../../04-multiplatform-apps/advanced-topics/performance/02-startup-optimization.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/advanced-topics/security/01-security-practices.md](../../../../04-multiplatform-apps/advanced-topics/security/01-security-practices.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/basics/01-environment-setup.md](../../../../04-multiplatform-apps/basics/01-environment-setup.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/basics/02-first-app.md](../../../../04-multiplatform-apps/basics/02-first-app.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/basics/03-components-jsx.md](../../../../04-multiplatform-apps/basics/03-components-jsx.md) | `runtime` | 1 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/basics/04-state-hooks.md](../../../../04-multiplatform-apps/basics/04-state-hooks.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/basics/05-navigation.md](../../../../04-multiplatform-apps/basics/05-navigation.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/basics/06-native-modules.md](../../../../04-multiplatform-apps/basics/06-native-modules.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/basics/07-advanced-features.md](../../../../04-multiplatform-apps/basics/07-advanced-features.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/basics/08-first-project.md](../../../../04-multiplatform-apps/basics/08-first-project.md) | `runtime` | 1 | 1 |
| React Native / Multi-platform | [04-multiplatform-apps/deployment/01-eas-build.md](../../../../04-multiplatform-apps/deployment/01-eas-build.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/deployment/02-app-store-release.md](../../../../04-multiplatform-apps/deployment/02-app-store-release.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/deployment/03-ota-updates-observability.md](../../../../04-multiplatform-apps/deployment/03-ota-updates-observability.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/frameworks/01-react-native-basics.md](../../../../04-multiplatform-apps/frameworks/01-react-native-basics.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/frameworks/02-react-native-advanced.md](../../../../04-multiplatform-apps/frameworks/02-react-native-advanced.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/frameworks/03-ecosystem-integration.md](../../../../04-multiplatform-apps/frameworks/03-ecosystem-integration.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/frameworks/04-devtools.md](../../../../04-multiplatform-apps/frameworks/04-devtools.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/projects/01-todo-app.md](../../../../04-multiplatform-apps/projects/01-todo-app.md) | `runtime` | 1 | 2 |
| React Native / Multi-platform | [04-multiplatform-apps/projects/02-weather-app.md](../../../../04-multiplatform-apps/projects/02-weather-app.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/projects/03-chat-app.md](../../../../04-multiplatform-apps/projects/03-chat-app.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/projects/04-production-mobile-app.md](../../../../04-multiplatform-apps/projects/04-production-mobile-app.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/framework-essentials/01-expo-essentials.md](../../../../04-multiplatform-apps/reference/framework-essentials/01-expo-essentials.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/framework-essentials/02-navigation-essentials.md](../../../../04-multiplatform-apps/reference/framework-essentials/02-navigation-essentials.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/framework-essentials/03-config-plugins-prebuild.md](../../../../04-multiplatform-apps/reference/framework-essentials/03-config-plugins-prebuild.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/framework-essentials/04-dev-client-and-updates.md](../../../../04-multiplatform-apps/reference/framework-essentials/04-dev-client-and-updates.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/01-rn-core-api.md](../../../../04-multiplatform-apps/reference/language-concepts/01-rn-core-api.md) | `not_verified` | 0 | 1 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/02-components-props.md](../../../../04-multiplatform-apps/reference/language-concepts/02-components-props.md) | `runtime` | 1 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/03-hooks-reference.md](../../../../04-multiplatform-apps/reference/language-concepts/03-hooks-reference.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/04-typescript-patterns.md](../../../../04-multiplatform-apps/reference/language-concepts/04-typescript-patterns.md) | `runtime` | 1 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/05-harmonyos-rnoh-api.md](../../../../04-multiplatform-apps/reference/language-concepts/05-harmonyos-rnoh-api.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/06-component-lifecycle.md](../../../../04-multiplatform-apps/reference/language-concepts/06-component-lifecycle.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/07-state-management.md](../../../../04-multiplatform-apps/reference/language-concepts/07-state-management.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/08-bridge-principles.md](../../../../04-multiplatform-apps/reference/language-concepts/08-bridge-principles.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/09-navigation-model.md](../../../../04-multiplatform-apps/reference/language-concepts/09-navigation-model.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/10-styling-model.md](../../../../04-multiplatform-apps/reference/language-concepts/10-styling-model.md) | `not_verified` | 0 | 1 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/11-new-architecture-terms.md](../../../../04-multiplatform-apps/reference/language-concepts/11-new-architecture-terms.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/12-list-performance-model.md](../../../../04-multiplatform-apps/reference/language-concepts/12-list-performance-model.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/language-concepts/13-platform-api-map.md](../../../../04-multiplatform-apps/reference/language-concepts/13-platform-api-map.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/library-guides/01-state-and-data.md](../../../../04-multiplatform-apps/reference/library-guides/01-state-and-data.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/library-guides/02-native-and-device-libs.md](../../../../04-multiplatform-apps/reference/library-guides/02-native-and-device-libs.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/library-guides/03-storage-options.md](../../../../04-multiplatform-apps/reference/library-guides/03-storage-options.md) | `not_verified` | 0 | 1 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/library-guides/04-animation-gesture-libs.md](../../../../04-multiplatform-apps/reference/library-guides/04-animation-gesture-libs.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/quick-references/01-cli-and-debug-cheatsheet.md](../../../../04-multiplatform-apps/reference/quick-references/01-cli-and-debug-cheatsheet.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/reference/quick-references/02-troubleshooting.md](../../../../04-multiplatform-apps/reference/quick-references/02-troubleshooting.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/testing/01-unit-testing.md](../../../../04-multiplatform-apps/testing/01-unit-testing.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/testing/02-component-testing.md](../../../../04-multiplatform-apps/testing/02-component-testing.md) | `not_verified` | 0 | 0 |
| React Native / Multi-platform | [04-multiplatform-apps/testing/03-e2e-testing.md](../../../../04-multiplatform-apps/testing/03-e2e-testing.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/Android原生开发学习路线.md](../../../../05-kotlin-compose/Android原生开发学习路线.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/LEARNING_GUIDE.md](../../../../05-kotlin-compose/LEARNING_GUIDE.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/README.md](../../../../05-kotlin-compose/README.md) | `not_verified` | 0 | 1 |
| Kotlin / Compose | [05-kotlin-compose/advanced-topics/architecture/01-app-architecture.md](../../../../05-kotlin-compose/advanced-topics/architecture/01-app-architecture.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/advanced-topics/performance/01-recomposition-optimization.md](../../../../05-kotlin-compose/advanced-topics/performance/01-recomposition-optimization.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/advanced-topics/performance/02-startup-memory.md](../../../../05-kotlin-compose/advanced-topics/performance/02-startup-memory.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/advanced-topics/security/01-security-practices.md](../../../../05-kotlin-compose/advanced-topics/security/01-security-practices.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/basics/01-environment-setup.md](../../../../05-kotlin-compose/basics/01-environment-setup.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/basics/02-first-compose-app.md](../../../../05-kotlin-compose/basics/02-first-compose-app.md) | `not_verified` | 0 | 1 |
| Kotlin / Compose | [05-kotlin-compose/basics/03-kotlin-syntax-essentials.md](../../../../05-kotlin-compose/basics/03-kotlin-syntax-essentials.md) | `runtime` | 1 | 0 |
| Kotlin / Compose | [05-kotlin-compose/basics/04-composables-state.md](../../../../05-kotlin-compose/basics/04-composables-state.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/basics/05-layouts.md](../../../../05-kotlin-compose/basics/05-layouts.md) | `not_verified` | 0 | 1 |
| Kotlin / Compose | [05-kotlin-compose/basics/06-navigation.md](../../../../05-kotlin-compose/basics/06-navigation.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/basics/07-coroutines-flow-basics.md](../../../../05-kotlin-compose/basics/07-coroutines-flow-basics.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/basics/08-first-project.md](../../../../05-kotlin-compose/basics/08-first-project.md) | `runtime` | 1 | 2 |
| Kotlin / Compose | [05-kotlin-compose/deployment/01-release-build.md](../../../../05-kotlin-compose/deployment/01-release-build.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/deployment/02-play-store-release.md](../../../../05-kotlin-compose/deployment/02-play-store-release.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/deployment/03-ci-cd-observability.md](../../../../05-kotlin-compose/deployment/03-ci-cd-observability.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/frameworks/01-compose-basics.md](../../../../05-kotlin-compose/frameworks/01-compose-basics.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/frameworks/02-compose-advanced.md](../../../../05-kotlin-compose/frameworks/02-compose-advanced.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/frameworks/03-ecosystem-integration.md](../../../../05-kotlin-compose/frameworks/03-ecosystem-integration.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/frameworks/04-devtools.md](../../../../05-kotlin-compose/frameworks/04-devtools.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/projects/01-notes-app.md](../../../../05-kotlin-compose/projects/01-notes-app.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/projects/02-weather-app.md](../../../../05-kotlin-compose/projects/02-weather-app.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/projects/03-news-reader.md](../../../../05-kotlin-compose/projects/03-news-reader.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/projects/04-production-android-app.md](../../../../05-kotlin-compose/projects/04-production-android-app.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/framework-essentials/01-compose-essentials.md](../../../../05-kotlin-compose/reference/framework-essentials/01-compose-essentials.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/framework-essentials/02-compose-material3.md](../../../../05-kotlin-compose/reference/framework-essentials/02-compose-material3.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/framework-essentials/03-side-effects.md](../../../../05-kotlin-compose/reference/framework-essentials/03-side-effects.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/framework-essentials/04-recomposition.md](../../../../05-kotlin-compose/reference/framework-essentials/04-recomposition.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/framework-essentials/05-animation-core.md](../../../../05-kotlin-compose/reference/framework-essentials/05-animation-core.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/framework-essentials/06-navigation-components.md](../../../../05-kotlin-compose/reference/framework-essentials/06-navigation-components.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/framework-essentials/07-compose-testing.md](../../../../05-kotlin-compose/reference/framework-essentials/07-compose-testing.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/framework-essentials/08-composition-model.md](../../../../05-kotlin-compose/reference/framework-essentials/08-composition-model.md) | `not_verified` | 0 | 1 |
| Kotlin / Compose | [05-kotlin-compose/reference/framework-essentials/09-gestures.md](../../../../05-kotlin-compose/reference/framework-essentials/09-gestures.md) | `not_verified` | 0 | 1 |
| Kotlin / Compose | [05-kotlin-compose/reference/framework-essentials/10-canvas-drawing.md](../../../../05-kotlin-compose/reference/framework-essentials/10-canvas-drawing.md) | `not_verified` | 0 | 1 |
| Kotlin / Compose | [05-kotlin-compose/reference/language-concepts/01-kotlin-keywords.md](../../../../05-kotlin-compose/reference/language-concepts/01-kotlin-keywords.md) | `not_verified` | 0 | 3 |
| Kotlin / Compose | [05-kotlin-compose/reference/language-concepts/02-null-safety-collections.md](../../../../05-kotlin-compose/reference/language-concepts/02-null-safety-collections.md) | `runtime` | 1 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/language-concepts/03-coroutines-flow-api.md](../../../../05-kotlin-compose/reference/language-concepts/03-coroutines-flow-api.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/language-concepts/04-compose-state-api.md](../../../../05-kotlin-compose/reference/language-concepts/04-compose-state-api.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/language-concepts/05-generics-delegates.md](../../../../05-kotlin-compose/reference/language-concepts/05-generics-delegates.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/language-concepts/06-extension-functions.md](../../../../05-kotlin-compose/reference/language-concepts/06-extension-functions.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/language-concepts/07-scope-functions.md](../../../../05-kotlin-compose/reference/language-concepts/07-scope-functions.md) | `runtime` | 2 | 1 |
| Kotlin / Compose | [05-kotlin-compose/reference/language-concepts/08-lambdas-higher-order.md](../../../../05-kotlin-compose/reference/language-concepts/08-lambdas-higher-order.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/language-concepts/09-collections-operations.md](../../../../05-kotlin-compose/reference/language-concepts/09-collections-operations.md) | `runtime` | 1 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/language-concepts/10-sequences.md](../../../../05-kotlin-compose/reference/language-concepts/10-sequences.md) | `runtime` | 2 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/language-concepts/11-text-and-regex.md](../../../../05-kotlin-compose/reference/language-concepts/11-text-and-regex.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/library-guides/01-androidx-libraries.md](../../../../05-kotlin-compose/reference/library-guides/01-androidx-libraries.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/library-guides/02-third-party-libs.md](../../../../05-kotlin-compose/reference/library-guides/02-third-party-libs.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/library-guides/03-ksp-configuration.md](../../../../05-kotlin-compose/reference/library-guides/03-ksp-configuration.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/quick-references/01-kotlin-compose-cheatsheet.md](../../../../05-kotlin-compose/reference/quick-references/01-kotlin-compose-cheatsheet.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/reference/quick-references/02-troubleshooting.md](../../../../05-kotlin-compose/reference/quick-references/02-troubleshooting.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/testing/01-unit-testing.md](../../../../05-kotlin-compose/testing/01-unit-testing.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/testing/02-ui-testing.md](../../../../05-kotlin-compose/testing/02-ui-testing.md) | `not_verified` | 0 | 0 |
| Kotlin / Compose | [05-kotlin-compose/testing/03-integration-e2e-testing.md](../../../../05-kotlin-compose/testing/03-integration-e2e-testing.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/LEARNING_GUIDE.md](../../../../06-swift-swiftui/LEARNING_GUIDE.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/README.md](../../../../06-swift-swiftui/README.md) | `not_verified` | 0 | 1 |
| Swift / SwiftUI | [06-swift-swiftui/advanced-topics/architecture/01-app-architecture.md](../../../../06-swift-swiftui/advanced-topics/architecture/01-app-architecture.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/advanced-topics/performance/01-rendering-performance.md](../../../../06-swift-swiftui/advanced-topics/performance/01-rendering-performance.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/advanced-topics/performance/02-concurrency-optimization.md](../../../../06-swift-swiftui/advanced-topics/performance/02-concurrency-optimization.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/advanced-topics/security/01-security-practices.md](../../../../06-swift-swiftui/advanced-topics/security/01-security-practices.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/basics/01-environment-setup.md](../../../../06-swift-swiftui/basics/01-environment-setup.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/basics/02-first-swiftui-app.md](../../../../06-swift-swiftui/basics/02-first-swiftui-app.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/basics/03-swift-syntax-essentials.md](../../../../06-swift-swiftui/basics/03-swift-syntax-essentials.md) | `runtime` | 1 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/basics/04-views-state.md](../../../../06-swift-swiftui/basics/04-views-state.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/basics/05-layouts.md](../../../../06-swift-swiftui/basics/05-layouts.md) | `not_verified` | 0 | 1 |
| Swift / SwiftUI | [06-swift-swiftui/basics/06-navigation.md](../../../../06-swift-swiftui/basics/06-navigation.md) | `not_verified` | 0 | 1 |
| Swift / SwiftUI | [06-swift-swiftui/basics/07-concurrency-async-await.md](../../../../06-swift-swiftui/basics/07-concurrency-async-await.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/basics/08-first-project.md](../../../../06-swift-swiftui/basics/08-first-project.md) | `runtime` | 1 | 1 |
| Swift / SwiftUI | [06-swift-swiftui/deployment/01-app-release.md](../../../../06-swift-swiftui/deployment/01-app-release.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/deployment/02-app-store-release.md](../../../../06-swift-swiftui/deployment/02-app-store-release.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/deployment/03-ci-cd-observability.md](../../../../06-swift-swiftui/deployment/03-ci-cd-observability.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/frameworks/01-swiftui-basics.md](../../../../06-swift-swiftui/frameworks/01-swiftui-basics.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/frameworks/02-swiftui-advanced.md](../../../../06-swift-swiftui/frameworks/02-swiftui-advanced.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/frameworks/03-ecosystem-integration.md](../../../../06-swift-swiftui/frameworks/03-ecosystem-integration.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/frameworks/04-devtools.md](../../../../06-swift-swiftui/frameworks/04-devtools.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/iOS原生开发学习路线.md](../../../../06-swift-swiftui/iOS原生开发学习路线.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/projects/01-notes-app.md](../../../../06-swift-swiftui/projects/01-notes-app.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/projects/02-weather-app.md](../../../../06-swift-swiftui/projects/02-weather-app.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/projects/03-habit-tracker.md](../../../../06-swift-swiftui/projects/03-habit-tracker.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/projects/04-production-ios-app.md](../../../../06-swift-swiftui/projects/04-production-ios-app.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/framework-essentials/01-swiftui-essentials.md](../../../../06-swift-swiftui/reference/framework-essentials/01-swiftui-essentials.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/framework-essentials/02-swiftdata-observability.md](../../../../06-swift-swiftui/reference/framework-essentials/02-swiftdata-observability.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/framework-essentials/03-state-driven-views.md](../../../../06-swift-swiftui/reference/framework-essentials/03-state-driven-views.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/framework-essentials/04-view-modifier.md](../../../../06-swift-swiftui/reference/framework-essentials/04-view-modifier.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/framework-essentials/05-data-flow.md](../../../../06-swift-swiftui/reference/framework-essentials/05-data-flow.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/framework-essentials/06-swift-charts.md](../../../../06-swift-swiftui/reference/framework-essentials/06-swift-charts.md) | `not_verified` | 0 | 1 |
| Swift / SwiftUI | [06-swift-swiftui/reference/framework-essentials/07-swiftdata-migration.md](../../../../06-swift-swiftui/reference/framework-essentials/07-swiftdata-migration.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/framework-essentials/08-gestures.md](../../../../06-swift-swiftui/reference/framework-essentials/08-gestures.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/01-swift-keywords.md](../../../../06-swift-swiftui/reference/language-concepts/01-swift-keywords.md) | `runtime` | 1 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/02-optionals-collections.md](../../../../06-swift-swiftui/reference/language-concepts/02-optionals-collections.md) | `runtime` | 2 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/03-concurrency-api.md](../../../../06-swift-swiftui/reference/language-concepts/03-concurrency-api.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/04-swiftui-state-api.md](../../../../06-swift-swiftui/reference/language-concepts/04-swiftui-state-api.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/05-protocols-generics.md](../../../../06-swift-swiftui/reference/language-concepts/05-protocols-generics.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/06-closures.md](../../../../06-swift-swiftui/reference/language-concepts/06-closures.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/07-enums-pattern-matching.md](../../../../06-swift-swiftui/reference/language-concepts/07-enums-pattern-matching.md) | `runtime` | 1 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/08-error-handling.md](../../../../06-swift-swiftui/reference/language-concepts/08-error-handling.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/09-property-wrappers.md](../../../../06-swift-swiftui/reference/language-concepts/09-property-wrappers.md) | `not_verified` | 0 | 2 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/10-value-types-arc.md](../../../../06-swift-swiftui/reference/language-concepts/10-value-types-arc.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/11-actors-sendability.md](../../../../06-swift-swiftui/reference/language-concepts/11-actors-sendability.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/12-initialization.md](../../../../06-swift-swiftui/reference/language-concepts/12-initialization.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/13-keywords-completion.md](../../../../06-swift-swiftui/reference/language-concepts/13-keywords-completion.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/14-regex.md](../../../../06-swift-swiftui/reference/language-concepts/14-regex.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/15-urlsession.md](../../../../06-swift-swiftui/reference/language-concepts/15-urlsession.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/language-concepts/16-stdlib-foundation-map.md](../../../../06-swift-swiftui/reference/language-concepts/16-stdlib-foundation-map.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/library-guides/01-foundation-and-stdlib.md](../../../../06-swift-swiftui/reference/library-guides/01-foundation-and-stdlib.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/library-guides/02-third-party-libs.md](../../../../06-swift-swiftui/reference/library-guides/02-third-party-libs.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/quick-references/01-swift-swiftui-cheatsheet.md](../../../../06-swift-swiftui/reference/quick-references/01-swift-swiftui-cheatsheet.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/reference/quick-references/02-troubleshooting.md](../../../../06-swift-swiftui/reference/quick-references/02-troubleshooting.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/testing/01-unit-testing.md](../../../../06-swift-swiftui/testing/01-unit-testing.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/testing/02-ui-testing.md](../../../../06-swift-swiftui/testing/02-ui-testing.md) | `not_verified` | 0 | 0 |
| Swift / SwiftUI | [06-swift-swiftui/testing/03-integration-testing.md](../../../../06-swift-swiftui/testing/03-integration-testing.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/LEARNING_GUIDE.md](../../../../07-php-mastery/LEARNING_GUIDE.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/README.md](../../../../07-php-mastery/README.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/advanced-topics/architecture/01-laravel-architecture.md](../../../../07-php-mastery/advanced-topics/architecture/01-laravel-architecture.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/advanced-topics/performance/01-query-optimization.md](../../../../07-php-mastery/advanced-topics/performance/01-query-optimization.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/advanced-topics/performance/02-caching-queues.md](../../../../07-php-mastery/advanced-topics/performance/02-caching-queues.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/advanced-topics/runtime/01-fpm-vs-resident.md](../../../../07-php-mastery/advanced-topics/runtime/01-fpm-vs-resident.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/advanced-topics/runtime/02-workerman-principles.md](../../../../07-php-mastery/advanced-topics/runtime/02-workerman-principles.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/advanced-topics/runtime/03-webman-practice.md](../../../../07-php-mastery/advanced-topics/runtime/03-webman-practice.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/advanced-topics/runtime/04-swoole-ecosystem.md](../../../../07-php-mastery/advanced-topics/runtime/04-swoole-ecosystem.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/advanced-topics/security/01-security-practices.md](../../../../07-php-mastery/advanced-topics/security/01-security-practices.md) | `runtime` | 1 | 2 |
| PHP | [07-php-mastery/basics/01-environment-setup.md](../../../../07-php-mastery/basics/01-environment-setup.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/basics/02-first-script.md](../../../../07-php-mastery/basics/02-first-script.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/basics/03-variables-types.md](../../../../07-php-mastery/basics/03-variables-types.md) | `runtime` | 2 | 0 |
| PHP | [07-php-mastery/basics/04-functions-oop.md](../../../../07-php-mastery/basics/04-functions-oop.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/basics/05-control-flow.md](../../../../07-php-mastery/basics/05-control-flow.md) | `runtime` | 1 | 0 |
| PHP | [07-php-mastery/basics/06-error-exceptions.md](../../../../07-php-mastery/basics/06-error-exceptions.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/basics/07-advanced-features.md](../../../../07-php-mastery/basics/07-advanced-features.md) | `runtime` | 3 | 0 |
| PHP | [07-php-mastery/basics/08-first-project.md](../../../../07-php-mastery/basics/08-first-project.md) | `runtime` | 1 | 0 |
| PHP | [07-php-mastery/deployment/01-docker-deployment.md](../../../../07-php-mastery/deployment/01-docker-deployment.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/deployment/02-server-deployment.md](../../../../07-php-mastery/deployment/02-server-deployment.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/deployment/03-ci-cd-observability.md](../../../../07-php-mastery/deployment/03-ci-cd-observability.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/frameworks/01-laravel-basics.md](../../../../07-php-mastery/frameworks/01-laravel-basics.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/frameworks/02-laravel-advanced.md](../../../../07-php-mastery/frameworks/02-laravel-advanced.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/frameworks/03-ecosystem-integration.md](../../../../07-php-mastery/frameworks/03-ecosystem-integration.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/frameworks/04-devtools.md](../../../../07-php-mastery/frameworks/04-devtools.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/projects/01-todo-api.md](../../../../07-php-mastery/projects/01-todo-api.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/projects/02-blog-platform.md](../../../../07-php-mastery/projects/02-blog-platform.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/projects/03-ecommerce-api.md](../../../../07-php-mastery/projects/03-ecommerce-api.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/projects/04-production-laravel-app.md](../../../../07-php-mastery/projects/04-production-laravel-app.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/framework-essentials/01-laravel-essentials.md](../../../../07-php-mastery/reference/framework-essentials/01-laravel-essentials.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/framework-essentials/02-symfony-essentials.md](../../../../07-php-mastery/reference/framework-essentials/02-symfony-essentials.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/01-php-keywords.md](../../../../07-php-mastery/reference/language-concepts/01-php-keywords.md) | `runtime` | 7 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/02-built-in-functions.md](../../../../07-php-mastery/reference/language-concepts/02-built-in-functions.md) | `runtime` | 11 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/03-types-oop-modern.md](../../../../07-php-mastery/reference/language-concepts/03-types-oop-modern.md) | `runtime` | 1 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/04-control-flow.md](../../../../07-php-mastery/reference/language-concepts/04-control-flow.md) | `runtime` | 1 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/05-arrays-patterns.md](../../../../07-php-mastery/reference/language-concepts/05-arrays-patterns.md) | `runtime` | 3 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/06-generators-iterators.md](../../../../07-php-mastery/reference/language-concepts/06-generators-iterators.md) | `runtime` | 3 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/07-namespaces-autoloading.md](../../../../07-php-mastery/reference/language-concepts/07-namespaces-autoloading.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/08-reflection-attributes.md](../../../../07-php-mastery/reference/language-concepts/08-reflection-attributes.md) | `runtime` | 1 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/09-strings-regex.md](../../../../07-php-mastery/reference/language-concepts/09-strings-regex.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/10-datetime.md](../../../../07-php-mastery/reference/language-concepts/10-datetime.md) | `runtime` | 1 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/11-errors-exceptions.md](../../../../07-php-mastery/reference/language-concepts/11-errors-exceptions.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/12-modern-php-85.md](../../../../07-php-mastery/reference/language-concepts/12-modern-php-85.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/13-weak-comparison.md](../../../../07-php-mastery/reference/language-concepts/13-weak-comparison.md) | `runtime` | 1 | 1 |
| PHP | [07-php-mastery/reference/language-concepts/14-references-value-semantics.md](../../../../07-php-mastery/reference/language-concepts/14-references-value-semantics.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/15-superglobals.md](../../../../07-php-mastery/reference/language-concepts/15-superglobals.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/16-operators.md](../../../../07-php-mastery/reference/language-concepts/16-operators.md) | `runtime` | 1 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/17-magic-methods.md](../../../../07-php-mastery/reference/language-concepts/17-magic-methods.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/language-concepts/18-constants-magic-constants.md](../../../../07-php-mastery/reference/language-concepts/18-constants-magic-constants.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/library-guides/01-standard-library-spl.md](../../../../07-php-mastery/reference/library-guides/01-standard-library-spl.md) | `runtime` | 1 | 0 |
| PHP | [07-php-mastery/reference/library-guides/02-composer-ecosystem.md](../../../../07-php-mastery/reference/library-guides/02-composer-ecosystem.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/library-guides/03-pdo.md](../../../../07-php-mastery/reference/library-guides/03-pdo.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/library-guides/04-json.md](../../../../07-php-mastery/reference/library-guides/04-json.md) | `runtime` | 1 | 0 |
| PHP | [07-php-mastery/reference/library-guides/05-file-stream-io.md](../../../../07-php-mastery/reference/library-guides/05-file-stream-io.md) | `runtime` | 1 | 0 |
| PHP | [07-php-mastery/reference/library-guides/06-http-session-cookie.md](../../../../07-php-mastery/reference/library-guides/06-http-session-cookie.md) | `runtime` | 1 | 0 |
| PHP | [07-php-mastery/reference/library-guides/07-extension-map.md](../../../../07-php-mastery/reference/library-guides/07-extension-map.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/quick-references/01-php-cheatsheet.md](../../../../07-php-mastery/reference/quick-references/01-php-cheatsheet.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/reference/quick-references/02-troubleshooting.md](../../../../07-php-mastery/reference/quick-references/02-troubleshooting.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/testing/01-unit-testing.md](../../../../07-php-mastery/testing/01-unit-testing.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/testing/02-pest-testing.md](../../../../07-php-mastery/testing/02-pest-testing.md) | `not_verified` | 0 | 0 |
| PHP | [07-php-mastery/testing/03-feature-testing.md](../../../../07-php-mastery/testing/03-feature-testing.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/LEARNING_GUIDE.md](../../../../08-java-revisited/LEARNING_GUIDE.md) | `not_verified` | 0 | 1 |
| Java | [08-java-revisited/README.md](../../../../08-java-revisited/README.md) | `not_verified` | 0 | 1 |
| Java | [08-java-revisited/advanced-topics/architecture/01-layered-architecture.md](../../../../08-java-revisited/advanced-topics/architecture/01-layered-architecture.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/advanced-topics/performance/01-jvm-tuning.md](../../../../08-java-revisited/advanced-topics/performance/01-jvm-tuning.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/advanced-topics/performance/02-virtual-threads.md](../../../../08-java-revisited/advanced-topics/performance/02-virtual-threads.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/advanced-topics/security/01-security-practices.md](../../../../08-java-revisited/advanced-topics/security/01-security-practices.md) | `not_verified` | 0 | 1 |
| Java | [08-java-revisited/basics/01-environment-setup.md](../../../../08-java-revisited/basics/01-environment-setup.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/basics/02-first-program.md](../../../../08-java-revisited/basics/02-first-program.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/basics/03-variables-types.md](../../../../08-java-revisited/basics/03-variables-types.md) | `runtime` | 2 | 0 |
| Java | [08-java-revisited/basics/04-classes-records.md](../../../../08-java-revisited/basics/04-classes-records.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/basics/05-control-flow.md](../../../../08-java-revisited/basics/05-control-flow.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/basics/06-exceptions.md](../../../../08-java-revisited/basics/06-exceptions.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/basics/07-modern-features.md](../../../../08-java-revisited/basics/07-modern-features.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/basics/08-first-project.md](../../../../08-java-revisited/basics/08-first-project.md) | `runtime` | 1 | 2 |
| Java | [08-java-revisited/deployment/01-docker-deployment.md](../../../../08-java-revisited/deployment/01-docker-deployment.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/deployment/02-kubernetes-deployment.md](../../../../08-java-revisited/deployment/02-kubernetes-deployment.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/deployment/03-ci-cd-observability.md](../../../../08-java-revisited/deployment/03-ci-cd-observability.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/frameworks/01-spring-boot-basics.md](../../../../08-java-revisited/frameworks/01-spring-boot-basics.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/frameworks/02-spring-boot-advanced.md](../../../../08-java-revisited/frameworks/02-spring-boot-advanced.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/frameworks/03-ecosystem-integration.md](../../../../08-java-revisited/frameworks/03-ecosystem-integration.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/frameworks/04-devtools.md](../../../../08-java-revisited/frameworks/04-devtools.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/projects/01-todo-api.md](../../../../08-java-revisited/projects/01-todo-api.md) | `not_verified` | 0 | 1 |
| Java | [08-java-revisited/projects/02-library-management.md](../../../../08-java-revisited/projects/02-library-management.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/projects/03-order-system.md](../../../../08-java-revisited/projects/03-order-system.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/projects/04-production-spring-app.md](../../../../08-java-revisited/projects/04-production-spring-app.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/framework-essentials/01-spring-boot-essentials.md](../../../../08-java-revisited/reference/framework-essentials/01-spring-boot-essentials.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/framework-essentials/02-jpa-essentials.md](../../../../08-java-revisited/reference/framework-essentials/02-jpa-essentials.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/framework-essentials/03-ioc-di-essentials.md](../../../../08-java-revisited/reference/framework-essentials/03-ioc-di-essentials.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/framework-essentials/04-aop-essentials.md](../../../../08-java-revisited/reference/framework-essentials/04-aop-essentials.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/framework-essentials/05-transaction-essentials.md](../../../../08-java-revisited/reference/framework-essentials/05-transaction-essentials.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/framework-essentials/06-spring-security-essentials.md](../../../../08-java-revisited/reference/framework-essentials/06-spring-security-essentials.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/framework-essentials/07-rest-client-essentials.md](../../../../08-java-revisited/reference/framework-essentials/07-rest-client-essentials.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/language-concepts/01-java-keywords.md](../../../../08-java-revisited/reference/language-concepts/01-java-keywords.md) | `runtime` | 9 | 1 |
| Java | [08-java-revisited/reference/language-concepts/02-collections-generics.md](../../../../08-java-revisited/reference/language-concepts/02-collections-generics.md) | `runtime` | 3 | 0 |
| Java | [08-java-revisited/reference/language-concepts/03-streams-optional.md](../../../../08-java-revisited/reference/language-concepts/03-streams-optional.md) | `runtime` | 3 | 0 |
| Java | [08-java-revisited/reference/language-concepts/04-concurrency-api.md](../../../../08-java-revisited/reference/language-concepts/04-concurrency-api.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/reference/language-concepts/05-records-sealed-patterns.md](../../../../08-java-revisited/reference/language-concepts/05-records-sealed-patterns.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/reference/language-concepts/06-exceptions-resources.md](../../../../08-java-revisited/reference/language-concepts/06-exceptions-resources.md) | `runtime` | 2 | 0 |
| Java | [08-java-revisited/reference/language-concepts/07-string-immutability-pool.md](../../../../08-java-revisited/reference/language-concepts/07-string-immutability-pool.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/reference/language-concepts/08-enums.md](../../../../08-java-revisited/reference/language-concepts/08-enums.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/language-concepts/09-annotations.md](../../../../08-java-revisited/reference/language-concepts/09-annotations.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/language-concepts/10-interface-semantics.md](../../../../08-java-revisited/reference/language-concepts/10-interface-semantics.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/library-guides/01-standard-library.md](../../../../08-java-revisited/reference/library-guides/01-standard-library.md) | `runtime` | 11 | 1 |
| Java | [08-java-revisited/reference/library-guides/02-third-party-libs.md](../../../../08-java-revisited/reference/library-guides/02-third-party-libs.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/library-guides/03-java-lang.md](../../../../08-java-revisited/reference/library-guides/03-java-lang.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/reference/library-guides/04-java-io.md](../../../../08-java-revisited/reference/library-guides/04-java-io.md) | `runtime` | 3 | 0 |
| Java | [08-java-revisited/reference/library-guides/05-java-util-function.md](../../../../08-java-revisited/reference/library-guides/05-java-util-function.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/reference/library-guides/06-java-math.md](../../../../08-java-revisited/reference/library-guides/06-java-math.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/reference/library-guides/07-java-text-and-time-format.md](../../../../08-java-revisited/reference/library-guides/07-java-text-and-time-format.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/reference/library-guides/08-java-util-regex.md](../../../../08-java-revisited/reference/library-guides/08-java-util-regex.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/reference/library-guides/09-jdk-package-map.md](../../../../08-java-revisited/reference/library-guides/09-jdk-package-map.md) | `runtime` | 1 | 0 |
| Java | [08-java-revisited/reference/quick-references/01-java-cheatsheet.md](../../../../08-java-revisited/reference/quick-references/01-java-cheatsheet.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/quick-references/02-troubleshooting.md](../../../../08-java-revisited/reference/quick-references/02-troubleshooting.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/reference/quick-references/03-spring-boot4-migration.md](../../../../08-java-revisited/reference/quick-references/03-spring-boot4-migration.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/testing/01-unit-testing.md](../../../../08-java-revisited/testing/01-unit-testing.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/testing/02-integration-testing.md](../../../../08-java-revisited/testing/02-integration-testing.md) | `not_verified` | 0 | 0 |
| Java | [08-java-revisited/testing/03-api-testing.md](../../../../08-java-revisited/testing/03-api-testing.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/LEARNING_GUIDE.md](../../../../09-nodejs-backend/LEARNING_GUIDE.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/README.md](../../../../09-nodejs-backend/README.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/advanced-topics/architecture/01-service-architecture.md](../../../../09-nodejs-backend/advanced-topics/architecture/01-service-architecture.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/advanced-topics/performance/01-event-loop.md](../../../../09-nodejs-backend/advanced-topics/performance/01-event-loop.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/advanced-topics/performance/02-streaming-clustering.md](../../../../09-nodejs-backend/advanced-topics/performance/02-streaming-clustering.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/advanced-topics/security/01-security-practices.md](../../../../09-nodejs-backend/advanced-topics/security/01-security-practices.md) | `runtime` | 1 | 3 |
| Node.js | [09-nodejs-backend/basics/01-environment-setup.md](../../../../09-nodejs-backend/basics/01-environment-setup.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/basics/02-first-server.md](../../../../09-nodejs-backend/basics/02-first-server.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/basics/03-modules-esm.md](../../../../09-nodejs-backend/basics/03-modules-esm.md) | `runtime` | 1 | 0 |
| Node.js | [09-nodejs-backend/basics/04-async-promises.md](../../../../09-nodejs-backend/basics/04-async-promises.md) | `runtime` | 2 | 0 |
| Node.js | [09-nodejs-backend/basics/05-http-routing.md](../../../../09-nodejs-backend/basics/05-http-routing.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/basics/06-error-handling.md](../../../../09-nodejs-backend/basics/06-error-handling.md) | `runtime` | 1 | 0 |
| Node.js | [09-nodejs-backend/basics/07-streams-workers.md](../../../../09-nodejs-backend/basics/07-streams-workers.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/basics/08-first-project.md](../../../../09-nodejs-backend/basics/08-first-project.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/deployment/01-docker-deployment.md](../../../../09-nodejs-backend/deployment/01-docker-deployment.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/deployment/02-ci-cd-pipelines.md](../../../../09-nodejs-backend/deployment/02-ci-cd-pipelines.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/deployment/03-observability.md](../../../../09-nodejs-backend/deployment/03-observability.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/frameworks/01-hono-basics.md](../../../../09-nodejs-backend/frameworks/01-hono-basics.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/frameworks/02-hono-advanced.md](../../../../09-nodejs-backend/frameworks/02-hono-advanced.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/frameworks/03-ecosystem-integration.md](../../../../09-nodejs-backend/frameworks/03-ecosystem-integration.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/frameworks/04-devtools.md](../../../../09-nodejs-backend/frameworks/04-devtools.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/projects/01-todo-api.md](../../../../09-nodejs-backend/projects/01-todo-api.md) | `not_verified` | 0 | 2 |
| Node.js | [09-nodejs-backend/projects/02-auth-service.md](../../../../09-nodejs-backend/projects/02-auth-service.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/projects/03-file-storage-service.md](../../../../09-nodejs-backend/projects/03-file-storage-service.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/projects/04-production-nodejs-api.md](../../../../09-nodejs-backend/projects/04-production-nodejs-api.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/reference/framework-essentials/01-hono-essentials.md](../../../../09-nodejs-backend/reference/framework-essentials/01-hono-essentials.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/reference/framework-essentials/02-fastify-nestjs.md](../../../../09-nodejs-backend/reference/framework-essentials/02-fastify-nestjs.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/reference/language-concepts/01-js-modern-syntax.md](../../../../09-nodejs-backend/reference/language-concepts/01-js-modern-syntax.md) | `runtime` | 2 | 0 |
| Node.js | [09-nodejs-backend/reference/language-concepts/02-async-api.md](../../../../09-nodejs-backend/reference/language-concepts/02-async-api.md) | `runtime` | 1 | 0 |
| Node.js | [09-nodejs-backend/reference/language-concepts/03-node-core-api.md](../../../../09-nodejs-backend/reference/language-concepts/03-node-core-api.md) | `runtime` | 2 | 0 |
| Node.js | [09-nodejs-backend/reference/language-concepts/04-streams-api.md](../../../../09-nodejs-backend/reference/language-concepts/04-streams-api.md) | `runtime` | 1 | 0 |
| Node.js | [09-nodejs-backend/reference/language-concepts/05-typescript-patterns.md](../../../../09-nodejs-backend/reference/language-concepts/05-typescript-patterns.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/reference/language-concepts/06-esm-module-resolution.md](../../../../09-nodejs-backend/reference/language-concepts/06-esm-module-resolution.md) | `runtime` | 1 | 1 |
| Node.js | [09-nodejs-backend/reference/language-concepts/07-js-core-semantics.md](../../../../09-nodejs-backend/reference/language-concepts/07-js-core-semantics.md) | `runtime` | 2 | 1 |
| Node.js | [09-nodejs-backend/reference/language-concepts/08-type-coercion-collections.md](../../../../09-nodejs-backend/reference/language-concepts/08-type-coercion-collections.md) | `runtime` | 2 | 5 |
| Node.js | [09-nodejs-backend/reference/language-concepts/09-globals-reference.md](../../../../09-nodejs-backend/reference/language-concepts/09-globals-reference.md) | `runtime` | 1 | 0 |
| Node.js | [09-nodejs-backend/reference/library-guides/01-core-modules.md](../../../../09-nodejs-backend/reference/library-guides/01-core-modules.md) | `runtime` | 2 | 0 |
| Node.js | [09-nodejs-backend/reference/library-guides/02-ecosystem-libs.md](../../../../09-nodejs-backend/reference/library-guides/02-ecosystem-libs.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/reference/library-guides/03-crypto.md](../../../../09-nodejs-backend/reference/library-guides/03-crypto.md) | `runtime` | 1 | 0 |
| Node.js | [09-nodejs-backend/reference/library-guides/04-child-process.md](../../../../09-nodejs-backend/reference/library-guides/04-child-process.md) | `runtime` | 3 | 1 |
| Node.js | [09-nodejs-backend/reference/library-guides/05-buffer.md](../../../../09-nodejs-backend/reference/library-guides/05-buffer.md) | `runtime` | 2 | 3 |
| Node.js | [09-nodejs-backend/reference/library-guides/06-util.md](../../../../09-nodejs-backend/reference/library-guides/06-util.md) | `runtime` | 1 | 0 |
| Node.js | [09-nodejs-backend/reference/library-guides/07-process-lifecycle.md](../../../../09-nodejs-backend/reference/library-guides/07-process-lifecycle.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/reference/library-guides/08-test-runner.md](../../../../09-nodejs-backend/reference/library-guides/08-test-runner.md) | `runtime` | 2 | 6 |
| Node.js | [09-nodejs-backend/reference/library-guides/09-zlib.md](../../../../09-nodejs-backend/reference/library-guides/09-zlib.md) | `runtime` | 2 | 0 |
| Node.js | [09-nodejs-backend/reference/quick-references/01-node-cheatsheet.md](../../../../09-nodejs-backend/reference/quick-references/01-node-cheatsheet.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/reference/quick-references/02-troubleshooting.md](../../../../09-nodejs-backend/reference/quick-references/02-troubleshooting.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/testing/01-unit-testing.md](../../../../09-nodejs-backend/testing/01-unit-testing.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/testing/02-integration-testing.md](../../../../09-nodejs-backend/testing/02-integration-testing.md) | `not_verified` | 0 | 0 |
| Node.js | [09-nodejs-backend/testing/03-e2e-api-testing.md](../../../../09-nodejs-backend/testing/03-e2e-api-testing.md) | `not_verified` | 0 | 1 |
| Python | [10-python-discovery/LEARNING_GUIDE.md](../../../../10-python-discovery/LEARNING_GUIDE.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/README.md](../../../../10-python-discovery/README.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/advanced-topics/architecture/01-project-architecture.md](../../../../10-python-discovery/advanced-topics/architecture/01-project-architecture.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/advanced-topics/performance/01-async-python.md](../../../../10-python-discovery/advanced-topics/performance/01-async-python.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/advanced-topics/performance/02-profiling-optimization.md](../../../../10-python-discovery/advanced-topics/performance/02-profiling-optimization.md) | `not_verified` | 0 | 1 |
| Python | [10-python-discovery/advanced-topics/security/01-security-practices.md](../../../../10-python-discovery/advanced-topics/security/01-security-practices.md) | `runtime` | 1 | 1 |
| Python | [10-python-discovery/basics/01-environment-setup.md](../../../../10-python-discovery/basics/01-environment-setup.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/basics/02-first-script.md](../../../../10-python-discovery/basics/02-first-script.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/basics/03-variables-types.md](../../../../10-python-discovery/basics/03-variables-types.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/basics/04-functions-oop.md](../../../../10-python-discovery/basics/04-functions-oop.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/basics/05-control-flow.md](../../../../10-python-discovery/basics/05-control-flow.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/basics/06-exceptions.md](../../../../10-python-discovery/basics/06-exceptions.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/basics/07-advanced-features.md](../../../../10-python-discovery/basics/07-advanced-features.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/basics/08-first-project.md](../../../../10-python-discovery/basics/08-first-project.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/deployment/01-docker-deployment.md](../../../../10-python-discovery/deployment/01-docker-deployment.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/deployment/02-ci-cd-pipelines.md](../../../../10-python-discovery/deployment/02-ci-cd-pipelines.md) | `not_verified` | 0 | 2 |
| Python | [10-python-discovery/deployment/03-observability.md](../../../../10-python-discovery/deployment/03-observability.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/frameworks/01-fastapi-basics.md](../../../../10-python-discovery/frameworks/01-fastapi-basics.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/frameworks/02-fastapi-advanced.md](../../../../10-python-discovery/frameworks/02-fastapi-advanced.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/frameworks/03-ecosystem-integration.md](../../../../10-python-discovery/frameworks/03-ecosystem-integration.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/frameworks/04-devtools.md](../../../../10-python-discovery/frameworks/04-devtools.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/projects/01-todo-api.md](../../../../10-python-discovery/projects/01-todo-api.md) | `not_verified` | 0 | 2 |
| Python | [10-python-discovery/projects/02-url-shortener.md](../../../../10-python-discovery/projects/02-url-shortener.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/projects/03-data-pipeline.md](../../../../10-python-discovery/projects/03-data-pipeline.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/projects/04-production-fastapi-app.md](../../../../10-python-discovery/projects/04-production-fastapi-app.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/reference/framework-essentials/01-fastapi-essentials.md](../../../../10-python-discovery/reference/framework-essentials/01-fastapi-essentials.md) | `runtime` | 1 | 1 |
| Python | [10-python-discovery/reference/framework-essentials/02-django-flask.md](../../../../10-python-discovery/reference/framework-essentials/02-django-flask.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/reference/framework-essentials/03-uv-package-manager.md](../../../../10-python-discovery/reference/framework-essentials/03-uv-package-manager.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/reference/language-concepts/01-python-keywords.md](../../../../10-python-discovery/reference/language-concepts/01-python-keywords.md) | `runtime` | 2 | 0 |
| Python | [10-python-discovery/reference/language-concepts/02-built-in-functions.md](../../../../10-python-discovery/reference/language-concepts/02-built-in-functions.md) | `runtime` | 2 | 4 |
| Python | [10-python-discovery/reference/language-concepts/03-data-structures.md](../../../../10-python-discovery/reference/language-concepts/03-data-structures.md) | `runtime` | 1 | 3 |
| Python | [10-python-discovery/reference/language-concepts/04-oop-protocols.md](../../../../10-python-discovery/reference/language-concepts/04-oop-protocols.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/reference/language-concepts/05-typing-annotations.md](../../../../10-python-discovery/reference/language-concepts/05-typing-annotations.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/reference/language-concepts/06-decorators.md](../../../../10-python-discovery/reference/language-concepts/06-decorators.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/reference/language-concepts/07-generators-iterators.md](../../../../10-python-discovery/reference/language-concepts/07-generators-iterators.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/reference/language-concepts/08-context-managers.md](../../../../10-python-discovery/reference/language-concepts/08-context-managers.md) | `runtime` | 2 | 1 |
| Python | [10-python-discovery/reference/language-concepts/09-asyncio-concurrency.md](../../../../10-python-discovery/reference/language-concepts/09-asyncio-concurrency.md) | `runtime` | 1 | 7 |
| Python | [10-python-discovery/reference/language-concepts/10-exceptions-system.md](../../../../10-python-discovery/reference/language-concepts/10-exceptions-system.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/reference/language-concepts/11-modules-imports.md](../../../../10-python-discovery/reference/language-concepts/11-modules-imports.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/reference/language-concepts/12-string-formatting.md](../../../../10-python-discovery/reference/language-concepts/12-string-formatting.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/reference/language-concepts/13-dataclasses.md](../../../../10-python-discovery/reference/language-concepts/13-dataclasses.md) | `runtime` | 1 | 1 |
| Python | [10-python-discovery/reference/language-concepts/14-comprehensions.md](../../../../10-python-discovery/reference/language-concepts/14-comprehensions.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/reference/language-concepts/15-closures-and-scope.md](../../../../10-python-discovery/reference/language-concepts/15-closures-and-scope.md) | `runtime` | 1 | 2 |
| Python | [10-python-discovery/reference/language-concepts/16-classes-and-inheritance.md](../../../../10-python-discovery/reference/language-concepts/16-classes-and-inheritance.md) | `runtime` | 1 | 0 |
| Python | [10-python-discovery/reference/language-concepts/17-functions-parameters.md](../../../../10-python-discovery/reference/language-concepts/17-functions-parameters.md) | `runtime` | 1 | 9 |
| Python | [10-python-discovery/reference/library-guides/01-standard-library.md](../../../../10-python-discovery/reference/library-guides/01-standard-library.md) | `runtime` | 2 | 0 |
| Python | [10-python-discovery/reference/library-guides/02-ecosystem-libs.md](../../../../10-python-discovery/reference/library-guides/02-ecosystem-libs.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/reference/library-guides/03-pytest-testing.md](../../../../10-python-discovery/reference/library-guides/03-pytest-testing.md) | `runtime` | 1 | 1 |
| Python | [10-python-discovery/reference/library-guides/04-os-sys.md](../../../../10-python-discovery/reference/library-guides/04-os-sys.md) | `runtime` | 2 | 5 |
| Python | [10-python-discovery/reference/library-guides/05-enum-module.md](../../../../10-python-discovery/reference/library-guides/05-enum-module.md) | `runtime` | 3 | 0 |
| Python | [10-python-discovery/reference/library-guides/06-functools-subprocess.md](../../../../10-python-discovery/reference/library-guides/06-functools-subprocess.md) | `runtime` | 4 | 0 |
| Python | [10-python-discovery/reference/quick-references/01-python-cheatsheet.md](../../../../10-python-discovery/reference/quick-references/01-python-cheatsheet.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/reference/quick-references/02-troubleshooting.md](../../../../10-python-discovery/reference/quick-references/02-troubleshooting.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/testing/01-unit-testing.md](../../../../10-python-discovery/testing/01-unit-testing.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/testing/02-integration-testing.md](../../../../10-python-discovery/testing/02-integration-testing.md) | `not_verified` | 0 | 0 |
| Python | [10-python-discovery/testing/03-mocking-testing.md](../../../../10-python-discovery/testing/03-mocking-testing.md) | `not_verified` | 0 | 1 |
| Rust / Cross-platform | [11-rust-cross-platform/LEARNING_GUIDE.md](../../../../11-rust-cross-platform/LEARNING_GUIDE.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/README.md](../../../../11-rust-cross-platform/README.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/advanced-topics/01-memory-layout-performance.md](../../../../11-rust-cross-platform/advanced-topics/01-memory-layout-performance.md) | `not_verified` | 0 | 1 |
| Rust / Cross-platform | [11-rust-cross-platform/advanced-topics/02-ffi-bindgen.md](../../../../11-rust-cross-platform/advanced-topics/02-ffi-bindgen.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/advanced-topics/03-wasm32-target.md](../../../../11-rust-cross-platform/advanced-topics/03-wasm32-target.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/advanced-topics/04-security-practices.md](../../../../11-rust-cross-platform/advanced-topics/04-security-practices.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/basics/01-environment-setup.md](../../../../11-rust-cross-platform/basics/01-environment-setup.md) | `not_verified` | 0 | 1 |
| Rust / Cross-platform | [11-rust-cross-platform/basics/02-ownership-borrowing.md](../../../../11-rust-cross-platform/basics/02-ownership-borrowing.md) | `runtime` | 1 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/basics/03-structs-enums-patterns.md](../../../../11-rust-cross-platform/basics/03-structs-enums-patterns.md) | `runtime` | 1 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/basics/04-traits-generics.md](../../../../11-rust-cross-platform/basics/04-traits-generics.md) | `runtime` | 1 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/basics/05-error-handling.md](../../../../11-rust-cross-platform/basics/05-error-handling.md) | `not_verified` | 0 | 2 |
| Rust / Cross-platform | [11-rust-cross-platform/basics/06-collections-iterators.md](../../../../11-rust-cross-platform/basics/06-collections-iterators.md) | `runtime` | 1 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/basics/07-lifetimes.md](../../../../11-rust-cross-platform/basics/07-lifetimes.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/basics/08-smart-pointers.md](../../../../11-rust-cross-platform/basics/08-smart-pointers.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/basics/09-concurrency-async.md](../../../../11-rust-cross-platform/basics/09-concurrency-async.md) | `not_verified` | 0 | 1 |
| Rust / Cross-platform | [11-rust-cross-platform/basics/10-cargo-testing.md](../../../../11-rust-cross-platform/basics/10-cargo-testing.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/deployment/01-cross-compilation-targets.md](../../../../11-rust-cross-platform/deployment/01-cross-compilation-targets.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/deployment/02-github-actions-ci.md](../../../../11-rust-cross-platform/deployment/02-github-actions-ci.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/deployment/03-signing-auto-update.md](../../../../11-rust-cross-platform/deployment/03-signing-auto-update.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/deployment/04-containerized-services.md](../../../../11-rust-cross-platform/deployment/04-containerized-services.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/frameworks/01-tauri-2-architecture.md](../../../../11-rust-cross-platform/frameworks/01-tauri-2-architecture.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/frameworks/02-tauri-plugins.md](../../../../11-rust-cross-platform/frameworks/02-tauri-plugins.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/frameworks/03-tauri-frontend-react.md](../../../../11-rust-cross-platform/frameworks/03-tauri-frontend-react.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/frameworks/04-axum-web-stack.md](../../../../11-rust-cross-platform/frameworks/04-axum-web-stack.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/frameworks/05-state-and-database-sqlx.md](../../../../11-rust-cross-platform/frameworks/05-state-and-database-sqlx.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/frameworks/06-auth-middleware.md](../../../../11-rust-cross-platform/frameworks/06-auth-middleware.md) | `not_verified` | 0 | 2 |
| Rust / Cross-platform | [11-rust-cross-platform/frameworks/07-desktop-packaging.md](../../../../11-rust-cross-platform/frameworks/07-desktop-packaging.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/projects/01-cli-tool.md](../../../../11-rust-cross-platform/projects/01-cli-tool.md) | `runtime` | 1 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/projects/02-tauri-notes-app.md](../../../../11-rust-cross-platform/projects/02-tauri-notes-app.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/projects/03-axum-rest-api.md](../../../../11-rust-cross-platform/projects/03-axum-rest-api.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/projects/04-websocket-realtime.md](../../../../11-rust-cross-platform/projects/04-websocket-realtime.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/projects/05-multiplatform-release.md](../../../../11-rust-cross-platform/projects/05-multiplatform-release.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/framework-essentials/09-tauri-2-essentials.md](../../../../11-rust-cross-platform/reference/framework-essentials/09-tauri-2-essentials.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/framework-essentials/10-tauri-ipc-commands.md](../../../../11-rust-cross-platform/reference/framework-essentials/10-tauri-ipc-commands.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/framework-essentials/11-axum-essentials.md](../../../../11-rust-cross-platform/reference/framework-essentials/11-axum-essentials.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/language-concepts/01-ownership-dictionary.md](../../../../11-rust-cross-platform/reference/language-concepts/01-ownership-dictionary.md) | `runtime` | 1 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/language-concepts/02-trait-objects.md](../../../../11-rust-cross-platform/reference/language-concepts/02-trait-objects.md) | `runtime` | 1 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/language-concepts/03-const-generics.md](../../../../11-rust-cross-platform/reference/language-concepts/03-const-generics.md) | `runtime` | 1 | 1 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/language-concepts/04-advanced-lifetimes.md](../../../../11-rust-cross-platform/reference/language-concepts/04-advanced-lifetimes.md) | `runtime` | 4 | 2 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/language-concepts/05-macros.md](../../../../11-rust-cross-platform/reference/language-concepts/05-macros.md) | `runtime` | 4 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/language-concepts/06-unsafe.md](../../../../11-rust-cross-platform/reference/language-concepts/06-unsafe.md) | `not_verified` | 0 | 1 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/language-concepts/07-smart-pointers.md](../../../../11-rust-cross-platform/reference/language-concepts/07-smart-pointers.md) | `runtime` | 1 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/language-concepts/08-async-internals.md](../../../../11-rust-cross-platform/reference/language-concepts/08-async-internals.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/language-concepts/09-keywords-and-syntax.md](../../../../11-rust-cross-platform/reference/language-concepts/09-keywords-and-syntax.md) | `runtime` | 1 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/language-concepts/10-standard-types-and-methods.md](../../../../11-rust-cross-platform/reference/language-concepts/10-standard-types-and-methods.md) | `runtime` | 1 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/library-guides/12-tokio-guide.md](../../../../11-rust-cross-platform/reference/library-guides/12-tokio-guide.md) | `runtime` | 4 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/library-guides/13-serde-guide.md](../../../../11-rust-cross-platform/reference/library-guides/13-serde-guide.md) | `runtime` | 4 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/library-guides/14-error-libraries.md](../../../../11-rust-cross-platform/reference/library-guides/14-error-libraries.md) | `runtime` | 2 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/reference/library-guides/15-standard-library-map.md](../../../../11-rust-cross-platform/reference/library-guides/15-standard-library-map.md) | `runtime` | 1 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/testing/01-unit-integration-tests.md](../../../../11-rust-cross-platform/testing/01-unit-integration-tests.md) | `not_verified` | 0 | 1 |
| Rust / Cross-platform | [11-rust-cross-platform/testing/02-criterion-benchmarks.md](../../../../11-rust-cross-platform/testing/02-criterion-benchmarks.md) | `not_verified` | 0 | 0 |
| Rust / Cross-platform | [11-rust-cross-platform/testing/03-tauri-e2e-webdriver.md](../../../../11-rust-cross-platform/testing/03-tauri-e2e-webdriver.md) | `not_verified` | 0 | 0 |

## 重新生成

先刷新结构库存，再生成本台账：

```bash
python shared-resources/tools/document-quality/finalize_validation.py
python shared-resources/tools/document-quality/build_verification_coverage.py
```
