# 服务器部署：Nginx + PHP-FPM 与发布策略

> **文档简介**: 在传统 VPS 上部署 Laravel——Nginx/PHP-FPM 配置、零停机发布思路（Envoyer/Deployer）与 Supervisor 守护
>
> **目标读者**: 需要直接管理服务器的开发者（跳过容器方案）
>
> **前置知识**: [Docker 部署](./01-docker-deployment.md)（对照参考）、[开发工具链](../frameworks/04-devtools.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Nginx` `#PHP-FPM` `#Deployer` `#Supervisor` `#零停机` |
| **更新日期** | `2026年9月` |

</details>

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

发布 = 解压新版本到 `releases/<ts>` → 软链 `shared/` → 同文件系统临时软链 + rename 切换 current → OPcache reload。回滚 = 把软链指回上一个目录。代码入口切换可以很快，但整体耗时取决于迁移、构建与服务检查——这就是 **Envoyer**（商业产品）与 **Deployer**（开源 PHP 工具）的核心思路。

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
pm.max_children = 20          ; 示例值；按忙时实际内存、CPU 与数据库连接预算测量
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

    location = /index.php {
        include fastcgi_params;
        fastcgi_pass unix:/run/php/php8.5-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        fastcgi_hide_header X-Powered-By;
    }
}
```

发布后若使用 OPcache（`validate_timestamps=0`），执行 `sudo systemctl reload php8.5-fpm` 让新代码生效。

> 💡 **JIT 说明**：PHP 8.4+ 默认 opcache.jit=disable，jit_buffer_size 默认已改为 64M；不要只靠缓冲区大小判断启用状态。需要时在 OPcache 配置中加 `opcache.jit=tracing` 与 `opcache.jit_buffer_size=64M`；典型 Web/I/O 密集应用收益有限，优化优先级仍是查询与缓存（见[缓存策略与队列调优](../advanced-topics/performance/02-caching-queues.md)）。

## 4. Supervisor：队列与调度守护

```ini
; /etc/supervisor/conf.d/laravel-worker.conf
[program:laravel-worker]
command=php /var/www/app/current/artisan queue:work redis --sleep=3 --tries=3 --max-time=3600
process_name=%(program_name)s_%(process_num)02d
numprocs=2                    ; 两个 worker 进程
autostart=true
autorestart=true
user=www-data
stopwaitsecs=180              ; 示例：应超过最长任务时间，并协调 worker timeout/retry_after
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
: "${TAG:?set release tag}" "${REPO_URL:?set repository URL}"
release_dir="/var/www/app/releases/$(date +%Y%m%d%H%M%S)"
git clone --depth 1 --branch "$TAG" "$REPO_URL" "$release_dir"
cd "$release_dir"
# 新检出目录中的 storage 保留作模板，再使用已准备好的共享目录
test -d /var/www/app/shared/storage
test -f /var/www/app/shared/.env
mv storage storage-template
ln -s /var/www/app/shared/storage storage
ln -s /var/www/app/shared/.env .env
composer install --no-dev --optimize-autoloader --no-interaction
php artisan migrate --force
php artisan optimize
# GNU/Linux 同文件系统内以 rename 替换软链，避免错误相对路径
ln -s "$release_dir" /var/www/app/current.next
mv -Tf /var/www/app/current.next /var/www/app/current
sudo systemctl reload php8.5-fpm
php artisan queue:restart
```

脚本逐行可读，正是 Envoyer/Deployer 内部逻辑的骨架。容器化替代方案见 [Docker 部署](./01-docker-deployment.md)。

## ❓ 常见问题

**Q: 502 Bad Gateway？**
A: Nginx 连不上 FPM：查 `php8.5-fpm` 是否运行、socket 路径是否与 Nginx `fastcgi_pass` 一致、`listen.owner` 权限。

**Q: 页面 404 但首页正常？**
A: `try_files` 缺少回退规则，或 Nginx 的 `root` 未指向 `public/`。

<!-- full-library-explanation -->
## 发布完成要由服务行为证明

前置是 Linux 权限、软链接和数据库迁移。软链接切换只改变新请求解析到的代码路径，已经运行的 FPM 请求与队列 worker 可能继续执行旧代码。先采用新旧版本都能兼容的表结构，再切代码、刷新进程并验收；删除旧字段通常要在确认旧进程退出后单独发布。

下方脚本假定 GNU/Linux、共享 storage 已含 Laravel 所需子目录、部署用户权限已配置，且发布串行执行。它提供发布骨架，还需项目自己的构建、测试、TLS、数据库备份及健康检查。TLS 配置必须补证书与私钥路径后才能通过 nginx -t。失败后指回旧目录只能回退代码，不能自动撤销已提交的数据库或外部副作用。

**练习**：在练习服务器发布带版本号的 /health 响应，切换后核对版本、数据库只读查询和队列消费。使新版本健康检查失败，执行代码回退并确认旧版本仍能读取迁移后的数据。用实际忙时进程内存估算 max_children，为系统、缓存和峰值留余量；例子中的 20 不是通用容量建议。

依据：[Laravel 部署](https://laravel.com/docs/13.x/deployment)、[OPcache 配置](https://www.php.net/manual/en/opcache.configuration.php)。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

## 🔗 相关文档

- 📄 [Composer 生态](../reference/library-guides/02-composer-ecosystem.md) — `--no-dev` 安装语义
- 📄 [生产级 Laravel 应用](../projects/04-production-laravel-app.md) — 部署前的完整上线清单
- 📄 [CI/CD 与可观测性](./03-ci-cd-observability.md) — 把本篇脚本接入流水线
- 📄 [PHP 故障排除](../reference/quick-references/02-troubleshooting.md) — 线上报错速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
