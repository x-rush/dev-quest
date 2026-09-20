# Rust 环境 Cargo 最小程序验证

本报告记录 [Rust 环境搭建](../../../../11-rust-cross-platform/basics/01-environment-setup.md) 的 `verify:rust-environment-cargo` 正文。运行器从 Markdown 原样提取代码，生成一个 `edition = "2024"`、没有第三方依赖的 Cargo 项目，在无网络容器中执行 `cargo check`、`cargo run` 和 `cargo test`。

它只覆盖该离线 Cargo 基础闭环，不证明 rustup、读者主机、第三方 crate、交叉编译、平台链接器、网络镜像或发布可用。

```bash
python shared-resources/tools/document-quality/verify_rust_environment.py --report shared-resources/tools/document-quality/reports/rust-environment-validation.json
```
