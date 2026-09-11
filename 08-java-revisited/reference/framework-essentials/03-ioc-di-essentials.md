# IoC/DI 与 Bean 生命周期速查

> **文档简介**: Spring 容器核心机制的条目式速查：IoC 容器与 Bean 定义、三种注入方式对比、Bean 作用域、生命周期回调、条件装配——Spring 一切特性的地基
>
> **目标读者**: 用惯了 Boot 但对容器行为"知其然不知其所以然"的开发者
>
> **前置知识**: [Spring Boot 入门](../../frameworks/01-spring-boot-basics.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#IoC` `#DI` `#Bean作用域` `#条件装配` |
| **更新日期** | `2026年9月` |

## 📌 定义

- **IoC（控制反转）**：对象的创建与依赖装配交给容器负责，业务代码只声明"需要什么"。
- **容器**：`BeanFactory`（最基础）→ `ApplicationContext`（增强：事件发布、资源加载、AOT 友好）；Boot 应用本质是 `SpringApplication` 启动的一个 `ApplicationContext`。
- **Bean**：由容器实例化、装配并管理生命周期的对象。
- **DI（依赖注入）**：IoC 的实现手段，三种方式——构造器注入（**推荐**）、setter 注入、字段注入。

## 📖 语法 / 签名

### 注册 Bean 的方式

```java
@Component                  // 业务组件（派生：@Service @Repository @Controller）
public class BorrowService { ... }

@Configuration
public class AppConfig {
    @Bean Clock clock() { return Clock.systemDefaultZone(); }   // 第三方对象用 @Bean 注册
}
```

### 注入方式对比

| 方式 | 写法 | 适用 |
|------|------|------|
| 构造器注入 | `private final BookRepository repo;` + 单构造器（可省 `@Autowired`）| **默认选择**：不可变、依赖显式、便于测试 |
| setter 注入 | `@Autowired void setX(...)` | 可选依赖/可替换依赖 |
| 字段注入 | `@Autowired BookRepository repo;` | 仅原型代码——隐藏依赖、无法 `final`、脱离容器难测试 |

### 消歧与作用域

```java
@Primary                                  // 同类型多 Bean 时的默认者
@Qualifier("mysqlRepo")                   // 按名字精确指定
@Value("${app.rate:0.1}")                 // 注入配置属性（冒号后为默认值）

@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)   // singleton（默认）/ prototype / request / session / application
```

### 生命周期与条件装配

- 回调顺序：构造器 → 依赖注入 → `@PostConstruct` →（使用）→ `@PreDestroy`
- 接口等价物：`InitializingBean`/`DisposableBean`、`*Aware` 系列注入容器底层组件
- 条件装配：`@ConditionalOnProperty`、`@ConditionalOnMissingBean`、`@ConditionalOnClass`；自动配置类经 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 登记

## 💡 示例

```java
@Service
public class BorrowService {
    private final BookRepository repo;
    private final Clock clock;

    BorrowService(BookRepository repo, Clock clock) {   // 单构造器免注解
        this.repo = repo;
        this.clock = clock;
    }

    @PostConstruct
    void warmUp() { /* 容器回调：此时依赖已就绪 */ }
}

// prototype 依赖的"每次新实例"诉求：用 ObjectProvider 而非直接注入
@Component
class ReportRunner {
    private final ObjectProvider<Report> reports;

    ReportRunner(ObjectProvider<Report> reports) { this.reports = reports; }

    void run() { reports.getObject().generate(); }      // 每次获取新实例
}
```

## ⚠️ 常见陷阱

- **字段注入泛滥**：依赖关系不可见、循环依赖被掩盖——除非一次性脚本，不要用
- **singleton 注入 prototype**：注入那一刻固定，之后永远同一个实例——改用 `ObjectProvider`
- **构造器循环依赖直接启动失败**（Boot 2.6+ 默认禁止循环引用）：正确解法是重新划分类的职责，而非 `@Lazy` 绕过
- **在 `@PostConstruct` 里假设其他 Bean 已完成业务初始化**：只保证自身依赖已注入，兄弟 Bean 的 `@PostConstruct` 顺序不确定
- **`@ConditionalOnMissingBean` 写在业务配置里**：普通 `@Configuration` 加载顺序不定，该条件只在自动配置类中可靠

## 🔗 相关条目

- 📄 **[Spring Boot 核心速查](./01-spring-boot-essentials.md)** - 自动配置与启动流程
- 📄 **[AOP 速查](./04-aop-essentials.md)** - 代理 Bean 的创建前提
- 📄 **[事务传播与隔离速查](./05-transaction-essentials.md)** - 事务 Bean 的代理机制
- 📄 **[JPA 核心速查](./02-jpa-essentials.md)** - Repository Bean
- 📄 **[TODO API 项目](../../projects/01-todo-api.md)** - 分层注入实战
