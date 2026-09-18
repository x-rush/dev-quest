# Laravel 核心速查（Laravel 13）

## 概述

Laravel 11 起精简骨架（应用骨架不再自带 app/Http/Kernel.php，框架仍有 HTTP Kernel、默认精简中间件栈），12/13 延续这一形态，本文收录日常开发最高频的四大核心：路由、Eloquent、Artisan、服务容器。条目式组织，供快速查阅。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Laravel` `#路由` `#Eloquent` `#Artisan` `#服务容器` |
| **更新日期** | `2026年9月` |

</details>

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

**陷阱**: 参数名匹配并有对应模型类型提示时，{order} 可按模型路由键隐式绑定（默认通常为 ID），记录不存在直接 404；现代 Laravel 支持可序列化的闭包路由缓存；复杂业务仍宜用控制器，缓存失败应检查实际捕获内容与重复路由名。

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

**陷阱**: `with()` 预加载是防 N+1 的第一手段；`$fillable` 之外的字段 `create()` 会静默丢弃；枚举 cast 读取可得到 enum 实例，赋值可接受对应实例或合法 backing 值，DB 中存 backing 值。

## 3. Artisan 常用命令

```bash
# 项目脚手架
composer create-project laravel/laravel:^13.0 app-demo   # 或 laravel new app-demo
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

**陷阱**: `bind` 的闭包每次调用都执行，重对象是否共享要按状态、安全性与生命周期选择 singleton/scoped；容器外 `new` 出来的类不会自动注入——入口必须来自容器（路由/Job/命令）。

## 5. 配置与环境

```php
config('app.timezone');              // 读配置（点语法）
env('QUEUE_CONNECTION');             // ⚠️ 仅允许在 config/*.php 中调用
Cache::remember('key', 300, fn () => heavy());   // 缓存 + 记住模式
```

**陷阱**: `config:cache` 后 `.env` 不再对运行时可见，env() 仍可能读到真实进程环境变量，但不再加载 .env，不应作为业务配置读取方式——一律先在 config 文件映射，业务读 `config()`。

## 陷阱速查

- **N+1**：关联访问前检查是否 `with()` 预加载，`Model::preventLazyLoading()` 可让调试期直接抛错
- **时区**：`app.timezone` 默认 UTC，DB 存 UTC、展示层转换是标准做法
- **队列与单例**：`singleton` 中持有请求态数据会在队列复用时"串单"，请求或任务专属状态用 scoped，跨请求共享数据应存入合适外部存储

## 相关文档

- 📄 **[Symfony 核心速查](./02-symfony-essentials.md)** — 对照学习另一主流框架
- 📄 **[Composer 生态精选](../library-guides/02-composer-ecosystem.md)** — Laravel 周边标准工具链
- 📄 **[常见错误排查](../quick-references/02-troubleshooting.md)** — env()/配置类问题速查


<!-- full-library-explanation -->
## 沿着一次请求查找框架职责

前置是 PHP 类、HTTP、数据库主键。路由参数约束决定 URL 是否匹配；模型绑定负责查找记录；FormRequest 验证数据；Policy 决定当前用户是否有权操作；Action 或控制器编排业务。找到 Order 不代表当前用户拥有 Order，模型绑定之后仍要授权。

Eloquent 模型既承载数据又提供持久化入口，读取关联属性可能发 SQL。把模型转换成 JSON 时，应控制对外字段与加载关系；数据库有一列不意味着 API 应暴露一列。批量赋值白名单仅限制 fill/create 一类入口，不替代授权，也不防止代码主动给敏感字段赋值。

**练习**：为不存在的订单、他人的订单和自己的订单各发一次请求，预期分别进入 404、拒绝、成功路径。用 route:list 核对中间件，缓存路由前后重复测试；再开启开发期懒加载保护，发现响应序列化过程中隐藏的关联查询。速查中的业务类和方法需由练习项目提供，片段不能整块粘贴注册重复路由。

依据：[Laravel 路由](https://laravel.com/docs/13.x/routing)、[Route 闭包序列化实现](https://github.com/laravel/framework/blob/13.x/src/Illuminate/Routing/Route.php)、[配置](https://laravel.com/docs/13.x/configuration)。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
