# Java / Spring：理解地图与学习规划

> 前置：函数、类与集合；知道 JDK 编译运行程序，Maven/Gradle 管依赖与构建。先使用一个构建工具。

## 先回答一个问题

**对象之间怎样协作，框架如何把一次请求交给正确的业务对象？**

Java 提供类型、对象与异常，Spring 管理对象装配与请求处理。先手动创建对象并调用方法，再比较框架注入；这样注解代表的职责才有具体含义。

## 先建立学习合同：版本、产物与失败案例

默认基线是 **JDK 21**。本模块中 record、sealed、模式匹配 `switch` 和虚拟线程都可以在这条基线上学习；Java 25 的紧凑源文件是选学内容，不能因为该写法无法在 JDK 21 编译而判定基础阶段失败。进入 Spring 项目前再选择一个构建工具，并只使用项目提交的 Maven/Gradle Wrapper。

| 阶段 | 只需完成的阅读 | 必须亲手产出 | 必须观察的失败案例 | 可以进入下一阶段的条件 |
|---|---|---|---|---|
| 0：工具闭环 | [环境搭建](basics/01-environment-setup.md) → [第一个程序](basics/02-first-program.md) | `Hello.java` 与 `Hello.class`；执行 `javac --release 21 -encoding UTF-8 Hello.java && java Hello` | 改了源码却不重新编译，确认仍会运行旧 class | 能解释源码、字节码与 JVM 启动各自发生什么；输出 `Hello, Java!` |
| 1：语言基础 | 变量/类型 → 类/record → 控制流 → 异常 | 一个能返回结果或抛出明确定义异常的普通 Java 方法 | 空输入、未知 ID 或非法状态至少一个；不能用吞掉异常伪装成功 | 能写出调用点可处理的正常结果和失败结果 |
| 2：集合与现代语法 | 按项目需要补集合、泛型、Stream、Optional；再读现代特性 | 一段读取固定数据并返回稳定结果的转换逻辑 | 空集合与无匹配是成功的零结果；Optional 缺失不可裸 `get()` | 能说明为什么该场景用循环或 Stream，以及缺失如何处理 |
| 3：控制台项目 | [图书管理系统](basics/08-first-project.md) | `Main.java`、`books.tsv`、一次命令记录 | 新进程读取借出状态；重复借阅必须失败且文件不被错误修改 | 正常、无结果和业务失败都有可复现命令与退出码 |
| 4：HTTP 与依赖注入 | Spring Boot 入门 → [Todo API](projects/01-todo-api.md) | 使用 Wrapper 构建的 API 工程与至少一个端到端请求记录 | 空标题和不存在 ID；必须指出异常如何转成 HTTP 响应 | 能画出 Controller → Service → Repository 的调用方向，且测试能重复运行 |
| 5：持久化与生产准备 | JPA/事务 → 测试 → Docker/可观测性 | 带真实测试数据库的集成测试、镜像构建记录 | 事务中途失败后验证没有半提交数据 | 先通过测试和镜像构建，再考虑部署与性能调优 |

每次阶段验收都保留四项：所用 JDK/构建工具版本、输入命令、标准输出或响应、一个失败案例的退出码或状态码。它们比“看懂了”更能定位问题，也为之后升级 JDK 或 Spring 提供基线。

## 概念怎样连接

编译运行 → 类型与集合 → 类/接口/record → 异常 → 测试 → 依赖注入 → Web → JPA/事务

| 概念 | 必要解释 |
|---|---|
| record | 适合表达一组数据的载体，字段引用不可重新赋值不代表被引用的 List 不可变。 |
| 依赖注入 | 构造器说明对象需要哪些协作者，Spring 负责提供实例；业务仍是普通方法调用。 |
| 事务 | 数据库一组操作要共同成功或撤销；方法加注解的效果还受调用边界与事务配置约束。 |

## 从 0 到 1 的阅读顺序

不要求已有 Java 工作经验。先能编译运行一个类，区分对象和引用，再用普通方法表达业务。基础项目用到 record、集合或 lambda 时就地补对应知识；虚拟线程无需在首个项目之前学完。

