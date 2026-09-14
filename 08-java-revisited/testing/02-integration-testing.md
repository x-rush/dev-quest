# 集成测试 - @SpringBootTest 与 Testcontainers

> **文档简介**: 用真实依赖验证装配正确性：`@SpringBootTest` 上下文裁剪、`@DataJpaTest` 切片测试、Testcontainers 启动真实 PostgreSQL/RabbitMQ，告别"H2 里能过、生产炸了"
>
> **目标读者**: 单元测试已上手、需要验证持久层与中间件集成的开发者
>
> **前置知识**: 已完成 [单元测试](./01-unit-testing.md) 与 [Spring Boot 进阶](../frameworks/02-spring-boot-advanced.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#SpringBootTest` `#Testcontainers` `#切片测试` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：
- 按验证目标选择合适的测试切片，避免"全家桶"式集成测试
- 用 Testcontainers 在 CI 与本地跑真实 PostgreSQL / RabbitMQ
- 处理测试数据隔离与上下文缓存问题

## 🛠️ 一、选择测试切面

| 注解 | 启动范围 | 适合验证 |
|------|---------|---------|
| 纯 JUnit + Mock | 无 Spring | 服务层逻辑（见 [单元测试](./01-unit-testing.md)） |
| `@WebMvcTest` | 仅 MVC 层 | 请求映射、校验、异常处理 |
| `@DataJpaTest` | 仅 JPA 层 | 查询、映射、事务行为 |
| `@SpringBootTest` | 完整上下文 | 端到端装配、定时任务、消费者 |

**原则**：能窄不宽——切片测试秒级完成，全上下文测试留给关键路径。

## 🛠️ 二、@DataJpaTest：持久层切片

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE) // 不替换为 H2
class BookRepositoryTest {

    @Autowired BookRepository books;
    @Autowired TestEntityManager em;

    @Test
    @DisplayName("悲观锁查询可正确锁定行")
    void pessimisticLock() {
        em.persist(new Book("978-0-13-468599-1", "Effective Java", "Bloch"));
        em.flush();

        // 第二个事务持锁时，本查询应阻塞或抛锁定冲突（此处验证 SQL 正确生成）
        Optional<Book> found = books.findByIdForUpdate(1L);

        assertThat(found).isPresent();
    }
}
```

> `@DataJpaTest` 默认每个测试方法事务回滚，数据零残留——无需手动清理。

## 🛠️ 三、Testcontainers：真实中间件

### 引入与基类

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<!-- Testcontainers 2.0（Boot 4 默认）：模块 artifact 统一加 testcontainers- 前缀 -->
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers-postgresql</artifactId>
    <scope>test</scope>
</dependency>
```

```java
@SpringBootTest
@Testcontainers
abstract class IntegrationTestBase {

    @Container
    @ServiceConnection                   // 自动把容器连接信息注入 DataSource
    static PostgreSQLContainer<?> postgres =
            new PostgreSQLContainer<>("postgres:16-alpine");

    @Container
    @ServiceConnection
    static RabbitMQContainer rabbit =
            new RabbitMQContainer("rabbitmq:3.13-management-alpine");
}

// 具体测试继承基类，连接配置全自动
class OrderFlowIT extends IntegrationTestBase {

    @Autowired OrderService orderService;

    @Test
    @DisplayName("下单后 Outbox 产生待发布事件")
    void orderProducesOutboxEvent() {
        orderService.place(1L, 1L, 2);

        var pending = outbox.findTop100ByPublishedAtIsNullOrderByCreatedAt();
        assertThat(pending).hasSize(1);
        assertThat(pending.get(0).getType()).isEqualTo("ORDER_PLACED");
    }
}
```

### 为什么不用 H2 模拟 PostgreSQL？

- 方言差异：`BIGSERIAL`、JSONB、窗口函数 H2 全没有
- 行为差异：隔离级别、锁等待、约束时序
- Testcontainers 用的是**与生产同版本**的镜像，测的就是部署的

## 🛠️ 四、测试数据与隔离策略

```java
// 跨类共享昂贵容器：单例容器模式（静态块启动，全 JVM 生命周期复用）
@Testcontainers
public abstract class SharedContainerBase {
    static final PostgreSQLContainer<?> POSTGRES =
            new PostgreSQLContainer<>("postgres:16-alpine");

    static {
        POSTGRES.start();
        System.setProperty("spring.datasource.url", POSTGRES.getJdbcUrl());
    }
}
```

| 策略 | 手段 | 适用 |
|------|------|------|
| 事务回滚 | 切片默认行为 | `@DataJpaTest` / `@WebMvcTest` |
| 每类重建 | `@Sql(scripts = "cleanup.sql")` | 有自建事务的测试 |
| 状态隔离 | 唯一数据（UUID 后缀） | 并行执行的集成测试 |

## ❓ 常见问题

### Q1: 上下文启动太慢？

同一套配置的 `@SpringBootTest` 会缓存上下文；避免每个测试类都改 `@TestPropertySource`（缓存失效重建）。统一配置放抽象基类。

### Q2: CI 里 Docker 不可用？

GitHub Actions 的 `ubuntu-latest` 自带 Docker；受限环境可给集成测试打 `@Tag("integration")`，用 Maven Profile 分离执行（见 [CI/CD](../deployment/03-ci-cd-observability.md)）。

### Q3: 消费者/定时任务在测试里乱跑？

定时任务用 `@TestConfiguration` 提供空转的 `TaskScheduler` Bean 替换默认实现（Boot 4 无 `spring.task.scheduling.enabled` 属性）；消费者用 `@MockitoSpyBean` 精确控制。

## 🎨 最佳实践

### ✅ 推荐
- 集成测试统一 `*IT` 后缀 + Failsafe 插件，与单元测试分离执行
- `@ServiceConnection` 替代手工写容器连接属性
- 关键业务流至少一条全链路 IT（HTTP → DB → MQ）

### ❌ 陷阱
- 测试里 `Thread.sleep` 等异步：用 Awaitility `await().atMost(5, SECONDS)`
- 测试数据硬编码主键 ID：依赖自增序列初始值，迁移后全挂
- 共享容器但每次测试不清理：用例间数据污染

## 🚀 下一步

- 走 HTTP 层验证 → [API 测试](./03-api-testing.md)（MockMvc / REST Assured）

## 🔗 相关文档

### 本模块
- 📖 [JPA 核心速查](../reference/framework-essentials/02-jpa-essentials.md) — 被测的持久化语义
- 📖 [第三方库指南](../reference/library-guides/02-third-party-libs.md) — Awaitility 等测试工具
- 📄 [单元测试](./01-unit-testing.md) — 快速反馈层
- 📄 [API 测试](./03-api-testing.md) — 下一篇：HTTP 契约验证
- 📄 [订单系统项目](../projects/03-order-system.md) — 本文测试策略的实战场景
