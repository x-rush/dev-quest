# Next.js 16 Docker 容器化部署完全指南

> **文档简介**: Next.js 16 + Docker 企业级容器化部署完整指南，涵盖多阶段构建、Docker Compose、生产环境优化、安全配置、监控日志等现代容器化部署技术

> **目标读者**: 具备Next.js基础的开发者，需要掌握企业级容器化部署和DevOps实践的开发运维工程师

> **前置知识**: Next.js 16基础、Docker基础概念、Linux基础、网络协议、安全基础

> **预计时长**: 6-8小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `deployment` |
| **难度** | ⭐⭐⭐⭐ (4/5星) |
| **标签** | `#docker` `#containerization` `#devops` `#deployment` `#production` `#security` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

### 🐳 企业级容器化部署
- 掌握Next.js 16多阶段Docker构建的最佳实践
- 实现生产级Docker Compose配置和编排
- 构建完整的容器化CI/CD流水线
- 实现容器安全加固和权限管理
- 掌握容器网络、存储、监控配置
- 建立容器化的高可用架构

### 🚀 生产环境优化
- 实现Docker镜像大小优化和安全扫描
- 掌握容器资源限制和性能调优
- 构建完整的容器监控和日志体系
- 实现容器的自动化备份和恢复
- 掌握容器编排和扩展策略
- 建立容器化的灾难恢复机制

### 🛡️ 安全与合规
- 实施容器安全扫描和漏洞检测
- 掌握容器运行时安全和访问控制
- 实现镜像签名和供应链安全
- 建立容器网络安全和通信加密
- 掌握合规性审计和安全监控
- 构建企业级容器安全策略

## 📖 概述

Next.js 16 与 Docker 的结合为企业级应用部署提供了现代化的容器化解决方案。本指南深入探讨从基础的多阶段构建到复杂的生产环境编排，涵盖安全、性能、监控等企业级容器化最佳实践，帮助你构建可扩展、安全、可靠的容器化部署架构。

## 🏗️ Docker 架构概览

### 容器化部署架构

```
┌─────────────────────────────────────────────────────────┐
│                   负载均衡层                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │    Nginx     │ │   CloudFlare │ │    ALB       │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                   应用容器层                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │Next.js App 1 │ │Next.js App 2 │ │Next.js App N │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                   数据容器层                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │ PostgreSQL  │ │    Redis     │ │    MinIO     │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                   监控和管理层                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │ Prometheus  │ │ Grafana      │ │   ELK Stack  │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
└─────────────────────────────────────────────────────────┘
```

## 🐳 Dockerfile 配置

### 企业级多阶段构建

#### 📦 优化版 Dockerfile
```dockerfile
# Dockerfile
# 构建阶段
FROM node:20-alpine AS deps

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package.json package-lock.json* ./

# 安装依赖
RUN npm ci --only=production && npm cache clean --force

# 构建阶段
FROM node:20-alpine AS builder

# 安装构建依赖
RUN apk add --no-cache libc6-compat

# 设置工作目录
WORKDIR /app

# 复制依赖
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package.json ./package.json
COPY --from=deps /app/package-lock.json ./package-lock.json

# 复制源代码
COPY . .

# 设置构建环境变量
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# 构建应用
RUN npm run build

# 生产阶段
FROM node:20-alpine AS runner

# 安装运行时依赖
RUN apk add --no-cache \
    dumb-init \
    curl \
    && addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# 设置工作目录
WORKDIR /app

# 设置生产环境变量
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# 创建应用用户目录
RUN mkdir -p /app/.next/cache && chown nextjs:nodejs /app/.next/cache

# 复制构建产物
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 切换到非root用户
USER nextjs

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# 暴露端口
EXPOSE 3000

# 启动应用
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
```

