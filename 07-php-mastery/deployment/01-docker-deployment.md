# 容器化部署：Docker 运行 PHP/Laravel

> **文档简介**: 用多阶段 Dockerfile 与 Compose 编排 PHP-FPM、Nginx、Redis，把 Laravel 应用打包成可复制的交付物
>
> **目标读者**: 准备把项目容器化、追求"本地即生产"的开发者
>
> **前置知识**: [开发工具链](../frameworks/04-devtools.md)、[PHP 故障排除](../reference/quick-references/02-troubleshooting.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Docker` `#PHP-FPM` `#Nginx` `#Laravel` `#部署` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 写出带多阶段构建的生产级 Laravel 镜像
- ✅ 用 Compose 编排 app/nginx/redis 三服务
- ✅ 理解镜像瘦身与权限的常见坑
- ✅ 容器内执行迁移与队列 worker

## 1. 多阶段 Dockerfile

```dockerfile
# Dockerfile —— 构建阶段与运行阶段分离，最终镜像不含 composer/dev 依赖
FROM php:8.3-cli AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
        git unzip libzip-dev \
    && docker-php-ext-install zip pdo_mysql opcache

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /app
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --prefer-dist --no-interaction
COPY . .
RUN composer dump-autoload --optimize && php artisan config:cache && php artisan route:cache


# 运行阶段：只拷贝产物
FROM php:8.3-fpm-alpine

RUN docker-php-ext-install pdo_mysql opcache

COPY --from=build /app /var/www/html
RUN chown -R www-data:www-data storage bootstrap/cache

EXPOSE 9000
CMD ["php-fpm"]
```

要点：`--no-dev` 保证测试依赖不进生产镜像；`config:cache`/`route:cache` 在**构建期**完成，运行时只读。

## 2. Compose 编排

```yaml
# docker-compose.yml
services:
  app:
    build: .
    environment:
      DB_HOST: db
      REDIS_HOST: redis
      QUEUE_CONNECTION: redis
    depends_on: [db, redis]

  web:
    image: nginx:1.27-alpine
    ports: ["8080:80"]
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      # PHP-FPM 场景下静态文件也需可读
      - ./:/var/www/html:ro
    depends_on: [app]

  worker:
    build: .
    command: php artisan queue:work --sleep=3 --tries=3
    depends_on: [app, redis]

  db:
    image: mysql:8.4
    environment:
      MYSQL_DATABASE: app
      MYSQL_ROOT_PASSWORD: root   # 仅本地演示值
    volumes: [db-data:/var/lib/mysql]

  redis:
    image: redis:7-alpine

volumes:
  db-data:
```

```nginx
# nginx.conf —— 关键配置节
server {
    listen 80;
    root /var/www/html/public;      # 永远指向 public，防止源码泄露
    index index.php;

    location / { try_files $uri $uri/ /index.php?$query_string; }

    location ~ \.php$ {
        fastcgi_pass app:9000;      # 服务名即 Compose 网络主机名
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```

```bash
docker compose up -d --build
docker compose exec app php artisan migrate --force   # 容器内执行迁移
```

## 3. 容器化 PHP 的三个经典坑

| 现象 | 原因与对策 |
|------|-----------|
| storage 权限报错 | 容器内 PHP-FPM 以 `www-data` 运行，构建时 `chown storage bootstrap/cache` |
| .env 不生效 | 生产用 `config:cache` 后 `env()` 失效，环境变量在容器层注入 |
| 镜像超 1GB | 忘了多阶段构建，或装了 dev 依赖；用 Alpine 基础镜像 |

## 4. 上线节奏

```text
构建 CI 镜像（tag = commit sha）
  → 推送镜像仓库
  → 部署平台拉取新镜像
  → docker compose exec app php artisan migrate --force
  → 平滑重启 worker：php artisan queue:restart
```

迁移放在启动新版本之前执行，保证旧代码兼容新表结构（向后兼容式迁移）。无容器场景见[服务器部署](./02-server-deployment.md)；流水线串联见[CI/CD 与可观测性](./03-ci-cd-observability.md)。

## ❓ 常见问题

**Q: 容器里 `php artisan` 报 `file not found`？**
A: 工作目录不对。Dockerfile 中确认 `WORKDIR` 与代码拷贝目标一致（本例为 `/app` 构建态、`/var/www/html` 运行态）。

**Q: 队列 worker 收不到任务？**
A: 三查：`QUEUE_CONNECTION` 环境变量是否传进容器、`queue:restart` 是否执行过（代码更新后 worker 仍在跑旧代码）、redis 网络是否互通。

## 🔗 相关文档

- 📄 [Composer 生态](../reference/library-guides/02-composer-ecosystem.md) — 镜像内依赖安装细节
- 📄 [开发工具链](../frameworks/04-devtools.md) — Xdebug 在容器中的 client_host 配置
- 📄 [生产级 Laravel 应用](../projects/04-production-laravel-app.md) — 部署前的上线清单
- 📄 [CI/CD 与可观测性](./03-ci-cd-observability.md) — 镜像构建与发布的自动化
