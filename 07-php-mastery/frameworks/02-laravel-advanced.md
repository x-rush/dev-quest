# Laravel 进阶：Eloquent 关系、队列与事件

> **文档简介**: 系统掌握 Eloquent 关系声明与高级查询构建，学会用队列削峰、用事件解耦业务逻辑
>
> **目标读者**: 完成 Laravel 入门、需要构建多表业务系统的中级开发者
>
> **前置知识**: [Laravel 入门](./01-laravel-basics.md)、[PHP 高级特性](../basics/07-advanced-features.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Laravel` `#Eloquent` `#队列` `#事件` `#预加载` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 正确声明与使用常用 Eloquent 关系
- ✅ 用预加载消灭 N+1，用子查询/聚合构建复杂查询
- ✅ 定义任务类并派发到队列，处理失败重试
- ✅ 用事件/监听器把副作用从控制器中剥离

## 1. Eloquent 关系全景

```php
// app/Models/Post.php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;

final class Post extends Model
{
    protected $fillable = ['user_id', 'title', 'body'];

    // 一对多（反向）：文章属于作者
    public function author(): BelongsTo
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    // 一对多：文章有多条评论
    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    // 多对多：文章与标签，中间表 post_tag
    public function tags(): BelongsToMany
    {
        return $this->belongsToMany(Tag::class)->withTimestamps();
    }
}
```

其余关系按需选用：`hasOne`（一对一）、`morphMany`（多态，如"可被评论的任何资源"）、`hasManyThrough`（跨层穿透）。所有关系本质都是封装好的查询构建器，可继续链式调用：

```php
// 关系作为查询入口：带约束的关联查询
$recent = $post->comments()->where('approved', true)->latest()->limit(5)->get();
```

## 2. 高级查询

```php
use App\Models\Post;
use App\Models\User;
use Illuminate\Database\Eloquent\Builder;

// whereHas：按关系存在性过滤（"有热评的文章"）
$hot = Post::query()
    ->whereHas('comments', fn (Builder $q) => $q->where('likes', '>', 10))
    ->get();

// 预加载 + 约束：一次查出文章与每篇的最新 3 条评论，避免 N+1
$posts = Post::query()
    ->with(['comments' => fn ($q) => $q->latest()->limit(3)])
    ->withCount('comments')                    // 附加 comments_count 聚合列
    ->paginate(15);

// 子查询排序：按作者文章数排序用户
$users = User::query()
    ->orderByDesc(Post::selectRaw('count(*)')
        ->whereColumn('user_id', 'users.id'))
    ->get();

// upsert：批量存在则更新，否则插入（键唯一性由数据库保证）
Post::upsert($rows, ['slug'], ['title', 'body']);
```

**预防 N+1 的纪律**：开发环境在 `AppServiceProvider::boot()` 中开启 `Model::preventLazyLoading()`，未预加载的关系会抛异常而不是悄悄发 N 条 SQL。深入调优见[查询优化](../advanced-topics/performance/01-query-optimization.md)。

## 3. 队列：把慢操作移出请求

```bash
php artisan make:job SendPostPublishedMail   # 生成任务类
```

```php
// app/Jobs/SendPostPublishedMail.php
namespace App\Jobs;

use App\Models\Post;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;

final class SendPostPublishedMail implements ShouldQueue
{
    use Dispatchable, Queueable;

    public int $tries = 3;        // 最多尝试 3 次
    public int $backoff = 60;     // 每次重试间隔 60 秒

    // 构造器接收 Eloquent 模型，派发时自动序列化主键、执行时自动还原
    public function __construct(public readonly Post $post) {}

    public function handle(): void
    {
        // 发邮件、调第三方 API 等耗时操作都写在这里
    }
}
```

```php
// 控制器中派发：请求立即返回，任务交给队列进程
SendPostPublishedMail::dispatch($post)->delay(now()->addMinutes(1));
```

本地用 `php artisan queue:work` 消费；生产环境要求 `QUEUE_CONNECTION=redis/database`（`sync` 驱动是同步执行，等于没有队列），并用 Supervisor 守护进程，细节见[缓存策略与队列调优](../advanced-topics/performance/02-caching-queues.md)。

## 4. 事件与监听器：解耦副作用

```bash
php artisan make:event PostPublished
php artisan make:listener NotifyFollowers --event=PostPublished
```

```php
// app/Events/PostPublished.php —— 纯数据载体
final class PostPublished
{
    public function __construct(public readonly Post $post) {}
}

// app/Listeners/NotifyFollowers.php —— 副作用执行者
final class NotifyFollowers
{
    public function handle(PostPublished $event): void
    {
        // 加 implements ShouldQueue 可让监听器也异步执行
    }
}
```

```php
// 任意位置触发；监听器映射注册在 EventServiceProvider 或自动发现
PostPublished::dispatch($post);
```

控制器只负责"发表文章"这一件事，通知、统计、缓存失效全部交给事件——控制器保持精瘦，业务边界清晰。

## ❓ 常见问题

**Q: 队列任务里改了模型字段却没生效？**
A: 任务类中反序列化的是派发时的快照。任务执行时间较长时，handle 内先 `Post::find($this->post->id)` 重新取最新状态。

**Q: belongsToMany 保存时报中间表不存在？**
A: 迁移中确认中间表名（默认按模型字母序拼接 `post_tag`）与外键命名，必要时在关系上显式指定表名。

## 🔗 相关文档

- 📄 [Laravel 核心速查](../reference/framework-essentials/01-laravel-essentials.md) — 关系/查询/任务条目速查
- 📄 [类型系统与现代 OOP](../reference/language-concepts/03-types-oop-modern.md) — 枚举 casts 等现代语法
- 📄 [生态集成：迁移、缓存与认证](./03-ecosystem-integration.md) — 队列驱动与缓存后端配置
- 📄 [博客平台实战](../projects/02-blog-platform.md) — 本文知识点的完整落地项目
