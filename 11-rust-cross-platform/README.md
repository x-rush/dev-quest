# Rust 跨平台开发（第 11 模块 · 探索系列）

> **本轮增强与版本核对**：学习路径及正文增强范围见 [逐文件台账](../shared-resources/tools/document-quality/reports/coverage.md)。下方技术基线中的旧核对日期属于历史记录，不表示这次已重跑所有平台；安装与升级以官方兼容要求、项目锁文件和实际构建结果为准。


第一次学习请从[理解地图与学习规划](LEARNING_GUIDE.md)开始，按其中的阶段任务和验收条件推进。先用 Cargo 做函数、借用和 Result 练习，完成 CLI 项目后选择 Tauri 桌面或 Axum 后端。两条应用方向可以独立推进，桌面方向另需 Web 前端知识。

查语法、函数或库时使用下方参考目录。文件数量与目录中的完成标记表示内容组织情况，不能替代示例运行证据；具体交付按[知识库质量基线](../shared-resources/standards/knowledge-delivery-baseline.md)验收。

> **模块定位**：以 Rust 语言全量参考为根基，Tauri 2 跨端应用为旗舰方向（对标 04-multiplatform-apps 的三端原生路线），Axum 后端为辅线。学习重点是所有权、类型约束、错误传播与平台边界。edition 提供演进机制，但不能据此承诺任意旧代码与第三方依赖永久无需迁移。

## 🧭 技术基线

> 以下版本于 **2026-09-16** 经 crates.io API 与 rust-lang 官方 stable channel 实核（工具：baseline-check）。正文中旧版本引用以本基线为准对齐。

| 技术 | 当前版本 | 说明 | 核实日期 |
|------|---------|------|---------|
| Rust | **1.98.1** | 2026-09-03 stable channel；edition 2024 为当前 edition | 2026-09-16 |
| Tauri | **2.11** | 跨端桌面+移动框架（crates.io 30.9M 下载） | 2026-09-16 |
| Tokio | **1.53** | 异步运行时事实标准 | 2026-09-16 |
| Axum | **0.8** | Tokio 生态 Web 框架（tower 中间件体系） | 2026-09-16 |
| Serde | **1.0.229** | 序列化框架（derive 生态核心） | 2026-09-16 |
| SQLx | **0.9** | 编译期校验 SQL 的异步数据库工具箱 | 2026-09-16 |
| Reqwest | **0.13** | HTTP 客户端 | 2026-09-16 |
| Clap | **4.6** | CLI 参数解析 derive 风格 | 2026-09-16 |
| Tracing | **0.1** | 结构化日志与 span 追踪 | 2026-09-16 |

**收录判据**：按[技术收录标准](../shared-resources/standards/tech-adoption-checklist.md)区分基础、应用主线与专题。当前主线分别用 Tauri 练习原生能力边界、Axum 练习 HTTP 服务、Tokio 练习异步调度；这不表示其他框架失去价值。WASM 作为按目标平台选修的扩展，不以“竞争尚未结束”代替适用性分析。上方历史版本核对记录保留日期，本轮没有重新验证整张版本表。

## 🗺️ 目录导览（原 47 篇，新增 3 篇基础参考）

原目录记录过 rustc 验证；本轮新增或修改的 Rust 示例尚未本机执行，不能沿用旧记录视为新内容已通过。目录“已建成”只表示文章存在。

| 象限 | 目录 | 篇数 | 状态 |
|------|------|-----:|------|
| 📖 教程（按序入门） | `basics/` | 10 | ✅ 已建成 |
| 📚 字典（全量参考） | `reference/` | 17 | ✅ 已建成 |
| 🛠️ 指南（框架生态） | `frameworks/` | 7 | ✅ 已建成 |
| 🚀 指南（实战项目） | `projects/` | 5 | ✅ 已建成 |
| 🔧 指南（测试工程） | `testing/` | 3 | ✅ 已建成 |
| 🔧 指南（部署运维） | `deployment/` | 4 | ✅ 已建成 |
| 💡 解释（高级主题） | `advanced-topics/` | 4 | ✅ 已建成 |

### 📖 basics/ 教程（文件目录，学习顺序见导读）

