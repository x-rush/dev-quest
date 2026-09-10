# 控制流程 - 从 if 到 match 表达式

> **文档简介**: 掌握 PHP 全部条件与循环结构，重点学习 PHP 8 的 match 表达式与枚举分支的组合用法
>
> **目标读者**: 已掌握函数与类的基础、正在完善语言核心能力的 PHP 初学者
>
> **前置知识**: 完成 [函数与面向对象](./04-functions-oop.md)，了解枚举的基本概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#条件` `#循环` `#match表达式` `#流程控制` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 选择正确的条件结构（if / match / 包含判断）
- ✅ 使用 for / foreach / while 及循环控制关键字
- ✅ 用 match 表达式替代 switch 与 if-else 链
- ✅ 避免弱比较、循环边界等经典陷阱

## 1. 条件结构

### if / elseif / else

```php
<?php

declare(strict_types=1);

$score = 85;

if ($score >= 90) {
    $grade = 'A';
} elseif ($score >= 80) {
    $grade = 'B';
} elseif ($score >= 60) {
    $grade = 'C';
} else {
    $grade = 'D';
}

echo $grade, PHP_EOL;   // B
```

### 三元与空合并的简写选择

```php
// 三元运算符：二选一
$label = $score >= 60 ? '及格' : '不及格';

// 空合并 ??：专治"存在吗"问题，比 isset + 三元简洁
$page = (int) ($_GET['page'] ?? '1');

// 空合并可以链式兜底，无需括号
$name = $input ?? $default ?? 'guest';
```

### 包含判断

```php
// 判断归属：in_array 带严格比较
$allowed = ['GET', 'POST'];
if (in_array($method, $allowed, true)) {
    // ...
}

// PHP 8.0 起字符串内置包含判断，不再需要 strpos !== false
if (str_contains($userAgent, 'Chrome')) {
    echo 'Chrome 浏览器', PHP_EOL;
}
```

## 2. match 表达式（PHP 8.0+）

`match` 是 PHP 8 最重要的流程控制新特性：它是**表达式**（有返回值）、使用**严格比较**、无穿透、未命中抛 `UnhandledMatchError`。

### 基本形态

```php
<?php

declare(strict_types=1);

$statusCode = 404;

$message = match (true) {
    $statusCode < 300 => '成功',
    $statusCode < 400 => '重定向',
    $statusCode < 500 => '客户端错误',
    default           => '服务端错误',
};

echo $message, PHP_EOL;   // 客户端错误
```

### 三种典型用法

```php
// 1. 值映射：替代查表式 if-else
$lang = match ($locale) {
    'zh'    => '中文',
    'en'    => 'English',
    'ja'    => '日本語',
    default => 'Unknown',
};

// 2. 多条件并列：一个分支匹配多个值
$ext = match (strtolower($file)) {
    'jpg', 'jpeg', 'png', 'gif', 'webp' => 'image',
    'mp4', 'mov', 'avi'                 => 'video',
    'pdf', 'doc', 'docx'                => 'document',
    default                             => 'other',
};

// 3. 条件分支：match (true) 配合布尔表达式
$fee = match (true) {
    $weight <= 1   => 5.0,
    $weight <= 5   => 12.0,
    $weight <= 20  => 30.0,
    default        => $weight * 2.0,
};
```

**`match` vs `switch` 对照**：

| 维度 | `match` | `switch` |
|------|---------|----------|
| 比较方式 | `===` 严格比较 | `==` 弱比较 |
| 返回值 | 是表达式，可直接赋值 | 是语句，需 break 后再赋值 |
| 穿透 | 无 | 忘写 `break` 会穿透（经典 bug） |
| 未命中 | 抛 `UnhandledMatchError` | 静默执行 default / 直接跳过 |

### match + 枚举：穷尽性检查

```php
<?php

declare(strict_types=1);

enum OrderStatus: string
{
    case Pending    = 'pending';
    case Paid       = 'paid';
    case Shipped    = 'shipped';
    case Cancelled  = 'cancelled';
}

function label(OrderStatus $status): string
{
    // 不写 default：新增枚举 case 时 PHPStan 会提醒此处漏了分支
    return match ($status) {
        OrderStatus::Pending   => '待支付',
        OrderStatus::Paid      => '已支付',
        OrderStatus::Shipped   => '已发货',
        OrderStatus::Cancelled => '已取消',
    };
}

echo label(OrderStatus::Paid), PHP_EOL;   // 已支付
```

