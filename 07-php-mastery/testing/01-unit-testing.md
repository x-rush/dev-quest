# 单元测试：PHPUnit 基础

> **文档简介**: 用 PHPUnit 为纯 PHP 类与 Laravel 服务层编写快速、隔离的单元测试，掌握断言、数据提供器与 Mock
>
> **目标读者**: 写过 PHP 业务代码但测试经验有限的学习者
>
> **前置知识**: [错误与异常](../basics/06-error-exceptions.md)、[Composer 生态](../reference/library-guides/02-composer-ecosystem.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#PHPUnit` `#单元测试` `#Mock` `#质量工程` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 写出第一个 PHPUnit 测试并跑通 `composer test`
- ✅ 用数据提供器覆盖边界输入
- ✅ 区分"可单测的设计"与"不可单测的设计"
- ✅ 用 Mock 隔离外部依赖

## 1. 安装与第一个测试

```bash
composer require --dev phpunit/phpunit
mkdir -p tests/Unit
```

```xml
<!-- phpunit.xml 最小配置：测试目录 + 源码覆盖率范围 -->
<phpunit bootstrap="vendor/autoload.php" colors="true">
    <testsuites>
        <testsuite name="Unit"><directory>tests/Unit</directory></testsuite>
    </testsuites>
    <source><include><directory>app</directory></include></source>
</phpunit>
```

```php
// tests/Unit/PriceCalculatorTest.php
namespace Tests\Unit;

use App\Services\PriceCalculator;
use PHPUnit\Framework\TestCase;

final class PriceCalculatorTest extends TestCase
{
    // 每个方法一个意图明确的测试：名称即文档
    public function test_applies_discount_percentage_to_base_price(): void
    {
        $calculator = new PriceCalculator();

        $this->assertSame(900, $calculator->finalPriceCents(baseCents: 1000, discountPercent: 10));
    }

    public function test_discount_cannot_exceed_100_percent(): void
    {
        $calculator = new PriceCalculator();

        $this->expectException(\DomainException::class);
        $calculator->finalPriceCents(1000, 120);   // 异常路径也是规格的一部分
    }
}
```

```bash
./vendor/bin/phpunit --testsuite Unit   # 单元测试应在毫秒级跑完
```

## 2. 数据提供器：一次测试多组输入

```php
// 边界值不该靠复制粘贴测试方法
public static function discountProvider(): array
{
    return [
        '无折扣'     => [1000, 0, 1000],
        '整十折'     => [1000, 10, 900],
        '零价格'     => [0, 50, 0],
        '上限内小数' => [999, 1, 989],
    ];
}

/** @dataProvider discountProvider */
public function test_final_price_for_various_inputs(int $base, int $discount, int $expected): void
{
    $this->assertSame($expected, (new PriceCalculator())->finalPriceCents($base, $discount));
}
```

## 3. 可测试的设计

单测慢/写不出的根源通常是**依赖直接 new 在方法体里**。把依赖从外部注入：

```php
// app/Services/OrderNotifier.php
namespace App\Services;

interface Mailer            // 面向接口，而非具体实现
{
    public function send(string $to, string $subject, string $body): void;
}

final readonly class OrderNotifier
{
    public function __construct(private Mailer $mailer) {}

    public function notifyShipped(string $email): void
    {
        $this->mailer->send($email, '已发货', '您的订单已发出');
    }
}
```

```php
// tests/Unit/OrderNotifierTest.php —— Mock 掉 Mailer，只测编排逻辑
final class OrderNotifierTest extends TestCase
{
    public function test_sends_shipped_notice(): void
    {
        $mailer = $this->createMock(Mailer::class);
        $mailer->expects($this->once())                  // 断言被调用且仅一次
            ->method('send')
            ->with('a@b.c', '已发货', $this->stringContains('订单'));

        (new OrderNotifier($mailer))->notifyShipped('a@b.c');
    }
}
```

Mock 使用纪律：**只 mock 你拥有的接口**（Mailer 而非第三方 SDK 类）；一次测试最多一个 mock 对象，超过说明该拆分了。

## 4. 单元测试与 Laravel 专属测试的边界

- 不需要容器/数据库（纯计算、纯编排）→ `PHPUnit\Framework\TestCase`（快）
- 需要 Eloquent、路由、事件 → 用 Laravel `Tests\TestCase`，详见 [Pest 测试](./02-pest-testing.md) 与 [Feature 测试](./03-feature-testing.md)

原则：越多的纯单测，套件越快越稳定；集成行为交给 Feature 测试兜底。

## ❓ 常见问题

**Q: 测试之间互相污染？**
A: 每个测试方法都跑在独立实例上（setUp 重建）；不要用静态可变状态跨测试传数据。

**Q: 该测私有方法吗？**
A: 不测。私有逻辑通过公共接口驱动覆盖；若公共入口难以触达该私有逻辑，说明职责该拆分。

## 🔗 相关文档

- 📄 [内置函数速查](../reference/language-concepts/02-built-in-functions.md) — 断言中常用数组/字符串函数
- 📄 [Composer 生态](../reference/library-guides/02-composer-ecosystem.md) — dev 依赖管理
- 📄 [Pest 测试](./02-pest-testing.md) — 同一套件的现代写法
- 📄 [TODO API](../projects/01-todo-api.md) — 给入门项目补上测试
