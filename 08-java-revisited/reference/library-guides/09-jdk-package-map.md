# JDK 包地图

> **文档简介**: JDK 常用包的查找入口，并链接完整官方索引——已单独成篇的核心包指向本目录条目，中低频包给"一句话职责 + Javadoc 21 链接"，并标注 JPMS 模块归属
>
> **目标读者**: 知道要做什么、不知道标准库哪个包管这件事的开发者
>
> **前置知识**: 无；本篇是其余条目的总索引

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#包地图` `#标准库` `#JPMS` `#索引` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

一张"包 → 职责 → 深入条目"的地图：先在本表定位包，再跳进本目录对应条目或官方 Javadoc。模块归属可用 Class.getModule().getName() 与官方 Javadoc 核对。命名模块隐式读取 java.base，对其他模块需建立可读关系；classpath 应用不使用同一套声明方式。

## 📖 包总表

### 已单独成篇的核心包

| 包 | 模块 | 深入条目 |
|----|------|---------|
| `java.lang`（含子包） | java.base | [java.lang 导览](./03-java-lang.md) |
| `java.util`（集合/工具） | java.base | [标准库核心](./01-standard-library.md)、[集合框架与泛型](../language-concepts/02-collections-generics.md) |
| `java.util.function` | java.base | [java.util.function 导览](./05-java-util-function.md) |
| `java.util.regex` | java.base | [java.util.regex 导览](./08-java-util-regex.md) |
| `java.util.concurrent` | java.base | [并发 API 速查](../language-concepts/04-concurrency-api.md) |
| `java.time`（含 format） | java.base | [标准库核心](./01-standard-library.md)、[java.text 与时间格式化](./07-java-text-and-time-format.md) |
| `java.io` / `java.nio`（含 file） | java.base | [java.io 导览](./04-java-io.md)、[标准库核心](./01-standard-library.md) |
| `java.math` | java.base | [java.math 导览](./06-java-math.md) |
| `java.text` | java.base | [java.text 与时间格式化](./07-java-text-and-time-format.md) |
| `java.lang.annotation` | java.base | [注解详解](../language-concepts/09-annotations.md) |
| `java.net.http` | **java.net.http** | [标准库核心](./01-standard-library.md) HttpClient 段 |
| `java.sql` / `javax.sql` | **java.sql** | Spring 场景见 [JPA 要点](../framework-essentials/02-jpa-essentials.md) |

### 中低频包速查（一句话职责 + 链接）

