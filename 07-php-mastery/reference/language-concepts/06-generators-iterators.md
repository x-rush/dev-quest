# 生成器与迭代器

## 概述

生成器（Generator）用 `yield` 把"遍历过程"变成可暂停的函数，是 PHP 处理大集合、惰性序列与内存敏感场景的核心工具；迭代器接口族是它的类型契约。本文按字典条目组织，供跳入查阅。Generator 自 5.5、yield from 自 7.0 引入；本页类型语法及字符串函数以 PHP 8.x 为前提。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#生成器` `#yield` `#迭代器` `#内存` |
| **更新日期** | `2026年9月` |

</details>

## 条目 1：Generator 与 `yield`

📌 **定义**: 含 `yield` 的函数调用时不执行函数体，而是返回一个 `Generator` 对象；每次迭代驱动函数运行到下一个 `yield` 处暂停。无需预先构建全部结果，但仍保留函数状态、局部变量及当前资源。

📖 **语法/签名**:

```text
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
    if ($fh === false) { throw new RuntimeException('无法打开文件'); }
    try {
        while (($line = fgets($fh)) !== false) {
            yield rtrim($line, "\r\n");        // 一行一行给，不把整个文件读进内存
        }
        if (!feof($fh)) { throw new RuntimeException('文件读取失败'); }
    } finally {
        fclose($fh);                  // 生成器正常结束、异常展开或销毁时清理；外部 break 后若仍持有生成器则可能尚未关闭
    }
}

foreach (readLines('access.log') as $line) {
    if (str_contains($line, 'ERROR')) {
        echo $line, PHP_EOL;
    }
}
```

⚠️ **常见陷阱**: 生成器**只能向前**迭代（rewind 只能在尚未越过第一个 yield 的阶段使用，不能任意倒回已经推进的生成器）；生成器是一次性的——迭代完毕即耗尽，重用需重新调用生成函数；`return $value` 的值进入 `getReturn()`，不会出现在产出序列里。

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

⚠️ **常见陷阱**: `yield from` 保留被委托对象的键，重复键在遍历时都可看到，转为保留键的数组时却会覆盖。仅正常完成的 Generator 才能取得返回值；因未捕获异常结束时 getReturn 仍会抛异常。外层不会自动继承内层返回值，需显式 return；对数组委托的表达式值是 null。

