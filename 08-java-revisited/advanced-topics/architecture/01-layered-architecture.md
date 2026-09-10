# 分层与六边形架构 - 从经典三层到领域驱动的演进

> **文档简介**: 解释 Java 后端架构的演进逻辑：经典三层为什么会长歪、六边形架构如何翻转依赖、DDD 的核心思想如何落地到 Spring Boot 代码组织——以及各自的真实代价
>
> **目标读者**: 写过 Spring Boot 项目、想理解"代码该怎么组织"背后设计哲学的开发者
>
> **前置知识**: 已完成 [Spring Boot 进阶](../../frameworks/02-spring-boot-advanced.md)；抽象类与接口见 [类、接口与 Record](../../basics/04-classes-records.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#架构` `#六边形` `#DDD` `#端口与适配器` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

理解以下"为什么"，而非记模板：
- 为什么经典三层会演变成"贫血 + 上帝 Service"
- 依赖倒置如何让领域层不依赖任何框架
- DDD 的聚合、限界上下文解决什么问题
- 什么时候**不该**用六边形架构

## 🔍 一、经典三层的自然衰败

```text
Controller ──> Service ──> Repository        每层只能调下一层
    DTO        实体+逻辑       SQL/ORM
```

三层本身没错，问题在**时间**：

1. Service 为了复用"再往下一层的方法"开始互相调用，最终一个 `OrderService` 几千行
2. JPA 实体被迫服务于数据库表结构，业务规则只能写在 Service 里 → 领域模型贫血
3. 数据库表结构成为架构中心：换存储 = 重写一切

**根因**：依赖方向是"由外向内压"——技术细节（框架、数据库）定义形状，业务逻辑填空。

## 🔍 二、六边形架构：依赖翻转

### 核心主张

应用内核（领域逻辑）位于中心，通过**端口（接口）** 与外界对话，外部世界都是**适配器**：

```text
            ┌────────────────────────────┐
 HTTP/RPC ──▶ 入站端口 ◀── 入站适配器     │
 (REST)     │  (OrderService 接口)        │
            │                            │
            │        领域核心             │   依赖只指向内核
            │   Order / 聚合 / 领域服务   │
            │                            │
            │  出站端口 ◀── 出站适配器    ◀── DB / MQ / 支付
            │ (OrderRepository 接口)      │
            └────────────────────────────┘
```

### Spring Boot 中的落地

```java
// 内核：纯领域对象，无任何 Spring/JPA 注解
public class Order {
    private OrderId id;
    private OrderStatus status;
    private Money total;

    public void pay(PaymentReceipt receipt) {   // 业务规则内聚
        if (status != OrderStatus.CREATED) {
            throw new IllegalStateTransition(status, "pay");
        }
        this.status = OrderStatus.PAID;
        this.total = total.plus(receipt.fee());
    }
}

// 出站端口：内核定义的接口（不是 Spring Data）
public interface OrderRepository {
    OrderId save(Order order);
    Optional<Order> findById(OrderId id);
}

// 出站适配器：持久化细节被隔离在内核之外
@Component
class JpaOrderRepository implements OrderRepository {
    private final SpringDataOrders jpa;      // 内部才用 JpaRepository

    @Override
    public Optional<Order> findById(OrderId id) {
        return jpa.findById(id.value()).map(OrderEntity::toDomain);
    }
}
```

**检验标准**：`order` 包的 import 列表里没有 `org.springframework`、没有 `jakarta.persistence`——领域代码用 JUnit 纯单测即可覆盖（见 [单元测试](../../testing/01-unit-testing.md)）。

## 🔍 三、DDD 的三个落地概念

### 聚合（Aggregate）：一致性边界

- 聚合根是唯一对外入口：`order.addItem(...)` 而非直接改 `item.orderId`
- **一个事务只改一个聚合**——跨聚合协调用事件（见 [订单系统的 Outbox](../../projects/03-order-system.md)）
- 聚合要小：Order 聚合装几百个 OrderItem 就是设计事故

### 限界上下文（Bounded Context）：模型的适用范围

"商品"在目录上下文（营销文案、图片）和库存上下文（仓位、安全库存）是**两个不同的模型**。上下文之间用防腐层（ACL）翻译，而非共享一个"万能 Product 类"——微服务拆分粒度本质上就是限界上下文的物理化。

### 通用语言（Ubiquitous Language）

代码命名与业务沟通用同一套词：`borrow`/`giveBack` 而非 `updateLoanStatus`。命名即文档。

## 🔍 四、包组织对比

```text
按层分包（传统）              按特性分包（模块化单体）
com.devquest                  com.devquest.order
├── controller/               ├── OrderController.java      [入站适配器]
│   ├── OrderController       ├── PlaceOrderUseCase.java    [入站端口]
│   └── BookController        ├── Order.java                [领域]
├── service/                  ├── OrderRepository.java      [出站端口]
│   └── OrderService          └── JpaOrderRepository.java   [出站适配器]
├── repository/               com.devquest.inventory
└── domain/                   └── ...
```

按特性分包把"改动"聚拢：一个需求只动一两个包，模块间靠端口通信，未来拆微服务沿着包边界切割。

## 🔍 五、什么时候不用？

| 场景 | 建议 |
|------|------|
| CRUD 为主、逻辑薄 | 经典三层足够，六边形是仪式感税 |
| 原型/验证期 | 先跑通，架构在第二版再翻 |
| 团队 < 3 人小项目 | 模块化分包即可，不必双映射完整端口体系 |

架构没有免费午餐：六边形用映射层换取内核纯净。**代价换来的收益是"业务规则可长期演化"**——如果你的业务规则一年变三次，这笔账就是值的。

## 🔗 相关文档

### 本模块
- 📖 [JPA 核心速查](../../reference/framework-essentials/02-jpa-essentials.md) — 适配器层用到的持久化语义
- 📖 [Record / Sealed / 模式匹配速查](../../reference/language-concepts/05-records-sealed-patterns.md) — 值对象与状态机的语言基础
- 📄 [Spring Boot 进阶](../../frameworks/02-spring-boot-advanced.md) — 事务边界与架构的关系
- 📄 [订单系统项目](../../projects/03-order-system.md) — 聚合 + 事件的综合实战
- 📄 [生产级 Spring Boot 应用](../../projects/04-production-spring-app.md) — 架构治理在生产中的延伸
