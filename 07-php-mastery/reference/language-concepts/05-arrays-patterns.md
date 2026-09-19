# 数组函数与集合操作模式

## 概述

PHP 数组是有序哈希表（可当列表也可当映射），配合 `array_*` 函数族可表达绝大多数集合运算。本文收录核心函数与 map/filter/reduce 组合范式，主要示例面向 PHP 8.3+；array_find/array_any/array_all 明确需要 PHP 8.4+。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#数组` `#集合操作` `#map` `#filter` `#reduce` |
| **更新日期** | `2026年9月` |

</details>

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

**陷阱**: 符合特定十进制整数形式的字符串键会转为 int，例如 "1"，但 "01" 保持字符串；浮点键转 int 丢失精度在现代 PHP 会产生弃用通知。

## 2. map：逐元素变换

**定义**: `array_map(?callable $callback, array $array, array ...$arrays): array` 返回变换后的数组。函数本身不会替换原数组槽位；回调若修改元素对象或外部引用，仍会造成可见副作用。只传一个数组保留键，传多个数组会重新编号。

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

**陷阱**: 若业务需要 JSON 列表，过滤后用 `array_values()` 重索引；若键是用户 ID 则应保留映射。并非每次过滤都会产生不连续键。无回调的弱过滤会把 `'0'` 一并剔除。`array_find` 返回 null 也可能表示找到了值为 null 的元素；需要区分时用 `array_find_key`，键不会是 null。空数组的 `array_all` 为 true、`array_any` 为 false，不代表已经检查到任何数据。

## 4. reduce：归约为单值

**定义**: `array_reduce(array $arr, callable $fn, mixed $initial = null): mixed`，回调签名 `(carry, item) => 新carry`。

```php
$nums = [1, 2, 3, 4];

// 求和
$sum = array_reduce($nums, fn(int $c, int $n): int => $c + $n, 0);   // 10

// 独立输入：每条记录需要 id，重复 id 的 + 合并保留先出现的记录。
$users = [['id' => 1, 'name' => 'Ada', 'age' => 36], ['id' => 2, 'name' => 'Alan', 'age' => 41]];
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

**陷阱**: 初始值省略时第一轮 carry 为 null，若回调参数声明为非可空 int 会触发类型错误；无类型算术的行为不能混为一谈——**永远显式传初始值**；纯计数/求和优先用 `count`/`array_sum`。

## 5. 组合范式：管道式数据处理

下面的金额以“分”为整数单位，输入已由边界校验为合法记录；演示不承担任意外部 JSON 的校验。整数仍有范围上限，金融业务应先约定最大金额和累计策略。

<!-- reference-case: {"id":"php-array-paid-pipeline","stdout":"47500\n"} -->
```php
<?php

declare(strict_types=1);

$orders = [
    ['id' => 1, 'total' => 12000, 'status' => 'paid'],
    ['id' => 2, 'total' => 8000,  'status' => 'pending'],
    ['id' => 3, 'total' => 30000, 'status' => 'paid'],
    ['id' => 4, 'total' => 5500,  'status' => 'paid'],
];

