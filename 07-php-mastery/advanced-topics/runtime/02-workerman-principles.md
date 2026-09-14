# Workerman 原理：事件驱动 + 多进程模型

> **文档简介**: 拆解 Workerman 的事件循环（EventLoop）、master-worker 多进程模型与连接管理机制，理解"纯 PHP 写出常驻高并发服务"是如何成立的
>
> **目标读者**: 读过 [FPM vs 常驻内存](./01-fpm-vs-resident.md)、想深入常驻运行时内部机制的开发者
>
> **前置知识**: 进程与信号的基本概念、TCP 基础；无需异步编程经验

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#Workerman` `#事件循环` `#多进程` `#常驻内存` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 解释 EventLoop 如何用 I/O 多路复用驱动成百上千连接
- ✅ 描述 Workerman master/worker 进程模型与平滑重启机制
- ✅ 说明连接对象的生命周期与 TCP 粘包的处理方式
- ✅ 写出准确的 Worker/Timer 基础代码

## 🔍 核心概念

### 概念一：EventLoop——一个进程如何同时"看着"几千个连接

**定义**: 事件循环是一个"永不返回的循环"：把关心的 I/O 事件（socket 可读/可写、定时器到点）注册给操作系统（`select`/`epoll`/`Ev` 等），然后反复等待事件发生、逐个执行回调。

```text
while (true) {
    $events = epoll_wait($registered);   // 阻塞直到有事件
    foreach ($events as $event) {
        $event->callback($event->data);  // 派发给业务回调
    }
}
```

**关键特性**:

- **非阻塞 socket**：连接全部设为非阻塞，读不到数据立即返回而不是挂起进程
- **一个进程管多个连接**：事件循环把"等数据"的时间集中交给内核，进程只在真正有数据时干活——这就是不需要每连接一个线程/进程的原因
- **回调里不能阻塞**：一旦某个回调执行 `sleep(10)` 或慢查询，同一进程内**所有**连接都会被卡住——这是事件驱动模型的第一纪律
- **可插拔后端**：Workerman 默认用 PHP 原生 `stream_select`，装有 `event`/`libevent`/`Ev` 扩展时自动切换到性能更好的后端

### 概念二：master-worker 多进程模型

**定义**: Workerman 启动时先 fork 出一个 master 进程与若干 worker 子进程：master 不处理业务，只负责监控 worker（异常退出自动拉起）与转发信号（reload/stop）；每个 worker 独立跑一个事件循环，监听**同一个端口**（由 master 建好监听 socket 后继承）。

```text
php start.php start
  → master 进程：解析配置 → 监听端口 → fork N 个 worker
      ├── worker-0：EventLoop（accept/读写/定时器回调）
      ├── worker-1：EventLoop
      └── worker-N：EventLoop
  → master 持续监控：worker 崩溃即 fork 补位；收到 reload 信号即平滑重启 worker
```

**关键特性**:

- **`$worker->count` 控制进程数**：CPU 密集服务 ≈ CPU 核数；I/O 密集可更高；有连接状态的 WebSocket 服务通常设 1（连接归属单一进程，见"陷阱"）
- **多进程 = 多份内存**：与协程共享内存不同，worker 之间不共享变量，跨进程通信要用 Redis/Queue/UnixSocket 等外部通道
- **平滑重启（reload）**：master 让旧 worker 处理完存量请求后退出，每退出一个即 fork 一个新 worker 补位，逐个置换实现不中断服务的代码更新

### 概念三：连接管理——Connection 对象与 TCP 粘包

**定义**: 每个客户端连接在 worker 内对应一个 `Workerman\Connection\TcpConnection` 对象，从 `onConnect` 到 `onClose` 存活。连接的读写事件由事件循环驱动，业务通过 `onMessage` 回调拿到完整数据。

**关键特性**:

- **生命周期回调**：`onConnect`（连接建立）、`onMessage`（收到数据）、`onClose`（断开，必须在此释放与连接绑定的资源）、`onBufferFull`/`onBufferDrain`（发送缓冲区水位，慢客户端防护）
- **TCP 粘包**：TCP 是字节流不保消息边界。Workerman 用**协议层**解决：内置 `http`、`websocket`、`text`（换行分隔）、`frame`（二进制长度前缀）等协议，也可实现 `Workerman\Protocols\ProtocolInterface` 自定义"拆包规则"——`onMessage` 拿到的永远是拆好的"一条消息"
- **发送即缓冲**：`$connection->send($data)` 先写入发送缓冲区，由事件循环在 socket 可写时刷出，业务无需关心背压细节（极端情况触发 `onBufferFull`）

## 💻 代码示例

### 示例一：最小 HTTP 服务

