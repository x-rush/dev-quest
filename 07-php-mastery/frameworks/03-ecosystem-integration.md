# Laravel 生态集成：迁移、Seeder、缓存与 Sanctum 认证

## 先看框架承担哪部分职责

**Laravel 集成**：迁移定义结构变化，Seeder 提供测试数据，认证定义身份，缓存保存副本。这四种状态必须分别管理。

**最小练习与预期结果**：在空测试库执行迁移与种子后调用受保护接口；用两名用户验证资源隔离，再测试缓存失效。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 打通 Laravel 数据层与安全层——用迁移与工厂管理数据库结构、用缓存加速读取、用 Sanctum 保护 API
>
> **目标读者**: 需要为 API 配备完整数据库与认证方案的开发者
>
> **前置知识**: [Laravel 进阶](./02-laravel-advanced.md)、[Composer 生态速查](../reference/library-guides/02-composer-ecosystem.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Laravel` `#迁移` `#Seeder` `#缓存` `#Sanctum` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 编写可回滚的迁移与带外键的表结构
- ✅ 用工厂 + Seeder 生成可信测试数据
- ✅ 按场景选择缓存策略并正确失效
- ✅ 用 Sanctum 实现 API Token 与 SPA 两类认证

## 1. 数据库迁移

```bash
php artisan make:migration create_posts_table
```

```php
// database/migrations/xxxx_create_posts_table.php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('posts', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete(); // 外键 + 级联删除
            $table->string('title', 120);
            $table->string('slug', 140)->unique();       // 唯一索引
            $table->text('body');
            $table->timestamp('published_at')->nullable()->index(); // 常查询列加索引
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('posts');   // 保证迁移可回滚
    }
};
```

```bash
php artisan migrate                # 执行未跑过的迁移
php artisan migrate:rollback       # 回滚最后一批
php artisan migrate:fresh --seed   # 重建全部表并填充（仅限开发环境）
```

## 2. 工厂与 Seeder

```php
// database/factories/PostFactory.php
namespace Database\Factories;

use App\Models\Post;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/** @extends Factory<Post> */
final class PostFactory extends Factory
{
    public function definition(): array
    {
        return [
            'user_id'      => User::factory(),           // 嵌套工厂自动创建作者
            'title'        => fake()->sentence(6),
            'slug'         => fake()->unique()->slug(),
            'body'         => fake()->paragraphs(3, true),
            'published_at' => fake()->optional()->dateTimeThisYear(),
        ];
    }
}
```

```php
// database/seeders/DatabaseSeeder.php
public function run(): void
{
    // 建一个作者，带 5 篇文章（factory 状态 published 需在工厂中定义）
    \App\Models\User::factory()
        ->has(\App\Models\Post::factory()->count(5))
        ->create(['email' => 'demo@example.com']);
}
```

Seeder 不是"假数据玩具"：演示环境、集成测试、E2E 冒烟都依赖它提供确定性的初始状态。

## 3. 缓存

```php
use App\Models\Post;
use Illuminate\Support\Facades\Cache;

// remember：命中直接返回，未命中执行回调后写入 10 分钟
$stats = Cache::remember('stats:posts', now()->addMinutes(10), fn () => [
    'total' => Post::count(),
    'today' => Post::whereDay('created_at', today())->count(),
]);

// 手动失效：数据变更时清除对应键
Cache::forget('stats:posts');

// 标签分组（redis/memcached 支持）：整组失效
Cache::tags(['posts'])->put('posts:hot', $hotPosts, now()->addHour());
Cache::tags(['posts'])->flush();
```

选型建议：本地开发 `file`；单机生产 `redis` 即可；**禁用 `database` 驱动承载高频读**（缓存读也会打数据库）。缓存键设计、原子锁与击穿防护见[缓存策略与队列调优](../advanced-topics/performance/02-caching-queues.md)。

## 4. Sanctum 认证

```bash
php artisan install:api          # Laravel 11 起引入、13 延续：启用 api.php 并附带安装 Sanctum
php artisan migrate              # personal_access_tokens 表
```

### 4.1 API Token（移动端 / 第三方调用）

```php
// routes/api.php —— 路由保护：auth:sanctum 中间件
Route::middleware('auth:sanctum')->group(function (): void {
    Route::apiResource('posts', \App\Http\Controllers\PostController::class);
});

// 登录签发 Token，并声明能力（abilities）
Route::post('/auth/token', function (\Illuminate\Http\Request $request) {
    $data = $request->validate([
        'email'    => ['required', 'email'],
        'password' => ['required'],
    ]);

    $user = \App\Models\User::where('email', $data['email'])->firstOrFail();

    if (! \Illuminate\Support\Facades\Hash::check($data['password'], $user->password)) {
        abort(422, '凭据错误');
    }

    return response()->json([
        'token' => $user->createToken('cli', ['posts:read'])->plainTextToken,
    ]);
});
```

```php
// 按能力细粒度授权
if (! $request->user()->tokenCan('posts:read')) {
    abort(403);
}
```

### 4.2 SPA 认证（同域前端）

SPA 场景不签 Token，改用 Cookie 会话：前端先请求 `/sanctum/csrf-cookie`，之后带凭据请求即可；`config/sanctum.php` 的 `stateful` 域名列表必须包含前端域名。

## ❓ 常见问题

**Q: 迁移报"外键格式不匹配"？**
A: MySQL 中确保表引擎一致（InnoDB）；`foreignId('user_id')` 要求 `users` 表先创建，注意迁移文件名的时间顺序。

**Q: `tokenCan` 永远返回 true？**
A: 检查是否用了无能力签发的旧 Token；`createToken` 未传能力数组时默认拥有全部能力。

## 🔗 相关文档

- 📄 [Laravel 核心速查](../reference/framework-essentials/01-laravel-essentials.md) — 迁移与模型条目速查
- 📄 [Composer 生态](../reference/library-guides/02-composer-ecosystem.md) — 安装 Sanctum 等包的依赖管理
- 📄 [Feature 测试与数据库测试](../testing/03-feature-testing.md) — 工厂在测试中的标准用法
- 📄 [电商 API 实战](../projects/03-ecommerce-api.md) — 迁移 + 认证 + 缓存的综合项目


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
