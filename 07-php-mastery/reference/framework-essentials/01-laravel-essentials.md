# Laravel 核心速查（Laravel 11+）

## 概述

Laravel 11/12 进一步精简骨架（无 Http Kernel、默认精简中间件栈），本文收录日常开发最高频的四大核心：路由、Eloquent、Artisan、服务容器。条目式组织，供快速查阅。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Laravel` `#路由` `#Eloquent` `#Artisan` `#服务容器` |
| **更新日期** | `2026年9月` |

## 1. 路由（routes/web.php、routes/api.php）

**定义**: 声明 URI 到动作的映射。Laravel 11+ API 路由需 `php artisan install:api` 启用。

```php
use App\Http\Controllers\OrderController;
use Illuminate\Support\Facades\Route;

// 基本与 RESTful 资源路由
Route::get('/orders/{order}', [OrderController::class, 'show']);
Route::resource('orders', OrderController::class);        // index/create/store/show/edit/update/destroy
Route::apiResource('orders', OrderController::class);     // 去掉 create/edit 两个表单页

// 路由参数约束与可选参数
Route::get('/users/{id}', fn (string $id) => $id)->whereNumber('id');
Route::get('/archive/{year?}', fn (?int $year = null) => $year ?? 'all');

// 命名与跳转
Route::get('/dashboard', fn () => view('dashboard'))->name('dashboard');
route('dashboard');   // 生成 URL

// 路由组：中间件 + 前缀
Route::middleware(['auth:sanctum'])->prefix('v1')->group(function (): void {
    Route::apiResource('projects', OrderController::class);
});

// 隐式枚举绑定（8.x + PHP 枚举）
Route::get('/status/{status}', fn (OrderStatus $status) => $status->value);
```

**陷阱**: `{order}` 参数默认按 ID 注入模型（隐式绑定），记录不存在直接 404；缓存路由（`route:cache`）后闭包路由会报错——生产环境路由必须用控制器类。

## 2. Eloquent ORM

**定义**: ActiveRecord 模式的 ORM，模型即表入口。

```php
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

final class Order extends Model
{
    protected $fillable = ['user_id', 'total', 'status'];   // 批量赋值白名单
    protected $casts = [
        'status'   => OrderStatus::class,   // enum 自动转换（8.x）
        'total'    => 'decimal:2',
        'paid_at'  => 'datetime',
    ];

    public function items(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }

    // Scope：可复用查询片段
    public function scopePaid($query)
    {
        return $query->where('status', OrderStatus::Paid);
    }
}
```

```php
// 查询
$orders = Order::paid()->with('items')->latest()->paginate(20);   // 预加载防 N+1
$order = Order::findOrFail($id);
$agg = Order::where('status', 'paid')->sum('total');

// 创建与更新
$order = Order::create(['user_id' => 1, 'total' => '99.00', 'status' => 'pending']);
$order->update(['status' => 'paid']);

// 关联写入
$order->items()->create(['sku' => 'PHP-1', 'qty' => 2]);
```

**陷阱**: `with()` 预加载是防 N+1 的第一手段；`$fillable` 之外的字段 `create()` 会静默丢弃；`casts` 成枚举后读写均为 enum 实例，DB 中存 backing 值。

## 3. Artisan 常用命令

```bash
# 项目脚手架
composer create-project laravel/laravel app-demo   # 或 laravel new app-demo
php artisan install:api                            # 启用 API 路由 + Sanctum

# 代码生成
php artisan make:model Order -mf                   # 模型 + 迁移 + 工厂
php artisan make:controller OrderController --resource --model=Order
php artisan make:command SyncOrders                # 自定义命令
php artisan make:job SyncOrder                     # 队列任务

# 数据库
php artisan migrate                                # 执行迁移
php artisan migrate:fresh --seed                   # 重建 + 种子（⚠️ 清库，勿在生产随意执行）
php artisan db:seed

# 运行与维护
php artisan serve                                  # 开发服务器
php artisan queue:work                             # 队列消费者
php artisan schedule:work                          # 本地跑调度器
php artisan route:list                             # 路由清单排查
php artisan tinker                                 # 交互式 REPL
```

**陷阱**: `migrate:fresh` 直接删表重建，生产库严禁；自定义命令放在 `app/Console/Commands/` 会被自动发现，无需手动注册。

## 4. 服务容器与依赖注入

**定义**: IoC 容器管理类依赖的解析与生命周期；`app()` 全局获取，构造器/方法注入为推荐用法。

```php
// 绑定：接口 → 实现（AppServiceProvider::register）
$this->app->bind(PaymentGateway::class, StripeGateway::class);     // 每次新实例
$this->app->singleton(Clock::class, SystemClock::class);           // 单例
$this->app->scoped(TenantContext::class);                          // 请求/队列任务内单例

// 使用：构造器注入即可，容器自动解析整条依赖链
final class OrderService
{
    public function __construct(
        private readonly PaymentGateway $gateway,   // 自动得到 StripeGateway
    ) {}
}

// 上下文绑定：同一接口在不同类中注入不同实现
$this->app->when(ReportService::class)
    ->needs(HttpClient::class)
    ->give(fn () => new SlowHttpClient());
```

**陷阱**: `bind` 的闭包每次调用都执行，重对象（HTTP client、连接池）必须 `singleton`/`scoped`；容器外 `new` 出来的类不会自动注入——入口必须来自容器（路由/Job/命令）。

## 5. 配置与环境

```php
config('app.timezone');              // 读配置（点语法）
env('QUEUE_CONNECTION');             // ⚠️ 仅允许在 config/*.php 中调用
Cache::remember('key', 300, fn () => heavy());   // 缓存 + 记住模式
```

**陷阱**: `config:cache` 后 `.env` 不再对运行时可见，任何在业务代码里 `env()` 的写法都会拿到 null——一律先在 config 文件映射，业务读 `config()`。

## 陷阱速查

- **N+1**：关联访问前检查是否 `with()` 预加载，`Model::preventLazyLoading()` 可让调试期直接抛错
- **时区**：`app.timezone` 默认 UTC，DB 存 UTC、展示层转换是标准做法
- **队列与单例**：`singleton` 中持有请求态数据会在队列复用时"串单"，跨请求状态用 `scoped`

## 相关文档

- 📄 **[Symfony 核心速查](./02-symfony-essentials.md)** — 对照学习另一主流框架
- 📄 **[Composer 生态精选](../library-guides/02-composer-ecosystem.md)** — Laravel 周边标准工具链
- 📄 **[常见错误排查](../quick-references/02-troubleshooting.md)** — env()/配置类问题速查
