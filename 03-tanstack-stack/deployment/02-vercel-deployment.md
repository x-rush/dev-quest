# Vercel 部署：SPA 与 SSR 双路径

> **文档简介**: 把 TanStack 应用部署到 Vercel：SPA 的重写规则与缓存策略，以及迁移到 TanStack Start（SSR）时的部署差异。
>
> **目标读者**: 完成 CI 搭建、需要稳定交付通道的开发者
>
> **前置知识**: [CI/CD 流水线](./01-ci-cd-pipelines.md)、[Router 基础](../basics/05-router-fundamentals.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#vercel` `#部署` `#spa` `#ssr` |
| **更新日期** | 2026年9月 |

</details>

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

文件：`vercel.json`（标准 JSON 不允许注释）。

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    },
    {
      "source": "/index.html",
      "headers": [
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

- `vite build` 产出服务端 bundle，由当前 Start 与 Vercel 支持的适配器产出服务端部署，**不再需要 SPA rewrites**
- 服务端函数里可以安全使用运行期环境变量（密钥不进前端产物）
- Router 的 loader 在服务端预取：首屏即带数据，SEO 友好
- Query 在 SSR 场景用 `dehydrate/hydrate` 把服务端缓存注入客户端（见 [Router 框架要点](../reference/framework-essentials/02-router-essentials.md)）

**迁移建议**：SPA 已经稳定运行的团队不必急于迁移；有 SEO/首屏诉求的新页面可按路由逐步 SSR 化。

---

## 5. 发版检查清单

- [ ] Preview 部署打开 `/dashboard` 深链不 404
- [ ] 硬刷新后静态资源命中 immutable 缓存（DevTools Network 验证）
- [ ] 深链 HTML 的实际响应支持重验证；刷新或重新访问能发现新入口，旧标签页不会自动升级
- [ ] 审查 VITE_* 变量与实际客户端产物；关键词扫描只能辅助，零匹配不能证明无密钥
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

<!-- full-library-explanation -->
## 路由回退和缓存需要实际响应验证

先修：Vite 构建、HTTP 缓存、客户端路由。SPA 回退解决 HTML 入口查找，不会修复 API 路径或不存在的资源；若项目有同域 API，不应把 API 错误重写成状态 200 的 index.html。

no-cache 表示使用前重验证，不是不存储。已经打开的标签页也不会仅因为这个响应头自动升级 JavaScript；需要刷新或应用自己的更新提示。检查深链 URL 的实际响应头，不能只检查 /index.html。

带内容哈希的资源可以长期缓存，入口 HTML 应允许及时发现新版本。缺失脚本若被回退成 HTML，浏览器可能报告 MIME 类型错误；应分别测试真实资源、缺失资源、深链和 API。

**练习：** 在 Preview 直接打开深链并刷新，再发布带版本标识的新构建，比较旧标签页和新访问。验收：能解释缓存命中与重验证，预览只连接测试服务。SSR/Start 部署按[当前 Hosting 文档](https://tanstack.com/start/latest/docs/framework/react/guide/hosting)配置适配器，不能把所有版本都称为同一种 Nitro 输出。

## 🔗 相关文档

- 📄 **[CI/CD 流水线](./01-ci-cd-pipelines.md)** - 构建产物从哪来
- 📄 **[可观测性](./03-observability.md)** - 部署后的监控闭环
- 📄 **[Router 框架要点](../reference/framework-essentials/02-router-essentials.md)** - SSR 集成与 hydration
- 📄 **[安全实践](../advanced-topics/security/01-security-practices.md)** - 环境变量与密钥治理
- 📄 **[SaaS 后台](../projects/04-saas-admin-platform.md)** - 完整交付链路的落点


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
