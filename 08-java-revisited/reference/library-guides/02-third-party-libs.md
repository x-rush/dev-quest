# 三方库指南 - Lombok / Jackson / JUnit 6 / Mockito / MapStruct

> **文档简介**: Java 生态五个高频三方库的条目式速查：定位、核心用法、与现代 Java（record/虚拟线程）的关系及陷阱
>
> **目标读者**: 需要快速上手或重新评估这些库（尤其对照 record 等语言新特性）的开发者
>
> **前置知识**: Maven 依赖管理（见 [环境搭建](../../basics/01-environment-setup.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Lombok` `#Jackson` `#JUnit6` `#Mockito` `#MapStruct` |
| **更新日期** | `2026年9月` |

## 🪄 Lombok - 编译期样板消除

**定位**: 注解处理器，编译时生成 getter/setter/构造器/builder 等样板代码。

```xml
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <scope>provided</scope>
</dependency>
```

```java
@Data                       // getter+setter+equals+hashCode+toString
@Builder                    // 链式构造器
@RequiredArgsConstructor    // final 字段构造注入（Spring 服务类常用）
@Slf4j                      // 自动生成 log 字段
public class Report { ... }
```

**与 record 的关系**: `@Data`+`@Value` 的"不可变 DTO"场景已被 **record 语言原生取代**（无插件依赖、IDE 零配置）；Lombok 保留价值在 `@Builder`（record 也可加）与可变类样板。

**陷阱**: 依赖 IDE 插件支持；`@Data` 用在实体上会连带生成与懒加载关联的 equals/toString——JPA 实体慎用。

## 📨 Jackson - JSON 序列化（3.x，Boot 4 默认）

```xml
<!-- Jackson 3：包名与 groupId 改为 tools.jackson（注解 jackson-annotations 除外） -->
<dependency>
    <groupId>tools.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>
```

```java
// Jackson 3：JsonMapper 不可变，用 builder 配置（替代 Jackson 2 的可变 ObjectMapper）
var mapper = JsonMapper.builder().build();
String json = mapper.writeValueAsString(user);        // 序列化
User u = mapper.readValue(json, User.class);           // 反序列化
List<User> users = mapper.readValue(json, new TypeReference<List<User>>() {});  // 泛型集合
```

常用注解（包名不变，仍是 `com.fasterxml.jackson.annotation`）：

| 注解 | 用途 |
|------|------|
| `@JsonProperty("user_name")` | 字段重命名 |
| `@JsonIgnore` / `@JsonIgnoreProperties({"pw"})` | 忽略字段 |
| `@JsonFormat(pattern = "yyyy-MM-dd")` | 日期格式 |
| `@JsonCreator` / `@JsonValue` | 枚举/值对象定制 |

**与 record 的关系**: Jackson 2.12+ 起就**原生支持 record**（构造器参数即组件），3.x 延续——record + Jackson 是现代 DTO 标配。

**陷阱**: Jackson 3 相比 2.x 的默认值变化要心里有数——`FAIL_ON_UNKNOWN_PROPERTIES` 默认已关闭（字段漂移不再炸接口，但类型不匹配仍会炸）；`java.time`/`Optional` 支持内建于 databind，无需再注册 `JavaTimeModule`；日期默认序列化为 ISO-8601 字符串。Spring Boot 4 的 `spring-boot-starter-webmvc` 已自动配置 `JsonMapper`，直接注入使用即可（定制用 `JsonMapperBuilderCustomizer`，或过渡期设 `spring.jackson.use-jackson2-defaults=true`）。

## 🧪 JUnit 6 - 单元测试（Jupiter API）

```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
</dependency>
```

```java
class LibraryTest {

    Library library;

    @BeforeEach
    void setUp() { library = new Library(); }

    @Test
    void 应能借出在库图书() {
        library.add(new Book("i1", "Java", "作者", 2026, BookStatus.AVAILABLE));
        assertDoesNotThrow(() -> library.borrow("i1"));
        assertEquals(BookStatus.BORROWED, library.findByIsbn("i1").orElseThrow().status());
    }

    @ParameterizedTest
    @CsvSource({"1, 1", "2, 4"})
    void 平方(int input, int expected) {
        assertEquals(expected, square(input));
    }
}
```

要点：`@DisplayName`/`@Nested` 组织结构；断言建议搭配 AssertJ 的流式链（`assertThat(x).isEqualTo(y)`）。

## 🎭 Mockito - Mock 与桩

```xml
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <scope>test</scope>
</dependency>
```

```java
@ExtendWith(MockitoExtension.class)
class BorrowServiceTest {
    @Mock BookRepository repo;            // Mockito 5 默认 inline mockmaker，final 类/record 也能 mock
    @InjectMocks BorrowService service;

    @Test
    void 找不到书时抛异常() {
        when(repo.findByIsbn("x")).thenReturn(Optional.empty());
        assertThrows(BookNotFoundException.class, () -> service.borrow("x"));
        verify(repo).findByIsbn("x");     // 验证交互
    }
}
```

**陷阱**: mock 返回类型为 Optional/集合时必须显式 stub（不会自动给"空 Optional"）；过度 mock 私有细节 = 测试与实现强耦合。

## 🗺️ MapStruct - 编译期 Bean 映射

```xml
<dependency>
    <groupId>org.mapstruct</groupId>
    <artifactId>mapstruct</artifactId>
    <version>1.6.5</version>
</dependency>
```

```java
@Mapper(componentModel = "spring")
public interface BookMapper {
    BookDto toDto(Book book);             // 同名字段自动映射，编译期生成代码
    Book toEntity(BookDto dto);

    @Mapping(source = "title", target = "name")
    BookView toView(Book book);           // 不同名需显式指定
}
```

**与 record 的关系**: MapStruct 1.5+ 支持 record（走构造器注入字段）；对比运行时反射的 ModelMapper/Dozer，**编译期生成 = 零反射开销 + 映射错误在编译期暴露**，是现代首选。

## ✅ 最佳实践 / ❌ 陷阱清单

- ✅ 新代码 DTO 优先 record；Lombok 只服务可变类与 @Builder 场景
- ✅ Boot 项目用注入的 JsonMapper（Jackson 3），不自建
- ✅ 测试命名表达行为；断言优先 AssertJ
- ❌ 不要 JPA 实体上 `@Data`
- ❌ 不要用反射式映射库（ModelMapper）处理关键字段

## 🔗 相关文档

- 📄 **[JPA 核心速查](../framework-essentials/02-jpa-essentials.md)** - 实体与 DTO 分离
- 📄 **[Spring Boot 核心速查](../framework-essentials/01-spring-boot-essentials.md)** - Jackson 自动配置
- 📄 **[Record/Sealed/模式匹配](../language-concepts/05-records-sealed-patterns.md)** - record 语义
