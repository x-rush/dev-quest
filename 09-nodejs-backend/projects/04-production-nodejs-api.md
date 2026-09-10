# 精通项目：生产级 Node.js API

> **文档简介**: 综合本模块全部知识，交付一个达到生产标准的 API 服务——配置校验、优雅关闭、限流、可观测性、容器化与 CI/CD 的完整闭环
>
> **目标读者**: 已完成⭐⭐项目、准备把服务真正上线的中高级后端开发者
>
> **前置知识**: 全部 frameworks 与 projects 文档、[集成测试](../testing/02-integration-testing.md)、[容器化部署](../deployment/01-docker-deployment.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#production` `#graceful-shutdown` `#rate-limit` `#observability` `#精通项目` |
| **更新日期** | `2026年9月` |

架构层面的"为什么"见 [`../advanced-topics/architecture/01-service-architecture.md`](../advanced-topics/architecture/01-service-architecture.md)，本文按上线路径推进。

## 🎯 项目目标

- 建立"启动即失败"的配置校验纪律
- 实现 SIGTERM 优雅关闭，零停机发布
- 接入限流、结构化日志与健康探测的完整运维面

## 1. 生产目录结构

```
src/
├── app.ts            # Express 组装（无监听）
├── server.ts         # 监听 + 生命周期管理
├── config/env.ts     # 启动时环境变量校验
├── lib/              # prisma.ts / redis.ts / logger.ts
├── middleware/       # auth / error-handler / rate-limit
├── routes/           # 按资源拆分
└── services/         # 业务逻辑
```

## 2. 配置即合同：启动时校验环境变量

```typescript
// src/config/env.ts —— 用 Zod 让"缺配置"在部署的第 1 秒暴露
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  JWT_ACCESS_SECRET: z.string().min(32), // 密钥长度强制下限
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
});

const parsed = envSchema.safeParse(process.env);
if (!parsed.success) {
  console.error('环境变量校验失败:', parsed.error.flatten().fieldErrors);
  process.exit(1); // 宁可不启动，不要带病运行
}

export const env = parsed.data;
```

## 3. 优雅关闭：零停机发布的关键

K8s/Docker 滚动更新时发 SIGTERM，服务必须：停止接新请求 → 等存量请求完成 → 释放连接 → 退出。

```typescript
// src/server.ts
import app from './app.js';
import { env } from './config/env.js';
import { prisma } from './lib/prisma.js';
import { redis } from './lib/redis.js';

const server = app.listen(env.PORT);

const shutdown = async (signal: string) => {
  console.log(`收到 ${signal}，开始优雅关闭`);

  // 1) 停止接受新连接，存量请求继续处理
  server.close(async (err) => {
    if (err) console.error('关闭监听失败', err);
  });

  // 2) 兜底超时：卡住的请求最多再等 10 秒
  const forceTimer = setTimeout(() => process.exit(1), 10_000);
  forceTimer.unref(); // 不阻止正常退出

  // 3) 释放连接池
  await Promise.allSettled([prisma.$disconnect(), redis.quit()]);

  console.log('关闭完成');
  clearTimeout(forceTimer);
  process.exit(0);
};

process.on('SIGTERM', () => void shutdown('SIGTERM')); // 容器编排标准信号
process.on('SIGINT', () => void shutdown('SIGINT'));   // Ctrl+C
```

> 注意：负载均衡摘除流量通常在 SIGTERM 前有一个传播延迟（K8s 默认 `terminationGracePeriodSeconds` 30s），需要 readiness 探针配合（见第 5 节）。

## 4. 限流与防护

```typescript
// src/middleware/rate-limit.ts —— Redis 支撑的多实例全局限流
import rateLimit from 'express-rate-limit';
import { RedisStore } from 'rate-limit-redis';
import { redis } from '../lib/redis.js';

export const apiLimiter = rateLimit({
  windowMs: 60_000,           // 统计窗口 1 分钟
  limit: 120,                 // 单 IP 每窗口 120 次
  standardHeaders: 'draft-8', // 返回 RateLimit-* 标准响应头
  legacyHeaders: false,
  // 内存存储在多实例下各算各的，生产必须换 Redis
  store: new RedisStore({ sendCommand: (...args: string[]) => redis.sendCommand(args) }),
});

// 认证接口单独收紧：防暴力破解
export const authLimiter = rateLimit({ windowMs: 15 * 60_000, limit: 10 });
```

```typescript
// src/app.ts 组装
app.use('/api', apiLimiter);
app.use('/auth/login', authLimiter);
```

## 5. 可观测性三件套

```typescript
// 结构化日志：pino 输出 JSON，便于采集系统解析（完整方案见 deployment/03）
import pino from 'pino';
export const logger = pino({
  level: env.LOG_LEVEL,
  base: { service: 'todo-api', version: process.env.APP_VERSION ?? 'dev' },
});

// 探针区分 liveness 与 readiness：
app.get('/livez', (_req, res) => res.json({ status: 'ok' }));            // 进程活着就 200
app.get('/readyz', async (_req, res) => {                                 // 依赖就绪才 200
  try {
    await prisma.$queryRaw`SELECT 1`;
    res.json({ status: 'ready' });
  } catch {
    res.status(503).json({ status: 'db-down' }); // 未就绪 → 编排摘除流量
  }
});
```

- 日志：pino 结构化输出 + 请求 ID 贯穿（[`../deployment/03-observability.md`](../deployment/03-observability.md)）
- 错误追踪：Sentry 捕获未处理异常（同上）
- 指标：事件循环延迟探测（[`../advanced-topics/performance/01-event-loop.md`](../advanced-topics/performance/01-event-loop.md)）

## 6. 上线清单

- [ ] 环境变量启动时校验，缺配置立即退出
- [ ] SIGTERM 优雅关闭实测通过（发信号后存量请求全部完成）
- [ ] 全局限流 + 登录限流已启用且走 Redis
- [ ] liveness/readiness 探针就绪，端到端测试全绿（[`../testing/03-e2e-api-testing.md`](../testing/03-e2e-api-testing.md)）
- [ ] 多阶段 Docker 构建，非 root 运行（[`../deployment/01-docker-deployment.md`](../deployment/01-docker-deployment.md)）
- [ ] GitHub Actions 完成测试→构建→推送→部署（[`../deployment/02-ci-cd-pipelines.md`](../deployment/02-ci-cd-pipelines.md)）
- [ ] 密钥全部来自运行时注入，仓库零明文（[`../advanced-topics/security/01-security-practices.md`](../advanced-topics/security/01-security-practices.md)）

## 🔗 相关文档

- 📄 [服务架构与模块化单体](../advanced-topics/architecture/01-service-architecture.md) — 生产项目的结构设计依据
- 📄 [事件循环原理](../advanced-topics/performance/01-event-loop.md) — 上线前的性能体检
- 📄 [可观测性](../deployment/03-observability.md) — pino/OpenTelemetry/Sentry 详解
- 📖 [常见故障排除](../reference/quick-references/02-troubleshooting.md) — 生产故障速查