#### 🔒 安全强化版 Dockerfile
```dockerfile
# Dockerfile.secure
# 构建阶段
FROM node:20-alpine AS deps

# 使用特定用户
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 builder

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package.json package-lock.json* ./

# 安装依赖
RUN npm ci --only=production && npm cache clean --force

# 构建阶段
FROM node:20-alpine AS builder

# 安装构建依赖
RUN apk add --no-cache libc6-compat

# 设置工作目录
WORKDIR /app

# 复制依赖
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package.json ./package.json
COPY --from=deps /app/package-lock.json ./package-lock.json

# 复制源代码
COPY --from=deps /app/.npmrc ./.npmrc
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM gcr.io/distroless/nodejs20-debian11 AS runner

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

# 复制构建产物
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# 非root用户运行
USER 65534:65534

# 暴露端口
EXPOSE 3000

# 启动应用
CMD ["server.js"]
```

#### 🛠️ 开发环境 Dockerfile
```dockerfile
# Dockerfile.dev
FROM node:20-alpine

# 安装开发工具
RUN apk add --no-cache \
    git \
    curl \
    bash \
    vim

# 创建开发用户
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 developer

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package.json package-lock.json* ./

# 安装所有依赖
RUN npm ci

# 切换到开发用户
USER developer

# 复制源代码
COPY --chown=developer:nodejs . .

# 暴露端口
EXPOSE 3000

# 启动开发服务器
CMD ["npm", "run", "dev"]
```

## 📋 Docker Compose 配置

### 开发环境配置

#### 🏠 docker-compose.dev.yml
```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=http://localhost:3001
      - DATABASE_URL=postgresql://postgres:password@db:5432/nextjs_dev
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - db
      - redis
    command: npm run dev
    restart: unless-stopped
    networks:
      - dev-network

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: nextjs_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./scripts/init-dev-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - dev-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data
    command: redis-server --appendonly yes --requirepass dev_password
    healthcheck:
      test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "dev_password", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped
    networks:
      - dev-network

  adminer:
    image: adminer:latest
    ports:
      - "8080:8080"
    depends_on:
      - db
    networks:
      - dev-network

  redis-commander:
    image: rediscommander/redis-commander:latest
    ports:
      - "8081:8081"
    environment:
      REDIS_HOSTS: local:redis:6379:0:dev_password
    depends_on:
      - redis
    networks:
      - dev-network

volumes:
  postgres_dev_data:
  redis_dev_data:

networks:
  dev-network:
    driver: bridge
```

### 生产环境配置

#### 🚀 docker-compose.prod.yml
```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/nextjs_prod
      - REDIS_URL=redis://redis:6379
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
      - NEXTAUTH_URL=${NEXTAUTH_URL}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: "1.0"
          memory: "1G"
        reservations:
          cpus: "0.5"
          memory: "512M"
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: nextjs_prod
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - postgres_backups:/backups
      - ./scripts/init-prod-db.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: "2G"
        reservations:
          cpus: "1.0"
          memory: "1G"
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    volumes:
      - redis_prod_data:/data
      - redis_backups:/backups
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD} --maxmemory 512mb --maxmemory-policy allkeys-lru
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: "512M"
        reservations:
          cpus: "0.2"
          memory: "256M"
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - app
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: "256M"
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - app-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_prod_data:
    driver: local
  postgres_backups:
    driver: local
  redis_prod_data:
    driver: local
  redis_backups:
    driver: local
  nginx_logs:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

networks:
  app-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 测试环境配置

#### 🧪 docker-compose.test.yml
```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=test
      - DATABASE_URL=postgresql://postgres:test_password@db:5432/nextjs_test
      - REDIS_URL=redis://redis:6379
      - NEXTAUTH_SECRET=test_secret
      - NEXTAUTH_URL=http://localhost:3000
    depends_on:
      - db
      - redis
    command: npm run test
    networks:
      - test-network

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: nextjs_test
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: test_password
    tmpfs:
      - /var/lib/postgresql/data
    networks:
      - test-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    tmpfs:
      - /data
    command: redis-server --save ""
    networks:
      - test-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

