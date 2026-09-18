# 项目实战 1：rtask —— JSON 持久化 CLI 工具（Clap + anyhow）

## 分阶段练习与验收

**最小阶段**：先做内存任务的增查，再增加 JSON 文件持久化。

**验收结果**：无效命令非零退出，损坏 JSON 明确失败，重启后任务可读取。

**扩展顺序**：不要吞掉读取错误并覆盖旧数据；再考虑原子写入与并发。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> **文档简介**: 从零构建一个完整的待办任务命令行工具，覆盖 Clap 4.6 derive 风格参数解析、子命令设计、JSON 文件持久化、anyhow 错误链与 `cargo install` 发布全流程
>
> **目标读者**: 完成 basics 入门路径（01-05 必读）的 Rust 初学者
>
> **前置知识**: 所有权与借用、Result 错误处理、结构体与枚举（见 [basics 05](../basics/05-error-handling.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 操作指南（项目实战） |
| **难度** | ⭐ 入门 |
| **标签** | `#rust` `#clap` `#anyhow` `#cli` `#cargo-install` |
| **更新日期** | `2026年9月` |
| **状态** | ✅ 已完成 |

</details>

> 版本基线以 [模块 README 技术基线区块](../README.md) 为准（Rust 1.98.1 / edition 2024、Clap 4.6、Serde 1.0.229）。本篇 Rust 代码块已经本机 `cargo`（含依赖实装）与 `rustc --edition 2024` 实测通过。

## 🎯 学习目标

完成本项目后，你将能够：

- ✅ **掌握 Clap 4.6 derive 风格**: 用结构体与枚举声明式定义参数、选项与子命令
- ✅ **实践文件持久化**: `std::fs` 读写 + serde_json 序列化，优雅处理"文件不存在"的首次运行
- ✅ **构建错误链**: 用 anyhow 的 `.context()` 与 `{e:#}` 输出可诊断的错误信息
- ✅ **发布工具**: 通过 `cargo install` 安装进 PATH，并了解 crates.io 发布流程

## 📋 目录

- [需求与项目结构](#需求与项目结构)
- [分步实现](#分步实现)
- [运行与验证](#运行与验证)
- [发布：cargo install 与 crates.io](#发布cargo-install-与-cratesio)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [扩展方向](#扩展方向)
- [相关资源](#相关资源)
- [总结](#-总结)

---

## 需求与项目结构

### 功能需求

`rtask` 是一个基于 JSON 文件的待办任务管理器，命令行交互设计如下：

```bash
rtask add "学习 Rust 所有权"    # 新增任务
rtask list                      # 列出全部任务
rtask list --pending            # 只看未完成
rtask done 1                    # 完成任务 #1
rtask rm 2                      # 删除任务 #2
rtask --file ~/tasks.json list  # 自定义存储文件
```

**非功能需求**：

- 首次运行（无存储文件）静默当作空列表，而不是报错
- 所有 IO/解析错误必须带上下文（哪个文件、什么操作），且退出码非 0
- 纯逻辑与 IO 分离，核心逻辑可单元测试

### 技术栈与依赖

`cargo new rtask` 后编辑 `Cargo.toml`（版本基线见模块 README）：

```toml
[package]
name = "rtask"
version = "0.1.0"
edition = "2024"

[dependencies]
clap = { version = "4.6", features = ["derive"] }
serde = { version = "1.0.229", features = ["derive"] }
serde_json = "1"
anyhow = "1"
```

### 项目结构

本项目体量小，单文件 `src/main.rs` 即可；模块化拆分见扩展方向。

```
rtask/
├── Cargo.toml
└── src/
    └── main.rs     # CLI 定义 + 存储 + 业务逻辑 + 单元测试
```

---

## 分步实现

### 步骤 1：声明命令行接口

Clap derive 风格把"参数解析"变成类型定义：结构体字段即选项，枚举变体即子命令。

```rust
use anyhow::{Context, Result, bail};
use clap::{Parser, Subcommand};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

/// rtask —— 基于 JSON 文件的待办任务管理器
#[derive(Parser)]
#[command(name = "rtask", version, about)]
struct Cli {
    /// 任务存储文件路径（默认 ./rtask.json）
    #[arg(short, long, default_value = "rtask.json")]
    file: PathBuf,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// 新增一条任务
    Add {
        /// 任务内容
        text: String,
    },
    /// 列出任务
    List {
        /// 只显示未完成任务
        #[arg(short, long)]
        pending: bool,
    },
    /// 完成指定任务
    Done { id: u32 },
    /// 删除指定任务
    Rm { id: u32 },
}
```

**关键点解析**：

- `#[derive(Parser)]`：入口结构体。`--file/-f` 是全局选项，必须出现在子命令之前（如 `rtask --file x.json list`）
- 文档注释 `///` 会成为 `rtask add --help` 的说明文本，不是装饰
- `Done { id: u32 }`：位置参数自动做类型校验，`rtask done abc` 会被 Clap 拒绝
- 枚举变体名 `Rm` 会被转为小写子命令 `rm`

### 步骤 2：数据模型与存储层

```rust
#[derive(Serialize, Deserialize)]
struct Task {
    id: u32,
    text: String,
    done: bool,
}

fn load(path: &Path) -> Result<Vec<Task>> {
    // 文件不存在视为空列表（首次使用体验），其余 IO 错误带上路径上下文上抛
    let raw = match std::fs::read_to_string(path) {
        Ok(s) => s,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(Vec::new()),
        Err(e) => return Err(e).with_context(|| format!("读取 {} 失败", path.display())),
    };
    serde_json::from_str(&raw).with_context(|| format!("解析 {} 失败", path.display()))
}

fn save(path: &Path, tasks: &[Task]) -> Result<()> {
    let raw = serde_json::to_string_pretty(tasks).context("序列化任务失败")?;
    std::fs::write(path, raw).with_context(|| format!("写入 {} 失败", path.display()))
}

fn next_id(tasks: &[Task]) -> u32 {
    tasks.iter().map(|t| t.id).max().unwrap_or(0) + 1
}
```

**关键点解析**：

- `with_context` 只在出错时才构造消息，成功路径零开销
- 错误链一条输出两层信息：`读取 /x/rtask.json 失败: No such file or directory`
- 打印路径用 `path.display()`，而非直接格式化 `Path`

### 步骤 3：业务逻辑（含一个借用检查教学点）

```rust
fn run(cli: &Cli) -> Result<()> {
    let mut tasks = load(&cli.file)?;
    match &cli.command {
        Commands::Add { text } => {
            let id = next_id(&tasks);
            tasks.push(Task { id, text: text.clone(), done: false });
            save(&cli.file, &tasks)?;
            println!("已添加任务 #{id}: {text}");
        }
        Commands::List { pending } => {
            let mut shown = false;
            for t in &tasks {
                if *pending && t.done {
                    continue;
                }
                let mark = if t.done { "x" } else { " " };
                println!("[{mark}] #{:<3} {}", t.id, t.text);
                shown = true;
            }
            if !shown {
                println!("（暂无任务）");
            }
        }
        Commands::Done { id } => {
            // 借用检查教学点：task 的可变借用必须先结束，才能把 tasks 整体传给 save。
            // 用块作用域收敛可变借用，块内取出所需数据。
            let text = {
                let task = tasks
                    .iter_mut()
                    .find(|t| t.id == *id)
                    .ok_or_else(|| anyhow::anyhow!("任务 #{id} 不存在"))?;
                if task.done {
                    bail!("任务 #{id} 已经完成，无需重复操作");
                }
                task.done = true;
                task.text.clone()
            };
            save(&cli.file, &tasks)?;
            println!("已完成任务 #{id}: {text}");
        }
        Commands::Rm { id } => {
            let before = tasks.len();
            tasks.retain(|t| t.id != *id);
            if tasks.len() == before {
                bail!("任务 #{id} 不存在");
            }
            save(&cli.file, &tasks)?;
            println!("已删除任务 #{id}");
        }
    }
    Ok(())
}
```

**关键点解析**：

- `Done` 分支：若在 `find` 返回的 `&mut Task` 存活期间调用 `save(&tasks)`，会触发 E0502（同一数据的可变借用与不可变借用并存）。块作用域 + 取出 `text` 是最直白的解法
- 一次性工具的业务错误直接用 `bail!`/`anyhow!` 构造，无需定义错误类型；库代码应改用 thiserror（对照 [basics 05](../basics/05-error-handling.md)）

### 步骤 4：入口与单元测试

```rust
fn main() {
    let cli = Cli::parse();
    if let Err(e) = run(&cli) {
        // {e:#} 用 anyhow 的交替格式输出整条错误链
        eprintln!("rtask: {e:#}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn task(id: u32, done: bool) -> Task {
        Task { id, text: "示例".into(), done }
    }

    #[test]
    fn next_id_starts_from_one() {
        assert_eq!(next_id(&[]), 1);
    }

    #[test]
    fn next_id_follows_max() {
        assert_eq!(next_id(&[task(3, false), task(7, true)]), 8);
    }
}
```

**关键点解析**：

- `Cli::parse()` 在解析失败或用户敲 `--help` 时自动退出，无需手写帮助文本
- `main` 保持薄：只做"解析 → 委托 → 报错"；`run` 返回 `Result`，业务逻辑可整体驱动
- 二进制 crate 里的 `#[cfg(test)]` 模块同样能被 `cargo test` 运行

---

## 运行与验证

```bash
cargo run -- add "学习 Rust 所有权"
cargo run -- add "完成 Tauri 笔记项目"
cargo run -- list
cargo run -- done 1
cargo run -- list --pending
cargo run -- rm 2
cargo run -- done 99     # 错误路径：rtask: 任务 #99 不存在（退出码 1）
cargo test               # 2 个单元测试
```

存储文件 `rtask.json`（serde_json 序列化结果）：

```json
[
  {
    "id": 1,
    "text": "学习 Rust 所有权",
    "done": true
  }
]
```

---

## 发布：cargo install 与 crates.io

**本地安装**：编译 release 版并放入 `~/.cargo/bin`（该目录默认在 PATH 中）：

```bash
cargo install --path .
rtask list   # 任意目录可用
```

**发布到 crates.io**（可选）：

1. 注册 crates.io 账号并 `cargo login <token>`
2. 确认 `Cargo.toml` 的 `name` 未被占用，补全 `description`、`license` 字段
3. `cargo publish --dry-run` 预检，再 `cargo publish` 正式发布
4. 修复 bug 后 bump 版本号重新 publish——crates.io 上的已发布版本不可覆盖

把 rtask 纳入 workspace 与 CLI/桌面/服务端统一发布，见 [项目实战 5](./05-multiplatform-release.md)。

---

## 最佳实践

CLI 将参数解析、业务计算和文件读写分开，纯函数测试不用碰真实用户文件，存储测试使用临时目录。退出码让 shell 能判断下一步是否执行，错误消息说明哪个操作失败并避免泄漏秘密。

Path/PathBuf 配合 args_os 等接口处理可能不是 UTF-8 的路径；库化参数解析有助复杂命令维护，最小实验也可手写。测试不存在文件、权限错误和非法参数，而不把外部 I/O 失败全部 unwrap 成 panic。

---

## 常见问题

### Q1: 想让 `rtask add --file x "..."`（选项在子命令后）也能用？

**A**: 把 `--file` 从 `Cli` 移到每个子命令变体中，或定义公共选项结构体后用 `#[command(flatten)]` 混入各子命令。`Cli` 上的全局选项必须出现在子命令之前，这是 POSIX 风格约定，Clap 默认遵循。

### Q2: JSON 文件被手工改坏了怎么办？

**A**: `serde_json::from_str` 的解析错误经 `with_context` 已带出行列信息。生产级工具可在此分支提示用户备份并重建文件；更严谨的方案是"写临时文件 + `std::fs::rename` 原子替换"，避免写一半崩溃损坏数据。

---

## 扩展方向

- **练习 1（基础）**: 新增 `rtask edit <id> <text>` 子命令，复用 `Done` 分支的块作用域借用模式
- **练习 2（进阶）**: 为 `Task` 增加 `created_at` 时间戳字段，旧文件无此字段时用 `#[serde(default)]` 兼容
- **练习 3（挑战）**: 并发安全——两个 rtask 进程同时写同一文件会互相覆盖，调研文件锁（`fd-lock`）或改用嵌入式数据库（`rusqlite`）

---

## 相关资源

### 📖 交叉引用

- 📄 **[错误处理：anyhow 与 thiserror](../basics/05-error-handling.md)** — 本篇错误处理的原理层
- 📄 **[Cargo 工程化与单元测试](../basics/10-cargo-testing.md)** — `cargo test` 与发布配置细节
- 📄 **[单元与集成测试](../testing/01-unit-integration-tests.md)** — 给 CLI 补集成测试
- 📄 **[多端发布流水线](./05-multiplatform-release.md)** — CLI + 桌面 + 服务端统一发布
- 📖 **[Clap 官方文档](https://docs.rs/clap/4.6/clap/)** — derive API 全量参考

---

## 📝 总结

### 核心要点回顾

1. **derive 风格 CLI**: 结构体/枚举即接口定义，帮助文本来自文档注释
2. **anyhow 错误链**: `.context()` 补语义、`{e:#}` 打印全链、退出码非 0
3. **存储隔离**: IO 集中在 `load`/`save`，纯逻辑可测

### 学习成果检查

- [ ] 能不查资料写出一个带 3 个子命令的 Clap derive 骨架
- [ ] 能解释 `Done` 分支为什么需要块作用域（E0502）
- [ ] 能用 `cargo install --path .` 安装并在任意目录运行工具

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team

> 🎯 **下一步**: 完成 CLI 后，进入 [项目实战 2：Tauri 桌面笔记](./02-tauri-notes-app.md)，从终端走向图形界面。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
