# Go、Node.js、Python 容器化 P1 完成记录

更新范围：

| 技术栈 | 文档 | 已覆盖的可执行内容 |
| --- | --- | --- |
| Go | `01-go-backend/deployment/01-containerization.md` | 多阶段编译、distroless 非 root 运行、`.dockerignore`、PostgreSQL Compose 与 `/healthz` 验收命令 |
| Node.js | `09-nodejs-backend/deployment/01-docker-deployment.md` | pnpm/Prisma 多阶段构建、非 root 运行、健康检查、迁移任务与 PostgreSQL/Redis Compose |
| Python | `10-python-discovery/deployment/01-docker-deployment.md` | uv 锁文件分层、多阶段虚拟环境、非 root 运行、健康检查与 PostgreSQL/Redis Compose |

本轮进行了文档与命令静态复核：三个示例都将依赖清单置于源码复制之前，以保留 Docker 缓存；均排除环境文件；均明确容器内服务发现使用 Compose 服务名。Go 模板另外避免将 shell、编译器和源码带入运行镜像。

未执行 Docker build 或启动 Compose：当前工作项要求完成示例与报告，未授权执行会拉取镜像、创建容器或写入本地 Docker 状态。读者可按各篇文档的验收命令在自己的 Docker 环境中完成运行验证。
