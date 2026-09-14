# 常用内置函数分类全表

## 概述

PHP 内置函数超过千个，本文按"高频 + 现代"原则收录数组、字符串、日期、数学与文件五类核心函数。所有函数均在严格类型模式下可用；标注 ⚠️ 的行为在 PHP 8 中有变化或易踩坑。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#内置函数` `#数组` `#字符串` `#日期` `#速查` |
| **更新日期** | `2026年9月` |

## 1. 数组函数

### 创建与查询

| 函数 | 签名要点 | 说明 |
|------|---------|------|
| `range()` | `range(1, 5)` / `range('a', 'e')` | 生成等差序列 |
| `array_fill()` | `array_fill(0, 3, 'x')` | 指定起始索引与数量填充 |
| `array_keys()` / `array_values()` | — | 取键列表 / 重索引取值列表 |
| `in_array()` | `in_array($v, $arr, true)` | ⚠️ 生产代码必须传第三参严格比较 |
| `array_search()` | 返回键名，找不到返回 `false` | ⚠️ 键名为 `0` 时与 `false` 弱比较混淆，用 `!== false` 判断 |
| `array_key_exists()` | — | 键存在判断（值为 null 也返回 true） |
| `array_slice()` | `array_slice($arr, 1, 2, true)` | 切片，第四参保留原键 |
| `array_column()` | `array_column($rows, 'name', 'id')` | 从二维数组提取列，第三参作键 |
| `array_combine()` | `array_combine($keys, $vals)` | 键数组 + 值数组合成映射 |

### 增删与合并

```php
$stack = [1, 2];
array_push($stack, 3);          // 尾部追加，等价 $stack[] = 3
array_pop($stack);              // 尾部弹出
array_unshift($stack, 0);       // 头部插入
array_shift($stack);            // 头部弹出

$merged = [...[1, 2], ...[2, 3]];           // 展开合并：[1, 2, 2, 3]
$mapA = [...['a' => 1], ...['a' => 2]];     // ⚠️ 字符串键后者覆盖，数字键追加
array_splice($merged, 1, 2, ['x']);          // 原地替换切片
```

### 过滤、变换与归约（详见 [数组操作模式](./05-arrays-patterns.md)）

| 函数 | 说明 |
|------|------|
| `array_map()` | 逐元素变换；`array_map(null, $a, $b)` 可实现多数组按位合并 |
| `array_filter()` | 默认剔除弱 false 值；`ARRAY_FILTER_USE_KEY` 按键过滤 |
| `array_reduce()` | 归约为单值 |
| `array_unique()` | 去重；⚠️ 保留原键，需再 `array_values()` |
| `array_reverse()` | 反转 |
| `usort()` / `uasort()` / `uksort()` | 自定义排序（⚠️ 8.0 起比较函数不对称返回值会抛异常） |
| `sort()` / `rsort()` / `asort()` / `ksort()` | 基础排序；8.0 起排序参数 `SORT_REGULAR` 语义更严格 |

```php
// PHP 8.4 新增：array_find / array_any / array_all
$users = [['age' => 15], ['age' => 22]];
$adult = array_find($users, fn(array $u): bool => $u['age'] >= 18);   // ['age'=>22]
var_dump(array_all($users, fn(array $u): bool => $u['age'] > 0));     // true
var_dump(array_any($users, fn(array $u): bool => $u['age'] > 21));    // true
```

## 2. 字符串函数

### 查找与判断（PHP 8 新家族，替代 strpos 老写法）

```php
str_contains('Hello PHP', 'PHP');     // true：包含判断（8.0）
str_starts_with('v8.3.0', 'v8');      // true：前缀判断（8.0）
str_ends_with('a.tar.gz', '.gz');     // true：后缀判断（8.0）
str_contains('abc', '');              // true（8.0 起）：空串恒为包含
```

### 截取、分割与拼接

```php
substr('现代PHP', 0, 2);             // ⚠️ 字节截取，中文用 mb_substr
mb_substr('现代PHP', 0, 2);           // '现代'：按字符处理
str_split('abcdef', 2);               // ['ab','cd','ef']
mb_str_split('现代PHP', 2);           // 多字节安全分割
explode(',', 'a,b,c', 2);             // ['a', 'b,c'] 第三参限制段数
implode('-', ['a', 'b']);             // 'a-b'（别名 join）
sprintf('%s 得分 %.1f', 'Ada', 92.45); // 'Ada 得分 92.5'
str_repeat('=-', 3);                  // '=-=-=-'
str_pad('7', 3, '0', STR_PAD_LEFT);   // '007'
wordwrap($long, 20, PHP_EOL);         // 按宽度折行
```

### 清理与替换

