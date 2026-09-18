# 函数与面向对象 - 构造器属性提升时代

## 先理解，再动手

类封装状态与行为，构造器建立有效初始状态。属性提升减少声明重复，不减少验证需求。

**本节自测**：创建要求标题非空的 Task，对正常与空白标题分别构造。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

非法对象应在明确边界被拒绝；public 属性或简短语法不会自动保证业务规则。

</details>

> **文档简介**: 系统学习 PHP 函数（含箭头函数、命名参数）与现代 OOP（构造器属性提升、只读属性、接口与抽象类）
>
> **目标读者**: 已掌握变量与类型系统、准备编写结构化代码的 PHP 初学者
>
> **前置知识**: 完成 [变量与类型系统](./03-variables-types.md)，理解类型声明

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#函数` `#面向对象` `#构造器提升` `#只读属性` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 编写普通函数、箭头函数并正确处理参数
- ✅ 定义类，使用 PHP 8 构造器属性提升写出简洁的 DTO
- ✅ 区分接口与抽象类的适用场景
- ✅ 理解只读属性与 `clone` 修饰符（8.3 新特性）

## 1. 函数：四种形态

### 常规函数

```php
<?php

declare(strict_types=1);

function formatPrice(int|float $price, string $currency = 'CNY'): string
{
    return number_format($price, 2) . ' ' . $currency;
}

echo formatPrice(1234.5), PHP_EOL;                     // 1,234.50 CNY
echo formatPrice(price: 99, currency: 'USD'), PHP_EOL; // 命名参数（8.0+）：跳过顺序直接指定
```

### 箭头函数（Arrow Function，7.4+）

```php
$nums = [1, 2, 3, 4];

// 自动按值捕获外部变量 $factor，无需 use
$factor = 10;
$doubled = array_map(fn(int $n): int => $n * $factor, $nums);
// [10, 20, 30, 40]
```

**`fn` vs `function`**：箭头函数只能写单个表达式、自动捕获外部变量（按值）；闭包 `function` 可以写多语句、需要显式 `use` 声明捕获。

### 可变参数

```php
function sum(int ...$numbers): int
{
    return array_sum($numbers);
}

echo sum(1, 2, 3), PHP_EOL;   // 6

// 参数展开：把数组拆开传入
echo sum(...[4, 5, 6]), PHP_EOL;  // 15
```

### 函数引用的一等公民写法

```php
$handler = strlen(...);              // PHP 8.1+ 一等公民 callable 语法
echo $handler('hello'), PHP_EOL;     // 5
```

一等公民 callable 语法的完整说明见 [`../reference/language-concepts/03-types-oop-modern.md`](../reference/language-concepts/03-types-oop-modern.md)。

## 2. 类与对象：现代写法

### 传统写法（PHP 7 时代）

```php
<?php

declare(strict_types=1);

class OrderLegacy
{
    private string $sku;
    private int $qty;

    public function __construct(string $sku, int $qty)
    {
        $this->sku = $sku;      // 三处重复：属性声明 + 参数 + 赋值
        $this->qty = $qty;
    }

    public function getSku(): string { return $this->sku; }
    public function getQty(): int { return $this->qty; }
}
```

### 现代写法：构造器属性提升（PHP 8.0+）

```php
<?php

declare(strict_types=1);

// 提升属性 + 只读：最常见的 DTO / 值对象形态
class OrderLine
{
    public function __construct(
        public readonly string $sku,
        public readonly int $qty,
        public readonly float $unitPrice,
    ) {
    }

    public function total(): float
    {
        return $this->qty * $this->unitPrice;
    }
}

$line = new OrderLine('PHP-BOOK', 2, 59.90);
echo $line->total(), PHP_EOL;   // 119.8
// $line->qty = 5;              // ❌ Error：readonly 属性初始化后不可修改
```

**构造器属性提升**把"声明属性 → 接收参数 → 赋值"三步压缩成一行，是现代 PHP 代码量骤减的最大功臣。`readonly`（8.1+）保证值对象不可变，天然线程安全、易于缓存。

### 只读属性与深拷贝（PHP 8.3 / 8.4 / 8.5）

```php
class Cart
{
    /** @var OrderLine[] */
    private array $items = [];

    public function add(OrderLine $line): void
    {
        $this->items[] = $line;
    }

    /** @return OrderLine[] */
    public function items(): array
    {
        return $this->items;
    }

    // 8.5 新特性（RFC clone_with_v2）：clone($obj, [...]) 克隆时批量覆盖属性，
    // 被覆盖属性须当前作用域可见——private 属性只能在类内方法里覆盖
    public function withExtra(OrderLine $extra): static
    {
        return clone($this, ['items' => [...$this->items, $extra]]);
    }
}

$cart = new Cart();
$cart->add($line);

$copy = $cart->withExtra(new OrderLine('NEW', 1, 9.9));   // 新 Cart 实例，$cart 不受影响
```

