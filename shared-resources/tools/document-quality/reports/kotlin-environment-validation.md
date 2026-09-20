# Kotlin 环境 JVM 最小程序验证

本报告记录 [Android Studio 与 Kotlin 环境](../../../../05-kotlin-compose/basics/01-environment-setup.md) 中的 `verify:kotlin-environment-jvm` 正文。运行器从 Markdown 原样提取该 Kotlin 文件，在本仓已有 `dev-quest-validation:local` 容器中执行 `kotlinc` 编译和 JVM 运行。

它仅提供纯 Kotlin/JVM 的最小证据，不代表 Android Studio、Gradle、Android SDK、Jetpack Compose、模拟器、真机或 APK 已验证。

在仓库根目录复现：

```bash
python shared-resources/tools/document-quality/verify_kotlin_environment.py --report shared-resources/tools/document-quality/reports/kotlin-environment-validation.json
```
