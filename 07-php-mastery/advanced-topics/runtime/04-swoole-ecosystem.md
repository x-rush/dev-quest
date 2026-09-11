# Swoole 协程生态：协程调度与 Hyperf

> **文档简介**: 介绍 Swoole 的协程调度模型与一键协程化机制，简述 Hyperf 框架生态，并给出"Swoole 协程路线 vs Workerman 多进程路线"的选型对比——PHP 并发世界的另一极
>
> **目标读者**: 理解 [常驻内存模型](./01-fpm-vs-resident.md) 与 [Workerman 原理](./02-workerman-principles.md)、想评估协程路线的开发者
>
> **前置知识**: [Fibers 教程](../../basics/07-advanced-features.md)（协程的语法层原语）、TCP 基础

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#Swoole` `#协程` `#Hyperf` `#并发` `#常驻内存` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 解释协程如何用"用户态调度"把阻塞 I/O 变成并发
- ✅ 说明"一键协程化"（hook）为什么让同步写法的库也能并发
- ✅ 用 Channel/WaitGroup 表达协程间的协作
- ✅ 在 Swoole 与 Workerman 两条路线间做有依据的选型

## 🔍 核心概念

### 概念一：协程调度——把"等"变成"让"

**定义**: 协程是用户态的轻量执行单元。协程在发起 I/O 时**主动让出**执行权（yield），调度器切到同进程内其他就绪协程；I/O 完成后由调度器把协程**恢复**（resume）到断点继续。成千上万个"正在等数据库返回"的协程，实际只占用极少量线程。

```text
FPM/Workerman 多进程视角：  慢 I/O = 进程空等 = 并发能力被占用
Swoole 协程视角：          慢 I/O = 让出执行权 = 等待期间服务其他连接
```

**关键特性**:

- **用户态切换**：协程切换不进内核，成本远低于进程/线程切换，单进程可轻松容纳上万协程
- **PHP 语法层的对应物是 Fiber**（8.1+）：Fiber 定义了"可挂起/恢复"的语言原语，Swoole 的协程是 C 扩展层的独立实现（性能更好、与内置服务深度集成），概念同源
- **调度发生在 I/O 边界**：CPU 计算不会自动让出——协程世界里"长时间循环计算"同样会卡住整个事件循环，纪律与 Workerman 一致

### 概念二：一键协程化（hook）——同步写法，异步执行

**定义**: Swoole 通过 hook 机制把常用阻塞库（PDO、MySQLi、Redis、curl、file 操作等）的阻塞调用在运行时替换为协程版本：代码保持同步写法，执行时自动让出。

```php
<?php

Co::set(['hook_flags' => SWOOLE_HOOK_ALL]);   // 一键协程化：尽量放在入口最前

Co\run(function (): void {
    $start = microtime(true);

    // 两个"同步风格"的请求，实际并发执行
    go(function (): void {
        $pdo = new PDO('mysql:host=db;dbname=app', 'user', 'pass');  // 让出点
        $pdo->query('SELECT SLEEP(1)');                              // 等 1s，让出
    });

    go(function (): void {
        $ch = curl_init('https://httpbin.org/delay/1');              // 等 1s，让出
        curl_exec($ch);
    });

    // 总耗时 ≈ 1s 而非 2s：等待重叠了
    co::sleep(1.2);
    echo 'elapsed: ', round(microtime(true) - $start, 2), 's', PHP_EOL;
});
```

**关键特性**:

- **不用改业务代码**：这是协程路线对比"回调式异步"的决定性优势——老库、老写法直接受益
- **代价是隐式切换**：两个语句之间可能插入其他协程的执行，"跨等待的全局状态"不再可靠（呼应[状态泄漏](./01-fpm-vs-resident.md)）

### 概念三：协程间协作原语

**定义**: `go()` 创建协程；`Channel` 是协程间的消息队列（生产者/消费者）；`WaitGroup` 等待一组协程完成；`defer` 注册协程退出时执行的清理逻辑。

```php
<?php

Co\run(function (): void {
    $chan = new Swoole\Coroutine\Channel(1);       // 容量 1 的管道

    go(function () use ($chan): void {
        $chan->push(['event' => 'task-done']);     // 生产
    });

    $msg = $chan->pop();                           // 消费（无数据时让出等待）
    var_export($msg);

    $wg = new Swoole\Coroutine\WaitGroup();
    for ($i = 0; $i < 3; $i++) {
        $wg->add();
        go(function () use ($wg, $i): void {
            defer(function () use ($wg): void { $wg->done(); });  // 确保计数回收
            co::sleep(0.1);                        // 模拟并发 I/O
        });
    }
    $wg->wait();                                   // 等全部协程结束
});
```

## 💻 代码示例

### 示例：Swoole HTTP 服务（常驻 + 协程）

