# JPA / Hibernate 核心速查

> **文档简介**: JPA 实体注解、Spring Data 仓库方法、@Transactional 事务语义、N+1 问题与懒加载陷阱的条目式速查（Hibernate 7.x / Spring Boot 4.x / Jakarta Persistence 3.2 命名空间）
>
> **目标读者**: 有旧版 JPA 经验、需要现代化对照与陷阱排查的开发者
>
> **前置知识**: 关系型数据库基础；Spring 注入见 [Spring Boot 核心速查](./01-spring-boot-essentials.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#JPA` `#Hibernate` `#SpringData` `#事务` |
| **更新日期** | `2026年9月` |

</details>

## 🏛️ 实体注解速查

```java
@Entity
@Table(name = "books")
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)   // 自增；SEQUENCE 适合批量
    private Long id;

    @Column(nullable = false, unique = true, length = 20)
    private String isbn;

    @Enumerated(EnumType.STRING)          // 必须显式 STRING！默认 ORDINAL 是坑
    private BookStatus status;

    private LocalDate publishedAt;        // java.time 直接映射（Hibernate 6+）

    @ManyToOne(fetch = FetchType.LAZY)    // 建议显式 LAZY，配 JOIN FETCH 解决 N+1
    @JoinColumn(name = "author_id")
    private Author author;

    @OneToMany(mappedBy = "book", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Review> reviews = new ArrayList<>();

    @Version                              // 乐观锁
    private long version;
}
```

要点：
- 实体类要求无参构造器（JPA 规范）——**实体不是 record 的适用场景**（record 无无参构造且不可变）；DTO 出参用 record 完全没问题
- 双向关系要手动维护两端（提供 `addReview()` 辅助方法）
- 继承策略 `@Inheritance(strategy = JOINED)` 按需选择，默认 SINGLE_TABLE

## 🗃️ Spring Data 仓库

```java
public interface BookRepository extends JpaRepository<Book, Long> {

    // 1. 派生查询：按方法名生成 SQL
    Optional<Book> findByIsbn(String isbn);
    List<Book> findByStatusOrderByPublishedAtDesc(BookStatus status);
    List<Book> findByTitleContainingIgnoreCase(String keyword);

    // 2. 自定义 JPQL
    @Query("select b from Book b where b.author.name = :author")
    List<Book> findByAuthorName(@Param("author") String author);

    // 3. 投影：只取需要的列（record 投影）
    @Query("select b.isbn as isbn, b.title as title from Book b where b.status = :s")
    List<BookSummary> findSummariesByStatus(BookStatus s);

    record BookSummary(String isbn, String title) {}   // record 投影（接口式投影也支持）
}

// 父接口自带：save / findById / findAll / findAll(Pageable) / count / deleteById / existsById ...
```

分页与排序：

```java
Page<Book> page = repo.findAll(PageRequest.of(0, 20, Sort.by("title").ascending()));
```

## 💱 @Transactional 语义

```java
@Service
public class LibraryService {
    @Transactional                       // 类或方法级
    public void borrow(String isbn) {
        var book = bookRepository.findByIsbn(isbn).orElseThrow();
        book.borrow();                   // 脏检查：事务提交时自动 UPDATE，无需显式 save
    }
}
```

| 属性 | 说明 |
|------|------|
| `propagation` | `REQUIRED`（默认，加入或新建）/ `REQUIRES_NEW`（挂起外层）/ `NESTED` / `MANDATORY` / `SUPPORTS` / `NOT_SUPPORTED` / `NEVER` |
| `readOnly = true` | 只读优化（Hibernate 关闭脏检查快照） |
| `rollbackFor` | **默认只回滚 RuntimeException 与 Error**——受检异常要 `rollbackFor = Exception.class` |
| `isolation` | 隔离级别（READ_COMMITTED 等，按数据库支持） |

**陷阱清单**:
- **自调用失效**：同类中 `this.method()` 调用带 `@Transactional` 的方法不经过代理，事务不生效——拆到另一个 Bean
- `private`/`final` 方法上的注解同样被代理忽略
- 事务内发 HTTP/发消息：拉长事务持锁时间——拆分或用事务提交后回调（`@TransactionalEventListener`）

## 🐌 N+1 与懒加载

**N+1 问题**: 查 N 个实体再逐个触发关联的懒加载 SQL，共 1 + N 条。

```java
// ❌ N+1：每个 book 的 author 单独查询
List<Book> books = bookRepository.findAll();
books.forEach(b -> b.getAuthor().getName());

// ✅ 方案一：JOIN FETCH
@Query("select b from Book b join fetch b.author")
List<Book> findAllWithAuthor();

// ✅ 方案二：@EntityGraph
@EntityGraph(attributePaths = "author")
List<Book> findByStatus(BookStatus status);

// ✅ 方案三：@BatchSize(size = 50) 批量 IN 查询
```

**LazyInitializationException**: 会话关闭后访问未初始化的懒代理——修复思路同上（在事务内取完数据或用 JOIN FETCH），不要用 `spring.jpa.open-in-view=true` 掩盖（Boot 默认开，建议显式关闭）。

## ✅ 最佳实践 / ❌ 陷阱清单

日期类型按语义选择：LocalDate 表示日期，Instant 表示时间点，不能不分时区需求互换。枚举存字符串便于理解，却仍需计划重命名后的旧数据迁移；存数字也要明确稳定映射，不能依赖随意调整的顺序。

saveAll 不保证自动产生高效 JDBC 批处理，效果受主键策略、驱动、批大小和 flush 行为影响。通过实际 SQL 与相同数据量的耗时验证。响应使用所需字段的 DTO，并检查关联加载，避免序列化才触发一串查询。

## 🔗 相关文档

- 📄 **[Spring Boot 核心速查](./01-spring-boot-essentials.md)** - 注入与配置上下文
- 📄 **[异常处理](../../basics/06-exceptions.md)** - 事务回滚与异常类型的契约
- 📄 **[三方库指南](../library-guides/02-third-party-libs.md)** - MapStruct 做 实体↔DTO 映射


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
