# 命名空间与自动加载

## 概述

命名空间把代码组织成可寻址的"路径"，自动加载把"类名 → 文件"的映射交给约定（PSR-4）与 Composer。两者合起来是现代 PHP 工程的地基，属语言稳定层（namespace 5.3+、PSR-4 通行至今）。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#命名空间` `#PSR-4` `#自动加载` `#Composer` |
| **更新日期** | `2026年9月` |

## 条目 1：namespace 声明与完全限定名

📌 **定义**: `namespace` 为该文件内的类/接口/函数/常量声明所属空间；完全限定名（FQCN）形如 `App\Service\Invoice`，对应 PSR-4 下的文件路径 `App/Service/Invoice.php`。

📖 **语法/签名**:

```php
<?php

declare(strict_types=1);

namespace App\Service;          // 必须是文件第一条（declare 之后）语句
```

💡 **示例**:

```php
namespace App\Service;

use App\Model\Order;

final class Invoice
{
    public function for(Order $order): string
    {
        return "INV-{$order->id}";
    }
}

// 其他文件中引用：
$invoice = new \App\Service\Invoice();   // 完全限定名（带根 \）
```

⚠️ **常见陷阱**: 一个文件原则上一个命名空间一个类（PSR-4 硬约定）；命名空间没有"继承"——每个文件都要自己写 `use`。

🔗 **相关条目**: [use 与别名](#条目-2use-与别名)

## 条目 2：use 与别名

📌 **定义**: `use` 在编译期建立"短名 → FQCN"的别名映射，只影响命名引用，不触发加载、不改变运行时行为。

📖 **语法/签名**:

```php
use App\Service\Invoice;                    // 类别名
use App\Service\Invoice as Contract;        // 显式别名
use function App\helpers\json_dump;         // 函数（7.0+）
use const App\MAX_RETRY;                    // 常量（7.0+）
use App\{Invoice, Order, Model\User};       // 分组 use（7.0+）
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

namespace App\Http;

use App\{Service\Invoice, Model\Order};     // 分组写法
use Illuminate\Support\Str as StrHelper;

final class OrderResponse
{
    public function render(Invoice $invoice, Order $order): string
    {
        return StrHelper::slug($invoice->for($order));
    }
}
```

⚠️ **常见陷阱**: `use App\Service\Invoice` 写的是**类名**而非文件路径；同文件两个同名类必须别名区分；`use` 引入的是编译期别名，动态 `new $class` 传的是字符串、不吃别名——动态场景写 FQCN。

🔗 **相关条目**: [命名空间声明](#条目-1namespace-声明与完全限定名)

## 条目 3：PSR-4 与 Composer 自动加载

📌 **定义**: PSR-4 约定"FQCN 前缀 ↔ 目录"的映射：`App\` → `app/`，则 `App\Service\Invoice` 自动映射到 `app/Service/Invoice.php`（逐段对应、大小写敏感）。Composer 是 PSR-4 的标准执行者。

📖 **语法/签名**:

```json
{
    "autoload": {
        "psr-4": {
            "App\\": "app/",
            "DevQuest\\": "src/DevQuest/"
        },
        "files": ["src/helpers.php"],
        "classmap": ["legacy/"]
    },
    "autoload-dev": {
        "psr-4": { "Tests\\": "tests/" }
    }
}
```

💡 **示例**:

```bash
composer dump-autoload        # 修改 autoload 配置或新增 classmap 后必须执行
composer dump-autoload -o     # 生成优化的类映射（生产常用）
```

```php
// 之后任意文件（入口加载 vendor/autoload.php 后）
require __DIR__ . '/vendor/autoload.php';

$invoice = new App\Service\Invoice();   // Composer 按映射找到 app/Service/Invoice.php
```

⚠️ **常见陷阱**: 新建类后报 "class not found"，九成是命名空间与目录/前缀不一致，其次才是忘了 `dump-autoload`；`files` 里的函数文件不走 PSR-4，每次加载无条件执行。

🔗 **相关条目**: [spl_autoload_register](#条目-4spl_autoload_register-与加载原理)、[Composer 生态](../library-guides/02-composer-ecosystem.md)

## 条目 4：spl_autoload_register 与加载原理

📌 **定义**: 自动加载是"用到未定义类时按注册顺序尝试加载"的懒加载钩子。Composer 本质上就是注册了一串 SPL autoloader；理解它才能排查加载故障。

📖 **语法/签名**: `spl_autoload_register(?callable $loader, bool $throw = true, bool $prepend = false): bool`——loader 接收类名，加载成功即可，无需返回值。

💡 **示例**:

```php
<?php

declare(strict_types=1);

spl_autoload_register(function (string $class): void {
    $prefix = 'DevQuest\\';
    if (! str_starts_with($class, $prefix)) {
        return;                                  // 不是本前缀，交给下一个 loader
    }
    $relative = substr($class, strlen($prefix));
    $file = __DIR__ . '/src/' . str_replace('\\', '/', $relative) . '.php';
    if (is_file($file)) {
        require $file;                          // 手写一个微型 PSR-4 loader
    }
});

new DevQuest\Core\Kernel();     // 首次使用时才触发加载
```

⚠️ **常见陷阱**: loader 里抛异常会中断整个加载链；`require` 找不到文件时不要 `exit`，应静默返回让后续 loader 接手。

🔗 **相关条目**: [PSR-4 与 Composer 自动加载](#条目-3psr-4-与-composer-自动加载)

## 条目 5：全局回退与名称解析规则

📌 **定义**: 命名空间内的**函数与常量**遵循"先看当前命名空间、再回退全局"的解析规则；**类名没有回退**——命名空间内写 `strlen()` 能用（函数回退），但写 `new Exception` 实际解析为 `\当前命名空间\Exception`，必须 `\Exception` 或 use。

📖 **语法/签名**:

```php
namespace App\Service;

// 函数：当前空间没有 foo() 时自动回退全局
foo();

// 类：无回退，必须显式
throw new \RuntimeException('x');   // ✅ 全局根
// throw new RuntimeException('x'); // ❌ 解析为 App\Service\RuntimeException
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

namespace App\Service;

use RuntimeException;                 // 惯用做法：use 全局类

final class Validator
{
    public function check(int $v): void
    {
        if ($v <= 0) {
            throw new RuntimeException('must be positive');   // 现在短名可用
        }
        echo strlen('abc'), PHP_EOL;  // 函数回退到全局 strlen
    }
}
```

⚠️ **常见陷阱**: "类不回退、函数与常量回退"是面试与 bug 双高发点；写 `new ArrayObject(...)` 报 not found 时，先想到是缺 `use ArrayObject;` 或根反斜杠。

🔗 **相关条目**: [use 与别名](#条目-2use-与别名)、[内置函数](./02-built-in-functions.md)

## 相关文档

- 📄 **[Composer 生态精选](../library-guides/02-composer-ecosystem.md)** — autoload 配置的工程化细节
- 📄 **[SPL 标准库](../library-guides/01-standard-library-spl.md)** — ArrayIterator 等迭代器生态
- 📄 **[环境搭建](../../basics/01-environment-setup.md)** — Composer 安装与第一份 composer.json

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
