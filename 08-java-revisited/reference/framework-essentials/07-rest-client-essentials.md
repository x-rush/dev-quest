# REST 客户端与 HTTP 服务速查

> **文档简介**: Spring HTTP 客户端家族的条目式速查：同步 RestClient、响应式 WebClient、声明式 HTTP Service Clients 与 Framework 7 的 API 版本化
>
> **目标读者**: 需要调用下游 HTTP 服务、为旧 RestTemplate 找替代的开发者
>
> **前置知识**: [Spring Boot 入门](../../frameworks/01-spring-boot-basics.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#RestClient` `#WebClient` `#声明式HTTP` `#API版本化` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

| 客户端 | 定位 | 依赖 |
|--------|------|------|
| `RestClient` | 同步、流式 API；**RestTemplate 的现代替代**（Spring 6.1+）| `spring-boot-starter-restclient` |
| `WebClient` | 响应式（Reactor）；需要流式/高并发非阻塞时选它 | `spring-boot-starter-webclient`（Boot 4 起独立 starter）|
| 声明式 HTTP 接口 | 接口 + `@HttpExchange` 注解，框架生成实现（Spring 6+）| 同 RestClient |
| API 版本化 | Framework 7 新增：同一 URL 按版本路由到不同处理方法 | Framework 7 |

- Spring Framework 7 已将 RestTemplate 标记废弃，建议评估迁移到 RestClient；既有应用应验证行为兼容后迁移。

## 📖 语法 / 签名

```java
// RestClient：链式调用，一行一发
RestClient client = RestClient.builder()
    .baseUrl("https://api.example.com")
    .defaultHeader("Accept", "application/json")
    .build();

Book book = client.get().uri("/books/{isbn}", isbn)
    .retrieve().body(Book.class);

// 按底层请求工厂显式配置超时；不要假设各实现具有相同默认值
@Bean
RestClient restClient(RestClient.Builder builder) {
    var httpClient = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(2))
        .build();
    var factory = new JdkClientHttpRequestFactory(httpClient);
    factory.setReadTimeout(Duration.ofSeconds(5));

    return builder.baseUrl("https://api.example.com")
        .requestFactory(factory)
        .build();
}
```

```java
// 声明式 HTTP Service Clients：接口即客户端
public interface BookApi {
    @GetExchange("/books/{isbn}")
    Book get(@PathVariable String isbn);

    @PostExchange("/books")
    Book create(@RequestBody Book book);
}

@Bean
BookApi bookApi(RestClient.Builder builder) {
    RestClient restClient = builder.baseUrl("https://api.example.com").build();
    return HttpServiceProxyFactory
        .builderFor(RestClientAdapter.create(restClient))
        .build()
        .createClient(BookApi.class);
}
```

- 错误映射：`.onStatus(HttpStatusCode::is4xxClientError, (req, res) -> { throw new DownstreamException(res.getStatusCode()); })`
- API 版本化（Framework 7）：`@GetMapping(value = "/api/books", version = "1.1")`——版本号从请求头/查询参数解析，解析策略（头名、参数名、默认版本）需在应用配置中显式声明，具体属性名以所用 Framework 7.x 文档为准。

## 💡 示例

```java
// 下游 404 是业务状态而非系统异常：onStatus 转业务异常
try {
    return client.get().uri("/books/{isbn}", isbn)
        .retrieve()
        .onStatus(status -> status.value() == 404, (req, res) ->
            { throw new BookFetchException(isbn, res.getStatusCode()); })
        .body(Book.class);
} catch (BookFetchException e) {
    return Book.placeholder(e.getIsbn());      // 降级
}
```

## ⚠️ 常见陷阱

- **不配超时**：底层默认值依请求工厂而异；缺少明确预算时，下游抖动可能耗尽调用资源
- **RestTemplate 继续写新代码**：维护模式，无新特性（如 API 版本化）
- **WebClient 用于纯同步场景**：白白引入 Reactor 依赖与响应式心智负担
- **把下游 404 当系统异常**：查无此资源是业务状态，用 `onStatus` 转业务异常处理
- **exchange() 的状态处理**：普通回调形式会在回调完成后关闭响应，且不执行 retrieve 的状态处理器；显式选择不自动关闭的变体时才需自己负责生命周期，不要从回调返回已关闭的流

<!-- full-library-explanation -->
## 一次远程调用有多个失败阶段

连接超时、等待响应超时、HTTP 错误和 JSON 解码失败是不同问题。下游返回 404 是否能降级取决于契约：查询可选资料可以为空，调用错误路径也可能是部署故障。401/403 通常需要修复凭据或权限，不能与 404 一起吞掉并伪造成功数据。

RestClient 使用同步调用模型，WebClient 使用响应式模型，HTTP 接口代理则把参数映射成请求。代理不会自动定义重试、幂等或认证。创建订单的 POST 超时后，下游可能已经完成写入；盲目重试可能创建两份订单，应使用约定的幂等键或查询结果确认。

**练习**：用本地替身服务分别返回正常 JSON、204、404、401、无效 JSON 和慢响应，断言每种场景如何映射到业务结果。给连接池、重试次数及总调用预算设上限，确保三次单次 5 秒超时不会意外超过上游 8 秒的预算。保存日志时记录目标服务和关联 ID，避免记录认证头与完整敏感响应。

依据：[Spring REST 客户端](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html)。本页配置为片段，需要相关类型导入与业务 DTO。

## 🔗 相关条目

- 📄 **[Spring Boot 核心速查](./01-spring-boot-essentials.md)** - 自动配置的 RestClient.Builder
- 📄 **[生产级 Spring Boot 应用](../../projects/04-production-spring-app.md)** - 下游调用与降级
- 📄 **[三方库指南](../library-guides/02-third-party-libs.md)** - JSON 序列化配合
- 📄 **[故障排除速查](../quick-references/02-troubleshooting.md)** - 常见连接类报错


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
