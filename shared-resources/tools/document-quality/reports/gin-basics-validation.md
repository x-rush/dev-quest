# Gin 入门最小工程验证

**执行时间：** 2026-09-20  
**运行环境：** `golang:1.27` Docker 容器  
**锁定依赖：** `github.com/gin-gonic/gin v1.12.0`

## 结果

`01-go-backend/frameworks/01-gin-framework-basics.md` 中标记为 `verify:gin-basics-main` 和 `verify:gin-basics-test` 的两个 Go 围栏已被脚本原样提取，在临时模块中执行：

```bash
docker run --rm -v <temporary-directory>:/src -w /src golang:1.27 go test -mod=mod ./...
```

结果为 **PASS**。测试覆盖 `GET /health`、畸形 JSON、缺少必填 `title`、创建待办成功，以及未知路径的 `404`。JSON 绑定错误被映射为 `400`，而不是被误写成成功响应。

## 证据与边界

机器可读记录在 [gin-basics-validation.json](gin-basics-validation.json)，其中保存了两个原文代码块的 SHA-256。验证脚本为 [verify_gin_basics.py](../verify_gin_basics.py)，它只接受具名围栏，避免手工复制后把测试对象和文档脱钩。

该检查不启动监听端口；不主张部署、反向代理、TLS、数据库、认证授权、性能或压力行为已经验证。Gin 官方仓库在本次复核时发布 `v1.12.0`，并注明该版本要求 Go 1.26 或更新版本：[官方仓库的入门说明](https://github.com/gin-gonic/gin#readme)。
