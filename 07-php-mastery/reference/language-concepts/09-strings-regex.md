# 字符串与正则

## 概述

字符串处理是 PHP 的看家本领：多字节安全交给 `mb_*` 族，现代判断函数（8.0+ `str_contains` 等）取代 strpos 比较，复杂模式匹配交给 PCRE（`preg_*`）。本文收录日常最高频条目，属语言稳定层。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#字符串` `#多字节` `#正则` `#PCRE` |
| **更新日期** | `2026年9月` |

## 条目 1：多字节字符串（mb_* 族）

📌 **定义**: UTF-8 下一个字符可占多字节，`strlen`/`substr` 等按**字节**计算；`mb_*` 族按**字符**计算。凡涉及用户可见文本的长度与截断，一律用 mb 系列。

📖 **语法/签名**:

```php
mb_strlen(string $s, ?string $encoding = null): int
mb_substr(string $s, int $start, ?int $length = null, ?string $encoding = null): string
mb_strtolower/mb_strtoupper(string $s, ?string $encoding = null): string
mb_convert_encoding(string $s, string $to, array|string|null $from = null): string
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

$title = 'PHP 中文手册';
echo strlen($title), PHP_EOL;        // 按 UTF-8 字节计（每汉字 3 字节）
echo mb_strlen($title), PHP_EOL;     // 8（字符）

echo mb_substr($title, 0, 3), PHP_EOL;    // PHP
echo mb_substr($title, 4, 2), PHP_EOL;    // 中文
```

⚠️ **常见陷阱**: `substr()` 截 UTF-8 会得到乱码半字符；表单"最多 20 字"校验用 `mb_strlen` 而非 `strlen`；数据库 varchar 长度按字符，与字节不一致。

🔗 **相关条目**: [现代字符串判断函数](#条目-2现代字符串判断函数8-0)

## 条目 2：现代字符串判断函数（8.0+）

📌 **定义**: `str_contains`/`str_starts_with`/`str_ends_with` 取代 `strpos(...) !== false` 这类绕口写法，语义直白且空串行为明确。

📖 **语法/签名**:

```php
str_contains(string $haystack, string $needle): bool
str_starts_with(string $haystack, string $needle): bool
str_ends_with(string $haystack, string $needle): bool
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

$path = '/api/v1/orders';

str_starts_with($path, '/api');       // true
str_ends_with($path, 'orders');       // true
str_contains($path, 'v1');            // true

// 对照旧写法（不要再写）：
// strpos($path, '/api') === 0
// strpos($path, 'v1') !== false
```

⚠️ **常见陷阱**: 三个函数都区分大小写；空 `$needle` 恒为 `true`（与 strpos 的 0 位置语义对齐）——别把它当"非空判断"。

🔗 **相关条目**: [多字节字符串](#条目-1多字节字符串mb_-族)

## 条目 3：sprintf 与格式化

📌 **定义**: `sprintf`/`printf` 用占位符拼装字符串，是日志、模板、固定宽度输出的标准工具；`number_format` 专管千分位与精度。

📖 **语法/签名**: `sprintf(string $format, mixed ...$values): string`——`%s` 字符串、`%d` 整数、`%.2f` 两位小数、`%05d` 补零、`%%` 字面百分号。

💡 **示例**:

```php
<?php

declare(strict_types=1);

sprintf('%s 下单 %d 件，合计 %.2f 元', 'Ada', 3, 199.5);   // Ada 下单 3 件，合计 199.50 元
sprintf('%05d', 42);                                       // 00042
sprintf('%s%%', 99.5);                                     // 99.5%

number_format(1234567.891, 2, '.', ',');                   // 1,234,567.89
```

⚠️ **常见陷阱**: 占位符个数与实参不匹配会抛 `ArgumentCountError`（8.0+ 行为趋严）；金额展示用 `number_format`，金额计算永远用整数分或 bcmath。

🔗 **相关条目**: [内置函数总表](./02-built-in-functions.md)

## 条目 4：PCRE 正则（preg_* 族）

📌 **定义**: PHP 正则以 `preg_*`（PCRE 库）为准：模式是"定界符 + 表达式 + 修饰符"的字符串，如 `/^\d+$/u`。

📖 **语法/签名**:

```php
preg_match(string $pattern, string $subject, array &$matches = [], int $flags = 0, int $offset = 0): int|false
preg_match_all(...): int|false
preg_replace(string|array $pattern, string|array $replacement, string|array $subject, int $limit = -1): string|array|null
preg_replace_callback(string $pattern, callable $callback, string|array $subject): string|array|null
preg_split(string $pattern, string $subject, int $limit = -1, int $flags = 0): array|false
preg_quote(string $str, ?string $delimiter = null): string
```

常用修饰符：`i` 忽略大小写、`m` 多行、`s` 点号匹配换行、`u` UTF-8 模式（处理中文必加）、`x` 忽略空白与注释。

💡 **示例**:

```php
<?php

declare(strict_types=1);

// 提取 + 命名分组
preg_match('/^(?<user>[\w.]+)@(?<domain>[\w-]+)$/', 'ada@example.com', $m);
echo $m['user'], PHP_EOL;      // ada
echo $m['domain'], PHP_EOL;    // example.com

// 回调式替换：把 {name} 占位符替换为数组值
$values = ['name' => 'Grace'];
$text = preg_replace_callback(
    '/\{(\w+)\}/',
    fn (array $m): string => $values[$m[1]] ?? $m[0],
    'Hello, {name}!',
);
echo $text, PHP_EOL;           // Hello, Grace!

// 中文字符类必须带 u 修饰符
var_dump((bool) preg_match('/^[\p{Han}]+$/u', '手机验证码'));   // true
```

⚠️ **常见陷阱**: 忘写 `u` 修饰符时中文按字节匹配，行为诡异；模式由用户输入拼出时必须 `preg_quote()`（并传定界符参数），否则注入正则；`preg_replace` 返回 `null` 表示出错（如回溯上限），不是"替换为零处"——重要路径要检查 `preg_last_error()`。

🔗 **相关条目**: [字符串类问题排查](../quick-references/02-troubleshooting.md)

## 条目 5：拆分与拼接

📌 **定义**: 简单分隔用 `explode`/`implode`；需要"多种分隔符/复杂规则"才升级到 `preg_split`；`trim` 族处理两端字符。

📖 **语法/签名**:

```php
explode(string $separator, string $string, int $limit = PHP_INT_MAX): array
implode(string $glue, array $array): string
ltrim/rtrim/trim(string $s, string $characters = " \n\r\t\v\0"): string
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

[$user, $host] = explode('@', 'ada@example.com');
echo implode('-', ['php', 'diataxis']), PHP_EOL;      // php-diataxis

// 多种分隔符：中英文逗号都拆
print_r(preg_split('/[,，]/u', 'a,b，c'));             // ['a','b','c']

echo trim('  hello  '), PHP_EOL;                       // hello
echo trim('xxhelloxx', 'x'), PHP_EOL;                  // hello
```

⚠️ **常见陷阱**: `explode` 分隔符传空串直接抛 `ValueError`；`implode` 参数顺序写统一为 `(glue, array)`，避免历史双写法误导阅读。

🔗 **相关条目**: [数组操作模式](./05-arrays-patterns.md)、[PCRE 正则](#条目-4pcre-正则preg_-族)

## 相关文档

- 📄 **[内置函数总表](./02-built-in-functions.md)** — 全景函数分类
- 📄 **[快速速查表](../quick-references/01-php-cheatsheet.md)** — 一行式字符串操作
- 📄 **[变量与类型](../../basics/03-variables-types.md)** — 字符串基础语法

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
