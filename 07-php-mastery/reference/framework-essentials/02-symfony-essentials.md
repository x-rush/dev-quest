# Symfony 核心速查（Symfony 7.4 LTS）

## 概述

Symfony 7 是纯 PHP 8.2+ 框架，以"微内核 + Bundle 组件"著称，也是 Laravel 大量组件的上游。本文收录 Bundle 体系、服务容器（DI）、Doctrine ORM 与路由控制器四大核心，条目式速查。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Symfony` `#Bundle` `#服务容器` `#Doctrine` `#Controller` |
| **更新日期** | `2026年9月` |

</details>

## 1. Bundle 与项目结构

**定义**: Bundle 是功能模块的打包单位（可理解为"可复用的应用插件"）；应用本体位于 `src/`，由 `App` 命名空间组成。

```text
project/
├── config/                  # packages/*.yaml 按组件拆分配置
│   ├── packages/framework.yaml
│   └── services.yaml        # 应用服务配置
├── src/
│   ├── Controller/          # 控制器
│   ├── Entity/              # Doctrine 实体
│   ├── Repository/          # 仓储
│   └── Kernel.php           # 微内核：注册 Bundle
├── templates/               # Twig 模板
└── var/cache, var/log       # 运行时产物
```

```php
// config/bundles.php：标准 Flex 项目由 MicroKernelTrait 读取此表
return [
    Symfony\Bundle\FrameworkBundle\FrameworkBundle::class => ['all' => true],
    Doctrine\Bundle\DoctrineBundle\DoctrineBundle::class => ['all' => true],
    Symfony\Bundle\TwigBundle\TwigBundle::class => ['all' => true],
];
```

**陷阱**: Symfony 无"魔法目录"，任何目录组织都合法，但实体/仓储自动发现依赖默认约定（`Entity/`、`Repository/` 前缀），改名需同步改 `config/packages/doctrine.yaml`。

## 2. 路由与控制器

**定义**: 路由可用 PHP 属性注解（主流）或 YAML 声明；控制器就是普通类方法。

```php
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

final class OrderController extends AbstractController
{
    #[Route('/orders/{id}', name: 'order_show', requirements: ['id' => '\d+'], methods: ['GET'])]
    public function show(int $id, OrderRepository $orders): Response
    {
        $order = $orders->find($id)
            ?? throw $this->createNotFoundException();   // 控制器辅助方法

        return $this->json([
            'id'     => $order->getId(),
            'status' => $order->getStatus()->value,
        ]);
    }
}
```

```bash
php bin/console debug:router        # 查看全部路由
php bin/console about               # 项目体检
```

**陷阱**: 路由参数默认是字符串，必须 `requirements` 或方法签名类型声明来约束；控制器继承 `AbstractController` 才有 `$this->json()` 等快捷方法。

## 3. 服务容器（DI）

**定义**: 配置 resource 范围内的类可自动注册，autowire 和 autoconfigure 负责装配与标签，构造器类型提示即可注入。

```php
// src/Service/OrderService.php —— 无需任何配置即成为服务
final class OrderService
{
    public function __construct(
        private readonly OrderRepository $orders,       // 自动注入
        private readonly ClockInterface $clock,         // 接口注入
    ) {}
}
```

```yaml
# config/services.yaml：仅在需要显式配置时使用
services:
    _defaults: { autowire: true, autoconfigure: true }

    App\:
        resource: '../src/'
        exclude: '../src/{Entity,Kernel.php}'

    App\Clock\SystemClock: ~

    # 接口 → 实现绑定
    App\PaymentGateway: '@App\Payment\StripeGateway'

    # 标量化参数
    App\Service\Mailer:
        arguments:
            $dsn: '%env(MAILER_DSN)%'
```

```php
// 注解式定制：指向特定服务别名
use Symfony\Component\DependencyInjection\Attribute\Autowire;

final class ReportService
{
    public function __construct(
        #[Autowire(service: 'app.http.slow')]
        private readonly HttpClientInterface $client,
    ) {}
}
```

**陷阱**: `bin/console cache:clear` 后服务定义重新编译；标量参数必须显式配置（容器无法推断字符串/数字）；环境差异用 `%kernel.environment%` 或独立 `services_<env>.yaml`。

## 4. Doctrine ORM

**定义**: Symfony 常用的独立 ORM 集成，需安装相应包，DataMapper 风格（实体是纯对象，EntityManager 负责持久化）。

