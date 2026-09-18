# Spring Security 7 速查

> **文档简介**: Spring Security 7（Boot 4 默认）的核心概念与最小可用配置速查：认证/授权模型、SecurityFilterChain DSL、密码编码、方法安全与测试
>
> **目标读者**: 需要快速接入或查阅 Security 配置的开发者；深度实践见 [Spring Security 最佳实践](../../advanced-topics/security/01-security-practices.md)
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
| **标签** | `#SpringSecurity` `#认证授权` `#DSL` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

- **认证（Authentication）**：确认"你是谁"——凭据校验成功后把 `Authentication` 放入 `SecurityContext`。
- **授权（Authorization）**：确认"你能做什么"——URL 规则由过滤器链裁决，方法注解由方法安全拦截器裁决。
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
        .httpBasic(org.springframework.security.config.Customizer.withDefaults())
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .build(); // CSRF 保持启用；修改操作需提供合法 CSRF token
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
- `hasRole("ADMIN")` 自动补 `ROLE_` 前缀；`hasAuthority("ROLE_ADMIN")` 不会——两种表达可以表达同一权限，关键是保持存储的 authority 与比较值一致

## 💡 示例

```java
// 方法级授权：角色或资源所有者
@PreAuthorize("hasRole('ADMIN') or @authz.canReadLoan(authentication, #loanId)")
public Loan detail(Long memberId, Long loanId) { ... }

// 测试中模拟登录态（security-test 提供）
@Test
@WithMockUser(roles = "ADMIN")
void adminCanList() throws Exception {
    // mockMvc 须在启用了 Spring Security 的测试配置中注入
    mockMvc.perform(org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get("/api/admin/books"))
        .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers.status().isOk());
}
```

## ⚠️ 常见陷阱

- **明文/MD5 存密码**：必须 BCrypt/Argon2（见[安全最佳实践](../../advanced-topics/security/01-security-practices.md)）
- **用了 `@PreAuthorize` 但没开 `@EnableMethodSecurity`**：注解静默不生效，授权形同虚设
- **`hasRole`/`hasAuthority` 混用**：`ROLE_` 前缀差一个，403 就找不到原因
- **按“无状态”盲目关闭 CSRF**：先确认凭据是否由浏览器自动携带，再为具体认证方式配置策略；403 也可能来自授权或其他过滤器
- **所有路径 `permitAll()` 图省事**：默认应为 `anyRequest().authenticated()`，白名单逐条放行
- **自建用户密码未 encode**：会导致验证失败；DelegatingPasswordEncoder 缺少 {id} 前缀时可能出现映射错误，BCryptPasswordEncoder 的行为不同（见[故障排除速查](../quick-references/02-troubleshooting.md)）

<!-- full-library-explanation -->
## 身份、角色与资源所有者要分别验证

认证成功只说明当前主体通过凭据验证。拥有 USER 角色不代表能读取所有用户的借阅记录；授权必须把实际 loanId 对应的所有者与当前主体比较，不能只相信请求参数里的 memberId。示例 authz.canReadLoan 应从可信存储读取资源归属；它是需实现的业务授权 Bean，不是框架内置方法。

CSRF 取决于浏览器是否自动携带凭据，而非服务端是否创建 Session。Cookie 内的 JWT 和浏览器缓存的 Basic 凭据仍可能被自动携带。只接受调用方显式设置 Authorization 的 Bearer API，可在确认没有 Cookie/Basic 等替代认证入口后单独配置 CSRF 策略。CORS 不能替代该分析。

**练习**：建立用户 A、用户 B 和管理员，为无凭据、错误凭据、合法角色但他人资源、合法本人资源分别写测试。@WithMockUser 可配合启用 Security 的 MockMvc 模拟同进程请求，不会自动把登录态发送到独立 HTTP 服务器；真实 HTTP 测试必须携带实际凭据。

参见 [Spring Security 的无状态应用与 CSRF 说明](https://docs.spring.io/spring-security/reference/features/exploits/csrf.html)。以下基础配置使用教学 Basic 认证并保留 CSRF，用户密码仅用于本地演示。

## 🔗 相关条目

- 📄 **[Spring Security 最佳实践](../../advanced-topics/security/01-security-practices.md)** - 纵深防御与 OAuth2/JWT
- 📄 **[Spring Boot 核心速查](./01-spring-boot-essentials.md)** - Security 自动配置
- 📄 **[图书管理系统项目](../../projects/02-library-management.md)** - 认证落地实战
- 📄 **[故障排除速查](../quick-references/02-troubleshooting.md)** - 401/403 常见报错


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
