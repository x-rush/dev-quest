# Spring Boot 入门 - 依赖注入、自动配置与 REST Controller

## 先看框架承担哪部分职责

**Spring Boot 入门**：容器创建并连接对象，Controller 把 HTTP 转成方法调用，自动配置根据依赖和配置提供默认组件。业务函数仍应能脱离 HTTP 测试。

**最小练习与预期结果**：用构造器注入一个服务，先直接单测它，再请求 Controller；分别验证业务行为与 HTTP 映射。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 用最短路径跑通 Spring Boot 4.x 应用的三大基石：IoC 容器与依赖注入、自动配置原理、REST Controller 开发，写出第一个规范的现代 Java Web 服务
>
> **目标读者**: 回归 Java、希望快速上手 Spring Boot 4.x 的开发者
>
> **前置知识**: 已完成 [现代 Java 特性](../basics/07-modern-features.md) 与 [第一个项目](../basics/08-first-project.md)；注解语法见 [类、接口与 Record](../basics/04-classes-records.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#SpringBoot` `#依赖注入` `#自动配置` `#REST` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：
- 用 `@Component` / `@Service` / `@Repository` / `@Configuration` 划分 Bean 的角色
- 通过构造器注入组装依赖，并理解为什么不用字段注入
- 读懂自动配置的生效条件，用 `application.yml` 定制配置
- 用 `@RestController` + Record 实现一个标准 REST 接口

## 🛠️ 一、创建项目

到 [Spring Initializr](https://start.spring.io/) 选择 Java 21（或 25 LTS）+ Spring Boot 4.1 生成 Maven 项目，勾选 `web`、`actuator` 起步。关键依赖（`pom.xml` 片段；Boot 4 起 Web MVC 的 starter 由 `spring-boot-starter-web` 更名为 **`spring-boot-starter-webmvc`**）：

```xml
<properties>
    <java.version>21</java.version>
</properties>
<dependencies>
    <!-- Spring MVC + 内嵌 Tomcat（Boot 4 起：starter-web 更名为 starter-webmvc） -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-webmvc</artifactId>
    </dependency>
</dependencies>
```

> Spring Boot 4.x 基于 Spring Framework 7.x（Jakarta EE 11 基线，Servlet 6.1），命名空间沿用 Boot 3 起的 `jakarta.*`（如 `jakarta.validation.constraints.NotNull`）；Boot 3→4 的 starter 改名与属性迁移见 [Boot 3→4 迁移速查](../reference/quick-references/03-spring-boot4-migration.md) 与 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md)。

## 🔍 二、依赖注入（DI）

### 核心：IoC 容器管理 Bean

你不再 `new` 对象，而是声明"我需要什么"，容器负责装配。

```java
// @Service：业务层 Bean 的标准标记
@Service
public class GreetingService {

    public String greet(String name) {
        return "Hello, %s!".formatted(name); // Java 15+ formatted
    }
}

// 构造器注入：推荐做法（单一构造器可省略 @Autowired）
@RestController
public class GreetingController {

    private final GreetingService greetingService; // final 保证不可变

    // Spring 4.3+ 单构造器自动注入，无需注解
    public GreetingController(GreetingService greetingService) {
        this.greetingService = greetingService;
    }

    @GetMapping("/greet/{name}")
    public String greet(@PathVariable String name) {
        return greetingService.greet(name);
    }
}
```

### Bean 角色注解对照

| 注解 | 语义层 | 典型用途 |
|------|--------|---------|
| `@Component` | 通用组件 | 工具类、转换器 |
| `@Service` | 业务逻辑 | 领域服务 |
| `@Repository` | 数据访问 | 附加异常转换 |
| `@Controller` / `@RestController` | Web 层 | 处理 HTTP 请求 |
| `@Configuration` | 配置类 | 声明 `@Bean` 方法 |

### 第三方类怎么注入？

无法给第三方类加 `@Component`，用 `@Configuration` + `@Bean`：

```java
@Configuration
public class AppConfig {

    @Bean // 方法返回值注册为单例 Bean
    public Clock clock() {
        return Clock.systemDefaultZone(); // 便于测试时注入固定时钟
    }
}
```

### ❌ 避免字段注入

```java
// 反例：字段注入隐藏依赖、无法用 final、难以脱离容器单测
@Autowired
private GreetingService service; // 不要这样写
```

## 🔍 三、自动配置

Spring Boot 按"classpath 里有什么"自动装配合理默认值：

1. 启动类 `@SpringBootApplication` = `@AutoConfigurationPackage` + `@EnableAutoConfiguration` + `@ComponentScan`
2. 自动配置类从 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 加载（Boot 2 的 `spring.factories` 已废弃）
3. 每个自动配置带条件注解，条件不满足就不生效：

```java
@AutoConfiguration
@ConditionalOnClass(DataSource.class)      // classpath 有数据源驱动才装配
@ConditionalOnMissingBean(DataSource.class) // 用户自己定义了就让位
public class DataSourceAutoConfiguration { /* ... */ }
```

排查：启动加 `--debug` 打印条件评估报告（Positive/Negative matches），或查 Actuator 的 `/actuator/conditions` 端点。

常用配置覆盖（`application.yml`）：

```yaml
spring:
  application:
    name: demo
server:
  port: 8080
logging:
  level:
    com.devquest: DEBUG
```

## 💻 四、REST Controller 实战

### 完整 CRUD 片段

```java
// 用 Record 做 DTO：不可变、自动生成访问器与 equals/hashCode
public record TaskDto(Long id, String title, boolean done) {}

@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    private final Map<Long, TaskDto> store = new ConcurrentHashMap<>();
    private final AtomicLong seq = new AtomicLong();

    @GetMapping
    public List<TaskDto> list() {
        return List.copyOf(store.values()); // 返回不可变副本
    }

    @GetMapping("/{id}")
    public ResponseEntity<TaskDto> get(@PathVariable Long id) {
        // ResponseEntity 显式控制状态码与响应体
        return ResponseEntity.of(Optional.ofNullable(store.get(id)));
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED) // 201
    public TaskDto create(@RequestBody @Valid CreateTaskRequest req) {
        long id = seq.incrementAndGet();
        TaskDto task = new TaskDto(id, req.title(), false);
        store.put(id, task);
        return task;
    }

    public record CreateTaskRequest(
            @NotBlank(message = "标题不能为空") String title) {}
}
```

### 统一异常处理

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Map<String, String> onValidation(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new LinkedHashMap<>();
        ex.getBindingResult().getFieldErrors()
          .forEach(e -> errors.put(e.getField(), e.getDefaultMessage()));
        return errors;
    }
}
```

## 🎨 最佳实践

构造器参数使依赖显式，测试可以传入替代实现。final 字段限制重新赋值，不会让依赖对象自动不可变；record 同样只提供浅层不可变的数据载体，成员若是可变集合仍需考虑防御性复制。

Web DTO 与持久化实体分开可避免意外暴露字段和懒加载。循环依赖优先检查职责是否混在一起，Lazy 只能在有明确生命周期理由时使用。把重工作移到 PostConstruct 仍会影响启动，初始化应定义超时、失败和就绪语义。

## 🔗 相关文档

### 本模块
- 📖 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md) — 自动配置与注解的完整字典条目
- 📖 [Record / Sealed / 模式匹配速查](../reference/language-concepts/05-records-sealed-patterns.md) — DTO 用到的 Record 语义
- 📄 [现代 Java 特性](../basics/07-modern-features.md) — 本文代码大量使用的 Lambda/Stream
- 📄 [第一个项目](../basics/08-first-project.md) — 无框架的纯 Java 版本项目，可对照体会框架带来的差异
- 📄 [Spring Boot 进阶](./02-spring-boot-advanced.md) — 下一篇：JPA、事务与 AOP


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
