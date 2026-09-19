# Go、Rust、Node.js P1 正文限定运行验证

结果：**3/3 passed**。

## 范围

Three named, complete fenced programs extracted unchanged from currently not_verified P1 Go, Rust, and Node.js pages. Go runs with the repository toolchain; Rust and Node run in existing local Docker images with network disabled, read-only roots, dropped capabilities, bounded CPU/memory/processes, and a read-only input mount. This does not verify other snippets, prose, network, filesystem, platform, framework, or production-security behavior.

## 结果

| ID | 页面 | 运行时 | 退出码 | 状态 |
| --- | --- | --- | ---: | --- |
| `go-nil-semantics` | `01-go-backend/reference/language-concepts/15-nil-semantics.md` | `go version go1.27.1 windows/amd64` | 0 | PASS |
| `rust-ownership-move-clone-copy` | `11-rust-cross-platform/basics/02-ownership-borrowing.md` | `rustc 1.98.1 (48a229cea 2026-09-01)` | 0 | PASS |
| `node-crypto-aes-gcm-round-trip` | `09-nodejs-backend/reference/library-guides/03-crypto.md` | `v24.21.0` | 0 | PASS |

JSON 报告保留完整命令、源码与提取程序的 SHA-256、期望/实际 stdout、stderr 及工具链版本。`PASS` 只表示该表列出的正文完整程序通过。
