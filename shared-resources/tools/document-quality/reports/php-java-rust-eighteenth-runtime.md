# PHP / Java / Rust 第十八轮正文提取运行验证

Three named, complete PHP/Java/Rust P1 core or standard-library Markdown programs are extracted unchanged and run with exact stdout assertions.

| Case | Source | Runtime | Result |
| --- | --- | --- | --- |
| `php-session-write-close` | `07-php-mastery/reference/library-guides/06-http-session-cookie.md` | `php:8.5-cli-alpine` | PASS |
| `java-jpms-module-map` | `08-java-revisited/reference/library-guides/09-jdk-package-map.md` | `eclipse-temurin:21-jdk-noble` | PASS |
| `rust-arc-weak-lifecycle` | `11-rust-cross-platform/reference/language-concepts/07-smart-pointers.md` | `rust:1-slim-bookworm` | PASS |

## 边界

只验证表中唯一具名围栏的原样提取、隔离执行和精确输出。PHP 覆盖隔离文件会话的写入和关闭，不覆盖 HTTP 或浏览器；Java 覆盖类到 JPMS 模块的反查，不覆盖命名模块构建；Rust 覆盖 Arc/Weak 生命周期，不覆盖线程调度或性能。JSON 报告保留来源和程序 SHA-256、完整容器命令、退出码及 stdout/stderr。
