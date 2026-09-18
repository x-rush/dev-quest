# 缓存策略与队列调优

> **文档简介**: 用缓存扛住读流量、用队列扛住写洪峰——缓存键设计、击穿防护、原子锁与队列 worker 的生产级配置
>
> **目标读者**: 已优化查询、需要支撑更高并发的开发者
>
> **前置知识**: [查询优化](./01-query-optimization.md)、[生态集成：缓存](../../frameworks/03-ecosystem-integration.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#缓存` `#Redis` `#队列` `#原子锁` `#性能` |
| **更新日期** | `2026年9月` |

</details>

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
3. 用标签组批量失效：`Cache::tags(['orders'])->flush()`（具体支持情况依驱动；file、database、dynamodb 不支持标签）

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
            // 获锁后再次查缓存，避免等待期间已由别的请求重建
            $orders = Cache::get($cacheKey) ?? Order::where('user_id', $userId)
                ->latest()->forPage($page, 20)->get();
            Cache::put($cacheKey, $orders, now()->addMinutes(10));
        } finally {
            $lock->release();
        }
    } else {
        abort(503, '缓存正在重建，请稍后重试'); // 明确失败；应用可另设有界重试或旧值存储
    }
}
```

框架把这一模式封装为原语：`Cache::flexible(key, [新值TTL, 旧值TTL], 回调)` 会优先返回未过期的新值、必要时返回仍在宽限期的旧值，新项目优先使用。

## 3. 队列：worker 配置的语义

```bash
# Bash：续行反斜杠后不能追加注释
php artisan queue:work redis \
    --queue=high,default \
    --sleep=3 --tries=3 --backoff=30 \
    --timeout=120 --max-time=3600 --memory=256
```

生产部署要点：

```ini
; Supervisor 托管 + 代码发布后重启 worker（worker 是常驻进程，跑的是旧代码）
[program:laravel-worker]
command=php /var/www/app/current/artisan queue:work redis --max-time=3600
process_name=%(program_name)s_%(process_num)02d
numprocs=4
autorestart=true
stopwaitsecs=180
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
    public array $backoff = [10, 60, 300, 600];   // 分段退避：给上游恢复窗口
    public int $timeout = 120;                    // 任务超时；依赖运行环境支持，HTTP/I/O 仍需自身超时

    public function failed(?\Throwable $e): void   // 重试耗尽后调用
    {
        if ($e !== null) { report($e); } // 按项目日志/监控配置上报
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

<!-- full-library-explanation -->
## 用故障时间线理解缓存与队列

前置是事务、缓存过期和任务重试。缓存回源存在竞态：读请求取得旧数据，写请求更新数据库并删缓存，读请求随后又把旧数据写回。TTL 只限制部分陈旧窗口，写后删缓存也不自动保证强一致；价格结算、权限判断等关键决策应读取可靠来源。

持有缓存锁的时间超过租期时，第二个进程可能重新获得锁，因此“拿锁”不等于业务恰好执行一次。队列也是如此：扣款成功后进程在确认任务前退出，任务会重投。使用稳定业务幂等键、唯一约束和支付方幂等接口，把重复请求映射到已有结果，不能仅用短时 Redis 锁防重复扣款。

**练习**：给任务加入“副作用完成后主动抛错”的故障点，重试后验收副作用总数仍为一。配置 worker timeout 小于 Redis/database retry_after，并留出退出时间；Supervisor stopwaitsecs 应大于最长任务时间。外部 HTTP 客户端还需独立超时。只增加 worker 可能压垮数据库，应观察最老任务等待时间及下游容量再扩容。

依据：[队列](https://laravel.com/docs/13.x/queues)、[缓存](https://laravel.com/docs/13.x/cache)。下面带业务占位的片段是设计示意，需要填入查询、回退与任务构造逻辑后才能运行。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

## 🔗 相关文档

- 📄 [Laravel 进阶](../../frameworks/02-laravel-advanced.md) — 任务类与事件的基础写法
- 📄 [查询优化](./01-query-optimization.md) — 上缓存之前的必修课
- 📄 [CI/CD 与可观测性](../../deployment/03-ci-cd-observability.md) — 队列告警接入 Sentry
- 📄 [服务器部署](../../deployment/02-server-deployment.md) — Supervisor 完整配置


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
