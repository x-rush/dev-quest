# 容器化部署：多阶段构建

> **文档简介**: 用多阶段 Dockerfile 把 Node.js 24 服务打成精简、安全的生产镜像——依赖分层缓存、Prisma 生成、非 root 运行与健康检查一步到位
>
> **目标读者**: 准备把 API 服务交付容器环境的中级后端开发者
>
> **前置知识**: [开发工具链](../frameworks/04-devtools.md) 的构建脚本、Docker 基本概念

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `09-nodejs-backend` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#docker` `#multi-stage` `#prisma` `#生产镜像` |
| **更新日期** | `2026年9月` |

</details>

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
# prisma generate 需读 schema 与 prisma.config.ts（v7 生成阶段不需要连接串）；
# 生成的 Client 是 TypeScript 源码产物，落在 generator output 目录
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

# 编译产物 + v7 生成的 Prisma Client（output 目录，不在 node_modules）
# + prisma.config.ts（migrate deploy 运行时从它读连接串）+ 迁移文件
COPY --from=build /app/dist ./dist
COPY --from=build /app/generated ./generated
COPY --from=build /app/prisma ./prisma
COPY --from=build /app/prisma.config.ts ./

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
      migrate: { condition: service_completed_successfully }
    restart: unless-stopped

  migrate:
    # 迁移需要 Prisma CLI；它是开发依赖，因此使用 build 阶段，而不是
    # 已剔除 devDependencies 的 runner 阶段。
    build:
      context: .
      target: build
    command: pnpm exec prisma migrate deploy
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

`service_completed_successfully` 让 API 只在迁移任务成功退出后启动；若迁移失败，先修复或回滚迁移，而不是让 API 带着旧 schema 启动。Kubernetes 场景则把迁移放进 InitContainer 或发布 Job。

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

把依赖清单与锁文件先复制进构建阶段，使只改业务源码时有机会复用依赖层；后续指令与安装脚本仍可能影响缓存和产物。冻结锁文件固定依赖解析，但运行时、平台和外部下载也属于复现条件。

node:24-alpine 仍是可移动标签，不是精确不可变锁定；需要严格追溯时记录镜像摘要，并维护安全更新流程。检查 native addon 与目标 libc/架构兼容性，不能只因为镜像小就选择 Alpine。

## 🔗 相关文档

- 📄 [CI/CD 流水线](02-ci-cd-pipelines.md) — 镜像构建推送的自动化
- 📄 [生产级 Node.js API](../projects/04-production-nodejs-api.md) — 优雅关闭与探针的来源
- 📖 [常见故障排除](../reference/quick-references/02-troubleshooting.md) — 容器内常见报错
- 📄 [端到端 API 测试](../testing/03-e2e-api-testing.md) — 用同一镜像做 E2E


<!-- acceptance-exercise -->
## 练习与验收：把进程生命周期纳入容器验收

用锁文件构建并启动测试镜像，完成一条 HTTP 业务请求，再在请求未完成时发 SIGTERM。预期入口停止接新工作，在宽限期内结束在途任务、关闭连接池并退出。检查容器 PID 1 是否能把信号送达应用。验收再在只读根文件系统或非特权用户条件下试运行，确认需要写入的目录已明确配置；成功 build 不保证这些条件成立。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
