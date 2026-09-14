# 运算符全表与优先级

> **模块**: `07-php-mastery` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

PHP 运算符速查：算术、字符串、赋值、比较、逻辑、位运算与错误控制。所有行为断言在 PHP 8.5.10 实测；比较语义细节见弱比较条目。

## 📖 分类速查

### 算术

| 运算符 | 说明 |
|--------|------|
| `+ - * /` | `/` 非整除时得 float（`7/2 === 3.5`） |
| `%` | 取模**符号跟随被除数**：`-7 % 3 === -1`，`7 % -3 === 1`（实测）；整除商用 `intdiv(7, 2) === 3`、`intdiv(-7, 2) === -3`（向零取整） |
| `**` | 幂，**右结合**：`2 ** 3 ** 2 === 512`，`(2 ** 3) ** 2 === 64`（实测） |

### 字符串

```php
$full = 'Dev' . 'Quest';          // . 拼接
echo "n: " . 1 + 2;               // "n: 3"（PHP 8 起 . 优先级低于 + -，先算 1+2 再拼接；PHP 7 结果是 2）
$name = 'PHP';
$ver  = 8.5;
echo "$name $ver";                // 简单插值：变量、数组无引号键 $arr[k]、对象属性 $o->p
echo "{$amount}00";               // 复杂插值（花括号）：$arr['k']、$o->m() 等表达式（实测均可用）
```

### 赋值与合并

```php
$a ??= $b;         // null 合并赋值：$a 为 null 时才赋值（实测：存在值时不覆盖）
$b = $x['k'] ?? 'default';   // ?? 链式安全：不存在的多维键不产生告警（实测）
$c = $opt ?: 'fallback';     // Elvis：取真值否则回退（实测 "" → fallback）
```

### 比较

`==`/`===`、`!=`/`!==`、`<=>`（太空船：小于返回 -1、等于 0、大于 1；字符串按字节比较，实测 `"a" <=> "b" === -1`）——完整规则见 **[弱比较与强比较](./13-weak-comparison.md)**。

### 逻辑

| 运算符 | 说明 |
|--------|------|
| `&&` `\|\|` `!` | 高优先级版 |
| `and` `or` `xor` | **优先级低于 `=`**：`$r = true and false;` 实测 `$r === true`；`$s = false or true;` 实测 `$s === false` |

### 位运算

```php
var_dump(5 & 3);    // 1    AND
var_dump(5 | 3);    // 7    OR
var_dump(5 ^ 3);    // 6    XOR
var_dump(~5);       // -6   NOT
var_dump(1 << 4);   // 16   左移
var_dump(256 >> 4); // 16   右移
```

### 错误控制 @

```php
$value = @file_get_contents('/maybe/missing');
```

- @ 抑制该表达式产生的诊断信息；自定义 `set_error_handler` 仍会被调用（php.net 明确说明），错误可通过 `error_get_last()` 取回。
- **PHP 8.0 起致命错误不再被 @ 吞掉**：`@unknown_function()` 依旧 Fatal（实测退出码 255）；php.net 原文："Prior to PHP 8.0.0, it was possible for the @ operator to disable critical errors that will terminate script execution."
- PHP 8.0 起自定义错误处理器内 `error_reporting()` 在 @ 场景不再返回 0，而是返回致命级别位掩码（`E_ERROR|E_CORE_ERROR|E_COMPILE_ERROR|E_USER_ERROR|E_RECOVERABLE_ERROR|E_PARSE`）。

## 📖 优先级速查（高 → 低）

```
**                （右结合）
++ -- ~ (int)... instanceof
!
* / %
+ -
<< >>
.                 （8.0 起从 + - 同级降到其下）
< <= > >=
== != === !== <=>
&
^
|
&&
||
??
? :               （8.0 起嵌套必须加括号：未加括号的 a ? b : c ? d : e 是不可捕获的编译错误，实测 Fatal）
= += -= ... ??=
and
xor
or                （最低，低于 =）
```

## ⚠️ 常见陷阱

- ❌ **`$result = getVal() or die('failed');` 后以为 `$result` 是布尔**：赋值先发生，`or` 只影响整条语句的短路。
- ✅ 显式写：`$result = getVal(); if ($result === false) { ... }`；避免 `or die` 风格。
- ❌ **`"合计: " . $a + $b`**：PHP 8 下语义变为拼接 `($a + $b)`，PHP 7 下完全不同——版本间结果不可移植。
- ✅ 拼接表达式一律加括号：`"合计: " . ($a + $b)`。
- ❌ **用 `%` 处理负数当"数学取模"**：结果符号跟随被除数（`-7 % 3 === -1`），不是数学模运算。
- ✅ 需要非负结果用 `$a % $b + $b` 或明确的规范化逻辑。
- ❌ **`@` 当异常防护网**：它只压诊断，压不住异常与致命错误，还会掩盖真实问题。
- ✅ 用 try/catch 与明确的错误分支；@ 仅限第三方库遗留告警等确需静音的窄场景。
- ❌ **`$x = 1 ? 2 : 3 ? 4 : 5;` 不加括号**：8.0 起是编译期 Fatal，try/catch 都包不住。
- ✅ 永远写全括号：`$x = (1 ? 2 : 3) ? 4 : 5;`。
- ❌ **字符串插值里写 `"$arr['k']"` 或 `${var}`**：前者语法错误，后者已弃用。
- ✅ 简单键写 `"$arr[k]"`，复杂表达式写 `"{$arr['k']}"`。

## 🔗 相关条目

- 📄 **[弱比较与强比较](./13-weak-comparison.md)** — 比较运算符的完整类型规则
- 📄 **[值语义与引用](./14-references-value-semantics.md)** — `=&` 与赋值语义
- 📄 **[PHP 关键字详解](./01-php-keywords.md)** — `and`/`or` 等保留字
- 🌐 **[php.net: 运算符优先级](https://www.php.net/manual/zh/language.operators.precedence.php)** — 官方完整优先级表

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
