# Rust 环境搭建和工具链管理

## 先理解，再动手

rustup 管工具链，cargo 管构建与依赖。edition 是源码语言模式，不等于编译器版本号。

**本节自测**：创建项目，分别运行 cargo check、cargo run 与 cargo test。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

能说明检查、运行、测试各自证明什么；命令成功不等于未编写的行为已验证。

</details>

> **文档简介**: 从零搭建 Rust 开发环境——用 rustup 管理工具链、用 cargo 创建并运行第一个项目、理解 edition 兼容机制。这是整个模块的起点。
>
> **目标读者**: 有任意语言开发经验（PHP/Go/JS/Java 均可），首次接触 Rust 的开发者
>
> **前置知识**: 基本命令行操作；无需任何系统语言经验

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#rust` `#环境配置` `#rustup` `#cargo` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ **掌握核心概念**: 理解 rustup / cargo / edition 三件套的分工——这是 Rust 工具链与多数语言的第一差异点
- ✅ **实践能力**: 安装并验证工具链、创建第一个 cargo 项目、掌握常用 cargo 命令与工具链版本管理
- ✅ **解决问题**: 多项目工具链版本不一致、国内依赖下载慢等常见环境问题
- ✅ **进阶方向**: 为 [02 所有权与借用](./02-ownership-borrowing.md) 的学习扫清环境障碍

## 📋 目录

