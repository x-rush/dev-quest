# 查询优化：N+1、预加载与索引

> **文档简介**: 系统排查 Laravel 数据层性能——定位 N+1、正确预加载、为查询模式建索引并用 EXPLAIN 验证
>
> **目标读者**: 接口响应慢、需要从 SQL 层找原因的开发者
>
> **前置知识**: [Laravel 进阶](../../frameworks/02-laravel-advanced.md)、[Laravel 核心速查](../../reference/framework-essentials/01-laravel-essentials.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#N+1` `#预加载` `#索引` `#EXPLAIN` `#性能` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 识别并消灭 N+1 查询
- ✅ 掌握 with/withCount/withExists 的适用场景
- ✅ 按"查询模式"而非"直觉"设计索引
- ✅ 用 EXPLAIN 与慢查询日志闭环验证

## 1. N+1：成因与识别

```php
// 反面教材：1 次查文章 + 每篇文章 1 次查作者 = N+1
$posts = Post::all();
foreach ($posts as $post) {
    echo $post->author->name;   // 触发延迟加载，循环内发 SQL
}
```

识别手段（按环境递进）：

```php
// ① 开发期兜底：未预加载直接抛异常（放进 AppServiceProvider::boot）
Model::preventLazyLoading(! app()->isProduction());

// ② 抓现行：监听循环内查询
DB::listen(fn ($query) => Log::debug($query->sql));

// ③ 工具定位：Debugbar / Telescope 的 SQL 面板按请求聚合
```

## 2. 预加载的正确姿势

```php
// 基础：两条 SQL 解决 N+1（IN 查询）
$posts = Post::with('author')->get();

// 带约束的预加载：只取每篇最新 3 条评论
$posts = Post::with(['comments' => fn ($q) => $q->latest()->limit(3)])->get();

// 聚合计数：附加列而非整条关联记录
$posts = Post::withCount('comments')->get();          // comments_count
$posts = Post::withCount(['comments as hot_comments' => fn ($q) => $q->where('likes', '>', 10)])->get();

// 只判断存在性，比 count 更便宜
$posts = Post::withExists('comments')->get();         // comments_exists

// 嵌套预加载 + 指定列（列裁剪减少传输与内存）
$posts = Post::with('author:id,name')->get();

// 预加载后按需取出，避免再次触发懒加载
$first = $posts->first()->getRelation('author');
```

**经验法则**：列表页需要什么就 `with` 什么；详情页关系统计用 `withCount`；排序/过滤用数据库子查询而不是 PHP 端 collection 操作。

## 3. 索引：为查询模式而建

```php
Schema::create('orders', function (Blueprint $table): void {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('status', 16);
    $table->timestamp('created_at');
    $table->timestamp('paid_at')->nullable();

    // 1. 等值过滤列 + 低区分度列建普通索引
    $table->index('status');
    // 2. 复合索引遵循最左前缀：此索引同时服务
    //    WHERE user_id = ? 与 WHERE user_id = ? AND status = ?
    $table->index(['user_id', 'status']);
    // 3. 排序查询：索引列顺序与 ORDER BY 一致，避免 filesort
    $table->index(['user_id', 'created_at']);
});
```

判定某索引是否被真正使用：

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 1 AND status = 'paid' ORDER BY created_at DESC;
-- 关注 type（目标 ref/range，拒绝 ALL 全表扫）与 rows（预估扫描行数）
-- Extra 出现 Using filesort / Using temporary 通常是排序列未进索引
```

索引不是越多越好：每个索引都拖慢写入并占用存储；**删除从未命中的索引**与新增同等重要（用 `sys.schema_unused_indexes` 或慢查询日志佐证）。

## 4. 大结果集处理

```php
// 逐块处理 100 万行：chunkById 不会一次载入内存，且用主键游标避免偏移量漂移
Order::query()
    ->where('status', 'paid')
    ->chunkById(1000, function ($orders): void {
        foreach ($orders as $order) {
            // 逐条处理；注意在回调内更新本表时用 whereKey 精确定位
        }
    });

// 只需要遍历、内存受限：cursor 走 PDO 流式读取（保持一个连接）
foreach (Order::where('status', 'paid')->cursor() as $order) {
}

// 聚合永远下推数据库：collection 的 sum() 是把数据拉回 PHP 再算
Order::where('status', 'paid')->sum('total_cents');
```

## 5. 优化闭环

```text
慢（APM/用户反馈）→ 定位（Telescope/慢查询日志）
  → 归因（N+1? 缺索引? 大结果集? 拉回 PHP 计算?）
  → 处理（with / index / chunk / aggregate 下推）
  → 验证（EXPLAIN + 压测对比）→ 固化（preventLazyLoading + 测试）
```

缓解不了再考虑缓存层（见[缓存策略与队列调优](./02-caching-queues.md)）——缓存是"用复杂度换读性能"，先修查询再上缓存。

## 🔗 相关文档

- 📄 [类型系统与现代 OOP](../../reference/language-concepts/03-types-oop-modern.md) — 闭包签名与可空类型
- 📄 [Laravel 进阶](../../frameworks/02-laravel-advanced.md) — 关系定义与高级查询入门
- 📄 [缓存策略与队列调优](./02-caching-queues.md) — 读放大之后的下一级优化
- 📄 [Feature 测试与数据库测试](../../testing/03-feature-testing.md) — 防止回归的测试护栏
