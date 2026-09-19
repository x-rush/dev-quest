# Go、Node.js、Python 容器化 P1 完成记录

更新范围：

| 技术栈 | 文档 | 已覆盖的可执行内容 |
| --- | --- | --- |
| Go | `01-go-backend/deployment/01-containerization.md` | 多阶段编译、distroless 非 root 运行、`.dockerignore`、PostgreSQL Compose 与 `/healthz` 验收命令；所有带 `wget` 的 Alpine 健康检查镜像均安装了 `wget`，生产模板的 `logs`、`uploads` 归非 root 应用用户所有。 |
| Node.js | `09-nodejs-backend/deployment/01-docker-deployment.md` | pnpm/Prisma 多阶段构建、非 root 运行、健康检查、迁移任务与 PostgreSQL/Redis Compose；迁移服务构建到保留 Prisma CLI 的 `build` 阶段，API 依赖迁移任务成功结束。 |
| Python | `10-python-discovery/deployment/01-docker-deployment.md` | uv 锁文件分层、多阶段虚拟环境、非 root 运行、健康检查与 PostgreSQL/Redis Compose；Alembic 迁移作为一次性服务运行，API 等待数据库、Redis 和迁移成功。 |

本轮进行了文档与命令静态复核：三个示例都将依赖清单置于源码复制之前，以保留 Docker 缓存；均排除环境文件；均明确容器内服务发现使用 Compose 服务名。Go 模板另外避免将 shell、编译器和源码带入运行镜像。已确认本机 Docker CLI 可连接守护进程（Server `29.8.0`），并检查了上述健康检查命令、迁移目标阶段、Compose 的 `service_completed_successfully` 依赖和 Redis 探针的对应关系。

未执行 Docker build 或启动 Compose：这些是面向不同读者项目结构的文档模板，工作区没有各模板所要求的 Go `cmd/api`、Node `package.json`/Prisma schema 或 Python `pyproject.toml`/Alembic 迁移项目可供真实构建。读者可在满足各篇前置条件的项目中运行文档的验收命令完成端到端验证。
