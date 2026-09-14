# 日期时间

## 概述

PHP 日期时间围绕 `DateTime`/`DateTimeImmutable` 两个类与 `DateInterval`/`DatePeriod`/`DateTimeZone` 辅助类展开。核心纪律只有一条：**业务代码用 Immutable**。属语言稳定层（DateTimeImmutable 5.5+）。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#日期` `#时间` `#DateTime` `#时区` |
| **更新日期** | `2026年9月` |

## 条目 1：DateTime vs DateTimeImmutable

📌 **定义**: `DateTime` 是可变对象——`modify/add/sub` **原地修改**自身并返回 `$this`；`DateTimeImmutable` 的同名方法返回**新对象**。链式写法下两者行为天差地别。

📖 **语法/签名**:

```php
new DateTime(string $datetime = "now", ?DateTimeZone $tz = null)
new DateTimeImmutable(string $datetime = "now", ?DateTimeZone $tz = null)
modify(string $modifier): static        // mutable 改自身 / immutable 返回副本
add/sub(DateInterval $i): static        // 同上
setDate/setTime/setTimezone(...): static
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

// ❌ Mutable：链式看着对，实际 $start 被一起改了
$start = new DateTime('2026-09-11 09:00:00');
$end = $start->modify('+1 hour');       // $start 也变成了 10:00！

// ✅ Immutable：修改即新对象
$start = new DateTimeImmutable('2026-09-11 09:00:00');
$end = $start->modify('+1 hour');       // $start 仍是 09:00，$end 是 10:00

echo $start->format('H:i'), ' ~ ', $end->format('H:i'), PHP_EOL;   // 09:00 ~ 10:00
```

⚠️ **常见陷阱**: Mutable 的链式调用是 bug 温床（每次 `modify` 都在改同一个对象）；工具函数签名应声明 `DateTimeImmutable` 参数，逼调用方给不可变值。

