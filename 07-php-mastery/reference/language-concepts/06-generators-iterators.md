# 生成器与迭代器

## 概述

生成器（Generator）用 `yield` 把"遍历过程"变成可暂停的函数，是 PHP 处理大集合、惰性序列与内存敏感场景的核心工具；迭代器接口族是它的类型契约。本文按字典条目组织，供跳入查阅。属语言稳定层，无版本门槛（Generator 5.5+、`yield from` 7.0+）。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#生成器` `#yield` `#迭代器` `#内存` |
| **更新日期** | `2026年9月` |

## 条目 1：Generator 与 `yield`

📌 **定义**: 含 `yield` 的函数调用时不执行函数体，而是返回一个 `Generator` 对象；每次迭代驱动函数运行到下一个 `yield` 处暂停。内存中只保留"当前一个值"，而非整个结果集。

📖 **语法/签名**:

```php
function generatorName(args): Generator
{
    yield $value;            // 产出值
    yield $key => $value;    // 产出键值对
}
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

function readLines(string $path): Generator
{
    $fh = fopen($path, 'rb');
    try {
        while (($line = fgets($fh)) !== false) {
            yield trim($line);        // 一行一行给，不把整个文件读进内存
        }
    } finally {
        fclose($fh);                  // 迭代结束/中断时可靠关闭
    }
}

foreach (readLines('access.log') as $line) {
    if (str_contains($line, 'ERROR')) {
        echo $line, PHP_EOL;
    }
}
```

⚠️ **常见陷阱**: 生成器**只能向前**迭代（`rewind` 只能在开始前调用一次）；生成器是一次性的——迭代完毕即耗尽，重用需重新调用生成函数；`return $value` 的值进入 `getReturn()`，不会出现在产出序列里。

🔗 **相关条目**: [数组操作模式](./05-arrays-patterns.md)、[Fibers](./03-types-oop-modern.md)

## 条目 2：`yield from` —— 生成器委托

📌 **定义**: `yield from` 把另一个可迭代对象（数组、生成器、Traversable）的全部产出"转发"出来，表达式值是被委托生成器的 `return` 值，用于拆分生成器逻辑。

📖 **语法/签名**: `yield from iterable;`（表达式值 = 被委托生成器的 return 值）

💡 **示例**:

```php
function inner(): Generator
{
    yield 1;
    yield 2;
    return 'inner-done';
}

function outer(): Generator
{
    yield 0;
    $result = yield from inner();   // 转发 1、2，并拿到 return 值
    echo $result, PHP_EOL;          // inner-done
}

foreach (outer() as $value) {
    echo $value, PHP_EOL;           // 0 1 2
}
```

⚠️ **常见陷阱**: `yield from` 对数组是逐个产出（键保留原数组键）；`getReturn()` 只能在最外层生成器上取值。

🔗 **相关条目**: [Generator 对象的方法](#条目-3generator-对象的方法)

## 条目 3：Generator 对象的方法

📌 **定义**: `Generator` 实现了 `Iterator`，另有三个专属方法：`send()` 向当前 `yield` 表达式"注入"值、`throw()` 在暂停点抛异常、`getReturn()` 取最终返回值。

📖 **语法/签名**:

| 方法 | 签名 | 语义 |
|------|------|------|
| `send` | `send(mixed $value): mixed` | 恢复执行，`$var = yield` 处收到 `$value` |
| `throw` | `throw(Throwable $e): mixed` | 在暂停点抛出 `$e` |
| `getReturn` | `getReturn(): mixed` | 生成器结束前调用抛异常 |
| `current/key/next/valid/rewind` | Iterator 标准 | 手动驱动迭代 |

💡 **示例**:

```php
function accumulator(): Generator
{
    $total = 0;
    while (true) {
        $delta = yield $total;      // 产出当前值；send 传入增量
        $total += $delta;
    }
}

$gen = accumulator();
echo $gen->current(), PHP_EOL;   // 0（首次停在首个 yield 前）
echo $gen->send(5), PHP_EOL;     // 5
echo $gen->send(3), PHP_EOL;     // 8
```

⚠️ **常见陷阱**: `send()` 可直接启动尚未运行的生成器，传入值即首个 `yield` 表达式的结果；`yield` 的"接收值"语义容易被误读为参数。

🔗 **相关条目**: [Fibers](./03-types-oop-modern.md)（需要"任意调用栈深度暂停"时用 Fiber 而非 Generator）

## 条目 4：迭代器接口族

📌 **定义**: `Traversable` 是"可 foreach"的类型标记（Generator/Iterator 都是它的子类型）；`Iterator` 定义手动遍历的 5 方法契约；`IteratorAggregate` 允许返回一个现成迭代器来外包遍历逻辑。

📖 **语法/签名**:

```php
interface Traversable {}            // 仅作类型约束，不能直接实现
interface Iterator extends Traversable {
    current(): mixed; key(): mixed; next(): void;
    rewind(): void; valid(): bool;
}
interface IteratorAggregate extends Traversable {
    getIterator(): Traversable;     // 通常 return new ArrayIterator($data)
}
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

final class Shelf implements IteratorAggregate
{
    public function __construct(private array $books = []) {}

    public function getIterator(): ArrayIterator
    {
        return new ArrayIterator($this->books);
    }
}

foreach (new Shelf(['PHP 内功', 'SQL 必知']) as $book) {
    echo $book, PHP_EOL;
}
```

⚠️ **常见陷阱**: 类要可 foreach，选 `IteratorAggregate`（省事）或 `Iterator`（精细控制）之一；`iterable` 类型 = `array|Traversable`，函数签名用它最宽容。

🔗 **相关条目**: [SPL 标准库](../library-guides/01-standard-library-spl.md)

## 条目 5：典型应用形态

📌 **定义**: 生成器最值钱的三个形态：**惰性管道**（每个阶段都是生成器，数据流过即处理）、**分页批处理**（`yield` 每批行，避免一次性取全表）、**无限序列**（按需产出，配合截断函数消费）。

📖 **语法/签名**: 组合形态无新语法，核心是"生成器返回生成器"的管道化。

💡 **示例**:

```php
<?php

declare(strict_types=1);

// 无限序列：自然数
function naturals(int $from = 0): Generator
{
    for ($i = $from; ; $i++) {
        yield $i;
    }
}

// 截断函数：取前 n 个
function take(iterable $it, int $n): Generator
{
    foreach ($it as $value) {
        if ($n-- <= 0) {
            return;
        }
        yield $value;
    }
}

// 惰性管道：平方 → 取前 5 个（全程只有 5 个值真正被计算）
foreach (take((static function (): Generator {
    foreach (naturals(1) as $n) {
        yield $n * $n;
    }
})(), 5) as $value) {
    echo $value, PHP_EOL;   // 1 4 9 16 25
}
```

⚠️ **常见陷阱**: 生成器管道里任何一个阶段抛异常，下游 `finally` 与资源清理要自己兜住；不要在生成器内 `die`/`exit`。

🔗 **相关条目**: [数组操作模式](./05-arrays-patterns.md)、[Generator 对象的方法](#条目-3generator-对象的方法)

## 相关文档

- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — `iterable`/`Traversable` 类型契约
- 📄 **[数组操作模式](./05-arrays-patterns.md)** — 数据已在内存时的集合运算
- 📄 **[高级特性教程](../../basics/07-advanced-features.md)** — Generator 与 Fiber 的分工讲解

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