枚举完整说明见 [`../reference/language-concepts/03-types-oop-modern.md`](../reference/language-concepts/03-types-oop-modern.md)。

## 3. 循环结构

### foreach：数组与对象的首选

```php
<?php

declare(strict_types=1);

$stocks = ['PHP-BOOK' => 12, 'GO-BOOK' => 3];

// 遍历值
foreach ($stocks as $qty) {
    echo $qty, ' ';
}

// 遍历键值
foreach ($stocks as $sku => $qty) {
    printf("%s 剩余 %d 本%s", $sku, $qty, PHP_EOL);
}

// 引用遍历：原地修改（记得用后 unset）
foreach ($stocks as $sku => &$qty) {
    $qty = max(0, $qty - 1);
}
unset($qty);
```

### for / while / do-while

```php
// for：已知次数
for ($i = 0; $i < 5; $i++) {
    echo $i, ' ';
}
echo PHP_EOL;

// while：先判断后执行
$retries = 0;
while ($retries < 3) {
    if (random_int(0, 2) === 0) {
        break;              // 模拟成功即退出
    }
    $retries++;
}

// do-while：至少执行一次
do {
    $input = random_int(1, 6);
    echo "掷出: {$input}", PHP_EOL;
} while ($input !== 6);
```

### 循环控制：break / continue / 指定层数

```php
foreach ($orders as $order) {
    foreach ($order['items'] as $item) {
        if ($item['qty'] <= 0) {
            continue 2;     // 跳过该订单，继续外层下一单
        }
        if ($order['status'] === 'cancelled') {
            break 2;        // 全部终止
        }
    }
}
```

## 4. goto 与替代方案

PHP 支持 `goto`，但现代代码中几乎只出现在解析器生成的代码或状态机内，**日常开发请用结构化控制替代**。需要提前退出多层嵌套时，优先考虑：

1. 提取函数 + `return`
2. match / 策略模式替代分支链
3. 异常表达异常路径（见 [错误与异常](./06-error-exceptions.md)）

## ✅ 最佳实践

- ✅ **新代码一律用 `match` 替代 `switch`**：严格比较 + 表达式语义 + 无穿透
- ✅ **配合枚举使用无 default 的 match**：换取静态分析的穷尽性检查
- ✅ **条件中避免赋值与副作用**：`if ($row = fetch())` 难读易错，拆成两行
- ❌ **不要在 foreach 引用遍历后忘记 `unset`**：残留引用会让后续赋值"意外"修改数组末元素
- ❌ **不要用 `elseif` 长链做类型分发**：多态或 match 更清晰

## ❓ 常见问题

### Q1: match 的分支能执行多条语句吗？
**A**: 不能，每个分支只能是一个表达式。多语句逻辑封装成函数/方法后调用，这反而促使代码更模块化。

### Q2: `foreach` 遍历时能增删元素吗？
**A**: PHP 7+ 遍历的是数组副本，增删原数组不影响当前遍历，但也别依赖此行为——需要结构性修改时先收集再统一处理。

### Q3: `while(true)` 死循环如何安全退出？
**A**: CLI 下 Ctrl+C；脚本内用 `pcntl` 信号或设置截止条件。消费队列的标准做法是捕获 `SIGTERM` 后优雅退出。

## 🎯 练习与实践

### 基础练习
- [ ] 用 `match (true)` 实现 BMI 分级（偏瘦/正常/偏胖/肥胖）
- [ ] 把第 2 节 `label()` 函数补一个新枚举 case `Refunded`，观察不写 default 时的行为与 PHPStan 提示
- [ ] 用 `do-while` 写一个"猜数字"游戏脚本（`random_int` 生成 1-100）

### 进阶挑战
- [ ] 实现 FizzBuzz，但要求只用 match 表达式，不允许出现任何 if
- [ ] 编写函数统计字符串中元音/辅音/数字/其他四类字符数，用 `match` 分类

---

## 🔗 相关文档

- 📄 **[错误与异常](./06-error-exceptions.md)** — 下一节：异常层次与 Throwable
- 📄 **[控制结构全表](../reference/language-concepts/04-control-flow.md)** — 所有结构的语法速查
- 📄 **[数组与集合操作模式](../reference/language-concepts/05-arrays-patterns.md)** — 用集合操作替代部分循环