networks:
  test-network:
    driver: bridge
```

## 🌐 Nginx 配置

### 生产级 Nginx 配置

#### 📄 nginx/nginx.conf
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    log_format detailed '$remote_addr - $remote_user [$time_local] "$request" '
                       '$status $body_bytes_sent "$http_referer" '
                       '"$http_user_agent" "$http_x_forwarded_for" '
                       'rt=$request_time uct="$upstream_connect_time" '
                       'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log detailed;

    # 基本设置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # 连接设置
    client_max_body_size 10M;
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # 安全头部
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'self';" always;

    # 限流设置
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # 上游服务器
    upstream app {
        least_conn;
        server app_1:3000 max_fails=3 fail_timeout=30s;
        server app_2:3000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    # 包含配置文件
    include /etc/nginx/conf.d/*.conf;
}
```

#### 📄 nginx/conf.d/default.conf
```nginx
# HTTP服务器 - 重定向到HTTPS
server {
    listen 80;
    server_name example.com www.example.com;

    # 重定向所有HTTP请求到HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS服务器
server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    # SSL配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # 根路径
    root /var/www/html;
    index index.html index.htm;

    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|webp|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
        try_files $uri @app;
    }

    # Next.js静态文件
    location /_next/static/ {
        alias /app/.next/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
        add_header X-Cache-Status "STATIC";
    }

    # API路由 - 限流
    location /api/ {
        limit_req zone=api burst=20 nodelay;

        proxy_pass http://app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;

        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 登录API - 特殊限流
    location /api/auth/ {
        limit_req zone=login burst=5 nodelay;

        proxy_pass http://app;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 主应用
    location / {
        proxy_pass http://app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # 启用缓存
        proxy_cache app_cache;
        proxy_cache_valid 200 5m;
        proxy_cache_key $scheme$proxy_host$request_uri;
        proxy_cache_bypass $http_pragma $http_authorization;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # robots.txt
    location = /robots.txt {
        access_log off;
        log_not_found off;
    }

    # 拒绝访问隐藏文件
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# 上游缓存配置
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app_cache:10m max_size=1g inactive=60m use_temp_path=off;
```

## 📜 部署脚本

### 自动化部署

