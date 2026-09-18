# Feature 测试与数据库测试

> **文档简介**: 用 Laravel Feature 测试整条 HTTP 链路——真实路由与中间件、RefreshDatabase 隔离、工厂造数与响应断言
>
> **目标读者**: 单元测试已上手、需要验证"接口级"行为的 Laravel 开发者
>
> **前置知识**: [单元测试](./01-unit-testing.md)、[生态集成：迁移与工厂](../frameworks/03-ecosystem-integration.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Laravel` `#Feature测试` `#RefreshDatabase` `#工厂` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 理解 Feature 测试与单元测试的分层职责
- ✅ 用 `RefreshDatabase` 实现测试间数据库隔离
- ✅ 用工厂构造关联数据（`has`/`for`）
- ✅ 对 JSON API 做全链路断言

## 1. 测试金字塔中的位置

```text
        /\        Feature（应用内 HTTP 请求与数据库协作）
       /--\       集成（服务层协作）
      /----\      单元（快，数量多）
```

Feature 测试的价值：**一次覆盖路由→中间件→验证→控制器→数据库→响应**，是最接近用户行为的回归防线。

## 2. 数据库隔离：RefreshDatabase

```php
// tests/TestCase.php —— Laravel 13 骨架上加 trait
namespace Tests;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\TestCase as BaseTestCase;

abstract class TestCase extends BaseTestCase
{
    use RefreshDatabase;  // 每个测试包在事务里，结束时回滚
}
```

`RefreshDatabase` 把每个用例包在数据库事务里，结束时回滚——可隔离参与事务的数据库变更；外部资源和其他连接需要单独处理。注意：

- 测试必须用独立数据库（`phpunit.xml` 的 `DB_DATABASE` 指向专用库，**永不指向生产**）
- 普通嵌套事务通常可配合 savepoint；真正提交后的回调、其他连接以及隐式提交 DDL 需要专门验证，必要时用迁移或截断策略

## 3. 工厂造数：关联关系一行搞定

```php
// 三种关联姿势
$user  = User::factory()->create();                       // 单个
$posts = Post::factory()->count(5)->for($user, 'author')->create(); // 属于该用户
$user  = User::factory()->has(Post::factory()->count(3))->create(); // 从上游挂下游

// 工厂状态：语义化变体
$post = Post::factory()->published()->create();   // published() 是工厂里定义的 state
```

工厂状态定义（`database/factories/PostFactory.php`）：

```php
public function published(): static
{
    return $this->state(fn (): array => [
        'status'       => \App\Enums\PostStatus::Published,
        'published_at' => now(),
    ]);
}
```

## 4. 全链路 JSON 断言

```php
// tests/Feature/PostApiTest.php
use App\Models\Post;
use App\Models\User;

it('游客可以浏览已发布文章列表', function (): void {
    Post::factory()->count(3)->published()->create();
    Post::factory()->create();   // 一篇草稿，不应出现

    $this->getJson('/api/posts')
        ->assertOk()
        ->assertJsonCount(3, 'data')
        ->assertJsonStructure([
            'data'  => [['id', 'title', 'status']],
            'links' => [],
        ]);
});

it('作者可以发布自己的草稿', function (): void {
    $post = Post::factory()->for(User::factory()->create(), 'author')->create();

    $this->actingAs($post->author)
        ->postJson("/api/posts/{$post->id}/publish")
        ->assertOk();

    // 副作用直接查库验证：不依赖响应内容
    $this->assertDatabaseHas('posts', [
        'id'     => $post->id,
        'status' => 'published',
    ]);
});

it('验证失败返回字段级错误', function (): void {
    $this->actingAs(User::factory()->create())
        ->postJson('/api/posts', ['title' => ''])
        ->assertUnprocessable()                  // 422
        ->assertJsonValidationErrors(['title']);
});
```

## 5. 编写纪律

- **每个用例只验一个行为**，失败信息即可定位
- 先工厂造数 → 发请求 → 断言响应 → 必要时查库验副作用，四段式固定下来
- 不在 Feature 测试里 mock Eloquent；要测隔离逻辑请回[单元测试](./01-unit-testing.md)
- CI 中把 Feature 套件与静态分析并行跑（见[CI/CD 与可观测性](../deployment/03-ci-cd-observability.md)）

## ❓ 常见问题

**Q: RefreshDatabase 每次都重新跑迁移，很慢？**
A: 它默认只在首次跑迁移，后续用事务回滚。若仍慢，检查测试类或 Pest 配置是否另用了 DatabaseMigrations，以及测试库是否在远程主机。

**Q: 测试里时间相关的断言不稳定？**
A: 用 `Carbon::setTestNow('2026-09-01 10:00:00')` 冻结时间，用例末尾 `Carbon::setTestNow()` 还原。

<!-- full-library-explanation -->
## 区分进程内请求与真实部署链路

前置是路由、中间件、数据库事务与工厂。getJson/postJson 在测试进程内调用应用，不经过真实网络、Nginx、TLS 或浏览器 Cookie 策略；它们验证应用协作很有效，但不能据此宣布部署链路可用。Laravel 测试环境通常绕过 CSRF 检查，需要专门的真实中间件或浏览器验证才能覆盖该防线。

RefreshDatabase 管理测试数据库状态，不回滚 Redis、邮件、文件和已经启动的其他进程。外部副作用使用受控替身或独立资源并清理。数据库驱动也影响约束、JSON 查询和事务行为，SQLite 快速测试不能替代关键 MySQL/PostgreSQL 集成案例。

**练习**：先创建一篇属于 B 的草稿，再让 A 发布，验证 403（或项目约定的隐藏资源响应），同时查库确认仍为草稿。列表测试除数量外还断言草稿 ID 不在结果中，防止“漏了一篇已发布又多了一篇草稿”抵消数量。冻结时间后用 finally 或测试框架清理机制恢复，即使断言失败也不污染下一条用例。

依据：[HTTP 测试](https://laravel.com/docs/13.x/http-tests)、[数据库测试](https://laravel.com/docs/13.x/database-testing)。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

## 🔗 相关文档

- 📄 [Laravel 核心速查](../reference/framework-essentials/01-laravel-essentials.md) — 模型与迁移条目回查
- 📄 [PHPUnit 单元测试](./01-unit-testing.md) — 分层职责与 Mock 纪律
- 📄 [博客平台实战](../projects/02-blog-platform.md) — 为真实项目补 Feature 测试
- 📄 [故障排除](../reference/quick-references/02-troubleshooting.md) — 测试报错速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
