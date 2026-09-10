# 缓存策略与队列调优

> **文档简介**: 用缓存扛住读流量、用队列扛住写洪峰——缓存键设计、击穿防护、原子锁与队列 worker 的生产级配置
>
> **目标读者**: 已优化查询、需要支撑更高并发的开发者
>
> **前置知识**: [查询优化](./01-query-optimization.md)、[生态集成：缓存](../../frameworks/03-ecosystem-integration.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#缓存` `#Redis` `#队列` `#原子锁` `#性能` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 设计有命名空间的缓存键与一致的失效策略
- ✅ 用原子锁防缓存击穿
- ✅ 配置生产级队列 worker 并理解重试语义
- ✅ 为队列积压建立告警

## 1. 缓存：键设计决定生死

```php
use Illuminate\Support\Facades\Cache;

// 键 = 主体:标识:参数，参数必须可序列化且排序稳定
$cacheKey = "orders:index:user:{$userId}:page:{$page}:sort:{$sort}";

$orders = Cache::remember($cacheKey, now()->addMinutes(10), fn () =>
    Order::where('user_id', $userId)
        ->latest()
        ->forPage($page, 20)
        ->get(),
);
```

**失效是缓存最难的部分**。三条纪律：

1. 写操作后失效对应键（`Cache::forget()`），而不是靠 TTL 自然过期
2. 键里纳入影响结果的所有输入（含认证主体），否则就是越权读取的洞
3. 用标签组批量失效：`Cache::tags(['orders'])->flush()`（注意 file 驱动不支持）

## 2. 防击穿：原子锁

热点键过期瞬间，大量请求同时穿透到数据库——用锁保证只有一个请求回源：

```php
use Illuminate\Support\Facades\Cache;

$orders = Cache::get($cacheKey);

if ($orders === null) {
    // 拿到锁的请求负责回源重建；拿不到的等待或直接返回旧值/兜底
    $lock = Cache::lock("lock:rebuild:{$cacheKey}", 5);

    if ($lock->get()) {
        try {
            $orders = /* 回源查询 */;
            Cache::put($cacheKey, $orders, now()->addMinutes(10));
        } finally {
            $lock->release();
        }
    } else {
        $orders = /* 短暂等待重试或返回过期数据 */;   // 容忍短暂旧值胜过 DB 雪崩
    }
}
```

框架把这一模式封装为原语：`Cache::flexible(key, [新值TTL, 旧值TTL], 回调)` 会优先返回未过期的新值、必要时返回仍在宽限期的旧值，新项目优先使用。

## 3. 队列：worker 配置的语义

```bash
php artisan queue:work redis \
    --queue=high,default \   # 队列优先级：先消费 high
    --sleep=3 \              # 无任务时休眠秒数
    --tries=3 \              # 兜底重试次数（可被任务类 $tries 覆盖）
    --backoff=30 \           # 重试退避
    --max-time=3600 \        # 1 小时后自杀，由 Supervisor 拉起（释放内存）
    --memory=256             # 超内存自杀，防泄漏
```

生产部署要点：

```ini
; Supervisor 托管 + 代码发布后重启 worker（worker 是常驻进程，跑的是旧代码）
[program:laravel-worker]
command=php /var/www/app/current/artisan queue:work redis --max-time=3600
numprocs=4
autorestart=true
stopwaitsecs=30
```

```bash
# 发布脚本中的固定一步：通知 worker 处理完当前任务后优雅退出
php artisan queue:restart
```

## 4. 重试语义与失败处理

```php
final class ChargeOrder implements ShouldQueue
{
    public int $tries = 5;
    public array $backoff = [10, 60, 300, 600];   // 指数退避：给上游恢复窗口
    public int $timeout = 120;                    // 单任务硬超时

    public function failed(\Throwable $e): void   // 重试耗尽后调用
    {
        report($e);                               // 进 Sentry（deployment/03）
        OrderPaymentFailed::dispatch($this->order);
    }
}
```

**幂等是重试的前提**：任务被重试时可能已部分执行，任务体内必须能安全重入（支付场景见[电商 API](../../projects/03-ecommerce-api.md)的幂等锁设计）。

## 5. 积压监控

```text
告警指标：
- Redis 队列长度（queues:default）持续 > 阈值 → 消费能力不足，扩 numprocs
- failed_jobs 新增速率 → 代码或上游故障，立即介入
- 最老任务等待时间 → 消费延迟的直接体现

一键排障：
php artisan queue:failed              # 列出失败任务
php artisan queue:retry <uuid>        # 修复后重放
php artisan queue:prune-failed --hours=720
```

缓存的读优化与队列的写削峰是互补的两半：前者降低"每秒读"，后者把"瞬时写"摊平到时间轴。两者的容量估算都应来自真实流量画像，而非拍脑袋。

## 🔗 相关文档

- 📄 [Laravel 进阶](../../frameworks/02-laravel-advanced.md) — 任务类与事件的基础写法
- 📄 [查询优化](./01-query-optimization.md) — 上缓存之前的必修课
- 📄 [CI/CD 与可观测性](../../deployment/03-ci-cd-observability.md) — 队列告警接入 Sentry
- 📄 [服务器部署](../../deployment/02-server-deployment.md) — Supervisor 完整配置