#### 🚀 scripts/deploy.sh
```bash
#!/bin/bash
set -euo pipefail

# 配置
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deploy.log"
HEALTH_CHECK_URL="http://localhost/api/health"
MAX_RETRIES=30
RETRY_DELAY=10

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# 检查前置条件
check_prerequisites() {
    log "检查前置条件..."

    # 检查Docker
    if ! command -v docker &> /dev/null; then
        error "Docker 未安装"
        exit 1
    fi

    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose 未安装"
        exit 1
    fi

    # 检查环境变量文件
    if [[ ! -f ".env.prod" ]]; then
        error ".env.prod 文件不存在"
        exit 1
    fi

    # 创建必要目录
    mkdir -p "$BACKUP_DIR"
    mkdir -p "./logs"
    mkdir -p "./ssl"

    success "前置条件检查完成"
}

# 加载环境变量
load_env() {
    log "加载环境变量..."
    set -a
    source .env.prod
    set +a

    # 验证必要的环境变量
    required_vars=("DB_PASSWORD" "REDIS_PASSWORD" "NEXTAUTH_SECRET" "NEXTAUTH_URL")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            error "环境变量 $var 未设置"
            exit 1
        fi
    done

    success "环境变量加载完成"
}

# 备份数据
backup_data() {
    log "备份数据..."

    local timestamp=$(date +%Y%m%d_%H%M%S)

    # 备份数据库
    if docker-compose -f "$COMPOSE_FILE" ps db | grep -q "Up"; then
        log "备份数据库..."
        docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U postgres nextjs_prod > "$BACKUP_DIR/db_backup_${timestamp}.sql"
        gzip "$BACKUP_DIR/db_backup_${timestamp}.sql"
        success "数据库备份完成"
    fi

    # 备份Redis
    if docker-compose -f "$COMPOSE_FILE" ps redis | grep -q "Up"; then
        log "备份Redis..."
        docker-compose -f "$COMPOSE_FILE" exec redis redis-cli --rdb - > "$BACKUP_DIR/redis_backup_${timestamp}.rdb"
        success "Redis备份完成"
    fi

    # 备份环境变量
    cp .env.prod "$BACKUP_DIR/env_backup_${timestamp}"

    success "数据备份完成"
}

# 构建镜像
build_images() {
    log "构建Docker镜像..."

    # 构建应用镜像
    docker-compose -f "$COMPOSE_FILE" build app

    # 可选：推送到镜像仓库
    if [[ "${PUSH_TO_REGISTRY:-false}" == "true" ]]; then
        log "推送镜像到仓库..."
        docker tag nextjs_app:latest "$REGISTRY_URL/nextjs_app:$BUILD_NUMBER"
        docker push "$REGISTRY_URL/nextjs_app:$BUILD_NUMBER"
        success "镜像推送完成"
    fi

    success "镜像构建完成"
}

# 部署服务
deploy_services() {
    log "部署服务..."

    # 停止旧服务
    log "停止旧服务..."
    docker-compose -f "$COMPOSE_FILE" down

    # 启动新服务
    log "启动新服务..."
    docker-compose -f "$COMPOSE_FILE" up -d

    success "服务部署完成"
}

# 健康检查
health_check() {
    log "执行健康检查..."

    local retry_count=0

    while [[ $retry_count -lt $MAX_RETRIES ]]; do
        if curl -f -s "$HEALTH_CHECK_URL" > /dev/null; then
            success "应用健康检查通过"
            return 0
        fi

        retry_count=$((retry_count + 1))
        warning "健康检查失败，重试 $retry_count/$MAX_RETRIES..."
        sleep $RETRY_DELAY
    done

    error "健康检查失败，部署可能有问题"
    return 1
}

# 数据库迁移
run_migrations() {
    log "运行数据库迁移..."

    if docker-compose -f "$COMPOSE_FILE" ps db | grep -q "Up"; then
        docker-compose -f "$COMPOSE_FILE" exec -T app npm run migrate
        success "数据库迁移完成"
    else
        warning "数据库未运行，跳过迁移"
    fi
}

# 清理旧资源
cleanup() {
    log "清理旧资源..."

    # 清理未使用的Docker镜像
    docker image prune -f

    # 清理旧的备份文件（保留最近7天）
    find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "*.rdb" -mtime +7 -delete 2>/dev/null || true

    success "清理完成"
}

# 回滚函数
rollback() {
    error "开始回滚..."

    local timestamp=$(date +%Y%m%d_%H%M%S)

    # 停止当前服务
    docker-compose -f "$COMPOSE_FILE" down

    # 恢复数据库备份
    local latest_backup=$(find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    if [[ -n "$latest_backup" ]]; then
        log "恢复数据库备份..."
        gunzip -c "$latest_backup" | docker-compose -f "$COMPOSE_FILE" exec -T db psql -U postgres nextjs_prod
        success "数据库恢复完成"
    fi

    # 启动服务
    docker-compose -f "$COMPOSE_FILE" up -d

    # 健康检查
    if health_check; then
        success "回滚完成"
    else
        error "回滚失败"
        exit 1
    fi
}

# 主函数
main() {
    log "开始部署 Next.js 应用..."

    # 检查是否是回滚
    if [[ "${1:-}" == "rollback" ]]; then
        rollback
        exit 0
    fi

    # 执行部署流程
    check_prerequisites
    load_env
    backup_data
    build_images
    deploy_services

    # 等待服务启动
    log "等待服务启动..."
    sleep 30

    # 运行迁移
    run_migrations

    # 健康检查
    if health_check; then
        cleanup
        success "部署成功完成！"

        # 发送通知
        if command -v curl &> /dev/null && [[ -n "${SLACK_WEBHOOK_URL}" ]]; then
            curl -X POST -H 'Content-type: application/json' \
                --data "{\"text\":\"✅ Next.js 应用部署成功\\n时间: $(date)\\n环境: production\"}" \
                "$SLACK_WEBHOOK_URL"
        fi
    else
        error "部署失败，开始回滚..."
        rollback
        exit 1
    fi
}

# 错误处理
trap 'error "部署过程中发生错误"; exit 1' ERR

# 执行主函数
main "$@"
```

