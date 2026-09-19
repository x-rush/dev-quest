# Go / PHP / Java P1 第九轮正文提取验证

Three named P1 core/standard-library Markdown programs (one each for Go, PHP, and Java) extracted unchanged from pages that had no runtime-evidence marker. Portable language/library behavior only.

| Case | Source | Runtime image | Result |
| --- | --- | --- | --- |
| `go-slice-full-expression` | `01-go-backend/reference/language-concepts/10-slice-semantics.md` | `golang:1.27` | PASS |
| `php-strict-search-and-match` | `07-php-mastery/reference/language-concepts/13-weak-comparison.md` | `php:8.5-cli` | PASS |
| `java-string-pool-and-content` | `08-java-revisited/reference/language-concepts/07-string-immutability-pool.md` | `eclipse-temurin:21-jdk` | PASS |

## 执行边界

Docker network disabled; read-only root filesystem and source mount; only /tmp is writable. This does not validate whole documents, frameworks, servers, databases, browsers, devices, or platform integrations.

JSON 限定报告保存源码 SHA-256、预期与实际标准输出、完整命令、标准错误、退出码和逐项断言。
