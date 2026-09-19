# Go 应用 Docker 部署指南

> **阅读准备**：已有可在本机启动的 Go 服务，理解端口、环境变量与进程退出，并已安装 Docker；开始前先执行 `docker version` 确认守护进程可用。

## 📚 概述

Docker容器化是现代Go应用部署的标准方式。Go的静态编译特性使其非常适合容器化部署，可以创建轻量级、高性能的容器镜像。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `deployment/devops` |
| **难度** | ⭐⭐⭐ |
| **标签** | `#docker` `#容器化` `#部署` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

### 🎯 学习目标
- 掌握Go应用Docker化技术
- 学会多阶段构建优化
- 理解容器编排和部署
- 掌握生产环境部署最佳实践
- 熟悉Go容器化与PHP的差异

## 🔄 Go vs PHP 容器化对比

### 传统PHP Docker部署
```dockerfile
# PHP应用Dockerfile (传统方式)
FROM php:8.2-fpm

# 安装依赖
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) gd pdo pdo_mysql

# 设置工作目录
WORKDIR /var/www/html

# 复制代码
COPY . .

# 安装PHP依赖
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer
RUN composer install --no-dev --optimize-autoloader

# 设置权限
RUN chown -R www-data:www-data /var/www/html

# 暴露端口
EXPOSE 9000

# 启动命令
CMD ["php-fpm"]
```

### Go应用Docker部署
```dockerfile
# Go应用Dockerfile (现代方式)
# 多阶段构建
FROM golang:1.25-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# 最终镜像
FROM alpine:3.18

# 安装必要工具
RUN apk --no-cache add ca-certificates tzdata

# 设置时区
ENV TZ=Asia/Shanghai

# 设置工作目录
WORKDIR /root/

# 从构建阶段复制二进制文件
COPY --from=builder /app/main .

# 复制配置文件
COPY --from=builder /app/configs ./configs

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# 启动命令
CMD ["./main"]
```

## 📝 Go Docker 部署详解

### 1. 基础Dockerfile

#### 单阶段构建
```dockerfile
# 基础单阶段构建
FROM golang:1.25-alpine

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN go build -o main .

# 暴露端口
EXPOSE 8080

# 运行应用
CMD ["./main"]
```

#### 优化单阶段构建
```dockerfile
# 优化的单阶段构建
FROM golang:1.25-alpine

# 安装必要的系统依赖
RUN apk add --no-cache git ca-certificates

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用 (启用优化选项)
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-w -s" \
    -o main .

# 暴露端口
EXPOSE 8080

# 非root用户运行
RUN addgroup -g 1000 appgroup && adduser -u 1000 -G appgroup -s /bin/sh -D appuser
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# 运行应用
CMD ["./main"]
```

### 2. 多阶段构建

#### 标准多阶段构建
```dockerfile
# 构建阶段
FROM golang:1.25-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-w -s" \
    -o main .

# 最终镜像
FROM alpine:3.18

# 安装必要工具
RUN apk --no-cache add ca-certificates tzdata

# 设置时区
ENV TZ=Asia/Shanghai

# 设置工作目录
WORKDIR /app

# 从构建阶段复制二进制文件
COPY --from=builder /app/main .

# 复制配置文件
COPY --from=builder /app/configs ./configs

# 创建非root用户
RUN addgroup -g 1000 appgroup && adduser -u 1000 -G appgroup -s /bin/sh -D appuser
USER appuser

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# 运行应用
CMD ["./main"]
```

#### 包含前端资源的构建
```dockerfile
# 前端构建阶段
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# 复制前端文件
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# Go构建阶段
FROM golang:1.25-alpine AS go-builder

WORKDIR /app

# 复制依赖文件
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 复制前端构建结果
COPY --from=frontend-builder /frontend/dist ./static

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-w -s" \
    -o main .

# 最终镜像
FROM alpine:3.18

# 安装必要工具
RUN apk --no-cache add ca-certificates tzdata

# 设置时区
ENV TZ=Asia/Shanghai

WORKDIR /app

# 从构建阶段复制二进制文件
COPY --from=go-builder /app/main .

# 复制静态资源
COPY --from=go-builder /app/static ./static

# 复制配置文件
COPY --from=go-builder /app/configs ./configs

# 创建非root用户
RUN addgroup -g 1000 appgroup && adduser -u 1000 -G appgroup -s /bin/sh -D appuser
USER appuser

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# 运行应用
CMD ["./main"]
```

### 3. Docker Compose 配置

#### 基础docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres
      - DB_USER=postgres
      - DB_PASSWORD=password
      - DB_NAME=myapp
    depends_on:
      - postgres
      - redis
    networks:
      - app-network

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

#### 生产环境docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8080:8080"
    environment:
      - APP_ENV=production
      - DB_HOST=postgres
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=${DB_NAME}
      - REDIS_HOST=redis
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### 4. 生产环境配置

