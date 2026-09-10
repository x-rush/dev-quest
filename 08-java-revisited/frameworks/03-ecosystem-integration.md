# Spring 生态集成 - Security、Redis 与消息队列

> **文档简介**: 给 Spring Boot 应用补上生产三件套：用 Spring Security 做认证授权，用 Redis 做缓存与会话，用消息队列实现服务间异步解耦
>
> **目标读者**: 已掌握 Spring Data JPA 与事务，准备接入中间件的开发者
>
> **前置知识**: 已完成 [Spring Boot 进阶](./02-spring-boot-advanced.md)；并发 API 背景见 [并发 API 速查](../reference/language-concepts/04-concurrency-api.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#SpringSecurity` `#Redis` `#消息队列` `#JWT` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：
- 用 Spring Security 6 的 SecurityFilterChain DSL 配置认证与授权
- 用 Spring Cache 抽象接入 Redis 缓存
- 用 Spring AMQP / Kafka 收发消息并保证消费幂等

## 🛠️ 一、Spring Security 6

### 最小可用配置

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity // 开启 @PreAuthorize 方法级授权
public class SecurityConfig {

    @Bean
    SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)      // 无状态 API 可关闭 CSRF
            .sessionManagement(s -> s.sessionCreationPolicy(
                    SessionCreationPolicy.STATELESS))   // 无状态：不用 Session
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/actuator/health").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));
        return http.build();
    }
}
```

> Boot 3 + Security 6 全面使用 Lambda DSL，`and()` 链式写法已废弃；`authorizeRequests()` 更名为 `authorizeHttpRequests()`。

### 密码必须加密存储

```java
@Bean
PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(); // 永远不存明文/MD5
}

// 注册
String hash = passwordEncoder.encode(rawPassword);

// 校验
boolean ok = passwordEncoder.matches(rawPassword, storedHash);
```

### 方法级授权

```java
@PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.id")
public UserProfile view(Long userId) { /* ... */ }
```

进阶配置与攻击面收敛（CSRF、CORS、权限模型设计）见 [安全最佳实践](../advanced-topics/security/01-security-practices.md)。

## 🛠️ 二、Redis 缓存

### 接入与启用

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

```java
@EnableCaching
@SpringBootApplication
public class DemoApplication { }
```

```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      timeout: 2s
  cache:
    redis:
      time-to-live: 10m   # 全局默认 TTL
```

### 声明式缓存注解

```java
@Service
public class BookService {

    private final BookRepository repo;
    public BookService(BookRepository repo) { this.repo = repo; }

    @Cacheable(cacheNames = "books", key = "#id") // 命中则不执行方法
    public Book getById(Long id) {
        return repo.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("book " + id));
    }

    @CacheEvict(cacheNames = "books", key = "#book.id") // 更新后失效
    public Book update(Book book) {
        return repo.save(book);
    }

    @CachePut(cacheNames = "books", key = "#result.id") // 执行并刷新
    public Book create(Book book) {
        return repo.save(book);
    }
}
```

### 陷阱：缓存对象需要序列化

默认 JDK 序列化要求实体实现 `Serializable` 且可读性差，推荐 JSON 序列化：

```java
@Bean
RedisCacheManagerBuilderCustomizer cacheCustomizer(ObjectMapper mapper) {
    return builder -> builder
        .withCacheConfiguration("books",
            RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(10))
                .serializeValuesWith(RedisSerializationContext.SerializationPair
                    .fromSerializer(new GenericJackson2JsonRedisSerializer())));
}
```

## 🛠️ 三、消息队列集成

### 选型速查

| 维度 | RabbitMQ | Kafka |
|------|----------|-------|
| 模型 | AMQP，路由灵活 | 分区日志，高吞吐 |
| 适合 | 任务分发、延迟队列 | 事件流、日志管道、回放 |
| 顺序 | 单队列有序 | 单分区内有序 |

### Spring AMQP 示例（订单事件）

```java
// 生产者：业务事务提交后再发消息（此处用事务同步器示意）
@Service
public class OrderEventPublisher {

    private final RabbitTemplate rabbit;

    public OrderEventPublisher(RabbitTemplate rabbit) { this.rabbit = rabbit; }

    public void publish(OrderCreatedEvent event) {
        rabbit.convertAndSend("order.exchange", "order.created", event);
    }
}

// 消费者：手动 ACK + 幂等（按消息 ID 去重）
@RabbitListener(queues = "order.created.q")
public void onOrderCreated(OrderCreatedEvent event, Channel channel,
                           @Header(name = "amqp_deliveryTag") long tag) throws IOException {
    try {
        orderService.handle(event);            // 内部以 eventId 做幂等键
        channel.basicAck(tag, false);
    } catch (Exception e) {
        // 失败重回队列；重试耗尽后应进入死信队列人工处理
        channel.basicNack(tag, false, false);
    }
}
```

Kafka 侧同理：`@KafkaListener(topics = "orders", groupId = "order-service")`，配合 `spring.kafka.consumer.enable-auto-commit: false` 手动提交位移。

### 可靠性要点

- **生产不丢**：开启 publisher confirm + 失败回调
- **消费不丢**：手动 ACK，处理成功才确认
- **幂等消费**：消息至少会送达一次（at-least-once），业务侧必须以唯一键去重

## 🎨 最佳实践

### ✅ 推荐
- Security 配置集中在一个 `SecurityFilterChain`，规则可读优先
- 缓存 TTL 显式设置，杜绝"永不过期"的脏数据
- 消息体只带 ID + 关键字段，消费方按需回查，避免大消息

### ❌ 陷阱
- `@Cacheable` 用于"每次结果都不同"的方法（如随机、时间相关）
- 在 `@Transactional` 事务内发消息：事务回滚但消息已发出 → 用事务同步器或 Outbox 模式

## 🚀 下一步

- 把这些中间件串成完整系统 → [订单系统项目](../projects/03-order-system.md)（事务 + 消息队列）
- 生产环境安全加固 → [安全最佳实践](../advanced-topics/security/01-security-practices.md)

## 🔗 相关文档

### 本模块
- 📖 [第三方库指南](../reference/library-guides/02-third-party-libs.md) — Redis/MQ 客户端选型参考
- 📖 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md) — 配置绑定语法
- 📄 [Spring Boot 进阶](./02-spring-boot-advanced.md) — 事务与 AOP 前置知识
- 📄 [订单系统项目](../projects/03-order-system.md) — 本文中间件的综合实战