#### 🔄 scripts/health-check.sh
```bash
#!/bin/bash
set -euo pipefail

# 配置
COMPOSE_FILE="docker-compose.prod.yml"
SERVICES=("app" "db" "redis" "nginx")
LOG_FILE="./logs/health-check.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 日志函数
log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# 检查单个服务
check_service() {
    local service=$1
    local health_url=""

    case $service in
        "app")
            health_url="http://localhost:3000/api/health"
            ;;
        "nginx")
            health_url="http://localhost/health"
            ;;
        "db")
            if docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready -U postgres > /dev/null 2>&1; then
                success "数据库连接正常"
                return 0
            else
                error "数据库连接失败"
                return 1
            fi
            ;;
        "redis")
            if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping > /dev/null 2>&1; then
                success "Redis连接正常"
                return 0
            else
                error "Redis连接失败"
                return 1
            fi
            ;;
    esac

    if [[ -n "$health_url" ]]; then
        if curl -f -s "$health_url" > /dev/null 2>&1; then
            success "$service 服务健康"
            return 0
        else
            error "$service 服务不健康"
            return 1
        fi
    fi
}

# 检查系统资源
check_resources() {
    log "检查系统资源..."

    # 检查磁盘空间
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 80 ]]; then
        warning "磁盘使用率过高: ${disk_usage}%"
    else
        success "磁盘使用率正常: ${disk_usage}%"
    fi

    # 检查内存使用
    local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [[ $mem_usage -gt 90 ]]; then
        warning "内存使用率过高: ${mem_usage}%"
    else
        success "内存使用率正常: ${mem_usage}%"
    fi

    # 检查负载
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    local cpu_cores=$(nproc)
    if (( $(echo "$load_avg > $cpu_cores" | bc -l) )); then
        warning "系统负载过高: $load_avg (CPU核心数: $cpu_cores)"
    else
        success "系统负载正常: $load_avg"
    fi
}

# 主函数
main() {
    log "开始健康检查..."

    local failed_services=()

    # 检查Docker Compose状态
    if ! docker-compose -f "$COMPOSE_FILE" ps > /dev/null 2>&1; then
        error "Docker Compose 服务未运行"
        exit 1
    fi

    # 检查各个服务
    for service in "${SERVICES[@]}"; do
        if ! check_service "$service"; then
            failed_services+=("$service")
        fi
    done

    # 检查系统资源
    check_resources

    # 输出结果
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        success "所有服务健康检查通过"
        exit 0
    else
        error "以下服务健康检查失败: ${failed_services[*]}"
        exit 1
    fi
}

# 执行主函数
main
```

## 🔒 安全配置

### 容器安全最佳实践

