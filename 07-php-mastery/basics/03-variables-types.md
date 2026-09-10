# 变量与类型系统 - 从动态到严格类型

> **文档简介**: 掌握 PHP 变量的作用域规则、八大数据类型，以及严格类型声明下的类型系统（联合类型、可空类型等）
>
> **目标读者**: 已能运行 PHP 脚本、希望理解 PHP 类型体系的初学者
>
> **前置知识**: 完成 [第一个 PHP 脚本](./02-first-script.md)，理解 `declare(strict_types=1)`

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#变量` `#类型系统` `#严格类型` `#联合类型` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 正确声明变量与常量，理解作用域差异
- ✅ 识别 PHP 的全部标量与复合类型
- ✅ 编写带类型声明的函数并解释严格模式与弱模式的行为差异
- ✅ 使用联合类型、可空类型表达更精确的签名

## 1. 变量：声明与作用域

PHP 变量以 `$` 开头，**无需（也不能）在声明时指定类型**——类型由赋的值决定，但在函数签名处可以显式约束。

```php
<?php

declare(strict_types=1);

$name = 'Ada';          // string
$age = 36;              // int
$score = 99.5;          // float
$active = true;         // bool
$tags = ['dev', 'php']; // array
$nullable = null;       // null
```

**命名规则**：`$` 后必须是字母或下划线，区分大小写；不可使用保留字。

### 作用域三规则

```php
<?php

declare(strict_types=1);

$global = '全局可见';               // 1. 全局作用域

function demo(): void
{
    // echo $global;               // ❌ 函数内部默认看不到全局变量
    $local = '仅函数内可见';        // 2. 函数作用域

    static $counter = 0;           // 3. 静态变量：函数多次调用间保留
    $counter++;
    echo $counter, PHP_EOL;
}

demo();  // 1
demo();  // 2
demo();  // 3

// 4. 超全局变量（$_GET/$_POST/$_SERVER/$_SESSION 等）在任何作用域都可直接访问
echo PHP_EOL . PHP_VERSION . PHP_EOL;   // 常量同理，全局可用
```

> 💡 函数内如需访问全局变量，**首选通过参数传入**，其次 `global` 关键字；依赖全局状态是测试性差的根源。

## 2. 常量与类常量

```php
<?php

declare(strict_types=1);

// 全局常量：define() 可在运行时任意处定义；const 必须在编译期（文件顶层/类内）
define('APP_NAME', 'DevQuest');
const APP_VERSION = '1.0.0';

echo APP_NAME, ' ', APP_VERSION, PHP_EOL;

// 类常量：PHP 8.3+ 支持 const 类型化 + 动态获取
class Config
{
    public const int MAX_RETRY = 3;
    final public const string VERSION = '2.0';   // 类型化常量（8.3+）、final 阻止覆盖（8.1+）
}

echo Config::MAX_RETRY, PHP_EOL;
echo Config::{'VERSION'}, PHP_EOL;        // PHP 8.3 新语法：动态获取常量
```

**`const` vs `define()`**：类内只能用 `const`；`define()` 仅适合条件定义等运行时场景。现代代码统一用 `const`。

## 3. 类型全景

PHP 10 种基础类型分三类：

| 分类 | 类型 | 说明 |
|------|------|------|
| 标量 | `int` `float` `string` `bool` | 四大标量，日常主力 |
| 复合 | `array` `object` `callable` `iterable` | 数组、对象、可调用、可迭代 |
| 特殊 | `null` `mixed` | 空值与"任意类型"（8.0+） |

```php
<?php

declare(strict_types=1);

// 类型检测函数
var_dump(is_int(1), is_string('a'), is_array([]));

// 类型转换（显式）
$sum = (int) '42';          // 42
$price = (float) '19.9';    // 19.9
$text = (string) 100;       // '100'

// 弱比较 vs 严格比较 —— 面试与 bug 高发区
var_dump(0 == 'a');          // PHP 8 起为 false（8.0 改变了字符串转数字规则）
var_dump(0 === 'a');         // false，恒为 false
var_dump('10' == '1e1');     // false（8.0 起）：字符串间 == 也要数字格式匹配
var_dump('10' === '10');     // true
```

> ⚠️ **PHP 8 变化**：`0 == 'foo'` 在 PHP 7 为 `true`（字符串转数字得 0），8.0 起比较字符串与数字时把字符串转为数字的规则更严格，返回 `false`。旧代码升级时这里是重灾区。

