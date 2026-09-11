# PHP 开发环境搭建 - PHP 8.5+ 与现代工具链

> **文档简介**: 从零搭建现代化 PHP 开发环境，包括 PHP 8.5+ 运行时、Composer 依赖管理、Xdebug 调试器与 IDE 配置
>
> **目标读者**: 有其他语言基础、首次系统学习 PHP 的开发者，或需要把旧环境升级到 PHP 8.5+ 的 PHP 开发者
>
> **前置知识**: 基本命令行操作经验，了解任意一门编程语言

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#环境搭建` `#PHP8.5` `#Composer` `#Xdebug` `#工具链` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 在本机安装并验证 PHP 8.5+ 运行时与常用扩展
- ✅ 安装 Composer 并理解它在 PHP 生态中的角色
- ✅ 配置 Xdebug 3 实现断点调试
- ✅ 在 PhpStorm 或 VS Code 中完成 PHP 开发环境配置

## 1. 安装 PHP 8.5+

PHP 官方对每个版本提供约两年的安全支持。2026 年当前稳定版本为 **PHP 8.5（活跃支持期）**，8.4、8.3 仍在各自支持窗口内；本模块代码以 8.5 语法为基线。

### Linux（Ubuntu/Debian）

推荐使用 Ondřej Surý 的 PPA 源，它提供最新版本与完整扩展：

```bash
# 添加 PPA 并安装 PHP 8.5 及常用扩展
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update
sudo apt install php8.5-cli php8.5-common \
    php8.5-mbstring php8.5-xml php8.5-curl \
    php8.5-sqlite3 php8.5-zip php8.5-intl
```

### macOS

```bash
# 使用 Homebrew 安装（formula 默认即最新稳定版）
brew install php
```

### Windows

从 [windows.php.net/download](https://windows.php.net/download/) 下载 Non Thread Safe 的 zip 包，解压后将目录加入 `PATH` 环境变量，并复制 `php.ini-development` 为 `php.ini`。

### 验证安装

```bash
php -v
# PHP 8.5.x (cli) ... 即为成功

php -m          # 列出已加载扩展
php --ini       # 查看当前使用的 php.ini 位置
```

**关键点**：CLI 与 Web 服务器（FPM）可能使用不同的 `php.ini`（如 `php.ini-development` 与 `php.ini-production`），配置不生效时先用 `php --ini` 确认加载的是哪一个。

## 2. Composer：PHP 的依赖管理器

Composer 是 PHP 生态的事实标准包管理器，相当于 Node 的 npm、Go 的 go modules。现代 PHP 项目几乎都以 `composer.json` 为起点。

### 安装 Composer

```bash
# Linux / macOS（官方安装器）
curl -sS https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer

# 或使用包管理器
brew install composer          # macOS
sudo apt install composer      # Ubuntu（注意版本可能偏旧）
```

```bash
composer --version   # 验证安装
```

### Composer 核心命令

```bash
composer init          # 交互式创建 composer.json
composer require monolog/monolog    # 安装生产依赖
composer require --dev phpunit/phpunit  # 安装开发依赖
composer install       # 按 composer.lock 安装全部依赖
composer update        # 升级依赖并更新 lock 文件
composer dump-autoload # 重新生成自动加载映射
```

> 💡 **锁文件原则**：`composer.lock` 必须提交到版本库，团队与生产环境统一用 `composer install` 保证依赖版本一致；只有维护者主动升级时才运行 `composer update`。

依赖与自动加载的深入用法见 [`../reference/library-guides/02-composer-ecosystem.md`](../reference/library-guides/02-composer-ecosystem.md)。

## 3. 配置 Xdebug 3 调试器

Xdebug 是 PHP 最主流的调试与性能分析扩展，3.x 版本用 `xdebug.mode` 取代了旧版一堆布尔开关。

### 安装

```bash
# 通过 PECL 安装（需要 php-dev / phpize）
pecl install xdebug

# macOS Homebrew
brew install pecl && pecl install xdebug
```

### 配置

在 `php.ini`（或独立的 `conf.d/xdebug.ini`）中加入：

```ini
[xdebug]
zend_extension=xdebug
xdebug.mode=debug           # debug=断点调试，develop=错误提示增强
xdebug.start_with_request=yes
xdebug.client_host=127.0.0.1
xdebug.client_port=9003     # Xdebug 3 默认端口从 9000 改为 9003
```

### 验证

```bash
php -v
# 输出中若包含 "with Xdebug v3.x" 即安装成功
```

也可以写一个 `<?php phpinfo();` 页面确认 Web 环境同样加载了 Xdebug。

## 4. IDE 配置

### PhpStorm（推荐）

1. **解释器**：`Settings → PHP`，选择 CLI Interpreter 为 php8.5
2. **Xdebug**：`Settings → PHP → Debug`，确认端口 9003；`Settings → PHP → Servers` 添加服务器映射（服务器路径 ↔ 本地路径）
3. **代码风格**：`Settings → PHP → Quality Tools` 接入 PHPStan / PHP CS Fixer
4. 零配置调试：点击工具栏"监听 PHP Debug Connections"后访问带 `XDEBUG_SESSION=1` Cookie 的页面即命中断点

### VS Code

安装 **Intelephense**（智能补全）与 **PHP Debug**（xdebug.php-debug）两个扩展，然后在工作区 `.vscode/launch.json` 中添加：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Listen for Xdebug",
      "type": "php",
      "request": "launch",
      "port": 9003
    }
  ]
}
```

> 💡 **建议**：避免同时启用多个 PHP 补全扩展（如 Intelephense 与 PHP Tools），它们会互相冲突造成卡顿。

## 5. 验证环境：跑通第一段代码

创建 `check.php`：

```php
<?php

