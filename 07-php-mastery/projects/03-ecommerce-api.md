# 高级项目：电商 API（购物车 + 订单 + 支付流程）

> **文档简介**: 综合运用事务、状态机与队列，实现购物车→下单→支付的完整链路，重点是"钱不丢单不错"的一致性设计
>
> **目标读者**: 已完成博客平台、需要设计多步业务流程的开发者
>
> **前置知识**: [博客平台](./02-blog-platform.md)、[Laravel 进阶](../frameworks/02-laravel-advanced.md)、[PHP 高级特性](../basics/07-advanced-features.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Laravel` `#电商` `#事务` `#状态机` `#支付` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

- ✅ 用数据库事务保证"扣库存 + 建订单"原子性
- ✅ 用枚举状态机管理订单生命周期
- ✅ 把支付回调做成队列化的异步确认流程
- ✅ 理解幂等：同一笔回调重复到达不重复扣款

## 1. 核心表结构

```text
products  (id, name, price_cents, stock)
carts     (id, user_id)
cart_items(id, cart_id, product_id, quantity)
orders    (id, user_id, total_cents, status, paid_at)
order_items(id, order_id, product_id, quantity, unit_price_cents)
payment_callbacks (id, trade_no, payload, status)
```

**金额一律用整数分（`*_cents`）存储**，浮点数算钱是经典事故源。

## 2. 下单：事务 + 行锁

```php
// app/Services/PlaceOrderService.php
namespace App\Services;

use App\Enums\OrderStatus;
use App\Models\Cart;
use App\Models\Order;
use App\Models\Product;
use Illuminate\Support\Facades\DB;

final class PlaceOrderService
{
    public function execute(Cart $cart): Order
    {
        // transaction 包裹"读库存→校验→扣减→建单"，任何一步抛异常整体回滚
        return DB::transaction(function () use ($cart): Order {
            // 购物车明细不锁——cart_items 不是发生竞争写入的行
            $items = $cart->items()->with('product')->get();

            $total = 0;
            $order = Order::create([
                'user_id'     => $cart->user_id,
                'status'      => OrderStatus::PendingPayment,
                'total_cents' => 0,
            ]);

            foreach ($items as $item) {
                // 锁必须落在"发生竞争写入的行"上：超卖竞争的是 products.stock，
                // 两张不同购物车抢同一商品时，锁 cart_items 挡不住并发扣减。
                // 先 SELECT ... FOR UPDATE 锁产品行，再读最新库存并扣减
                // （多商品下单按 id 升序加锁可避免交叉死锁，此处从简）
                $product = Product::whereKey($item->product_id)->lockForUpdate()->first();

                abort_if($product->stock < $item->quantity, 409, "库存不足：{$product->name}");

                $product->decrement('stock', $item->quantity);

                $order->items()->create([
                    'product_id'       => $product->id,
                    'quantity'         => $item->quantity,
                    'unit_price_cents' => $product->price_cents, // 快照下单时价格
                ]);

                $total += $product->price_cents * $item->quantity;
            }

            $order->update(['total_cents' => $total]);
            $cart->items()->delete(); // 清空购物车

            return $order;
        });
    }
}
```

## 3. 订单状态机

```php
// app/Enums/OrderStatus.php
namespace App\Enums;

enum OrderStatus: string
{
    case PendingPayment = 'pending_payment';
    case Paid           = 'paid';
    case Shipped        = 'shipped';
    case Cancelled      = 'cancelled';

    /** 合法流转表：状态机由数据定义，而非散落的 if */
    public function canTransitionTo(self $next): bool
    {
        return match ($this) {
            self::PendingPayment => $next === self::Paid || $next === self::Cancelled,
            self::Paid           => $next === self::Shipped,
            default              => false,   // 终态不可再流转
        };
    }
}
```

```php
// 状态流转统一走这个方法，越权跳转直接抛异常
public function transition(Order $order, OrderStatus $next): void
{
    if (! $order->status->canTransitionTo($next)) {
        throw new \DomainException("非法状态流转: {$order->status->value} -> {$next->value}");
    }
    $order->update(['status' => $next]);
}
```

## 4. 支付回调：幂等 + 异步

```php
// app/Http/Controllers/PaymentWebhookController.php
use App\Jobs\ProcessPaymentCallback;
use App\Models\PaymentCallback;

public function handle(\Illuminate\Http\Request $request): \Illuminate\Http\JsonResponse
{
    $data = $request->validate([
        'order_id'     => ['required', 'integer'],
        'trade_no'     => ['required', 'string'],   // 支付渠道流水号
        'amount_cents' => ['required', 'integer'],
    ]);

    // 回调只做三件事：验签 → 落一条"待处理回调"记录 → 派发队列任务后立刻 200
    $callback = PaymentCallback::create([
        'trade_no' => $data['trade_no'],
        'payload'  => $request->all(),
        'status'   => 'received',
    ]);

    ProcessPaymentCallback::dispatch($callback);

    return response()->json(['ok' => true]);   // 快速应答，避免渠道方频繁重试
}
```

```php
// app/Jobs/ProcessPaymentCallback.php（节选）
final class ProcessPaymentCallback implements ShouldQueue
{
    public int $tries = 5;

    public function handle(PaymentCallback $callback): void
    {
        // 幂等锁：同一流水号只允许一个实例在处理（10 秒自动过期兜底）
        $lock = \Illuminate\Support\Facades\Cache::lock("payment:{$callback->trade_no}", 10);
        if (! $lock->get()) {
            return;   // 已有并发实例在处理，直接跳过
        }

        try {
            // 金额校验放在事务外：金额不符属"不可重试的永久失败"，
            // 标记回调 rejected 后抛领域异常。Job 里绝不能用 abort(409)——
            // HTTP 异常会被队列当作任务失败重试满 5 次后进 failed_jobs，
            // 且 409 语义只对 HTTP 响应才有意义
            $order = Order::findOrFail($callback->payload['order_id']);
            if ($order->total_cents !== (int) $callback->payload['amount_cents']) {
                $callback->update(['status' => 'rejected']);
                throw new \DomainException('回调金额与订单不符');
            }

            DB::transaction(function () use ($callback): void {
                $order = Order::whereKey($callback->payload['order_id'])->lockForUpdate()->firstOrFail();

                if ($order->status !== OrderStatus::PendingPayment) {
                    return;   // 幂等：已支付的订单忽略重复回调
                }

                // 状态流转必须走状态机：直接 update(['status' => ...]) 会绕过 transition() 的合法性校验
                transition($order, OrderStatus::Paid);
                $order->update(['paid_at' => now()]);
                $callback->update(['status' => 'processed']);
            });
        } finally {
            $lock->release();   // 必须 release：漏释放要等 10 秒过期，期间同流水号的回调全部被跳过
        }
    }
}
```

## 5. 设计要点复盘

| 风险 | 对策 |
|------|------|
| 并发超卖 | 事务内锁**发生竞争写入的行**（products.stock，`lockForUpdate`），或乐观锁 version 字段 |
| 回调乱序/重复 | 幂等锁 + 状态机校验（统一走 `transition()`） |
| 幂等锁泄漏 | `Cache::lock()->get()` 之后必须在 `finally` 中 `release()`（或改用 `->block()`） |
| 回调金额不符 | 队列中抛领域异常并标记回调 rejected，不做无意义的重试 |
| 回调处理慢拖垮接口 | 落库后异步队列处理 |
| 金额精度 | 全程整数分 |

下一步：给关键路径补 Feature 测试（[Feature 测试与数据库测试](../testing/03-feature-testing.md)），性能瓶颈定位见[查询优化](../advanced-topics/performance/01-query-optimization.md)。

## 🔗 相关文档

- 📄 [类型系统与现代 OOP](../reference/language-concepts/03-types-oop-modern.md) — 枚举与 readonly 语法
- 📄 [Laravel 核心速查](../reference/framework-essentials/01-laravel-essentials.md) — Eloquent 与事务条目
- 📄 [缓存策略与队列调优](../advanced-topics/performance/02-caching-queues.md) — 原子锁与队列重试细节
- 📄 [生产级 Laravel 应用](./04-production-laravel-app.md) — 本项目上生产的改造清单
