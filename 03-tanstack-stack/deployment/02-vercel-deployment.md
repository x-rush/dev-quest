# Vercel 部署：SPA 与 SSR 双路径

> **文档简介**: 把 TanStack 应用部署到 Vercel：SPA 的重写规则与缓存策略，以及迁移到 TanStack Start（SSR）时的部署差异。
>
> **目标读者**: 完成 CI 搭建、需要稳定交付通道的开发者
>
> **前置知识**: [CI/CD 流水线](./01-ci-cd-pipelines.md)、[Router 基础](../basics/05-router-fundamentals.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#vercel` `#部署` `#spa` `#ssr` |
| **更新日期** | 2026年9月 |

## 🎯 完成后你将能够

- 修复 SPA 深链 404，配置合理的静态资源缓存
- 区分构建期与运行期环境变量
- 了解 TanStack Start 路线下的部署差异

---

## 1. 接入 Vercel

```bash
npm i -g vercel
vercel        # 首次：关联项目，生成 .vercel 配置
vercel --prod # 部署生产
```

推荐 Git 集成模式：连接仓库后，**每个 PR 自动生成 Preview 部署**，`main` 分支自动进 Production——PR 评审直接点开预览链接验收。

---

## 2. SPA 部署配置

纯客户端渲染（Vite + TanStack Router）必须处理两件事：**所有路径回落 index.html**、**静态资源长缓存**。

```json
// vercel.json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        // Vite 产物带内容哈希，可安全一年缓存
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    },
    {
      "source": "/index.html",
      "headers": [
        // 入口 HTML 不缓存，发版立即生效
        { "key": "Cache-Control", "value": "no-cache" }
      ]
    }
  ]
}
```

**深链 404 的根因**：刷新 `/dashboard/users/7` 时服务器找不到该文件；rewrites 让服务器统一返回 SPA 入口，由 Router 接管路径。

**框架预设**：Vercel 检测到 Vite 会自动填 `Build Command: vite build`、`Output Directory: dist`，通常无需手配。

---

## 3. 环境变量管理

```bash
vercel env add VITE_API_BASE_URL        # 引导式添加
vercel env pull .env.local              # 拉到本地开发
```

| 类型 | 例子 | 特点 |
|------|------|------|
| 构建期（`VITE_*`） | API 地址、功能开关 | 编译时内联进 JS，**对用户可见** |
| 运行期（仅 SSR/Start） | 密钥、第三方 token | 只存在于服务端函数 |

**Preview / Production 分离**：同一个变量在不同环境配不同值（如 preview 连测试后端），避免预览环境污染生产数据。

---

## 4. TanStack Start（SSR）路线

若迁移到 TanStack Start（基于 Router 的全栈框架），部署方式改变：

- `vite build` 产出服务端 bundle，Vercel 以 Nitro/serverless target 承载，**不再需要 SPA rewrites**
- 服务端函数里可以安全使用运行期环境变量（密钥不进前端产物）
- Router 的 loader 在服务端预取：首屏即带数据，SEO 友好
- Query 在 SSR 场景用 `dehydrate/hydrate` 把服务端缓存注入客户端（见 [Router 框架要点](../reference/framework-essentials/02-router-essentials.md)）

**迁移建议**：SPA 已经稳定运行的团队不必急于迁移；有 SEO/首屏诉求的新页面可按路由逐步 SSR 化。

---

## 5. 发版检查清单

- [ ] Preview 部署打开 `/dashboard` 深链不 404
- [ ] 硬刷新后静态资源命中 immutable 缓存（DevTools Network 验证）
- [ ] index.html 为 no-cache，新版发布后旧标签页能拿到新入口
- [ ] `VITE_*` 中无任何密钥（`grep -r "sk_\|secret" dist/` 无结果）
- [ ] Web Vitals 与 Sentry 接入生产域名（见 [可观测性](./03-observability.md)）

---

## ❓ 常见坑

| 现象 | 原因 | 修复 |
|------|------|------|
| 深链刷新 404 | 缺 SPA rewrites | 补 vercel.json rewrites |
| 发版后用户停在旧版本 | index.html 被中间层缓存 | no-cache 头 |
| 预览环境连了生产库 | 环境变量未分环境 | Preview/Production 分别配置 |
| 改了 VITE_* 但页面没变 | 构建期变量需重新构建 | 触发 Redeploy |

---

## 🔗 相关文档

- 📄 **[CI/CD 流水线](./01-ci-cd-pipelines.md)** - 构建产物从哪来
- 📄 **[可观测性](./03-observability.md)** - 部署后的监控闭环
- 📄 **[Router 框架要点](../reference/framework-essentials/02-router-essentials.md)** - SSR 集成与 hydration
- 📄 **[安全实践](../advanced-topics/security/01-security-practices.md)** - 环境变量与密钥治理
- 📄 **[SaaS 后台](../projects/04-saas-admin-platform.md)** - 完整交付链路的落点
