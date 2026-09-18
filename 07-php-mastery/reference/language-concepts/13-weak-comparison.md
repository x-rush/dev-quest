# 弱比较与强比较全表（== / ===）

> **模块**: `07-php-mastery` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

`==`（弱比较/松散比较）在比较前做类型转换，只看"转换后的值"；`===`（强比较/严格比较）要求**类型与值都相同**。PHP 8.0 重写了字符串↔数字的比较规则，消除了 PHP 7 大量反直觉结果。本表给出 PHP 8.x 比较结果供核对。

## 一、标量互比矩阵（`==`，PHP 8.5 预期）

| `==` | `null` | `0` | `"0"` | `""` | `false` | `[]` | `"a"` |
|---------|--------|-----|-------|------|---------|------|-------|
| **`null`** | ✔ | ✔ | ✘ | ✔ | ✔ | ✔ | ✘ |
| **`0`** | ✔ | ✔ | ✔ | ✘ | ✔ | ✘ | ✘ |
| **`"0"`** | ✘ | ✔ | ✔ | ✘ | ✔ | ✘ | ✘ |
| **`""`** | ✔ | ✘ | ✘ | ✔ | ✔ | ✘ | ✘ |
| **`false`** | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✘ |
| **`[]`** | ✔ | ✘ | ✘ | ✘ | ✔ | ✔ | ✘ |
| **`"a"`** | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | ✔ |

（✔ = true，✘ = false。规则按类型组合有优先顺序：null 与字符串比较时先转为空字符串，因此 null == "0" 为 false；bool 参与时通常按布尔值比较。数组的比较规则不能覆盖前面更优先的 bool/null 特例。参见本页官方比较文档。）

`===` 版本：对本表列出的普通值，除 `(x === x)` 自身（如 `[] === []`、`null === null`）外，**跨类型全为 false**；同类型还要值相同，如 `[1] === [1.0]` 为 false（int ≠ float）。

## 二、字符串 ↔ 数字比较规则（PHP 8 起语义）

PHP 8 字符串与数字规则摘要：**两个操作数都是 numeric string，或一方是数字另一方是 numeric string，则按数值比较；否则（string 非数字时）按字符串比较。** PHP 7 及之前会把 string 转成数字再比，因此文档给出的经典对照：

```php
var_dump(0 == "a");    // PHP 7: true（"a" 被转成 0）  PHP 8: false
var_dump("1" == "01"); // 两个版本都 true（都是 numeric string，1 == 1）
var_dump("10" == "1e1"); // true
var_dump(100 == "1e2");  // true

switch ("a") {          // switch 同样适用上述规则
case 0:  echo "0"; break;  // PHP 7 输出 "0"（"a" == 0）
case "a": echo "a"; break; // PHP 8 输出 "a"
}
```

PHP 8.5 预期补充（numeric string 判定允许首尾空白，不允许 `0x` 十六进制与下划线）：

| 表达式 | 结果 | 原因 |
|--------|------|------|
| `" 1" == "1"` / `"1 " == "1"` | true | 首尾空白均允许 |
| `"0x1A" == "26"` | false | 十六进制字符串不是 numeric string |
| `"1_0" == "10"` | false | 下划线分隔符仅限字面量书写 |
| `"10" == "10.0"` / `"100" == "1e2"` | true | 都是 numeric string，数值比较 |
| `42 == "42abc"` / `"10 apples" == "10"` | false | 非数字串按字符串比较 |
| `"abc" < 0` / `"abc" > 0` | false / true | `"abc"` 与 `"0"` 按字符串比，`"0" < "abc"` |
| `"10" < "9"` | false | 两个 numeric string → 按数值比（10 < 9 不成立） |
| `"A" < "a"` | true | 按 ASCII 字节比较 |
| `"abc" == 0` | false | PHP 8 核心修正点 |

## 三、switch 与 match 的比较语义

