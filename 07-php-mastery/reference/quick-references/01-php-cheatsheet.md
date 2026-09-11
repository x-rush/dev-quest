# 现代 PHP 一行式速查

## 概述

面向 PHP 8.5 的单行代码速查表，按场景分组，每行可直接复制使用。供随手翻阅，不做展开讲解。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#速查表` `#一行式` `#语法` `#PHP8.5` |
| **更新日期** | `2026年9月` |

## 1. 文件骨架

```php
<?php declare(strict_types=1);                                   // 纯 PHP 文件第一行标配
namespace App\Service;                                           // PSR-4 命名空间
final class Invoice { public function __construct(private readonly int $cents) {} }   // 不可变值对象
```

## 2. 变量与类型

```php
$n = $input ?? 0;                                        // null 兜底
$s = trim((string) ($_GET['q'] ?? ''));                  // 安全读外部输入
[$a, $b] = explode(',', 'x,y');                          // 解构赋值
['name' => $name, 'age' => $age] = $user;                // 关联解构
$id = is_numeric($raw) ? (int) $raw : throw new DomainException('非法 id');   // throw 表达式
$ok = match(true) { $v > 0 => true, default => false };  // match 表达式
$never = fn(): never => throw new LogicException();      // never 返回类型
$set = fn(int|float $v): int|float => $v;                // 联合类型
$both = function (Countable&Stringable $x): string { return (string) count($x); };   // 交叉类型
$clean = $s |> trim(...) |> strtoupper(...);             // 管道运算符（8.5+，右侧单参 callable）
```

## 3. 数组一行式

```php
$names = array_column($rows, 'name', 'id');              // 抽列并建索引
$active = array_values(array_filter($rows, fn($r) => (bool) ($r['on'] ?? false)));   // 过滤+重索引
$first  = array_find($rows, fn($r) => $r['age'] > 18);   // 首个满足（8.4+）
usort($rows, fn($a, $b) => $b['score'] <=> $a['score']);  // 降序排序（原地）
$unique = array_values(array_unique($list));             // 去重并重索引
$group  = array_reduce($rows, fn($c, $r) => $c + [$r['type'] => ($c[$r['type']] ?? 0) + 1], []);   // 分组计数
$flat   = array_merge(...array_column($nested, 'tags')); // 二维摊平
$flip   = array_flip(array_unique($list));               // 值转键去重
$mapped = array_map(fn($k, $v) => "$k=$v", array_keys($m), $m);    // map 带键
```

## 4. 字符串一行式

```php
$has = str_contains($haystack, $needle);                 // 包含判断（8.0+）
$head = str_starts_with($s, 'http');                     // 前缀
$tail = str_ends_with($file, '.php');                    // 后缀
$slug = strtolower(preg_replace('/[^a-z0-9]+/i', '-', trim($title)));   // 粗略 slug
$json = json_encode($data, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE);
$arr  = json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
$mask = str_repeat('*', max(0, mb_strlen($phone) - 4)) . mb_substr($phone, -4);   // 手机号打码
$csv  = implode(',', array_map(fn($v) => '"' . str_replace('"', '""', $v) . '"', $row));   // CSV 单行
$pad  = str_pad((string) $seq, 6, '0', STR_PAD_LEFT);    // 单号补零
```

## 5. 日期时间一行式

```php
$now = new DateTimeImmutable('now', new DateTimeZone('Asia/Shanghai'));
$due = $now->modify('+7 days')->setTime(23, 59);         // 链式（返回新对象）
$iso = $now->format(DateTimeInterface::ATOM);            // ISO 8601
$days = (new DateTimeImmutable('2026-09-30'))->diff(new DateTimeImmutable('2026-09-01'))->days;
$stamp = strtotime('2026-09-10T08:00:00+08:00');         // 解析为时间戳
```

## 6. 类与对象一行式

```php
enum Level: string { case Low = 'low'; case High = 'high'; }   // Backed 枚举单行
$l = Level::from('high'); $v = $l->value; $k = $l->name;       // 枚举取值
$c = new class { public function hi(): string { return 'hi'; } };   // 匿名类
$p = new Point(x: 1, y: 2);                              // 命名参数构造
$copy = clone($point, ['x' => 9]);                       // 克隆并覆盖属性（8.5+，RFC clone_with_v2）
$u = new Uri\WhatWg\Url('https://php.net/docs');         // WHATWG URI（8.5+，构造即校验）
$is = $obj instanceof $class;                            // 动态 instanceof
$name = $obj::class;                                     // 运行时类名（8.0+）
```

## 7. 调试与诊断一行式

```php
var_dump($mixed);                                        // 类型+值，调试首选
$dump = print_r($array, true);                           // 返回字符串不打印
error_log(print_r($ctx, true));                          // 写错误日志
printf('%s = %.2f (%d items)%s', $k, $v, $n, PHP_EOL);   // 格式化输出
dd(get_class($obj));                                     // Laravel 调试（框架内）
var_dump(debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 3));  // 调用链前 3 层
```

## 8. 文件与 HTTP 一行式

```php
$ok = file_put_contents($path, $json, LOCK_EX) !== false;   // LOCK_EX 防并发覆盖
$list = array_diff(scandir($dir) ?: [], ['.', '..']);       // 列目录去点项
$ext  = pathinfo($name, PATHINFO_EXTENSION);
http_response_code(201);                                    // 设置响应码
header('Content-Type: application/json; charset=utf-8');
$ua   = $_SERVER['HTTP_USER_AGENT'] ?? '';
exit(1);                                                    // CLI 非零退出
```

## 9. 安全一行式

```php
$hash = password_hash($pwd, PASSWORD_BCRYPT);            // 密码哈希
$pass = password_verify($pwd, $hash);                     // 校验
$token = bin2hex(random_bytes(32));                       // 随机令牌
$clean = htmlspecialchars($html, ENT_QUOTES, 'UTF-8');    // 输出转义
$int   = filter_var($input, FILTER_VALIDATE_INT);         // 输入校验
$urlOK = filter_var($url, FILTER_VALIDATE_URL) !== false;
```

## 相关文档

- 📄 **[常见错误排查](./02-troubleshooting.md)** — 出错后来这里
- 📄 **[常用内置函数分类全表](../language-concepts/02-built-in-functions.md)** — 函数展开版
- 📄 **[类型系统与现代 OOP](../language-concepts/03-types-oop-modern.md)** — 类型语法细节
- 📄 **[PHP 8.4/8.5 增量特性](../language-concepts/12-modern-php-85.md)** — 钩子/管道/URI 扩展细节