| 包 | 模块（预期） | 一句话职责 |
|----|------|-----------|
| `java.net` | java.base | 网络基础：URL/URI、Socket/TCP-UDP、InetAddress → [Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/net/package-summary.html) |
| `java.lang.reflect` | java.base | 反射核心：Field/Method/Constructor、动态代理 Proxy → [Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/reflect/package-summary.html)、机制见 [java.lang 导览](./03-java-lang.md) |
| `java.lang.invoke` | java.base | 方法句柄 MethodHandle、VarHandle，invokedynamic 的底层（字符串拼接即由它实现）→ [Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/invoke/package-summary.html) |
| `java.util.zip` | java.base | GZIP/ZIP 压缩解压流 → [Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/zip/package-summary.html) |
| `java.util.jar` | java.base | JAR 文件读写（Manifest/条目）→ [Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/jar/package-summary.html) |
| `javax.crypto` | java.base | 加解密 Cipher、密钥生成 KeyGenerator、Mac（预期归属 java.base）→ [Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/crypto/package-summary.html) |
| `javax.net.ssl` | java.base | TLS/SSLSocket、证书上下文（预期归属 java.base）→ [Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/package-summary.html) |
| `java.util.logging` | **java.logging** | JDK 内置日志框架 → [Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.logging/java/util/logging/package-summary.html) |
| `java.util.concurrent.atomic` | java.base | 无锁原子变量（AtomicInteger/LongAdder）→ [Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/package-summary.html) |
| `javax.annotation.processing`（连同 `javax.lang.model`） | **java.compiler** | 编译期注解处理器 API（预期归属 java.compiler）→ [Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.compiler/javax/annotation/processing/package-summary.html)、场景见 [注解详解](../language-concepts/09-annotations.md) |
| `java.lang.module` | java.base | JPMS 模块系统编程接口（Configuration/ModuleDescriptor；Module 类本身位于 java.lang）→ [Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/module/package-summary.html) |
| `java.rmi` / `javax.management` / `javax.naming` | java.rmi / java.management / java.naming | 分布式遗留 / JMX 管理 / JNDI 命名目录，新项目极少直用（归属预期）→ [Javadoc 总索引](https://docs.oracle.com/en/java/javase/21/docs/api/index.html) |

## 💡 示例

查一个类属于哪个 JPMS 模块（决定模块化应用要不要 `requires`）：

```bash
java --list-modules                      # 列出全部模块（预期 java.net.http、java.sql 为独立模块）
```

```java
// 编程式核验归属（预期输出：java.compiler / java.base / java.sql ...）
System.out.println(javax.annotation.processing.Processor.class.getModule().getName());
System.out.println(javax.crypto.Cipher.class.getModule().getName());

```

下面单独保存为 module-info.java，不能与上面的表达式混放在同一文件：

```java
module com.example.app {
    requires java.net.http;   // java.base 中的包无需声明
    requires java.sql;
}
```

## ⚠️ 常见陷阱

- ❌ **以为 `javax.*` 都是"需要额外依赖的扩展"**：`javax.crypto`/`javax.net.ssl` 随 JDK 的 `java.base` 分发，开箱即用（预期归属）。
  ✅ 用 `Class.getModule().getName()` 或 `java --list-modules` 核实，再看是否需要 `requires`。
- ❌ **模块化应用里直接用 `javax.annotation.processing` 失败就懵**：它在 `java.compiler` 模块，不在 `java.base`（预期）。
  ✅ `module-info.java` 加 `requires java.compiler;`。
- ❌ **模块化应用里直接 import `java.sql.*` 编译失败**：`java.sql` 是独立模块（预期），不在 `java.base`。
  ✅ `module-info.java` 加 `requires java.sql;`，或暂不模块化（classpath 模式无此限制）。
- ❌ **拿本表当 API 字典逐个背**：地图是用来定位的。
  ✅ 先定位包 → 跳对应条目 → 再查 Javadoc 细节。

<!-- full-library-explanation -->
## 用任务定位包，再核对类、模块与版本

“压缩日志”先查 java.util.zip 的 GZIPOutputStream；“发送 HTTP 请求”查 java.net.http 的 HttpClient；“读取配置文件”查 java.nio.file.Files。找到类后应阅读方法参数、返回值、异常、线程安全和 Since，而不是只复制类名。标准库未提供具体数据库驱动，java.sql 只是接口，运行时还需对应驱动依赖。

包和 JPMS 模块是两层组织。import 缩短类型名字，不安装依赖，也不增加模块可读性；命名模块用 requires 声明读取其他模块，exports 控制编译期 API 可见性，opens 涉及深反射访问。classpath 项目在未命名模块中运行，不能照抄“所有包都加 requires”。

**练习**：用 jshell 分别查看 String.class、java.util.logging.Logger.class 与 java.sql.Connection.class 的 getModule().getName()，预期为 java.base、java.logging、java.sql。再打开对应 Javadoc 的模块首页核对。地图覆盖常用入口，不宣称列出每个 JDK 包；完整范围以所用版本的官方总索引为准。

## 完整实验：从类反查 JPMS 模块

这个完整的 classpath 程序以 Java 21 编译运行，直接使用 `Class::getModule` 验证三类常见包的模块归属。它不验证命名模块的 `requires` 编译配置，也不枚举整个 JDK。

<!-- terra-eighteenth-case: java-jpms-module-map -->
```java
public class Main {
    static void show(Class<?> type) {
        System.out.println(type.getName() + "=" + type.getModule().getName());
    }

    public static void main(String[] args) {
        show(String.class);
        show(java.util.logging.Logger.class);
        show(java.sql.Connection.class);
        show(javax.annotation.processing.Processor.class);
    }
}
```

预期输出依次为 `java.lang.String=java.base`、`java.util.logging.Logger=java.logging`、`java.sql.Connection=java.sql` 与 `javax.annotation.processing.Processor=java.compiler`。这说明包名前缀不能替代模块查询；例如 `javax.annotation.processing` 并不在 `java.base`。

## 🔗 相关条目

- 📄 **[标准库核心速查](./01-standard-library.md)** — 最常用包的 API 速查
- 📄 **[第三方库导览](./02-third-party-libs.md)** — 标准库之外的生态补充
- 📄 **[Java 关键字详解](../language-concepts/01-java-keywords.md)** — module/requires/exports 语法
- 🌐 **[JDK 21 API 文档总索引](https://docs.oracle.com/en/java/javase/21/docs/api/index.html)** — 全量包/模块权威入口

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
