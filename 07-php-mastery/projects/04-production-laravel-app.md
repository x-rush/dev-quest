# 毕业项目：生产级 Laravel 应用

> **文档简介**: 把一个"能跑"的 Laravel 应用改造成"敢上线"的生产级工程——分层架构、配置治理、可观测性与发布清单
>
> **目标读者**: 已完成三个递进项目、准备把作品部署上线的开发者
>
> **前置知识**: [电商 API](./03-ecommerce-api.md)、[架构解析](../advanced-topics/architecture/01-laravel-architecture.md)、[Docker 部署](../deployment/01-docker-deployment.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#Laravel` `#生产化` `#分层架构` `#可观测性` `#发布清单` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

- ✅ 把胖控制器重构为 Action + DTO 分层
- ✅ 统一配置、日志与异常响应规范
- ✅ 接入限流、健康检查等生产护栏
- ✅ 手持一份可勾选的上线清单

## 1. 分层架构：让控制器只做编排

```text
Request → FormRequest（验证）
        → Controller（编排，<10 行）
        → Action/Service（业务规则）
        → Model（数据访问）
        → Job/Event（异步副作用）
```

```php
// app/Actions/Orders/CreateOrderAction.php —— 一个 Action 只做一件事
namespace App\Actions\Orders;

use App\DataTransferObjects\OrderData;
use App\Models\Order;
use App\Models\User;
use App\Jobs\CreateOrderAudit;
use Illuminate\Support\Facades\DB;

final class CreateOrderAction
{
    public function execute(User $user, OrderData $data): Order
    {
        return DB::transaction(function () use ($user, $data): Order {
            $order = $user->orders()->create([...]);   // 核心规则（示意）

            CreateOrderAudit::dispatch($order);        // 副作用全部异步

            return $order;
        });
    }
}
```

```php
// 控制器瘦身后的样子
final class OrderController extends Controller
{
    public function __construct(private readonly CreateOrderAction $createOrder) {}

    public function store(StoreOrderRequest $request): OrderResource
    {
        return new OrderResource(
            $this->createOrder->execute($request->user(), OrderData::fromRequest($request)),
        );
    }
}
```

DTO 用 readonly 属性承载数据（`final readonly` 类为 PHP 8.2+ 特性），杜绝数组传来传去：

```php
// app/DataTransferObjects/OrderData.php
namespace App\DataTransferObjects;

final readonly class OrderData
{
    public function __construct(
        public int $productId,
        public int $quantity,
        public ?string $couponCode = null,
    ) {}
}
```

## 2. 配置与环境治理

- 所有可变参数进 `config/` + `.env`，**代码里不出现硬编码开关**
- `config:cache` 之后 `env()` 在运行时返回 null——配置读取一律走 `config('x.y')`
- 敏感值用 secret manager 注入，不进仓库

```php
// config/services.php 自定义段
'payment' => [
    'gateway' => env('PAYMENT_GATEWAY', 'mock'),
    'timeout' => (int) env('PAYMENT_TIMEOUT', 5),
],
// 使用处：config('services.payment.timeout')
```

## 3. 统一异常与日志

```php
// bootstrap/app.php（Laravel 11+ 集中配置异常渲染，13 延续）
use Illuminate\Foundation\Application;
use Illuminate\Http\Request;

return Application::configure(basePath: dirname(__DIR__))
    ->withExceptions(function ($exceptions): void {
        $exceptions->render(function (\DomainException $e, Request $request) {
            if ($request->is('api/*')) {
                return response()->json([
                    'error' => ['code' => 'domain_violation', 'message' => $e->getMessage()],
                ], 422);
            }
        });
    })->create();
```

日志纪律：业务关键路径打 `warning` 起；错误必须带上下文（订单号、trace id），绝不打整段请求体（可能含密码）。

## 4. 生产护栏

```php
// routes/api.php —— 限流：按用户 60 次/分钟
Route::middleware(['auth:sanctum', 'throttle:60,1'])->group(function (): void {
    Route::apiResource('orders', OrderController::class);
});

// 健康检查：负载均衡探针的最小依赖端点
Route::get('/health', fn () => response()->json([
    'status' => 'ok',
    'time'   => now()->toIso8601String(),
]));
```

其余护栏：HTTPS 强制（`URL::forceScheme('https')`）、`APP_DEBUG=false`、CORS 白名单收敛、队列失败告警接入 Sentry（见[CI/CD 与可观测性](../deployment/03-ci-cd-observability.md)）。

## 5. 上线清单（发布前逐项勾选）

```text
[ ] phpstan level 6 通过（frameworks/04-devtools.md）
[ ] 全量测试通过且覆盖核心业务流（testing/03-feature-testing.md）
[ ] migrate 已在灰度库演练，down() 可回滚
[ ] optimize:clear 后重新 php artisan optimize
[ ] 队列 worker 由 Supervisor 托管，failed_jobs 有告警
[ ] Sentry 报 issue 到值班群；/health 接入探活
[ ] 回滚预案：上一个镜像 + migrate:rollback 演练通过
```

部署执行细节见 [Docker 部署](../deployment/01-docker-deployment.md) 与 [服务器部署](../deployment/02-server-deployment.md)。

## 🔗 相关文档

- 📄 [服务容器与架构模式](../advanced-topics/architecture/01-laravel-architecture.md) — 依赖注入与分层的原理支撑
- 📄 [安全实践](../advanced-topics/security/01-security-practices.md) — 上线前安全自查
- 📄 [CI/CD 与可观测性](../deployment/03-ci-cd-observability.md) — 流水线与监控落地
- 📄 [PHP 故障排除](../reference/quick-references/02-troubleshooting.md) — 线上问题应急速查
