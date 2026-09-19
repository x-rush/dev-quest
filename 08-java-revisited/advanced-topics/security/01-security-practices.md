# Spring Security 最佳实践 - 从过滤器链到纵深防御

> **文档简介**: 解释 Spring Security 的运行模型并给出生产级实践：过滤器链与认证流程、OAuth2/JWT 资源服务器、权限模型设计、输入与配置的安全收敛——按攻击面组织而非按 API 罗列
>
> **目标读者**: 已接入 Spring Security、想把它做"对"的后端开发者
>
> **前置知识**: [生态集成](../../frameworks/03-ecosystem-integration.md)、[图书管理系统的认证](../../projects/02-library-management.md)、[异常处理](../../basics/06-exceptions.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#SpringSecurity` `#OAuth2` `#JWT` `#纵深防御` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- 理解 SecurityFilterChain 的过滤器流水线与认证时刻
- 为系统选择正确的认证架构（Session/JWT/OAuth2 授权服务器）
- 建立"最小权限 + 纵深防御"的配置习惯

## 🔍 一、运行模型：一切都发生在过滤器链里

```text
HTTP 请求
  └─▶ SecurityFilterChain（一串 Filter，按序执行）
        ├── CsrfFilter            CSRF 令牌校验（按凭据是否自动附带决定）
        ├── BearerTokenAuthenticationFilter 从 Authorization 头解析 Bearer 凭据
        ├── ...
        └── AuthorizationFilter   按 authorizeHttpRequests 规则裁决
```

两个关键时刻：

1. **认证（Authentication）**：`BearerTokenAuthenticationFilter` 交给认证提供者验证凭据，成功则把 `Authentication` 放入 `SecurityContext`（无状态模式下基于请求作用域）
2. **授权（Authorization）**：`AuthorizationFilter` 统一裁决，`hasRole("ADMIN")` 背后是 `ROLE_ADMIN` 的字符串比对

**心智模型**：Security 不是"一个注解"，而是一条流水线。只在受控调试环境临时开启 `logging.level.org.springframework.security=TRACE`，使用测试身份并检查日志是否包含敏感信息；不能把生产访问令牌连同日志复制到工单。

## 🛠️ 二、认证架构选型

| 架构 | 适用 | Java 侧实现 |
|------|------|------------|
| Session + Cookie | 传统 Web、单域名 | 默认表单登录即可 |
| JWT 资源服务器 | 前后端分离 / 微服务 | `oauth2ResourceServer().jwt()` |
| 授权服务器（中央 IdP） | 多服务统一登录 | Keycloak / Spring Authorization Server |

### JWT 资源服务器的最小集成配置

适用于只接受显式 `Authorization: Bearer` 的服务，依赖 Spring Boot 的 OAuth2 Resource Server starter。以下配置类放入组件扫描路径；发行方地址为占位符，需要替换为真实且可信的 OIDC/OAuth2 提供方。它不签发令牌，也不实现撤销。若同时接受 Cookie、Basic 或浏览器自动附带的其他凭据，应保留 CSRF 并另行设计过滤器链。

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.oauth2.core.DelegatingOAuth2TokenValidator;
import org.springframework.security.oauth2.core.OAuth2Error;
import org.springframework.security.oauth2.core.OAuth2TokenValidator;
import org.springframework.security.oauth2.core.OAuth2TokenValidatorResult;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtValidators;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;

@Configuration
public class ApiSecurity {
    @Bean
    JwtDecoder jwtDecoder(
            @Value("${spring.security.oauth2.resourceserver.jwt.issuer-uri}") String issuer,
            @Value("${app.jwt-audience}") String audience) {
        NimbusJwtDecoder decoder = NimbusJwtDecoder.withIssuerLocation(issuer).build();
        OAuth2TokenValidator<Jwt> requiredClaims = jwt -> {
            boolean valid = jwt.getExpiresAt() != null && jwt.getSubject() != null
                && !jwt.getSubject().isBlank() && jwt.getAudience() != null
                && jwt.getAudience().contains(audience);
            return valid ? OAuth2TokenValidatorResult.success()
                : OAuth2TokenValidatorResult.failure(new OAuth2Error("invalid_token"));
        };
        decoder.setJwtValidator(new DelegatingOAuth2TokenValidator<>(
            JwtValidators.createDefaultWithIssuer(issuer), requiredClaims));
        return decoder;
    }

    @Bean
    SecurityFilterChain apiChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable()) // 仅在上述“显式 Bearer、无自动凭据”前提成立时
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/**").authenticated()
                .anyRequest().denyAll())
            .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .build();
    }
}
```

在 `application.yml` 提供自定义 decoder 的两个服务端参数：

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://idp.example.com/issuer
app:
  jwt-audience: todo-api
```

`JwtDecoders.fromIssuerLocation(...)` 本身不能替你猜出服务的受众；默认时间验证也不能当成“必需字段存在”的业务契约。这里自定义 decoder，组合默认发行方/时间验证与必需 exp、sub、aud 检查。若使用 Boot 自动 decoder，`spring.security.oauth2.resourceserver.jwt.audiences` 可以校验受众；一旦提供自定义 decoder，则要自己保留相应检查，不能认为所有自动配置仍生效。本例保留默认 `SCOPE_` 权限映射。需要角色时先明确定义来自可信令牌的 claim 到权限的映射。此处默认使用 Nimbus 的 RS256 验签策略，IdP 必须提供对应算法；`withIssuerLocation(...).build()` 会依赖可信发现服务的可达性，超时与启动策略需在实际环境配置。

这里采用覆盖所有请求的单条链，最后显式拒绝未知路径。使用 `securityMatcher("/api/**")` 时，链只处理匹配路径；它不会自动保护其他 URL，必须另有兜底链。多链顺序也需要验收。

### JWT 的三条红线

1. **必须验签**：信任发行方公钥（JWKS），绝不 `alg: none`
2. **校验受众与过期**：`iss`/`aud`/`exp` 全部核对，token 只是"签名过的声明"不是通行证
3. **有效期与撤销分开设计**：访问令牌有效期按风险与重认证成本选择。撤销刷新令牌只阻止继续刷新，已经签发的访问令牌通常仍可用到到期；即时封禁需要内省、撤销表或业务状态检查

## 🛠️ 三、授权模型设计

### 分层授权：粗到细

```java
// 第一层：URL 粗粒度（过滤器链）
.requestMatchers("/api/admin/**").hasRole("ADMIN")

// 第二层：方法细粒度（注解）
@PreAuthorize("hasAuthority('SCOPE_loans:read')")
public Loan detail(Long loanId) { ... }

// 第三层：数据行级（Service 内显式判断）
if (!loan.getMemberId().equals(currentUser.id()) && !currentUser.isAdmin()) {
    throw new AccessDeniedException("只能查看自己的借阅");
}
```

第二层片段需要启用 `@EnableMethodSecurity`，并通过 Spring 代理调用。JWT 的默认 principal 是 `Jwt`，不能假设它有业务字段 `memberId`。由已验证的 `sub` 查找内部用户，不能信任请求里传来的 memberId。方法授权可以调用实际对象权限规则；上例的 scope 只表达操作能力，仍需第三层对象检查或带 owner 条件的数据查询。

越权（IDOR）意味着更换 `loanId` 就能访问别人的数据。写操作尽量将当前用户条件放进同一数据库语句或事务，避免授权检查完成后对象归属发生变化。

## 🛠️ 四、纵深防御清单

### 输入与注入

- 外部值用 SQL/JPQL 参数绑定（见 [JPA 速查](../../reference/framework-essentials/02-jpa-essentials.md)）；真正的注入点是把不可信输入拼进查询语法。动态排序字段用允许列表，常量字符串组合本身不等于漏洞
- 反序列化白名单化：Jackson 多态只走注册子类
- 文件上传：校验 MIME + 大小 + 存储路径不可控（防路径穿越 `../`）

### 配置面收敛

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health        # /env /heapdump 不暴露
  endpoint:
    health:
      show-details: never
spring:
  web:
    error:
      include-stacktrace: never  # 异常细节不给客户端（Boot 4.0 起 server.error.* 迁入 spring.web.error.*）
```

### 密码与密钥

- BCrypt/Argon2 存哈希（见 [生态集成](../../frameworks/03-ecosystem-integration.md)），禁止 MD5/SHA-1
- 密钥轮换预案：JWT 用 JWKS 多 kid 并存，先加新钥再删旧钥
- 环境变量注入，Git 历史也要扫（gitleaks 进 CI）

### CORS 与 CSRF 的真相

- **CORS 是浏览器的约束**，对 curl/Postman 无效——它不是访问控制，只是同源策略的协商机制
- CSRF 判断看凭据是否被浏览器自动附带，不看服务端是否保存 session。只有确认所有受保护入口仅接受显式 Bearer 头、没有 Cookie/Basic 等备用认证路径，才能按该威胁模型关闭 CSRF；Cookie 认证需要 CSRF 防护

## 以拒绝矩阵验收配置

先用本地测试 IdP 或测试私钥签发令牌，在真实过滤器链中发送请求。`@WithMockUser` 和 MockMvc 的 `jwt()` 可验证权限映射，但不会证明真实签名、issuer、audience 校验已经工作。

| 请求 | 预期结果 |
|---|---|
| 无凭据访问 `/api/public/ping` | 业务定义的公开成功响应 |
| 无凭据访问私有 API；错误签名、过期、缺 exp、空 sub、错误受众令牌 | 401，业务方法不执行 |
| 正确令牌，缺少方法需要的 scope | 403 |
| 用户 A 的正确令牌访问用户 B 的借阅 | 统一的 403 或隐藏资源策略下的 404，不返回借阅正文 |
| 已登录用户访问 `/internal/export` 等未知路径 | 被兜底规则拒绝，不应绕过安全链 |
| Cookie 认证写请求缺 CSRF 凭据 | 拒绝且数据库未变更 |

每项同时断言响应与数据副作用；仅断言非 200 不足以证明没有写入。框架配置仍需在项目锁定依赖和真实 IdP 下做集成验证。

依据：[Spring Resource Server 的 issuer 与 audience 配置](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)、[CSRF 与无状态浏览器应用](https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html)。

## 🎨 最佳实践

安全规则要分别表达公开访问、必须登录与资源授权。anyRequest().authenticated() 要求身份认证，并不等于“默认拒绝全部”；真正禁止请求与允许已登录者是不同策略。对路由与方法建立测试矩阵，确认公开例外没有覆盖敏感接口。

有效令牌可证明已签发身份，但角色变化、撤销与资源归属还需按业务时效校验。401、403、404 的选择按认证协议与资源隐藏策略统一设计，不把所有失败强行返回同一种状态。跨用户访问测试比只检查安全注解存在更有价值。

## 🔗 相关文档

### 本模块
- 📖 [Spring Boot 核心速查](../../reference/framework-essentials/01-spring-boot-essentials.md) — Security 自动配置
- 📖 [Java 关键字详解](../../reference/language-concepts/01-java-keywords.md) — `synchronized`/`final` 的安全含义
- 📄 [生态集成](../../frameworks/03-ecosystem-integration.md) — Security 7 基础配置
- 📄 [图书管理系统项目](../../projects/02-library-management.md) — 认证落地实战
- 📄 [生产级 Spring Boot 应用](../../projects/04-production-spring-app.md) — 密钥管理与配置收敛


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
