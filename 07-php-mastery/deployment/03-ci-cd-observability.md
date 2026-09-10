# CI/CD 与可观测性：GitHub Actions + Sentry/Telescope

> **文档简介**: 用 GitHub Actions 串联检查-测试-部署流水线，用 Sentry 与 Telescope 建立线上问题的发现与诊断能力
>
> **目标读者**: 已能手动部署、想让发布自动化并"第一时间知道线上坏了"的开发者
>
> **前置知识**: [Feature 测试](../testing/03-feature-testing.md)、[Docker 部署](./01-docker-deployment.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#GitHubActions` `#CI/CD` `#Sentry` `#Telescope` `#可观测性` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 编写覆盖静态检查、测试、构建、部署的完整流水线
- ✅ 理解"检查在 PR、部署在 main"的分支策略
- ✅ 接入 Sentry 错误上报并分级治理
- ✅ 用 Telescope 定位开发/预发环境的慢查询与异常

## 1. GitHub Actions 流水线

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  checks:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.4
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: testing
        ports: ["3306:3306"]
        options: >-
          --health-cmd="mysqladmin ping" --health-interval=10s
          --health-timeout=5s --health-retries=5
    steps:
      - uses: actions/checkout@v4

      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.3'
          coverage: none

      - name: Install dependencies
        run: composer install --prefer-dist --no-interaction

      - name: Static analysis (PHPStan)
        run: vendor/bin/phpstan analyse --error-format=github

      - name: Run tests
        run: php artisan test
        env:
          DB_CONNECTION: mysql
          DB_HOST: 127.0.0.1
          DB_DATABASE: testing
          DB_USERNAME: root
          DB_PASSWORD: root

  deploy:
    needs: checks          # 全部检查通过才进入部署
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trigger deploy
        run: ./scripts/deploy.sh   # 内部调用 Docker 构建（deployment/01）或 Deployer（deployment/02）
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

设计原则：**PR 阶段所有检查并行跑**（静态分析 + 全套测试）；**main 分支通过后自动部署**，任何 job 红灯即拦截发布。

## 2. Sentry：错误监控

```bash
composer require sentry/sentry-laravel
php artisan sentry:publish --dsn=...   # 写入 .env 的 SENTRY_LARAVEL_DSN
```

```php
// 定向增强：给错误附加业务上下文
use function Sentry\configureScope;

public function handle(Order $order): void
{
    configureScope(function ($scope) use ($order): void {
        $scope->setTag('order.status', $order->status->value);
    });

    // ...业务逻辑；未捕获异常自动上报
}
```

治理纪律：

- `warning` 及以上的错误进值班群，`error` 起自动建 issue
- **禁止吞异常**：catch 后不上报等于给线上问题打码，至少 `report($e)`
- 按版本（release）分组，部署后新错误一眼可见

## 3. Laravel Telescope：请求级诊断

```bash
composer require --dev laravel/telescope   # 只装在开发/预发
php artisan telescope:install && php artisan migrate
```

Telescope 记录每个请求的 SQL、队列任务、异常、日志——是"本地复现线上诡异行为"的利器。注意两点：

- **只用于非生产环境**（官方建议），生产请用 Sentry + 慢查询日志组合
- `telescope:prune` 定期清理，防止表膨胀

## 4. 可观测性三支柱落地

| 支柱 | 工具 | 最小实践 |
|------|------|---------|
| 日志 | Laravel Log + 结构化上下文 | 关键路径 `Log::warning('...', ['order_id' => ...])` |
| 指标 | /health 探针 + 队列深度 | `failed_jobs` 行数告警 |
| 追踪 | Sentry performance / trace id | 请求入口生成 trace id 贯穿日志 |

从"报障才查"到"告警先知"的分水岭，就是把这三件事在部署当天接完。

## ❓ 常见问题

**Q: CI 里测试偶发失败（数据库连不上）？**
A: service 容器未就绪。确认 health check options 已配置，或测试前加 `mysqladmin ping` 等待循环。

**Q: Sentry 报了错误但堆栈全是 vendor？**
A: 上传 PHP 运行时与代码的 release 标记（`SENTRY_RELEASE` 设为 commit sha），并在 Sentry 后台启用源码上下文。

## 🔗 相关文档

- 📄 [PHPUnit 单元测试](../testing/01-unit-testing.md) — 流水线中的测试层
- 📄 [开发工具链](../frameworks/04-devtools.md) — phpstan 与 Xdebug 的日常用法
- 📄 [生产级 Laravel 应用](../projects/04-production-laravel-app.md) — 流水线对应的上线清单
- 📄 [缓存策略与队列调优](../advanced-topics/performance/02-caching-queues.md) — 告警背后的队列指标
