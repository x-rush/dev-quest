# PHP 8.4/8.5 增量特性

## 概述

本文是 PHP 8.4（2024-11 发布）与 PHP 8.5（2025-11-20 发布）增量特性的字典速查：属性钩子、管道运算符、URI 扩展、`#[\NoDiscard]`、`clone()` 批量覆盖、常量表达式增强等。每条按"📌 定义 → 📖 语法 → 💡 示例 → ⚠️ 陷阱"组织，供已熟悉 8.1-8.3 特性的开发者快速补课。版本基线：本模块以 8.5 为编写基线（2026-09 核实）。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#PHP8.4` `#PHP8.5` `#属性钩子` `#管道运算符` `#URI扩展` |
| **更新日期** | `2026年9月` |

## 条目 1：属性钩子 Property Hooks（8.4+）

📌 **定义**: 属性可以内联定义读写行为：`get` 钩子自定义"读取时返回什么"，`set` 钩子自定义"写入时做什么校验/变换"。省掉手写 getter/setter，且可定义**无实际存储的虚拟属性**。

📖 **语法/签名**:

```php
public Type $prop {
    get => expression;                    // 简写：表达式的值即读取结果
    set (Type $value) { $this->prop = ...; }   // 全写：$value 是入参（可省类型）
    set => expression;                    // 简写：表达式值写入底层存储
}
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

final class User
{
    public string $email {
        set (string $value) {
            if (! str_contains($value, '@')) {
                throw new ValueError('邮箱格式非法');
            }
            $this->email = strtolower($value);   // 写入底层存储
        }
    }

    public string $name { set => ucfirst(trim($value)); }   // 简写钩子

    // 虚拟属性：无底层存储，每次读取时计算
    public string $initials {
        get => mb_strtoupper(mb_substr($this->name, 0, 1));
    }
}

$u = new User();
$u->email = 'ADA@example.com';    // 触发 set：校验 + 小写化
echo $u->email, PHP_EOL;          // ada@example.com
```

⚠️ **常见陷阱**: 钩子与 `readonly` 互斥（readonly 没有 set 时机）；只有 `get` 没有 `set` 的 **backed** 属性外部仍可写——写入按默认语义落到底层存储，仅 **virtual** 属性（无底层存储）不可写（实测 8.5.10 报 `Error: Property ... is read-only`）；构造器提升参数也能挂钩子；`get` 钩子里直读 `$this->prop` 不会递归——直读底层存储是绕过钩子的原语，递归风险仅在把钩子逻辑写到会再次触发钩子的路径上。

🔗 **相关条目**: [readonly 与非对称可见性](./03-types-oop-modern.md)、[类型系统全表](./03-types-oop-modern.md)

## 条目 2：`new` 直接链式调用（8.4+）

📌 **定义**: `new Foo()->method()` 不再需要外层括号——new 表达式可以直接接 `->` 链式操作。

📖 **语法/签名**: `new ClassName(...)->method(...)`（此前必须 `(new ClassName(...))->method(...)`）

💡 **示例**:

```php
<?php

declare(strict_types=1);

$rule = new Validator()
    ->required('title')
    ->max('title', 120);        // 8.4+：无需 (new Validator())->required(...)

$accept = new Request()->header('accept', 'application/json');
```

⚠️ **常见陷阱**: 只是语法糖，语义与加括号完全一致；静态分析器与格式化工具需支持 8.4 语法（PHPStan/Pint 近年版本均已支持）。

🔗 **相关条目**: [类型系统与现代 OOP](./03-types-oop-modern.md)

## 条目 3：管道运算符 `|>`（8.5+）

📌 **定义**: `$value |> callable` 把左侧值作为**唯一实参**传给右侧可调用值，返回其结果。链式管道从左到右阅读，取代"嵌套调用从内往外读"与中间变量。

📖 **语法/签名**: `$x |> strlen(...)` ——右侧必须求值为"单参数可调用"：一等公民 callable 语法（推荐）、闭包、可调用对象均可。

💡 **示例**:

```php
<?php

declare(strict_types=1);

$title = '  modern php  ';

// 嵌套写法（从内往外读）
echo mb_strtoupper(trim($title)), PHP_EOL;

// 管道写法（从左往右读）
$clean = $title |> trim(...) |> mb_strtoupper(...);
echo $clean, PHP_EOL;                    // MODERN PHP

// 多参数函数用一等公民语法固化参数，或用闭包包装
$pad = 'php' |> (static fn (string $s): string => str_pad($s, 8, '_', STR_PAD_BOTH));
echo $pad, PHP_EOL;                      // __php___
```

⚠️ **常见陷阱**: 右侧只接受**单参数**调用——`|> str_pad(...)` 缺参不可用，需闭包包装；传字符串 `'trim'` 虽是合法 callable，但丢失静态分析，统一用 `trim(...)`；运算符优先级低于算术运算符、高于比较运算符（实测 `1 |> strlen(...) == "1"` 按 `(1 |> strlen(...)) == "1"` 结合），复杂表达式左侧加括号。

