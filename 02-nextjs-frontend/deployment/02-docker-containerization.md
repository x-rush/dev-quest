# Docker容器化部署指南 (Docker Containerization Guide)

> **PHP开发者视角**: 从传统虚拟机部署到现代容器化部署的转变，了解Docker如何简化Next.js应用的部署和管理。

## Docker基础概念

### 什么是Docker

Docker是一个开源的容器化平台，允许开发者将应用程序及其依赖项打包到轻量级、可移植的容器中。

### 为什么使用Docker

1. **环境一致性**: 确保开发、测试、生产环境完全一致
2. **快速部署**: 容器启动速度快，便于扩展
3. **资源隔离**: 提供安全的运行环境
4. **版本控制**: 镜像版本化管理
5. **微服务架构**: 支持服务拆分和独立部署

## Dockerfile配置

### 1. 多阶段构建

```dockerfile
# Dockerfile
# 构建阶段
FROM node:18-alpine AS builder

# 安装依赖
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM node:18-alpine AS runner

# 创建应用用户
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 设置工作目录
WORKDIR /app

# 复制构建产物
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 设置环境变量
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# 创建缓存目录
RUN mkdir .next
RUN chown nextjs:nodejs .next

# 切换用户
USER nextjs

# 暴露端口
EXPOSE 3000

# 启动应用
CMD ["node", "server.js"]
```

### 2. 优化的Dockerfile

```dockerfile
# Dockerfile.optimized
# 构建阶段
FROM node:18-alpine AS deps

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package.json package-lock.json* ./

# 安装依赖
RUN npm ci

# 构建阶段
FROM node:18-alpine AS builder

# 安装构建依赖
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package.json ./package.json
COPY --from=deps /app/package-lock.json ./package-lock.json

# 复制源代码
COPY . .

# 禁用遥测
ENV NEXT_TELEMETRY_DISABLED=1

# 构建应用
RUN npm run build

# 生产阶段
FROM node:18-alpine AS runner

# 安装系统依赖
RUN apk add --no-cache \
    libc6-compat \
    dumb-init \
    && addgroup -g 1001 -S nodejs \
    && adduser -S nextjs -u 1001

# 设置工作目录
WORKDIR /app

# 复制构建产物
COPY --from=builder /app/public ./public

# 设置正确的权限
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 设置环境变量
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# 创建进程管理目录
RUN mkdir -p /app/.next/cache && chown nextjs:nodejs /app/.next/cache

# 切换用户
USER nextjs

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# 启动应用
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
```

## Docker Compose配置

### 1. 开发环境配置

```yaml
# docker-compose.dev.yml
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
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - db
      - redis
    command: npm run dev

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  postgres_data:
  redis_data:
```

### 2. 生产环境配置

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/myapp
      - REDIS_URL=redis://redis:6379
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
      - NEXTAUTH_URL=${NEXTAUTH_URL}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - app-network
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    healthcheck:
      test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
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

## 开发环境Dockerfile

```dockerfile
# Dockerfile.dev
FROM node:18-alpine

# 安装开发工具
RUN apk add --no-cache git

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装所有依赖（包括开发依赖）
RUN npm ci

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 3000

# 启动开发服务器
CMD ["npm", "run", "dev"]
```