> 💡 PHP 8.4 引入**非对称可见性**：`public private(set) array $items` 表示外部可读、仅内部可写，可替代手写 getter。注意它与 `readonly` 互斥，二选一即可。

## 3. 继承、接口与抽象类

```php
<?php

declare(strict_types=1);

// 接口：契约，PHP 支持常量与方法的签名
interface PaymentGateway
{
    public function charge(int $amountCents): string;   // 返回交易号
}

// 抽象类：部分实现 + 强制子类补全
abstract class BasePayment implements PaymentGateway
{
    public function __construct(
        protected readonly string $merchantId,
    ) {
    }

    // 已实现：公共流程
    public function charge(int $amountCents): string
    {
        $this->validate($amountCents);
        return $this->doCharge($amountCents);
    }

    abstract protected function doCharge(int $amountCents): string;

    private function validate(int $amountCents): void
    {
        if ($amountCents <= 0) {
            throw new InvalidArgumentException('金额必须为正');
        }
    }
}

final class AlipayPayment extends BasePayment   // final 禁止再继承
{
    protected function doCharge(int $amountCents): string
    {
        return "alipay-{$this->merchantId}-{$amountCents}";
    }
}

$gw = new AlipayPayment('M-001');
echo $gw->charge(9900), PHP_EOL;   // alipay-M-001-9900
```

**选型口诀**：

- 需要"多角色能力"（一个类实现多种能力）→ 接口，一个类可 `implements` 多个
- 需要"复用骨架代码 + 强制差异实现" → 抽象类，只能单继承
- 接口方法只能声明签名，默认实现需 trait 承载

## 4. 静态成员与静态返回类型

```php
<?php

declare(strict_types=1);

final class Money
{
    private function __construct(
        public readonly int $cents,
    ) {
    }

    public static function of(int $cents): self
    {
        return new self($cents);
    }

    public static function zero(): static   // static 返回类型：跟随实际调用类
    {
        return new static(0);
    }

    public function add(Money $other): static
    {
        return new static($this->cents + $other->cents);
    }
}

$total = Money::of(100)->add(Money::of(250));
echo $total->cents, PHP_EOL;   // 350
```

**`self` vs `static`**：`self` 绑定定义时的类，`static` 绑定运行时的实际类（后期静态绑定）。返回 `new static` 的工厂方法在子类中会返回子类实例。

## ✅ 最佳实践

值对象应保证创建后仍满足不变量，例如价格不能为负；readonly 属性限制重新赋值，但内部对象仍可能可变，因此不能仅凭关键字声称深度不可变。构造器提升减少声明重复，并不决定对象的业务设计。

依赖通过参数传入，测试可替换网络或存储。final 用于确实不支持继承扩展的类型，不必机械作用于所有类。将不可预测 I/O 与简单对象初始化分开，使失败和重试发生在明确边界。

## ❓ 常见问题

### Q1: 提升的属性能写默认值吗？
**A**: 能。`public int $qty = 1` 即提升 + 默认值；提升的 `readonly` 属性同样可配默认值，构造时传参会正常覆盖；不允许默认值的是非提升的 `readonly`（直接 fatal），它只能在构造器内初始化。

### Q2: `private(set)` 是什么？
**A**: PHP 8.4 引入的非对称可见性：读取用 `public`、写入用 `private(set)`，替代手写 getter 的场景。注意它与 `readonly` 不能组合使用，8.3 环境请使用 `readonly`。

### Q3: 一个类可以实现两个有同名方法的接口吗？
**A**: 可以，只要方法签名兼容（8.0 起放宽）；否则需要在类中给出同时满足两者的实现。

## 🎯 练习与实践

### 基础练习
- [ ] 用构造器属性提升实现 `Rectangle(float $w, float $h)`，提供 `area()` 与 `scale(float $factor): static`（返回新对象）
- [ ] 定义 `interface Logger { public function log(string $msg): void; }`，并写出 `FileLogger`、`MemoryLogger` 两个实现
- [ ] 把第 3 节的支付示例改成接收 `PaymentGateway` 接口参数的函数，体会多态

### 进阶挑战
- [ ] 实现不可变 `Money` 类：支持 `add/sub/multiply`，所有操作返回新实例，`readonly` 保证原值不变
- [ ] 用 `clone()`（8.5 批量覆盖形式，封装为类内 `withXxx()` 方法）实现 `Cart` 的不可变添加操作，验证原对象未被修改

---

## 🔗 相关文档

- 📄 **[控制流程](./05-control-flow.md)** — 下一节：条件、循环与 match 表达式
- 📄 **[类型系统与现代 OOP 全表](../reference/language-concepts/03-types-oop-modern.md)** — 枚举/属性/Fibers 的权威条目
- 📄 **[综合练习：CLI 任务管理工具](./08-first-project.md)** — 用本文知识完成完整项目


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
