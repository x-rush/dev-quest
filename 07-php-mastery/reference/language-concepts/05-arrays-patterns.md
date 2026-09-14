# 数组函数与集合操作模式

## 概述

PHP 数组是有序哈希表（可当列表也可当映射），配合 `array_*` 函数族可表达绝大多数集合运算。本文收录核心函数与 map/filter/reduce 组合范式，所有示例兼容 PHP 8.3+。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#数组` `#集合操作` `#map` `#filter` `#reduce` |
| **更新日期** | `2026年9月` |

## 1. 数组基础形态速览

```php
$list = ['a', 'b', 'c'];                    // 列表：自动数字索引 0..n
$map  = ['name' => 'Ada', 'age' => 36];     // 映射：字符串键
$mixed = [10 => 'x', 'y'];                  // 'y' 的键为 11（自动续接）
$nested = ['rows' => [['id' => 1]]];        // 任意嵌套

// 键规则
$mixed2 = [1 => 'a', '1' => 'b', 1.8 => 'c'];   // ⚠️ 全部归并为键 1，依次覆盖
var_dump($mixed2);   // [1 => 'c']
```

**陷阱**: 含整数字符串的键会被强制转 int；浮点键截断为 int。

## 2. map：逐元素变换

**定义**: `array_map(callable $fn, array $arr): array` 对每个元素应用回调，返回新数组（不改变原数组）。

```php
$prices = [100, 250, 80];

// 基本变换
$withTax = array_map(fn(int $p): float => round($p * 1.13, 2), $prices);

// map 回调只拿"值"：需要键时，把键数组与值数组同时传入
$upper = array_map(
    fn(string $k, mixed $v): string => strtoupper($k) . '=' . $v,
    array_keys($map),
    array_values($map),
);

// 多数组按位合并：回调传 null
$names = ['Ada', 'Alan'];
$ages  = [36, 41];
$pairs = array_map(null, $names, $ages);   // [['Ada',36], ['Alan',41]]
```

**陷阱**: `array_map` 回调只接收"值"，不接收键；多个数组长度不等时以最长者为准，短数组缺位补 `null`。

## 3. filter：筛选元素

**定义**: `array_filter(array $arr, ?callable $fn = null, int $mode = 0): array` 按回调保留元素，**保留原键**。

```php
$nums = [0, 1, 2, '', 'a', null, false, true];

array_filter($nums);                        // 无回调：剔除弱 false 值 → [1=>1, 2=>2, 4=>'a', 7=>true]
array_filter($nums, fn($v) => $v !== null); // 严格剔除 null

$users = [['age' => 15], ['age' => 22], ['age' => 8]];
$adults = array_values(array_filter(          // 常用组合：过滤后重索引
    $users,
    fn(array $u): bool => $u['age'] >= 18,
));

// 按键过滤 / 双向过滤
array_filter($map, fn(string $k) => str_starts_with($k, 'app_'), ARRAY_FILTER_USE_KEY);
array_filter($map, fn(mixed $v, string $k) => $v !== '' && $k !== 'debug', ARRAY_FILTER_USE_BOTH);

// PHP 8.4 新函数：array_find / array_any / array_all
array_find($users, fn(array $u): bool => $u['age'] > 20);    // 首个满足的元素或 null
array_any($users, fn(array $u): bool => $u['age'] < 10);     // true
array_all($users, fn(array $u): bool => $u['age'] > 0);      // true
```

**陷阱**: 结果键不连续——必须 `array_values()` 重索引再 `json_encode`，否则输出成对象；无回调的弱过滤会把 `'0'` 一并剔除。

## 4. reduce：归约为单值

**定义**: `array_reduce(array $arr, callable $fn, mixed $initial = null): mixed`，回调签名 `(carry, item) => 新carry`。

```php
$nums = [1, 2, 3, 4];

// 求和
$sum = array_reduce($nums, fn(int $c, int $n): int => $c + $n, 0);   // 10

// 构建映射：reduce 出"数组"也完全合法
$byId = array_reduce(
    $users,
    fn(array $c, array $u): array => $c + [$u['id'] => $u],   // + 合并保留数字键
    [],
);

// 分组计数
$words = ['php', 'go', 'php', 'rust', 'php'];
$counts = array_reduce($words, function (array $c, string $w): array {
    $c[$w] = ($c[$w] ?? 0) + 1;
    return $c;
}, []);   // ['php' => 3, 'go' => 1, 'rust' => 1]
```

