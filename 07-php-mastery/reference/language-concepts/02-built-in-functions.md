# PHP 常用内置函数：输入、返回值、失败与副作用

本篇从数组、字符串、验证/编解码、时间、数学、文件六类建立查询入口。PHP 的函数集合受版本与扩展影响，不存在一张对所有安装环境都相同的“全部内置函数表”。完整索引见[官方函数参考](https://www.php.net/manual/en/funcref.php)；先用 `php -v`、`php -m` 确认环境，扩展函数可用 `function_exists` 检查。

这里的 5 个完整脚本采用 PHP 8.3+、不依赖 mbstring/intl 等可选扩展；分别存成 `.php` 文件后运行 `php 文件名.php`。PHP 8.4 新增函数单独列出，不能在旧解释器上直接调用。前置知识是变量、数组、函数与严格比较。

## 1. 数组：先决定保留键还是重新编号

PHP 数组同时承担列表与映射用途。查询失败、键为 0、值为 null 是三个不同状态；不要用一次宽松布尔转换把它们混在一起。

| 任务 | 函数 | 契约与边界 |
|---|---|---|
| 构造 | `range`、`array_fill`、`array_combine` | range 生成序列；fill 按数量填充；combine 要求键值数量一致，否则 ValueError |
| 查值 | `in_array($v, $a, true)`、`array_search($v, $a, true)` | 第三参明确严格类型比较；search 返回键或 false，必须严格判断 |
| 查键 | `array_key_exists`、`array_keys`、`array_values` | key_exists 对值为 null 的现有键也返回 true；values 重新编号为连续整数 |
| 取片段/列 | `array_slice`、`array_column` | slice 默认重新编号整数键，第四参 true 才保留；column 的索引键重复会覆盖 |
| 入栈/出栈 | `array_push`、`array_pop` | push 修改原数组并返回新长度；pop 删除末项并返回值，空数组返回 null |
| 队首修改 | `array_unshift`、`array_shift` | 修改原数组，数字键可能重编；不要作为超大队列的默认实现 |
| 替换片段 | `array_splice` | 修改原数组并返回移除部分，不是返回修改后的完整数组 |
| 变换/筛选 | `array_map`、`array_filter` | 单数组 map 保留键，多数组 map 重新编号；filter 保留键 |
| 归约 | `array_reduce` | 指定初始值，避免空输入的结果与累加类型不明确 |
| 去重/倒序 | `array_unique`、`array_reverse` | unique 默认按字符串形式比较且保留键；reverse 是否保留数字键由参数决定 |

<!-- reference-case: {"id":"php-array","stdout":"int(0)\nbool(true)\n{\"1\":2,\"2\":4}\n[2,4]\nbool(true)\nbool(false)\n"} -->
```php
<?php
declare(strict_types=1);
$values = [0, 2, 4];
$position = array_search(0, $values, true);
var_dump($position, $position !== false);
$filtered = array_filter($values, fn(int $n): bool => $n > 0);
echo json_encode($filtered, JSON_THROW_ON_ERROR), PHP_EOL;
echo json_encode(array_values($filtered), JSON_THROW_ON_ERROR), PHP_EOL;
$row = ['nickname' => null];
var_dump(array_key_exists('nickname', $row), isset($row['nickname']));
```

输出首先是 `int(0)`、`bool(true)`，然后是 `{"1":2,"2":4}` 和 `[2,4]`，最后 true/false。`array_filter` 之后的整数键不连续，因此 JSON 编成对象；确实需要列表时才用 array_values。无回调的 filter 会去掉 false、0、`'0'`、空字符串、null 等假值，可能误删合法数据，应按需求写条件。

### 排序会改变谁？

| 函数 | 按什么排序 | 键处理 |
|---|---|---|
| `sort` / `rsort` | 值，升序/降序 | 原地修改且重新编号 |
| `asort` / `arsort` | 值，升序/降序 | 保留键关联 |
| `ksort` / `krsort` | 键 | 保留键值关联 |
| `usort` / `uasort` / `uksort` | 自定义比较器比较值/值/键 | 依次为重编键/保留键/保留键 |

比较器返回负整数、0、正整数，不应返回“a 是否大于 b”的布尔值。PHP 8 起比较为相等的元素保留原相对顺序；这不意味着混合数字和字符串的比较自动符合业务意图，应统一数据类型或指定比较方式。[sort 文档](https://www.php.net/manual/en/function.sort.php)、[usort 文档](https://www.php.net/manual/en/function.usort.php)说明了返回值与键处理。

<!-- reference-case: {"id":"php-sort","stdout":"bool(true)\n[1,2,3]\n[3,1,2]\n[\"Ada\",\"Lin\"]\n"} -->
```php
<?php
declare(strict_types=1);
$original = [3, 1, 2];
$sorted = $original;
$success = sort($sorted, SORT_NUMERIC);
var_dump($success);
echo json_encode($sorted, JSON_THROW_ON_ERROR), PHP_EOL;
echo json_encode($original, JSON_THROW_ON_ERROR), PHP_EOL;
$users = [['name' => 'Lin', 'age' => 30], ['name' => 'Ada', 'age' => 20]];
usort($users, fn(array $a, array $b): int => $a['age'] <=> $b['age']);
echo json_encode(array_column($users, 'name'), JSON_THROW_ON_ERROR), PHP_EOL;
```

不要写 `$sorted = sort($original)`，那样得到的是 bool 且原数组已被排序。数组复制是值语义，但数组中的对象仍引用同一对象，不能据此推断深拷贝。

PHP 8.4 的 `array_find` 返回首个符合条件的值或 null，`array_find_key` 返回相应键或 null；匹配到 null 值时，用 find_key 可以区分“找到 null”和“没有找到”。`array_any`、`array_all` 返回是否至少一个/全部符合条件；空数组的 any 是 false，all 是 true。版本入口见 [PHP 8.4 新函数](https://www.php.net/manual/en/migration84.new-functions.php)。

## 2. 字符串：协议按字节，界面按文字边界

| 任务 | 函数与最小调用 | 边界 |
|---|---|---|
| 包含与前后缀 | `str_contains('abc', 'b')`、`str_starts_with`、`str_ends_with` | 返回 bool、区分大小写；空查找字符串匹配成功 |
| 位置 | `strpos('abc', 'a')` → 0 | 未找到返回 false，因此比较 `!== false` |
| 长度与截取 | `strlen`、`substr` | 按字节；直接截中文 UTF-8 可能破坏编码 |
| 多字节文字 | `mb_strlen`、`mb_substr`、`mb_str_split` | 需要 mbstring，明确 `'UTF-8'`；组合字形可能需 intl 的 grapheme 系列 |
| 分割与拼接 | `explode(',', 'a,b', 2)`、`implode('-', ['a','b'])` | explode 是字面分隔；空分隔符抛 ValueError；不是完整 CSV 解析 |
| 固定块拆分 | `str_split('abcd', 2)` | 按字节拆为 `['ab','cd']` |
| 修剪 | `trim($s)`、`ltrim($s)`、`rtrim($s)` / `chop($s)` | 删除两端指定字符集合，不是删除一个完整前后缀 |
| 替换 | `str_replace`、`strtr` | replace 可通过第4参得到次数；strtr 的映射数组优先较长键，不再处理已替换部分 |
| 大小写 | `strtolower`、`strtoupper`、`ucfirst`、`lcfirst`、`ucwords` | ASCII/字节规则不等于所有语言的大小写；多字节文本选择 mbstring 相应函数 |
| 格式化 | `sprintf`、`number_format` | 产生字符串，显示规则不解决浮点计算误差 |
| 填充/重复/折行 | `str_pad`、`str_repeat`、`wordwrap` | 按指定宽度/次数构造文本，确认字节与显示宽度差异 |

<!-- reference-case: {"id":"php-text-json","stdout":"int(0)\nbool(true)\n6\n&lt;b&gt;Ada&lt;/b&gt;\ninvalid json\n"} -->
```php
<?php
declare(strict_types=1);
$position = strpos('abc', 'a');
var_dump($position, $position !== false);
echo strlen('中文'), PHP_EOL;
echo htmlspecialchars('<b>Ada</b>', ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'), PHP_EOL;
try {
    json_decode('{broken}', true, flags: JSON_THROW_ON_ERROR);
} catch (JsonException $error) {
    echo 'invalid json', PHP_EOL;
}
```

PHP 文件本身保存为 UTF-8 时，“中文”占 6 字节。`htmlspecialchars` 用于 HTML 文本或正确加引号的普通 HTML 属性值；它不替代 JavaScript、URL、CSS、SQL 各自的处理规则。`strip_tags` 只是剥离部分标签，即使允许 `<a>` 也不会移除其危险属性，不能当富文本安全过滤器。契约见 [htmlspecialchars](https://www.php.net/manual/en/function.htmlspecialchars.php) 与 [strip_tags](https://www.php.net/manual/en/function.strip-tags.php)。

## 3. 验证、JSON 和类型：解析后仍要检查形状

`json_encode($data, JSON_THROW_ON_ERROR)` 与 `json_decode($raw, true, flags: JSON_THROW_ON_ERROR)` 把 JSON 错误变成异常；true 参数将 JSON 对象解析为关联数组。合法 JSON 可以是 null、数字、字符串或列表，所以成功解析不等于“具备 name 字段的对象”。再用 `is_array`、`array_key_exists`、`is_string` 等检查业务要求。

`filter_var($raw, FILTER_VALIDATE_INT)` 成功返回整数，失败返回 false；合法的整数 0 不应被 `if (!$value)` 拒绝。`is_numeric` 接受数字字符串，`is_int` 判断值本身是否为整数；二者用途不同。`get_debug_type` 用于诊断类型，`var_dump` 用于开发观察，不应直接暴露到生产响应。

`strict_types=1` 主要控制调用的标量类型转换，并不验证数组的字段结构。直接从严格文件调用许多接受标量的内置函数时会遵循严格规则，但由内部函数发起的回调调用等存在专门规则；不能概括成“全部内置函数与用户函数一视同仁”。此外 int 可传给 float 形参。详细边界见[类型声明官方文档](https://www.php.net/manual/en/language.types.declarations.php)。

## 4. 日期时间：固定实验输入，明确时区

`DateTimeImmutable` 的修改方法返回新对象；`DateTime` 则可能原地修改。记录某次事件用明确的时刻，生日只需要日期，不能因为它们都能 format 就随意互换。解析相对时间的 strtotime 适合明确上下文，外部日期表单更适合确定格式与合法性检查。

<!-- reference-case: {"id":"php-date","stdout":"2026-09-10 12:00 +08:00\n2026-09-13 18:00 +08:00\nbool(false)\n"} -->
```php
<?php
declare(strict_types=1);
$start = new DateTimeImmutable('2026-09-10 12:00:00', new DateTimeZone('Asia/Shanghai'));
$due = $start->modify('+3 days')->setTime(18, 0);
echo $start->format('Y-m-d H:i P'), PHP_EOL;
echo $due->format('Y-m-d H:i P'), PHP_EOL;
var_dump(checkdate(2, 30, 2026));
```

原时间保持不变，截止日为 9 月 13 日，2 月 30 日被拒绝。`DateTimeImmutable::createFromFormat` 对某些越界分量会产生警告并归一化，严谨验证要查看 `getLastErrors()`，不能只判断是否返回对象。

| 函数 | 作用与单位 | 失败/限制 |
|---|---|---|
| `time`、`date` | 秒级 Unix 时间戳、按默认时区格式化 | date 输出取决于时区设置 |
| `microtime(true)` | 浮点秒 | 不是单调耗时计时器；测时长优先 `hrtime(true)` 纳秒计数 |
| `mktime` | 从本地日历分量构造时间戳 | 会按时区和归一化规则处理分量，不是严格日期验证 |
| `strtotime` | 解析英文时间描述为时间戳 | 失败 false；相对描述依赖基准时间 |
| `date_parse`、`checkdate` | 解析分量/检查月日年 | 解析结果要检查 errors/warnings；checkdate 不处理时区 |

## 5. 数学与随机：算术模型先于格式化

`abs` 求绝对值；`min`/`max` 从多个参数或非空数组取极值；`floor`/`ceil` 返回向下/向上取整的浮点值；`intdiv(7, 2)` 返回整数 3，除零抛 DivisionByZeroError。`round` 需要明确精度和舍入模式，不能消除整个浮点计算链的误差。

金额可使用定义好币种与最小单位的整数，或安装 BCMath/适当十进制库。`random_int(1, 6)` 两端都包含，`random_bytes(16)` 返回二进制字节，可用 bin2hex 转成文本。安全随机源失败会抛异常，不应悄悄退回 rand/mt_rand。普通仿真与安全令牌的需求不同。

## 6. 文件：空内容与失败不同

| 操作 | 返回/副作用 | 需要检查 |
|---|---|---|
| `file_get_contents` | 字符串或 false | 空字符串、字符串 `'0'` 均为成功；大文件不要无限整体读取 |
| `file_put_contents` | 写入字节数或 false，默认覆盖 | 0 字节也可成功；LOCK_EX 不保护此前的读改写过程 |
| `fopen` / `fgets` / `fclose` | 流资源、行或 false、关闭结果 | fopen 失败；读取失败与 EOF；finally 关闭 |
| `file_exists` / `is_file` / `is_dir` | 检查当前状态 | 检查与后续操作间状态仍会变，最终操作的失败也需处理 |
| `mkdir` / `unlink` | 创建目录/删除文件，bool | 权限、已存在、路径目标；不接受未限制的外部路径 |
| `pathinfo` / `basename` / `dirname` | 文本路径信息 | 不验证目标存在，也不构成目录穿越防护 |
| `scandir` | 文件名数组或 false | 通常包含 `.` 与 `..`，读取失败会发出警告 |

<!-- reference-case: {"id":"php-file","stdout":"int(1)\nstring(1) \"0\"\nbool(true)\n"} -->
```php
<?php
declare(strict_types=1);
$path = tempnam(sys_get_temp_dir(), 'reference-');
if ($path === false) {
    throw new RuntimeException('cannot create temporary file');
}
try {
    $written = file_put_contents($path, '0', LOCK_EX);
    if ($written === false) throw new RuntimeException('write failed');
    $content = file_get_contents($path);
    if ($content === false) throw new RuntimeException('read failed');
    var_dump($written, $content, $content !== false);
} finally {
    if (!unlink($path)) throw new RuntimeException('cleanup failed');
}
```

结果为 1 字节、字符串 `"0"`、true。这里没有全局错误处理器，文件函数的 warning 与 false 两种信号都保留；若工程把 warning 转成 ErrorException，应按工程约定处理，不能假设每个函数都只通过异常失败。此实验只写自己创建的临时文件；删除失败会明确报错。文件契约见 [file_get_contents](https://www.php.net/manual/en/function.file-get-contents.php) 与 [file_put_contents](https://www.php.net/manual/en/function.file-put-contents.php)。

## 7. 验收与后续学习

逐个执行 5 个脚本并对照输出，再完成三个改动：把合法输入改为 0 并保持验证成功；解释 filter 后 JSON 为什么可能变成对象；故意传入损坏 JSON 并获得明确失败。练习结果应包含正常、空值和失败分支，而非只有“程序没有报错”。

进一步学习[数组操作](./05-arrays-patterns.md)、[标准库与 SPL](../library-guides/01-standard-library-spl.md)、[Composer 生态](../library-guides/02-composer-ecosystem.md)，最后用于[CLI 任务项目](../../basics/08-first-project.md)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
