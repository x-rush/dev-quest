# 高级特性 - 枚举、属性注解与 Fibers

> **文档简介**: 系统学习 PHP 8.1-8.4 的进阶语言特性：枚举、属性注解（Attributes）、Fibers 协程与一等公民 callable 语法
>
> **目标读者**: 已完成基础教程、希望写出地道现代 PHP 代码的中级学习者
>
> **前置知识**: 完成 [错误与异常](./06-error-exceptions.md)，熟悉类与接口、反射的基本概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#枚举` `#属性注解` `#Fibers` `#Callable` `#PHP8.1+` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 Backed Enum 替代类常量，实现带行为的枚举
- ✅ 用属性注解声明验证规则、路由等元数据并反射读取
- ✅ 解释 Fiber 与线程/协程的关系，编写基础的 Fiber 协作调度
- ✅ 在集合操作中使用一等公民 callable 语法简化代码

## 1. 枚举（PHP 8.1+）：类型安全的常量集合

### 纯枚举与 Backed 枚举

```php
<?php

declare(strict_types=1);

// 纯枚举：case 即值
enum Suit
{
    case Hearts;
    case Spades;
}

// Backed 枚举：case 映射到标量（int 或 string），可持久化到数据库
enum OrderStatus: string
{
    case Pending   = 'pending';
    case Paid      = 'paid';
    case Shipped   = 'shipped';

    // 枚举可实现接口、包含方法，甚至静态方法
    public function isFinal(): bool
    {
        return $this === OrderStatus::Shipped;
    }

    public static function fromDbOrDefault(?string $raw): self
    {
        return $raw === null ? self::Pending : self::from($raw);
    }
}

$status = OrderStatus::from('paid');    // 无效值抛 ValueError
$maybe  = OrderStatus::tryFrom('gone'); // 无效值返回 null
echo $status->value, PHP_EOL;           // paid：读取标量值
echo $status->name, PHP_EOL;            // Paid：读取 case 名

print_r(OrderStatus::cases());          // 全部 case 组成的数组
```

**核心价值**：枚举是"类 + 单例集合"，类型系统可以精确到具体状态，配合 `match` 获得穷尽性检查（见 [控制流程](./05-control-flow.md)）。

### 带实现的枚举：策略分发

```php
enum PaymentMethod: string
{
    case Alipay = 'alipay';
    case Wechat = 'wechat';

    public function handlerClass(): string
    {
        return match ($this) {
            self::Alipay => AlipayHandler::class,
            self::Wechat => WechatHandler::class,
        };
    }
}
```

## 2. 属性注解（Attributes，PHP 8.0+）

属性是**写在代码里的结构化元数据**，取代了 DocBlock 注解（`@Route(...)`），可被反射读取，是现代框架（Laravel、Symfony）路由与验证的主流声明方式。

### 声明与使用

```php
<?php

declare(strict_types=1);

#[Attribute(Attribute::TARGET_PROPERTY)]   // 限定可用于属性
final class MaxLength
{
    public function __construct(
        public readonly int $length,
    ) {
    }
}

#[Attribute(Attribute::TARGET_CLASS)]
final class Table
{
    public function __construct(
        public readonly string $name,
    ) {
    }
}

#[Table(name: 'users')]          // 命名参数传值
final class User
{
    public function __construct(
        #[MaxLength(20)]
        public readonly string $nickname,
    ) {
    }
}
```

### 反射读取

```php
use ReflectionClass;

$ref = new ReflectionClass(User::class);

// 读取类级属性
$table = $ref->getAttributes(Table::class)[0]->newInstance();
echo $table->name, PHP_EOL;        // users

// 读取构造器参数上的属性
$param = $ref->getConstructor()->getParameters()[0];
$max = $param->getAttributes(MaxLength::class)[0]->newInstance();
echo $max->length, PHP_EOL;        // 20
```

**使用准则**：属性只放**声明性元数据**（配置、规则、路由），不承载业务逻辑；运行时行为交给读取属性的框架/工具层。

## 3. 一等公民 callable 语法（PHP 8.1+）

`Foo::method(...)` 创建闭包，不再需要字符串或数组形式，IDE 与静态分析全程可追踪：

```php
<?php

declare(strict_types=1);

$names = ['  ada ', ' grace', 'alan '];

// 旧写法：array_map('trim', $names) —— 字符串引用，重构时易漏改
$trimmed = array_map(trim(...), $names);          // ✅ 新写法
print_r($trimmed);                                 // ['ada', 'grace', 'alan']

// 静态方法同样适用
$upper = array_map(strtoupper(...), $trimmed);
print_r($upper);                                   // ['ADA', 'GRACE', 'ALAN']

class Formatter
{
    public function quote(string $s): string
    {
        return "[{$s}]";
    }
}

$f = new Formatter();
$quoted = array_map($f->quote(...), $trimmed);     // 实例方法引用
print_r($quoted);                                  // [[ada] [grace] [alan]]
```

