# 环境搭建 - JDK 与现代工具链

## 先理解，再动手

JDK 提供编译器与运行时，Maven/Gradle 描述依赖和构建过程。IDE 配置的 JDK 与终端的 JDK 可能不同。

**本节自测**：在终端记录 java 与 javac 版本，运行模板程序，再比对 IDE 设置。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

出现 class version 错误时先检查编译与运行版本，不先修改业务代码。

</details>

> **文档简介**: 在 Linux、macOS 或 WSL 中用 SDKMAN 安装与切换 JDK，配置 Maven/Gradle 与 IDE，完成可复现的 Java 开发环境
>
> **目标读者**: 有旧版 Java 经验、需要更新到现代 Java 工具链的开发者
>
> **前置知识**: 基本命令行操作经验

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#环境搭建` `#JDK` `#SDKMAN` `#Maven` `#Gradle` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：
- 用 SDKMAN 安装并切换多个 JDK；能区分项目要求的 Java 版本与供应商发行版
- 了解主流 JDK 发行版的差异并做出合理选择
- 安装 Maven 与 Gradle，理解构建 Wrapper 的作用
- 完成 IntelliJ IDEA 或 VS Code 的 Java 开发配置

## 🔄 旧回顾：环境管理方式的变化

**旧写法（Java 8 时代）**：
1. 官网下载安装包，双击安装
2. 手动设置 `JAVA_HOME` 与 `PATH`
3. 切换版本 = 手改环境变量 + 重开终端

**现代做法（当前 LTS 时代）**：
1. `sdk install java` 一条命令完成安装
2. `sdk use` / `sdk default` 秒级切换版本
3. 项目通过构建 Wrapper（`mvnw`/`gradlew`）锁定工具版本，本地与 CI 天然一致

## ☕ 第一步：安装 SDKMAN 与 JDK

### 1. 为什么选 SDKMAN

- 一条命令安装 JDK、Maven、Gradle 等 JVM 生态工具
- 多版本并存、按需切换，告别 `JAVA_HOME` 手工管理
- 跨平台（Linux/macOS/WSL），脚本可固化到安装文档

### 2. 安装 SDKMAN

```bash
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk version   # 打印版本号即安装成功
```

### 3. 查看、选择与安装 JDK

