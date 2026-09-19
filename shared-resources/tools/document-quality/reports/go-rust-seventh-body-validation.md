# Go / Rust P1 第七轮正文提取验证

本报告只验证表中四个新命名的 Go Markdown 正文程序。它不声称整页、其他围栏、Rust 页面、网络服务、竞态、性能或不同工具链已经验证。

每项从 HTML 标记后紧邻的 Go 围栏逐字提取，写入独立临时目录，并以精确 stdout 和零退出码断言。验证不会补充 import、helper 或 stub。

| 类别 | 正文 | 标记 | 结果 |
| --- | --- | --- | --- |
| 关键词 | `01-go-backend/reference/language-concepts/01-go-keywords.md` | `keyword-decisions-seventh` | PASS |
| 内置函数 | `01-go-backend/reference/language-concepts/02-go-built-in-functions.md` | `builtin-append-copy-seventh` | PASS |
| 标准库 | `01-go-backend/reference/library-guides/05-context.md` | `context-cancellation-seventh` | PASS |
| 核心基础 | `01-go-backend/reference/language-concepts/04-go-data-types.md` | `data-type-value-copy-seventh` | PASS |

结果：4/4 个命名正文程序通过。
JSON 报告保留文档及提取源码哈希、Go 工具链、命令、退出码、stdout 和 stderr；通过只适用于表中程序。
