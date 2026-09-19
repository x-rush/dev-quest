# Rust 生态基础：Tokio、Serde 与错误链验证

核验日期：2026-09-19。正文中的 10 个命名完整程序按原样抽取，使用 Rust 1.98.1 / Cargo 1.98.1、edition 2024 构建与运行。结果为 **10 / 10**；每个程序必须正常退出且标准输出完全匹配，程序内部同时断言正常与失败路径。

| 来源 | 程序 | 实际验证范围 |
|---|---|---|
| [Tokio](../../../../11-rust-cross-platform/reference/library-guides/12-tokio-guide.md) | `tokio-tasks` | 永不自行完成的任务取消、正常任务取值、阻塞任务结果 |
| 同上 | `tokio-channels` | mpsc 先排空再结束、oneshot 关闭、watch 最新值、broadcast 关闭 |
| 同上 | `tokio-reserve` | 取消等待容量时保留外部消息，继续发送并排空 |
| 同上 | `tokio-time` | 虚拟时间下的 timeout；不依赖主机调度快慢 |
| [Serde](../../../../11-rust-cross-platform/reference/library-guides/13-serde-guide.md) | `serde-fields` | 字段缺省、null、alias、重复字段、跳过与条件序列化 |
| 同上 | `serde-serialize` | 手写 Serialize 输出的 JSON |
| 同上 | `serde-visitor` | 忽略嵌套未知值，拒绝缺失、重复与类型错误 |
| 同上 | `serde-with` | 字符串格式往返，拒绝缺括号、多余分隔符、非法整数 |
| [错误处理库](../../../../11-rust-cross-platform/reference/library-guides/14-error-libraries.md) | `error-std` | Display、source、向下转换、链终止 |
| 同上 | `error-anyhow` | context、完整原因链、transparent 桥接与输入失败 |

正文修正了可直接导致错误行为的内容：mpsc 首次接收误判结束；把 oneshot 错误当作枚举；笼统称 send 取消不丢消息；Serde Visitor 未消费未知字段的值；把缺失坐标静默补成 0；`with` 解析留空且未导入 Point；声称 transparent anyhow 包装丢失 source；将 thiserror 枚举误当成 trait 对象。同时补充缺失/null、格式限制、运行时上下文和已完成任务取消等边界。

依赖清单来自正文的 TOML 围栏，验证器只加 Cargo 包声明，不修改 Rust 源码，不补 import、main 或缺失函数。锁文件固定直接和传递依赖：

- [Tokio 锁文件](rust-ecosystem-locks/tokio/Cargo.lock)：Tokio 1.53.0、tokio-stream 0.1.17。
- [Serde 锁文件](rust-ecosystem-locks/serde/Cargo.lock)：Serde 1.0.229、serde_json 1.0.145、toml 0.8.23。
- [错误库锁文件](rust-ecosystem-locks/errors/Cargo.lock)：thiserror 2.0.17、anyhow 1.0.100。
- [命令、源文件哈希与案例结果](rust-ecosystem-runtime.json)。文件哈希按当前工作树原始字节计算；跨平台换行可能改变文件哈希，代码围栏还单独记录统一换行后的代码哈希。

## 复现

从仓库根目录运行，主机需有 Rust 1.98.1 与 Python 3。也可在装有这些工具的临时容器内执行，工作目录与 Cargo 缓存独立于源码：

```bash
python3 shared-resources/tools/document-quality/verify_rust_ecosystem.py \
  --work /tmp/dev-quest-rust-ecosystem \
  --locks shared-resources/tools/document-quality/reports/rust-ecosystem-locks \
  --prepare
python3 shared-resources/tools/document-quality/verify_rust_ecosystem.py \
  --work /tmp/dev-quest-rust-ecosystem \
  --locks shared-resources/tools/document-quality/reports/rust-ecosystem-locks
```

第一步只允许下载锁定依赖；第二步强制 `cargo build --offline --locked --bins`。本次第二步使用 Docker `--network none --read-only --cap-drop ALL --pids-limit 256 --memory 1g --cpus 2`，源码只读挂载，构建结果和依赖缓存挂载到独立实验目录。

## 证据边界

10 个程序验证三篇中的命名完整示例；API 示意片段、TOML 往返、完整异步 I/O、所有 stream 适配器、负载调度、网络失败、Tauri/Axum 集成均不属于本报告的执行范围。锁文件含某依赖不等于该依赖的全部能力已经测试。取消程序使用 pending future 和明确分支顺序，只证明声明的取消情形，不证明任意线程竞争或阻塞任务都可及时取消。

技术契约对照：[Tokio Sender 取消](https://docs.rs/tokio/1.53.0/tokio/sync/mpsc/struct.Sender.html#cancel-safety)、[watch Receiver](https://docs.rs/tokio/1.53.0/tokio/sync/watch/struct.Receiver.html)、[Serde 字段属性](https://serde.rs/field-attrs.html)、[Serde 枚举表示](https://serde.rs/enum-representations.html)、[thiserror 文档](https://docs.rs/thiserror/2.0.17/thiserror/)。
