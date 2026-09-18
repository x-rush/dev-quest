# 端到端 API 测试策略

> **文档简介**: 构建面向用户旅程的端到端 API 测试——真实依赖环境、关键业务流断言、与 CI 的集成方式，为发布提供最终置信度
>
> **目标读者**: 已建立单元/集成测试体系、负责发布质量的中高级后端开发者
>
> **前置知识**: [集成测试](02-integration-testing.md)、[容器化部署](../deployment/01-docker-deployment.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#e2e` `#api-testing` `#smoke-test` `#ci` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 本节目标

- 划定 E2E 测试的边界：测什么、不测什么
- 用 Docker Compose 编排真实依赖环境
- 把 E2E 作为 CI 的发布门禁

## 1. 测试金字塔中的 E2E 定位

```
        ╱ E2E ╲          少而关键：完整环境 + 用户旅程
       ╱ 集成  ╲         中等数量：模块协作 + 真实数据库
      ╱ 单元    ╲        海量：业务规则毫秒级反馈
```

**E2E 只测"用户旅程"**：注册 → 登录 → 创建 → 消费 → 登出这样的端到端剧本。单条规则的错误分支、分页换算等细节已在单元/集成层覆盖，重复测试只会拖慢反馈。

## 2. 环境：Compose 编排真实依赖

E2E 的价值来自真实——数据库、缓存、应用本身全部是真实进程：

```yaml
# docker-compose.e2e.yml —— E2E 专用环境，端口避开开发默认值
services:
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_PASSWORD: e2e-pass
      POSTGRES_DB: app_e2e
    ports: ["55432:5432"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 2s
      retries: 15

  redis:
    image: redis:7-alpine
    ports: ["56379:6379"]

  app:
    build: .                    # 用生产 Dockerfile 构建——顺带验证镜像可用
    environment:
      DATABASE_URL: postgresql://postgres:e2e-pass@postgres:5432/app_e2e
      REDIS_URL: redis://redis:6379
      JWT_ACCESS_SECRET: e2e-secret-e2e-secret-e2e-secret-32!
      PORT: "3000"
    ports: ["53000:3000"]
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_started }
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/livez"]
      interval: 2s
      retries: 15
```

```bash
# 运行 E2E 套件（与单元测试分开）
pnpm exec vitest run --config vitest.e2e.config.ts
```

```typescript
// vitest.e2e.config.ts —— E2E 单独成套，互不拖累
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['e2e/**/*.test.ts'],
    fileParallelism: false, // 按顺序执行，避免旅程之间相互污染
    testTimeout: 30_000,
  },
});
```

## 3. 用户旅程测试

```typescript
// e2e/user-journey.test.ts —— 一条完整的业务剧本
import { describe, it, expect } from 'vitest';

// E2E 直连运行中的容器，不再 import 源码
const BASE = process.env.E2E_BASE_URL ?? 'http://localhost:53000';

describe('用户完整旅程', () => {
  let accessToken: string;

  it('注册 → 登录 → 创建任务 → 查询', async () => {
    // 1) 注册
    const reg = await fetch(`${BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'journey@example.com', password: 's3curePass!' }),
    });
    expect(reg.status).toBe(201);

    // 2) 登录，取 access token
    const login = await fetch(`${BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'journey@example.com', password: 's3curePass!' }),
    });
    expect(login.status).toBe(200);
    const body = await login.json() as { accessToken: string };
    accessToken = body.accessToken;

    // 3) 创建任务
    const created = await fetch(`${BASE}/todos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ title: 'E2E 旅程任务', priority: 'high' }),
    });
    expect(created.status).toBe(201);

    // 4) 查询验证可见
    const list = await fetch(`${BASE}/todos?status=open`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    const listBody = await list.json() as { items: Array<{ title: string }> };
    expect(listBody.items.some((t) => t.title === 'E2E 旅程任务')).toBe(true);
  });

  it('健康探针可用（冒烟测试）', async () => {
    const res = await fetch(`${BASE}/livez`);
    expect(res.status).toBe(200);
  });
});
```

## 4. E2E 在 CI 中的位置

```text
PR 打开   → lint + typecheck + unit（秒级反馈，阻塞合并）
PR 合并前 → 全部集成测试（分钟级）
发布候选  → compose.e2e 起环境 → E2E 旅程通过 → 才允许构建镜像推送
```

具体流水线写法见 [`../deployment/02-ci-cd-pipelines.md`](../deployment/02-ci-cd-pipelines.md)。

## ✅ 最佳实践与陷阱

端到端测试通过真实运行入口完成业务旅程，关键字段如创建后的 id、金额或权限结果仍必须验证，不能因“只测旅程”而省掉契约断言。底层组合边界留给更快的测试，减少重复成本。

使用接近发布的构建产物并隔离测试数据，失败保留服务日志、请求信息和产物版本。先定位失败，再决定重试；否则暂时变绿可能掩盖竞态。

## 🔗 相关文档

- 📄 [集成测试](02-integration-testing.md) — E2E 的上一层基础
- 📄 [生产级 Node.js API](../projects/04-production-nodejs-api.md) — E2E 作为上线门禁
- 📄 [CI/CD 流水线](../deployment/02-ci-cd-pipelines.md) — E2E 的自动化运行
- 📖 [Node 一行式速查](../reference/quick-references/01-node-cheatsheet.md) — 相关 CLI 命令


<!-- acceptance-exercise -->
## 练习与验收：增加一个越权失败旅程

除正常创建和查询外，准备两个测试账号：A 创建资源，B 尝试读取与修改，预期按产品协议拒绝且数据不变。再用 A 删除后查询，确认返回约定的不存在结果。验收保存请求状态、关键返回字段和资源 ID，测试仅清理本次创建的资源；健康接口 200 不足以证明认证、授权和持久化链路正常。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
