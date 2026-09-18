# 容器化部署 — uv 镜像多阶段构建

> **文档简介**: 用多阶段 Dockerfile 构建既小又可复现的 Python 镜像，并用 Compose 编排应用 + 数据库 + Redis 三件套
>
> **目标读者**: 准备把应用打包交付的开发者
>
> **前置知识**: [开发工具链（uv）](../frameworks/04-devtools.md)、Docker 基本概念

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Docker` `#uv` `#多阶段构建` `#Compose` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 写出利用层缓存的多阶段 Dockerfile
- ✅ 以非 root 用户运行容器并配置健康检查
- ✅ 用 Compose 一键编排应用 + PostgreSQL + Redis

---

## 1. 为什么多阶段

- **构建阶段**：uv 解析依赖生成 `.venv`，可以带构建工具
- **运行阶段**：只拷贝 `.venv` 与代码——无编译器、无 pip 缓存，镜像更小、攻击面更小

## 2. Dockerfile 模板

```dockerfile
# ---- 构建阶段 ----
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# 先只拷依赖清单：代码改动时不重装依赖（利用层缓存）
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY . .
RUN uv sync --locked --no-dev

# ---- 运行阶段 ----
FROM python:3.14-slim-bookworm
RUN groupadd -r app && useradd -r -g app app      # 非 root 运行
WORKDIR /app
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH"
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

**要点**：

- `--locked` 要求依赖声明与锁文件一致；镜像还受系统库、基础镜像与目标平台影响（锁文件工作流见[开发工具链](../frameworks/04-devtools.md)）
- `--no-dev` 排除 pytest/ruff 等开发依赖
- `--no-install-project` + 二次 `uv sync` 的组合让依赖层与代码层分离，改代码不再触发依赖重装
- worker 数按 CPU 核数与异步占比调整，别照抄 2

## 3. .dockerignore

```text
.git
.venv
tests
__pycache__
*.pyc
.env
.env.*
*.pem
data/
```

**要点**：`.env` 绝不进镜像，密钥运行时注入（见[安全实践](../advanced-topics/security/01-security-practices.md)）。

## 4. 构建与运行

```bash
docker build -t todo-api:0.1.0 .
docker run --rm -p 8000:8000 -e DATABASE_URL="sqlite+aiosqlite:///./app.db" todo-api:0.1.0
```

## 5. Compose 编排三件套

```yaml
# compose.yaml
services:
  app:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+asyncpg://app:app@db:5432/app
      REDIS_URL: redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy     # 等数据库就绪再启动应用
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app               # 示例占位值，生产用密钥注入
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
  cache:
    image: redis:7-alpine
```

```bash
docker compose up --build      # 本地一键起全栈
```

**要点**：服务间用服务名当主机名（`db`、`cache`）——这就是容器网络里的 DNS；首次启动后记得跑 `alembic upgrade head`（迁移见[生态集成](../frameworks/03-ecosystem-integration.md)）。

## 6. 常见问题

**Q1: 镜像为什么这么大？**
检查是否单阶段、是否把构建工具带进了运行层；用 `dive <镜像>` 逐层分析体积。

**Q2: 改一行代码为什么全量重建？**
依赖清单必须先于代码 COPY——层缓存顺序错了就每次全量重装依赖，对照第 2 节模板检查顺序。

---

<!-- full-library-explanation -->
## 容器成功启动之后还要验证什么

前置是已有可启动的 main:app、依赖锁文件和 /health 路由。本文 Dockerfile 是这些条件下的打包模板，数据库迁移、持久卷和业务配置仍由应用提供。多阶段构建隔离构建工具，但复制虚拟环境还要求构建与运行镜像的解释器、路径及系统库兼容。

练习依次验证：镜像构建成功；容器进程以预期用户运行；健康端点返回 200；创建数据后重建容器，确认数据是否仍存在。若 SQLite 文件只保存在容器可写层，删除容器后丢失是预期生命周期，持久化需要外部卷或数据库服务。

健康检查通过只能说明该检查所覆盖的条件成立。进程活着、能接请求、数据库可用是不同状态；不要让每次活性检查执行昂贵的完整业务流程。基础镜像标签与系统包也影响构建结果，锁定 Python 依赖并不能独自保证镜像字节级一致。

## 🔗 相关文档

- 📄 **[开发工具链](../frameworks/04-devtools.md)** — uv.lock 与 `--frozen` 的来源
- 🚀 **[CI/CD 流水线](./02-ci-cd-pipelines.md)** — CI 里自动构建并推送镜像
- 🚀 **[项目：生产级应用](../projects/04-production-fastapi-app.md)** — Dockerfile 的完整工程上下文
- 🎓 **[安全实践](../advanced-topics/security/01-security-practices.md)** — 密钥注入与镜像安全
- 📖 **[故障排除](../reference/quick-references/02-troubleshooting.md)** — 构建报错速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