## Nginx配置

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # 基本设置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
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

    # 上游服务器
    upstream app {
        server app:3000;
    }

    # HTTP服务器
    server {
        listen 80;
        server_name example.com www.example.com;

        # 重定向到HTTPS
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
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # 安全头部
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

        # 静态文件缓存
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|webp)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            try_files $uri @app;
        }

        # Next.js静态文件
        location /_next/static/ {
            alias /app/.next/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        # API路由
        location /api/ {
            proxy_pass http://app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
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
        }

        # 健康检查
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

## 数据库初始化

```sql
-- init.sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS myapp;

-- 连接到数据库
\c myapp;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建会话表
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token);

-- 插入初始数据
INSERT INTO users (email, name, password_hash) VALUES
('admin@example.com', 'Admin', '$2b$12$example_hash'),
('user@example.com', 'User', '$2b$12$example_hash')
ON CONFLICT (email) DO NOTHING;
```

## 部署脚本

### 1. 构建脚本

```bash
#!/bin/bash
# scripts/build.sh

set -e

echo "🚀 开始构建Docker镜像..."

# 构建应用镜像
echo "📦 构建应用镜像..."
docker build -t my-app:latest .

# 推送到镜像仓库
echo "📤 推送镜像到仓库..."
docker tag my-app:latest registry.example.com/my-app:latest
docker push registry.example.com/my-app:latest

echo "✅ 构建完成！"
```

### 2. 部署脚本

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 开始部署应用..."

# 设置环境变量
export COMPOSE_FILE=docker-compose.prod.yml
export DB_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)
export NEXTAUTH_SECRET=$(openssl rand -base64 64)

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose -f $COMPOSE_FILE down

# 拉取最新镜像
echo "📥 拉取最新镜像..."
docker-compose -f $COMPOSE_FILE pull

# 启动服务
echo "🏃 启动服务..."
docker-compose -f $COMPOSE_FILE up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 健康检查
echo "🏥 健康检查..."
if curl -f http://localhost:3000/api/health; then
    echo "✅ 部署成功！"
else
    echo "❌ 部署失败！"
    exit 1
fi

# 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
docker-compose -f $COMPOSE_FILE exec -T db psql -U postgres -d myapp -f /migrations/latest.sql

echo "✅ 部署完成！"
```

### 3. 备份脚本

```bash
#!/bin/bash
# scripts/backup.sh

set -e

echo "💾 开始备份数据..."

# 设置变量
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_BACKUP_FILE="${BACKUP_DIR}/db_${DATE}.sql"
APP_BACKUP_FILE="${BACKUP_DIR}/app_${DATE}.tar.gz"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
echo "🗄️ 备份数据库..."
docker-compose exec -T db pg_dump -U postgres myapp > $DB_BACKUP_FILE
gzip $DB_BACKUP_FILE

# 备份应用文件
echo "📁 备份应用文件..."
docker-compose exec app tar -czf - /app/.next/static > $APP_BACKUP_FILE

# 备份环境变量
echo "🔧 备份环境变量..."
cp .env.prod ${BACKUP_DIR}/env_${DATE}.backup

# 清理旧备份（保留最近7天）
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.backup" -mtime +7 -delete

echo "✅ 备份完成！"
echo "📁 备份文件位置: $BACKUP_DIR"
```

## 监控和日志

### 1. 日志配置

```yaml
# docker-compose.prod.yml (补充)
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    environment:
      - NODE_ENV=production
      - LOG_LEVEL=info

  db:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 2. 监控脚本

```bash
#!/bin/bash
# scripts/monitor.sh

set -e

echo "📊 检查服务状态..."

# 检查容器状态
echo "🔍 检查容器状态..."
docker-compose ps

# 检查应用健康状态
echo "❤️ 检查应用健康状态..."
if curl -f http://localhost:3000/api/health; then
    echo "✅ 应用健康"
else
    echo "❌ 应用不健康"
    exit 1
fi

# 检查数据库连接
echo "🗄️ 检查数据库连接..."
if docker-compose exec -T db pg_isready -U postgres; then
    echo "✅ 数据库连接正常"
else
    echo "❌ 数据库连接失败"
    exit 1
fi

# 检查Redis连接
echo "🔴 检查Redis连接..."
if docker-compose exec -T redis redis-cli ping; then
    echo "✅ Redis连接正常"
else
    echo "❌ Redis连接失败"
    exit 1
fi

# 检查磁盘空间
echo "💾 检查磁盘空间..."
df -h | grep -E "(/dev/|/var/lib/docker)"

# 检查内存使用
echo "🧠 检查内存使用..."
free -h

echo "✅ 监控检查完成！"
```

