# 第一个程序 - 从 javac 到现代工作流

## 先理解，再动手

源码先被编译为字节码，再由 JVM 执行。main 是程序入口，类名、文件名与包路径共同影响工具如何找到入口。

**本节自测**：修改输出后先只运行旧 class，再重新编译运行。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

能解释为何未重新编译可能看到旧输出；IDE 自动构建隐藏了这一步，不代表它不存在。

</details>

> **文档简介**: 体验 Java 程序从经典 javac 编译，到单文件直跑、JShell 交互探索、Maven/Gradle 工程化的完整演进
>
> **目标读者**: 有旧版 Java 经验，想快速掌握现代 Java 编译运行方式的学习者
>
> **前置知识**: 已完成[环境搭建](./01-environment-setup.md)，JDK 21+ 可用

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#HelloWorld` `#javac` `#JShell` `#Maven` `#Gradle` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：
- 用三种方式运行 Hello World：javac+java、单文件直跑、Java 25 紧凑源文件
- 使用 JShell 交互式探索 Java 语法
- 创建并运行第一个 Maven 与 Gradle 项目

## 🔄 旧回顾：Hello World 的三次进化

### 写法一：经典写法（Java 1.0 至今有效）

下面是本页的基线程序。它只使用 JDK 21 也支持的语法，因此可用来区分“经典编译运行闭环已通”与后文需要 JDK 25 的紧凑源文件。

<!-- reference-case: {"id":"java-first-program-classic","stdout":"Hello, Java!\n","requires":"JDK 21"} -->
```java
// Hello.java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, Java!");
    }
}
```

```bash
javac Hello.java   # 生成 Hello.class
java Hello         # 运行
```

要点回顾：文件名必须与 public 类名一致；JVM 入口是 `public static void main(String[] args)`。本例的可观察结果固定为 `Hello, Java!`；修改源码后必须重新执行 `javac Hello.java`，否则 `java Hello` 仍会运行先前生成的 `Hello.class`。

### 写法二：单文件直接运行（Java 11+）

```bash
java Hello.java    # 不再需要先执行 javac
```

适合小脚本与练手场景；注意它不会在磁盘生成 `.class` 文件。

### 写法三：紧凑源文件与简化 main（Java 25+）

```java
// Hello.java —— Java 25 紧凑源文件写法
void main() {
    IO.println("Hello, modern Java!");
}
```

```bash
java Hello.java    # 直接运行
```

- 不再强制类声明，实例方法 `main` 即可作为入口
- 新增 `java.lang.IO` 提供 `IO.println` / `IO.readln` 等简单控制台 IO
- 旧经验对照：需要参数时仍可声明 `void main(String[] args)`

> Java 21 环境下请使用写法一或写法二；写法三需要 JDK 25。

## 🐚 JShell：交互式学习利器（Java 9+）

先在终端执行：

```bash
jshell
```

进入 `jshell>` 提示符后，逐条输入以下 Java 代码（不要复制提示符）：

```java
1 + 1
var list = new java.util.ArrayList<String>();
list.add("hello");
String greet(String name) { return "Hi, " + name; }
greet("Java");
```

依次可观察到加法结果 `2`、空列表、添加成功的 `true`、方法创建提示，以及 `"Hi, Java"`。最后在 JShell 内输入 `/exit` 退出。

常用命令：

| 命令 | 作用 |
|------|------|
| `/vars` | 查看已声明变量 |
| `/methods` | 查看已定义方法 |
| `/list` | 查看历史代码 |
| `/edit <片段>` | 打开编辑器修改片段 |
| `/exit` | 退出 |

**旧对照**：Java 9 之前想验证一段代码，必须建类、建 main、编译、运行；JShell 让"试一行代码"的成本降为零，特别适合学习新 API。

## 📦 Maven 项目初体验

```bash
mvn archetype:generate -DgroupId=com.example -DartifactId=demo \
  -DarchetypeArtifactId=maven-archetype-quickstart \
  -DarchetypeVersion=1.4 -DinteractiveMode=false
cd demo
mvn package
java -cp target/classes com.example.App
```

关注 `pom.xml` 中与版本相关的最小配置：

```xml
<properties>
    <!-- release 会同时控制 source/target，并使用正确的 API 集合 -->
    <maven.compiler.release>21</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>
```

常用命令：`mvn compile` / `mvn test` / `mvn package` / `mvn clean`。

**旧对照**：`source`/`target` 只管语法级别；`release`（Java 9+）还会检查 API 兼容性，避免"低版本运行却用了新 API"的隐性事故。

## 🐘 Gradle 项目初体验

```bash
gradle init --type java-application --dsl kotlin
./gradlew run
```

`build.gradle.kts` 关键片段：

```kotlin
plugins {
    id("java")
    application
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21) // 指定编译与运行用的 JDK
    }
}
```

Toolchain 让"项目要什么 JDK"成为工程配置的一部分，机器上装有对应版本即可，不再依赖全局 `JAVA_HOME`。

## 🧭 如何选择运行方式

| 场景 | 推荐方式 |
|------|---------|
| 验证语法/探索 API | JShell |
| 单文件小工具、算法题 | `java 文件名.java` |
| 正式工程 | Maven 或 Gradle + Wrapper |
| 教学/极简示例（JDK 25） | 紧凑源文件 + `void main()` |

## 🎯 练习与实践

### 练习一：三种方式跑 Hello World
1. 分别用 javac+java、单文件直跑运行同一程序
2. 若装有 JDK 25，改写为紧凑源文件 + `IO.println`

### 练习二：JShell 探索
1. 在 JShell 中定义一个方法并调用
2. 用 `/vars` 和 `/methods` 查看会话状态

### 练习三：工程化
1. 分别创建 Maven 与 Gradle 项目，跑通 `package` / `run`
2. 给两个项目都生成 Wrapper 并提交

## 🔗 相关文档

- 📄 **[变量与类型](./03-variables-types.md)** - 下一站：Java 类型系统与 var 推断
- 📄 **[环境搭建](./01-environment-setup.md)** - 工具安装细节回顾
- 📄 **[标准库核心](../reference/library-guides/01-standard-library.md)** - JShell 中可探索的标准库速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
