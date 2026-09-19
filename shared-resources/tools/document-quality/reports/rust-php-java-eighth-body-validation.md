# Rust / PHP / Java P1 正文提取验证

本报告只记录三个在选择时 `primary state=not_verified` 的 P1 基础或标准库页面。每个案例都是从文档中“正文提取验证”标题后的完整语言围栏直接抽取，原样送入隔离容器工具链；结果不能外推为整页、框架、部署或外部服务验证。

| 模块 | 页面 | 抽取案例 | 工具链 | 结果 |
| --- | --- | --- | --- | --- |
| PHP | `07-php-mastery/reference/language-concepts/04-control-flow.md` | `match` 严格比较与未命中 | `php:8.5-cli-alpine` | PASS：`integer|unmatched` |
| Java | `08-java-revisited/reference/library-guides/05-java-util-function.md` | Function 组合顺序与 Predicate 短路 | `eclipse-temurin:21-jdk-noble` | PASS：`11`、`12`、`false|0` |
| Rust | `11-rust-cross-platform/reference/language-concepts/01-ownership-dictionary.md` | `&mut` 重新借用与字段析构顺序 | `rust:1-slim-bookworm`（edition 2024） | PASS：`ok!?`，随后 `pair first second` |

运行时还出现一条 Rust `dead_code` 警告，指出 `Pair` 的两个字段未被读取；它不影响该案例以析构行为为目的的断言。完整命令、文档 SHA-256、stdout/stderr、退出码和断言见同名 [JSON](./rust-php-java-eighth-body-validation.json)。
