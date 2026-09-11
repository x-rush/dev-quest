# CI/CD 流水线：GitHub Actions

> **文档简介**: 为 Node.js 24 + pnpm 项目搭建完整的 GitHub Actions 流水线——测试门禁、Docker 镜像构建推送与自动化部署，附带 pnpm 缓存加速实践
>
> **目标读者**: 已完成容器化、需要自动化发布的中级后端开发者
>
> **前置知识**: [单元/集成测试](../testing/01-unit-testing.md)、[容器化部署](01-docker-deployment.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#github-actions` `#ci-cd` `#pnpm` `#docker` |
| **更新日期** | `2026年9月` |

## 🎯 本节目标

- 建立分层的流水线：PR 快速门禁 → 合并前全量测试 → 发布构建
- 为 pnpm 与 Vitest 配置缓存，缩短反馈时间
- 自动化镜像推送与部署触发

## 1. 流水线分层设计

```text
ci.yml（PR 触发）:
  ① check   — typecheck + lint        （~30s，并行）
  ② unit    — Vitest 单元测试          （~1min，并行）
  ③ integration — app.request() 集成测试（带 PostgreSQL service）

release.yml（打 tag 触发）:
  ④ 复用 ci 检查 → 构建 Docker 镜像 → 推送 registry → 触发部署
```

原则：**PR 阶段越快越好**（并行 + 缓存），重的 E2E 放在发布候选阶段（见 [`../testing/03-e2e-api-testing.md`](../testing/03-e2e-api-testing.md)）。

## 2. PR 门禁流水线

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # pnpm 缓存三件套：setup-node 自带 pnpm store 缓存支持
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with:
          node-version: 24
          cache: pnpm
      - run: pnpm install --frozen-lockfile

      - run: pnpm typecheck
      - run: pnpm lint

  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 24, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm test:cov   # 覆盖率低于阈值自动失败

  integration:
    runs-on: ubuntu-latest
    services:
      postgres:                       # service 容器：测试库的 CI 化
        image: postgres:17-alpine
        env:
          POSTGRES_PASSWORD: ci-pass
          POSTGRES_DB: app_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 2s --health-retries 15
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
    env:
      DATABASE_URL: postgresql://postgres:ci-pass@localhost:5432/app_test
      REDIS_URL: redis://localhost:6379
      JWT_ACCESS_SECRET: ci-secret-ci-secret-ci-secret-32!
      NODE_ENV: test
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 24, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec prisma migrate deploy
      - run: pnpm exec vitest run tests/
```

> 密钥规则：CI 中只允许**合成测试值**；真实密钥通过 `secrets.*` 注入且只出现在 release 流程。

## 3. 发布流水线：构建 → 推送 → 部署

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags: ["v*"]

jobs:
  quality-gate:
    uses: ./.github/workflows/ci.yml   # 复用 CI 作为门禁

  build-push:
    needs: quality-gate
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write                  # 推送到 GHCR 需要
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # 构建镜像 + 层缓存，镜像 tag 跟随 git tag
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.ref_name }}
            ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build-push
    runs-on: ubuntu-latest
    steps:
      - name: 触发服务器拉取新镜像
        run: |
          curl -X POST "${{ secrets.DEPLOY_WEBHOOK_URL }}" \
            -H "Authorization: Bearer ${{ secrets.DEPLOY_TOKEN }}" \
            -d '{"tag": "${{ github.ref_name }}"}'
      # K8s/云平台可替换为 kubeconfig 或厂商 CLI 步骤
```

## 4. 部署侧的最小配合

服务器端 webhook 接收后执行：

```bash
# 服务器上：拉新镜像 + 滚动重启（配合优雅关闭实现零停机）
docker compose pull api
docker compose up -d --no-deps api
```

- [ ] PR 流水线全绿时间 < 3 分钟（缓存生效后）
- [ ] tag 推送自动产出 `ghcr.io` 镜像并触发部署
- [ ] 流水线失败能在 PR 页面一眼定位到失败 job

## ✅ 最佳实践与陷阱

- ✅ `--frozen-lockfile` 是 CI 的纪律：锁文件与 package.json 不同步直接失败
- ✅ 三个 job 并行，最慢的集成测试不阻塞 lint 反馈
- ❌ 把部署密钥塞进 PR 流程——PR 可被 fork 触发，密钥只进 release
- ❌ 用 `npm install` 替代 `pnpm install --frozen-lockfile`——依赖树漂移，构建不可复现

## 🔗 相关文档

- 📄 [容器化部署](01-docker-deployment.md) — 本流水线构建的镜像从哪来
- 📄 [可观测性](03-observability.md) — 部署后的监控闭环
- 📄 [端到端 API 测试](../testing/03-e2e-api-testing.md) — 发布门禁的最后一环
- 📄 [生产级 Node.js API](../projects/04-production-nodejs-api.md) — 流水线服务的对象
