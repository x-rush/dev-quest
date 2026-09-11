# 可观测性：pino 日志 + OpenTelemetry/Sentry

> **文档简介**: 为生产 Node 服务建立三支柱可观测性——pino 结构化日志与请求 ID 贯穿、OpenTelemetry 分布式追踪、Sentry 错误聚合，让线上问题可定位可复盘
>
> **目标读者**: 服务已上线或即将上线、需要运维能力的中高级后端开发者
>
> **前置知识**: [生产级 API](../projects/04-production-nodejs-api.md) 的探针与优雅关闭、[CI/CD](02-ci-cd-pipelines.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#pino` `#opentelemetry` `#sentry` `#logging` |
| **更新日期** | `2026年9月` |

## 🎯 本节目标

- 用 pino 输出机器可解析的结构化日志
- 用请求 ID 把一次请求的所有日志串成一条线
- 接入 OpenTelemetry 追踪与 Sentry 错误聚合

## 1. pino：结构化日志基座

```bash
pnpm add pino
```

```typescript
// src/lib/logger.ts —— 全局唯一的日志出口
import pino from 'pino';
import { env } from '../config/env.js';

export const logger = pino({
  level: env.LOG_LEVEL,
  base: { service: 'todo-api', env: env.NODE_ENV }, // 每条日志附带服务标识
  // 生产写 JSON 到 stdout（采集器接管）；开发用 pino-pretty 人类可读
  transport: env.NODE_ENV === 'development'
    ? { target: 'pino-pretty', options: { translateTime: 'HH:MM:ss' } }
    : undefined,
  redact: {
    paths: ['req.headers.authorization', '*.password', '*.token'], // 敏感字段脱敏
    censor: '[REDACTED]',
  },
});
```

```typescript
// src/middleware/request-log.ts —— 请求日志 + 请求 ID 注入
import { randomUUID } from 'node:crypto';
import type { MiddlewareHandler } from 'hono';
import type { Logger } from 'pino';
import { logger } from '../lib/logger.js';

// 类型扩展：c.get('requestId') / c.get('log') 获得完整类型提示（见字典 05-typescript-patterns）
declare module 'hono' {
  interface ContextVariableMap { requestId: string; log: Logger; }
}

export const requestContext: MiddlewareHandler = async (c, next) => {
  // 优先采信上游网关的 x-request-id（跨服务串联），否则自生成
  const requestId = c.req.header('x-request-id') ?? randomUUID();
  c.set('requestId', requestId);
  c.set('log', logger.child({ requestId })); // 子 logger 自动带 ID
  c.header('x-request-id', requestId);       // 回传给客户端便于反馈

  const start = performance.now();
  await next(); // 洋葱模型：next() 返回即响应出站，等价于 Express 的 res 'finish'
  c.get('log').info({
    method: c.req.method,
    url: c.req.path,
    status: c.res.status,
    durationMs: Math.round(performance.now() - start),
  }, 'request');
};
```

业务代码里统一用 `c.get('log')` 而非 console：

```typescript
app.post('/todos', async (c) => {
  const body = await c.req.json(); // 请求体只能消费一次，先存变量
  c.get('log').debug({ body }, '创建任务'); // 自带 requestId，可全文检索
  return c.json(await todoService.create(body), 201);
});
```

## 2. OpenTelemetry：分布式追踪

一次请求横跨 API → Prisma → Redis 时，追踪能给出每跳耗时：

```typescript
// src/telemetry.ts —— 必须在所有其他 import 之前加载
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';

const sdk = new NodeSDK({
  serviceName: 'todo-api',
  // 本地可指向 Jaeger 的 OTLP 端点，生产对接采集器
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT,
  }),
  instrumentations: [getNodeAutoInstrumentations()], // 自动埋点 http/pg/ioredis（Hono 跑在 node-server 的 http 层，天然被覆盖）
});

sdk.start();

// 防止进程退出时丢失缓冲中的 span
process.on('SIGTERM', () => { void sdk.shutdown(); });
```

```bash
# server.ts 第一行加载（早于业务 import，确保埋点覆盖所有模块）
node --import ./dist/telemetry.js dist/server.js
```

**采样策略**：流量大时全量采样成本高，生产常用按 TraceID 比例采样（如 10%）+ 错误请求全采。

## 3. Sentry：错误聚合与告警

```bash
pnpm add @sentry/node
```

```typescript
// src/lib/sentry.ts —— 错误追踪优先于路由初始化
import * as Sentry from '@sentry/node';
import { env } from '../config/env.js';

Sentry.init({
  dsn: process.env.SENTRY_DSN,             // 未配置时 init 是 no-op，开发无副作用
  environment: env.NODE_ENV,
  release: process.env.APP_VERSION,        // 与 CI 构建版本对齐，错误可溯源
  tracesSampleRate: 0.1,                   // 性能追踪采样 10%
});
```

```typescript
// error-handler.ts 中把未知错误交给 Sentry（保留自有的响应逻辑）
import * as Sentry from '@sentry/node';

if (err instanceof HttpError) { /* ...返回业务错误... */ }

Sentry.captureException(err);          // 未知错误：聚合同类、触发告警
return res.status(500).json({ error: '服务器内部错误' });
```

## 4. 三支柱如何协作排障

一次 500 报障的定位链路：

```text
用户报障 + x-request-id
→ 日志系统按 requestId 查出该请求全部日志（含耗时与状态码）
→ 日志中的 trace_id 跳转 OpenTelemetry 瀑布图，看到卡在 Prisma 查询 4s
→ Sentry 中同一 trace 的异常堆栈，确认是连接池耗尽
→ 回到 troubleshooting 字典定位修复
```

- 日志回答"发生了什么"；追踪回答"时间花在哪"；错误聚合回答"谁的锅、影响面多大"。

## ✅ 最佳实践与陷阱

- ✅ 日志写 stdout，由采集器（Loki/ELK）接管——容器时代不要自己写日志文件
- ✅ 每个 handler 用 `c.get('log')`，让 requestId 自动贯穿
- ❌ `console.log(obj)` 打印大对象——热路径上的同步序列化会拖慢事件循环（见 [`../advanced-topics/performance/01-event-loop.md`](../advanced-topics/performance/01-event-loop.md)）
- ❌ 日志里记录完整 token/身份证号——`redact` 必须在上线前配置

## 🔗 相关文档

- 📄 [生产级 Node.js API](../projects/04-production-nodejs-api.md) — 探针与优雅关闭的来源
- 📄 [CI/CD 流水线](02-ci-cd-pipelines.md) — release 版本号如何进入 Sentry
- 📖 [常见故障排除](../reference/quick-references/02-troubleshooting.md) — 日志定位后的修复手册
- 📄 [事件循环原理](../advanced-topics/performance/01-event-loop.md) — 追踪图异常耗时的原理侧