JDK 的**主版本**决定语言和标准库能力；`-tem` 这类**供应商后缀**决定二进制发行方。先读项目的 `pom.xml`、`build.gradle(.kts)` 或团队约定：项目要求 Java 21 时，即使机器已有 Java 25，也先安装并使用 21。Java 21 与 Java 25 都是 LTS 线；具体可下载的补丁号会随时间变化，不能把本文写死的补丁号当作永久命令。[Adoptium 的支持页](https://adoptium.net/support/)列出 Temurin 的当前支持线；[SDKMAN 的候选版本页](https://sdkman.io/sdks/)才是执行安装前应查看的实际列表。

```bash
# 列出所有可用 JDK（供应商 + 版本号）
sdk list java

# 从刚才的列表复制一个当前可用的 Temurin 21 标识，例如 21.x.y-tem；
# 尖括号是需要替换的占位符，不能原样执行。
sdk install java <21.x.y-tem>

# 只有要体验新特性或项目明确要求时，才另装列表中的 Java 25 LTS。
sdk install java <25.x.y-tem>

# 切换：use 只影响当前终端，default 影响全局
sdk use java <21.x.y-tem>
sdk default java <21.x.y-tem>
```

如果你只需要最新的默认 Java，SDKMAN 也支持 `sdk install java`。教学或团队项目中通常应显式复制项目要求的版本标识，因为“默认版本”会随 SDKMAN 的候选列表变化。

### 4. 验证安装

```bash
java --version
# 版本、供应商与构建号；应与刚才选择的主版本相符

javac --version
# 编译器主版本；例如 21.x.y
```

### 5. 最小编译与运行验收

版本命令只能证明可执行文件在 PATH 中。新建 `Hello.java` 后实际编译并运行，才能确认编译器与运行时配套：

```java verify:java-environment-hello
public class Hello {
    public static void main(String[] args) {
        System.out.println(42);
    }
}
```

```bash
javac Hello.java
java Hello
# 42
```

本仓于 2026-09-20 在 `eclipse-temurin:21-jdk` 容器用这段完整程序得到输出 `42`；运行时为 Temurin 21.0.12 LTS。该证据只覆盖 Java 21 的最小编译与运行，不覆盖 SDKMAN、IDE、Maven、Gradle 或 JDK 25。

## 📦 第二步：选择 JDK 发行版

| 发行版 | 维护方 | 适用场景 |
|--------|--------|---------|
| Eclipse Temurin | Adoptium | 通用学习与服务器开发；有公开的 LTS 发布与支持信息 |
| Amazon Corretto | AWS | 已在 AWS 或其支持体系中运行，并希望统一 JDK 来源 |
| Azul Zulu | Azul | 需要其平台覆盖或商业支持选项时 |
| Oracle JDK | Oracle | 组织已有 Oracle 支持或许可安排时 |
| GraalVM | Oracle | 确认要研究 Native Image 或特定运行时能力时；先核对目标项目要求 |

> 💡 个人学习可从 Temurin 开始。不要因为供应商名称不同就假定行为必然一致：先锁定项目使用的 Java 主版本，再阅读该项目对发行版、许可证、容器镜像和 Native Image 的要求。基础 Java 语法和标准库学习通常不依赖特定供应商。

## 🛠️ 第三步：安装构建工具

### Maven

```bash
sdk install maven
mvn -v   # 确认 Maven 及其绑定的 JDK
```

### Gradle

```bash
sdk install gradle
gradle --version
```

### 构建 Wrapper：项目的版本锁

```bash
# 在 Maven 项目根目录生成 wrapper
mvn wrapper:wrapper

# 在 Gradle 项目根目录生成 wrapper
gradle wrapper
```

生成 `mvnw`/`gradlew` 脚本后，协作者无需预装构建工具——脚本会按项目声明的版本自动下载。**把 wrapper 提交进版本库**是现代 Java 项目的标准做法。

## 🖥️ 第四步：配置 IDE

### IntelliJ IDEA（推荐）

- Community 版免费，完整覆盖 Java + Maven/Gradle 开发
- 首次打开项目时选择 SDKMAN 安装的 JDK（File → Project Structure → SDK）
- 对现代特性支持完善：record/sealed/模式匹配补全、虚拟线程调试均可用

### VS Code（轻量选择）

- 安装 "Extension Pack for Java" 扩展包
- SDKMAN 安装的 JDK 通常会被自动识别，无需手工配置

## ✅ 环境检查清单

```bash
java --version          # 输出 21 或 25
mvn -v                  # 或 ./mvnw -v
gradle --version        # 或 ./gradlew --version
echo $JAVA_HOME         # SDKMAN 环境下自动指向当前 JDK
```

四条命令都能正常输出，环境即就绪。

## ❓ 常见问题

**Q: 还需要手动设置 JAVA_HOME 吗？**
A: SDKMAN 会自动管理。仅当 IDE 或某些工具找不到 JDK 时，将其指向 `~/.sdkman/candidates/java/current`。

**Q: 不同项目需要不同 JDK 版本怎么办？**
A: SDKMAN 负责安装多个版本；Maven/Gradle 通过 toolchain 或 wrapper 按项目声明选择 JDK，互不干扰。

**Q: Windows 用户怎么办？**
A: 推荐 WSL2 + SDKMAN；纯 Windows 可用 winget 安装 Temurin，步骤思路相同。

## 🎯 练习与实践

### 练习一：多版本切换
1. 用 SDKMAN 安装 21 与 25 两个 LTS JDK
2. 用 `sdk use` 在两个版本间切换，分别运行 `java --version` 记录差异

### 练习二：Wrapper 实践
1. 在任意空目录生成 Maven wrapper，观察新增了哪些文件
2. `sdk uninstall maven` 后验证 `./mvnw -v` 仍能正常工作

## 🔗 相关文档

- 📄 **[第一个程序](./02-first-program.md)** - 环境就绪后，编写并运行第一个程序
- 📄 **[现代 Java 速查](../reference/quick-references/01-java-cheatsheet.md)** - 常用工具与代码一行式速查
- 📄 **[模块总览](../README.md)** - 了解本模块的整体学习路径


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