🔗 **相关条目**: [Generator 对象的方法](#条目-3generator-对象的方法)

## 条目 3：Generator 对象的方法

📌 **定义**: `Generator` 实现了 `Iterator`，另有三个专属方法：`send()` 向当前 `yield` 表达式"注入"值、`throw()` 在暂停点抛异常、`getReturn()` 取最终返回值。

📖 **语法/签名**:

| 方法 | 签名 | 语义 |
|------|------|------|
| `send` | `send(mixed $value): mixed` | 恢复执行，`$var = yield` 处收到 `$value` |
| `throw` | `throw(Throwable $e): mixed` | 在暂停点抛出 `$e` |
| `getReturn` | `getReturn(): mixed` | 正常完成后取返回值；未完成或异常结束时抛异常 |
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
echo $gen->current(), PHP_EOL;   // 0（首次执行至首个 yield 并暂停，值已经产出）
echo $gen->send(5), PHP_EOL;     // 5
echo $gen->send(3), PHP_EOL;     // 8
```

⚠️ **常见陷阱**: `send()` 可直接启动尚未运行的生成器，传入值即首个 `yield` 表达式的结果；`yield` 的"接收值"语义容易被误读为参数。

🔗 **相关条目**: [Fibers](./03-types-oop-modern.md)（需要"任意调用栈深度暂停"时用 Fiber 而非 Generator）

## 条目 4：迭代器接口族

📌 **定义**: `Traversable` 是"可 foreach"的类型标记（Generator/Iterator 都是它的子类型）；`Iterator` 定义手动遍历的 5 方法契约；`IteratorAggregate` 允许返回一个现成迭代器来外包遍历逻辑。

📖 **语法/签名**:

以下为接口形状示意，不能复制到 PHP 中重声明内置接口：

```text
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

⚠️ **常见陷阱**: 想定义对象的自有遍历协议，选 `IteratorAggregate` 或 `Iterator`；普通对象的可见属性也可被 foreach，但这种对象不因此满足 iterable 类型。`iterable` = `array|Traversable`。IteratorAggregate 能否重复遍历取决于 getIterator 是否每次返回可独立遍历的对象，返回同一个耗尽生成器不会自动恢复。

🔗 **相关条目**: [SPL 标准库](../library-guides/01-standard-library-spl.md)

## 条目 5：典型应用形态

📌 **定义**: 生成器最值钱的三个形态：**惰性管道**（每个阶段都是生成器，数据流过即处理）、**分页批处理**（`yield` 每批行，避免一次性取全表）、**无限序列**（按需产出，配合截断函数消费）。

📖 **语法/签名**: 组合形态无新语法，核心是"生成器返回生成器"的管道化。

💡 **示例**:

```php
<?php

declare(strict_types=1);

// 按需序列：到机器整数边界就显式失败，避免 PHP 整数溢出转浮点
function naturals(int $from = 0): Generator
{
    for ($i = $from; ; $i++) {
        yield $i;
        if ($i === PHP_INT_MAX) { throw new OverflowException('integer limit'); }
    }
}

// 截断函数：取前 n 个
function take(iterable $it, int $n): Generator
{
    if ($n <= 0) { return; }
    foreach ($it as $value) {
        yield $value;
        if (--$n === 0) { return; } // 在推进上游到下一项之前结束
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

## 完整实验：提前停止不会等于释放生成器

分别将以下完整程序保存为 `main.php`，运行 `php -d error_reporting=-1 main.php`。这个实验用清理标志观察 finally，而不是依赖平台文件锁行为。

<!-- reference-case: {"id":"php-generator-resource-lifetime","stdout":"0\nstart\n10\n0\nclosed\n1\n0\n"} -->
```php
<?php
declare(strict_types=1);
function values(array &$events): Generator {
    echo 'start', PHP_EOL;
    try {
        yield 10;
        yield 20;
    } finally {
        $events[] = 'closed';
        echo 'closed', PHP_EOL;
    }
}
$events = [];
$generator = values($events);
echo count($events), PHP_EOL;
foreach ($generator as $value) {
    echo $value, PHP_EOL;
    break;
}
echo count($events), PHP_EOL;
unset($generator); // 本例无其他引用，销毁暂停对象并执行 finally
echo count($events), PHP_EOL;
$unusedEvents = [];
$unused = values($unusedEvents);
unset($unused); // 函数体未启动，因此也未进入 try/finally
echo count($unusedEvents), PHP_EOL;
```

输出中 10 后先出现 0，说明 break 没有关闭仍持有引用的生成器。不要把 unset 写成通用 close：其他引用或循环引用会影响销毁时机。必须立即释放的资源应在明确生命周期里消费完、由资源所有者关闭，或设计专用可关闭迭代器。

## 完整实验：重复键与正常、异常返回

<!-- reference-case: {"id":"php-generator-delegation-return","stdout":"{\"0\":\"inner\"}\n[\"outer\",\"inner\"]\n[\"outer\",\"inner\"]\ndone\nnot-finished\nboom\nno-return\n"} -->
```php
<?php
declare(strict_types=1);
function inner(): Generator {
    yield 0 => 'inner';
    return 'done';
}
function outer(): Generator {
    yield 0 => 'outer';
    return yield from inner();
}
$keyed = iterator_to_array(outer());
echo json_encode((object) $keyed, JSON_THROW_ON_ERROR), PHP_EOL;
echo json_encode(iterator_to_array(outer(), false), JSON_THROW_ON_ERROR), PHP_EOL;
$normal = outer();
echo json_encode(iterator_to_array($normal, false), JSON_THROW_ON_ERROR), PHP_EOL;
echo $normal->getReturn(), PHP_EOL;
function broken(): Generator {
    yield 1;
    throw new RuntimeException('boom');
}
$failed = broken();
try { $failed->getReturn(); }
catch (Exception $e) { echo 'not-finished', PHP_EOL; }
try { iterator_to_array($failed); }
catch (RuntimeException $e) { echo $e->getMessage(), PHP_EOL; }
try { $failed->getReturn(); }
catch (Exception $e) { echo 'no-return', PHP_EOL; }
```

第一个输出为了直观显示键 0，显式转为对象后编码；覆盖早已发生在 iterator_to_array 中。正常的 return 会成为 getReturn 的值，异常终止不会把“没有结果”变成正常 null。

## 完整实验：取 N 项不额外推进上游

<!-- reference-case: {"id":"php-generator-take-demand","stdout":"[]\n0\n[1,4,9]\n3\n"} -->
```php
<?php
declare(strict_types=1);
function squares(int &$produced): Generator {
    for ($i = 1; $i <= 10; $i++) {
        $produced++;
        yield $i * $i;
    }
}
function take(iterable $input, int $n): Generator {
    if ($n <= 0) { return; }
    foreach ($input as $value) {
        yield $value;
        if (--$n === 0) { return; }
    }
}
$produced = 0;
echo json_encode(iterator_to_array(take(squares($produced), 0)), JSON_THROW_ON_ERROR), PHP_EOL;
echo $produced, PHP_EOL;
echo json_encode(iterator_to_array(take(squares($produced), 3)), JSON_THROW_ON_ERROR), PHP_EOL;
echo $produced, PHP_EOL;
```

把数量检查挪到 foreach 下一轮开头，会先要求上游产生第 N+1 项；如果上游是远程分页读取，额外推进就可能触发多余请求。练习：在第 4 项处主动抛异常，确认取 3 项仍不触发它。

官方依据：[Generator 语法](https://www.php.net/manual/en/language.generators.syntax.php)、[getReturn](https://www.php.net/manual/en/generator.getreturn.php)、[对象迭代](https://www.php.net/manual/en/language.oop5.iterations.php)。命名程序的结果及未覆盖边界见[验证报告](../../../shared-resources/tools/document-quality/reports/php-java-pipelines-validation.md)。

## 相关文档

- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — `iterable`/`Traversable` 类型契约
- 📄 **[数组操作模式](./05-arrays-patterns.md)** — 数据已在内存时的集合运算
- 📄 **[高级特性教程](../../basics/07-advanced-features.md)** — Generator 与 Fiber 的分工讲解

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team


<!-- full-library-explanation -->
## 惰性从第一次消费开始，资源一直跟着状态走

前置是 foreach、函数返回值和 finally。调用生成器函数只得到 Generator，第一次 current、next、foreach 等操作才驱动函数体。yield 暂停时局部变量和资源仍可能被保留，所以内存不只是“一个返回值”的大小；消费端把全部结果存进数组也会失去节省内存的收益。

```php
<?php
function steps(): Generator {
    echo 'started', PHP_EOL;
    yield 10;
    yield 20;
    return 'done';
}
$g = steps();
echo 'created', PHP_EOL;
foreach ($g as $value) { echo $value, PHP_EOL; }
echo $g->getReturn(), PHP_EOL;
```

保存为 generator.php，预期依次输出 created、started、10、20、done。练习：在第一项后 break 并保留 $g，再检查它并未自然耗尽；正常完成后才可取得最终返回值，显式 return 'done' 得到字符串，没有显式 return 的正常完成则得到 null。若多个 yield from 产生重复键，iterator_to_array 默认保留键会覆盖前值，想保留所有项应明确使用不保留键的模式。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
