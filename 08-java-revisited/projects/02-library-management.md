# 项目实战 02 - 图书管理系统（JPA + 认证）

> **文档简介**: 进阶项目：图书借阅管理，落地 Spring Data JPA 关联映射、Spring Security 7 认证授权、Flyway 数据库迁移与 Redis 缓存，体会"真实数据库 + 真实用户"下的开发节奏
>
> **目标读者**: 完成 TODO API、想练习多实体关联与安全控制的开发者
>
> **前置知识**: 已完成 [TODO API 项目](./01-todo-api.md)、[Spring Boot 进阶](../frameworks/02-spring-boot-advanced.md)、[生态集成](../frameworks/03-ecosystem-integration.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#JPA` `#关联映射` `#SpringSecurity` `#Flyway` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

- 功能：图书管理、会员注册登录、借书/还书、逾期查询
- 技术栈：Spring Boot 4.x + JPA（PostgreSQL）+ Spring Security 7 + Flyway + Redis 缓存

## 🏗️ 一、领域建模与关联映射

### 实体关系

```
Member (会员)  1 ──── N  Loan (借阅)  N ──── 1  Book (图书)
```

```java
@Entity
public class Book {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String isbn;

    private String title;
    private String author;

    @Enumerated(EnumType.STRING)   // 字符串枚举：可读、可追加
    private BookStatus status;     // AVAILABLE / BORROWED / LOST

    protected Book() {}
    // getter / 领域方法省略
}

@Entity
public class Loan {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)  // 多对一默认 EAGER，必须显式 LAZY
    @JoinColumn(name = "member_id")
    private Member member;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "book_id")
    private Book book;

    private LocalDate borrowedAt;
    private LocalDate dueAt;
    private LocalDate returnedAt;       // null 表示未还

    protected Loan() {}
}
```

> 懒加载、持久化上下文、N+1 问题的完整语义见 [JPA 核心速查](../reference/framework-essentials/02-jpa-essentials.md)。

## 🛠️ 二、数据库迁移：Flyway

```text
src/main/resources/db/migration/
└── V1__init.sql              # 建表（后续变更新增 V2、V3…）
```

```sql
-- V1__init.sql（loan 表含 member_id/book_id 外键与日期列，随实体映射）
CREATE TABLE book (
    id     BIGSERIAL PRIMARY KEY,
    isbn   VARCHAR(20) NOT NULL UNIQUE,
    title  VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    status VARCHAR(20) NOT NULL
);
```

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate   # 表结构归 Flyway 管，JPA 只做校验
  flyway:
    enabled: true
```

**规则**：已提交的迁移文件永不修改，变更一律新增 `V<N>__xxx.sql`。

> Boot 4 起模块化更细：使用 Flyway 需显式引入 `spring-boot-starter-flyway`（旧版仅加第三方依赖即可）。

## 🛠️ 三、借书业务：并发安全

```java
@Service
public class LoanService {

    @Transactional
    public Loan borrow(Long memberId, Long bookId) {
        // 1. 悲观锁锁定图书行，防止两个会员同时借走同一本
        Book book = bookRepository.findByIdForUpdate(bookId)
                .orElseThrow(() -> new BookNotFoundException(bookId));

        if (book.getStatus() != BookStatus.AVAILABLE) {
            throw new IllegalStateException("图书当前不可借");
        }

        // 2. 会员借阅上限校验
        if (loanRepository.countActiveLoans(memberId) >= 5) {
            throw new IllegalStateException("超出借阅上限");
        }

        // 3. 领域方法收敛状态变更，避免散落 setter
        book.markBorrowed();

        // 4. Loan.create 接收 Member 实体（而非 memberId），先按 id 取出会员
        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new MemberNotFoundException(memberId));

        return loanRepository.save(Loan.create(member, book, LocalDate.now(), 30));
    }

    @Transactional
    public void giveBack(Long loanId) {
        loanRepository.findById(loanId).ifPresent(loan -> {
            loan.markReturned(LocalDate.now());
            loan.getBook().markAvailable();
        });
    }
}
```

```java
// Repository 侧的悲观锁写法
public interface BookRepository extends JpaRepository<Book, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select b from Book b where b.id = :id")
    Optional<Book> findByIdForUpdate(@Param("id") Long id);
}
```

## 🛠️ 四、认证：Security 7 + 用户详情

```java
@Service
public class DbUserDetailsService implements UserDetailsService {

    private final MemberRepository members;

    public DbUserDetailsService(MemberRepository members) {
        this.members = members;
    }

    @Override
    public UserDetails loadUserByUsername(String email) {
        return members.findByEmail(email)
                .map(m -> User.withUsername(m.getEmail())
                        .password(m.getPasswordHash())  // BCrypt 哈希
                        .roles(m.getRole().name())      // ROLE_ 前缀自动补
                        .build())
                .orElseThrow(() -> new UsernameNotFoundException(email));
    }
}
```

```java
@Bean
SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    return http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers(HttpMethod.POST, "/api/members").permitAll() // 开放注册
            .requestMatchers("/api/loans/**").hasAnyRole("MEMBER", "ADMIN")
            .requestMatchers("/api/books/**").hasRole("ADMIN")
            .anyRequest().authenticated())
        .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .build();
}
```

## 🛠️ 五、热点数据缓存

图书详情等热点查询用 Redis 缓存：`@Cacheable(cacheNames = "bookDetails", key = "#isbn")` 读、`@CacheEvict` 在更新后失效。配置与 JSON 序列化要点见 [生态集成](../frameworks/03-ecosystem-integration.md)。

## 🧪 测试与验证

- 服务层：`@DataJpaTest` 验证借阅上限与悲观锁（见 [集成测试](../testing/02-integration-testing.md)）
- 接口层：未带 token 访问 `/api/books/**` 应得 401；并发借同一本书，断言只有一次成功

## 🎨 最佳实践

### ✅ 推荐
- 枚举状态 + 领域方法（`markBorrowed`）替代裸 setter
- 所有 `@ManyToOne` 显式 `LAZY`，列表接口用 JOIN FETCH 定向加载

### ❌ 陷阱
- 双向关联直接序列化 → 无限递归；用 DTO 投影替代
- 缓存实体对象：脱管后懒加载报错；缓存 DTO
- 迁移文件重命名/修改导致 Flyway 校验失败

## 🚀 下一步

多表操作跨服务拆分 → [订单系统](./03-order-system.md)（事务 + 消息队列）。

## 🔗 相关文档

### 本模块
- 📖 [JPA 核心速查](../reference/framework-essentials/02-jpa-essentials.md) — 关联映射完整条目
- 📖 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md) — Security 自动配置
- 📄 [Spring Boot 进阶](../frameworks/02-spring-boot-advanced.md) — 事务与锁的前置
- 📄 [集成测试](../testing/02-integration-testing.md) — Testcontainers 验证迁移脚本
- 📄 [安全最佳实践](../advanced-topics/security/01-security-practices.md) — 认证方案选型
