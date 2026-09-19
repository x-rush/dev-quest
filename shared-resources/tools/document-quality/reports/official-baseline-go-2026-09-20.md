# Go 模块官方技术基线复核（2026-09-20）

本记录只复核模块入口的版本与迁移陈述；不构成 Gin、GORM、MongoDB、Redis 或任何部署示例的构建证明。

| 项目 | 本次结论 | 取证方式 | 官方来源 |
|---|---|---|---|
| Go | `go1.27.1` 和 `go1.26.8` 均标记为 stable；模块基线保持 1.27.1 | 读取下载 JSON 的前两个 stable 条目 | [Go Downloads](https://go.dev/dl/?mode=json) |
| Gin | 最新 GitHub release 为 `v1.12.0` | GitHub Releases API 的 `releases/latest` | [gin-gonic/gin releases](https://github.com/gin-gonic/gin/releases) |
| GORM | 最新 GitHub release 为 `v1.31.2` | GitHub Releases API 的 `releases/latest` | [go-gorm/gorm releases](https://github.com/go-gorm/gorm/releases) |
| MongoDB Go Driver | 最新 GitHub release 为 `v2.9.1` | GitHub Releases API 的 `releases/latest` | [mongodb/mongo-go-driver releases](https://github.com/mongodb/mongo-go-driver/releases) |
| go-redis | 最新 GitHub release 为 `v9.22.0` | GitHub Releases API 的 `releases/latest` | [redis/go-redis releases](https://github.com/redis/go-redis/releases) |

复核时刻为 2026-09-20（Asia/Shanghai）。其中“最新 release”只描述该时刻上游发布页返回的标签；安装项目必须仍以 `go.mod` / `go.sum`、兼容性矩阵和实际构建为准。MongoDB v1 的生命周期和具体 API 签名另由对应驱动文档页逐项核对，不能从 release 标签推出。
