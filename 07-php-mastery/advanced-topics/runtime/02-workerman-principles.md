# Workerman 原理：事件驱动 + 多进程模型

> **文档简介**: 拆解 Workerman 的事件循环（EventLoop）、master-worker 多进程模型与连接管理机制，理解"纯 PHP 写出常驻高并发服务"是如何成立的
>
> **目标读者**: 读过 [FPM vs 常驻内存](./01-fpm-vs-resident.md)、想深入常驻运行时内部机制的开发者
>
> **前置知识**: 进程与信号的基本概念、TCP 基础；无需异步编程经验

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#Workerman` `#事件循环` `#多进程` `#常驻内存` |
| **更新日期** | `2026年9月` |

</details>

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

事件循环中的慢同步调用会延迟同一 worker 处理其他连接。先用两个并发客户端复现：一个触发慢操作，另一个发轻量请求；若轻量请求也延迟，就要考虑异步客户端、独立 worker 或任务队列。

多个 worker 的内存不自动共享，广播与在线状态需要跨进程通信或共享存储。进程交给监督器管理时，前台运行还是自行 daemonize 应匹配监督器配置；代码与启动配置变更分别核对 reload/restart 的生效范围，不假定一次 reload 更新所有资源。

## ❓ 常见问题

### Q1: Workerman 是框架吗？

**A**: 不是，它是**常驻运行时/网络库**：提供事件循环、进程管理、连接与协议处理。业务框架是它的上层——Webman 就是官方基于 Workerman 的 MVC 框架（见[下一篇](./03-webman-practice.md)）。

### Q2: 多进程之间内存不共享，会话/数据怎么办？

**A**: 这是多进程模型的明确取舍：跨进程状态应放在 Redis、数据库或消息队列等可共享边界。若确实需要在同一进程内协调短生命周期状态，可评估协程模型；但可承载的连接数仍受每连接内存、文件描述符、事件循环延迟、限流和下游容量限制。选型先看状态归属与故障恢复，再用目标负载测量容量，而不是按“单进程”推断并发数。

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


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