**陷阱**: 初始值省略时第一轮 `$carry` 为 `null`，对 `int` 运算直接 TypeError——**永远显式传初始值**；纯计数/求和优先用 `count`/`array_sum`。

## 5. 组合范式：管道式数据处理

```php
<?php

declare(strict_types=1);

$orders = [
    ['id' => 1, 'total' => 120.0, 'status' => 'paid'],
    ['id' => 2, 'total' => 80.0,  'status' => 'pending'],
    ['id' => 3, 'total' => 300.0, 'status' => 'paid'],
    ['id' => 4, 'total' => 55.0,  'status' => 'paid'],
];

// 需求：已支付订单的金额总和（过滤 → 映射 → 归约）
$paidTotal = array_reduce(
    array_map(
        fn(array $o): float => $o['total'],
        array_filter($orders, fn(array $o): bool => $o['status'] === 'paid'),
    ),
    fn(float $c, float $t): float => $c + $t,
    0.0,
);   // 475.0
```

### 等价替代函数对照

| 目标 | reduce 手写 | 更直接的内建 |
|------|------------|-------------|
| 求和 | `array_reduce($nums, fn($c, $n) => $c + $n, 0)` | `array_sum()` |
| 计数 | reduce 累加 | `count()` |
| 首个满足 | filter + reset | `array_find()`（8.4+） |
| 去重 | — | `array_unique()` / `array_flip()` 技巧 |
| 极值 | — | `max()` / `min()` |
| 判存在 | filter + count | `in_array($v, $arr, true)` |

## 6. 排序与比较

```php
// <=> 太空船运算符返回 -1/0/1，是 usort 的标配
usort($users, fn(array $a, array $b): int => $a['age'] <=> $b['age']);

// 多级排序：先按部门升序，再按工资降序
usort($staff, fn(array $a, array $b): int =>
    [$a['dept'], $b['salary']] <=> [$b['dept'], $a['salary']]
);

// 保留键的排序
uasort($map, fn($a, $b) => $a <=> $b);   // 关联数组排序后键不丢

// 按另一数组定义的顺序排序
$order = ['high' => 0, 'normal' => 1, 'low' => 2];
usort($tasks, fn($a, $b) => $order[$a['priority']] <=> $order[$b['priority']]);
```

**陷阱**: `usort` 比较函数必须**全序且对称**（8.0 起违反会抛异常）；排序是原地修改，需要不可变风格时先对副本排序。

## 7. 实用工具函数集

```php
// 抽取列并指定键：结果直接是 [id => name] 映射
$index = array_column($users, 'name', 'id');

// 集合运算
$diff  = array_diff([1, 2, 3], [2]);                 // 值差集 [0=>1, 2=>3]
$diffA = array_diff_key(['a' => 1, 'b' => 2], ['a' => 0]);   // 键差集
$inter = array_intersect([1, 2, 3], [2, 3]);         // 值交集
$union = $a + $b;                                    // ⚠️ + 合并：先到先得，不覆盖

// 随机与切分
$keys  = array_rand($list, 2);                       // 随机取 2 个"键"
$chunk = array_chunk($list, 2, true);                // 分块，第三参保留键

// 折叠展开
$flipped = array_flip(['a' => 1]);                   // [1 => 'a']
$deep    = array_merge_recursive($a, $b);            // ⚠️ 同名键递归成数组，慎用
```

**陷阱**: `+` 与 `array_merge` 对数字键行为不同（`+` 保留左侧、merge 重索引追加）；`array_merge_recursive` 极易产生意外深嵌套，多数场景该用 `...` 展开。

## 相关文档

- 📄 **[常用内置函数分类全表](./02-built-in-functions.md)** — 数组之外的全量函数速查
- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — 一等公民 callable 与回调类型
- 📄 **[教程：控制流程](../../basics/05-control-flow.md)** — 循环与集合操作的取舍
