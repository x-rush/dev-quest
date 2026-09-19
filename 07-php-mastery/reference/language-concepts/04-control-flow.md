# 控制结构全表

## 概述

本文收录 PHP 全部控制结构的语法与行为要点，含 PHP 8 的 `match` 表达式与 PHP 7.4+ 的箭头函数。条目式排列，供速查与跳读。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#控制结构` `#match` `#循环` `#条件` |
| **更新日期** | `2026年9月` |

</details>

## 1. 条件结构

### if / elseif / else

**定义**: 基础分支。`elseif` 可连写；替代语法 `if: endif;` 用于模板混写场景。

```php
if ($a > $b) {
    echo 'a 大';
} elseif ($a === $b) {
    echo '相等';
} else {
    echo 'b 大';
}

```

替代语法用于 PHP 模板文件：

```html
<?php if ($ok): ?>
    <p>通过</p>
<?php endif; ?>
```

**陷阱**: 花括号语法中 `elseif` 与 `else if` 都可用；但替代语法必须写成 `elseif: ... endif;`，不要把两个词拆开，否则会按嵌套 `if` 的形式解析而无法与 `endif` 正确配对。条件内赋值 `if ($x = f())` 合法但高危。

### 三元运算符 `? :` 与空合并 `??`

```php
$label = $ok ? 'yes' : 'no';
$label ??= 'default';                 // null 时赋值（7.4+）
$page = $_GET['p'] ?? $fallback ?? 1; // 链式兜底，无需 isset
```

**陷阱**: 三元的嵌套不加括号在 PHP 8 起直接报错（此前为弃用警告）；`??` 只处理 `null`，`0`/`''`/`false` 不会被跳过。

### match 表达式（8.0+）

**定义**: 表达式形式的严格比较分支，有值、无穿透、未命中抛 `UnhandledMatchError`。

```php
$grade = match (true) {
    $score >= 90 => 'A',
    $score >= 80 => 'B',
    $score >= 60 => 'C',
    default      => 'D',
};

// match 不会进行模式解构；先显式解构，再判断坐标。
[$x, $y] = $point; // 此前应验证输入确为两个数字的列表
$desc = match (true) {
    $x == 0 && $y == 0 => '原点',
    $y == 0 => "X 轴上 x={$x}",
    $x == 0 => "Y 轴上 y={$y}",
    default => "点({$x}, {$y})",
};

// 无 default：配合枚举获得穷尽性检查
$op = match ($status) {
    OrderStatus::Pending => '待处理',
    OrderStatus::Done    => '完成',
};
```

**陷阱**: 分支体只能是一个表达式（不能用语句块）；`match (true)` 按书写顺序求值，注意条件先后；无 `default` 时未命中即抛异常。

### 正文提取验证：match 的严格比较与未命中

下面是可独立执行的完整围栏。它刻意把整数 `1` 与字符串 `'1'` 放在一起：`match` 不做 `switch` 那样的弱比较；没有 `default` 的未命中会抛 `UnhandledMatchError`。

```php
<?php
declare(strict_types=1);

$numberCase = match (1) {
    '1' => 'string',
    1 => 'integer',
};

try {
    match ('missing') {
        'ok' => 'ok',
    };
} catch (UnhandledMatchError) {
    $unmatched = 'unmatched';
}

echo "$numberCase|$unmatched\n";
```

### switch（遗留兼容）

```php
switch ($code) {
    case 200:
    case 201:          // 故意穿透共享分支
        echo 'ok';
        break;
    case 404:
        echo 'not found';
        break;
    default:
        echo 'unknown';
}
```

**陷阱**: 弱比较（`==`）+ 穿透是两大经典 bug 源；需要表达式结果和严格比较时优先 match；多语句分支仍可使用 if/switch，并显式管理穿透。

## 2. 循环结构

### foreach（数组/对象首选）

```php
foreach ($map as $key => $value) { /* ... */ }

// 引用遍历：修改原数组，之后必须 unset
foreach ($map as $key => &$value) {
    $value = strtoupper($value);
}
unset($value);

// 对象遍历：实现 Iterator/IteratorAggregate 的类可自定义行为
foreach ($collection as $item) { /* ... */ }
```

**陷阱**: 普通 foreach 按值提供元素，但不意味着立即深复制整个数组；对象和引用元素另有共享语义，引用遍历忘记 `unset` 会导致末元素被"残留引用"污染。

### for / while / do-while

```php
for ($i = 0, $j = 10; $i < $j; $i++, $j--) { /* 双变量初始化与步进 */ }

while (($line = fgets($fh)) !== false) {   // 惯用法：读文件
    process($line);
}

do { $roll = random_int(1, 6); } while ($roll !== 6);
```

**陷阱**: `while ($row = fetch())` 依赖弱比较，`0`/`''` 会提前终止，写成 `!== false`；`do-while` 至少执行一次。

### break / continue（含层数）

```php
foreach ($orders as $o) {
    foreach ($o['items'] as $item) {
        if (!$item['valid']) {
            continue 2;    // 直接跳到外层下一轮
        }
        if ($o['cancel']) {
            break 2;       // 双层全退
        }
    }
}
```

