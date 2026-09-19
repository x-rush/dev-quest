# Go、Rust、PHP 第十二轮：正文提取运行验证

只从三个 P1 核心基础/标准库页面中紧随具名标记的完整围栏逐字提取程序，写入临时目录后在无网络容器中运行。验证器不会补充 import、helper、stub 或替代实现。

| 语言 | 页面 | 具名案例 | 容器 | 结果 |
| --- | --- | --- | --- | --- |
| Go | `01-go-backend/reference/language-concepts/06-go-oop-concepts.md` | `go-pointer-method-set` | `golang:1.27` | PASS |
| Rust | `11-rust-cross-platform/reference/language-concepts/02-trait-objects.md` | `rust-dyn-collection` | `rust:1-slim-bookworm` | PASS |
| PHP | `07-php-mastery/reference/language-concepts/16-operators.md` | `php-precedence-remainder` | `php:8.5-cli` | PASS |

## 范围

通过只覆盖表中的三个完整程序及其精确标准输出：Go 指针接收者的方法集、Rust trait 对象异构集合与借用传参、PHP `and`/`&&` 赋值优先级和正模数下的余数规范化。它不验证整篇页面、编译失败教学步骤、网络、文件、框架、性能、并发或其他 PHP 版本行为。

JSON 同伴报告保留来源和提取代码的 SHA-256、容器命令、实际 stdout/stderr、退出码与镜像工具链版本。
