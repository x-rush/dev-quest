# 常见错误排查

## 概述

按"报错信息 → 原因 → 修复"组织的故障排除手册，覆盖类型错误、依赖冲突、配置坑三类最高频问题。遇到报错先在此匹配错误关键字。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#故障排除` `#TypeError` `#Composer冲突` `#配置` |
| **更新日期** | `2026年9月` |

## 1. 类型错误（TypeError / ValueError）

### `Fatal error: Uncaught TypeError: ... must be of type string, int given`

**原因**: 严格模式（`strict_types=1`）下传入了错误类型，或可空参数收到 null。
**修复**:

```php
// ❌ 触发：intval 直接塞给 string 参数
echo strlen(intval($raw));

// ✅ 修复：调用前显式转换或校验
$raw = (string) ($_GET['id'] ?? '');
echo strlen($raw);
```

**排查要点**：错误信息给出"第 1 个参数是 int"等精确位置；注意 `strict_types` 约束的是**调用方文件**，检查发起调用的文件是否开了严格模式。

### `Uncaught ValueError: ... is not a valid backing value for enum`

**原因**: `Enum::from()` 收到未定义的 backing 值（常见于数据库脏数据或外部输入）。
**修复**: 外部输入一律 `tryFrom()` 并处理 null：

```php
$status = OrderStatus::tryFrom($row['status'])
    ?? OrderStatus::Pending;   // 或抛出带上下文的业务异常
```

### `Uncaught UnhandledMatchError`

**原因**: `match` 无 `default` 且未命中任何分支。
**修复**: 补分支，或显式 `default => throw new UnexpectedValueException("未知状态: {$v}")` 保留报错语义并给出上下文。

### `DivisionByZeroError` / `ArithmeticError`

**原因**: `/` 与 `%` 除零；`intdiv` 溢出、非法位移。
**修复**: 运算前校验除数；浮点业务可用 `fdiv()`（除零返回 INF/NAN 而不抛错），但结果需再校验。

## 2. 数组与空值类

### `Warning: Undefined array key "x"`

**原因**: 访问不存在的键（8.0 起从 Notice 升级为 Warning）。
**修复**: 读用 `??` 兜底；确定应存在时先 `isset`/`array_key_exists` 断言，把 Warning 变成显式失败。

### `Attempted to read property "name" on null`

**原因**: 链式调用中途为 null（查询无结果、关联未加载）。
**修复**: 空安全运算符 `$user?->name`，或在源头断言非空 `assert($user !== null)`；框架场景优先检查查询是否漏了 `findOrFail`。

### `Cannot use object of type stdClass as array`（及反向）

**原因**: `json_decode($raw)` 默认返回对象，`json_decode($raw, true)` 才是数组。
**修复**: 团队统一约定一种形态（建议 `true` 数组），并全局检索混用点。

## 3. Composer 依赖冲突

### `Your requirements could not be resolved to an installable set of packages`

**原因**: 包 A 要求 `symfony/console:^7.0`，包 B 钉死 `^6.4`，版本区间无交集。
**修复路径**（按优先级）：

```bash
composer why-not symfony/console 7.0    # 看谁卡住了版本
composer why symfony/console            # 看依赖链
composer update phpstan/phpstan --with-all-dependencies   # 定点升级连带依赖
```

1. 升级钉死旧版本的直接依赖
2. 找有兼容新分支的替代包（Packagist 看 `abandoned` 标记）
3. 最后手段：`composer require "pkg:~6.4"` 降级共存——只是延期不是解决

### `Class "App\X" not found` / 自动加载失效

**原因**: PSR-4 路径与命名空间不匹配、新增类未刷新映射、大小写不一致。
**修复**:

```bash
composer dump-autoload           # 首选
composer dump-autoload -o        # classmap 优化后再试
```

核对三要素：`composer.json` 的 `psr-4` 前缀、文件路径、`namespace` 声明——三者必须逐字符对应（Linux 大小写敏感）。

### `composer install` 报缺少 PHP 扩展（`ext-*`）

**原因**: `composer.json` 声明了平台依赖（如 `ext-mbstring`）而本机未装。
**修复**:

```bash
php -m | grep mbstring                       # 确认现状
sudo apt install php8.5-mbstring             # 按报错包名安装对应扩展
```

**注意**: 若只是本地演示而确需跳过平台检查，`composer install --ignore-platform-req=ext-gd`（仅限临时，勿用于生产）。

## 4. 配置坑

### 改了 `php.ini` 不生效

**排查链**:

```bash
php --ini                 # CLI 实际加载哪个 ini
php -i | grep loaded      # 或查 web SAPI 的加载路径
```

- CLI 与 FPM 用**不同**的 ini（`/etc/php/8.5/cli/` vs `/etc/php/8.5/fpm/`）
- FPM 修改后必须 `sudo systemctl reload php8.5-fpm`
- 同一扩展在两个 ini 重复加载会告警

### `Allowed memory size of N bytes exhausted`

**原因**: 单请求内存超限（大结果集、图片处理、死循环累积）。
**修复**: `ini_set('memory_limit', '512M')` 只是止血；根因通常是"全量加载"，改用 `yield` 生成器或分批 `chunk` 处理。

### `Maximum execution time of 30 seconds exceeded`

**原因**: Web 请求超时（默认 30s），多为同步外呼慢接口或大循环。
**修复**: CLI 默认不限制；Web 中拆任务入队列、HTTP 客户端设置短 `timeout`、必要时 `set_time_limit(0)`（长任务仍应改队列）。

### 生产环境白屏 / 500 无日志

**排查顺序**:

1. `display_errors=Off` 是生产标配，看 `log_errors` 指向的日志文件
2. 检查 `error_reporting=E_ALL` 是否被关闭
3. opcache 缓存旧代码：`opcache_reset()` 或重启 FPM
4. 文件权限：`storage/`、`var/log/` 不可写是框架白屏头号原因

### Session 丢失 / Cookie 写不进去

**原因**: `session_start()` 或任何 `header()` 之前已有输出（包括 BOM、`?>` 后空行）。
**修复**: 纯 PHP 文件省略结束标签；输出前禁用任何 echo；用 `headers_sent()` 定位最早的输出点。

## 5. Xdebug 排查速记

| 现象 | 修复 |
|------|------|
| 断点不命中 | 确认 `xdebug.mode=debug`、端口 9003、IDE 监听已开启 |
| CLI 不触发 | 设环境变量 `XDEBUG_SESSION=1` 再运行 |
| 性能骤降 | 开发态正常；确认生产 `php -v` 无 Xdebug |
| 死循环卡死 | 加 `xdebug.max_nesting_level` 与执行步数限制 |

## 相关文档

- 📄 **[现代 PHP 一行式速查](./01-php-cheatsheet.md)** — 写代码时的正确姿势
- 📄 **[Composer 生态精选](../library-guides/02-composer-ecosystem.md)** — `why-not` 等诊断命令详解
- 📄 **[教程：环境搭建](../../basics/01-environment-setup.md)** — 从源头减少环境问题
- 📄 **[教程：错误与异常](../../basics/06-error-exceptions.md)** — 异常体系与兜底设计
