# 项目实战 03 - 订单系统（事务 + 消息队列）

> **文档简介**: 高级项目：以"下单-扣库存-发货"为主线，演练跨聚合事务边界、本地消息表（Outbox）模式、RabbitMQ 异步解耦与幂等消费，构建一个可扩展的订单服务
>
> **目标读者**: 已掌握 JPA 事务与消息队列基础、想演练分布式一致性模式的开发者
>
> **前置知识**: 已完成 [图书管理系统](./02-library-management.md)、[生态集成](../frameworks/03-ecosystem-integration.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#订单` `#Outbox` `#消息队列` `#幂等` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

- 功能：下单、支付回调、库存扣减、发货通知（异步）
- 技术栈：Spring Boot 3.x + JPA + RabbitMQ + Testcontainers
- 关键挑战：**数据库事务与消息发送的原子性**、消费幂等

## 🏗️ 一、事务边界设计

### 核心矛盾

```text
@Transactional 内发消息 → 事务回滚但消息已发出（脏消息）
事务提交后再发消息  →  发送失败导致状态不一致（丢消息）
```

**解法：Outbox 本地消息表**——把"要发的消息"当成一行数据，与业务同事务落库，再由独立的发布器投递。

### 数据模型

```java
@Entity
public class Order {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long userId;
    private BigDecimal amount;

    @Enumerated(EnumType.STRING)
    private OrderStatus status;   // CREATED / PAID / SHIPPED / CANCELLED

    @Version                      // 乐观锁：并发修改直接抛异常
    private Long version;

    protected Order() {}
}

@Entity
public class OutboxMessage {

    @Id @GeneratedValue
    private Long id;

    private String aggregateId;   // 关联业务 ID，如订单号
    private String type;          // 事件类型，如 ORDER_PAID
    private String payload;       // JSON 消息体

    private Instant createdAt;
    private Instant publishedAt;  // null = 未发布
    protected OutboxMessage() {}
}
```

## 🛠️ 二、下单主流程

```java
@Service
public class OrderService {

    private final OrderRepository orders;
    private final OutboxRepository outbox;
    private final ProductRepository products;
    private final ObjectMapper json;

    @Transactional
    public Order place(Long userId, Long productId, int qty) {
        // 1. 扣库存（与订单同一事务）
        Product product = products.findByIdForUpdate(productId)
                .orElseThrow(ProductNotFoundException::new);
        product.deduct(qty);                        // 领域方法内含余量校验

        // 2. 创建订单
        Order order = Order.create(userId, product.price().multiply(BigDecimal.valueOf(qty)));
        orders.save(order);

        // 3. 事件与业务同事务写入 Outbox —— 原子性由数据库保证
        OutboxMessage msg = new OutboxMessage(
                order.getId().toString(), "ORDER_PLACED",
                json.writeValueAsString(new OrderPlacedEvent(order.getId(), productId, qty)));
        outbox.save(msg);

        return order;
    }
}
```

> `@Transactional` 的传播、只读与失效场景见 [Spring Boot 进阶](../frameworks/02-spring-boot-advanced.md)。

## 🛠️ 三、Outbox 发布器与消费

### 独立发布器：定时扫描投递

```java
@Component
public class OutboxPublisher {

    private final OutboxRepository outbox;
    private final RabbitTemplate rabbit;

    @Scheduled(fixedDelay = 500)   // 半秒一轮；生产可换成 CDC（Debezium）
    @Transactional
    public void publishPending() {
        for (OutboxMessage msg : outbox.findTop100ByPublishedAtIsNullOrderByCreatedAt()) {
            try {
                rabbit.convertAndSend("order.exchange",
                        msg.getType().toLowerCase(), msg.getPayload());
                msg.markPublished(Instant.now());  // 成功才标记
            } catch (Exception e) {
                // 记日志，下轮重试；长期未投递的进入告警
            }
        }
    }
}
```

### 幂等消费：以业务键去重

```java
@RabbitListener(queues = "inventory.deduct.q")
public void onOrderPlaced(OrderPlacedEvent event, Channel ch, long tag)
        throws IOException {
    try {
        // 消费记录表以 eventId 为唯一键：重复投递直接视为已处理
        if (consumeLog.insertIfAbsent(event.eventId()) == 0) {
            ch.basicAck(tag, false);
            return;
        }
        inventoryService.deduct(event.productId(), event.qty());
        ch.basicAck(tag, false);
    } catch (Exception e) {
        ch.basicNack(tag, false, false);  // 重试耗尽后进死信队列
    }
}
```

## 🛠️ 四、状态机与支付回调

```java
// 订单状态流转用 Sealed + switch 表达式收敛（Java 21 模式匹配）
public sealed interface OrderEvent permits Paid, Shipped, Cancelled {}

public OrderStatus next(OrderStatus current, OrderEvent event) {
    return switch (event) {
        case Paid e when current == OrderStatus.CREATED -> OrderStatus.PAID;
        case Shipped e when current == OrderStatus.PAID -> OrderStatus.SHIPPED;
        case Cancelled e when current == OrderStatus.CREATED -> OrderStatus.CANCELLED;
        default -> throw new IllegalStateException(
                "非法状态流转: %s + %s".formatted(current, event));
    };
}
```

> Sealed 与模式匹配语义见 [Record / Sealed / 模式匹配速查](../reference/language-concepts/05-records-sealed-patterns.md)。

## 🧪 测试策略

| 层次 | 工具 | 验证点 |
|------|------|--------|
| 事务原子性 | `@SpringBootTest` + Testcontainers(RabbitMQ) | 扣减失败时订单与 Outbox 同回滚 |
| 发布器 | 集成测试 | 消息投递后 `publishedAt` 非空 |
| 幂等 | 重复发送同 eventId | 库存只扣一次 |
| 乐观锁 | 并发线程改同一订单 | 一方抛 `ObjectOptimisticLockingFailureException` |

详见 [集成测试](../testing/02-integration-testing.md) 与 [API 测试](../testing/03-api-testing.md)。

## 🎨 最佳实践

### ✅ 推荐
- 一致性先"同库事务 + Outbox"，再考虑分布式事务框架
- 消息体只含 ID 与最小字段，消费方回查本地库
- 状态流转用类型（Sealed + switch）而非 if-else 散落

### ❌ 陷阱
- `@Scheduled` 单实例假设：多实例部署需 ShedLock/分片
- 消费端"先扣库存再记消费日志"：崩溃窗口导致重复扣减
- 无死信队列：失败消息静默堆积

## 🚀 下一步

- 走向生产：配置中心、可观测性、容器化 → [生产级 Spring Boot 应用](./04-production-spring-app.md)

## 🔗 相关文档

### 本模块
- 📖 [并发 API 速查](../reference/language-concepts/04-concurrency-api.md) — 并发消费与线程模型
- 📖 [第三方库指南](../reference/library-guides/02-third-party-libs.md) — MQ 客户端与 ShedLock 选型
- 📄 [生态集成](../frameworks/03-ecosystem-integration.md) — RabbitMQ 收发基础
- 📄 [Spring Boot 进阶](../frameworks/02-spring-boot-advanced.md) — 事务与 AOP
- 📄 [生产级 Spring Boot 应用](./04-production-spring-app.md) — 下一篇：生产化
