# 容器化部署：多阶段构建

> **文档简介**: 用多阶段 Dockerfile 把 Node.js 24 服务打成精简、安全的生产镜像——依赖分层缓存、Prisma 生成、非 root 运行与健康检查一步到位
>
> **目标读者**: 准备把 API 服务交付容器环境的中级后端开发者
>
> **前置知识**: [开发工具链](../frameworks/04-devtools.md) 的构建脚本、Docker 基本概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#docker` `#multi-stage` `#prisma` `#生产镜像` |
| **更新日期** | `2026年9月` |

## 🎯 本节目标

- 编写"依赖缓存友好 + 体积最小"的多阶段构建
- 在镜像内完成 Prisma Client 生成与迁移
- 以非 root 用户运行并配置健康检查

## 1. 多阶段 Dockerfile 全解

```dockerfile
# Dockerfile
# ---- 阶段 1：依赖解析（仅声明依赖，最能命中缓存）----
FROM node:24-alpine AS deps
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# ---- 阶段 2：构建（TypeScript 编译 + Prisma 生成）----
FROM node:24-alpine AS build
WORKDIR /app
RUN corepack enable
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# prisma generate 需要读 schema；devDependencies 里含有 typescript
RUN pnpm exec prisma generate && pnpm run build

# ---- 阶段 3：生产运行（只带生产依赖与编译产物）----
FROM node:24-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# 非 root 运行：镜像被攻破也拿不到 root 权限
RUN addgroup -S app && adduser -S app -G app

# 生产依赖独立安装（跳过 devDependencies）
RUN corepack enable
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --prod

# 编译产物 + Prisma 生成物 + 迁移文件（migrate deploy 需要）
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=build /app/prisma ./prisma

USER app
EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:3000/livez || exit 1

CMD ["node", "dist/server.js"]
```

**体积对比直觉**：单阶段镜像（含 devDependencies + 源码）常见 1-2GB；上面的 runner 阶段通常 200-300MB。

## 2. .dockerignore：缓存正确性的前提

```text
# .dockerignore —— 缺了它，本地改动会反复打碎缓存层
node_modules
dist
.git
.env*
*.md
coverage
tests
e2e
```

## 3. 启动命令：迁移与服务的编排

迁移不应写进 CMD 链式执行（多副本会并发迁移）。推荐"一次性迁移任务 + 常驻服务"分离：

```yaml
# docker-compose.yml —— 本地/单机生产
services:
  api:
    build: .
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgresql://postgres:pass@db:5432/app
      REDIS_URL: redis://cache:6379
      JWT_ACCESS_SECRET: ${JWT_ACCESS_SECRET}   # 密钥走运行时注入，不进镜像
    depends_on:
      db: { condition: service_healthy }
    restart: unless-stopped

  migrate:
    build: .
    command: sh -c "npx prisma migrate deploy && echo done"
    environment:
      DATABASE_URL: postgresql://postgres:pass@db:5432/app
    depends_on:
      db: { condition: service_healthy }
    restart: "no"     # 跑完即退出，一次性任务

  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 3s
      retries: 10

  cache:
    image: redis:7-alpine

volumes:
  pgdata:
```

Kubernetes 场景则把迁移放进 InitContainer 或发布 Job。

## 4. 验证清单

```bash
docker compose build api
docker compose up migrate api -d
docker compose ps                 # api 应显示 healthy
docker exec $(docker compose ps -q api) whoami      # 应输出 app 而非 root
docker image ls | grep api        # 检查镜像体积
```

- [ ] 镜像不含 `.env`、源码、tests 目录（`docker exec ls /app` 验证）
- [ ] 容器以 `app` 用户运行
- [ ] `docker stop` 时服务优雅退出（看日志出现"收到 SIGTERM"，见 [`../projects/04-production-nodejs-api.md`](../projects/04-production-nodejs-api.md)）

## ✅ 最佳实践与陷阱

- ✅ 先 COPY 依赖清单再 `pnpm install`——源码改动不触发依赖重装
- ✅ `--frozen-lockfile` 锁定依赖树，保证可复现构建
- ❌ 在 Dockerfile 里 `COPY . .` 到 deps 阶段——任何文件改动都打碎缓存
- ❌ 用 `latest` 基础镜像——用 `node:24-alpine` 明确锁定

## 🔗 相关文档

- 📄 [CI/CD 流水线](02-ci-cd-pipelines.md) — 镜像构建推送的自动化
- 📄 [生产级 Node.js API](../projects/04-production-nodejs-api.md) — 优雅关闭与探针的来源
- 📖 [常见故障排除](../reference/quick-references/02-troubleshooting.md) — 容器内常见报错
- 📄 [端到端 API 测试](../testing/03-e2e-api-testing.md) — 用同一镜像做 E2E
