# Spring Boot 3 → 4 迁移速查

> **文档简介**: Boot 3.x 升级到 4.x 的高频变化条目式对照：基线要求、starter 改名、属性迁移、Jackson 3、测试栈替换与部署变化——升级前先过一遍这张清单
>
> **目标读者**: 正在评估或执行 Boot 3 → 4 升级的团队
>
> **前置知识**: [Spring Boot 核心速查](../framework-essentials/01-spring-boot-essentials.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Boot4` `#迁移` `#Jackson3` |
| **更新日期** | `2026年9月` |

## 📌 定义（基线与升级路线）

- **推荐路线**：先升到 3.5.x 最新补丁 → 4.0 → 4.1，逐版本消化弃用项；过程中临时引入 `spring-boot-properties-migrator`（runtime 依赖，迁移完移除）自动报告属性改名。
- **基线对比**：

| 项 | Boot 3.x | Boot 4.x |
|----|----------|----------|
| Java | 17+ | 17+（推荐 25 LTS；Native Image 需 25）|
| Spring Framework | 6.x | 7.0.x |
| Jakarta EE | 10 | 11（Servlet 6.1 / JPA 3.2 / Validation 3.1）|
| Servlet 容器 | Tomcat 10.1 | Tomcat 11 / Jetty 12.1；**Undertow 移除** |
| 构建 | Maven 3.6.3+ / Gradle 7.5+ | Maven 3.6.3+ / Gradle 8.14+（8.x 需 8.14 或 9.x）|
| 测试 | JUnit 5 + Testcontainers 1.x | JUnit 6 + Testcontainers 2.0 |

## 📖 语法 / 签名（starter 与属性改名）

### starter 改名对照

| Boot 3 | Boot 4 |
|--------|--------|
| `spring-boot-starter-web` | `spring-boot-starter-webmvc` |
| `spring-boot-starter-aop` | `spring-boot-starter-aspectj` |
| （随 data-jpa/web 传递引入） | Flyway/Liquibase 需显式 `spring-boot-starter-flyway` / `-liquibase` |
| `spring-boot-starter-test` 一把梭 | 按技术拆分的 `-test` starter（均传递引入 starter-test）|

### 属性迁移对照

| Boot 3 | Boot 4 | 风险 |
|--------|--------|------|
| `server.error.include-message` | `spring.web.error.include-message` | **无别名，静默失效** |
| `server.error.whitelabel.enabled` | `spring.web.error.whitelabel.enabled` | 同上 |
| `server.error.path` | `spring.web.error.path` | 同上 |
| `spring.jackson.*`（配置 Jackson 2）| Jackson 3 沿用 `spring.jackson.*`（语义/默认值变化）；Jackson 2 过渡走 `spring.jackson2.*` | 混淆高发 |

"静默失效"意味着旧属性不报错也不生效——升级后错误响应里 `message` 字段"神秘消失"，多半是这里。

## 💡 示例（Jackson 3 适配）

```java
// 依赖坐标：com.fasterxml.jackson.* → tools.jackson.core（仅 jackson-annotations 不变）
// 类型：可变 ObjectMapper → 不可变 JsonMapper（builder 配置）
var mapper = JsonMapper.builder().build();
```

| 行为 | Jackson 2 默认 | Jackson 3 默认 |
|------|---------------|---------------|
| 未知属性 | 抛错（`FAIL_ON_UNKNOWN_PROPERTIES=true`）| 忽略 |
| 尾随 token | 容忍 | 抛错（`FAIL_ON_TRAILING_TOKENS=true`）|
| 日期序列化 | 时间戳 | ISO-8601 字符串 |
| 属性排序 | 声明序 | 字母序（`SORT_PROPERTIES_ALPHABETICALLY=true`）|

- `java.time`/`Optional` 支持已内建 databind，无需再注册 `JavaTimeModule`
- 定制入口：`JsonMapperBuilderCustomizer`；过渡兜底：`spring.jackson.use-jackson2-defaults=true`

```xml
<!-- 迁移期临时依赖：启动时报告全部待迁移属性 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-properties-migrator</artifactId>
    <scope>runtime</scope>
</dependency>
```

## ⚠️ 常见陷阱（易漏清单）

- `@MockBean`/`@SpyBean` 已移除 → `@MockitoBean`/`@MockitoSpyBean`
- Testcontainers 2.0：模块 artifact 加 `testcontainers-` 前缀（如 `testcontainers-postgresql`）；JUnit 4 支持移除
- REST Assured 不再由 Boot BOM 管理——继续用需显式指定版本；官方新推 `RestTestClient`
- 镜像构建：`layertools` 模式移除，改用 `jarmode=tools`（见 [Docker 部署](../../deployment/01-docker-deployment.md)）
- 4.1 起 `-DskipTests` **不再**跳过测试 AOT 处理——CI 时长异常时改用 `-Dmaven.test.skip=true`
- DevTools 的 LiveReload 服务器在 4.1 标记废弃
- 旧 `server.error.*` 属性静默失效（见上表），升级后错误响应差异先查这里

## 🔗 相关条目

- 📄 **[Spring Boot 核心速查](../framework-essentials/01-spring-boot-essentials.md)** - 4.x 概念全貌
- 📄 **[三方库指南](../library-guides/02-third-party-libs.md)** - Jackson 3 / JUnit 6 / Mockito 细节
- 📄 **[故障排除速查](./02-troubleshooting.md)** - 升级后报错对照
- 📄 **[单元测试](../../testing/01-unit-testing.md)** - JUnit 6 / @MockitoBean
- 📄 **[Docker 部署](../../deployment/01-docker-deployment.md)** - jarmode=tools