// 需求：已支付订单的金额总和（过滤 → 映射 → 归约）
$paidTotal = array_reduce(
    array_map(
        fn(array $o): int => $o['total'],
        array_filter($orders, fn(array $o): bool => $o['status'] === 'paid'),
    ),
    fn(int $c, int $t): int => $c + $t,
    0,
);
echo $paidTotal, PHP_EOL; // 47500 分
```

### 等价替代函数对照

| 目标 | reduce 手写 | 更直接的内建 |
|------|------------|-------------|
| 求和 | `array_reduce($nums, fn($c, $n) => $c + $n, 0)` | `array_sum()` |
| 计数 | reduce 累加 | `count()` |
| 首个满足 | filter + reset | `array_find()`（8.4+） |
| 去重 | — | `array_unique()` 需约定比较模式；`array_flip()` 只接受 int/string 值且冲突覆盖 |
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

**陷阱**: `usort` 比较函数必须返回负数、零或正数，并满足一致的排序关系；PHP 不会完整验证比较器的传递性，也不保证违反时抛异常；排序是原地修改，需要不可变风格时先对副本排序。

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

**陷阱**: `+` 与 `array_merge` 对数字键行为不同（`+` 保留左侧、merge 重索引追加）。`array_merge_recursive` 把冲突字符串键的值合并成数组；`...` 是浅合并，不是“递归覆盖”的替代品。要递归替换，应明确检查 `array_replace_recursive` 的规则。`array_diff`/`array_intersect` 按值转成字符串后比较，不能直接当严格类型集合运算。

## 完整实验：键、JSON 和重复元素

保存下面的程序为 `main.php`，执行 `php -d error_reporting=-1 main.php`。先观察过滤后的结构，再决定是否重编号。示例使用 PHP 8.3 可用的 API；上方的 array_find/any/all 需要 PHP 8.4+，不由这个实验覆盖。

<!-- reference-case: {"id":"php-array-key-contracts","stdout":"{\"0\":0,\"2\":2}\n[0,2]\n[\"0\",0,false,\"\"]\n{\"a\":2,\"b\":4}\n[2,4]\n{\"name\":\"left\",\"0\":\"L\"}\n{\"name\":\"right\",\"0\":\"L\",\"1\":\"R\"}\n[]\n[1]\nduplicate-id\n"} -->
```php
<?php
declare(strict_types=1);
function show(array $value): void {
    echo json_encode($value, JSON_THROW_ON_ERROR), PHP_EOL;
}
$filtered = array_filter([0, 1, 2], fn(int $n): bool => $n !== 1);
show($filtered);
show(array_values($filtered));
show(array_values(array_filter(['0', 0, null, false, ''], fn($v) => $v !== null)));
show(array_map(fn(int $n): int => $n * 2, ['a' => 1, 'b' => 2]));
show(array_map(fn(int $a, int $b): int => $a + $b, ['a' => 1, 'b' => 2], [1, 2]));
$left = ['name' => 'left', 0 => 'L'];
$right = ['name' => 'right', 0 => 'R'];
show($left + $right);
show(array_merge($left, $right));
show(array_diff([1], ['1']));
show(array_values(array_filter([1], fn($v) => !in_array($v, ['1'], true))));
$byId = [];
try {
    foreach ([['id' => 1], ['id' => 1]] as $row) {
        if (array_key_exists($row['id'], $byId)) {
            throw new DomainException('duplicate-id');
        }
        $byId[$row['id']] = $row;
    }
} catch (DomainException $e) { echo $e->getMessage(), PHP_EOL; }
```

`array_diff([1], ['1'])` 得到空数组，证明它并不是严格的整数集合差。最后一段用显式循环拒绝重复 ID；如果业务需要覆盖，删除拒绝分支会改变契约，不能作为纯重构看待。

## 完整实验：复制数组不等于复制其中对象

<!-- reference-case: {"id":"php-array-object-and-sort","stdout":"changed\n[2,3,1]\n[20,10]\n"} -->
```php
<?php
declare(strict_types=1);
$item = (object) ['name' => 'before'];
$original = [$item];
$mapped = array_map(function (object $row): object {
    $row->name = 'changed';
    return $row;
}, $original);
echo $original[0]->name, PHP_EOL;

$staff = [
    ['id' => 1, 'dept' => 'B', 'salary' => 10],
    ['id' => 2, 'dept' => 'A', 'salary' => 20],
    ['id' => 3, 'dept' => 'A', 'salary' => 10],
];
usort($staff, fn(array $a, array $b): int =>
    ($a['dept'] <=> $b['dept']) ?: ($b['salary'] <=> $a['salary']));
echo json_encode(array_column($staff, 'id'), JSON_THROW_ON_ERROR), PHP_EOL;
$scores = [10 => 30, 20 => 5];
asort($scores);
echo json_encode(array_keys($scores), JSON_THROW_ON_ERROR), PHP_EOL;
```

排序比较器把“部门升序、薪资降序”拆成两步，便于修改和检查；`asort` 保留业务键，`usort` 会重新编号。练习：增加同部门、同薪资员工，观察 PHP 8 稳定排序保留其原相对顺序；不要用 `(int)($a - $b)` 比较小数，小于 1 的差会错误地变成相等。

官方依据：[array_map](https://www.php.net/manual/en/function.array-map.php)、[array_diff](https://www.php.net/manual/en/function.array-diff.php)、[array_find](https://www.php.net/manual/en/function.array-find.php)。命名程序的限定结果见[验证报告](../../../shared-resources/tools/document-quality/reports/php-java-pipelines-validation.md)。

## 相关文档

- 📄 **[常用内置函数分类全表](./02-built-in-functions.md)** — 数组之外的全量函数速查
- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — 一等公民 callable 与回调类型
- 📄 **[教程：控制流程](../../basics/05-control-flow.md)** — 循环与集合操作的取舍


<!-- full-library-explanation -->
## 数组变换还要跟踪键与冲突规则

前置是数组键值与回调。array_filter 保留键，所以过滤列表后可能出现 0、2、5；JSON 编码可能把它当作对象。只有业务确实要求列表时才用 array_values，若键是用户 ID 就应保留。array_map 传一个数组时保留键，传多个数组时结果重新编号；不能只看元素值判断转换是否保持数据结构。

`$left + $right` 的同名键由左侧获胜，array_merge 的字符串键由后侧覆盖，数字键重新编号。为重复 ID 建索引时，必须决定首次优先、末次优先还是拒绝冲突。reduce 每轮复制不断增长的累加数组可能很贵，直接 foreach 累加通常更清楚，不必把所有循环改成函数链。

**练习**：过滤 [0,1,2] 中的 1，比较直接 json_encode 与 array_values 后编码，预期分别是对象形状和列表形状。再合并两个都含字符串键 name 和数字键 0 的数组，对照 + 与 array_merge。将合法值 '0' 加入样本，确认无回调 array_filter 会移除它，显式 null 过滤则保留。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
