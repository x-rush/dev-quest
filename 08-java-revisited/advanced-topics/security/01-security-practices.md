# Spring Security 最佳实践 - 从过滤器链到纵深防御

> **文档简介**: 解释 Spring Security 的运行模型并给出生产级实践：过滤器链与认证流程、OAuth2/JWT 资源服务器、权限模型设计、输入与配置的安全收敛——按攻击面组织而非按 API 罗列
>
> **目标读者**: 已接入 Spring Security、想把它做"对"的后端开发者
>
> **前置知识**: [生态集成](../../frameworks/03-ecosystem-integration.md)、[图书管理系统的认证](../../projects/02-library-management.md)、[异常处理](../../basics/06-exceptions.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#SpringSecurity` `#OAuth2` `#JWT` `#纵深防御` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- 理解 SecurityFilterChain 的过滤器流水线与认证时刻
- 为系统选择正确的认证架构（Session/JWT/OAuth2 授权服务器）
- 建立"最小权限 + 纵深防御"的配置习惯

## 🔍 一、运行模型：一切都发生在过滤器链里

```text
HTTP 请求
  └─▶ SecurityFilterChain（一串 Filter，按序执行）
        ├── CsrfFilter            CSRF 令牌校验（有状态 API 才启用）
        ├── BearerTokenAuthFilter 从 Authorization 头解析 JWT
        ├── ...
        └── AuthorizationFilter   按 authorizeHttpRequests 规则裁决
```

两个关键时刻：

1. **认证（Authentication）**：`BearerTokenAuthFilter` 等解析凭据，成功则把 `Authentication` 放入 `SecurityContext`（无状态模式下基于请求作用域）
2. **授权（Authorization）**：`AuthorizationFilter` 统一裁决，`hasRole("ADMIN")` 背后是 `ROLE_ADMIN` 的字符串比对

**心智模型**：Security 不是"一个注解"，而是一条流水线。调试认证问题时，开启 `logging.level.org.springframework.security=TRACE` 观察每个过滤器的放行/拒绝。

## 🛠️ 二、认证架构选型

| 架构 | 适用 | Java 侧实现 |
|------|------|------------|
| Session + Cookie | 传统 Web、单域名 | 默认表单登录即可 |
| JWT 资源服务器 | 前后端分离 / 微服务 | `oauth2ResourceServer().jwt()` |
| 授权服务器（中央 IdP） | 多服务统一登录 | Keycloak / Spring Authorization Server |

### JWT 资源服务器的生产配置

```java
@Bean
SecurityFilterChain apiChain(HttpSecurity http) throws Exception {
    return http
        .securityMatcher("/api/**")                 // 只管 API，不越界
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/public/**").permitAll()
            .anyRequest().authenticated())
        .oauth2ResourceServer(o -> o.jwt(jwt -> jwt
            .decoder(jwtDecoder())                  // 校验签名与受众
            .jwtAuthenticationConverter(converter()))) // 声明 → 权限映射
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .build();
}

@Bean
JwtDecoder jwtDecoder() {
    return JwtDecoders.fromIssuerLocation("https://idp.example.com"); // 发现端点
}
```

### JWT 的三条红线

1. **必须验签**：信任发行方公钥（JWKS），绝不 `alg: none`
2. **校验受众与过期**：`iss`/`aud`/`exp` 全部核对，token 只是"签名过的声明"不是通行证
3. **短有效期 + 刷新**：访问令牌 15 分钟级，撤销靠刷新令牌管理，不搞"十年 JWT"

## 🛠️ 三、授权模型设计

### 分层授权：粗到细

```java
// 第一层：URL 粗粒度（过滤器链）
.requestMatchers("/api/admin/**").hasRole("ADMIN")

// 第二层：方法细粒度（注解）
@PreAuthorize("hasRole('LOAN_ADMIN') or #memberId == principal.memberId")
public Loan detail(Long memberId, Long loanId) { ... }

// 第三层：数据行级（Service 内显式判断）
if (!loan.getMemberId().equals(currentUser.id()) && !currentUser.isAdmin()) {
    throw new AccessDeniedException("只能查看自己的借阅");
}
```

**越权（IDOR）是最常见的 Java API 漏洞**：URL 里换个 `loanId` 就能看别人的数据。URL/方法注解挡不住它，行级检查必须落进业务代码。

## 🛠️ 四、纵深防御清单

### 输入与注入

- SQL 一律参数绑定（JPA/JPQL 参数化，见 [JPA 速查](../../reference/framework-essentials/02-jpa-essentials.md)）；拼接 `@Query` 字符串即注入
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
- 无状态 API（`Authorization` 头带 token）**没有 CSRF 风险**，可安全关闭；Cookie 认证必须保留 CSRF 防护

## 🎨 最佳实践

### ✅ 推荐
- 默认全拒绝（`anyRequest().authenticated()`），白名单放行
- 安全规则集中一个 `SecurityConfig`，代码评审时一眼可查
- 认证失败与"不存在"返回相同响应（401 vs 404 泄露资源存在性）

### ❌ 陷阱
- `permitAll()` 越积越多：每次"临时放开"都变成永久后门
- 把用户 ID 存 JWT 明文字段当权限依据：token 签发后角色变更不生效，权限要实时查
- 依赖 `SecurityContextHolder` 全局可变性：无状态模式下按请求读取即可

## 🔗 相关文档

### 本模块
- 📖 [Spring Boot 核心速查](../../reference/framework-essentials/01-spring-boot-essentials.md) — Security 自动配置
- 📖 [Java 关键字详解](../../reference/language-concepts/01-java-keywords.md) — `synchronized`/`final` 的安全含义
- 📄 [生态集成](../../frameworks/03-ecosystem-integration.md) — Security 7 基础配置
- 📄 [图书管理系统项目](../../projects/02-library-management.md) — 认证落地实战
- 📄 [生产级 Spring Boot 应用](../../projects/04-production-spring-app.md) — 密钥管理与配置收敛
