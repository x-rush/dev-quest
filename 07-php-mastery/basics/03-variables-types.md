# 变量与类型系统 - 从动态到严格类型

## 先理解，再动手

变量可以绑定不同类型，但函数契约仍会约束输入。strict_types 影响特定调用边界的标量转换，不等于全语言禁止所有转换。

**本节自测**：比较 0、false、空串的 == 与 ===，再对输入字符串显式转换。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

严格比较检查类型和值；判断查找结果时不要把下标 0 当作未找到。

</details>

> **文档简介**: 掌握 PHP 变量作用域，区分值的运行时类型与类型声明，并理解联合类型、可空类型及严格调用边界。
>
> **目标读者**: 已能运行 PHP 脚本、希望理解 PHP 类型体系的初学者
>
> **前置知识**: 完成 [第一个 PHP 脚本](./02-first-script.md)，理解 `declare(strict_types=1)`

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#变量` `#类型系统` `#严格类型` `#联合类型` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 正确声明变量与常量，理解作用域差异
- ✅ 识别 PHP 的全部标量与复合类型
- ✅ 编写带类型声明的函数并解释严格模式与弱模式的行为差异
- ✅ 使用联合类型、可空类型表达更精确的签名

## 1. 变量：声明与作用域

普通局部变量以 `$` 开头，赋值时不写类型声明；变量以后可以绑定其他类型的值。函数参数、返回值以及类属性可以有类型声明。不要把局部变量规则套到 `public int $age` 这样的属性声明上。

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

