# 事务传播与隔离速查

> **文档简介**: `@Transactional` 的属性全表、七种传播行为、四种隔离级别与失效场景清单——声明式事务的完整字典条目
>
> **目标读者**: 排查"事务没回滚/没生效"或设计跨方法事务边界的开发者
>
> **前置知识**: [AOP 速查](./04-aop-essentials.md)、[JPA 核心速查](./02-jpa-essentials.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#事务` `#传播行为` `#隔离级别` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

- **声明式事务**：`@Transactional` 方法被 AOP 代理拦截，经 `PlatformTransactionManager`（JPA 场景为 `JpaTransactionManager`）统一开启/提交/回滚。
- **传播行为**：方法被调用时如何对待"当前已存在的事务"。
- **隔离级别**：并发事务之间的可见程度，决定脏读/不可重复读/幻读是否可能。

## 📖 语法 / 签名

### @Transactional 常用属性

| 属性 | 说明 | 默认 |
|------|------|------|
| `propagation` | 传播行为 | `REQUIRED` |
| `isolation` | 隔离级别 | `DEFAULT`（跟随数据库）|
| `timeout` | 超时秒数 | 跟随全局 |
| `readOnly` | 只读提示（驱动/持久层可据此优化）| `false` |
| `rollbackFor` | 触发回滚的异常类型 | 见下"默认回滚规则" |
| `noRollbackFor` | 不触发回滚的异常 | — |
| `transactionManager` / `value` | 多事务管理器时指定 | 唯一管理器 |

**默认回滚规则**：只有 `RuntimeException` 与 `Error` 触发回滚；受检异常默认**提交**——可用 rollbackFor 配置受检异常回滚；Spring 6.2+ 也支持在 EnableTransactionManagement 中设 rollbackOn=ALL_EXCEPTIONS 改变全局默认。

### 七种传播行为

| 传播行为 | 外层有事务 | 外层无事务 | 备注 |
|----------|-----------|-----------|------|
| `REQUIRED`（默认）| 加入 | 新建 | 绝大多数场景够用 |
| `REQUIRES_NEW` | 挂起外层，新建独立事务 | 新建 | 占两个数据库连接——审计/日志场景；警惕连接池耗尽与死锁 |
| `NESTED` | 在保存点内执行 | 新建 | 外层回滚则内层必回滚；**≠ `REQUIRES_NEW`**（不独立提交）|
| `SUPPORTS` | 加入 | 非事务执行 | 读接口的可选事务 |
| `NOT_SUPPORTED` | 挂起外层 | 非事务执行 | 大批量导入绕开长事务 |
| `MANDATORY` | 加入 | 抛异常 | 强制"调用方必须已开事务" |
| `NEVER` | 抛异常 | 非事务执行 | 禁止在事务内被调用 |

### 隔离级别与并发异常

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|----------|:----:|:----------:|:----:|
| `READ_UNCOMMITTED` | 可能 | 可能 | 可能 |
| `READ_COMMITTED`（PostgreSQL/Oracle 默认）| 不会 | 可能 | 可能 |
| `REPEATABLE_READ`（MySQL InnoDB 默认）| 不会 | 不会 | 视实现（InnoDB 快照读基本不会）|
| `SERIALIZABLE` | 不会 | 不会 | 不会 |

## 💡 示例

```java
// 业务主流程：显式声明回滚受检异常 + 超时
@Transactional(rollbackFor = Exception.class, timeout = 5)
public void transfer(Long from, Long to, Money amount) { ... }

// 只读查询
@Transactional(readOnly = true)
List<Order> findByMember(Long memberId) { ... }

// REQUIRES_NEW：无论主流程成败都要留下的审计记录
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void audit(String action, Long orderId) { ... }

// 提交后再动作：发消息/清缓存，避免"消息发出但事务随后回滚"
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void onOrderPaid(OrderPaidEvent event) { notify(event); }
```

## ⚠️ 常见陷阱（失效场景清单）

1. **同类自调用**：`this.save()` 不走代理 → 事务失效（根因见 [AOP 速查](./04-aop-essentials.md)）
2. **方法可见性与代理**：接口代理要求 public 接口方法；Spring 6+ 类代理默认也可处理 protected 与包可见方法。private、自调用及不可重写方法仍受限制
3. **异常被 catch 吞掉**：外层代理可能看不到失败；但若内层或持久化提供者已标记 rollback-only，仍会回滚
4. **抛受检异常但未设 `rollbackFor`**：默认不回滚（最反直觉的一条）
5. **跨线程**：常规 PlatformTransactionManager 使用线程绑定上下文，不自动传播到新线程；响应式事务使用 Reactor 上下文，是另一种模型
6. **`REQUIRES_NEW` 连接耗尽**：内外各占一个连接，池小 + 层层嵌套 = 互相等待死锁
7. **多事务管理器未指定 `transactionManager`**：操作落在错误数据源的事务里

<!-- full-library-explanation -->
## 用两次写入观察真正的提交边界

设计“扣库存后创建订单”，在第二步故意抛异常，再从新事务读取库存。只有这样才能验证第一步是否被撤销；仅在同一测试事务里查对象，可能看到缓存状态或被测试框架的最终回滚掩盖。数据库 flush 成功也不等于事务最终提交，约束错误可能直到提交才暴露。

REQUIRED 通常共享物理事务。内层将事务标记 rollback-only 后，即使外层捕获异常，提交仍可能失败并报告 UnexpectedRollbackException。REQUIRES_NEW 独立提交，但需要额外连接，也可能等待外层仍持有的锁。NESTED 依赖事务管理器和保存点支持，不能假设所有 JPA 操作都支持同样的嵌套语义。

AFTER_COMMIT 监听器避免回滚前发送，却不能保证消息可靠到达：提交后进程崩溃仍会丢消息。可靠发布可用事务发件箱保存待发送记录，再由独立任务重试。readOnly 只是提示与优化契约，是否强制拒写取决于数据库和配置。

**练习**：分别让第二步抛受检异常、运行时异常、被 catch 的异常，记录数据库最终状态，再调整 rollbackFor 比较。还应给下游 HTTP 设独立超时，事务 timeout 不会自动中断任意 Java 代码或远程请求。

参考：[事务方法可见性与回滚配置](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)。

## 🔗 相关条目

- 📄 **[AOP 速查](./04-aop-essentials.md)** - 代理与自调用失效的根因
- 📄 **[JPA 核心速查](./02-jpa-essentials.md)** - 持久化上下文与事务边界
- 📄 **[异常体系与资源管理](../language-concepts/06-exceptions-resources.md)** - 异常类型决定回滚
- 📄 **[订单系统项目](../../projects/03-order-system.md)** - 事务边界设计实战
- 📄 **[Spring Boot 核心速查](./01-spring-boot-essentials.md)**


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