#### Dockerfile.prod
```dockerfile
# 生产环境Dockerfile
FROM golang:1.25-alpine AS builder

# 设置构建参数
# 注意：ARG 只做字面量赋值，不会执行 $(...) 命令替换；
# BUILD_TIME/GIT_COMMIT 需在构建时通过 --build-arg 注入（见下方构建命令）
ARG VERSION=dev
ARG BUILD_TIME=unknown
ARG GIT_COMMIT=unknown

# 安装必要的系统依赖
RUN apk add --no-cache git

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用 (包含版本信息)
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-w -s \
    -X 'main.Version=${VERSION}' \
    -X 'main.BuildTime=${BUILD_TIME}' \
    -X 'main.GitCommit=${GIT_COMMIT}'" \
    -o main .

# 最终镜像
FROM alpine:3.18

# 设置标签
LABEL maintainer="your-email@example.com"
LABEL version="${VERSION}"
LABEL description="Go application"

# 安装必要工具
RUN apk --no-cache add ca-certificates tzdata wget

# 设置时区
ENV TZ=Asia/Shanghai

# 设置工作目录
WORKDIR /app

# 从构建阶段复制二进制文件
COPY --from=builder /app/main .

# 复制配置文件
COPY --from=builder /app/configs ./configs

# 创建必要的目录
RUN mkdir -p logs uploads

# 创建非root用户
RUN addgroup -g 1000 appgroup && adduser -u 1000 -G appgroup -s /bin/sh -D appuser
USER appuser

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# 运行应用
CMD ["./main"]
```

构建时注入版本信息（时间戳与提交号在宿主机上取值，经 `--build-arg` 传入）：
```bash
docker build -f Dockerfile.prod \
  --build-arg VERSION=$(git describe --tags --always) \
  --build-arg BUILD_TIME=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) \
  -t myapp:1.0.0 .
```

#### 环境变量配置
```bash
# .env 文件
# 数据库配置
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=myapp
DB_HOST=postgres
DB_PORT=5432

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT配置
JWT_SECRET=your_super_secret_jwt_key
JWT_EXPIRES_IN=3600

# 应用配置
APP_ENV=production
APP_PORT=8080
APP_HOST=0.0.0.0

# 日志配置
LOG_LEVEL=info
LOG_FORMAT=json

# 监控配置
METRICS_PORT=9090
METRICS_PATH=/metrics
```

### 5. 容器编排和扩展

#### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-app
  labels:
    app: go-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: go-app
  template:
    metadata:
      labels:
        app: go-app
    spec:
      containers:
      - name: go-app
        image: your-registry/go-app:latest
        ports:
        - containerPort: 8080
        env:
        - name: DB_HOST
          value: "postgres-service"
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: go-app-service
spec:
  selector:
    app: go-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

#### Kubernetes ConfigMap和Secret
```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  config.yaml: |
    server:
      host: "0.0.0.0"
      port: 8080
    database:
      host: "postgres-service"
      port: 5432
      dbname: "myapp"
      sslmode: "disable"
    redis:
      host: "redis-service"
      port: 6379
    logging:
      level: "info"
      format: "json"

# Secret
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: cG9zdGdyZXM=  # base64 encoded 'postgres'
  password: eW91cl9zZWN1cmVfcGFzc3dvcmQ=  # base64 encoded password
```

### 6. CI/CD 集成

#### GitHub Actions 工作流
```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Go
      uses: actions/setup-go@v3
      with:
        go-version: '1.25'

    - name: Run tests
      run: |
        go test -v ./...
        go test -race ./...

    - name: Run lint
      uses: golangci/golangci-lint-action@v3
      with:
        version: latest

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write

    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

### 7. 监控和日志

#### 监控配置
```go
// main.go - 添加监控端点
package main

import (
    "expvar"
    "net/http"
    "net/http/pprof"

    "github.com/gin-gonic/gin"
)

func main() {
    // 主应用路由
    router := gin.Default()

    // 添加监控端点
    router.GET("/metrics", gin.WrapH(expvar.Handler()))

    // 添加pprof端点
    router.GET("/debug/pprof/", gin.WrapH(http.HandlerFunc(pprof.Index)))
    router.GET("/debug/pprof/cmdline", gin.WrapH(http.HandlerFunc(pprof.Cmdline)))
    router.GET("/debug/pprof/profile", gin.WrapH(http.HandlerFunc(pprof.Profile)))
    router.GET("/debug/pprof/symbol", gin.WrapH(http.HandlerFunc(pprof.Symbol)))
    router.GET("/debug/pprof/trace", gin.WrapH(http.HandlerFunc(pprof.Trace)))

    // 运行应用
    router.Run(":8080")
}
```

#### 日志配置
```go
// logging/logger.go
package logging

