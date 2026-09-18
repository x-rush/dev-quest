# Spring Boot 进阶 - Spring Data JPA、事务管理与 AOP

## 先看框架承担哪部分职责

**JPA 与事务**：持久化上下文追踪对象变化，事务规定数据库提交边界，AOP 通过代理等机制附加行为。理解调用路径才能判断注解是否生效。

**最小练习与预期结果**：在实际事务边界模拟第二次写入失败并查询数据库；不能只断言仓库 mock 被调用两次。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 让 Spring Boot 应用真正"有数据、有边界、有横切能力"：用 Spring Data JPA 完成数据访问，用 `@Transactional` 划清事务边界，用 AOP 抽离横切逻辑
>
> **目标读者**: 已能写出基本 REST 接口、需要接入数据库的开发者
>
> **前置知识**: 已完成 [Spring Boot 入门](./01-spring-boot-basics.md)；注解基础见 [现代 Java 特性](../basics/07-modern-features.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#SpringDataJPA` `#事务` `#AOP` `#Hibernate` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：
- 用方法名派生查询与 `@Query` 完成 JPA 数据访问
- 用 `@Transactional` 正确划界，理解传播行为与只读优化
- 用 AOP 实现日志、耗时统计等横切关注点
- 避开 N+1 查询、事务失效等经典陷阱

## 🛠️ 一、Spring Data JPA 快速接入

### 引入依赖与配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope> <!-- 演练用 H2；生产换 PostgreSQL/MySQL 驱动 -->
</dependency>
```

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:demo
  jpa:
    hibernate:
      ddl-auto: validate   # 生产推荐 validate + Flyway 管理表结构
    open-in-view: false    # 关闭 OSIV：避免视图层懒加载引发隐藏事务
```

### 实体与 Repository

```java
import jakarta.persistence.*;

@Entity
@Table(name = "books")
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    private String author;

    protected Book() {}         // JPA 要求无参构造器（protected 即可）

    public Book(String title, String author) {
        this.title = title;
        this.author = author;
    }
    // getter 省略
}

public interface BookRepository extends JpaRepository<Book, Long> {

    // 方法名派生查询：框架按规则生成 SQL
    List<Book> findByAuthorOrderByTitleAsc(String author);

    // 复杂查询用 JPQL，参数绑定防注入；分页传 Pageable 即可
    @Query("select b from Book b where b.title like %:keyword%")
    List<Book> searchByKeyword(@Param("keyword") String keyword);
}
```

> JPA 注解、实体生命周期与懒加载的完整语义见 [JPA 核心速查](../reference/framework-essentials/02-jpa-essentials.md)。

## 🔍 二、事务管理

### @Transactional 放哪一层？

**服务层**。Controller 管协议、Repository 管 SQL，事务边界属于"一段完整业务"：

```java
@Service
public class CheckoutService {   // 构造器注入两个 Repository，声明省略

    @Transactional // 写方法：默认 REQUIRED 传播
    public Order checkout(Long userId, Long bookId, int qty) {
        Book book = inventory.lockBook(bookId);   // 悲观锁防超卖
        if (book == null || qty <= 0) {
            throw new IllegalArgumentException("库存不足");
        }
        Order order = Order.of(userId, book, qty);
        inventory.deduct(bookId, qty);
        return orders.save(order);                // 同一事务：扣减失败则订单也回滚
    }
}
```

### 传播行为常用三档

| 传播行为 | 语义 | 典型场景 |
|----------|------|---------|
| `REQUIRED`（默认） | 有事务加入，没有就新建 | 绝大多数业务方法 |
| `REQUIRES_NEW` | 挂起当前事务，新开一个 | 独立审计日志、失败也要落库 |
| `SUPPORTS` | 有就用没有就非事务 | 纯查询辅助方法 |

### 只读事务

`@Transactional(readOnly = true)` 让 Hibernate 跳过脏检查、驱动可优化为从库路由，适合查询类服务方法。

## 🔍 三、AOP 横切关注点

### 用 AOP 统计方法耗时

```java
@Aspect
@Component
public class TimingAspect {

    private static final Logger log =
            LoggerFactory.getLogger(TimingAspect.class);

    // 切所有 Service 层公共方法
    @Around("execution(* com.devquest..service..*(..))")
    public Object time(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.nanoTime();
        try {
            return pjp.proceed(); // 执行目标方法
        } finally {
            long ms = (System.nanoTime() - start) / 1_000_000;
            log.info("{}#{} took {} ms",
                    pjp.getSignature().getDeclaringType().getSimpleName(),
                    pjp.getSignature().getName(), ms);
        }
    }
}
```

### 自定义注解 + AOP：精确控制切面范围

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Audited {
    String action();
}

@Aspect
@Component
public class AuditAspect {

    @Around("@annotation(audited)") // 绑定注解参数，可读取其属性
    public Object audit(ProceedingJoinPoint pjp, Audited audited) throws Throwable {
        Object result = pjp.proceed();
        // 生产中写入审计表（注意与业务事务解耦，可用 REQUIRES_NEW）
        System.out.printf("[AUDIT] action=%s args=%s%n",
                audited.action(), Arrays.toString(pjp.getArgs()));
        return result;
    }
}
```

## ❓ 常见问题

### Q1: 同类内部调用导致 @Transactional 失效？

事务由代理实现：同类内 `this.processOne(id)` 绕过了代理，注解静默失效。**解法**：把 `processOne` 移到另一个 Bean；或注入自身代理 `ObjectProvider<UserService>` 后经代理调用。

### Q2: N+1 查询怎么发现和解决？

`@OneToMany` 懒加载时，循环访问每条主记录都触发一次子查询。**发现**：开启 `spring.jpa.properties.hibernate.generate_statistics=true` 或看日志 SQL 条数。**解决**：对聚合场景用 `@EntityGraph` 或 JOIN FETCH 一次取回；`final` 方法上的 AOP 切面同理基于代理实现，需改用 AspectJ 织入。

## 🎨 最佳实践

事务边界围绕需要一起成功或失败的数据库操作，避免在持有连接和锁时等待不受控外部 HTTP。禁用 open-in-view 后，应在明确的数据访问范围内取齐响应需要的数据；返回 DTO 的形状由 API 契约决定，不必暴露框架的 Page 类型。

事务注解是否生效取决于代理调用路径、方法可见性与配置，自调用尤其要检查。回滚规则也可以被应用配置改变；显式为业务异常定义期望并测试，不能默认“加注解就一定回滚”。

## 🚀 下一步

- 接入缓存、安全与消息中间件 → [生态集成](./03-ecosystem-integration.md)
- 用 JPA + 认证做一个完整系统 → [图书管理系统项目](../projects/02-library-management.md)

## 🔗 相关文档

### 本模块
- 📖 [JPA 核心速查](../reference/framework-essentials/02-jpa-essentials.md) — 实体映射与持久化上下文完整条目
- 📖 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md) — 配置绑定与 Actuator
- 📄 [Spring Boot 入门](./01-spring-boot-basics.md) — 本文的前置
- 📄 [异常处理](../basics/06-exceptions.md) — 受检/非受检异常影响回滚行为


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
