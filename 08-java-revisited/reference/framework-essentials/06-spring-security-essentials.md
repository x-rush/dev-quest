# Spring Security 7 速查

> **文档简介**: Spring Security 7（Boot 4 默认）的核心概念与最小可用配置速查：认证/授权模型、SecurityFilterChain DSL、密码编码、方法安全与测试
>
> **目标读者**: 需要快速接入或查阅 Security 配置的开发者；深度实践见 [Spring Security 最佳实践](../../advanced-topics/security/01-security-practices.md)
>
> **前置知识**: [Spring Boot 入门](../../frameworks/01-spring-boot-basics.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#SpringSecurity` `#认证授权` `#DSL` |
| **更新日期** | `2026年9月` |

## 📌 定义

- **认证（Authentication）**：确认"你是谁"——凭据校验成功后把 `Authentication` 放入 `SecurityContext`。
- **授权（Authorization）**：确认"你能做什么"——`AuthorizationFilter` 按 URL 规则与方法注解裁决。
- **SecurityFilterChain**：一组按序执行的过滤器构成的安全流水线，每个请求先过它再到业务。
- **Security 7 相对 6 的关键点**：延续并只保留 Lambda DSL，6.x 时代的 `and()` 链式拼接写法在 7 中不再可用。

## 📖 语法 / 签名

```java
// 最小可用配置（Security 7 / Boot 4）
@Bean
SecurityFilterChain security(HttpSecurity http) throws Exception {
    return http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/public/**").permitAll()
            .anyRequest().authenticated())
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .build();
}

@Bean
PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();      // 存储：encode() 一次，校验：matches()
}

@Bean
UserDetailsService users(PasswordEncoder encoder) {
    return new InMemoryUserDetailsManager(
        User.withUsername("alice").password(encoder.encode("secret")).roles("USER").build());
}
```

- 依赖：`spring-boot-starter-security`；测试另加 `spring-boot-starter-security-test`（提供 `@WithMockUser` 等）
- 方法安全：`@EnableMethodSecurity` 开启后可用 `@PreAuthorize`/`@PostAuthorize`
- `hasRole("ADMIN")` 自动补 `ROLE_` 前缀；`hasAuthority("ROLE_ADMIN")` 不会——两者不可混搭

## 💡 示例

```java
// 方法级授权：角色或资源所有者
@PreAuthorize("hasRole('ADMIN') or #memberId == principal.memberId")
public Loan detail(Long memberId, Long loanId) { ... }

// 测试中模拟登录态（security-test 提供）
@Test
@WithMockUser(roles = "ADMIN")
void adminCanList() {
    given().when().get("/api/admin/books").then().statusCode(200);
}
```

## ⚠️ 常见陷阱

- **明文/MD5 存密码**：必须 BCrypt/Argon2（见[安全最佳实践](../../advanced-topics/security/01-security-practices.md)）
- **用了 `@PreAuthorize` 但没开 `@EnableMethodSecurity`**：注解静默不生效，授权形同虚设
- **`hasRole`/`hasAuthority` 混用**：`ROLE_` 前缀差一个，403 就找不到原因
- **无状态 token API 忘记关 CSRF**：POST 全部 403；反过来 Cookie 会话绝不能关
- **所有路径 `permitAll()` 图省事**：默认应为 `anyRequest().authenticated()`，白名单逐条放行
- **自建用户密码未 encode**：登录即抛 `There is no PasswordEncoder mapped for the id "null"`（见[故障排除速查](../quick-references/02-troubleshooting.md)）

## 🔗 相关条目

- 📄 **[Spring Security 最佳实践](../../advanced-topics/security/01-security-practices.md)** - 纵深防御与 OAuth2/JWT
- 📄 **[Spring Boot 核心速查](./01-spring-boot-essentials.md)** - Security 自动配置
- 📄 **[图书管理系统项目](../../projects/02-library-management.md)** - 认证落地实战
- 📄 **[故障排除速查](../quick-references/02-troubleshooting.md)** - 401/403 常见报错
