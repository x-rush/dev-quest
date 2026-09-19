# PHP / Java / Rust 第二十轮正文提取运行验证

Twentieth-round runtime evidence for three named P1 PHP, Java, and Rust core or standard-library body programs.

| 具名程序 | 来源 | 隔离工具链 | 结果 |
| --- | --- | --- | --- |
| `php-magic-isset-get` | `07-php-mastery/reference/language-concepts/17-magic-methods.md` | `php:8.5-cli-alpine` | PASS |
| `java-annotation-inherited-runtime` | `08-java-revisited/reference/language-concepts/09-annotations.md` | `eclipse-temurin:21-jdk-noble` | PASS |
| `rust-unsafe-split-at-mut` | `11-rust-cross-platform/reference/language-concepts/06-unsafe.md` | `rust:1-slim-bookworm` | PASS |

验证器只原样提取表中唯一具名完整围栏，并断言精确 stdout、空 stderr 和零退出码。JSON 记录文档与提取程序 SHA-256、完整 Docker 命令、退出码及输出。隔离限制和未覆盖范围见 JSON 的 `isolation` 与 `scope`。