## 安全配置

### 1. Docker安全最佳实践

```dockerfile
# Dockerfile.security
# 使用非root用户
FROM node:18-alpine

# 创建专用用户
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# 安装必要的安全包
RUN apk add --no-cache dumb-init

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# 复制源代码
COPY --chown=nextjs:nodejs . .

# 构建应用
USER nextjs
RUN npm run build

# 切换回root复制构建产物
USER root
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 切换回非root用户
USER nextjs

# 设置环境变量
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# 启动应用
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
```

### 2. 网络安全配置

```yaml
# docker-compose.security.yml
version: "3.8"

services:
  app:
    build: .
    networks:
      - app-network
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /var/run/nginx/tmp
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - NET_BIND_SERVICE

  db:
    image: postgres:15-alpine
    networks:
      - app-network
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    read_only: true
    tmpfs:
      - /tmp
      - /var/run/postgresql
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID

  redis:
    image: redis:7-alpine
    networks:
      - app-network
    command: redis-server --requirepass ${REDIS_PASSWORD}
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    cap_add:
      - SETGID
      - SETUID

networks:
  app-network:
    driver: bridge
    internal: true

secrets:
  db_password:
    file: ./secrets/db_password.txt

volumes:
  postgres_data:
```

## 性能优化

### 1. 构建优化

```dockerfile
# Dockerfile.optimized
# 使用多阶段构建减少镜像大小
FROM node:18-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package.json ./package.json
COPY --from=deps /app/package-lock.json ./package-lock.json
COPY . .
RUN npm run build

# 生产阶段
FROM node:18-alpine AS runner
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
WORKDIR /app

# 只复制必要的文件
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NODE_ENV=production

CMD ["node", "server.js"]
```

### 2. 资源限制

```yaml
# docker-compose.prod.yml (补充)
services:
  app:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: "1G"
        reservations:
          cpus: "0.5"
          memory: "512M"

  db:
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: "2G"
        reservations:
          cpus: "1.0"
          memory: "1G"

  redis:
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: "512M"
        reservations:
          cpus: "0.2"
          memory: "256M"
```

## 故障排除

### 1. 常见问题解决

```bash
# 查看容器日志
docker-compose logs app
docker-compose logs db
docker-compose logs redis

# 查看实时日志
docker-compose logs -f app

# 重启服务
docker-compose restart app

# 进入容器调试
docker-compose exec app sh
docker-compose exec db psql -U postgres -d myapp

# 清理未使用的资源
docker system prune -a
docker volume prune
```

### 2. 调试技巧

```bash
# 检查网络连接
docker-compose exec app wget -qO- http://localhost:3000/api/health

# 检查数据库连接
docker-compose exec app node -e "const { PrismaClient } = require('@prisma/client'); const prisma = new PrismaClient(); prisma.$connect().then(() => console.log('Database connected')).catch(e => console.error('Database connection failed'))"

# 检查Redis连接
docker-compose exec redis redis-cli ping

# 检查端口占用
netstat -tulpn | grep :3000
```

## 总结

通过本指南，我们学习了如何使用Docker容器化部署Next.js应用的各个方面：

### 核心概念
- Docker容器化的优势
- 多阶段构建的原理
- 容器编排的概念

### 实践技能
- Dockerfile编写和优化
- Docker Compose配置
- 生产环境部署
- 监控和日志管理

### 高级主题
- 安全配置
- 性能优化
- 故障排除
- 自动化部署

### 从PHP开发者角度
- 从传统部署到容器化部署的转变
- Docker简化了环境配置和部署流程
- 提高了应用的可移植性和可扩展性

掌握Docker容器化技能，将帮助您更加高效地部署和管理Next.js应用，享受现代容器化技术带来的便利和优势。容器化不仅是一种部署方式，更是现代软件开发和运维的标准实践。