```php
<?php

$http = new Swoole\Http\Server('0.0.0.0', 9501);

$http->on('request', function (Swoole\Http\Request $request, Swoole\Http\Response $response): void {
    // 每个回调自动运行在协程中；这里的 Redis 调用会在等待时让出
    $redis = new Swoole\Coroutine\Redis();
    $redis->connect('127.0.0.1', 6379);
    $hits = $redis->incr('http:hits');

    $response->header('content-type', 'application/json');
    $response->end(json_encode(['hits' => $hits]));
});

$http->start();   // 常驻：进程不随请求退出
```

**关键点解析**:

- 与 Workerman 的 `onMessage` 相同的常驻纪律（单例/静态状态警惕），多了一层协程语义
- `Swoole\Coroutine\Redis` 等协程客户端与 hook 版同步客户端都可用，团队可按场景选择

## 🎨 最佳实践

### ✅ 推荐做法

- **连接池化一切外设**：Hyperf 内置 MySQL/Redis 连接池，避免"每协程新建连接"打垮下游
- **协程上下文存请求态**：用户/租户等请求级数据放协程上下文（`Swoole\Coroutine::getContext()`），不放全局/静态
- **压测内存曲线**：常驻 + 协程的服务按小时级压测观察内存，纳入 CI 或值班巡检

### ❌ 避免陷阱

- **陷阱 1**：CPU 密集循环不让出——协程调度发生在 I/O 边界，纯计算会饿死同进程其他协程
- **陷阱 2**：hook 后以为"绝对安全"——部分扩展/库不在 hook 覆盖内，混用阻塞调用会拖垮事件循环
- **陷阱 3**：把 Laravel 组件直接搬进协程环境——大量 illuminate 组件假设"进程=请求"，需使用明确支持协程的框架层（如 Hyperf）

## 🔍 对比：Swoole 协程 vs Workerman 多进程

| 维度 | Swoole 路线 | Workerman/Webman 路线 |
|------|------------|----------------------|
| 实现层 | C 扩展（phpize 安装） | 纯 PHP（composer 即用） |
| 并发原语 | 单进程内协程（万级并发连接） | 多进程 + 事件循环（并发=进程数×连接数） |
| 阻塞库兼容 | hook 一键协程化，同步写法直接并发 | 必须异步客户端或踢出事件循环 |
| 心智负担 | 协程切换语义（隐式让出） | 进程模型语义（内存不共享） |
| 生态代表 | Hyperf、imi | Webman |
| 部署要求 | 需安装并匹配扩展版本 | 无扩展依赖，跨环境最省事 |
| Windows 支持 | 不支持（Linux/macOS） | 支持（开发环境友好） |

**选型信号**: 大量并发慢 I/O（网关聚合、爬虫、推送）且追求单机吞吐 → Swoole 路线；希望零扩展部署、业务规模中等、或需要长连接但并发量可控 → Workerman/Webman 路线。两条路线**没有绝对优劣**，都是 FPM 之外的"另一种运行模型"。

## ❓ 常见问题

### Q1: Hyperf 是什么？和 Laravel 什么关系？

**A**: Hyperf 是基于 Swoole/Swow 的协程框架：注解路由、依赖注入、连接池、协程客户端开箱即用，并有 gRPC/服务治理等微服务组件。它不兼容 Laravel 应用代码，但组件思想高度相似——写过 Laravel 的团队上手的是"概念"而不是"代码"。

### Q2: Laravel 能用 Swoole 吗？

**A**: 可以通过 Laravel Octane 让 Laravel 应用运行在 Swoole/OpenSwoole/RoadRunner/FrankenPHP 之上，从而获得常驻内存能力。但按[Laravel 官方文档](https://laravel.com/docs/octane)的要求，必须先完成状态审计（单例、容器注入、静态属性），这正是 [FPM vs 常驻](./01-fpm-vs-resident.md) 第三节的清单。

## 🔄 文档交叉引用

### 相关文档

- 📄 **[FPM vs 常驻内存](./01-fpm-vs-resident.md)** — 协程收益与状态泄漏的模型背景
- 📄 **[Workerman 原理](./02-workerman-principles.md)** — 对比项：多进程事件循环路线
- 📄 **[Webman 实战](./03-webman-practice.md)** — 对比项：Workerman 路线的框架实践
- 📄 **[Fibers（basics/07）](../../basics/07-advanced-features.md)** — PHP 语言层的协程原语

### 外部资源

- Swoole 官方文档：https://wiki.swoole.com/
- Hyperf 官方文档：https://hyperf.wiki/
- Laravel Octane：https://laravel.com/docs/octane

## 📝 总结

### 核心要点回顾

1. 协程把"阻塞等待"变成"让出执行权"，单进程承载万级并发连接
2. hook 一键协程化让同步写法获得异步执行——收益与"隐式切换"风险同源
3. Swoole 与 Workerman 是常驻内存下的两条工程路线，按 I/O 形态、部署约束与生态选型

### 学习成果检查

- [ ] 能向同事解释"协程为什么不用多进程/多线程就能高并发"
- [ ] 能说出 Channel 与 WaitGroup 各解决什么问题
- [ ] 能给自己的场景在 FPM / Workerman / Swoole 三条路线中做出并论证选型

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
