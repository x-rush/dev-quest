# 第一个 PHP 脚本 - CLI 与 Web 双运行模式

## 先理解，再动手

CLI 从参数和标准输入取数据，Web 从请求取数据。输出都可能用 echo，但状态码、请求头和生命周期不同。

**本节自测**：同一问候逻辑分别通过 CLI 参数与 Web 查询参数调用。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

业务函数可复用，输入适配不同；Web 输入必须当作不可信数据。

</details>

> **文档简介**: 编写并运行你的第一个现代 PHP 程序，同时掌握 CLI 与 Web 两种执行方式及各自适用场景
>
> **目标读者**: 已完成环境搭建、希望快速跑通第一个程序的 PHP 初学者
>
> **前置知识**: PHP 8.5+ 环境已就绪（见 [环境搭建](./01-environment-setup.md)），了解基本命令行操作

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#第一个程序` `#CLI` `#内置服务器` `#程序结构` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 编写符合现代规范的 PHP 脚本并理解其结构
- ✅ 用 `php` 命令直接执行脚本（CLI 模式）
- ✅ 用内置服务器运行 Web 页面（Web 模式）
- ✅ 理解 `declare(strict_types=1)` 对程序行为的影响

## 1. 第一个脚本：`hello.php`

创建 `hello.php`：

```php
<?php

declare(strict_types=1);

/**
 * 第一个现代 PHP 程序：演示基本结构与输出
 */

function greet(string $name): string
{
    return "Hello, {$name}! 欢迎来到现代 PHP 的世界。";
}

// 解析命令行参数，未提供时使用默认值
$name = $argv[1] ?? 'PHP Learner';

echo greet($name), PHP_EOL;
printf('当前 PHP 版本: %s%s', PHP_VERSION, PHP_EOL);
```

### 逐行解析

```php
<?php                        // 开始标签：标记 PHP 代码区开始，纯 PHP 文件末尾不要写 ?>
                             // 空行与 declare 之间：declare 必须是文件第一条语句

declare(strict_types=1);     // 开启严格类型模式：函数调用时参数类型不再隐式转换

function greet(string $name): string   // 参数与返回值都显式声明类型
{
    return "Hello, {$name}! 欢迎来到现代 PHP 的世界。";  // 双引号内支持变量插值
}

$name = $argv[1] ?? 'PHP Learner';     // $argv 是 CLI 参数数组；?? 为空合并运算符

echo greet($name), PHP_EOL;  // echo 可一次输出多个表达式，PHP_EOL 跨平台换行
```

**关键概念**：

- **`<?php` 开始标签**：PHP 是嵌入式语言，解析器只处理标签内的代码；纯 PHP 文件按 PSR-12 规范应省略结束标签 `?>`，避免意外输出空白字符破坏 HTTP 头
- **`declare(strict_types=1)`**：现代 PHP 项目标配。开启后 `greet(123)` 会抛出 `TypeError`，而不是静默把 `123` 转成 `"123"`——错误尽早暴露
- **`$argv`**：仅 CLI 模式可用的超全局变量，`$argv[0]` 是脚本名，`$argv[1]` 起才是真实参数

### 可复现验收：严格类型与默认 CLI 输入

下面的案例不依赖 PHP 小版本字符串，也不启动 HTTP 服务。它只验证本节的两个语言契约：未传参数时使用默认值；严格类型下把整数传给 `string` 参数会抛出 `TypeError`。真实脚本仍应通过 `php hello.php Ada` 读取终端参数；这个固定案例用于确认你理解了函数边界。

<!-- reference-case: {"id":"php-first-script-cli-contract","stdout":"PHP Learner\nAda\nstrict-type-error\n"} -->
```php
<?php

declare(strict_types=1);

function greet(string $name): string
{
    return $name;
}

function nameFromArgs(array $args): string
{
    return $args[1] ?? 'PHP Learner';
}

echo greet(nameFromArgs(['hello.php'])), PHP_EOL;
echo greet(nameFromArgs(['hello.php', 'Ada'])), PHP_EOL;

try {
    greet(42);
} catch (TypeError) {
    echo "strict-type-error", PHP_EOL;
}
```

预期输出：

```text
PHP Learner
Ada
strict-type-error
```

## 2. 运行方式一：CLI（命令行）

```bash
php hello.php                # 输出: Hello, PHP Learner! ...
php hello.php World          # 输出: Hello, World! ...
```

也可以不落盘直接执行一段代码：

```bash
php -r 'echo PHP_VERSION, PHP_EOL;'    # -r：运行一行代码
php -a                                 # 进入交互式 Shell（REPL），exit 退出
```

