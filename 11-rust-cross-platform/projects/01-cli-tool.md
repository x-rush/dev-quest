# 项目实战 1：rtask —— JSON 持久化 CLI 工具（Clap + anyhow）

## 分阶段练习与验收

**最小阶段**：先做内存任务的增查，再增加 JSON 文件持久化。

**验收结果**：无效命令非零退出，损坏 JSON 明确失败，重启后任务可读取。

**扩展顺序**：不要吞掉读取错误并覆盖旧数据；再考虑原子写入与并发。

下面四个 Rust 代码块按顺序组成同一个 `src/main.rs`，不要分别编译。先完成这个单进程项目，再增加锁或数据库；不要同时启动两个命令修改同一文件。

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

> 工程使用 edition 2024；实际工具链、锁定依赖和正文抽取验证结果见[Go/Rust 首项目验证报告](../../shared-resources/tools/document-quality/reports/go-rust-project-validation.md)。首次安装依赖需要网络，之后保留 `Cargo.lock` 并用 `--locked` 重现依赖选择。

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

运行 `cargo new rtask`、`cd rtask` 后编辑 `Cargo.toml`。下面的版本约束允许兼容更新；首次构建生成的 `Cargo.lock` 才记录实际精确版本，应随二进制项目提交：

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
tempfile = "3"
```

### 项目结构

本项目体量小，单文件 `src/main.rs` 即可；模块化拆分见扩展方向。

```
rtask/
├── Cargo.toml
├── Cargo.lock     # 首次 cargo build 后生成
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
use std::collections::HashSet;
use std::io::Write;
use std::path::{Path, PathBuf};

/// rtask —— 基于 JSON 文件的待办任务管理器
#[derive(Parser)]
#[command(name = "rtask", version, about)]
struct Cli {
    /// 任务存储文件路径（默认 ./rtask.json）
    #[arg(short, long, global = true, default_value = "rtask.json")]
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

- `#[derive(Parser)]`：入口结构体。`global = true` 让 `--file/-f` 同时在根命令和子命令可用，例如 `rtask --file x.json list` 与 `rtask list --file x.json`。
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
    let tasks: Vec<Task> = serde_json::from_str(&raw)
        .with_context(|| format!("解析 {} 失败", path.display()))?;
    validate_tasks(&tasks).with_context(|| format!("校验 {} 失败", path.display()))?;
    Ok(tasks)
}

fn save(path: &Path, tasks: &[Task]) -> Result<()> {
    let raw = serde_json::to_string_pretty(tasks).context("序列化任务失败")?;
    // 同目录临时文件确保替换时处于同一文件系统；失败时旧文件不被提前截断。
    let parent = path.parent().filter(|p| !p.as_os_str().is_empty()).unwrap_or(Path::new("."));
    let mut temp = tempfile::NamedTempFile::new_in(parent)
        .with_context(|| format!("在 {} 创建临时文件失败", parent.display()))?;
    temp.write_all(raw.as_bytes()).context("写临时文件失败")?;
    temp.as_file().sync_all().context("同步临时文件失败")?;
    temp.persist(path).with_context(|| format!("替换 {} 失败", path.display()))?;
    Ok(())
}

fn validate_tasks(tasks: &[Task]) -> Result<()> {
    let mut ids = HashSet::new();
    for task in tasks {
        if task.id == 0 || !ids.insert(task.id) {
            bail!("任务 ID 必须为非零且不重复的整数");
        }
        if task.text.trim().is_empty() {
            bail!("任务 #{} 的标题不能为空", task.id);
        }
    }
    Ok(())
}

