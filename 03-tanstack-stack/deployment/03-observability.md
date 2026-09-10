# 可观测性：Sentry 与 Web Vitals

> **文档简介**: 为上线后的应用装上仪表盘：Sentry 捕获并聚合运行时错误，Web Vitals 量化真实用户体验，并把 Query 错误流接入统一上报。
>
> **目标读者**: 应用已上线或即将上线、需要线上问题预警的开发者
>
> **前置知识**: [Vercel 部署](./02-vercel-deployment.md)、[SaaS 后台的错误处理](../projects/04-saas-admin-platform.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#sentry` `#web-vitals` `#监控` `#可观测性` |
| **更新日期** | 2026年9月 |

## 🎯 完成后你将能够

- 接入 Sentry：错误自动聚合、版本标注、source map 还原
- 把 Query 的失败率变成可告警的指标
- 采集 Core Web Vitals 并回传分析

---

## 1. Sentry 接入

```bash
npm install @sentry/react
```

```ts
// src/main.tsx（入口最上方，先于任何业务代码）
import * as Sentry from '@sentry/react'

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE, // production / preview
  release: __APP_VERSION__,          // vite.config.ts 里 define 注入 package.json version
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({ maskAllInputs: true }), // 会话回放，输入脱敏
  ],
  tracesSampleRate: 0.2,  // 性能采样 20%，控制成本
  replaysSessionSampleRate: 0.01,
})
```

```ts
// vite.config.ts —— 注入版本号，让错误能对上发布的版本
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
})
```

**source map**：构建时生成、上传后从产物中删除——`npx @sentry/wizard@latest -i sourcemaps -p vite` 一条命令配置完成；错误堆栈即可还原到源码行。

---

## 2. Query 错误流接入上报

### 2.1 全局兜底

```ts
// src/shared/query-client.ts
import { QueryCache, MutationCache, QueryClient } from '@tanstack/react-query'
import * as Sentry from '@sentry/react'

export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {
      // queryKey 是定位问题的关键上下文
      Sentry.captureException(error, {
        tags: { queryKey: JSON.stringify(query.queryKey), layer: 'query' },
      })
    },
  }),
  mutationCache: new MutationCache({
    onError: (error, _vars, _ctx, mutation) => {
      Sentry.captureException(error, {
        tags: { mutationKey: JSON.stringify(mutation.options.mutationKey ?? []), layer: 'mutation' },
      })
    },
  }),
})
```

> 注意：这是监控上报，与 [SaaS 后台](../projects/04-saas-admin-platform.md) 中的用户提示（toast）互补——onError 里可以同时做 toast 与 captureException，但建议收敛到一个 `reportError()` 工具避免重复上报。

### 2.2 错误边界兜住渲染异常

```tsx
import * as Sentry from '@sentry/react'

// 提供现成的 ErrorBoundary：渲染期异常自动上报
export const RouteErrorBoundary = Sentry.withErrorBoundary(PageComponent, {
  fallback: <ErrorPage />,
})
```

**三层防线**：queryCache.onError（数据请求失败）→ ErrorBoundary（渲染崩溃）→ window.onerror（全局残留），覆盖面才完整。

---

## 3. Web Vitals 采集

```bash
npm install web-vitals
```

```ts
// src/shared/vitals.ts
import { onCLS, onINP, onLCP, onTTFB, type Metric } from 'web-vitals'

function report(metric: Metric) {
  // 方案 A：发给自有分析端点
  navigator.sendBeacon?.('/api/vitals', JSON.stringify({
    name: metric.name,       // CLS | INP | LCP | TTFB
    value: metric.value,
    rating: metric.rating,   // good | needs-improvement | poor
    path: location.pathname,
    version: __APP_VERSION__,
  }))
}

onCLS(report); onINP(report); onLCP(report); onTTFB(report)
```

**关注指标与 Query 的关系**：

| 指标 | 与数据层的关联 |
|------|----------------|
| LCP | 首屏查询是否被 loader 预取覆盖 |
| INP | 交互后是否有意外的大范围 refetch 阻塞主线程 |
| CLS | keepPreviousData 缺失导致的表格塌陷抖动 |

---

## 4. 告警与复盘闭环

- **告警规则**：Sentry Alert 上配置"同 fingerprint 10 分钟内 > 5 次"通知（Slack/邮件）；Web Vitals 的 poor 占比周环比上涨 20% 触发 review
- **发版对照**：每次 release 后观察 24h 新增 issue 数，回归错误立刻可见
- **复盘路径**：Sentry issue → 回放视频 → 复现 queryKey → 本地 Devtools 重放

---

## 🎨 最佳实践速查

- ✅ release 版本号贯穿"构建 → 上报 → source map"三处，否则错误无法归版
- ✅ 采样率分级：错误 100%，性能 10~20%，回放 1%
- ❌ 不要把 Sentry DSN 当密钥藏——它本来就是公开的，靠项目级权限控制
- ❌ 不要在 onError 里既 toast 又直接 captureException 又打日志——收敛为一个 reportError 入口

---

## 🔗 相关文档

- 📄 **[Vercel 部署](./02-vercel-deployment.md)** - 环境变量与发版流程
- 📄 **[CI/CD 流水线](./01-ci-cd-pipelines.md)** - release 版本号从哪来
- 📄 **[渲染性能](../advanced-topics/performance/02-rendering-performance.md)** - INP/CLS 恶化的根因分析
- 📄 **[SaaS 后台](../projects/04-saas-admin-platform.md)** - 错误处理架构总图
- 📄 **[故障排除](../reference/quick-references/02-troubleshooting.md)** - 本地复现线上错误的排查路径
