# 开发工具链：Composer、Artisan、PHPStan 与 Xdebug

> **文档简介**: 配齐 PHP 开发者的四件日常武器——依赖管理、代码生成、静态分析与断点调试
>
> **目标读者**: 希望把本地开发效率提升一个档次的 PHP 学习者
>
> **前置知识**: [环境搭建](../basics/01-environment-setup.md)、[Composer 生态速查](../reference/library-guides/02-composer-ecosystem.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#Composer` `#Artisan` `#PHPStan` `#Xdebug` `#工具链` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 熟练使用 Composer 的依赖与脚本工作流
- ✅ 用 Artisan 生成器与 tinker 加速日常开发
- ✅ 部署 PHPStan/Larastan 并让级别 6+ 检查通过
- ✅ 配置 Xdebug 3 断点调试与性能分析

## 1. Composer

```bash
composer require laravel/sanctum           # 安装运行时依赖
composer require --dev larastan/larastan   # 安装开发期依赖

composer install                     # 按 lock 文件精确安装（CI/生产用）
composer update laravel/framework    # 只升级指定包并更新 lock
composer dump-autoload -o            # 重新生成优化过的自动加载映射
```

`composer.json` 中的 `scripts` 可把团队流程固化为命令：

```json
{
    "scripts": {
        "analyze": "phpstan analyse --memory-limit=1G",
        "test": "php artisan test"
    }
}
```

之后 `composer analyze` 即可全仓静态检查。lock 文件必须提交进仓库，保证所有人环境一致。

## 2. Artisan

```bash
# 生成器：模型、迁移、控制器、工厂一条龙
php artisan make:model Post -mfsc   # -m 迁移 -f 工厂 -s Seeder -c 控制器
php artisan make:request StorePostRequest  # 表单请求（集中验证逻辑）

# 交互式 REPL：直接在终端里试 Eloquent
php artisan tinker
# >>> Post::whereNotNull('published_at')->count();

php artisan route:list --except-vendor   # 查看全部路由
php artisan db:show --counts             # 检查表行数
php artisan optimize                     # 生产前缓存配置/路由/事件
```

自定义命令（`php artisan make:command PruneOldPosts`）把重复运维动作脚本化，是对"手动改线上"最有效的替代。

## 3. PHPStan / Larastan

```bash
composer require --dev larastan/larastan
```

```neon
# phpstan.neon：从低级别起步，逐步收紧
parameters:
    level: 6
    paths:
        - app
```

```bash
composer analyze   # 运行（依赖上文 composer scripts）
```

级别 0-9 递进，Laravel 项目建议 6 起步（Larastan 已理解 Eloquent 魔术方法）。常见收益：

- 抓出对 `?int` 传 `int` 的可空性错误
- 提示未使用的构造器参数与死代码
- 强制数组形状（`array{title: string, body: string}`）替代裸数组

Laravel 13 项目推荐同时使用 **Laravel Pint**（自动代码风格修复，`./vendor/bin/pint`）统一团队格式，把评审时间还给逻辑问题。

## 4. Xdebug 3

```ini
; php.ini 片段（Docker/本地通用）
zend_extension=xdebug
; 调试模式；profile 为性能分析
xdebug.mode=debug
; Docker 内指向宿主机
xdebug.client_host=host.docker.internal
xdebug.client_port=9003
xdebug.start_with_request=yes
```

VS Code `launch.json` 关键片段：

```json
{
    "type": "php",
    "request": "listen",
    "name": "Listen for Xdebug",
    "pathMappings": { "/var/www/html": "${workspaceFolder}" }
}
```

断点调试的正确姿势：在控制器第一行下断点，观察 `$request` 实际结构，再决定验证规则——比 `var_dump` 快一个数量级。

```bash
# 性能分析：生成 cachegrind 文件，用 qcachegrind/KCacheGrind 打开
XDEBUG_MODE=profile php artisan your-slow-command
```

不装 Xdebug 的临时场景用 `php artisan tinker` 也能完成大部分探查；两者配合覆盖 95% 的调试需求。

## ❓ 常见问题

**Q: Xdebug 触发后 IDE 没反应？**
A: 三查：端口 9003 是否被占用、`client_host` 在 Docker 里是否指向宿主、防火墙是否放行。`php -v` 出现 `Xdebug` 字样才代表扩展已加载。

**Q: PHPStan 报 Eloquent 关系返回类型未知？**
A: 给模型关系方法写明确的返回类型（`HasMany` 等），Larastan 即可推断链式调用类型；裸 `$model->posts` 动态属性尽量少用。

## 🔗 相关文档

- 📄 [Composer 生态速查](../reference/library-guides/02-composer-ecosystem.md) — 依赖解析与版本约束字典
- 📄 [PHP 快速速查表](../reference/quick-references/01-php-cheatsheet.md) — 语法级速查
- 📄 [故障排除](../reference/quick-references/02-troubleshooting.md) — 常见报错对照
- 📄 [单元测试](../testing/01-unit-testing.md) — 与静态分析互补的质量手段
