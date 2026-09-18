# 安全实践：认证、注入与前端数据安全

> **文档简介**: 系统梳理 TanStack 应用的安全清单：token 存储权衡、XSS/CSRF 防线、路由授权与数据缓存的敏感信息治理。
>
> **目标读者**: 要为生产应用做安全评审的资深开发者
>
> **前置知识**: [SaaS 后台的认证流](../../projects/04-saas-admin-platform.md)、[Router 框架要点](../../reference/framework-essentials/02-router-essentials.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#安全` `#xss` `#csrf` `#认证授权` `#token` |
| **更新日期** | 2026年9月 |

</details>

---

## 1. Token 存储：没有完美选项，只有权衡

| 方案 | XSS 风险 | CSRF 风险 | 适用 |
|------|----------|-----------|------|
| localStorage + Bearer | 可被 JS 读取（XSS 即失守） | 无（不自动携带） | 已有严格 CSP、API 无 Cookie 生态 |
| HttpOnly Secure Cookie | JS 不可读 | 需 SameSite + CSRF token | 同域部署、传统会话 |
| 内存 + 静默续期（Refresh in HttpOnly） | 页面刷新丢失，靠续期恢复 | 同上 | SPA 常见折中 |

**结论**：攻击者若能执行任意 JS（XSS 得手），任何前端存储都守不住——真正的第一道防线是**不产生 XSS**（§2），存储方案只是纵深防御的第二层。[SaaS 后台](../../projects/04-saas-admin-platform.md) 的 localStorage 方案须以本节前提为条件。

---

## 2. XSS 防线

- **不渲染不可信 HTML**：React 默认转义，`dangerouslySetInnerHTML` 出现即应触发代码评审；确需渲染富文本时用 DOMPurify 白名单消毒
- **CSP 兜底**：

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' https://cdn.example.com;
  connect-src 'self' https://api.example.com;
  object-src 'none';
  frame-ancestors 'none';
```

先检查 Vite 实际产物是否包含内联脚本；需要时选择哈希或 nonce 等策略。不要无依据加入 unsafe-inline，也不要假定平台自动注入 nonce。

- **依赖供应链**：`npm audit` 进 CI；Lockfile 提交；关键脚本（MSW 的 worker、Sentry loader）走官方渠道或自托管

**常见攻击面速查**：

| 攻击面 | 入口 | 防线 |
|--------|------|------|
| XSS | 富文本渲染、URL 参数回显 | React 默认转义 + DOMPurify + CSP |
| CSRF | Cookie 凭据自动携带 | SameSite=Lax + CSRF token 头 |
| 点击劫持 | iframe 嵌套 | `frame-ancestors 'none'` |
| 供应链 | npm 依赖、CDN 脚本 | Lockfile + audit 进 CI + SRI |

---

## 3. CSRF：Cookie 方案的必修课

自动携带的认证凭据会带来 CSRF 风险，Cookie 是常见情况：

- `Set-Cookie: session=...; HttpOnly; Secure; SameSite=Lax`——Lax 挡住绝大多数跨站 POST
- 写操作加 CSRF token（服务端下发、`X-CSRF-Token` 头回传），或改用自定义头 + CORS 白名单的双校验
- **与 Query 的配合点**：mutation 的 `http` 封装里统一注入 CSRF 头（见 [SaaS 后台 http.ts](../../projects/04-saas-admin-platform.md)），散写必漏

---

## 4. 授权：认证之后的事

**认证（你是谁）≠ 授权（你能干什么）**。前端授权是"体验优化"，服务端才是执法者：

1. **路由层**：[beforeLoad 守卫](../../projects/04-saas-admin-platform.md)——无权跳转/404，防止用户"看到不该看的界面"
2. **组件层**：IfAllowed 隐藏写按钮——防止误操作，但**不防恶意调用**
3. **服务端**：每个 API 独立鉴权（IDOR 检查：`GET /api/orders/999` 必须校验 999 是否属于当前用户）——前端永远不可信任

```ts
// 服务端视角的 IDOR 检查示例（Node/Express 伪码）
app.get('/api/orders/:id', requireAuth, async (req, res) => {
  const order = await db.orders.findById(req.params.id)
  if (!order || order.orgId !== req.session.orgId) {
    return res.status(404).json({ message: 'not found' }) // 404 而非 403，不暴露存在性
  }
  res.json(order)
})
```

---

## 5. 缓存中的敏感数据

Query 缓存会持久驻留内存，还会被 Devtools 完整展示：

- **登出/切换账号必 `queryClient.clear()`**——防止下一用户从缓存读到前任数据（含乐观快照）
- **敏感字段前端脱敏**：缓存里只存展示需要的数据（服务端裁剪返回），不存全量对象
- **SSR/Start 场景的 dehydrate**：序列化进 HTML 的缓存会出现在页面源码里——敏感键务必排除（按键前缀过滤 dehydratedState）
- **共享电脑场景**：`gcTime` 再长也不能替代登出清理；sessionStorage 仅改变生命周期，同样能被同源脚本读取，不能作为敏感数据的安全保证

---

## 6. 上线前安全清单

- [ ] CSP 头已配置且无 `unsafe-eval`
- [ ] 全站 HTTPS，Cookie 带 Secure/HttpOnly/SameSite
- [ ] 富文本渲染经 DOMPurify 消毒
- [ ] 每个写接口服务端独立鉴权（抽查 IDOR）
- [ ] 登出清空 Query 缓存 + 撤销服务端会话
- [ ] `npm audit` 无 high/critical 进 CI
- [ ] Sentry 等第三方域名在 CSP connect-src 白名单内
- [ ] 安全响应头齐备（HSTS、X-Content-Type-Options、Referrer-Policy）
- [ ] 生产构建的 sourcemap 不随产物公开分发

---

<!-- full-library-explanation -->
## 从账号切换验证缓存隔离

先修：Cookie、HTTP 授权、Query 生命周期。建立 A/B 两个测试账号，A 登录时发起延迟请求，随后退出并登录 B。清理旧缓存后，如果 A 的在途响应仍可写回，B 仍可能看到旧数据。因此要同时设计取消、查询键身份、持久化清理与服务端授权。

敏感字段必须在服务器响应前裁剪。浏览器收到完整对象后再隐藏字段，无法撤回已经发送的数据。dehydrate 的过滤也要在服务端完成，不能等页面加载后才清理 HTML 中的秘密。

CSP nonce 需要与当前响应中的脚本标记匹配；静态 SPA、动态 SSR 与 CDN 缓存的部署方式不同，不存在自动适用所有项目的注入方案。先采用实际构建产物所需策略，再用浏览器报告验证。

**练习：** A 访问 B 的资源 ID、登出后重放写请求、切账号时让旧请求晚返回。验收：服务端拒绝越权，客户端不显示旧账号数据，日志不含令牌。参考[OWASP 授权](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)与[CSRF 防护](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)。

## 🔗 相关文档

- 📄 **[SaaS 后台](../../projects/04-saas-admin-platform.md)** - 本清单的工程载体
- 📄 **[Router 框架要点](../../reference/framework-essentials/02-router-essentials.md)** - 守卫与 SSR 集成参数
- 📄 **[缓存架构与数据流](../architecture/01-cache-architecture.md)** - 敏感数据驻留内存的机制
- 📄 **[可观测性](../../deployment/03-observability.md)** - 安全事件的发现通道
- 📄 **[环境搭建](../../basics/01-environment-setup.md)** - 依赖安装的供应链起点


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
