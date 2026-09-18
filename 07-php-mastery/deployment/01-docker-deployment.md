# 容器化部署：Docker 运行 PHP/Laravel

> **文档简介**: 用多阶段 Dockerfile 与 Compose 编排 PHP-FPM、Nginx、Redis，把 Laravel 应用打包成可复制的交付物
>
> **目标读者**: 准备把项目容器化、追求"本地即生产"的开发者
>
> **前置知识**: [开发工具链](../frameworks/04-devtools.md)、[PHP 故障排除](../reference/quick-references/02-troubleshooting.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Docker` `#PHP-FPM` `#Nginx` `#Laravel` `#部署` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 写出带多阶段构建的生产级 Laravel 镜像
- ✅ 用 Compose 编排 app/nginx/redis 三服务
- ✅ 理解镜像瘦身与权限的常见坑
- ✅ 容器内执行迁移与队列 worker

## 1. 多阶段 Dockerfile

```dockerfile
# Dockerfile：基础扩展在构建与运行阶段保持一致
FROM php:8.5-fpm AS base
RUN apt-get update && apt-get install -y --no-install-recommends libzip-dev unzip \
    && docker-php-ext-install zip pdo_mysql opcache \
    && pecl install redis && docker-php-ext-enable redis \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /var/www/html

FROM base AS build
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --prefer-dist --no-interaction
COPY . .
RUN composer dump-autoload --no-dev --optimize --no-scripts \
    && php artisan package:discover --ansi

FROM base AS app
COPY --from=build /var/www/html /var/www/html
RUN chown -R www-data:www-data storage bootstrap/cache
EXPOSE 9000
CMD ["php-fpm"]
```

要点：`--no-dev` 保证测试依赖不进生产镜像；配置依赖部署环境时，应在注入环境变量后生成 config:cache；不要在通用镜像构建期固化目标环境配置。

## 2. Compose 编排

```yaml
# docker-compose.yml
services:
  app:
    build: .
    env_file: .env.compose # 自备 APP_KEY、DB_DATABASE、DB_USERNAME、DB_PASSWORD 等
    environment: &app-env
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
    env_file: .env.compose
    environment: *app-env
    command: php artisan queue:work --sleep=3 --tries=3
    restart: unless-stopped
    depends_on: [app, redis]

  db:
    image: mysql:8.4
    environment:
      MYSQL_DATABASE: app
      MYSQL_ROOT_PASSWORD: root   # 仅本地演示值
      MYSQL_USER: app
      MYSQL_PASSWORD: local-demo # 与 .env.compose 的 DB_PASSWORD 一致，仅本地
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

    location = /index.php {
        fastcgi_pass app:9000;      # 服务名即 Compose 网络主机名
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
    location ~ \.php$ { return 404; }
    location ~ /\.(?!well-known).* { deny all; }
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
| .env 不生效 | 缓存后不再加载 .env；真实进程环境仍可读取，业务应通过 config()，缓存须在正确配置下生成 |
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

<!-- full-library-explanation -->
## 镜像、配置与持久数据分别管理

前置是镜像层、容器进程和 FPM。FPM 的 9000 端口使用 FastCGI，不能当作 HTTP 服务直接给浏览器访问。Nginx 处理静态文件并转发 PHP 请求；两者必须使用同一版本的 public 文件。这里 Compose 的源码挂载仅供本地练习，生产应把静态资源打成配套镜像或发布产物。

构建前提供 .dockerignore，排除 .env、.env.*（保留无密钥示例文件）、.git、vendor、node_modules、storage/logs 和本机 bootstrap/cache/*.php。否则 COPY . . 可能把密钥、开发依赖或旧配置覆盖进产物。按 composer.lock 补齐项目所需扩展；本例只是基础集合，前端资源构建也需按项目补充。可复现发布进一步固定基础镜像摘要与扩展版本。

**练习**：同一个镜像分别注入两套数据库配置，检查应用实际读取值。故意让数据库尚未启动，确认连接失败可重试，不能把 depends_on 的启动顺序当作就绪保证。app 与 worker 注入同样的 APP_KEY、数据库、Redis 配置，上传文件使用持久卷或对象存储；销毁练习容器后重建，验收持久数据仍在。

依据：[Laravel 部署](https://laravel.com/docs/13.x/deployment)、[Docker 构建上下文](https://docs.docker.com/build/building/context/)。本页未执行镜像构建或部署，需在独立练习项目中补齐环境变量、项目依赖和健康检查后验证。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

## 🔗 相关文档

- 📄 [Composer 生态](../reference/library-guides/02-composer-ecosystem.md) — 镜像内依赖安装细节
- 📄 [开发工具链](../frameworks/04-devtools.md) — Xdebug 在容器中的 client_host 配置
- 📄 [生产级 Laravel 应用](../projects/04-production-laravel-app.md) — 部署前的上线清单
- 📄 [CI/CD 与可观测性](./03-ci-cd-observability.md) — 镜像构建与发布的自动化


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