🔗 **相关条目**: [一等公民 callable 语法](./03-types-oop-modern.md)、[数组操作模式](./05-arrays-patterns.md)

## 条目 4：URI 扩展（8.5+）

📌 **定义**: 始终启用的内置 `uri` 扩展，提供两套不可变 URI 类型：`Uri\Rfc3986\Uri`（按 RFC 3986 宽松解析）与 `Uri\WhatWg\Url`（按 WHATWG URL 标准，与浏览器行为一致，构造即校验）。取代 `parse_url()` 的碎片化数组与歧义行为。

📖 **语法/签名**:

```php
// 两个类都是 final readonly，修改方法 with* 返回新实例
new Uri\Rfc3986\Uri(string $uri, ?Uri\Rfc3986\Uri $baseUrl = null)
new Uri\WhatWg\Url(string $uri, ?Uri\WhatWg\Url $baseUrl = null, array &$softErrors = [])

// Uri\Rfc3986\Uri：getter 与 with*（返回新实例）
getScheme/getUserInfo/getUsername/getPassword/getHost/getPort/getPath/getQuery/getFragment(): ?string
withScheme/withUserInfo/withUsername/withPassword/withHost/withPort/withPath/withQuery/withFragment(string $v): static

// Uri\WhatWg\Url：无 getUserInfo/getHost——用户信息用 getUsername/getPassword，
// 主机用 getAsciiHost/getUnicodeHost，其余 getter/with* 同名
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

// RFC 3986：构造时即校验，非法 URI 抛 Uri\InvalidUriException
$uri = new Uri\Rfc3986\Uri('https://example.com:8080/a/b?x=1#frag');
echo $uri->getHost(), PHP_EOL;             // example.com
echo $uri->getPort(), PHP_EOL;             // 8080
echo $uri->getPath(), PHP_EOL;             // /a/b

$patched = $uri->withHost('php.net')->withPath('/downloads');
echo $patched->toString(), PHP_EOL;        // https://php.net:8080/downloads?x=1#frag（端口/query/fragment 均保留）

// WHATWG：浏览器同款规则，非法输入直接抛异常
try {
    $url = new Uri\WhatWg\Url('not a url');
} catch (Uri\WhatWg\InvalidUrlException $e) {
    echo 'WHATWG 校验失败', PHP_EOL;
}

$url = new Uri\WhatWg\Url('https://example.com');
echo $url->withHost('example.net')->getAsciiHost(), PHP_EOL;   // example.net
```

⚠️ **常见陷阱**: 两个类都**不可变**——`with*` 返回新实例，`Rfc3986\Uri` 没有 `set*` 方法；`getPort()` 返回 `?int`（无端口或默认端口为 null）；取完整字符串用 `->toString()`——**没有** `getUri()` 方法，也未实现 `__toString`（对象直接进字符串上下文抛 Error，实测 8.5.10）；`parse_url()` 未被移除但新代码建议迁移；两个类的构造函数都会校验输入：非法 RFC 3986 URI 在**构造时**即抛 `Uri\InvalidUriException`，非法 WHATWG 输入在构造时抛 `Uri\WhatWg\InvalidUrlException`。

🔗 **相关条目**: [PHP 快速速查表](../quick-references/01-php-cheatsheet.md)

## 条目 5：`#[\NoDiscard]` 与 `(void)` 转换（8.5+）

📌 **定义**: `#[\NoDiscard]` 标注"返回值必须被消费"的函数：裸调用会触发警告；`(void)` 转换则显式声明"我故意不要返回值"。两者配合把"忘了用返回值"从静默 bug 变成可检测信号。

📖 **语法/签名**:

```php
#[\NoDiscard]
function mustConsume(): array { ... }

(void) mustConsume();    // 显式忽略返回值：不警告
mustConsume();           // ⚠️ Warning: the return value is expected to be consumed
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

final class Cart
{
    private array $items = [];

    #[\NoDiscard]
    public function add(string $sku): array      // 返回"加入后的完整清单"，约定必须使用
    {
        $this->items[] = $sku;
        return $this->items;
    }
}

$cart = new Cart();
$summary = $cart->add('PHP-BOOK');    // ✅ 消费返回值

(void) $cart->add('MUG');             // ✅ 明确声明"本次不需要清单"

// $cart->add('MUG');                  // ⚠️ 提示返回值未被消费
```

⚠️ **常见陷阱**: 这是对**调用方**的检查，不改变函数行为；多数内部小函数不需要它——用在"返回值承载核心语义"的 API（不可变容器、链式构建器）最合适。

🔗 **相关条目**: [类型系统全表](./03-types-oop-modern.md)

## 条目 6：`clone()` 批量覆盖（clone with，8.5+）

