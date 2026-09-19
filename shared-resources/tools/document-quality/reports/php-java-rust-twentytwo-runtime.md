# PHP / Java / Rust 第二十二轮正文提取运行验证

三个案例均来自选择时处于 `not_verified` 状态的 P1 核心页。验证器只从具名标记后提取唯一的完整围栏，不会补充 import、辅助函数、替代实现或测试桩。

| 具名程序 | 来源 | 隔离工具链 | 结果 |
| --- | --- | --- | --- |
| `php-reflection-repeatable-route` | `07-php-mastery/reference/language-concepts/08-reflection-attributes.md` | `php:8.5-cli-alpine` | PASS |
| `java-sealed-record-exhaustive-switch` | `08-java-revisited/reference/language-concepts/05-records-sealed-patterns.md` | `eclipse-temurin:21-jdk-noble` | PASS |
| `rust-enum-exhaustive-message` | `11-rust-cross-platform/basics/03-structs-enums-patterns.md` | `rust:1-slim-bookworm` | PASS |

容器均使用已存在镜像（`--pull=never`）、禁用网络、只读根文件系统、移除 Linux capabilities、`no-new-privileges`、CPU/内存/PID 限制和仅 `/tmp` 的 tmpfs 工作区。精确命令、来源与代码 SHA-256、stdout/stderr、退出码见同名 JSON。

本证据只覆盖表中三个命名程序及其列出的输出契约：不覆盖页面其他围栏或文字，也不覆盖框架、HTTP、文件系统、并发、性能、Miri/sanitizer、外部依赖或完整项目。