JDK 与框架基线见[模块 README](README.md)。语言基础和控制台首项目直接用 `javac` / `java`；进入需要第三方依赖的工程时，再选 Maven 或 Gradle 并使用 Wrapper。官方学习入口：[Dev.java Learn](https://dev.java/learn/)，从语言基础和类开始，随后进入异常与集合。

1. [环境搭建 - JDK 与现代工具链](basics/01-environment-setup.md)
2. [第一个程序 - 从 javac 到现代工作流](basics/02-first-program.md)
3. [变量与类型 - 基本类型、var 与包装类型](basics/03-variables-types.md)
4. [类、接口与 Record](basics/04-classes-records.md)
5. [控制流程 - 条件、循环与模式匹配](basics/05-control-flow.md)
6. [异常处理 - 异常体系与现代设计](basics/06-exceptions.md)
7. [综合练习 - 控制台图书管理系统](basics/08-first-project.md)
8. 按需补课：[Lambda、Stream、Optional、虚拟线程与 Sealed](basics/07-modern-features.md)，先补项目使用的语法，虚拟线程留到并发专题。

## 三个阶段如何验收

首项目的明确前置是能编译一个类，并读懂 [类与 record](basics/04-classes-records.md) 和 [异常](basics/06-exceptions.md)；使用到的集合、Optional 和 Stream 可以对照 [现代特性](basics/07-modern-features.md) 相应小节补齐。产物为 `Main.java`、编译出的类文件和练习数据 `books.tsv`，此阶段无需构建工具或 Spring。

在空练习目录按 [控制台图书项目](basics/08-first-project.md) 保存源码，执行 `javac --release 21 -encoding UTF-8 Main.java`，再运行 `java Main books.tsv add 978-1 "Java 入门" Alice 2024`、`java Main books.tsv borrow 978-1`、`java Main books.tsv find 978-1`。最后一次是新进程，仍应显示 `BORROWED`；再借同一本应失败且不改变文件。编译失败先回查 [环境搭建](basics/01-environment-setup.md) 的 `java` / `javac` 版本与当前目录；业务失败回查首项目的命令规则；存储失败回查它的读写与文件格式说明。保存命令、输出和退出码后，再进入 [Todo API](projects/01-todo-api.md)，把同样的业务错误映射到 HTTP。

| 阶段与入口 | 练习输入与动作 | 通过条件 |
| --- | --- | --- |
| 普通对象：[控制台图书项目](basics/08-first-project.md) | 新增 ISBN、借出后用新进程查询，再执行 `find` 查询未知 ISBN；另用 `search` 查询无匹配词 | 已借出状态可读回；未知 ISBN 的 `find` 报错并退出 1，`search` 无匹配则成功输出空列表；不能把内部 Optional 的空值当作 CLI 成功结果 |
| HTTP 映射：[Todo API](projects/01-todo-api.md) | 创建合法条目、提交空标题、查询不存在 ID | 状态码和响应与接口约定一致；能指出 Java 异常在哪一层转成 HTTP 响应 |
| 持久化：[图书管理系统](projects/02-library-management.md) | 写入后重启；制造一组操作中的第二步失败 | 持久数据可读回，事务应回滚的部分确实未保留；验证使用真实测试数据库而非只检查 Mock 调用 |

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

## 框架与高级主题怎么选

Spring Boot 为主线。先 Web 与 Validation，再按需要引入 JPA、Security、Redis 和消息队列。虚拟线程和微服务放在已经理解阻塞与资源上限之后。

## 全量参考怎么查

关键词解决“语法是什么意思”，内置函数解决“直接能调用什么”，标准库解决“导入以后能做什么”。框架 API 另列，避免把库函数误当成语言本身。以下是现有文章的完整导航，不代表每个 API 都已充分讲解；具体覆盖缺口进入审查台账。

### framework-essentials

- [Spring Boot 核心速查](reference/framework-essentials/01-spring-boot-essentials.md)
- [JPA / Hibernate 核心速查](reference/framework-essentials/02-jpa-essentials.md)
- [IoC/DI 与 Bean 生命周期速查](reference/framework-essentials/03-ioc-di-essentials.md)
- [AOP 切面编程速查](reference/framework-essentials/04-aop-essentials.md)
- [事务传播与隔离速查](reference/framework-essentials/05-transaction-essentials.md)
- [Spring Security 7 速查](reference/framework-essentials/06-spring-security-essentials.md)
- [REST 客户端与 HTTP 服务速查](reference/framework-essentials/07-rest-client-essentials.md)

### language-concepts

- [Java 关键字详解](reference/language-concepts/01-java-keywords.md)
- [集合框架与泛型速查](reference/language-concepts/02-collections-generics.md)
- [Stream / Optional / Collector API 速查](reference/language-concepts/03-streams-optional.md)
- [并发 API 速查 - Executor、虚拟线程、并发集合与 CompletableFuture](reference/language-concepts/04-concurrency-api.md)
- [Record / Sealed / 模式匹配速查](reference/language-concepts/05-records-sealed-patterns.md)
- [异常体系与资源管理](reference/language-concepts/06-exceptions-resources.md)
- [字符串不可变语义与 String Pool](reference/language-concepts/07-string-immutability-pool.md)
- [枚举详解](reference/language-concepts/08-enums.md)
- [注解详解](reference/language-concepts/09-annotations.md)
- [接口语义](reference/language-concepts/10-interface-semantics.md)

### library-guides

- [标准库核心速查 - java.util / java.time / java.nio](reference/library-guides/01-standard-library.md)
- [三方库指南 - Lombok / Jackson / JUnit 6 / Mockito / MapStruct](reference/library-guides/02-third-party-libs.md)
- [java.lang 导览](reference/library-guides/03-java-lang.md)
- [java.io 导览](reference/library-guides/04-java-io.md)
- [java.util.function 导览](reference/library-guides/05-java-util-function.md)
- [java.math 导览](reference/library-guides/06-java-math.md)
- [java.text 与时间格式化](reference/library-guides/07-java-text-and-time-format.md)
- [java.util.regex 导览](reference/library-guides/08-java-util-regex.md)
- [JDK 包地图](reference/library-guides/09-jdk-package-map.md)

### quick-references

- [现代 Java 一行式速查](reference/quick-references/01-java-cheatsheet.md)
- [常见错误排查](reference/quick-references/02-troubleshooting.md)
- [Spring Boot 3 → 4 迁移速查](reference/quick-references/03-spring-boot4-migration.md)

## 卡住时

先判断是术语不懂、输入输出不清、代码上下文缺失，还是运行环境不同。返回[学习方法](../shared-resources/learning-guide.md)按证据排查；通用术语见[术语解释](../shared-resources/glossary.md)。
