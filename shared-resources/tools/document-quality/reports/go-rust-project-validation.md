# Go / Rust 首项目与 Rust 标准库正文运行验证

本报告只覆盖以下 4 篇正文。源码由[验证器](../verify_go_rust_projects.py)直接抽取，未自动补 import、stub、函数或业务实现。Rust CLI 的 4 个连续代码块按正文要求拼接为同一个 `src/main.rs`；Go 的两个代码块分别保存为程序与测试。验证环境：Linux、Go 1.27.1、Rust/Cargo 1.98.1、edition 2024。

| 正文 | 已执行的验收 |
|---|---|
| [Go 标准库待办 CLI](../../../../01-go-backend/projects/00-stdlib-todo-cli.md) | `go mod init`、构建、5 个单元测试；添加、demo、空标题与多余参数的实际进程输出/退出码 |
| [Rust JSON CLI](../../../../11-rust-cross-platform/projects/01-cli-tool.md) | 实装依赖后离线构建；7 个单元测试；跨进程增查改删、空标题、未知 ID、损坏 JSON、重复 ID、ID 溢出、全局文件选项、非法数字退出码 |
| [Rust 标准库地图](../../../../11-rust-cross-platform/reference/library-guides/15-standard-library-map.md) | 正常/空文件的精确计数；无参数、多参数、文件不存在、非法 UTF-8 的失败退出且不输出假计数 |
| [Rust 标准类型](../../../../11-rust-cross-platform/reference/language-concepts/10-standard-types-and-methods.md) | 完整程序精确输出；4 个测试验证原始顺序、空输入、非法整数和越界 |

结果：35 条命令符合预期，其中包括工具链版本查询、编译与测试命令；这不是“35 个项目”。单元测试共 16 个，独立程序行为调用共 24 次。预期失败案例的非零退出被明确断言，损坏数据/无效修改还验证原文件内容未变化。

[完整机器证据](go-rust-project-validation.json)保留每篇正文 SHA-256、命令、标准输出、标准错误和退出码；[本次 Cargo.lock](go-rust-project-Cargo.lock)保留传递依赖与校验和。直接依赖实际解析为 Clap 4.6.7、Serde 1.0.229、serde_json 1.0.151、anyhow 1.0.104、tempfile 3.27.0。版本约束与精确锁定不是同一件事。

## 已修复的问题

Go 首项目原步骤在新目录缺少模块初始化，`go test ./...` 与 `go run .` 无法按说明直接执行；现补齐 `go mod init`。`demo extra` 原先悄悄忽略额外参数，现明确失败，测试同时覆盖输出设备错误传播。

Rust CLI 原先接受空标题、可能发生整数溢出、接受重复/零 ID 持久化数据，并直接覆盖目标文件。现在输入先校验、ID 使用 checked_add、加载时验证记录约束，写入先完成同目录临时文件并同步文件，再替换目标。还修正了 Clap 全局选项的前后位置说明，以及“必须使用块作用域才能结束借用”的误导。初学者可以通过 7 个测试看到这些边界实际如何表现。

## 复现

验证器需要 `python3`、`go`、`cargo`、`rustc` 与系统 C 链接器可用。可在 Linux/WSL 的对应工具链环境执行；路径必须指向专用的构建目录：

```bash
# 仓库根目录；prepare 只解析/下载依赖，不执行正文程序。
python3 shared-resources/tools/document-quality/verify_go_rust_projects.py \
  --work /tmp/dev-quest-go-rust \
  --lockfile shared-resources/tools/document-quality/reports/go-rust-project-Cargo.lock \
  --prepare

# 保留前一步的构建目录与 Cargo 缓存；所有 cargo 构建强制 --offline --locked。
python3 shared-resources/tools/document-quality/verify_go_rust_projects.py \
  --work /tmp/dev-quest-go-rust
```

本次使用现有 `dev-quest-validation:local` 工具链镜像，下载阶段和运行阶段分开。运行阶段网络禁用、根文件系统只读、capabilities 全部移除；仓库只读挂载。输出和编译缓存写入专用实验目录。`/tmp` 需要允许执行 Go 临时测试二进制；禁止执行的 tmpfs 会导致环境层的 `permission denied`，不能判正文有错。

## 证据边界

本次没有执行 Windows/macOS、Tauri 或 Axum 工程。Rust CLI 为单进程教学工具：临时文件替换不提供多进程事务、历史 ID 永不复用、权限继承或断电后的目录耐久性保证。没有测试掉电、磁盘耗尽或操作系统权限故障注入；不把普通文件测试当作这些保证。Go CLI 只在当前进程保存状态，明确不持久化。

官方契约：[Clap global 参数](https://docs.rs/clap/latest/clap/struct.Arg.html#method.global)、[tempfile persist](https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html#method.persist)、[Rust checked_add](https://doc.rust-lang.org/std/primitive.u32.html#method.checked_add)、[Rust BufRead](https://doc.rust-lang.org/std/io/trait.BufRead.html)。
