# Rust 生命周期基础页限定验证

只验证正文中两个具名 Rust 围栏：一个运行输出契约与一个 `E0515` 编译失败契约；不代表整页或整个 Rust 模块已完成验证。

| 页面 | 示例 | 类型 | 结果 |
|---|---|---|---|
| [11-rust-cross-platform/basics/07-lifetimes.md](../../../../11-rust-cross-platform/basics/07-lifetimes.md) | `rust-lifetime-borrowed-and-owned` | runtime | PASS |
| [11-rust-cross-platform/basics/07-lifetimes.md](../../../../11-rust-cross-platform/basics/07-lifetimes.md) | `rust-lifetime-local-reference` | compile_fail_contract | PASS |

隔离条件、源码哈希、编译器输出与完整诊断见同名 JSON 报告。