**CLI 模式的典型用途**：定时任务（crontab）、队列消费者、一次性脚本、安装器（如 `composer` 本身就是 PHP CLI 程序）。

## 3. 运行方式二：Web（内置服务器）

PHP 自带一个开发用 Web 服务器，无需安装 Nginx/Apache 即可体验 Web 模式。

创建 `web/index.php`：

```php
<?php

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// 一个极简路由演示
$response = match ($path) {
    '/'        => ['message' => '欢迎使用 PHP 内置服务器'],
    '/time'    => ['server_time' => date('c')],
    default    => ['error' => '未找到路径: ' . $path],
};

echo json_encode($response, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), PHP_EOL;
```

启动服务：

```bash
php -S localhost:8080 -t web/
# -S 指定监听地址，-t 指定文档根目录
```

在浏览器（或 curl）访问：

```bash
curl http://localhost:8080/
curl http://localhost:8080/time
```

> ⚠️ **注意**：内置服务器是**单线程、仅限开发**的，不要用于生产环境。生产部署使用 Nginx + PHP-FPM 或容器化方案。

### 两种模式对比

| 维度 | CLI 模式 | Web 模式 |
|------|---------|---------|
| 入口 | `php script.php` | HTTP 请求命中 `index.php` |
| 参数来源 | `$argv` | `$_GET` / `$_POST` / `$_SERVER` 等 |
| 超时 | 默认无 `max_execution_time` 限制 | 默认 30 秒 |
| 生命周期 | 脚本结束进程退出 | 每次请求独立执行 |
| 典型场景 | 定时任务、队列、工具 | 网站、API 服务 |

## 4. 现代脚本的标配写法

一个面向 8.5 的脚本文件通常包含以下要素，后续文档都会沿用：

```php
<?php

declare(strict_types=1);

// 1. 严格类型（永远开启）
// 2. 显式类型签名（参数 + 返回值）
// 3. 命名空间（复杂项目）/ PSR-4 自动加载（见 08-first-project）
// 4. 异常而非静默失败（见 06-error-exceptions）

function divide(int $a, int $b): float
{
    if ($b === 0) {
        throw new InvalidArgumentException('除数不能为零');
    }

    return $a / $b;
}
```

类型系统的完整说明见 [`../reference/language-concepts/03-types-oop-modern.md`](../reference/language-concepts/03-types-oop-modern.md)。

## ✅ 最佳实践

把脚本入口与可复用函数分开，成功返回 0，失败返回明确非零退出码，方便终端脚本判断是否继续。输出协议规定换行时遵循协议，PHP_EOL 用于本地文本方便；不能声称 Windows 普遍无法显示 Unix 换行。

Web 响应的 header 必须在实际输出前发送，BOM 或意外空白也可能提前产生输出。纯 PHP 文件省略结束标签可减少末尾误输出。strict_types 影响特定标量类型转换规则，不会把所有外部输入自动验证成业务合法数据。

## ❓ 常见问题

### Q1: 浏览器访问显示的是源码而不是执行结果？
**A**: 说明请求没有经过 PHP 处理。确认用 `php -S` 启动了服务器，且 URL 端口、目录正确。

### Q2: `Undefined array key 1` 报错？
**A**: `$argv[1]` 不存在（未传参数）。这是严格模式下的常见 Notice，用 `$argv[1] ?? '默认值'` 防御。

### Q3: 修改代码后输出没变化？
**A**: CLI 脚本每次执行都是新进程，检查是否编辑了另一个路径的文件；Web 模式下注意 opcache，开发环境建议关闭。

## 🎯 练习与实践

### 基础练习
- [ ] 让 `hello.php` 接受两个参数（名字和年龄）并格式化输出
- [ ] 用 `php -a` 交互式模式实验字符串插值 `"{$name}今年{$age}岁"`
- [ ] 给内置服务器程序新增 `/random` 路由，返回随机数 JSON

### 进阶挑战
- [ ] 写一个 CLI 脚本 `sum.php`，接受不定数量的数字参数并求和（提示：`array_sum`、`array_slice($argv, 1)`）
- [ ] 用 `php -S` 启动服务，编写返回 404 状态码的路由分支（`http_response_code(404)`）

---

## 🔗 相关文档

- 📄 **[变量与类型](./03-variables-types.md)** — 下一节：深入严格类型与类型系统
- 📄 **[控制结构全表](../reference/language-concepts/04-control-flow.md)** — `match` 表达式的权威条目
- 📄 **[常见错误排查](../reference/quick-references/02-troubleshooting.md)** — 运行报错速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