import (
    "os"
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func NewLogger(level string) *zap.Logger {
    zapLevel := zapcore.InfoLevel
    switch level {
    case "debug":
        zapLevel = zapcore.DebugLevel
    case "info":
        zapLevel = zapcore.InfoLevel
    case "warn":
        zapLevel = zapcore.WarnLevel
    case "error":
        zapLevel = zapcore.ErrorLevel
    }

    config := zap.Config{
        Level:    zap.NewAtomicLevelAt(zapLevel),
        Encoding: "json",
        EncoderConfig: zapcore.EncoderConfig{
            TimeKey:        "timestamp",
            LevelKey:       "level",
            NameKey:        "logger",
            CallerKey:      "caller",
            FunctionKey:    zapcore.OmitKey,
            MessageKey:     "message",
            StacktraceKey:  "stacktrace",
            LineEnding:     zapcore.DefaultLineEnding,
            EncodeLevel:    zapcore.LowercaseLevelEncoder,
            EncodeTime:     zapcore.ISO8601TimeEncoder,
            EncodeDuration: zapcore.SecondsDurationEncoder,
            EncodeCaller:   zapcore.ShortCallerEncoder,
        },
        OutputPaths:      []string{"stdout"},
        ErrorOutputPaths: []string{"stderr"},
    }

    if os.Getenv("APP_ENV") == "production" {
        config.OutputPaths = []string{"stdout", "/var/log/app.log"}
        config.ErrorOutputPaths = []string{"stderr", "/var/log/app-error.log"}
    }

    logger, _ := config.Build()
    return logger
}
```

## 🧪 实践练习

### 练习1: 构建基础Docker镜像
```dockerfile
# 创建Dockerfile
FROM golang:1.25-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# 运行镜像
FROM alpine:3.18

RUN apk --no-cache add ca-certificates tzdata

WORKDIR /app

COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]
```

### 练习2: 创建docker-compose配置
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres
      - DB_USER=postgres
      - DB_PASSWORD=password
      - DB_NAME=myapp
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - app-network

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

## 📋 部署最佳实践

多阶段构建把编译工具与运行产物分开，减少运行镜像携带的内容；基础镜像还必须具备程序需要的 libc、证书与时区等能力。先验证可运行，再比较镜像大小与构建时间，不能只追求最小体积。

容器以合适非特权身份运行，配置与秘密由部署环境提供；健康探测要区分能否接流量与是否需要重启。发布记录关联源码、镜像摘要与配置版本，并在隔离环境演练退出、重启和恢复。回滚镜像不会自动撤销数据迁移，应另行验证兼容性。

## 📋 检查清单

- [ ] 掌握Go应用Docker化技术
- [ ] 理解多阶段构建的优势
- [ ] 学会使用Docker Compose
- [ ] 掌握Kubernetes部署
- [ ] 理解CI/CD集成
- [ ] 学会监控和日志配置
- [ ] 理解生产环境最佳实践
- [ ] 掌握安全配置

## 🚀 下一步

掌握Docker部署后，你可以继续学习：
- **云原生部署**: AWS, GCP, Azure部署
- **服务网格**: Istio, Linkerd
- **无服务器**: Lambda, Cloud Functions
- **微服务架构**: 完整的微服务实践

---

**学习提示**: Go的静态编译特性使其非常适合容器化部署。通过Docker和Kubernetes，你可以构建高度可扩展的Go应用。相比于PHP的部署方式，Go容器化更加简单和高效。

*最后更新: 2025年9月*

---

<!-- full-library-explanation -->
## 可直接采用的生产构建模板

前置是项目有 `go.mod`、`go.sum`，并且 `./cmd/api` 能构建出一个监听 `8080`、提供 `/healthz` 的服务。下面的版本把依赖下载、交叉编译和运行镜像分开；`-trimpath` 与 `-buildvcs=false` 减少构建路径和 VCS 元数据进入二进制，`CGO_ENABLED=0` 使其可运行在无 shell 的 distroless 镜像中。

```dockerfile
# syntax=docker/dockerfile:1
FROM golang:1.25-bookworm AS build
WORKDIR /src

# 先下载模块，业务代码变化不会让这一层失效。
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build \
    -trimpath -buildvcs=false -ldflags="-s -w" \
    -o /out/api ./cmd/api

FROM gcr.io/distroless/static-debian12:nonroot
WORKDIR /app
COPY --from=build /out/api /app/api
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/app/api"]
```

配套 `.dockerignore` 应至少排除构建上下文中不需要的文件：

```text
.git
bin
tmp
coverage.out
*.test
.env
.env.*
```

Compose 中把应用和依赖服务分开，并让应用使用服务 DNS 名称，而不是 `localhost`：

```yaml
services:
  api:
    build: .
    ports: ["8080:8080"]
    environment:
      DATABASE_URL: postgres://app:app@db:5432/app?sslmode=disable
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app # 仅用于本地示例；生产环境注入密钥
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      timeout: 3s
      retries: 10
```

## 构建后的验收

```bash
docker build -t go-api:local .
docker run --rm -p 8080:8080 go-api:local
# 另一个终端：curl -f http://127.0.0.1:8080/healthz
```

成功 build 只能证明 Dockerfile 的编译链路可用。还应检查健康端点、停止信号下的优雅退出，以及容器删除后的数据生命周期。运行镜像没有 shell 是有意的安全边界；调试时使用独立的调试镜像或临时 sidecar，不要为了 `sh` 把构建工具带回生产镜像。镜像标签会移动，发布记录应保存实际镜像摘要。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
