# Java 环境最小程序验证

本报告仅记录 [环境搭建](../../../../08-java-revisited/basics/01-environment-setup.md) 中标记为 `verify:java-environment-hello` 的完整 `Hello.java` 正文。运行器原样提取该代码块，在 `eclipse-temurin:21-jdk` 容器执行 `javac --release 21 -encoding UTF-8 Hello.java && java Hello`，预期标准输出为 `42`。

它证明的是 Java 21 的这一个最小编译与运行路径。它不证明读者主机的 PATH、SDKMAN、IDE 设置、Maven、Gradle、JDK 25、依赖下载或任何项目工程已经可用。

在仓库根目录复现：

```bash
python shared-resources/tools/document-quality/verify_java_environment.py --report shared-resources/tools/document-quality/reports/java-environment-validation.json
```