| | `switch` | `match`（8.0+） |
|---|---------|----------------|
| 比较方式 | **弱比较 `==`**（受第二节全部规则影响） | **强比较 `===`** |
| 类型转换 | 有（见上表陷阱） | 无 |
| 未命中 | 落入 `default`（无则跳过） | 抛 `UnhandledMatchError` |
| 分支结构 | 顺序穿透（需 `break`） | 单表达式，无穿透 |

```php
$v = 0;
switch ($v) { case "a": /* PHP 8 不再命中 */ case 0: break; }  // 命中 case 0
switch (null) { case 0: }      // null == 0 → 命中
echo match ($v) { "a" => 'x', 0 => 'y' };  // 'y'（"a" === 0 为 false）
```

## 四、in_array / array_search 松散比较陷阱

默认使用弱比较，输入来自用户时是重灾区（PHP 8.5 预期）：

```php
in_array(0, ["a", "b"]);        // false（PHP 7 为 true——0 == "a"）
in_array("", [0]);              // false（PHP 8 起 "" == 0 为 false，PHP 7 为 true）
in_array(null, [false]);        // true！null == false
array_search(0, ["a", "b", "c"]); // false（PHP 7 返回 0）
array_search("a", ["a", "b"]);  // 返回 0——索引 0 本身是假值！
```

## 💡 正确姿势

```php
// 白名单 + 强比较
$allowed = ['a', 'b'];
$page = $_GET['page'] ?? '';
if (in_array($page, $allowed, true)) { /* ... */ }   // 第三参 true 启用 ===

// array_search 返回值要显式区分 false 与索引 0
$idx = array_search('x', $list, true);
if ($idx !== false) { /* 找到 */ }

// 状态码、ID 等一律 ===
if ($input === 0 || $input === '0') { /* 业务明确允许这两种零 */ }
```

## ⚠️ 常见陷阱

- ❌ **`if ($x == '0')` 判断"是否为零"**：`"0"` 弱等于 `false`，`null == 0`、`null == ""` 等链式意外无法穷举。
- ✅ 判断零：`if ($x === 0 || $x === '0')`，按业务显式列出。
- ❌ **`switch` 匹配用户输入**：`switch ($_GET['type'])` 里 `case 0:` 可能被 false、null 等弱命中；PHP 8 中空串不再等于数字 0。
- ✅ 分支逻辑用 `match`（天然 `===`），或先强校验类型。
- ❌ **用 `if (array_search(...))` 判断是否找到**：索引 `0` 是假值，会误判"未找到"。
- ✅ `!== false` 判断。
- ❌ **把 `"0.0"` 当假值**：只有 `"0"` 是假字符串，`"0.0"`、`"false"` 均为真值。

<!-- full-library-explanation -->
## 严格比较之前还要正确解析输入

前置是类型、布尔值和数组。强制转换不是验证：把 'abc' 转为 int 会丢失原始信息，之后再 === 0 也无法知道输入原来不是零。先验证原始类型、格式和范围，再把已验证的值转为内部类型，最后做业务比较。

松散相等不具备你可能期待的传递性：0 == null 为 true，0 == '0' 为 true，但 null == '0' 为 false。不要用矩阵替代输入契约。安全令牌等还应使用对应的比较函数，例如 hash_equals 要比较已确认类型和格式的秘密值，而不是先弱转换。

**练习**：对 null、false、0、'0'、'00'、'abc' 分别应用直接严格判断和先转 int 再判断，记录哪些信息在转换时丢失。array_search 找到第一个元素会返回索引 0，要与 false 严格区分；若合法数据本身包含 null，isset 与 array_key_exists 的结果也不同。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

## 🔗 相关条目

- 📄 **[控制流](./04-control-flow.md)** — switch/match 语法与使用场景
- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — 联合类型下的类型判定
- 📄 **[数组操作模式](./05-arrays-patterns.md)** — in_array 的集合化替代（isset 翻转）
- 🌐 **[php.net: 比较运算符](https://www.php.net/manual/zh/language.operators.comparison.php)** — 官方比较规则与 PHP 7/8 对照表

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
