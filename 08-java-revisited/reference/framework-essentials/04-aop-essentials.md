# AOP 切面编程速查

> **文档简介**: Spring AOP 的术语、五种通知、切点表达式与代理机制的条目式速查——理解 `@Transactional` 等声明式特性失效的根源
>
> **目标读者**: 需要写日志/审计/限流切面，或排查"注解不生效"的开发者
>
> **前置知识**: [IoC/DI 速查](./03-ioc-di-essentials.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#AOP` `#切点表达式` `#代理` |
| **更新日期** | `2026年9月` |

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
}

// 自定义注解 + @annotation：按需启用审计
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Audited { String action(); }

@Around("@annotation(audited)")
public Object audit(ProceedingJoinPoint pjp, Audited audited) throws Throwable {
    auditLog.record(audited.action(), pjp.getArgs());
    return pjp.proceed();
}
```

## ⚠️ 常见陷阱

- **自调用失效**：同类内 `this.method()` 不经过代理 → 该方法上的 `@Transactional`/缓存/自定义切面**全部失效**。解法：拆到另一个 Bean，或经 `ObjectProvider<Self>` 注入自身代理
- **final 类 / final 方法无法被 CGLIB 代理**：切面静默不生效；`private` 方法同样不拦截
- **通知内抛异常**：会向业务调用方传播——`@Around` 的收尾逻辑放在 `finally` 里
- **切点过宽**：`..*.*(..)` 匹配一切方法，性能开销与误伤并存；生产切点要收窄
- **record 不适用**：AOP 只面向方法调用，无法改造 record 组件访问器

## 🔗 相关条目

- 📄 **[事务传播与隔离速查](./05-transaction-essentials.md)** - `@Transactional` 即 AOP 的头号应用
- 📄 **[IoC/DI 速查](./03-ioc-di-essentials.md)** - 代理 Bean 由容器创建
- 📄 **[Spring Boot 核心速查](./01-spring-boot-essentials.md)** - 自动代理开启
- 📄 **[生产级 Spring Boot 应用](../../projects/04-production-spring-app.md)** - 审计/指标切面实战
