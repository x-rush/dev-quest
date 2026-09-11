# REST 客户端与 HTTP 服务速查

> **文档简介**: Spring HTTP 客户端家族的条目式速查：同步 RestClient、响应式 WebClient、声明式 HTTP Service Clients 与 Framework 7 的 API 版本化
>
> **目标读者**: 需要调用下游 HTTP 服务、为旧 RestTemplate 找替代的开发者
>
> **前置知识**: [Spring Boot 入门](../../frameworks/01-spring-boot-basics.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#RestClient` `#WebClient` `#声明式HTTP` `#API版本化` |
| **更新日期** | `2026年9月` |

## 📌 定义

| 客户端 | 定位 | 依赖 |
|--------|------|------|
| `RestClient` | 同步、流式 API；**RestTemplate 的现代替代**（Spring 6.1+）| `spring-boot-starter-restclient` |
| `WebClient` | 响应式（Reactor）；需要流式/高并发非阻塞时选它 | `spring-boot-starter-webclient`（Boot 4 起独立 starter）|
| 声明式 HTTP 接口 | 接口 + `@HttpExchange` 注解，框架生成实现（Spring 6+）| 同 RestClient |
| API 版本化 | Framework 7 新增：同一 URL 按版本路由到不同处理方法 | Framework 7 |

- RestTemplate 处于维护模式：不再新增功能，新代码一律从 RestClient 起步。

## 📖 语法 / 签名

```java
// RestClient：链式调用，一行一发
RestClient client = RestClient.builder()
    .baseUrl("https://api.example.com")
    .defaultHeader("Accept", "application/json")
    .build();

Book book = client.get().uri("/books/{isbn}", isbn)
    .retrieve().body(Book.class);

// 超时必须显式配置（默认无限等待）
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
        .onStatus(HttpStatusCode::is4xxClientError, (req, res) ->
            { throw new BookFetchException(isbn, res.getStatusCode()); })
        .body(Book.class);
} catch (BookFetchException e) {
    return Book.placeholder(e.getIsbn());      // 降级
}
```

## ⚠️ 常见陷阱

- **不配超时**：默认无限等待，下游抖动会拖垮整条调用链与线程池
- **RestTemplate 继续写新代码**：维护模式，无新特性（如 API 版本化）
- **WebClient 用于纯同步场景**：白白引入 Reactor 依赖与响应式心智负担
- **把下游 404 当系统异常**：查无此资源是业务状态，用 `onStatus` 转业务异常处理
- **`exchange()` 手动管理响应**：必须保证响应关闭，否则连接泄漏；能用 `retrieve()` 就不用 `exchange()`

## 🔗 相关条目

- 📄 **[Spring Boot 核心速查](./01-spring-boot-essentials.md)** - 自动配置的 RestClient.Builder
- 📄 **[生产级 Spring Boot 应用](../../projects/04-production-spring-app.md)** - 下游调用与降级
- 📄 **[三方库指南](../library-guides/02-third-party-libs.md)** - JSON 序列化配合
- 📄 **[故障排除速查](../quick-references/02-troubleshooting.md)** - 常见连接类报错
