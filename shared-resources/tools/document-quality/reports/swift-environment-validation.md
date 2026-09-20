# Swift 环境最小程序验证

本报告记录 [Xcode 与 Swift 工具链](../../../../06-swift-swiftui/basics/01-environment-setup.md) 中的 `verify:swift-environment-toolchain` 正文。运行器从 Markdown 原样提取程序，在 `swift:6.3.3-noble` Linux 容器运行。

它仅证明这个纯 Swift 标准库程序能在该 Linux 工具链执行。它不证明 Xcode、macOS、iOS SDK、SwiftUI、SwiftData、模拟器、签名、真机或发布流程已经验证。

在仓库根目录复现：

```bash
python shared-resources/tools/document-quality/verify_swift_environment.py --report shared-resources/tools/document-quality/reports/swift-environment-validation.json
```
