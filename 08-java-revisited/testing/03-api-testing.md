# API 测试 - MockMvc 与 REST Assured

> **文档简介**: 从 HTTP 契约层面验证 API：用 MockMvc 快速测控制器与校验规则，用 REST Assured 做贴近真实调用的验收测试，让接口行为成为可执行规格
>
> **目标读者**: 需要为 REST 接口补自动化测试的开发者
>
> **前置知识**: 已完成 [集成测试](./02-integration-testing.md)；REST 设计见 [Spring Boot 入门](../frameworks/01-spring-boot-basics.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#MockMvc` `#RESTAssured` `#契约测试` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：
- 用 `@WebMvcTest` + MockMvc 独立验证控制器层
- 用 REST Assured 编写基于随机端口的验收测试
- 为接口建立"状态码 + 结构 + 业务语义"三层断言

## 🛠️ 一、MockMvc：控制器切片测试

```java
@WebMvcTest(TodoController.class)          // 只装配 MVC 层
class TodoControllerTest {

    @Autowired MockMvc mockMvc;

    @MockitoBean                           // Boot 3.4+：替换容器中的 Bean
    TodoService todoService;

    @Autowired JsonMapper jsonMapper;      // Boot 4 / Jackson 3：复用主配置的 JsonMapper

    @Test
    @DisplayName("POST /api/todos 校验空白标题返回 400 与字段错误")
    void rejectBlankTitle() throws Exception {
        var body = jsonMapper.writeValueAsString(new TodoDto(null, "  ", false));

        mockMvc.perform(post("/api/todos")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isBadRequest())                    // HTTP 层
                .andExpect(jsonPath("$.title").value("标题不能为空"));  // 响应结构
    }

    @Test
    @DisplayName("GET 不存在的 id 返回 404 错误码")
    void notFound() throws Exception {
        given(todoService.get(999L)).willThrow(new TodoNotFoundException(999L));

        mockMvc.perform(get("/api/todos/999"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error").value("TODO_NOT_FOUND"));
    }

    @Test
    @DisplayName("POST 成功返回 201 与完整资源")
    void createSuccess() throws Exception {
        given(todoService.create("学完 Java 21"))
                .willReturn(new Todo(1L, "学完 Java 21", false, Instant.now()));

        mockMvc.perform(post("/api/todos")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"学完 Java 21\"}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.done").value(false));
    }
}
```

### MockMvc 关键点

- `jsonPath()` 用 JSONPath 表达式断言响应体，`$` 为根
- `@WebMvcTest` 不连数据库：服务层用 `@MockitoBean` 替换（旧版为 `@MockBean`）
- 认证场景用 `with(user("alice").roles("ADMIN"))` 模拟登录态

## 🛠️ 二、REST Assured：验收级 API 测试

### 引入与基本风格

> Boot 4 的依赖管理不再收录 REST Assured（仍可用，但需自行指定版本）；官方新推的 `RestTestClient` 是更轻的替代。

```xml
<dependency>
    <groupId>io.rest-assured</groupId>
    <artifactId>rest-assured</artifactId>
    <version>5.5.0</version> <!-- Boot 4 BOM 不再管理，需显式指定（以官方最新版为准） -->
    <scope>test</scope>
</dependency>
```

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class TodoApiIT {

    @LocalServerPort int port;   // 随机端口：可并行、防冲突

    @BeforeEach
    void setUp() {
        RestAssured.port = port;
    }

    @Test
    @DisplayName("完整生命周期：创建 → 查询 → 删除")
    void fullLifecycle() {
        // given - when - then 以 HTTP 契约表达
        var id =
            given()
                .contentType(ContentType.JSON)
                .body("{\"title\":\"集成测试\"}")
            .when()
                .post("/api/todos")
            .then()
                .statusCode(201)
                .body("title", equalTo("集成测试"))
                .body("id", notNullValue())
                .extract().jsonPath().getLong("id");

        get("/api/todos/" + id)
            .then()
                .statusCode(200)
                .body("done", is(false));

        delete("/api/todos/" + id)
            .then()
                .statusCode(204);
    }
}
```

### 带认证的请求

```java
given()
    .auth().oauth2(accessToken)          // JWT 资源服务器的标准姿势
    .header("X-Request-Id", UUID.randomUUID())  // 追踪键贯穿日志
.when()
    .get("/api/admin/books")
.then()
    .statusCode(200);
```

## 🛠️ 三、三层断言模型

| 层 | 断言内容 | 示例 |
|----|---------|------|
| 状态码 | HTTP 语义 | `statusCode(201)` |
| 结构 | 字段存在与类型 | `body("id", notNullValue())` |
| 语义 | 业务规则 | `body("done", is(false))` |

状态码测试挂了说明契约破坏，结构测试挂了说明 DTO 变更未同步，语义测试挂了说明业务回归。

## 🎨 最佳实践

### ✅ 推荐
- MockMvc 管"控制器单元"，REST Assured 管"整条链路验收"，各司其职
- 测试里先创建数据再断言，不依赖其他测试留下的状态
- 把核心接口的请求/响应样例沉淀为 API 文档（配合 springdoc-openapi）

### ❌ 陷阱
- MockMvc 断言整个 JSON 字符串：字段顺序变化就挂，用 `jsonPath` 逐字段断言
- 验收测试共享可变状态（自增 ID）：改用创建后返回的 ID
- 只测 happy path：401/404/400 分支必须有覆盖

## 🚀 下一步

- API 跑通后打包交付 → [Docker 部署](../deployment/01-docker-deployment.md)

## 🔗 相关文档

### 本模块
- 📖 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md) — 测试自动配置
- 📖 [故障排除速查](../reference/quick-references/02-troubleshooting.md) — 401/JSON 解析常见报错
- 📄 [单元测试](./01-unit-testing.md) — 服务层逻辑测试
- 📄 [集成测试](./02-integration-testing.md) — 真实依赖环境
- 📄 [TODO API 项目](../projects/01-todo-api.md) — 为其补 API 测试