```php
<?php

use Workerman\Connection\TcpConnection;
use Workerman\Protocols\Http\Request;
use Workerman\Worker;

require_once __DIR__ . '/vendor/autoload.php';

$http = new Worker('http://0.0.0.0:8080');   // 协议写在监听地址里
$http->count = 4;                            // 4 个 worker 进程

$http->onMessage = function (TcpConnection $connection, Request $request): void {
    // $request 是按 http 协议拆好的完整请求对象
    $connection->send('hello, ' . $request->get('name', 'world'));
};

Worker::runAll();   // 启动：fork 进程 + 进入事件循环（阻塞）
```

**关键点解析**:

- `new Worker('http://...')` 一行完成"监听 + 协议解析 + 连接管理"三件事
- 回调注册后由事件循环调用，**不要在回调里写阻塞代码**
- `$request->get()` 读 query 参数；`$request->post()`、`$request->header()`、`$request->rawBody()` 同理

### 示例二：WebSocket 广播与定时器

```php
<?php

use Workerman\Connection\TcpConnection;
use Workerman\Timer;
use Workerman\Worker;

require_once __DIR__ . '/vendor/autoload.php';

$ws = new Worker('websocket://0.0.0.0:2346');
$ws->count = 1;   // 连接有状态：所有连接必须在一个进程内才能互相广播

$ws->onConnect = function (TcpConnection $connection): void {
    $connection->lastPing = time();          // 挂在连接对象上的自定义属性
};

$ws->onMessage = function (TcpConnection $connection, string $data) use ($ws): void {
    foreach ($ws->connections as $client) {  // 当前进程内全部连接
        $client->send($data);                // 广播
    }
};

$ws->onClose = function (TcpConnection $connection): void {
    unset($connection->lastPing);            // 释放连接级资源，防内存累积
};

// 定时器：每 10 秒心跳检查（常驻进程的标配能力）
Timer::add(10, function () use ($ws): void {
    foreach ($ws->connections as $client) {
        if (time() - ($client->lastPing ?? 0) > 60) {
            $client->close();                // 踢掉超时连接
        }
    }
});

Worker::runAll();
```

**关键点解析**:

- `Timer::add($interval, $callback, $args, $persistent)`：第四个参数 `true`（默认）为周期执行，`false` 为一次性
- 常驻进程必须**主动清理连接级状态**：`onClose` 里不释放，对象就随进程一直活着

## 🎨 最佳实践

### ✅ 推荐做法

- **CPU 密集任务踢出事件循环**：图片处理、大 JSON 编码丢给队列（Redis/消息服务），回调里只做投递
- **用 `status` 命令观测**：`php start.php status` 查看各进程连接数、内存、请求量，是常驻服务的基本体检手段
- **守护化 + 开机自启**：生产环境 `php start.php start -d` 并配 systemd 守护

### ❌ 避免陷阱

- **陷阱 1**：在 `onMessage` 里同步调用慢接口——整个进程所有连接一起卡死。I/O 密集场景应考虑协程运行时（见[Swoole 生态](./04-swoole-ecosystem.md)）或异步客户端
- **陷阱 2**：有连接状态的服务把 `count` 设成多进程——连接分散在不同进程，广播/会话互相看不见
- **陷阱 3**：把 FPM 的"代码改了刷新就生效"习惯带过来——常驻进程必须 `php start.php reload` 才加载新代码

## ❓ 常见问题

### Q1: Workerman 是框架吗？

**A**: 不是，它是**常驻运行时/网络库**：提供事件循环、进程管理、连接与协议处理。业务框架是它的上层——Webman 就是官方基于 Workerman 的 MVC 框架（见[下一篇](./03-webman-practice.md)）。

### Q2: 多进程之间内存不共享，会话/数据怎么办？

**A**: 这是多进程模型的明确取舍：跨进程状态一律外置（Redis、数据库、消息队列）。需要进程内共享大量状态时，协程模型（单进程内成千上万连接）更合适，这是两者选型的核心差异点。

## 🔄 文档交叉引用

### 相关文档

- 📄 **[FPM vs 常驻内存](./01-fpm-vs-resident.md)** — 本篇机制所处的模型背景
- 📄 **[Webman 实战](./03-webman-practice.md)** — 在 Workerman 之上的完整框架实践
- 📄 **[Swoole 协程生态](./04-swoole-ecosystem.md)** — 与多进程事件循环相对的协程路线

### 外部资源

- Workerman 官方文档：https://www.workerman.net/doc/workerman/
- Webman 官方文档：https://www.workerman.net/doc/webman/

## 📝 总结

### 核心要点回顾

1. **EventLoop**：I/O 多路复用 + 非阻塞 socket + 回调派发，"回调里绝不阻塞"是第一纪律
2. **master-worker**：master 管进程与信号，worker 各自跑事件循环，`count` 决定并发形态
3. **连接管理**：Connection 对象贯穿连接生命周期，协议层解决粘包，`onClose` 释放资源

### 学习成果检查

- [ ] 能解释"为什么一个进程能同时服务几千个连接"
- [ ] 能说出 reload 平滑重启的工作过程
- [ ] 能判断自己的服务该设几个 worker 进程

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
