# Rust / Tauri / Axum：理解地图与学习规划

> 前置：基本函数、结构体和集合；使用 cargo 创建和运行项目，愿意根据编译器提示追踪值的来源与使用位置。

## 先回答一个问题

**谁拥有数据、谁可以借用，资源什么时候被释放？**

Rust 把所有权与借用约束放进类型检查。先用 CLI 理解数据如何跨函数流动，再分成 Tauri 应用与 Axum 服务两条实践路线；不要求先掌握所有高级生命周期技巧。

## 概念怎样连接

所有权/借用 → struct/enum → trait/泛型 → Result → 集合/迭代器 → 生命周期 → 测试 → async/应用框架

| 概念 | 必要解释 |
|---|---|
| 所有权与借用 | 移动后原绑定通常不能再使用；借用提供临时访问。Copy 与 Clone 的行为由类型契约决定，不能只看值在栈还是堆上。 |
| 生命周期 | 标注描述引用之间必须满足的关系，不会延长对象存活时间。 |
| 异步 | Future 需要被驱动才推进；运行时负责调度，不能把 async 当作自动创建线程。 |

## 从 0 到 1 的阅读顺序

先用 Cargo 建立工程并运行，再学习变量、函数与所有权。基本单元测试应在 Result 和集合练习时开始；智能指针、异步与复杂生命周期按应用需求逐步补齐。

