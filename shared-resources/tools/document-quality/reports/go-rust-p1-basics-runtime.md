# Go / Rust P1 基础正文运行验证

Three standalone Go programs and one Rust test module extracted verbatim from the named pages. No whole-document, benchmark, panic, network, or external-service claim is made.

| 来源 | 正文完整提取项 | 状态 | 断言 |
|---|---|---|---|
| `01-go-backend/basics/03-variables-constants.md` | `zero-values` | `blocked` | stdout contains 'string零值: "" (长度: 0)' |
| `01-go-backend/basics/03-variables-constants.md` | `iota` | `passed` | stdout contains 'GB: 1073741824' |
| `01-go-backend/basics/03-variables-constants.md` | `circle-calculation` | `passed` | stdout contains '面积(整数部分): 78' |
| `11-rust-cross-platform/basics/06-collections-iterators.md` | `normalize-unit-tests` | `passed` | stdout contains '2 passed' |

JSON 报告保留精确命令、退出码和 stdout/stderr；`passed` 仅表示表中命名提取项通过。
