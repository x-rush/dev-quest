# Java / Spring：理解地图与学习规划

> 前置：函数、类与集合；知道 JDK 编译运行程序，Maven/Gradle 管依赖与构建。先使用一个构建工具。

## 先回答一个问题

**对象之间怎样协作，框架如何把一次请求交给正确的业务对象？**

Java 提供类型、对象与异常，Spring 管理对象装配与请求处理。先手动创建对象并调用方法，再比较框架注入；这样注解代表的职责才有具体含义。

## 概念怎样连接

编译运行 → 类型与集合 → 类/接口/record → 异常 → 测试 → 依赖注入 → Web → JPA/事务

| 概念 | 必要解释 |
|---|---|
| record | 适合表达一组数据的载体，字段引用不可重新赋值不代表被引用的 List 不可变。 |
| 依赖注入 | 构造器说明对象需要哪些协作者，Spring 负责提供实例；业务仍是普通方法调用。 |
| 事务 | 数据库一组操作要共同成功或撤销；方法加注解的效果还受调用边界与事务配置约束。 |

## 从 0 到 1 的阅读顺序

以下按模块现有章节编号导航。章节中的“先理解，再动手”给出本节重点与自测；环境版本集中看[模块 README](README.md)。

1. [环境搭建 - JDK 与现代工具链](basics/01-environment-setup.md)
2. [第一个程序 - 从 javac 到现代工作流](basics/02-first-program.md)
3. [变量与类型 - 基本类型、var 与包装类型](basics/03-variables-types.md)
4. [类、接口与 Record](basics/04-classes-records.md)
5. [控制流程 - 条件、循环与模式匹配](basics/05-control-flow.md)
6. [异常处理 - 异常体系与现代设计](basics/06-exceptions.md)
7. [现代 Java 特性 - Lambda、Stream、Optional、虚拟线程与 Sealed](basics/07-modern-features.md)
8. [综合练习 - 控制台图书管理系统](basics/08-first-project.md)

## 三个阶段如何验收

1. 用普通 Java 对象完成图书新增与查询，未知 ID 产生明确异常。
2. 为业务方法写测试后再接 Controller；HTTP 状态码属于接口映射，不属于普通 Java 异常本身。
3. 切换数据库实现并用集成测试证明约束和回滚；不能只验证 Mock 调用。

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