#### 🛡️ 安全扫描脚本
```bash
#!/bin/bash
# scripts/security-scan.sh

set -euo pipefail

# 配置
IMAGE_NAME="nextjs_app:latest"
SCAN_REPORT_DIR="./security-reports"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建报告目录
mkdir -p "$SCAN_REPORT_DIR"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[ERROR] $1"
}

success() {
    echo "[SUCCESS] $1"
}

# 检查Docker Bench Security
run_docker_bench() {
    log "运行 Docker Bench Security..."

    if command -v docker-bench-security &> /dev/null; then
        docker-bench-security > "$SCAN_REPORT_DIR/docker-bench-$DATE.txt"
        success "Docker Bench Security 检查完成"
    else
        error "Docker Bench Security 未安装，跳过检查"
    fi
}

# 检查镜像漏洞
run_trivy() {
    log "运行 Trivy 漏洞扫描..."

    if command -v trivy &> /dev/null; then
        trivy image --format json --output "$SCAN_REPORT_DIR/trivy-$DATE.json" "$IMAGE_NAME"
        trivy image --severity HIGH,CRITICAL "$IMAGE_NAME" > "$SCAN_REPORT_DIR/trivy-critical-$DATE.txt"
        success "Trivy 扫描完成"
    else
        error "Trivy 未安装，跳过扫描"
    fi
}

# 检查配置文件安全
check_config_security() {
    log "检查配置文件安全性..."

    # 检查环境变量文件
    if [[ -f ".env.prod" ]]; then
        if grep -E "(password|secret|key)" .env.prod | grep -v "^#" > /dev/null; then
            error "发现明文密码或密钥"
        else
            success "环境变量文件安全检查通过"
        fi
    fi

    # 检查Docker Compose文件权限
    if [[ -f "docker-compose.prod.yml" ]]; then
        local file_perms=$(stat -c "%a" docker-compose.prod.yml)
        if [[ "$file_perms" =~ [0-9]*[6-9][0-9]* ]]; then
            warning "Docker Compose 文件权限过于宽松: $file_perms"
        else
            success "Docker Compose 文件权限正常: $file_perms"
        fi
    fi
}

# 主函数
main() {
    log "开始安全扫描..."

    run_docker_bench
    run_trivy
    check_config_security

    success "安全扫描完成，报告保存在 $SCAN_REPORT_DIR"
}

main
```

## 📊 监控配置

### Prometheus 配置

#### 📈 monitoring/prometheus.yml
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'nextjs-app'
    static_configs:
      - targets: ['app:3000']
    metrics_path: '/api/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s