**陷阱**: `break 2`/`continue 2` 的数字是"跳出层数"而非"目标标签"，超过实际嵌套层数是致命错误。

## 3. 分支跳转与终止

| 结构 | 语法 | 说明 |
|------|------|------|
| `return` | `return $v;` | 结束函数/脚本（顶层 return 可终止 include） |
| `goto` | `goto end;` | 同文件内跳转，只能跳出不能跳入循环/方法 |
| `exit`/`die` | `exit(1)` / `exit('msg')` | 终止进程；输出消息等价 `echo` 后 `exit(0)` |
| `declare` | `declare(strict_types=1);` | 编译/执行指令；strict_types 须为文件第一条语句 |
| `require`/`include` | `require __DIR__.'/x.php'` | 失败：require 致命，include 警告；`_once` 变体防重复加载 |

**陷阱**: `include` 返回被包含文件的 `return` 值，可用来做简易配置加载，但现代项目用 Composer autoload + 类；`exit('消息')` 退出码恒为 0，脚本编排场景必须用 `exit(1)`。

## 4. 箭头函数与闭包

### fn（7.4+）

**定义**: 单表达式匿名函数，自动按值捕获外部变量。

```php
$factor = 10;
$scale = fn(int $n): int => $n * $factor;      // 自动捕获 $factor

$nums = array_map(
    fn(int $n): int => $n * 2,
    [1, 2, 3],
);
```

**陷阱**: 按值捕获是"定义时快照"，之后外部变量变化不影响 fn；需要引用捕获或多语句时用 `function ... use (...)`。

### function 闭包

```php
$count = 0;
$counter = function () use (&$count): int {   // & 按引用捕获
    return ++$count;
};
$counter(); $counter();    // $count === 2

// 闭包在类内自动绑定 $this；static function/fn 不绑定，用于严格隔离
$pure = static fn(): int => 42;
```

**陷阱**: `use ($obj)` 复制的是对象句柄（对象本身仍共享），基础类型才是真复制；`Closure::bind` 可改绑定作用域，慎用。

### callable 三形态（回调传参）

```php
usort($rows, fn($a, $b) => $a['age'] <=> $b['age']);  // 闭包
usort($rows, $this->compare(...));                     // 一等公民语法（8.1+）
usort($rows, [self::class, 'compare']);                // 数组形式（遗留）
```

## 5. 生成器：yield 与 yield from

```php
function readLines(string $file): Generator
{
    $fh = fopen($file, 'rb');
    if ($fh === false) { throw new RuntimeException('无法打开文件'); }
    try {
        while (($line = fgets($fh)) !== false) {
            yield rtrim($line, "\r\n"); // 保留行内空格；内存受最长行及消费方保留数据影响
        }
    } finally {
        fclose($fh);                    // 生成器结束或被 GC 时执行
    }
}

function merged(): Generator
{
    yield from readLines('a.log');      // 委托另一个生成器/可迭代
    yield from [4, 5];
}
```

**陷阱**: 生成器只能向前；`Generator::send()` 才能向 yield 点注入值；生成器函数可 `return` 终止，返回值经 `getReturn()` 获取。

## 陷阱速查

- **match vs switch**：严格/弱比较、表达式/语句、有无穿透——三者差异是 8.0 迁移最高频考点
- **引用遍历三步曲**：`&$v` → 使用 → `unset($v)`，缺一不可
- **`??` 与 `?:` 混淆**：`$a ?? $b` 判 null；`$a ?: $b` 判弱 false（`0`、`''` 也会触发）——语义不同勿混用

## 相关文档

- 📄 **[PHP 关键字详解](./01-php-keywords.md)** — `break`/`continue`/`goto` 等关键字条目
- 📄 **[数组操作模式](./05-arrays-patterns.md)** — 用集合操作替代显式循环
- 📄 **[教程：控制流程](../../basics/05-control-flow.md)** — 渐进式讲解版


<!-- full-library-explanation -->
## 分支比较与变量绑定要分开理解

前置是布尔值和数组。match 将输入与各分支条件严格比较，不会像某些语言的模式匹配那样给 `$x` 自动绑定值。`match (true)` 则让每个条件表达式产生布尔值，按顺序选择第一个 true；更宽泛的条件放在前面会遮住后面的细分条件。

`??` 可处理未设置或 null，`?:` 按真假性判断，因此合法的 0 和字符串 '0' 会触发后者的默认值。读取用户输入时先决定“缺失、空串、零”是否不同，再选运算符。无 default 的枚举 match 在遗漏值出现时抛异常，并不代表 PHP 编译器已经完成穷尽性证明。

**练习**：给分支依次输入 0、'0'、null、false，记录 match 与 switch 的选择；再给 score=95 的 match(true) 将 >=60 放在第一条，解释为何得到 C。对生成器只读取第一行后保留引用，观察 finally 不会因为外部 break 就必然立即完成；需要明确资源所有者与释放时机。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