工具链、edition 和框架基线见[模块 README](README.md)，第三方依赖按 Cargo.lock 复现。官方主线：[The Rust Programming Language](https://doc.rust-lang.org/book/)。先用语言基础章节解释编译器报错，再选择桌面或后端方向。

先用[关键词与完整语法实验](reference/language-concepts/09-keywords-and-syntax.md)认识 fn、let、struct 和 match，再开始所有权章节；不要求从其他系统语言迁移而来。

1. [Rust 环境搭建和工具链管理](basics/01-environment-setup.md)
2. [所有权与借用：Rust 的第一道门槛](basics/02-ownership-borrowing.md)
3. [结构体、枚举与模式匹配](basics/03-structs-enums-patterns.md)
4. [trait 与泛型](basics/04-traits-generics.md)
5. [错误处理：Result / panic / anyhow / thiserror](basics/05-error-handling.md)
6. [Cargo 工程化与单元测试](basics/10-cargo-testing.md)：先完成工程结构与基本测试部分。
7. [集合与迭代器](basics/06-collections-iterators.md)，随后完成 [CLI 工具](projects/01-cli-tool.md)。
8. [生命周期标注](basics/07-lifetimes.md)：涉及返回引用时带着具体编译问题学习。
9. [智能指针](basics/08-smart-pointers.md)：需要共享所有权或内部可变性时再引入。
10. [并发与 async](basics/09-concurrency-async.md)：进入需要异步运行时的框架前学习。

## 三个阶段如何验收

| 阶段与入口 | 练习输入与动作 | 通过条件 |
| --- | --- | --- |
| 借用与结果：[所有权](basics/02-ownership-borrowing.md)、[错误处理](basics/05-error-handling.md) | 用 &str 接收同一个 String 两次；再改成按值接收并比较编译结果 | 能解释移动和借用；涉及长度时声明计算字节数还是字符数，中文输入也符合契约 |
| 完整工具：[Cargo 与测试](basics/10-cargo-testing.md)、[CLI 项目](projects/01-cli-tool.md) | 指向尚不存在的测试文件执行 `list`，再新增、重启读取；分别提交空白任务、未知 ID 和损坏 JSON | 文件不存在时成功显示空列表；成功新增后可读回；空白任务、未知 ID、损坏 JSON 非零退出且原数据不变，不能把所有读取错误都当首次运行 |
| 应用分支：[桌面笔记](projects/02-tauri-notes-app.md)或 [Axum API](projects/03-axum-rest-api.md) | 选择一条路径，完成一次创建和读取，再触发非法输入 | 桌面命令或 HTTP 路由能往返，界面/接口能显示失败；桌面文件持久化与 Axum 的 PostgreSQL 均按各自正文验收。平台打包与 WebSocket 留作后续扩展 |

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

进入 CLI 前，先能解释 [Result 的传播](basics/05-error-handling.md)，并完成 [Cargo 与单元测试](basics/10-cargo-testing.md) 的基础部分。交付 `Cargo.toml`、`Cargo.lock`、按正文四个代码块顺序组成的 `src/main.rs`，以及记录命令、退出码和文件变化的 `LEARNING.md`。在独立练习目录使用同一个 `--file` 路径运行全部案例；相对路径跟随当前工作目录，换目录后的空列表不能当作持久化失败。

编译或依赖失败回 [环境与工具链](basics/01-environment-setup.md)，任务操作失败回 [CLI 正文](projects/01-cli-tool.md) 的 `run` 分支，损坏文件行为回该页 `load` 和测试；先保留失败证据，不要删除数据来消除错误。`cargo test --locked` 通过后仍需用新进程验证一次新增与读回。通过这两个层级后，再补 [并发与 async](basics/09-concurrency-async.md)，选择上表桌面或 API 分支；安装到 PATH 与发布不属于首次完成的必要条件。

选择 [Axum API](projects/03-axum-rest-api.md) 时，前置还包括 HTTP 方法/状态码、Tokio 基础及可连接的 PostgreSQL；按该页配置 `DATABASE_URL`，阅读[状态与 SQLx](frameworks/05-state-and-database-sqlx.md)。其首个路由就读取数据库，不能推迟到完成 HTTP 后才准备数据库。产物为正文的 Cargo 工程、SQL 迁移、分层源码与请求验收记录。正常验收为创建后按返回 ID 读取，并在同一数据库上重启后再读；失败验收为空标题 400 且没有新增行，删除后查询同一 ID 为 404。启动失败回查连接串与迁移，状态码错误回查 service 和 `IntoResponse`；通过后再做该页分页与仓库集成测试，随后进入 [WebSocket 实时应用](projects/04-websocket-realtime.md)。

选择 [Tauri 桌面笔记](projects/02-tauri-notes-app.md) 时，先补 React/TypeScript 函数组件、`Mutex` 与平台 WebView 构建环境，交付前端、Rust 命令、配置/权限文件和应用数据目录中的笔记文件。按正文完成创建、读取及重启读回；正文前端尚未捕获命令拒绝，需先给 `submit` 补 `try/catch` 与可见错误提示，再验收空白标题显示失败且不新增笔记；IPC 调用失败回查命令注册与参数，重启读回失败回查数据目录和保存逻辑。完成这些验收步骤后，再进入该页平台打包挑战。这些是分支学习的验收要求；学习者需在目标平台自行执行并记录结果。

## 框架与高级主题怎么选

Tauri 解决 Web 前端与原生能力协作，Axum 解决 HTTP 服务。Tokio、Serde 和错误库按具体边界引入；unsafe、宏与复杂 Pin 规则作为有前提的扩展。

## 全量参考怎么查

关键词解决“语法是什么意思”，内置函数解决“直接能调用什么”，标准库解决“导入以后能做什么”。框架 API 另列，避免把库函数误当成语言本身。以下是现有文章的完整导航，不代表每个 API 都已充分讲解；具体覆盖缺口进入审查台账。

### framework-essentials

- [Tauri 2.11 精要](reference/framework-essentials/09-tauri-2-essentials.md)
- [Tauri IPC 命令](reference/framework-essentials/10-tauri-ipc-commands.md)
- [Axum 0.8 精要](reference/framework-essentials/11-axum-essentials.md)

### language-concepts

- [所有权细则字典（move / Clone / Copy / 借用 / Drop）](reference/language-concepts/01-ownership-dictionary.md)
- [trait 对象与动态分发字典（dyn Trait / 对象安全 / vtable）](reference/language-concepts/02-trait-objects.md)
- [常量泛型字典（const N / 数组与固定长度抽象 / 稳定版限制）](reference/language-concepts/03-const-generics.md)
- [高级生命周期字典（变型 / HRTB / 'static 两种含义）](reference/language-concepts/04-advanced-lifetimes.md)
- [宏系统](reference/language-concepts/05-macros.md)
- [unsafe Rust](reference/language-concepts/06-unsafe.md)
- [智能指针全表](reference/language-concepts/07-smart-pointers.md)
- [Future·Pin·Waker](reference/language-concepts/08-async-internals.md)

### library-guides

- [Tokio - 异步运行时全量速查](reference/library-guides/12-tokio-guide.md)
- [Serde - 序列化框架全量速查](reference/library-guides/13-serde-guide.md)
- [错误处理库 - std Error / thiserror / anyhow](reference/library-guides/14-error-libraries.md)

### 新补基础参考

- [Rust 关键词与语法入口](reference/language-concepts/09-keywords-and-syntax.md)
- [Rust 常用标准类型、方法与宏](reference/language-concepts/10-standard-types-and-methods.md)
- [Rust 常用标准库地图](reference/library-guides/15-standard-library-map.md)

## 卡住时

先判断是术语不懂、输入输出不清、代码上下文缺失，还是运行环境不同。返回[学习方法](../shared-resources/learning-guide.md)按证据排查；通用术语见[术语解释](../shared-resources/glossary.md)。
