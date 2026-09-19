# Go/Rust P1 参考页正文提取验证

本报告刻意只覆盖本轮此前没有命名运行证据的 P1 参考页：Go 内置函数与 Go 标准库。关键字页和两篇 Rust 标准库页已有独立的命名运行证据，未在这里重复执行。

验证器从 HTML 标记后紧邻的 Markdown 围栏中逐字提取 Go 源码；不会补充 import、函数或 stub。每个程序在独立临时目录运行，精确比较 stdout 和退出码。
验证工具链：`go version go1.27.1 windows/amd64`。

| 正文 | 标记 | 结果 |
| --- | --- | --- |
| [01-go-backend/reference/language-concepts/02-go-built-in-functions.md](../../../../01-go-backend/reference/language-concepts/02-go-built-in-functions.md) | `builtin-panic-recover` | PASS |
| [01-go-backend/reference/library-guides/01-go-standard-library.md](../../../../01-go-backend/reference/library-guides/01-go-standard-library.md) | `stdlib-parse-json` | PASS |

结果：2/2 个正文程序通过。
[完整机器可读证据](go-rust-p1-page-validation.json)保存正文与代码 SHA-256、命令、stdout、stderr 和退出码。

## 限定范围

这不是全库代码块覆盖率报告，也不验证网络、数据库、文件系统故障、不同 Go 版本或 Rust 工具链。Go 标准库样本仅验证 strconv 和 encoding/json 的值与错误路径；内置函数样本仅验证 panic/recover 的同 goroutine 边界。