```php
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: OrderRepository::class)]
#[ORM\Table(name: 'orders')]
class Order
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private ?int $id = null;

    #[ORM\Column(type: 'string', enumType: OrderStatus::class)] // backing enum 与数据库字符串映射
    private OrderStatus $status = OrderStatus::Pending;

    #[ORM\OneToMany(targetEntity: OrderItem::class, mappedBy: 'order', cascade: ['persist'])]
    private Collection $items;

    public function __construct()
    {
        $this->items = new ArrayCollection();
    }

    // 纯 getter/setter；实体不含持久化逻辑
    public function getId(): ?int { return $this->id; }
    public function getStatus(): OrderStatus { return $this->status; }
    public function pay(): void { $this->status = OrderStatus::Paid; }
}
```

```php
// Repository：查询入口
use Doctrine\Persistence\ManagerRegistry;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;

final class OrderRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Order::class);
    }

    /** @return list<Order> */
    public function findPaid(): array
    {
        return $this->createQueryBuilder('o')
            ->where('o.status = :status')
            ->setParameter('status', OrderStatus::Paid)
            ->orderBy('o.id', 'DESC')
            ->setMaxResults(50)
            ->getQuery()
            ->getResult();
    }
}
```

```bash
php bin/console make:entity Order       # 交互式生成实体
php bin/console make:migration          # 生成迁移差异
php bin/console doctrine:migrations:migrate -n   # 执行
php bin/console dbal:run-sql "SELECT 1"          # 快速验证
```

**陷阱**: Doctrine 需要 `flush()` 才落库，`persist()` 只是纳入管理；实体在请求内被 detach 后修改不会保存；ID 何时可用取决于生成策略；数据库自增常在插入后可用，应用分配 ID 可以更早存在。

## 5. 常用命令与调试

```bash
composer create-project symfony/skeleton:"7.4.*" app-demo   # 最小骨架
composer require webapp                             # 加 web 常用包
php bin/console debug:container --parameter=kernel.environment
php bin/console debug:autowiring ClockInterface     # 查接口可注入的实现
symfony server:log                          # 开发期日志流
```

## 陷阱速查

- **Bundle ≠ 必须**：业务代码直接放 `App\`，只有可复用组件才值得抽成独立 Bundle
- **配置优先级**：没有适用于所有配置类型的统一优先级口诀；检查加载顺序、显式服务定义与编译 pass，用 debug:container 核对最终结果
- **Doctrine vs Eloquent**：Mapper（实体无 save 方法）与 ActiveRecord 心智不同，互相切换时最容易写出 `entity->save()` 这种不存在的方法

## 相关文档

- 📄 **[Laravel 核心速查](./01-laravel-essentials.md)** — 对照 ActiveRecord 与 Mapper 差异
- 📄 **[Composer 生态精选](../library-guides/02-composer-ecosystem.md)** — symfony/console 等独立组件
- 📄 **[教程：CLI 任务管理工具](../../basics/08-first-project.md)** — 用 symfony/console 改造实战项目


<!-- full-library-explanation -->
## 理解编译容器和工作单元

前置是依赖注入、对象映射与数据库事务。Symfony 通常在容器编译时解析服务定义，autowire 用类型匹配参数，autoconfigure 按接口或属性补标签，两者不是同一能力。服务必须先被配置资源范围注册；接口有多个实现时应明确别名，不能把“自动装配”理解为自动猜业务选择。

Doctrine 的工作单元记录受管理实体的变化，flush 将待执行变更同步到数据库。它不是只保存刚才那个对象，可能包含同一 EntityManager 中其他实体的变更。集合关联的 owning side 与 inverse side 要同步维护，仅向反向集合加入对象未必更新外键。

**练习**：加载订单并修改状态，flush 前后分别用独立查询观察数据库；再 detach 后修改，预期不会自动持久化。长批处理定期 flush/clear 以控制被管理对象数量，同时确认清理后不再复用已脱管对象。模型中的 pay 方法还应检查状态转移，不能让已取消订单直接变成已支付。

本页以 Symfony 7.4 LTS 为明确学习基线，升级其他主版本先核对 PHP 要求与迁移指南。依据：[Symfony 版本](https://symfony.com/releases)、[Doctrine 基础映射](https://www.doctrine-project.org/projects/doctrine-orm/en/3.8/reference/basic-mapping.html)、[Symfony 容器](https://symfony.com/doc/7.4/service_container.html)。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
