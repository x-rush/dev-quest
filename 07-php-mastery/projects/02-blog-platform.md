# 进阶项目：博客平台（CRUD + 认证）

> **文档简介**: 构建带用户体系的多作者博客——关系建模、Sanctum 登录、Policy 授权与草稿/发布工作流
>
> **目标读者**: 完成 TODO API、想掌握"认证 + 授权 + 关系"三件套的开发者
>
> **前置知识**: [TODO API](./01-todo-api.md)、[Laravel 进阶](../frameworks/02-laravel-advanced.md)、[Sanctum 认证](../frameworks/03-ecosystem-integration.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Laravel` `#博客` `#认证` `#Policy` `#实战项目` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

- ✅ 建模 User/Post/Tag 多对多关系并写出对应迁移
- ✅ 实现 Sanctum 登录 + Token 签发
- ✅ 用 Policy 保证"只有作者能改自己的文章"
- ✅ 实现草稿→发布状态机与 slug 唯一性

## 1. 数据建模

```text
users (id, name, email, password)
posts (id, user_id, title, slug, body, status, published_at)
tags  (id, name)
post_tag (post_id, tag_id)   -- 多对多中间表
```

```php
// 迁移要点（posts 表）
Schema::create('posts', function (Blueprint $table): void {
    $table->id();
    $table->foreignId('user_id')->constrained()->cascadeOnDelete();
    $table->string('title', 120);
    $table->string('slug', 140)->unique();
    $table->text('body');
    $table->string('status', 16)->default('draft')->index();
    $table->timestamp('published_at')->nullable();
    $table->timestamps();
});
```

```php
// app/Enums/PostStatus.php
namespace App\Enums;

enum PostStatus: string
{
    case Draft     = 'draft';
    case Published = 'published';

    public function label(): string
    {
        return match ($this) {
            self::Draft     => '草稿',
            self::Published => '已发布',
        };
    }
}
```

## 2. 认证：登录与 Token

```php
// routes/api.php
use App\Http\Controllers\AuthController;
use App\Http\Controllers\PostController;
use Illuminate\Support\Facades\Route;

Route::post('/register', [AuthController::class, 'register']);
Route::post('/login', [AuthController::class, 'login']);

Route::middleware('auth:sanctum')->group(function (): void {
    Route::post('/logout', [AuthController::class, 'logout']);
    Route::apiResource('posts', PostController::class);
});
```

```php
// app/Http/Controllers/AuthController.php（节选）
namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;

final class AuthController extends Controller
{
    public function register(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'     => ['required', 'string', 'max:40'],
            'email'    => ['required', 'email', 'unique:users'],
            'password' => ['required', 'min:10'],   // 密码策略宁严勿松
        ]);

        $user = User::create([
            ...$data,
            // bcrypt 自动加盐；绝不存明文
            'password' => Hash::make($data['password']),
        ]);

        return response()->json(['token' => $user->createToken('web')->plainTextToken], 201);
    }

    public function login(Request $request): JsonResponse
    {
        $user = User::where('email', $request->string('email'))->first();

        if ($user === null || ! Hash::check($request->string('password'), $user->password)) {
            throw ValidationException::withMessages(['email' => '凭据错误']); // 不区分"无此用户/密码错"
        }

        return response()->json(['token' => $user->createToken('web')->plainTextToken]);
    }

    public function logout(Request $request): JsonResponse
    {
        $request->user()->currentAccessToken()->delete();

        return response()->json(status: 204);
    }
}
```

## 3. 授权：Policy

```bash
php artisan make:policy PostPolicy --model=Post
```

```php
// app/Policies/PostPolicy.php
namespace App\Policies;

use App\Enums\PostStatus;
use App\Models\Post;
use App\Models\User;

final class PostPolicy
{
    // 更新：只有作者本人可以
    public function update(User $user, Post $post): bool
    {
        return $user->id === $post->user_id;
    }

    // 发布：作者本人 + 草稿状态
    public function publish(User $user, Post $post): bool
    {
        return $user->id === $post->user_id && $post->status === PostStatus::Draft;
    }
}
```

```php
// 控制器中一行完成授权检查（403 由框架抛出）
public function update(Request $request, Post $post): PostResource
{
    $this->authorize('update', $post);
    // ...实际更新逻辑
}
```

Laravel 11 中在 `AppServiceProvider::boot()` 调用 `Gate::policy(Post::class, PostPolicy::class)` 完成注册。

## 4. 文章接口（节选）

```php
// app/Http/Controllers/PostController.php
use App\Enums\PostStatus;

public function index(Request $request): AnonymousResourceCollection
{
    return PostResource::collection(
        Post::query()
            ->published()                                  // 模型 scope
            ->with('author:id,name', 'tags:id,name')       // 预加载防 N+1
            ->when($request->filled('tag'), fn ($q, $tag) => $q->whereHas(
                'tags', fn ($t) => $t->where('name', $tag),
            ))
            ->latest('published_at')
            ->paginate(15),
    );
}

public function publish(Request $request, Post $post): PostResource
{
    $this->authorize('publish', $post);

    $post->update(['status' => PostStatus::Published, 'published_at' => now()]);

    return new PostResource($post);
}
```

## 5. 验收清单

- [ ] 未带 Token 请求写接口返回 401
- [ ] 用户 B 修改用户 A 的文章返回 403
- [ ] `published()` 列表对游客可见，草稿不可见
- [ ] 删除用户时其文章级联删除

扩展方向：为接口写 Feature 测试（[Feature 测试](../testing/03-feature-testing.md)），或把通知改为队列事件（[缓存策略与队列调优](../advanced-topics/performance/02-caching-queues.md)）。

## 🔗 相关文档

- 📄 [Laravel 核心速查](../reference/framework-essentials/01-laravel-essentials.md) — 关系与中间件条目
- 📄 [生态集成：迁移、缓存与认证](../frameworks/03-ecosystem-integration.md) — Sanctum 完整配置
- 📄 [高级特性](../basics/07-advanced-features.md) — match 表达式、首类 callable 等语法
- 📄 [电商 API 实战](./03-ecommerce-api.md) — 下一级项目
