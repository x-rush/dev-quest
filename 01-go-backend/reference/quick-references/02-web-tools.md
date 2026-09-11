# Go Web开发工具速查

> **文档简介**: Go Web开发常用工具和命令的速查手册，包含开发、测试、部署的实用工具
>
> **目标读者**: Go Web开发者，需要快速查阅Web开发工具的开发者
>
> **前置知识**: Go基础、Web开发基础
>
> **预计时长**: 20分钟速查

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `reference/quick-references` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#Web工具` `#开发工具` `#速查` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 开发工具

### Go 命令
```bash
# 初始化模块
go mod init example.com/myapp

# 下载依赖
go get github.com/gin-gonic/gin
go get -u ./...  # 更新所有依赖

# 运行应用
go run main.go

# 构建应用
go build -o myapp main.go

# 测试
go test ./...
go test -v ./...
go test -cover ./...
```

### 环境变量
```bash
# 设置环境变量
export GO_ENV=development
export PORT=8080
export DB_HOST=localhost

# Go模块代理
export GOPROXY=https://goproxy.cn,direct
export GOSUMDB=sum.golang.google.cn
```

## 🎯 包管理

### go.mod 文件
```go
module example.com/myapp

go 1.25

require (
    github.com/gin-gonic/gin v1.12.0
    github.com/joho/godotenv v1.4.0
    gorm.io/gorm v1.31.2
    github.com/redis/go-redis/v9 v9.22.0
)
```

### 常用包安装
```bash
# Web框架
go get github.com/gin-gonic/gin

# 数据库ORM
go get gorm.io/gorm
go get gorm.io/driver/mysql
go get gorm.io/driver/postgres

# 配置管理
go get github.com/joho/godotenv

# 日志
go get github.com/sirupsen/logrus
go get go.uber.org/zap

# 验证
go get github.com/go-playground/validator/v10

# 测试
go get github.com/stretchr/testify
```

## 🎯 开发服务器

### Gin 开发模式
```go
package main

import (
    "github.com/gin-gonic/gin"
    "github.com/gin-contrib/cors"
)

func main() {
    r := gin.Default()
    
    // 启用CORS
    r.Use(cors.Default())
    
    // 开发模式设置
    gin.SetMode(gin.DebugMode)
    
    r.GET("/api/health", func(c *gin.Context) {
        c.JSON(200, gin.H{"status": "ok"})
    })
    
    r.Run(":8080") // 开发服务器
}
```

### 热重载工具
```bash
# 安装air
go install github.com/cosmtrek/air@latest

# 创建.air.toml配置
air init

# 运行热重载
air
```

## 🎯 数据库工具

### MySQL 连接
```bash
# 安装MySQL驱动
go get github.com/go-sql-driver/mysql

# 连接测试命令
mysql -h localhost -u root -p
```

### Redis 连接
```bash
# 安装Redis驱动
go get github.com/redis/go-redis/v9

# Redis CLI命令
redis-cli ping
redis-cli set key value
```

## 🎯 API测试工具

### curl 命令
```bash
# GET请求
curl http://localhost:8080/api/users

# POST请求
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com"}'

# PUT请求
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"John Updated"}'

# DELETE请求
curl -X DELETE http://localhost:8080/api/users/1
```

### HTTPie (更友好的替代)
```bash
# 安装HTTPie
# Ubuntu: sudo apt install httpie
# macOS: brew install httpie

# GET请求
http GET localhost:8080/api/users

# POST请求
http POST localhost:8080/api/users name="John" email="john@example.com"
```

## 🔗 相关资源

- **深入学习**: [frameworks/01-gin-framework-basics.md](../../frameworks/01-gin-framework-basics.md)
- **相关文档**: [reference/framework-essentials/01-gin-framework.md](../framework-essentials/01-gin-framework.md)
- **实践参考**: [projects/01-rest-api-server.md](../../projects/01-rest-api-server.md)

---

**更新日志**: 2026年9月 - 创建Go Web开发工具速查