**命名规则**：常用 ASCII 写法以字母或下划线开头，后续可含数字，区分大小写。PHP 也接受某些非 ASCII 字节作为变量名字符，但团队通常采用易读的 ASCII 名称。变量名可以与关键字相同，例如 `$class` 合法；特殊变量 `$this` 不能重新赋值。参见 [变量命名规则](https://www.php.net/manual/en/language.variables.basics.php)。

### 作用域与跨调用状态

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

// define() 是函数调用，可在条件分支中执行；此处 const 是顶层常量声明
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

**`const` vs `define()`**：类常量用 `const` 声明；顶层常量名称和值固定时，`const` 直观。需要动态名称或按运行时条件定义全局常量时，使用 `define()`。两者有各自用途，不能仅按新旧选型。

## 3. 类型全景

先区分“值是什么”与“签名允许什么”。日常运行时值包括 `null`、`bool`、`int`、`float`、`string`、`array`、`object`、`resource`；`get_debug_type()` 可帮助观察。签名还提供下列表达能力，不能把它们混成一个“10 种值类型”的列表：

| 分类 | 类型 | 说明 |
|------|------|------|
| 标量 | `int` `float` `string` `bool` | 四大标量，日常主力 |
| 容器与对象 | `array` `object`、类名和接口名 | 数组、对象及特定对象契约 |
| 特殊值 | `null`、`resource` | 空值；文件句柄等资源。`resource` 不能直接作为类型声明使用 |
| 可调用契约 | `callable` | 允许可调用值；不能用于属性类型 |
| 别名 | `iterable`、`mixed` | 分别代表 `array|Traversable` 与任意 PHP 值 |
| 返回契约 | `void`、`never` | 不返回值；不正常返回（抛异常或终止），不是变量可持有的值 |
| 组合 | `A|B`、`A&B` | 满足任一类型；同时满足多个类/接口类型 |

完整分类及单值类型 `true`/`false` 见 [PHP 类型系统](https://www.php.net/manual/en/language.types.type-system.php)。

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
var_dump('10' == '1e1');     // true：两边均为数值字符串时按数值比较（PHP 8 只改字符串 vs 数字的比较）
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

// 联合类型（PHP 8.0+）：类型检查后仍需校验字符串格式与数值范围
function normalize(int|float|string $value): float
{
    if (is_string($value) && !is_numeric($value)) {
        throw new InvalidArgumentException('需要数值字符串');
    }
    $number = (float) $value;
    if (!is_finite($number)) {
        throw new InvalidArgumentException('需要有限数值');
    }
    return $number;
}

// 交叉类型（PHP 8.1+）：必须同时满足多个类型/接口
function process(Countable&Stringable $item): string
{
    return 'count=' . count($item) . ', text=' . $item;
}

// 默认值仅用于省略参数；允许 null 要明确写 ?string 或 string|null
function greet(string $name = 'stranger'): string
{
    return "Hi, {$name}";
}
```

**严格模式 vs 弱模式的行为差异**：

若定义 `function len(string $s): int { return strlen($s); }`，从弱模式文件调用 `len(123)` 会把整数转换为字符串并返回 3；从严格模式文件调用则抛 `TypeError`。本页后面的两个完整脚本展示如何分别观察它们，仅切换注释不会改变严格模式。

对用户定义函数的标量参数，调用文件决定严格性；返回值的严格性由函数定义文件决定。严格模式仍允许 `int` 传给 `float`，也不会取消显式强制转换或运算符自己的转换规则。内部函数发起的调用另有边界，不能把本规则推广为所有回调都严格。另：`string $name = null` 的隐式可空写法从 PHP 8.4 起弃用，应写 `?string $name = null`。参见 [类型声明与 strict_types](https://www.php.net/manual/en/language.types.declarations.php)。

## 5. 类型推断与静态分析

PHP 在运行时检查声明；PHPStan / Psalm 可在执行前分析更多路径和 DocBlock 契约，但不会自动验证外部 JSON、表单或数据库内容。注解与实际输入仍可能不一致：

```php
<?php

declare(strict_types=1);

/** @param array<string, int> $scores  键为姓名、值为分数的映射 */
function average(array $scores): float
{
    if ($scores === []) {
        throw new InvalidArgumentException('空集合没有本例定义的平均分');
    }
    $sum = array_sum($scores);
    return $sum / count($scores);
}
```

- `array<string, int>` 这类泛型注解写在 DocBlock 中，PHPStan 直接消费
- 现代 PHP 的工程实践 = 运行时类型声明 + 静态分析双保险（详见 [`../reference/library-guides/02-composer-ecosystem.md`](../reference/library-guides/02-composer-ecosystem.md)）

## ✅ 最佳实践

类型声明帮助描述函数接受什么，但外部字符串仍要按业务规则解析。strict_types 不等于全局禁止一切转换；比较时用 === 明确区分值和类型，确实需要转换则显式写出，便于审查。

mixed 可以表达尚未验证的边界输入，随后应通过检查缩小范围，而不是把不确定值一路传给业务。用数组映射动态字段通常比可变变量更容易追踪；练习比较 0、"0"、null 与空串，写出各自业务含义。

## ❓ 常见问题

### Q1: `int` 和 `float` 能互相隐式转换吗？
**A**: 严格模式下允许把 `int` 传给 `float`，但大整数可能丢失精度，不能称为无损转换。反过来把 `float` 传给 `int` 参数会报 `TypeError`。整数标识符和金额不要先转浮点再转回。

### Q2: `iterable` 和 `array` 有什么区别？
**A**: `iterable = array|Traversable`，函数签名写 `iterable` 表示"接受数组或任何可迭代对象"，是更宽的接口承诺。

### Q3: 为什么 `$undefined` 不报错却输出 `null`？
**A**: 读未定义变量产生 `Warning` 并返回 `null`；严格类型不改变这一行为。开发环境应配置 `error_reporting=E_ALL` 让问题显形。

## 完整实验：类型检查、转换与验证是三件事

以下两块各存成一个 PHP 文件，使用 `php 文件名.php` 执行。每块都是完整脚本；检查失败会抛异常。第一块的预期输出是 `strict types: ok`，第二块是 `weak caller: ok`。该实验的运行范围见 [基础类型验证记录](../../shared-resources/tools/document-quality/reports/php-java-types-validation.md)。

<!-- reference-case: {"id":"php-strict-types-boundaries","stdout":"strict types: ok\n"} -->
```php
<?php
declare(strict_types=1);

function check(bool $condition): void {
    if (!$condition) { throw new RuntimeException('检查失败'); }
}
function countBytes(string $value): int { return strlen($value); }
function half(float $value): float { return $value / 2; }
function parseAge(mixed $input): int {
    // 本例只接受不带符号、无前导零的十进制文本，范围 0..150。
    if (!is_string($input) || preg_match('/\A(?:0|[1-9][0-9]{0,2})\z/', $input) !== 1) {
        throw new InvalidArgumentException('年龄格式错误');
    }
    $age = (int) $input;
    if ($age > 150) { throw new InvalidArgumentException('年龄超出范围'); }
    return $age;
}

$class = '合法变量名';
check(is_string($class));
check((int) 'abc' === 0); // 强转成功不代表原输入合法。
check(parseAge('0') === 0 && parseAge('150') === 150);
foreach (['abc', '', '01', '151', '-1', 0, null, []] as $invalid) {
    try { parseAge($invalid); throw new RuntimeException('应拒绝输入'); }
    catch (InvalidArgumentException $expected) {}
}
try { countBytes(123); throw new RuntimeException('应拒绝 int'); }
catch (TypeError $expected) {}
check(half(3) === 1.5); // 严格模式允许 int -> float。
check(0 !== false && 0 !== '' && 0 !== '0');
check(0 == false && 0 == '0' && !(0 == ''));
check(array_search('a', ['a', 'b'], true) === 0);
check(array_search('x', ['a', 'b'], true) === false);
$stream = fopen('php://memory', 'r+');
if ($stream === false) { throw new RuntimeException('无法打开内存流'); }
try { check(is_resource($stream)); } finally { fclose($stream); }
echo "strict types: ok\n";
```

这里 `mixed` 表达尚未验证的外部输入；类型、格式和范围均通过后，业务才接收 `int`。先强转再检查无法区分 `'abc'` 和真正的零。

<!-- reference-case: {"id":"php-weak-call-boundaries","stdout":"weak caller: ok\n"} -->
```php
<?php
// 本文件故意不启用 strict_types，以观察调用方的标量转换。
function countBytes(string $value): int { return strlen($value); }
function check(bool $condition): void {
    if (!$condition) { throw new RuntimeException('检查失败'); }
}
check(countBytes(123) === 3);
// 弱模式也不是任何值都能强转为参数类型。
try { countBytes([]); throw new RuntimeException('应拒绝数组'); }
catch (TypeError $expected) {}
echo "weak caller: ok\n";
```

把第二个脚本加上 `declare(strict_types=1);` 后，第一次调用会抛 `TypeError`。这说明严格性约束调用契约；它没有代替年龄格式等业务校验。

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


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
