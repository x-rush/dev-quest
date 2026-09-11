# Laravel 架构解析：服务容器、服务提供者与架构模式

> **文档简介**: 从"能配置"到"懂原理"——拆解服务容器的绑定机制、服务提供者的启动流程与常见架构模式在 Laravel 中的落地方式
>
> **目标读者**: 日常使用 Laravel、想理解框架骨架如何运转的中高级开发者
>
> **前置知识**: [Laravel 进阶](../../frameworks/02-laravel-advanced.md)、[面向对象基础](../../basics/04-functions-oop.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#Laravel` `#服务容器` `#服务提供者` `#架构模式` `#依赖注入` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 解释容器如何"猜"出构造器依赖（反射 + 递归解析）
- ✅ 区分 bind/singleton/scoped 三种绑定的生命周期
- ✅ 说清服务提供者 register/boot 两阶段的执行顺序
- ✅ 为业务代码选择合适的组织模式（Action/DTO/Repository）

## 1. 服务容器：框架的心脏

容器本质是一个"接口 → 实例工厂"的注册表，加上自动解析能力：

```php
// app/Providers/AppServiceProvider.php
public function register(): void
{
    // bind：每次解析都新建（有状态服务、短生命周期对象）
    $this->app->bind(PaymentGateway::class, StripeGateway::class);

    // singleton：进程内只建一次（无状态重量级服务）
    $this->app->singleton(RateLimiter::class, RedisRateLimiter::class);

    // scoped：单个请求/队列任务内单例（Octane 场景下避免状态跨请求泄漏）
    $this->app->scoped(UserContext::class);

    // 带上下文的绑定：同一接口在不同类里给不同实现
    $this->app->when(PhotoController::class)
        ->needs(Filesystem::class)
        ->give(fn () => Storage::disk('photos'));
}
```

自动解析（零配置注入）的原理：控制器/任务类的方法签名类型提示 → 容器用**反射**读取构造器参数 → 递归解析每个依赖 → 没有提示的具体类直接 `new`。这也解释了两条纪律：

1. 面向接口的依赖必须显式 bind，否则容器无从得知实现
2. 构造器参数只放依赖，**不放原始值**（原始值走方法参数或配置）

## 2. 服务提供者：启动的两阶段

Laravel 11+（13 延续）的提供者集中在 `bootstrap/providers.php` 注册，每个提供者经历两阶段：

```text
所有提供者的 register() 依次执行     ← 只做绑定，绝不使用其他服务
        ↓ 容器就绪
所有提供者的 boot() 依次执行        ← 可以依赖任何已注册服务
        ↓
请求被路由/任务被处理
```

```php
final class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        // ✔ 绑定接口、注册配置——此时不能安全地使用别的服务
        $this->app->singleton(AuditLogger::class);
    }

    public function boot(): void
    {
        // ✔ 框架功能就绪：注册 Gate、宏、事件监听、模型观察者
        Gate::policy(Post::class, PostPolicy::class);
        Model::preventLazyLoading(! $this->app->isProduction());
    }
}
```

**为什么分两阶段？** 保证"注册"与"使用"解耦：A 提供者可以在 register 阶段绑定 B 依赖的东西，而 B 在 boot 阶段才消费它，顺序问题被彻底消灭。

## 3. 请求生命周期的容器视角

```text
public/index.php
  → 加载 bootstrap/app.php → 创建 Application（容器本身）
  → register 全部提供者 → boot 全部提供者
  → HTTP Kernel 中间件管道
  → 路由解析出控制器 → 容器反射构造控制器（注入 Request、Action…）
  → 执行动作 → 响应逐层穿出中间件
```

对照[入门篇的生命周期描述](../../frameworks/01-laravel-basics.md)，此处补充的正是"容器在启动期的两阶段准备工作"。

## 4. 业务架构模式：框架之上的一层

| 模式 | Laravel 中的形态 | 适用信号 |
|------|-----------------|---------|
| Action 类 | `app/Actions/*`，一个类一个用例 | 控制器超过 10 行、逻辑被多处复用 |
| DTO | `readonly` 属性类（PHP 8.2+） | 数组参数四处传递、字段含义模糊 |
| Service 层 | `app/Services/*`，聚合多个 Action | 事务边界、跨模型编排 |
| Repository | 接口 + Eloquent 实现 | 需要替换存储或严格隔离查询（慎用，勿过度抽象） |

落地示例见[生产级应用](../../projects/04-production-laravel-app.md)的 Action + DTO 重构；职责边界的判定依据是依赖方向：**外层可依赖内层，内层绝不感知外层**（Controller → Action → Model）。

## 5. 设计权衡：为什么 Laravel 选"约定优先"

- 门面（Facade）：静态语法访问容器实例——省样板代码，代价是隐式依赖（测试中需 `fake()`）
- 魔术方法：Eloquent 的 `$model->title`——开发效率高，代价是静态分析需要 Larastan 补偿
- 评价框架架构的标准不是"魔法多少"，而是**魔法是否可控**：提供者、容器绑定、接口绑定就是官方给出的"降魔法旋钮"

## 🔗 相关文档

- 📄 [Laravel 核心速查](../../reference/framework-essentials/01-laravel-essentials.md) — 容器与提供者 API 条目
- 📄 [函数与 OOP](../../basics/04-functions-oop.md) — 反射、接口与抽象类的语言基础
- 📄 [安全实践](../security/01-security-practices.md) — 架构分层外的另一条纵深防线
- 📄 [查询优化](../performance/01-query-optimization.md) — 数据访问层的性能主题