```php
trim("  x  \n", " \t\n");             // 去两端字符，第二参指定字符集
ltrim();                              // 去左端，rtrim() 别名 chop() 去右端
str_replace(['a', 'b'], ['A', 'B'], $s);          // 批量替换
strtr($s, ['kg' => '千克', 'g' => '克']);          // ⚠️ 按"最长优先"整体映射，不回溯已替换部分
str_replace('甲', '乙', $s, $count);               // 第四参接收替换次数
ucfirst(); lcfirst(); ucwords(); strtoupper(); strtolower(); mb_strtolower();
```

### 编解码与格式

```php
json_encode($data, JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
json_decode($raw, true, flags: JSON_THROW_ON_ERROR);   // true 返回数组，默认对象
number_format(1234567.891, 2, '.', ',');               // '1,234,567.89'
htmlspecialchars($html, ENT_QUOTES, 'UTF-8');          // 输出转义（防 XSS 必备）
strip_tags($html, '<p><a>');                           // 剥离标签，白名单除外
```

## 3. 日期时间函数

### DateTimeImmutable：现代首选

```php
$now = new DateTimeImmutable('now', new DateTimeZone('Asia/Shanghai'));
$due  = $now->modify('+3 days')->setTime(18, 0);   // ⚠️ Immutable：返回新对象
echo $due->format('Y-m-d H:i:s P'), PHP_EOL;       // 2026-09-13 18:00:00 +08:00
```

**⚠️ 陷阱**：`DateTime::modify()` 修改自身并返回 `$this`，链式调用在 DateTime 上是"原地改"；项目统一用 `DateTimeImmutable` 避免共享可变状态。

### 工具函数

| 函数 | 示例 | 说明 |
|------|------|------|
| `date()` | `date('Y-m-d', $ts)` | 格式化时间戳 |
| `time()` / `microtime(true)` | — | 当前秒 / 毫秒级时间戳 |
| `mktime()` | `mktime(18, 0, 0, 9, 13, 2026)` | 由分量构造时间戳 |
| `strtotime()` | `strtotime('next friday')` | ⚠️ 解析英文相对时间，非法输入返回 false |
| `date_parse()` | — | 解析为关联数组，配合 errors 校验 |
| `checkdate()` | `checkdate(2, 30, 2026)` | 校验日期合法性（false） |

### Interval 与比较

```php
$a = new DateTimeImmutable('2026-09-10');
$b = new DateTimeImmutable('2026-09-20');
$diff = $a->diff($b);                 // DateInterval
echo $diff->days, PHP_EOL;            // 10

if ($a < $b) { /* DateTime 可直接比较 */ }
echo $a->getTimestamp(), PHP_EOL;     // Unix 时间戳
```

## 4. 数学与随机

```php
abs(-5);            // 5
max(1, 2, 3);       // 3，也接受数组
min([4, 2, 9]);     // 2
var_dump(0.1 + 0.2);   // ⚠️ float(0.30000000000000004)：浮点精度问题，金额用 int 分或 BCMath
floor(4.9); ceil(4.1);
intdiv(7, 2);       // 3：整数除法，除零抛 DivisionByZeroError
random_int(1, 6);   // 密码学安全随机整数（⚠️ 不要再用 rand/mt_rand 于安全场景）
```

## 5. 文件与 JSON 实用集

```php
file_exists($p); is_file($p); is_dir($p);
file_get_contents($url);              // 读文件/URL，失败返回 false（⚠️ 需判 false）
file_put_contents($p, $data, LOCK_EX); // LOCK_EX 防并发覆盖
mkdir($dir, 0755, true);              // 第三参递归创建
unlink($p);                           // 删除文件
fopen()/fgets()/fclose();             // 大文件用流式逐行读
pathinfo('/a/b/c.txt', PATHINFO_EXTENSION);   // 'txt'
basename('/a/b/c.txt'); dirname('/a/b/c.txt'); // 'c.txt' / '/a/b'
scandir($dir);                        // 列目录（含 . 与 ..）
```

## 陷阱速查

- **严格模式同样约束内置函数**：`strict_types=1` 下 `str_contains(123, '1')` 直接抛 `TypeError`——内置函数与用户函数一视同仁，弱转换仅发生在非严格模式
- **false 歧义返回**：`strpos`/`array_search`/`file_get_contents` 失败返回 `false`，判断一律 `!== false` / `=== false`
- **多字节函数**：处理中文/Emoji 必须用 `mb_*` 家族，确保 `mbstring` 扩展已启用
- **浮点金额**：`round`/`floor` 受 IEEE 754 限制，金额计算用整数分、BCMath 或 `brick/math` 库

## 相关文档

- 📄 **[数组操作模式](./05-arrays-patterns.md)** — map/filter/reduce 组合范式
- 📄 **[Composer 生态精选](../library-guides/02-composer-ecosystem.md)** — 内置函数不够用时的标准三方替代
- 📄 **[常见错误排查](../quick-references/02-troubleshooting.md)** — 返回 false 类 bug 的排查清单