declare(strict_types=1);

// 输出版本与已加载的关键扩展
printf("PHP 版本: %s\n", PHP_VERSION);
printf("Xdebug: %s\n", extension_loaded('xdebug') ? '已启用' : '未启用');
printf("Composer: %s\n", shell_exec('composer --version 2>/dev/null') ?? '未安装');
```

```bash
php check.php
```

## ✅ 最佳实践

- ✅ **用版本管理器**：使用 `brew` 或 phpbrew/asdf 管理多个 PHP 版本，方便在不同项目间切换
- ✅ **开发/生产配置分离**：本地用 `php.ini-development`（错误直接显示），生产环境必须用 production 配置并关闭 `display_errors`
- ✅ **所有项目用 Composer 管理依赖**：不要手工下载类库或修改全局 `php.ini` 来"装库"
- ❌ **避免使用 PHP 8.0 以下的版本**：枚举、属性注解、构造器属性提升等现代特性均需 8.1+
- ❌ **不要用 `@` 错误抑制符**：现代 PHP 应通过异常处理与 `error_reporting` 管理错误

## ❓ 常见问题

### Q1: `php -v` 显示旧版本怎么办？
**A**: 通常是 PATH 中存在多个 PHP。用 `which php` 查看实际调用的二进制，调整 PATH 顺序或卸载系统自带的旧包。

### Q2: Xdebug 已安装但断点不命中？
**A**: 按顺序排查：① `php -v` 确认扩展加载；② `xdebug.mode` 是否为 `debug`；③ IDE 监听端口是否为 9003；④ CLI 调试需要设置环境变量 `XDEBUG_SESSION=1`。

### Q3: Composer 提示缺少扩展？
**A**: Composer 会按 `composer.json` 的 `require` 检查平台依赖。先安装对应扩展（如 `sudo apt install php8.5-mbstring`）再重试。

## 🎯 练习与实践

### 基础练习
- [ ] 安装 PHP 8.5+ 并让 `php check.php` 输出正确信息
- [ ] 创建一个空目录并运行 `composer init`，观察生成的 `composer.json`
- [ ] 配置 Xdebug 并在 IDE 中对 `check.php` 打上断点命中一次

### 进阶挑战
- [ ] 用 Docker 编写一个包含 PHP 8.5 + Xdebug 的 `Dockerfile`，在容器内复现本篇环境
- [ ] 对比 `php.ini-development` 与 `php.ini-production` 的差异，列出你认为最重要的 5 项配置

---

## 🔗 相关文档

- 📄 **[第二个脚本：CLI 与 Web 双运行模式](./02-first-script.md)** — 环境搭好后的下一步
- 📄 **[PHP 关键字详解](../reference/language-concepts/01-php-keywords.md)** — 阅读 `declare` 等语法的权威条目
- 📄 **[Composer 生态精选](../reference/library-guides/02-composer-ecosystem.md)** — 依赖管理深入
- 📄 **[常见错误排查](../reference/quick-references/02-troubleshooting.md)** — 环境问题速查