- [核心概念](#-核心概念)
- [实践指南](#️-实践指南)
- [代码示例](#-代码示例)
- [最佳实践](#-最佳实践)
- [常见问题](#-常见问题)
- [交叉引用](#-交叉引用)
- [总结](#-总结)

---

## 🔍 核心概念

### 概念一：rustup —— 工具链管理器

**定义**: rustup 是 Rust 官方推荐的工具链安装与管理器，负责安装 rustc（编译器）、cargo（构建工具）与标准文档，并能维护多套工具链并存切换。

**关键特性**:
- 一条命令安装全套工具链，所有内容收敛在用户目录，不污染系统
- stable / beta / nightly 三条通道并存，可全局切换也可按目录覆盖
- 组件化管理：clippy（静态检查）、rustfmt（格式化）按需补装

**使用场景**:
- 跟进 stable 六周一发的更新节奏：`rustup update`
- 老项目锁定旧工具链：目录级覆盖（见实践指南步骤四）

### 概念二：cargo —— 构建工具与包管理器

**定义**: cargo 是 Rust 的官方构建系统与包管理器，一个命令覆盖创建、编译、测试、发布全流程，角色上对标 Go Modules、Composer、npm。

**关键特性**:
- `Cargo.toml` 声明项目元数据与依赖，`Cargo.lock` 锁定精确版本
- 默认从 crates.io 拉取依赖，按语义化版本兼容规则解析
- `cargo check` 只做类型与借用检查、不生成二进制，是日常最快的反馈手段

### 概念三：edition —— 版本兼容承诺

**定义**: edition 是 Rust 的"语言方言版本"机制。每个 edition 是一组语法与默认行为的集合，编译器同时支持所有 edition，旧代码迁移通常只需改一行 `Cargo.toml`。

**关键特性**:
- 当前 edition 为 **2024**（版本基线见 [模块 README](../README.md) 技术基线区块）
- 历史 editions：2015 / 2018 / 2021 / 2024，可按项目各自选择
- edition 只影响语言层规则，标准库跨 edition 通用，第三方库天然兼容

**与其他语言的对比**（理解 Rust"零破坏升级"的关键）:

| 语言 | 升级方式 | 兼容成本 |
|------|---------|---------|
| Python | 解释器大版本切换（2→3 破坏性） | 高 |
| JavaScript | 运行时兼容旧语法，靠转译工具链前进 | 中 |
| Rust | edition 显式切换，编译器永远支持旧 edition | 低 |

> 💡 这就是模块 README 所说"Rust 是知识库中半衰期最长的语言资产"的机制原因：自 2015 年 1.0 至今零破坏性升级。

---

## 🛠️ 实践指南

### 步骤一：安装 rustup 与工具链

**目标**: 拿到同一 rustup 工具链提供的可用 rustc / cargo；记录实际版本而不是假定它们显示相同的补丁号

**操作指南**:
1. 访问 [rustup.rs](https://rustup.rs) 按官方指引安装
2. 验证安装结果
3. 国内用户可选配置 crates.io 镜像加速

```bash
# Linux / macOS 安装（一行装齐 rustc、cargo、rustup 与标准库文档）
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 使当前 shell 生效（或重开终端）
source "$HOME/.cargo/env"

# 验证：记录编译器、构建工具和 rustup 的实际版本
rustc --version
cargo --version
rustup --version
```

```toml
# ~/.cargo/config.toml —— 可选：国内 crates.io 镜像加速（以 rsproxy 为例）
[source.crates-io]
replace-with = 'rsproxy'

[source.rsproxy]
registry = "sparse+https://rsproxy.cn/index/"
```

**判断方法**：`rustc --version`、`cargo --version` 能输出版本，并用下一步的 `cargo check`/`cargo run` 验证当前项目实际调用它们。稳定通道的小版本会变化；本模块的版本基线见 [模块 README](../README.md)，新建或升级项目时以 `rust-toolchain.toml` 和 CI 使用的工具链为准。

### 步骤二：创建第一个项目

**操作指南**:

```bash
cargo new hello-rust   # 创建项目并初始化 git
cd hello-rust
cargo run              # 编译并运行
```

目录结构：

```text
hello-rust/
├── Cargo.toml      # 项目清单：元数据 + 依赖声明
├── Cargo.lock      # 依赖精确锁定（应用项目应提交进 git）
├── .gitignore      # cargo 已写好，target/ 不入库
└── src/
    └── main.rs     # 入口源码
```

```toml
[package]
name = "hello-rust"
version = "0.1.0"
edition = "2024"   # 当前 edition，与模块 README 技术基线一致

[dependencies]
```

把 `src/main.rs` 改成以下程序，再在项目根目录按顺序运行 `cargo check`、`cargo run` 与 `cargo test`。`cargo check` 验证当前源码能通过分析，`cargo run` 还会生成并执行二进制，`cargo test` 只验证你实际写出的断言。

```rust verify:rust-environment-cargo
fn greeting(name: &str) -> String {
    format!("Hello, {name}!")
}

fn main() {
    println!("{}", greeting("Rust"));
}

#[cfg(test)]
mod tests {
    use super::greeting;

    #[test]
    fn formats_a_greeting() {
        assert_eq!(greeting("Rust"), "Hello, Rust!");
    }
}
```

```bash
cargo check
cargo run
# Hello, Rust!
cargo test
```

这三条命令不下载外部依赖，因为示例没有依赖；它们也不证明交叉编译目标、第三方 crate、网络镜像或发布流程可用。

### 步骤三：常用 cargo 命令

```bash
cargo new xxx        # 新建项目
cargo init           # 在现有目录初始化项目
cargo run            # 编译并运行
cargo check          # 只做类型/借用检查，不生成二进制（最快反馈）
cargo build          # 编译（debug）；--release 进入优化模式
cargo test           # 运行测试
cargo fmt            # rustfmt 格式化代码
cargo clippy         # 更严格的静态检查，日常开发必开
cargo add serde      # 添加依赖并写入 Cargo.toml
cargo update         # 按 Cargo.toml 约束升级 Cargo.lock
cargo tree           # 打印依赖树
cargo doc --open     # 生成并打开本项目及依赖的文档
```

### 步骤四：工具链管理与目录覆盖

rustup 的核心价值是"多套工具链并存 + 按目录切换"：

```bash
# 更新当前默认工具链
rustup update

# 查看当前生效的工具链与已装组件
rustup show

# 补装常用组件
rustup component add clippy rustfmt

# 阅读本地离线文档（含 The Rust Programming Language）
rustup doc
```

**rustup 覆盖目录**：同一台机器上，不同项目可绑定不同工具链。

```bash
# 方式一：对当前目录做一次性覆盖
rustup override set stable
```

```toml
# 方式二（推荐）：项目根放 rust-toolchain.toml，随仓库走、对全团队生效
[toolchain]
channel = "stable"
components = ["clippy", "rustfmt"]
```

进入含 `rust-toolchain.toml` 的目录后，所有 cargo / rustc 命令自动使用文件指定的工具链，优先级高于全局默认值。

---

## 💻 代码示例

> 以下两段是可用 `rustc --edition 2024` 复核的完整示例。请在自己的工具链中编译、运行，并把实际版本和输出记入项目记录。

### 示例一：Hello World 与变量预览

```rust
fn main() {
    println!("Hello, Rust!");
    // 变量默认不可变
    let name = "Dev Quest";
    // mut 声明可变变量
    let mut count = 0;
    count += 1;
    println!("欢迎来到 {name}，计数: {count}");
}
```

**关键点解析**:
- `let` 默认不可变、`let mut` 才可变——Rust 把"可变性"做成显式声明，编译器可据此优化并拦截误改
- `{name}` 是格式化内插写法，变量名直接写进字符串
- `println!` 是宏而非函数（感叹号是宏的标志），参数个数在编译期检查

### 示例二：读取命令行参数

```rust
use std::env;

fn main() {
    // 跳过程序名本身，收集命令行参数
    let args: Vec<String> = env::args().skip(1).collect();

    if args.is_empty() {
        println!("用法: greet <你的名字>");
        return;
    }

    let name = &args[0];
    println!("你好，{name}！这是你的第一个 Rust CLI。");
}
```

```bash
cargo run -- rustacean
# 输出: 你好，rustacean！这是你的第一个 Rust CLI。
```

**关键点解析**:
- `env::args()` 返回迭代器，`skip(1)` 跳过程序名，`collect()` 收集成 `Vec<String>`
- `cargo run --` 之后的内容传给程序本身，而不是 cargo
- `&args[0]` 中的 `&` 是借用——这正是下一篇的主题

---

## 🎨 最佳实践

先让同一工具链完成 check、build、test，理解三者分别验证类型、生成产物和执行行为。工具链文件、锁文件和 CI 配置共同记录复现条件，编译目标与系统依赖也要说明。

clippy 提供改进线索，遇到告警先理解原因再修或写出例外依据。target 可重建不应提交；Cargo.lock 的提交与下游依赖解析是两回事，库项目也可以提交锁文件以固定自身开发测试，不能概括成“库通常必须忽略”。

---

## ❓ 常见问题

### Q1: rustup、rustc、cargo 三者的关系？
**A**: rustup 管安装与版本（维护的是"工具链"整体）；rustc 是编译器本体；cargo 是面向项目的构建与包管理入口。你 95% 的时间只敲 cargo，它在底层调用 rustc。

### Q2: 目录覆盖和 rust-toolchain.toml 冲突吗？
**A**: 优先级为 `rust-toolchain.toml` > `rustup override set` > 全局 default。两处同时配置时以 rust-toolchain.toml 为准，团队项目建议只用后者。

### Q3: stable 更新一定不会影响我的代码吗？
**A**: Rust 的 edition 机制降低语言迁移成本，但不能把它理解成所有项目升级都零风险。编译器 lint 变化、依赖的 MSRV、build script、链接器和平台目标都可能让构建结果变化。stable 通道通常约每 6 周发布；先在独立变更中更新 `rust-toolchain.toml`，运行项目的 check/test/build，再升级 CI，而不是直接把所有项目切到最新版本。

---

## 🔗 交叉引用

### 本模块
- 📄 **[02 所有权与借用](./02-ownership-borrowing.md)** — 环境就绪后的第一道核心门槛
- 📄 **[05 错误处理](./05-error-handling.md)** — 掌握 cargo 后的第一个工程化主题
- 📖 **[模块 README](../README.md)** — 技术基线与三路径学习视图

### 跨模块
- 📄 **[04 多平台应用](../../04-multiplatform-apps/README.md)** — 三端原生路线的环境搭建对标；Rust 侧的跨端方案（Tauri 2）详见本模块 frameworks/ 后续篇目

---

## 📝 总结

### 核心要点回顾
1. **分工明确**: rustup 管"工具链"，cargo 管"项目"，edition 管"语言方言版本"
2. **零破坏承诺**: edition 机制让 Rust 十年零破坏升级，是知识库首选它的根本原因
3. **日常三件套**: `cargo check` / `cargo fmt` / `cargo clippy`，加上 `rust-toolchain.toml` 锁定团队环境

### 学习成果检查
- [ ] rustc / cargo / rustup 版本号输出一致
- [ ] `cargo new` → `cargo run` 走通第一个项目
- [ ] 能说出 `rust-toolchain.toml` 与全局默认的优先级关系
- [ ] 理解 edition 与"语言版本"的区别

---

**最后更新**: 2026年9月

> 🎯 **下一步**: 环境就绪，进入 [02 所有权与借用](./02-ownership-borrowing.md)——Rust 与其他语言思维方式差异最大的部分。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