```

#### 🚨 monitoring/alert_rules.yml
```yaml
groups:
  - name: nextjs-app-alerts
    rules:
      - alert: AppDown
        expr: up{job="nextjs-app"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Next.js 应用宕机"
          description: "Next.js 应用已经宕机超过1分钟"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "错误率过高"
          description: "5xx错误率超过10%"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "响应时间过长"
          description: "95%的请求响应时间超过1秒"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "数据库宕机"
          description: "PostgreSQL数据库已经宕机"

      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis宕机"
          description: "Redis缓存已经宕机"

      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU使用率过高"
          description: "CPU使用率超过80%"

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率过高"
          description: "内存使用率超过85%"

      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "磁盘空间不足"
          description: "磁盘使用率超过90%"
```

## 📋 最佳实践清单

### ✅ Dockerfile优化
- [ ] 使用多阶段构建减少镜像大小
- [ ] 使用非root用户运行容器
- [ ] 优化层缓存和构建顺序
- [ ] 实施健康检查
- [ ] 使用轻量级基础镜像

### ✅ Docker Compose配置
- [ ] 配置资源限制和预留
- [ ] 设置健康检查和重启策略
- [ ] 实现服务发现和负载均衡
- [ ] 配置网络隔离和安全策略
- [ ] 设置数据持久化和备份

### ✅ 安全配置
- [ ] 定期运行安全扫描
- [ ] 实施镜像签名和验证
- [ ] 配置运行时安全策略
- [ ] 管理密钥和敏感信息
- [ ] 实施网络分段和访问控制

### ✅ 监控和日志
- [ ] 配置全面的指标收集
- [ ] 设置智能告警规则
- [ ] 实现日志聚合和分析
- [ ] 建立性能基线监控
- [ ] 配置可视化仪表板

## 🎯 总结

Next.js 16 Docker 容器化部署为现代应用提供了可靠、可扩展的部署解决方案。通过合理配置Dockerfile、Docker Compose、安全策略和监控系统，可以构建企业级的容器化部署架构。

## 🔗 相关资源链接

### 官方资源
- [Docker 官方文档](https://docs.docker.com/)
- [Next.js Docker部署](https://nextjs.org/docs/deployment#docker-image)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Kubernetes部署指南](https://kubernetes.io/docs/concepts/)

### 技术文章
- [Docker多阶段构建最佳实践](https://docs.docker.com/build/building/multi-stage/)
- [Next.js生产环境容器化](https://vercel.com/guides/deploying-a-docker-project)
- [容器安全最佳实践](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [微服务架构设计](https://microservices.io/patterns/microservices.html)

### 工具和资源
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Portainer 容器管理](https://www.portainer.io/)
- [Docker Hub](https://hub.docker.com/)
- [容器监控工具](https://prometheus.io/docs/guides/docker-exporter/)

## 📚 模块内相关文档

### 同模块相关文档
- [Vercel部署指南](./01-vercel-deployment.md) - 对比云平台部署和容器化部署
- [CI/CD流水线](./03-ci-cd-pipelines.md) - 容器化应用的CI/CD集成
- [监控与分析](./04-monitoring-analytics.md) - 容器化应用的监控和日志管理

### 相关知识模块
- [框架相关模块](../frameworks/03-full-stack-patterns.md) - 全栈应用的容器化架构设计
- [框架相关模块](../frameworks/04-performance-optimization.md) - 容器环境下的性能优化
- [测试相关模块](../testing/03-e2e-testing.md) - 容器化环境中的E2E测试

### 基础前置知识
- Docker基础概念 - Docker的核心概念和使用
- [微服务架构](../../01-go-backend/advanced-topics/architecture/01-microservices-design.md) - 微服务架构的基础知识
- [DevOps实践](../deployment/03-ci-cd-pipelines.md) - DevOps和容器化部署

---

## ✨ 总结

### 核心技术要点
1. **多阶段构建**: 优化镜像大小的多阶段Dockerfile构建策略
2. **生产环境配置**: 高性能的生产环境容器配置和Nginx集成
3. **容器编排**: Docker Compose的开发环境管理
4. **安全最佳实践**: 容器安全、权限管理和环境变量保护
5. **扩展和集成**: Kubernetes部署、容器监控和企业级扩展

### 学习成果自检
- [ ] 理解Docker容器化的核心概念和优势
- [ ] 掌握Next.js应用的多阶段构建优化
- [ ] 能够设计和实施生产级容器化部署
- [ ] 熟练运用容器编排和微服务架构
- [ ] 能够建立完整的容器安全和管理体系

---

## 🤝 贡献与反馈

### 贡献指南
欢迎提交Issue和Pull Request来改进本模块内容！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 反馈渠道
- **问题反馈**: [GitHub Issues](https://github.com/your-username/dev-quest/issues)
- **内容建议**: [Discussion板块](https://github.com/your-username/dev-quest/discussions)
- **技术交流**: 欢迎提交PR或Issue参与讨论

### 贡献者
- Dev Quest Team - 核心内容开发
- 社区贡献者 - 内容完善和纠错

---

**📜 文档版本**: v1.0.0
**📅 最后更新**: 2026年9月
**🏷️ 标签**: `#docker` `#containers` `#kubernetes` `#microservices` `#devops`
**⭐ 推荐指数**: ⭐⭐⭐⭐⭐

**💡 提示**: 本模块专注于Docker容器化部署，适合需要企业级部署方案的团队。

**🎯 学习建议**:
- 建议学习周期: 2-3周
- 理论与实践时间比例: 3:7
- 重点掌握多阶段构建和容器安全
- 结合Kubernetes进行大规模部署实践