# 函数与面向对象 - 构造器属性提升时代

> **文档简介**: 系统学习 PHP 函数（含箭头函数、命名参数）与现代 OOP（构造器属性提升、只读属性、接口与抽象类）
>
> **目标读者**: 已掌握变量与类型系统、准备编写结构化代码的 PHP 初学者
>
> **前置知识**: 完成 [变量与类型系统](./03-variables-types.md)，理解类型声明

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#函数` `#面向对象` `#构造器提升` `#只读属性` |
| **更新日期** | `2026年9月` |

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
}

$cart = new Cart();
$cart->add($line);

// 8.3 新特性：clone($obj, [...]) 克隆时批量覆盖属性（含 readonly），
// 配合 readonly 实现"修改即新对象"；被覆盖属性须当前作用域可见
$extra = new OrderLine('NEW', 1, 9.9);
$copy  = clone($cart, ['items' => [...$cart->items(), $extra]]);
// 8.5 起等价链式写法：clone($cart)->with(items: [...$cart->items(), $extra])
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
- 8.1+ 接口方法可以带默认实现，但仍优先用接口表达契约

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

- ✅ **值对象一律构造器提升 + readonly**：不可变对象消除整类状态 bug
- ✅ **组合优于继承**：优先注入接口依赖，而非拉深继承链
- ✅ **类设计成 `final`**：留好接口，默认关闭继承，避免子类破坏不变式
- ❌ **不要在构造器中做 I/O**：构造器只做赋值与校验，网络/DB 调用交给工厂或服务
- ❌ **不要滥用魔术方法 `__get/__set`**：显式方法签名对 IDE 与静态分析更友好

## ❓ 常见问题

### Q1: 提升的属性能写默认值吗？
**A**: 能。`public int $qty = 1` 即提升 + 默认值；但 `readonly` 属性带默认值后构造时再传同名参数会报错——通常只给非 readonly 提升属性配默认值。

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
- [ ] 用 `clone()`（8.3 批量覆盖形式 / 8.5 链式 `->with()`）实现 `Cart` 的不可变添加操作，验证原对象未被修改

---

## 🔗 相关文档

- 📄 **[控制流程](./05-control-flow.md)** — 下一节：条件、循环与 match 表达式
- 📄 **[类型系统与现代 OOP 全表](../reference/language-concepts/03-types-oop-modern.md)** — 枚举/属性/Fibers 的权威条目
- 📄 **[综合练习：CLI 任务管理工具](./08-first-project.md)** — 用本文知识完成完整项目
