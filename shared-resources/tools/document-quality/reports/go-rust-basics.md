# Go 并发、错误处理与 Rust 生命周期验证

2026-09-19，Linux x86_64，Go 1.27.1、Rust 1.98.1 / edition 2024。验证器从下列三篇正文的 `verified-case` 标记直接抽取程序，不补 import、不包 main、不改源代码。结果：**16 / 16 通过**，其中 13 个完整程序运行通过、3 个 Rust 反例按预期编译失败。

| 来源 | 命名案例 | 本次证明的范围 |
|---|---|---|
| [Go 并发基础](../../../../01-go-backend/basics/07-concurrency-basics.md) | `go-concurrency-results`、`go-concurrency-channel`、`go-concurrency-cancel`、`go-concurrency-mutex` | 并发结果汇集、关闭后的接收、nil channel 的 default 分支、取消后实际退出、Mutex 与 atomic 计数；全部开启 race 检测 |
| [Go 错误处理](../../../../01-go-backend/basics/08-error-handling.md) | `go-errors-contract`、`go-errors-typed-nil`、`go-errors-cleanup`、`go-errors-recover`、`go-errors-http` | Is/As/Join/Unwrap、typed nil、写入与关闭双错误、已知 panic 转 error/未知 panic 重抛、400/200/404/500 响应 |
| [Rust 高级生命周期](../../../../11-rust-cross-platform/reference/language-concepts/04-advanced-lifetimes.md) | `rust-lifetime-nll`、`rust-lifetime-covariance`、`rust-lifetime-hrtb`、`rust-lifetime-static` | NLL 与方法省略、共享引用与容器、HRTB 和带类型上下文的闭包、String 满足 static 约束 |
| 同上 | `rust-lifetime-dangling`、`rust-lifetime-elision`、`rust-lifetime-owned-borrow` | 编译器分别报告 E0597、E0106、E0597；拥有 Vec 不代表内部引用满足 static |

## 验证方式

[验证器](../verify_go_rust_basics.py)要求恰好 4、5、7 个标记案例；两篇 Go 文档的所有 Go 围栏都必须属于命名案例。每项在独立临时目录编译。正常程序必须退出 0、标准错误为空，标准输出必须逐字匹配紧随程序的 `text` 围栏。Go 统一使用 `go build -race`；Rust 失败例解析 rustc JSON 诊断，要求非零退出并包含指定错误码。

[原始 JSON 证据](go-rust-basics.json)保存每个来源、正文行号、规范化正文 SHA-256、代码 SHA-256、工具链、构建命令与输出、执行命令与输出。哈希用于发现正文或代码变动；改动后应重新执行，不能继续把旧记录当作新正文证据。

本机已有 `dev-quest-validation:local` 多语言工具镜像。仓库根目录下可用 PowerShell 复现：

```powershell
docker run --rm --network none --read-only `
  --tmpfs /tmp:rw,exec,nosuid,size=1536m `
  --cap-drop ALL --pids-limit 256 --memory 2g --cpus 2 `
  -e GOCACHE=/tmp/go-cache -e HOME=/tmp `
  -v "${PWD}:/source:ro" `
  -v "${PWD}/shared-resources/tools/document-quality/reports:/reports:rw" `
  dev-quest-validation:local `
  python3 /source/shared-resources/tools/document-quality/verify_go_rust_basics.py `
  --report /reports/go-rust-basics.json
```

该镜像是本地工具环境，不是远程公开发布的镜像。其他机器需准备 Linux、Python 3.10+、Go 1.27.1、Rust 1.98.1 和 Go race 所需 C 编译器，再在隔离环境执行同一验证器。无需第三方 Go/Rust 依赖，也不需要外网访问。

## 本次发现并修正的问题

- Go 原超时示例在前台超时后遗留无接收者的后台发送，现改为传播 context 并等待退出；修正“无配对收发必然立即全局死锁”“select 防止饥饿”等过度保证。
- Go 循环变量说明补充模块语言版本和 `:=`/`=` 的差别；说明 `sync.Once` 无法阻止发送与关闭竞争。
- Go 错误处理移除错误的 `sql.Open` 签名和“缺请求参数应 panic”示例，补错误树、typed nil、Close 失败和已提交 HTTP 响应无法撤销等边界。
- Rust 示例一原称三行输出，实际为两行；修正“所有 owned 值满足 static”“两个输入引用必需显式生命周期”“move 能修复借用返回”等误导，增加拥有 Vec 仍携带短借用的编译反例。

## 边界

这些记录只覆盖列出的案例和环境。race 检测没有覆盖所有调度与未执行路径；HTTP 使用 ResponseRecorder，没有进行真实网络服务、认证或数据库集成测试；资源清理使用故障写入器验证契约，没有模拟磁盘断电或文件系统持久化；Rust 的结构体签名片段、错误码速查表其他条目及练习不属于完整运行案例。生命周期规则另对照了 [Rust Reference](https://doc.rust-lang.org/reference/lifetime-elision.html) 与 [Rust By Example](https://doc.rust-lang.org/rust-by-example/scope/lifetime/static_lifetime.html)，Go 契约对照 [errors](https://pkg.go.dev/errors) 与 [sync](https://pkg.go.dev/sync)。