## 4. 类型声明：函数签名的精确表达

```php
<?php

declare(strict_types=1);

// 基本参数与返回值类型
function add(int $a, int $b): int
{
    return $a + $b;
}

// 可空类型：?T 等价于 T|null
function findUser(?int $id): ?string
{
    return $id === null ? null : "user-{$id}";
}

// 联合类型（PHP 8.0+）：多种类型之一
function normalize(int|float|string $value): float
{
    return (float) $value;
}

// 交叉类型（PHP 8.1+）：必须同时满足多个类型/接口
function process(Countable&Stringable $item): string
{
    return 'count=' . count($item) . ', text=' . $item;
}

// 默认值：默认 null 时类型自动涵盖 null
function greet(string $name = 'stranger'): string
{
    return "Hi, {$name}";
}
```

**严格模式 vs 弱模式的行为差异**：

```php
// 文件未声明 strict_types（弱模式）
function len(string $s): int { return strlen($s); }
len(123);        // ✅ 隐式转换成 '123'，返回 3

// 文件声明 declare(strict_types=1)（严格模式）
len(123);        // ❌ TypeError: 必须是 string，给定了 int
```

注意：`strict_types` 影响**该文件中发起的函数调用**，而非函数定义所在文件。

## 5. 类型推断与静态分析

PHP 本身在运行时弱类型检查，但配合 **PHPStan / Psalm** 可以获得编译期级别的类型安全：

```php
<?php

declare(strict_types=1);

/** @param array<string, int> $scores  键为姓名、值为分数的映射 */
function average(array $scores): float
{
    /** @var int|float $sum */
    $sum = array_sum($scores);
    return $sum / max(count($scores), 1);
}
```

- `array<string, int>` 这类泛型注解写在 DocBlock 中，PHPStan 直接消费
- 现代 PHP 的工程实践 = 运行时类型声明 + 静态分析双保险（详见 [`../reference/library-guides/02-composer-ecosystem.md`](../reference/library-guides/02-composer-ecosystem.md)）

## ✅ 最佳实践

- ✅ **所有生产代码开启 `strict_types=1` 并写全类型签名**：让错误在调用点立刻暴露
- ✅ **恒等比较 `===` / `!==`**：仅在明确需要弱比较时用 `==`，并注释原因
- ✅ **优先窄化类型**：能写 `int|float` 就不写 `mixed`，能写 `?string` 就不写更宽的联合
- ❌ **不要滥用 `mixed`**：它是"放弃类型检查"的信号，应尽量限定到具体联合类型
- ❌ **不要用可变变量 `$$name`**：静态分析与 IDE 均无法追踪，改用数组映射

## ❓ 常见问题

### Q1: `int` 和 `float` 能互相隐式转换吗？
**A**: 严格模式下传 `int` 给 `float` 参数是允许的（无损转换），反过来传 `float` 给 `int` 参数会报 `TypeError`。

### Q2: `iterable` 和 `array` 有什么区别？
**A**: `iterable = array|Traversable`，函数签名写 `iterable` 表示"接受数组或任何可迭代对象"，是更宽的接口承诺。

### Q3: 为什么 `$undefined` 不报错却输出 `null`？
**A**: 读未定义变量产生 `Warning` 并返回 `null`；严格类型不改变这一行为。开发环境应配置 `error_reporting=E_ALL` 让问题显形。

## 🎯 练习与实践

### 基础练习
- [ ] 写函数 `clamp(int|float $v, int|float $min, int|float $max): int|float`，把值约束到区间内
- [ ] 验证严格模式下 `strlen(123)` 抛出 `TypeError`，移除 `strict_types` 后对比
- [ ] 用 `static` 变量实现一个调用计数器，统计某函数被执行的次数

### 进阶挑战
- [ ] 安装 PHPStan（`composer require --dev phpstan/phpstan`），对练习代码运行 `vendor/bin/phpstan analyse`，消除全部报错
- [ ] 编写同时接受 `Countable&Stringable` 的函数，并实现一个满足交叉类型的类

---

## 🔗 相关文档

- 📄 **[函数与面向对象](./04-functions-oop.md)** — 下一节：构造器属性提升等现代 OOP
- 📄 **[类型系统与现代 OOP 全表](../reference/language-concepts/03-types-oop-modern.md)** — 联合/交叉/DNF 类型权威条目
- 📄 **[关键字详解](../reference/language-concepts/01-php-keywords.md)** — `const`/`static`/`global` 的精确定义
