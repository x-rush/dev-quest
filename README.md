# Dev Quest：开发知识参考与渐进学习路径

这份知识库面向会基本编程、希望系统掌握新技术栈的开发者。它同时提供基础知识参考、从 0 到 1 的学习规划、高级特性解释，以及值得投入的框架与项目练习。

**查知识**：进入模块的 reference，按关键词、内置函数、标准库、框架 API 查阅。**学技术**：从模块的学习导读开始，再按 basics 的检查点推进。两种入口使用同一套知识，不要求查阅者按章节通读，也不要求学习者先背完整个字典。

## 选一个入口开始

| 模块 | 能用来做什么 | 学习入口 | 完整目录与版本 |
|---|---|---|---|
| Go | 后端 API、命令行工具与并发服务 | [Go 学习导读](01-go-backend/LEARNING_GUIDE.md) | [模块目录](01-go-backend/README.md) |
| Next.js | 具有路由、服务端渲染与交互的 Web 应用 | [Next.js 学习导读](02-nextjs-frontend/LEARNING_GUIDE.md) | [模块目录](02-nextjs-frontend/README.md) |
| TanStack | 请求缓存、数据表格、路由与表单 | [TanStack 学习导读](03-tanstack-stack/LEARNING_GUIDE.md) | [模块目录](03-tanstack-stack/README.md) |
| React Native | 复用 React 思维开发移动端，按平台适配原生能力 | [React Native 学习导读](04-multiplatform-apps/LEARNING_GUIDE.md) | [模块目录](04-multiplatform-apps/README.md) |
| Kotlin / Compose | Android 原生界面、状态与应用生命周期 | [Android 学习导读](05-kotlin-compose/LEARNING_GUIDE.md) | [模块目录](05-kotlin-compose/README.md) |
| Swift / SwiftUI | Apple 平台原生应用与数据流 | [SwiftUI 学习导读](06-swift-swiftui/LEARNING_GUIDE.md) | [模块目录](06-swift-swiftui/README.md) |
| PHP / Laravel | 服务端 Web、数据库驱动的业务应用 | [PHP 学习导读](07-php-mastery/LEARNING_GUIDE.md) | [模块目录](07-php-mastery/README.md) |
| Java / Spring | 类型化业务建模、事务与后端服务 | [Java 学习导读](08-java-revisited/LEARNING_GUIDE.md) | [模块目录](08-java-revisited/README.md) |
| Node.js / Hono | JavaScript 服务端、异步 I/O 与接口 | [Node.js 学习导读](09-nodejs-backend/LEARNING_GUIDE.md) | [模块目录](09-nodejs-backend/README.md) |
| Python / FastAPI | 自动化、数据处理与 Web API | [Python 学习导读](10-python-discovery/LEARNING_GUIDE.md) | [模块目录](10-python-discovery/README.md) |
| Rust / Tauri / Axum | 系统编程、桌面应用与后端服务 | [Rust 学习导读](11-rust-cross-platform/LEARNING_GUIDE.md) | [模块目录](11-rust-cross-platform/README.md) |

模块编号用于归档，不表示必须从 Go 一直学到 Rust。可以先用熟悉的语言完成一个小产品，再根据需要进入另一个模块。浏览器端需要 HTML/CSS/JavaScript 的基础；原生平台还需要相应设备或工具链，具体见模块导读。

## 内容怎样分工

| 目录 | 应回答的问题 | 阅读时应获得的东西 |
|---|---|---|
| basics | 第一次怎么做，为什么这样做？ | 连续步骤、必要解释、可观察结果与小练习 |
| reference | 这个词、函数或库到底是什么意思？ | 定义、签名、输入输出、边界、反例与关联条目 |
| frameworks | 用框架怎样解决一个明确问题？ | 项目上下文、配置、数据流与替代方案 |
| advanced-topics | 更复杂条件下为什么这样设计？ | 机制、成立条件、代价和可验证的推理 |
| projects | 能否把已学内容连起来？ | 有限需求、分阶段产物与验收方法 |
| testing / deployment | 怎样证明正确并交付？ | 测试边界、运行配置、故障排查与恢复步骤 |

完整参考的目标是覆盖语言关键词、内置能力和常用标准库，并为每项提供必要解释。覆盖范围与深度要分开核查：列出名字不等于讲清楚。本轮已覆盖 11 个模块的教学增强；具体处理层级与尚未实际运行的平台范围见[文档审查记录](shared-resources/tools/document-quality/README.md)。

## 怎样使用与维护

- 首次学习先读[学习方法](shared-resources/learning-guide.md)，术语不熟查[跨技术栈术语](shared-resources/glossary.md)。
- [文档索引](shared-resources/tools/document-index.md)用于定位，[学习记录](shared-resources/progress/learning-progress.md)用于保存自己的实践证据。
- 易变版本与 API 看各模块 README 的技术基线；已有核实日期是历史记录，不能替代自己工程的锁文件和兼容性检查。
- 框架收录看[价值与维护标准](shared-resources/standards/tech-adoption-checklist.md)。稳定原理长期保留，版本相关写法单独注明；不承诺某个框架永远不过时。
- 文档修改遵循[写作规范](shared-resources/standards/documentation-guidelines.md)和[贡献说明](CONTRIBUTING.md)。

历史重构过程保存在 [refactor-archives](refactor-archives/README.md)，不作为当前学习的必读内容。

## 跨模块语言参考

前端、跨端和 Node.js 共用 [JavaScript 关键词](shared-resources/javascript-keywords.md)与[常用内置能力](shared-resources/javascript-builtins.md)。Rust 的[关键词](11-rust-cross-platform/reference/language-concepts/09-keywords-and-syntax.md)、[标准类型与方法](11-rust-cross-platform/reference/language-concepts/10-standard-types-and-methods.md)、[标准库地图](11-rust-cross-platform/reference/library-guides/15-standard-library-map.md)构成进入应用框架前的基础查阅入口。
