# Spring Boot 核心速查

> **文档简介**: Spring Boot 3.x 核心条目速查：自动配置机制、核心注解、REST 与配置绑定、Actuator 端点，以及从 Boot 2 迁移的关键变化
>
> **目标读者**: 有旧版 Spring/Boot 经验、需要对照现代化（Boot 3.x + Jakarta + Java 21/25）的开发者
>
> **前置知识**: IoC/依赖注入概念；Java 基础见 [现代 Java 特性](../../basics/07-modern-features.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#SpringBoot` `#自动配置` `#注解` `#Actuator` |
| **更新日期** | `2026年9月` |

## 🚀 Boot 3.x 关键变化（对照旧版）

| 变化点 | Boot 2.x | Boot 3.x |
|--------|----------|----------|
| 命名空间 | `javax.*` | `jakarta.*`（Jakarta EE 9+） |
| Java 基线 | Java 8+ | **Java 17+**（推荐 21/25） |
| 自动配置注册 | `META-INF/spring.factories` | `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` |
| Spring Framework | 5.x | 6.x（原生 AOT、虚拟线程友好） |
| 可观测性 | Micrometer 1.x | Micrometer 1.x + Observation API 统一指标/追踪 |

## 🏗️ 启动与自动配置

**定义**: `@SpringBootApplication` 是三合一注解，自动配置按"条件满足才装配"的原则工作。

```java
@SpringBootApplication   // = @Configuration + @EnableAutoConfiguration + @ComponentScan
public class App {
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}
```

自动配置机制链路：
1. `@EnableAutoConfiguration` 触发 `AutoConfiguration.imports` 中列出的自动配置类加载
2. 每个配置类由 `@ConditionalOnClass`/`@ConditionalOnMissingBean`/`@ConditionalOnProperty` 等条件注解把关
3. **用户自定义 Bean 优先**（`@ConditionalOnMissingBean` 语义），可用 `spring.autoconfigure.exclude` 排除

```java
@AutoConfiguration
@ConditionalOnClass(DataSource.class)
public class MyAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean          // 用户没配才上
    public MyService myService(MyProps props) { return new MyService(props); }
}
```

## 🏷️ 核心注解速查

| 分类 | 注解 | 说明 |
|------|------|------|
| 声明 Bean | `@Component` `@Service` `@Repository` `@Controller` | 组件扫描注册（语义化别名） |
| 配置类 | `@Configuration` + `@Bean` | Java 配置；`proxyBeanMethods=false` 提升启动速度 |
| 注入 | `@Autowired` / 构造器注入（推荐） | 单构造器可省略注解 |
| 条件 | `@ConditionalOnClass` `@ConditionalOnMissingBean` `@ConditionalOnProperty` | 自动配置/条件装配 |
| 环境 | `@Profile("prod")` `@Value("${key}")` | 环境隔离 / 简单取值 |
| 配置绑定 | `@ConfigurationProperties(prefix = "app")` | 批量绑定，类型安全 |
| 生命周期 | `@PostConstruct` `@PreDestroy` | 初始化/销毁回调 |

## ⚙️ 配置绑定（record 原生支持）

```java
@ConfigurationProperties(prefix = "app.mail")
public record MailProps(String host, int port, boolean sslEnabled) {}
// application.yml: app.mail.host=smtp.example.com
```

```java
@SpringBootApplication
@ConfigurationPropertiesScan        // 扫描并注册配置属性 Bean
public class App {}
```

**陷阱**: 缺少 `@ConfigurationPropertiesScan`（或 `@EnableConfigurationProperties`）时绑定类不会注册为 Bean。

## 🌐 REST 注解速查

```java
@RestController
@RequestMapping("/api/books")
public class BookController {

    @GetMapping("/{isbn}")                          // GET，路径变量
    public Book get(@PathVariable String isbn) { ... }

    @PostMapping                                    // POST，JSON 请求体
    @ResponseStatus(HttpStatus.CREATED)
    public Book create(@RequestBody @Valid BookRequest req) { ... }

    @GetMapping
    public Page<Book> list(@RequestParam(defaultValue = "0") int page) { ... }

    @PutMapping("/{isbn}")
    public Book update(@PathVariable String isbn, @RequestBody BookRequest req) { ... }

    @DeleteMapping("/{isbn}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable String isbn) { ... }
}
```

异常集中处理：

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(BookNotFoundException.class)
    public ProblemDetail handle(BookNotFoundException e) {
        var pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, e.getMessage());
        return pd;                                  // RFC 7807 问题详情（Boot 3 默认支持）
    }
}
```

## 🩺 Actuator

**定义**: 生产级运维端点集合，配合 Micrometer 暴露健康、指标与追踪数据。

| 端点 | 用途 |
|------|------|
| `/actuator/health` | 健康检查（含 DB/Redis 等指示器）；`show-details` 可看详情 |
| `/actuator/info` | 构建信息（需配置 `info.*` 属性） |
| `/actuator/metrics` | JVM/HTTP/自定义指标 |
| `/actuator/prometheus` | Prometheus 抓取格式（需引入 micrometer-registry-prometheus） |
| `/actuator/env` | 环境属性（默认脱敏） |

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus    # 默认只暴露 health,info
  endpoint:
    health:
      show-details: always
```

**陷阱**: `include: "*"` 全暴露有安全风险——生产按需最小化并配合认证。

## ✅ 最佳实践 / ❌ 陷阱清单

- ✅ 依赖注入用**构造器注入**（final 字段、可测试）；不用字段 `@Autowired`
- ✅ 配置用 `@ConfigurationProperties` + record，不用散落的 `@Value`
- ✅ 虚拟线程开启：`spring.threads.virtual.enabled=true`（Boot 3.2+，Java 21+）
- ❌ 不要在 `@Configuration` 里互相 `new` 部件——交给容器
- ❌ 不要用 `javax.*` 导入（Boot 3 必用 `jakarta.*`）
- ❌ 不要吞掉 `@Transactional` 边界内的受检异常期望回滚（默认不回滚，见 [JPA 核心](./02-jpa-essentials.md)）

## 🔗 相关文档

- 📄 **[JPA 核心速查](./02-jpa-essentials.md)** - Spring Data JPA 配套
- 📄 **[三方库指南](../library-guides/02-third-party-libs.md)** - 生态常用库
- 📄 **[现代 Java 特性](../../basics/07-modern-features.md)** - record/虚拟线程的教程基础
