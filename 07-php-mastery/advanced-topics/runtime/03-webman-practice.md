# Webman 实战：常驻内存框架的 Laravel 视角迁移指南

> **文档简介**: 以 Webman（基于 Workerman 的常驻框架，中文社区极活跃）为载体，走一遍项目结构、路由、中间件的实战路径，并重点对照 Laravel 心智模型的差异点——哪些习惯要改，为什么
>
> **目标读者**: 有 Laravel 使用经验、想上手一个常驻框架的后端开发者
>
> **前置知识**: [FPM vs 常驻内存](./01-fpm-vs-resident.md)、[Workerman 原理](./02-workerman-principles.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#Webman` `#Workerman` `#常驻内存` `#Laravel 对比` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 创建 Webman 项目并说清其目录职责
- ✅ 编写路由、控制器与中间件，跑通常驻 HTTP 服务
- ✅ 列出"从 Laravel 迁移心智"的关键差异清单（状态、连接、配置、热更新）
- ✅ 判断一个需求是否适合用 Webman 承载

## 🔍 核心概念

### 概念一：Webman 是什么、不是什么

**定义**: Webman 是基于 Workerman 的常驻内存 MVC 框架，作者与 Workerman 同源（walkor），依赖极少、启动极快，在中文社区被广泛用于 API 网关、推送、高并发接口。

**它不是 Laravel 的替代品，而是另一种运行模型上的框架**：

| 维度 | Laravel（FPM） | Webman（常驻） |
|------|---------------|---------------|
| 运行载体 | PHP-FPM，每请求重建应用 | Workerman 进程，应用启动一次常驻 |
| 心智负担 | 框架帮你隔离开请求 | 状态泄漏风险由你的代码纪律兜底 |
| 组件复用 | 全生态 | 大量复用 Laravel 组件（illuminate/database、illuminate/redis、validator 等） |
| 生态定位 | 全功能 Web 应用 | 高并发 API/长连接/网关等场景优先 |

### 概念二：项目结构速览

**定义**: Webman 目录刻意向 Laravel 靠拢，迁移成本主要在"运行时"而不是"代码组织"。

```text
webman/
├── app/
│   ├── controller/          # 控制器（默认命名空间 app\controller）
│   ├── middleware/          # 中间件
│   ├── model/               # 模型
│   └── functions.php        # 全局助手函数
├── config/
│   ├── route.php            # 路由定义（也支持注解/自动路由）
│   ├── middleware.php       # 中间件注册（全局/分组）
│   ├── process.php          # 自定义常驻进程（队列消费、定时任务…）
│   ├── database.php         # 数据库（基于 illuminate/database）
│   ├── redis.php            # Redis 连接配置
│   └── server.php           # 监听协议/端口/进程数
├── process/                 # 自定义进程类
├── public/                  # 静态资源
├── runtime/                 # 日志与运行时文件
└── support/                 # 框架引导（bootstrap）
```

**关键特性**:

- `config/process.php` 是 Webman 的特色：**自定义常驻进程**（队列消费者、定时器进程）与 HTTP 服务同生命周期管理
- 视图层默认支持 PHP 原生语法模板（`webman/view` 随骨架内置，无需安装）；Blade 语法需另行安装 `webman/blade` 插件，纯 API 项目可以完全不用模板

## 🛠️ 实践指南

### 步骤一：创建项目并跑通

**操作指南**:

```bash
# 创建项目（要求 PHP >= 8.1，本模块基线 8.5；骨架包名是 workerman/webman，webman-framework 只是依赖包）
composer create-project workerman/webman:~2.0
cd webman

# 前台启动（开发）
php start.php start

# 守护化启动（生产）
php start.php start -d

# 其余日常命令
php start.php status    # 进程状态：连接数/内存/请求量
php start.php reload    # 平滑重启：加载新代码
php start.php stop      # 停止
```

浏览器访问 `http://localhost:8787` 看到 JSON 响应即成功。

**验证方法**: `php start.php status` 能看到 master 与多个 worker 进程。

### 步骤二：路由、控制器与中间件

**操作指南**:

```php
// config/route.php
use Webman\Route;
use app\controller\UserController;

Route::get('/users/{id}', [UserController::class, 'show']);
Route::post('/users', [UserController::class, 'store']);
Route::group('/api/v1', function (): void {
    Route::get('/todos', [app\controller\TodoController::class, 'index']);
})->middleware([app\middleware\AuthCheck::class]);
```

```php
// app/controller/UserController.php
namespace app\controller;

use support\Request;
use support\Response;

final class UserController
{
    public function show(Request $request, int $id): Response
    {
        // 常驻框架里同样注入 Request；业务对象用构造器注入由容器解析
        return json(['id' => $id, 'name' => 'demo']);   // 全局助手返回 JSON
    }
}
```

```php
// app/middleware/AuthCheck.php
namespace app\middleware;

use support\Request;
use support\Response;
use Webman\MiddlewareInterface;

final class AuthCheck implements MiddlewareInterface
{
    public function process(Request $request, callable $handler): Response
    {
        if (! $request->header('authorization')) {
            return json(['code' => 401, 'msg' => 'unauthorized'], 401);
        }
        return $handler($request);   // 放行进入下一层
    }
}
```

```php
// config/middleware.php —— 注册：键为应用名（多应用模式下生效），'' 即全局；
// 路由级中间件用 Route::group(...)->middleware([...])
return [
    ''  => [app\middleware\AccessLog::class],      // 全局中间件
    'api' => [app\middleware\RateLimit::class],    // api 应用
];
```

**验证方法**: `curl http://localhost:8787/api/v1/todos` 观察中间件日志与响应。

## 💻 代码示例

### 示例：数据库长连接与断线重连（与 Laravel 的第一个实质差异）

```php
// config/database.php —— 基于 illuminate/database，但配置项不同
return [
    'default' => 'mysql',
    'connections' => [
        'mysql' => [
            'driver'    => 'mysql',
            'host'      => getenv('DB_HOST'),
            'database'  => getenv('DB_DATABASE'),
            'username'  => getenv('DB_USERNAME'),
            'password'  => getenv('DB_PASSWORD'),
            'charset'   => 'utf8mb4',
            // ⚠️ 常驻进程的连接是长连接：MySQL 服务端会主动断开闲置连接，
            // pool 仅在 swoole/swow 驱动下生效；默认驱动需自行处理断线重连，防止 "MySQL server has gone away"
            'pool' => [
                'heartbeat_interval' => 50,
            ],
        ],
    ],
];
```

**关键点解析**:

- 连接在进程启动后建立并**复用到底**，不像 FPM 每请求新建——这是常驻的核心收益之一
- 连接池心跳（`heartbeat_interval`）仅 swoole/swow 驱动下生效；默认 Workerman 驱动没有连接池，断线重连需自行处理

## 🎨 最佳实践

常驻进程可能连续处理不同用户，请求身份和临时缓存不能随意放在长寿命单例里。用“用户 A 请求结束后紧接用户 B”验证数据隔离；需要请求级状态时显式传参或使用框架支持的上下文。

Laravel 是否逐请求重建同样取决于运行方式，不能认为 static 在 Laravel 中天然安全。配置变更需按资源生命周期选择重载或重启，后台任务则声明退出、失败与重试责任。多 worker 的会话存储必须可共享，异常后的资源清理由明确的 finally/框架生命周期负责。

## ❓ 常见问题

### Q1: Webman 能用 Eloquent 吗？

**A**: 能。Webman 直接集成 `illuminate/database`（Laravel 的 ORM 组件），模型写法与 Laravel 几乎一致；但 Laravel 的 Facade、服务提供者体系并不完整搬过来，属于"组件级复用"而非"框架级兼容"。

### Q2: 什么时候选 Webman 而不是留在 Laravel/FPM？

**A**: 出现以下信号再考虑：①高 QPS 低延迟 API 且 profile 证明启动税占比可观；②长连接（WebSocket/推送）需求；③想用纯 PHP 部署（无扩展依赖）获得常驻能力。普通业务系统没有这些信号，Laravel/FPM 是更稳的选择。

## 🔄 文档交叉引用

### 相关文档

- 📄 **[FPM vs 常驻内存](./01-fpm-vs-resident.md)** — 本篇所有"差异"的模型根源
- 📄 **[Workerman 原理](./02-workerman-principles.md)** — Webman 底层的进程与事件循环机制
- 📄 **[Swoole 协程生态](./04-swoole-ecosystem.md)** — 另一条协程路线的对比项
- 📄 **[生产级 Laravel 应用](../../projects/04-production-laravel-app.md)** — 迁移前先看 Laravel 侧的等价工程实践

### 外部资源

- Webman 官方文档（中文）：https://www.workerman.net/doc/webman/

## 📝 总结

### 核心要点回顾

1. Webman = Workerman 常驻运行时 + 贴近 Laravel 的代码组织，迁移成本低在"写法"、高在"心智"
2. 长连接、配置启动期加载、reload 才生效是三大运行时差异
3. 状态泄漏纪律（静态/单例/请求态）是常驻框架的 code review 硬项

### 学习成果检查

- [ ] 能不查文档画出 Webman 目录树并说明 process.php 的用途
- [ ] 能复述"Laravel 心智迁移清单"中的四个陷阱
- [ ] 能为一个具体需求论证"该不该用 Webman"

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