1. `01-environment-setup.md` — rustup / cargo / 工具链管理
2. `02-ownership-borrowing.md` — 所有权与借用（Rust 第一道门槛）
3. `03-structs-enums-patterns.md` — 结构体、枚举与模式匹配
4. `04-traits-generics.md` — trait 与泛型
5. `05-error-handling.md` — Result / panic / anyhow / thiserror
6. `06-collections-iterators.md` — 集合与迭代器（零抽象成本）
7. `07-lifetimes.md` — 生命周期标注
8. `08-smart-pointers.md` — Box / Rc / Arc / RefCell
9. `09-concurrency-async.md` — 并发与 async/.await（Tokio 入门）
10. `10-cargo-testing.md` — Cargo 工程化与单元测试

### 📚 reference/ 知识字典

- [关键词与语法入口](reference/language-concepts/09-keywords-and-syntax.md)
- [常用标准类型、方法与宏](reference/language-concepts/10-standard-types-and-methods.md)
- [常用标准库地图](reference/library-guides/15-standard-library-map.md)

- `language-concepts/01-ownership-dictionary.md` ~ `08-async-internals.md`（8 篇：所有权细则 / trait 对象与动态分发 / 常量泛型 / 高级生命周期 / 宏系统 / unsafe / Future·Pin·Waker / 智能指针全表）
- `framework-essentials/09-tauri-2-essentials.md`、`10-tauri-ipc-commands.md`、`11-axum-essentials.md`
- `library-guides/12-tokio-guide.md`、`13-serde-guide.md`、`14-error-libraries.md`

### 🛠️ frameworks/ + 🚀 projects/ + 🔧 testing|deployment/

- `frameworks/`：Tauri 2 架构 / 插件体系 / 前端集成（React+TS）/ Axum Web 栈 / 状态与数据库（SQLx）/ 认证中间件 / 桌面打包
- `projects/`（⭐ 递进）：CLI 工具 → Tauri 桌面笔记 → Axum REST API → WebSocket 实时应用 → 多端发布流水线
- `testing/`：单元与集成测试 / Criterion 基准 / Tauri E2E（WebDriver）
- `deployment/`：交叉编译 targets / GitHub Actions CI / 签名与自动更新 / 容器化服务

### 💡 advanced-topics/

内存布局与性能 / FFI 与 bindgen / wasm32 target / 安全实践

## 🛤️ 三路径视图

- **基础路径**：[环境](basics/01-environment-setup.md) → [语法入口](reference/language-concepts/09-keywords-and-syntax.md) → [所有权](basics/02-ownership-borrowing.md) → [结构体与枚举](basics/03-structs-enums-patterns.md) → [trait](basics/04-traits-generics.md) → [错误处理](basics/05-error-handling.md) → [Cargo 与测试](basics/10-cargo-testing.md) → [集合](basics/06-collections-iterators.md) → [CLI 项目](projects/01-cli-tool.md)。验收正常输入、格式错误和文件不存在。
- **应用路径**：按需求选择 [Tauri 笔记](projects/02-tauri-notes-app.md)或 [Axum API](projects/03-axum-rest-api.md)。先完成一条读写流程，再加入数据库、错误恢复和测试；桌面前端知识与异步知识按所选分支补齐。
- **专题路径**：从应用中遇到的问题选择生命周期、智能指针、异步、FFI 或 wasm；[多平台发布](projects/05-multiplatform-release.md)分别验证每个目标的构建和运行，不以一套平台的结果推断其他平台。

## 📚 文档元数据

- **前置模块**：无硬性前置；Tauri 前端集成篇建议先修 [02-nextjs-frontend](../02-nextjs-frontend/README.md) 或 [03-tanstack-stack](../03-tanstack-stack/README.md)
- **关联模块**：[04-multiplatform-apps](../04-multiplatform-apps/README.md)（三端原生对标）、[09-nodejs-backend](../09-nodejs-backend/README.md)（Axum 与 Express 对照）
- **建设约定**：新建篇目须同步更新本 README 建设状态、[document-index](../shared-resources/tools/document-index.md) 与 [learning-progress](../shared-resources/progress/learning-progress.md)