📌 **定义**: 8.5 给 `clone` 增加函数形式 `clone($obj, ['prop' => value])`，在克隆时批量覆盖属性——为 `readonly` 类实现 with-er（不可变值对象"修改即新对象"）模式提供了语言级支持（RFC clone_with_v2）。

📖 **语法/签名**:

```php
clone($object, array $properties): object    // 8.5+：克隆时批量覆盖
(clone($object, [...]))->prop                // 返回值链式访问需括号包裹
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

final class Invoice
{
    public function __construct(
        public readonly string $no,
        public readonly int $cents,
    ) {}

    // with-er 模式：类内方法封装克隆覆盖
    public function withCents(int $cents): self
    {
        return clone($this, ['cents' => $cents]);
    }
}

$origin = new Invoice('INV-1', 1000);

// 类内（经方法）：readonly 覆盖成功
$b = $origin->withCents(2000);

// 直接覆盖非 readonly 属性：任意作用域可用
class Point { public function __construct(public int $x) {} }
$p2 = clone(new Point(1), ['x' => 9]);

echo $b->no, '/', $b->cents, PHP_EOL;    // INV-1/2000（$origin 不受影响）
```

⚠️ **常见陷阱**: 覆盖属性必须**当前作用域可见**——`readonly` 提升属性自 8.4 起默认 `protected(set)`，在全局作用域 `clone($obj, [...])` 覆盖它会 Fatal error，须封装到类方法内；**不存在 `clone($obj)->with()` 链式语法**（实测 8.5.10 为 parse error），with-er 模式靠类内 `withXxx()` 方法实现；`clone(...)` 返回值直接接 `->` 会解析错误，需括号 `((clone($obj, [...]))->prop)`；`__clone()` 魔术方法照常触发。

🔗 **相关条目**: [readonly 属性](./03-types-oop-modern.md)、[教程：函数与 OOP](../../basics/04-functions-oop.md)

## 条目 7：常量表达式增强（8.5+）

📌 **定义**: 8.5 扩大了常量表达式（类常量、属性默认值、注解参数等）的允许范围：**一等公民 callable 引用**、**类型转换**与 **static 闭包**（`static function () {...}` 写法）都可以进入常量；但 **`fn` 箭头函数不允许**——`public const F = fn () => ...;` 实测 8.5.10 编译期直接 Fatal，这正是本条目最需要记住的边界。

📖 **语法/签名**:

```php
public const TRIM = trim(...);            // 8.5 ✅：一等公民 callable 引用进常量
public const int N = (int) self::RAW;     // 8.5 ✅：类型转换进常量
public const G = static function (): int { return 1; };   // 8.5 ✅：static 闭包进常量
public const F = fn () => 1;              // ❌ Fatal: Constant expression contains invalid operations
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

final class Retry
{
    public const POW = pow(...);                     // callable 引用进常量
    public const string RAW = '5';
    public const int MAX_ATTEMPTS = (int) self::RAW; // 类型转换进常量
}

var_dump((Retry::POW)(2, 3));     // int(8)：调用常量里的 callable 必须包一层括号
var_dump(Retry::MAX_ATTEMPTS);    // int(5)
```

⚠️ **常见陷阱**（以下边界均实测 8.5.10）:

- **`fn` 箭头函数进不了常量**：`public const BACKOFF = fn (int $a): int => 2 ** $a;`（`static fn` 同理）报 `Fatal error: Constant expression contains invalid operations`——8.5 允许进常量的是 callable **引用**（`trim(...)`、`Foo::bar(...)`）、类型转换与 **static 闭包**（`static function () {...}`），`fn` 箭头函数不在其列。想在常量里存"行为"，用 static 闭包或函数引用，而不是箭头函数。
- **直接调用常量里的 callable 必须包一层括号**：`Retry::POW(2, 3)` 会被解析为静态方法调用，抛 `Error: Call to undefined method Retry::POW()`；正确写法是 `(Retry::POW)(2, 3)`。管道运算符右侧是个例外——`$x |> Retry::POW` 与 `$x |> (Retry::POW)` 实测均可用。
- **`callable` 不能作常量的类型标注**：`public const callable C = ...` 报 `Fatal error: Class constant cannot have type callable`——存 callable 的常量不要写类型。
- **注解参数同规则**：`#[Sanitizer(trim(...))]` 可用，`#[Sanitizer(fn () => ...)]` 同样 Fatal（见[反射与属性注解](./08-reflection-attributes.md)）。
- 收益：`pow(...)` 进常量后，函数改名由 IDE/静态分析全程追踪，优于字符串 `'pow'`。

🔗 **相关条目**: [一等公民 callable 语法](./03-types-oop-modern.md)、[常量类型化（8.3+）](./03-types-oop-modern.md)

## 相关文档

- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — 8.0-8.4 主线特性全表
- 📄 **[PHP 快速速查表](../quick-references/01-php-cheatsheet.md)** — 本文特性的单行版
- 📄 **[高级特性教程](../../basics/07-advanced-features.md)** — 含 8.4/8.5 增量的渐进式讲解

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
