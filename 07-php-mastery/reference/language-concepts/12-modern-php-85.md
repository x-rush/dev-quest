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

⚠️ **常见陷阱**: 钩子与 `readonly` 互斥（readonly 没有 set 时机）；有 `get` 无 `set` 的属性对外只读，但类内仍可写底层存储；构造器提升参数也能挂钩子；`get` 里再读 `$this->prop` 会递归——读写底层存储是无钩子原语。

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

⚠️ **常见陷阱**: 右侧只接受**单参数**调用——`|> str_pad(...)` 缺参不可用，需闭包包装；传字符串 `'trim'` 虽是合法 callable，但丢失静态分析，统一用 `trim(...)`；运算符优先级低于算术与比较，复杂表达式左侧加括号。

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

// RFC 3986：解析宽松，不做合法性判断
$uri = new Uri\Rfc3986\Uri('https://example.com:8080/a/b?x=1#frag');
echo $uri->getHost(), PHP_EOL;             // example.com
echo $uri->getPort(), PHP_EOL;             // 8080
echo $uri->getPath(), PHP_EOL;             // /a/b

$patched = $uri->withHost('php.net')->withPath('/downloads');
echo $patched->getUri(), PHP_EOL;          // https://php.net/downloads?x=1

// WHATWG：浏览器同款规则，非法输入直接抛异常
try {
    $url = new Uri\WhatWg\Url('not a url');
} catch (Uri\WhatWg\InvalidUrlException $e) {
    echo 'WHATWG 校验失败', PHP_EOL;
}

$url = new Uri\WhatWg\Url('https://example.com');
echo $url->withHost('example.net')->getAsciiHost(), PHP_EOL;   // example.net
```

⚠️ **常见陷阱**: 两个类都**不可变**——`with*` 返回新实例，`Rfc3986\Uri` 没有 `set*` 方法；`getPort()` 返回 `?int`（无端口或默认端口为 null）；`parse_url()` 未被移除但新代码建议迁移；非法 RFC 3986 结果在 `with*` 时抛 `Uri\InvalidUriException`，非法 WHATWG 输入在构造时抛 `Uri\WhatWg\InvalidUrlException`。

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

📌 **定义**: 常量表达式（类常量、属性默认值、注解参数等）现在允许出现**闭包、一等公民 callable、类型转换**——此前只允许标量、数组、`new` 等形态。

📖 **语法/签名**:

```php
public const X = static fn (...): T => expr;    // 8.5：闭包进常量
public const Y = self::handler(...);            // 8.5：一等公民 callable 进常量
public const int N = (int) self::RAW;           // 8.5：类型转换进常量
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

final class Retry
{
    public const callable BACKOFF = static fn (int $attempt): int => 2 ** $attempt;
    public const int MAX_ATTEMPTS = (int) '5';   // 转换后的常量
}

echo Retry::BACKOFF(3), PHP_EOL;      // 8
echo Retry::MAX_ATTEMPTS, PHP_EOL;    // 5
```

⚠️ **常见陷阱**: 常量里的闭包每次类初始化只创建一次，但**不是**纯静态——不能引用外部变量；`json_encode(...)` 等函数引用进常量后，重构改名由 IDE/静态分析接管，优于字符串 `'json_encode'`。

🔗 **相关条目**: [一等公民 callable 语法](./03-types-oop-modern.md)、[常量类型化（8.3+）](./03-types-oop-modern.md)

## 相关文档

- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — 8.0-8.4 主线特性全表
- 📄 **[PHP 快速速查表](../quick-references/01-php-cheatsheet.md)** — 本文特性的单行版
- 📄 **[高级特性教程](../../basics/07-advanced-features.md)** — 含 8.4/8.5 增量的渐进式讲解

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
