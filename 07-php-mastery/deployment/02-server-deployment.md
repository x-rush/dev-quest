# 服务器部署：Nginx + PHP-FPM 与发布策略

> **文档简介**: 在传统 VPS 上部署 Laravel——Nginx/PHP-FPM 配置、零停机发布思路（Envoyer/Deployer）与 Supervisor 守护
>
> **目标读者**: 需要直接管理服务器的开发者（跳过容器方案）
>
> **前置知识**: [Docker 部署](./01-docker-deployment.md)（对照参考）、[开发工具链](../frameworks/04-devtools.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Nginx` `#PHP-FPM` `#Deployer` `#Supervisor` `#零停机` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 完成 Nginx + PHP-FPM 的生产级配置
- ✅ 建立"发布目录 + 软链"的原子发布结构
- ✅ 用 Supervisor 守护队列 worker 与定时任务
- ✅ 了解 Envoyer/Deployer 的自动化思路

## 1. 目录结构：原子发布的基础

```text
/var/www/app/
├── releases/          # 每次发布一个带时间戳的完整目录
│   ├── 20260910143000/
│   └── 20260909090000/
├── shared/            # 跨版本共享：.env、storage/
│   ├── .env
│   └── storage/
└── current -> releases/20260910143000   # 软链切换即"发布"
```

发布 = 解压新版本到 `releases/<ts>` → 软链 `shared/` → `ln -sfn` 切 `current` → OPcache reload。回滚 = 把软链指回上一个目录。整个过程秒级且可脚本化——这就是 **Envoyer**（商业产品）与 **Deployer**（开源 PHP 工具）的核心思路。

```bash
# Deployer 极简用法
composer require --dev deployer/deployer
vendor/bin/dep init            # 生成 deploy.php
vendor/bin/dep deploy production
```

## 2. PHP-FPM 池配置

```ini
; /etc/php/8.5/fpm/pool.d/www.conf 关键参数
[www]
pm = dynamic
pm.max_children = 20          ; 单进程约 50MB 内存 → 上限 = 可用内存 / 50MB
pm.start_servers = 6
pm.min_spare_servers = 4
pm.max_spare_servers = 10
pm.max_requests = 500         ; 防内存泄漏累积：500 次请求后回收进程
```

```ini
; /etc/php/8.5/fpm/php.ini 生产必改
opcache.enable=1
opcache.memory_consumption=256
opcache.max_accelerated_files=20000
opcache.validate_timestamps=0   ; 生产关闭时间戳校验（发布后需 reload FPM）
expose_php=Off
```

## 3. Nginx 站点配置

```nginx
server {
    listen 443 ssl http2;
    server_name app.example.com;
    root /var/www/app/current/public;    # 指向软链，发布后自动生效
    index index.php;

    # 静态资源长缓存（带 hash 的文件名才可这样设）
    location ~* \.(css|js|jpg|png|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass unix:/run/php/php8.5-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        fastcgi_hide_header X-Powered-By;
    }
}
```

发布后若使用 OPcache（`validate_timestamps=0`），执行 `sudo systemctl reload php8.5-fpm` 让新代码生效。

> 💡 **JIT 说明**：PHP 8.x 的 JIT 默认关闭（`opcache.jit_buffer_size=0`）。需要时在 OPcache 配置中加 `opcache.jit=tracing` 与 `opcache.jit_buffer_size=64M`；典型 Web/I/O 密集应用收益有限，优化优先级仍是查询与缓存（见[缓存策略与队列调优](../advanced-topics/performance/02-caching-queues.md)）。

## 4. Supervisor：队列与调度守护

```ini
; /etc/supervisor/conf.d/laravel-worker.conf
[program:laravel-worker]
command=php /var/www/app/current/artisan queue:work redis --sleep=3 --tries=3 --max-time=3600
numprocs=2                    ; 两个 worker 进程
autostart=true
autorestart=true
user=www-data
stopwaitsecs=30               ; 优雅停止：等当前任务处理完
```

```bash
sudo supervisorctl reread && sudo supervisorctl update
# 代码发布后：php artisan queue:restart 让 worker 加载新代码
```

定时任务用 Laravel 自己的调度器统一入口，只加一条 crontab：

```cron
* * * * * cd /var/www/app/current && php artisan schedule:run >> /dev/null 2>&1
```

## 5. 发布脚本最小集

```bash
#!/usr/bin/env bash
set -euo pipefail
TS=$(date +%Y%m%d%H%M%S)
git clone --depth 1 --branch "$TAG" "$REPO_URL" "/var/www/app/releases/$TS"
ln -sfn /var/www/app/shared/.env        "/var/www/app/releases/$TS/.env"
ln -sfn /var/www/app/shared/storage     "/var/www/app/releases/$TS/storage"
cd "/var/www/app/releases/$TS"
composer install --no-dev --optimize-autoloader
php artisan migrate --force
php artisan optimize
ln -sfn "$TS" /var/www/app/current && systemctl reload php8.5-fpm
```

脚本逐行可读，正是 Envoyer/Deployer 内部逻辑的骨架。容器化替代方案见 [Docker 部署](./01-docker-deployment.md)。

## ❓ 常见问题

**Q: 502 Bad Gateway？**
A: Nginx 连不上 FPM：查 `php8.5-fpm` 是否运行、socket 路径是否与 Nginx `fastcgi_pass` 一致、`listen.owner` 权限。

**Q: 页面 404 但首页正常？**
A: `try_files` 缺少回退规则，或 Nginx 的 `root` 未指向 `public/`。

## 🔗 相关文档

- 📄 [Composer 生态](../reference/library-guides/02-composer-ecosystem.md) — `--no-dev` 安装语义
- 📄 [生产级 Laravel 应用](../projects/04-production-laravel-app.md) — 部署前的完整上线清单
- 📄 [CI/CD 与可观测性](./03-ci-cd-observability.md) — 把本篇脚本接入流水线
- 📄 [PHP 故障排除](../reference/quick-references/02-troubleshooting.md) — 线上报错速查
