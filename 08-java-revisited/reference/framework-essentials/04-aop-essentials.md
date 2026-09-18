# AOP 切面编程速查

> **文档简介**: Spring AOP 的术语、五种通知、切点表达式与代理机制的条目式速查——理解 `@Transactional` 等声明式特性失效的根源
>
> **目标读者**: 需要写日志/审计/限流切面，或排查"注解不生效"的开发者
>
> **前置知识**: [IoC/DI 速查](./03-ioc-di-essentials.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#AOP` `#切点表达式` `#代理` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

| 术语 | 含义 |
|------|------|
| Aspect | 横切关注点的模块化（`@Aspect` 类）|
| Join Point | 程序执行点；Spring AOP 中仅为**方法执行** |
| Pointcut | 匹配 Join Point 的表达式 |
| Advice | 匹配点上执行的动作：`@Before`/`@After`/`@AfterReturning`/`@AfterThrowing`/`@Around` |
| Weaving | 织入；Spring 采用**运行时代理**（非编译期/类加载期）|

- **代理实现**：目标实现了接口 → JDK 动态代理；否则 CGLIB 子类代理。Spring Boot 默认 `proxyTargetClass=true`（统一 CGLIB）。

## 📖 语法 / 签名

```xml
<!-- Boot 4：starter 改名（Boot 3 及以前为 spring-boot-starter-aop）-->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aspectj</artifactId>
</dependency>
```

切点表达式速查：

| 指示器 | 示例 | 匹配目标 |
|--------|------|---------|
| `execution` | `execution(* com.app.service..*(..))` | 方法签名（service 包及子包的全部方法）|
| `within` | `within(com.app.service..*)` | 指定类型内的所有连接点 |
| `@annotation` | `@annotation(com.app.aop.Audited)` | 标注了该注解的**方法** |
| `@within` | `@within(org.springframework.stereotype.Service)` | 标注了该注解的**类型**内方法 |
| `bean` | `bean(*Service)` | Bean 名模式 |
| `args` | `args(java.lang.Long)` | 参数类型匹配 |

参数绑定：`@Before("execution(* pay(..)) && args(orderId,..)")` 直接拿到实参；`@Around("@annotation(audited)")` 拿到注解实例。

## 💡 示例

```java
@Aspect
@Component
public class TimingAspect {

    @Around("execution(* com.app.service..*(..))")
    public Object time(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.nanoTime();
        try {
            return pjp.proceed();
        } finally {
            log.info("{} took {} ms", pjp.getSignature().toShortString(),
                     (System.nanoTime() - start) / 1_000_000);
        }
    }
// 自定义注解 + @annotation：按需启用审计
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Audited { String action(); }

@Around("@annotation(audited)")
public Object audit(ProceedingJoinPoint pjp, Audited audited) throws Throwable {
    auditLog.record(audited.action()); // 只记录明确允许的元数据，避免直接输出所有参数
    return pjp.proceed();
}

}
```

## ⚠️ 常见陷阱

- **自调用失效**：同类内 `this.method()` 不经过代理 → 该方法上的 `@Transactional`/缓存/自定义切面**全部失效**。解法：拆到另一个 Bean，或经 `ObjectProvider<Self>` 注入自身代理
- **final 类 / final 方法无法被 CGLIB 代理**：final 类无法创建子类代理，通常会导致配置或启动失败；final 方法不能被子类代理重写，private 方法也不能被拦截
- **通知内抛异常**：会向业务调用方传播——`@Around` 的收尾逻辑放在 `finally` 里
- **切点过宽**：`..*.*(..)` 匹配一切方法，性能开销与误伤并存；生产切点要收窄
- **record 与代理方式**：record 是 final，不能用子类代理；若实现接口且调用走 JDK 接口代理，可增强接口暴露的方法。不要用 record 作为需要子类代理的服务 Bean

<!-- full-library-explanation -->
## 画出代理边界就能判断哪些调用被增强

调用者拿到代理对象，代理先执行通知，再调用目标对象。目标对象内部的 this.method() 直接访问自身，不会重新穿过代理。于是同一个方法从其他 Bean 调用有事务，从本类调用却没有新增事务边界；若外层已有事务，内层仍在外层事务中，不能笼统说“事务全部消失”。

Around 通知决定是否调用 proceed、调用几次以及返回什么。重试切面多次调用 proceed 会重复执行副作用，需要幂等设计。计时切面对返回 CompletableFuture 或响应式 Publisher 的方法，默认只量到方法返回，不等于异步任务完成。日志也不应直接序列化所有参数，密码和令牌需要排除。

**练习**：为一个方法添加计数切面，分别通过注入 Bean 和 this 调用，记录通知次数。再让业务方法抛错，确认 finally 的计时执行且原异常继续传播。审计失败是否应阻止业务，要由需求明确决定；把日志放入 finally 不会自动防止日志异常覆盖业务异常。

依据：[Spring 代理机制](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html)。

## 🔗 相关条目

- 📄 **[事务传播与隔离速查](./05-transaction-essentials.md)** - `@Transactional` 即 AOP 的头号应用
- 📄 **[IoC/DI 速查](./03-ioc-di-essentials.md)** - 代理 Bean 由容器创建
- 📄 **[Spring Boot 核心速查](./01-spring-boot-essentials.md)** - 自动代理开启
- 📄 **[生产级 Spring Boot 应用](../../projects/04-production-spring-app.md)** - 审计/指标切面实战


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
