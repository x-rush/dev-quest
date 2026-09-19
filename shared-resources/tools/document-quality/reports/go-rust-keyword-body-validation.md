# Go / Rust 关键词正文提取验证

Only the extracted Go package/import program and Rust keyword task program are verified. Other fences, prose, compiler-error exercises, OS behavior, dependencies, and performance claims are out of scope.

| 文档 | 提取项 | 容器镜像 | 状态 | 断言 |
|---|---|---|---|---|
| `01-go-backend/reference/language-concepts/01-go-keywords.md` | `go-keyword-package` | `golang:1` | `passed` | stdout 与完整预期逐字一致 |
| `11-rust-cross-platform/reference/language-concepts/09-keywords-and-syntax.md` | `rust-keyword-task` | `rust:1-slim-bookworm` | `passed` | stdout 与完整预期逐字一致 |

JSON 报告保存每个容器命令、退出码、stdout/stderr 和提取内容哈希；通过只说明表内这两个命名正文程序。