🔗 **相关条目**: [DateInterval 与 DatePeriod](#条目-3dateinterval-与-dateperiod)

## 条目 2：format 与 createFromFormat

📌 **定义**: `format()` 用格式符输出；`createFromFormat()` 按"给定格式"解析字符串——是解析非 ISO 格式日期的唯一正确姿势。

📖 **语法/签名**:

```php
$dt->format(string $format): string
DateTime::createFromFormat(string $format, string $datetime, ?DateTimeZone $tz = null): DateTime|false
DateTimeImmutable::createFromFormat(...): DateTimeImmutable|false
DateTime::createFromImmutable(DateTimeImmutable $dt): DateTime
```

高频格式符：`Y` 四位年、`m/d` 月日、`H:i:s` 时分秒、`U` Unix 时间戳、`c` ISO8601、`N` 星期（1=周一）。

💡 **示例**:

```php
<?php

declare(strict_types=1);

$dt = new DateTimeImmutable('2026-09-11 14:30:00');
echo $dt->format('Y-m-d H:i:s'), PHP_EOL;    // 2026-09-11 14:30:00
echo $dt->format('U'), PHP_EOL;              // 时间戳
echo $dt->format('l'), PHP_EOL;              // Friday（英文星期名）

// 解析"11/09/2026"这类自定义格式——new DateTime() 会按美式月日误判！
$dt2 = DateTimeImmutable::createFromFormat('d/m/Y', '11/09/2026');
if ($dt2 === false) {
    print_r(DateTime::getLastErrors());      // 解析错误/警告明细
}
echo $dt2->format('Y-m-d'), PHP_EOL;         // 2026-09-11
```

⚠️ **常见陷阱**: `new DateTime('11/09/2026')` 按美式解析成 11 月 9 日——非 ISO 格式必须 `createFromFormat`；`createFromFormat` 失败返回 `false`，且可能有残留警告（如"多出的字符"），关键路径要检查 `getLastErrors()`。

🔗 **相关条目**: [DateTime vs DateTimeImmutable](#条目-1datetime-vs-datetimeimmutable)

## 条目 3：DateInterval 与 DatePeriod

📌 **定义**: `DateInterval` 表达"一段时长"（`P` 日期部分 + `T` 时间部分的 ISO8601 记法）；`DatePeriod` 按起止与间隔枚举出一个日期序列（本身就是迭代器）；`diff()` 返回 `DateInterval`。

📖 **语法/签名**:

```php
new DateInterval(string $duration)          // ISO8601：P1Y2M3DT4H5M6S
new DatePeriod(DateTimeInterface $start, DateInterval $interval, int|DateTimeInterface $end, int $options = 0)
$dt->diff(DateTimeInterface $target, bool $absolute = false): DateInterval
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

$start = new DateTimeImmutable('2026-09-01');
$end = new DateTimeImmutable('2026-09-11');

// 每天一格，枚举区间
$period = new DatePeriod($start, new DateInterval('P1D'), $end);
foreach ($period as $day) {
    echo $day->format('m-d'), PHP_EOL;      // 09-01 … 09-10
}

// 间隔计算
$diff = $start->diff($end);
echo $diff->days, ' days', PHP_EOL;         // 10 days
```

⚠️ **常见陷阱**: ISO 串里日期与时间必须用 `T` 分隔（`PT1H` 是 1 小时，`P1H` 非法）；`DatePeriod` 默认**不含**终点（8.2+ 才有 `INCLUDE_END_DATE` 选项）；`$diff->days` 对"不足一天"按 0 计。

🔗 **相关条目**: [DateTime vs DateTimeImmutable](#条目-1datetime-vs-datetimeimmutable)

## 条目 4：时区（DateTimeZone）

📌 **定义**: 每个对象自带时区；存储用 UTC、展示按用户时区是标准做法。`setTimezone` 只换"表达时区"，不换时间点本身。

📖 **语法/签名**:

```php
new DateTimeZone(string $timezone)                       // 'Asia/Shanghai'、'UTC'
$dt->setTimezone(DateTimeZone $tz): static               // 同一时间点的另一时区表达
$dt->getTimezone(): DateTimeZone
date_default_timezone_set(string $tz): bool              // 全局默认（php.ini date.timezone）
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

// 会话开始时刻（同一时间点，两种表达）
$meeting = new DateTimeImmutable('2026-09-11 14:00:00', new DateTimeZone('Asia/Shanghai'));
$utc = $meeting->setTimezone(new DateTimeZone('UTC'));

echo $meeting->format('H:i'), PHP_EOL;   // 14:00
echo $utc->format('H:i'), PHP_EOL;       // 06:00（同一时刻）
echo $utc->format('c'), PHP_EOL;         // 2026-09-11T06:00:00+00:00
```

⚠️ **常见陷阱**: `setTimezone` ≠ 时间平移；改全局默认时区影响所有未显式指定时区的解析，应用入口统一设置而非散落各处；数据库时间列存 UTC（Laravel `app.timezone=UTC`），展示层再转。

🔗 **相关条目**: [Laravel 核心速查](../framework-essentials/01-laravel-essentials.md)

## 条目 5：比较与时间戳

📌 **定义**: 两个 `DateTimeInterface` 可直接用比较运算符（5.2 起内置比较语义）；与 Unix 时间戳互转用 `getTimestamp()`/`'@ts'` 构造。

📖 **语法/签名**:

```php
$a < $b            // DateTimeInterface 直接比较（5.2 起）
$a->getTimestamp(): int
new DateTimeImmutable('@' . time())      // @ 前缀按 UTC 创建
DateTimeImmutable::createFromFormat('U', (string) time())
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

$deadline = new DateTimeImmutable('2026-09-30 23:59:59');
$now = new DateTimeImmutable('now');

if ($now > $deadline) {
    echo '已截止', PHP_EOL;
}

$left = $now->diff($deadline);
printf('还剩 %d 天 %d 小时%s', $left->d, $left->h, PHP_EOL);
```

⚠️ **常见陷阱**: 比较运算符 5.2 起即可用，"对象比较不可靠"的老文章结论早已失效；`time()`/`getTimestamp()` 是秒级，毫秒要用 `microtime(true)` 或 `format('v')`；`'@ts'` 构造的对象时区是 UTC，展示前先 `setTimezone`。

🔗 **相关条目**: [时区](#条目-4时区datetimezone)、[DateInterval 与 DatePeriod](#条目-3dateinterval-与-dateperiod)

## 相关文档

- 📄 **[内置函数总表](./02-built-in-functions.md)** — time()/strtotime() 等过程式函数定位
- 📄 **[变量与类型](../../basics/03-variables-types.md)** — 值对象不可变的语言背景
- 📄 **[缓存策略与队列调优](../../advanced-topics/performance/02-caching-queues.md)** — TTL 计算的工程应用

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