fn next_id(tasks: &[Task]) -> Result<u32> {
    tasks.iter().map(|t| t.id).max().unwrap_or(0)
        .checked_add(1).context("任务 ID 已耗尽")
}
```

**关键点解析**：

- `with_context` 的闭包只在出错时构造消息，不应据此承诺整个调用“零开销”。
- 文件不存在返回空列表；其他读取错误、JSON 语法错误、重复 ID 和空标题都会失败。合法 JSON 也可能不满足业务约束。
- 打印路径用 `path.display()`，而非直接格式化 `Path`
- `checked_add` 将 ID 溢出变成可说明的错误，避免调试模式 panic、发布模式回绕。当前 ID 只保证在现有列表内唯一；删除最大 ID 后可能复用它。需要历史永久唯一 ID 时，持久化单独的递增序列或使用 UUID。
- 临时文件替换避免提前截断旧文件，但不是完整事务系统：没有并发锁，也没有跨平台的目录元数据同步保证。断电耐久性、权限继承和多进程一致性应作为下一阶段的专门需求。

### 步骤 3：业务逻辑（含一个借用检查教学点）

```rust
fn run(cli: &Cli) -> Result<()> {
    let mut tasks = load(&cli.file)?;
    match &cli.command {
        Commands::Add { text } => {
            let text = text.trim();
            if text.is_empty() {
                bail!("任务标题不能为空");
            }
            let id = next_id(&tasks)?;
            tasks.push(Task { id, text: text.to_owned(), done: false });
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
            // 复制要打印的文本，让 save 时不再需要 task 的可变借用。
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

- `Done` 分支：如果 `save(&tasks)` 后还要使用 `task`，两种借用会重叠，触发 E0502。Rust 的非词法生命周期通常可以在最后一次使用后结束借用，块并非必需；这里的块让读者容易看清借用边界。
- 应用入口可用 `anyhow` 保留上下文。库接口若要求调用者按错误种类处理，应暴露具体错误类型；可以手写 `Error`，也可以使用 thiserror，后者不是强制依赖。

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
        assert_eq!(next_id(&[]).unwrap(), 1);
    }

    #[test]
    fn next_id_follows_max() {
        assert_eq!(next_id(&[task(3, false), task(7, true)]).unwrap(), 8);
    }

    #[test]
    fn next_id_rejects_overflow() {
        assert!(next_id(&[task(u32::MAX, false)]).is_err());
    }

    #[test]
    fn storage_rejects_invalid_records() {
        assert!(validate_tasks(&[task(0, false)]).is_err());
        assert!(validate_tasks(&[task(1, false), task(1, true)]).is_err());
        assert!(validate_tasks(&[Task { id: 1, text: "  ".into(), done: false }]).is_err());
    }

    #[test]
    fn file_option_works_after_subcommand() {
        let cli = Cli::try_parse_from(["rtask", "list", "--file", "other.json"]).unwrap();
        assert_eq!(cli.file, PathBuf::from("other.json"));
    }

    #[test]
    fn invalid_input_preserves_original_file() {
        let dir = tempfile::tempdir().unwrap();
        let file = dir.path().join("tasks.json");
        save(&file, &[task(1, false)]).unwrap();
        let original = std::fs::read(&file).unwrap();
        assert!(run(&Cli { file: file.clone(), command: Commands::Add { text: "  ".into() } }).is_err());
        assert!(run(&Cli { file: file.clone(), command: Commands::Done { id: 99 } }).is_err());
        assert_eq!(std::fs::read(&file).unwrap(), original);
    }

    #[test]
    fn storage_roundtrip_and_corruption() {
        let dir = tempfile::tempdir().unwrap();
        let file = dir.path().join("tasks.json");
        assert!(load(&file).unwrap().is_empty());
        save(&file, &[task(1, false)]).unwrap();
        save(&file, &[task(1, true), task(2, false)]).unwrap();
        let tasks = load(&file).unwrap();
        assert_eq!(tasks.len(), 2);
        assert!(tasks[0].done);
        std::fs::write(&file, "{").unwrap();
        assert!(run(&Cli { file: file.clone(), command: Commands::Add { text: "valid".into() } }).is_err());
        assert_eq!(std::fs::read_to_string(&file).unwrap(), "{");
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
cargo test --locked      # 7 个单元测试
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

**本地安装**：编译 release 版并放入 Cargo 安装目录的 `bin`（通常为 `~/.cargo/bin`；请确认它在 PATH 中）：

```bash
cargo install --path . --locked
rtask list   # 从当前工作目录读取 rtask.json
```

**发布到 crates.io**（可选）：

从不同目录运行默认读取的是不同文件。需要共用任务时，显式传同一个 `--file` 绝对路径；安装可执行文件不会自动迁移数据。

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

**A**: 本例已经通过 `#[arg(global = true)]` 支持。去掉该属性才会让此选项只属于根命令。这个行为是 Clap 的参数作用域配置，不是 POSIX 对所有 CLI 的强制规定。见 [Clap global 参数](https://docs.rs/clap/latest/clap/struct.Arg.html#method.global)。

### Q2: JSON 文件被手工改坏了怎么办？

**A**: 保留原文件，先备份再修复。解析失败会非零退出，`add` 不会覆盖坏文件；业务校验也拒绝重复 ID。写入采用同目录临时文件与替换，相关保证和限制见 [NamedTempFile::persist](https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html#method.persist)。原子替换不能修复已经损坏的数据，也不能阻止两个进程相互覆盖。

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
- [ ] 能解释 `Done` 分支的借用何时结束，以及为什么块作用域不是唯一解法
- [ ] 能用 `cargo install --path .` 安装并在任意目录运行工具

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team

> 🎯 **下一步**: 完成 CLI 后，进入 [项目实战 2：Tauri 桌面笔记](./02-tauri-notes-app.md)，从终端走向图形界面。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
