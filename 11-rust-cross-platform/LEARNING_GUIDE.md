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

以下按模块现有章节编号导航。章节中的“先理解，再动手”给出本节重点与自测；环境版本集中看[模块 README](README.md)。

先用[关键词与完整语法实验](reference/language-concepts/09-keywords-and-syntax.md)认识 fn、let、struct 和 match，再开始所有权章节；不要求从其他系统语言迁移而来。

1. [Rust 环境搭建和工具链管理](basics/01-environment-setup.md)
2. [所有权与借用：Rust 的第一道门槛](basics/02-ownership-borrowing.md)
3. [结构体、枚举与模式匹配](basics/03-structs-enums-patterns.md)
4. [trait 与泛型](basics/04-traits-generics.md)
5. [错误处理：Result / panic / anyhow / thiserror](basics/05-error-handling.md)
6. [集合与迭代器：零抽象成本的数据流水线](basics/06-collections-iterators.md)
7. [生命周期标注：让引用的合法性成为编译期契约](basics/07-lifetimes.md)
8. [智能指针：当所有权与借用不够用的时候](basics/08-smart-pointers.md)
9. [并发与 async：无畏并发的两条路线](basics/09-concurrency-async.md)
10. [Cargo 工程化与单元测试：从单文件到可维护的仓库](basics/10-cargo-testing.md)

## 三个阶段如何验收

1. 写一个接收 &str 返回长度的函数，原字符串调用两次仍可用；再比较接收 String。
2. 做内存 CLI 并把错误用 Result 返回，测试无效输入；持久化另加文件错误用例。
3. 选择 Tauri 或 Axum 一条分支，先走通一条命令或路由，再引入数据库和并发。

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

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
