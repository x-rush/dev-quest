# Pest 测试：更优雅的测试风格

> **文档简介**: 用 Pest 重写测试套件——函数式 API、链式 expect 断言、数据集与架构测试
>
> **目标读者**: 已了解 PHPUnit、想降低测试维护成本的 Laravel 开发者
>
> **前置知识**: [单元测试](./01-unit-testing.md)、[Laravel 入门](../frameworks/01-laravel-basics.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Pest` `#测试` `#架构测试` `#数据集` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 用 `test()/expect()` 风格重写 PHPUnit 用例
- ✅ 用 datasets 表达多组输入
- ✅ 用 Pest 的 Laravel 插件做 HTTP 与数据库断言
- ✅ 用架构测试固化代码规范

## 1. 安装与风格对比

```bash
composer remove phpunit/phpunit --dev   # Pest 依赖并接管 phpunit
composer require --dev pestphp/pest pestphp/pest-plugin-laravel    # Pest 5（PHP 8.4+，基于 PHPUnit 13）；PHP 8.3 项目用 Pest 4
./vendor/bin/pest --init
```

```php
// tests/Unit/PriceCalculatorTest.php —— Pest 版
use App\Services\PriceCalculator;

test('按折扣率计算最终价格', function (): void {
    expect((new PriceCalculator())->finalPriceCents(1000, 10))->toBe(900);
});

test('折扣不允许超过 100%', function (): void {
    (new PriceCalculator())->finalPriceCents(1000, 120);
})->throws(\DomainException::class);
```

与 PHPUnit 版逐行对比：无类骨架、无 `test_` 前缀方法、断言从 `$this->assertSame(x, y)` 变为 `expect(y)->toBe(x)`——实际值在 expect 中，期望值在 toBe 中；注意与 assertSame 的参数顺序不同。

## 2. 数据集：数据提供器的进化

```php
// datasets.php（或直接写在测试文件内）
dataset('折扣输入', [
    '无折扣' => [1000, 0, 1000],
    '整十折' => [1000, 10, 900],
    '零价格' => [0, 50, 0],
]);

test('最终价格计算', function (int $base, int $discount, int $expected): void {
    expect((new PriceCalculator())->finalPriceCents($base, $discount))->toBe($expected);
})->with('折扣输入');
```

每个数据集条目在报告中是独立命名用例，失败时一眼定位到具体输入。

## 3. Laravel 插件：声明式 HTTP 断言

```php
// tests/Feature/PostApiTest.php
use App\Models\User;

it('拒绝未认证的写操作', function (): void {
    $this->postJson('/api/posts', ['title' => 'x', 'body' => 'y'])
        ->assertUnauthorized();          // 链式断言，替代 self::assertXxx
});

it('允许作者发布自己的文章', function (): void {
    $author = User::factory()->create();          // 工厂用法见 feature-testing
    $post   = \App\Models\Post::factory()->for($author, 'author')->create();

    $this->actingAs($author)                       // 使用默认 guard 模拟认证；与路由认证配置保持一致
        ->postJson("/api/posts/{$post->id}/publish")
        ->assertOk()
        ->assertJsonPath('data.status', 'published');
});
```

`it()` 与 `test()` 等价，语义化命名让报告读起来像验收标准。

## 4. 架构测试：让规范自动执行

```php
// tests/ArchTest.php —— Pest 内置的架构断言
arch('控制器不直接查询数据库', function (): void {
    expect('App\Http\Controllers')
        ->not->toUse('Illuminate\Support\Facades\DB');
});

arch('选定 DTO 命名空间中的类是 final 的', function (): void {
    expect('App\Data')->classes()->toBeFinal();
});
```

架构测试把"口头规范"变成 CI 里会红的测试，是 Pest 最有杠杆的功能。

## 5. 常用 hooks 与组织

```php
beforeEach(fn () => $this->calculator = new \App\Services\PriceCalculator()); // 每用例前置
afterEach(fn () => \Mockery::close());                                        // 每用例后置
```

迁移建议：新旧共存，**按文件渐进替换**（Pest 可直接跑 PHPUnit 类测试），不必一次性重写。

## ❓ 常见问题

**Q: Pest 与 PHPUnit 能共存吗？**
A: 能。Pest 能运行 PHPUnit 格式的测试类；但 `composer.json` 中 PHPUnit 版本须与 Pest 兼容（Pest 自带版本约束）。

**Q: expect 断言速查在哪？**
A: `toBe`（===）、`toBeInstanceOf`、`toThrow`、`each`、`not->`…完整清单见官方文档，本文聚焦高频子集。

<!-- full-library-explanation -->
## 语法变短后，测试边界仍要明确

前置是 PHPUnit 的准备、执行和断言。Pest 的 expect 接收实际值，toBe 接收期望值并严格比较。把实例方法改成静态调用不会因为换了测试框架而合法；本页沿用单元测试文章中的 PriceCalculator 实例。

Laravel Feature 测试需要在 tests/Pest.php 中绑定项目 TestCase，例如 pest()->extend(Tests\TestCase::class)->in('Feature')；数据库隔离 trait 按项目统一配置。安装 Laravel 插件本身不等于所有闭包自动获得应用上下文。认证模拟还要匹配路由 guard；专门测试 Sanctum token abilities 时使用相应的 Sanctum 测试 API。

**练习**：同一价格案例分别用 PHPUnit 和 Pest 表达，故意把返回 int 改为 string，严格断言都应失败。为发布文章接口增加“另一位作者”和“游客”用例，并检查拒绝后数据库未变化。架构测试禁止 DB 门面，只禁止了这一种依赖路径，不能证明控制器没有通过 Eloquent 或服务访问数据库。

依据：[Pest 安装](https://pestphp.com/docs/installation)、[版本迁移](https://pestphp.com/docs/upgrade-guide)。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

## 🔗 相关文档

- 📄 [PHP 快速速查表](../reference/quick-references/01-php-cheatsheet.md) — 箭头函数与闭包语法
- 📄 [错误与异常](../basics/06-error-exceptions.md) — ->throws() 背后的异常机制
- 📄 [Feature 测试与数据库测试](./03-feature-testing.md) — 工厂与 RefreshDatabase 配合
- 📄 [博客平台实战](../projects/02-blog-platform.md) — 用 Pest 验收认证与 Policy


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