**对比三种形态**：

| 形态 | 示例 | 静态分析 | 重构安全 |
|------|------|---------|---------|
| 字符串 | `'trim'` | 弱 | 弱 |
| 数组 | `[$obj, 'method']` | 弱 | 弱 |
| 一等公民 | `$obj->method(...)` | 强 | 强 |

## 4. Fibers（PHP 8.1+）：中断与恢复的执行流

Fiber 是可以在任意点**暂停并交还控制权**、之后从断点**恢复**的轻量执行单元。它是异步框架（Revolt、Amp 等）的底层原语——**不是**多线程，同一时刻只有一段代码在执行。

### 最小示例

```php
<?php

declare(strict_types=1);

$fiber = new Fiber(function (string $task): string {
    echo "执行 {$task} 前半段", PHP_EOL;
    $input = Fiber::suspend("{$task}-等待中");   // 暂停，把值交还给 resume 调用方
    echo "恢复，收到: {$input}", PHP_EOL;
    return "{$task}-完成";
});

$result = $fiber->start('任务A');
echo "主流程拿到: {$result}", PHP_EOL;

$final = $fiber->resume('外部数据');
echo "最终结果: {$final}", PHP_EOL;
```

输出顺序：

```
执行 任务A 前半段
主流程拿到: 任务A-等待中
恢复，收到: 外部数据
最终结果: 任务A-完成
```

### 生命周期与状态检查

```php
<?php

declare(strict_types=1);

$f = new Fiber(fn(): string => 'done');

var_dump($f->isStarted());      // false
$f->start();
var_dump($f->isTerminated());   // true —— 一次性执行完毕

// 典型生命周期：created -> start() -> running -> suspend() -> suspended
//             -> resume() -> ... -> terminated
// start() 只能调用一次；isSuspended()/isRunning()/isTerminated() 描述当前状态
```

**心智模型**：

- `Fiber::suspend()` = "我暂停，调度器请继续干别的"
- `->resume($value)` = "回到你暂停的地方，这是你要的数据"
- Fiber 内抛出的未捕获异常会在 `start/resume` 调用处重新抛出

真实项目中一般不直接操作 Fiber，而是使用基于它的 async 库（如 Revolt + Amp）做并发 HTTP/MySQL 请求。

## ✅ 最佳实践

- ✅ **数据库可枚举状态一律用 Backed Enum**：配合 `match` 的穷尽性检查，新增状态时静态分析兜底
- ✅ **属性注解只做元数据**：复杂校验逻辑交给读取注解的通用服务（如 Validator）
- ✅ **回调一律 `Foo::method(...)` 语法**：重构时 IDE 全程追踪，消灭字符串回调
- ❌ **不要把枚举当命名空间**：一个枚举表达一个封闭状态集，不要塞无关 case
- ❌ **不要在普通 Web 请求里手写 Fiber 调度**：这是框架/运行时的职责，业务代码直接用 async API

## ❓ 常见问题

### Q1: 枚举能继承或实例化吗？
**A**: 不能 `new`，不能继承（枚举隐式 final），但可以实现接口、使用 trait、定义常量与方法——本质是特殊的 final 类。

### Q2: 属性注解和 DocBlock 注解什么关系？
**A**: 属性注解是语言级结构、有语法检查、可携带类型化参数；DocBlock 只是注释文本。新代码一律用 `#[...]`，仅泛型等 PHPStan 专属信息仍写在 DocBlock。

### Q3: Fiber 和 Generator（yield）怎么选？
**A**: Generator 面向惰性序列迭代；Fiber 面向"调用栈任意深度处暂停"。异步 I/O 场景选 Fiber（或其上层库），数据流处理选 Generator。

## 🎯 练习与实践

### 基础练习
- [ ] 实现 `enum Weekday: int`，提供 `isWorkday(): bool` 与 `next(): static` 方法
- [ ] 为一个 `Form` 类编写 `#[Required]`、`#[MaxLength(n)]` 属性，写反射校验器逐条检查
- [ ] 把一段使用字符串回调 `usort($arr, 'strcmp')` 的代码改为 `strcmp(...)` 形式

### 进阶挑战
- [ ] 用两个 Fiber 实现"生产者-消费者"：生产者 `suspend` 交付数据，消费者 `resume` 驱动
- [ ] 基于 Fiber 实现一个伪并发演示：三个 Fiber 各自 `suspend`，由调度循环依次 `resume`，观察交错输出

---

## 🔗 相关文档

- 📄 **[综合练习：CLI 任务管理工具](./08-first-project.md)** — 用枚举与属性完成真实项目
- 📄 **[类型系统与现代 OOP 全表](../reference/language-concepts/03-types-oop-modern.md)** — 本篇各特性的条目式权威速查
- 📄 **[关键字详解](../reference/language-concepts/01-php-keywords.md)** — `enum`/`match`/`fn` 关键字精确定义
