# 高级特性 - 枚举、属性注解与 Fibers

## 先理解，再动手

enum 限制可取值集合，attribute 附加可供反射读取的元数据，Fiber 提供可暂停执行。它们解决不同问题，不是同一套“高级语法”。

**本节自测**：用 enum 表达待办状态，再尝试从非法文本构造。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

非法状态必须处理；attribute 不会自行执行验证，Fiber 也不自动提供异步 I/O 调度器。

</details>

> **文档简介**: 系统学习 PHP 8.1-8.5 的进阶语言特性：枚举、属性注解（Attributes）、Fibers 协程、一等公民 callable 语法与 8.4/8.5 增量
>
> **目标读者**: 已完成基础教程、希望写出地道现代 PHP 代码的中级学习者
>
> **前置知识**: 完成 [错误与异常](./06-error-exceptions.md)，熟悉类与接口、反射的基本概念

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#枚举` `#属性注解` `#Fibers` `#Callable` `#PHP8.1+` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 Backed Enum 替代类常量，实现带行为的枚举
- ✅ 用属性注解声明验证规则、路由等元数据并反射读取
- ✅ 解释 Fiber 与线程/协程的关系，编写基础的 Fiber 协作调度
- ✅ 在集合操作中使用一等公民 callable 语法简化代码
- ✅ 建立 8.4/8.5 增量索引：属性钩子、管道运算符、URI 扩展

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

**核心价值**：枚举限制一组合法状态。`match` 通过严格比较分派；如果运行时遇到未覆盖的 case 且没有 `default`，会抛出 `UnhandledMatchError`，PHP 本身不会提前拒绝这个不完整的分支集合。需要提前发现遗漏时，配置支持枚举分析的静态分析工具（见 [控制流程](./05-control-flow.md)）。

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

Attributes 是**写在代码里的结构化元数据**，可由反射读取。只有框架或应用主动读取时，它们才产生业务效果；某个库是否支持属性声明，要查该库的接口，不能把 `#[Route]` 写到任意控制器上就假定路由已注册。

### 声明与使用

下面是完整脚本，保存为 `attributes.php` 后执行 `php attributes.php`。它同时检查属性侧读取成功、参数侧实例化失败，并区分“获取元数据”和“实例化元数据”。

<!-- reference-case: {"id":"php-promoted-attributes","stdout":"users\n20\n1\nparameter-target-rejected\n"} -->
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
$ref = new ReflectionClass(User::class);

// 读取类级属性
$table = $ref->getAttributes(Table::class)[0]->newInstance();
echo $table->name, PHP_EOL;        // users

// 读取构造器提升参数上的属性：注解 target 是 property，从提升出的属性读取
$prop = $ref->getProperty('nickname');
$max = $prop->getAttributes(MaxLength::class)[0]->newInstance();
echo $max->length, PHP_EOL;        // 20

$param = $ref->getConstructor()->getParameters()[0];
$attributes = $param->getAttributes(MaxLength::class);
echo count($attributes), PHP_EOL; // 元数据存在不代表 target 合法
try {
    $attributes[0]->newInstance();
    throw new RuntimeException('参数 target 本应被拒绝');
} catch (Error $error) {
    echo 'parameter-target-rejected', PHP_EOL;
}
```

**陷阱（提升参数上的注解）**：提升参数上的注解同时出现在参数与生成的属性上；本例 `MaxLength` 仅允许 `TARGET_PROPERTY`，所以从参数侧 `newInstance()` 会抛 `Error`。如果注解只允许 `TARGET_PARAMETER`，读取端则应使用参数反射；若两边都允许，可组合 target 标志。选择哪一端取决于注解声明与工具契约，不能一律使用 `getProperty()`。

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

<!-- reference-case: {"id":"php-fiber-return-channels","stdout":"执行 任务A 前半段\n主流程拿到: 任务A-等待中\n恢复，收到: 外部数据\nNULL\n任务A-完成\n"} -->
```php
<?php

declare(strict_types=1);

$fiber = new Fiber(function (string $task): string {
    echo "执行 {$task} 前半段", PHP_EOL;
    $input = Fiber::suspend("{$task}-等待中");   // 暂停，把值交还给 start/resume 调用方
    echo "恢复，收到: {$input}", PHP_EOL;
    return "{$task}-完成";
});

$sent = $fiber->start('任务A');            // 返回值 = fiber 经 suspend() 交出的值
echo "主流程拿到: {$sent}", PHP_EOL;

$resumed = $fiber->resume('外部数据');     // 实参 = fiber 在挂起点收到的值
var_dump($resumed);                         // NULL：fiber 没有再次 suspend，而是直接 return

echo $fiber->getReturn(), PHP_EOL;          // "任务A-完成"：fiber 的 return 值，仅终止后可调
```

输出顺序：

```
执行 任务A 前半段
主流程拿到: 任务A-等待中
恢复，收到: 外部数据
NULL
任务A-完成
```

**两个返回通道不要混淆**（本例的运行版本与输出见文末验证报告）：

- `start()/resume()` 的返回值 = fiber **下一次 `Fiber::suspend()` 交出的值**；若 fiber 不再挂起、直接结束，得到 `NULL`
- fiber 函数的 `return` 值只能用 `$fiber->getReturn()` 获取，且必须在 fiber 终止后调用（否则抛 `Error: Cannot get fiber return value: The fiber has not returned`）

### 生命周期与状态检查

<!-- reference-case: {"id":"php-fiber-lifecycle","stdout":"bool(false)\nbool(true)\n"} -->
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

- `Fiber::suspend($v)` = "我暂停，把 $v 交给调度器（start/resume 调用方）"
- `->resume($v)` = "回到你暂停的地方"——`$v` 是 fiber 在挂起点收到的数据；resume 是向 fiber **传入**数据的通道，不是取结果的通道
- Fiber 内抛出的未捕获异常会在 `start/resume` 调用处重新抛出

真实项目中一般不直接操作 Fiber，而是使用基于它的 async 库（如 Revolt + Amp）做并发 HTTP/MySQL 请求。

## 5. 8.4/8.5 增量速览：属性钩子、管道运算符与 URI 扩展

这三个特性不改变既有写法，但在进阶阶段值得建立索引——完整条目见 [PHP 8.4/8.5 增量特性](../reference/language-concepts/12-modern-php-85.md)。

### 属性钩子（8.4+）：把 getter/setter 写进属性

```php
<?php

declare(strict_types=1);

final class Profile
{
    public string $email {
        set (string $value) {
            if (! str_contains($value, '@')) {
                throw new ValueError('邮箱格式非法');
            }
            $this->email = strtolower($value);   // 写入底层存储
        }
    }
}

$p = new Profile();
$p->email = 'ADA@Example.COM';
echo $p->email, PHP_EOL;    // ada@example.com
```

要点：`get`/`set` 钩子内联读写行为，可定义无底层存储的虚拟属性；与 `readonly` 互斥；`get` 钩子里直读 `$this->prop` 不会递归（直读底层存储），递归风险仅在把钩子逻辑写到会再次触发钩子的路径上。

### 管道运算符（8.5+）：从左往右读的数据流

```php
$title = '  modern php  ';
$clean = $title |> trim(...) |> mb_strtoupper(...);   // MODERN PHP
```

管道把左侧结果作为一个实参传给右侧 callable；其他参数必须有默认值，或由闭包提供，例如 `$text |> (fn(string $s): string => str_replace(' ', '-', $s))`。`str_replace(...)` 只创建函数引用，**不会固定部分实参**。本节 8.5 片段需要 PHP 8.5，`mb_strtoupper` 还需要 mbstring 扩展。

### URI 扩展（8.5+）：类型化的 URL 解析

```php
$uri = new Uri\Rfc3986\Uri('https://example.com:8080/a?x=1');
echo $uri->getHost(), PHP_EOL;    // example.com
$next = $uri->withPath('/b');     // 不可变：with* 返回新实例
```

`Uri\WhatWg\Url` 使用 WHATWG 解析规则，解析失败抛 `Uri\WhatWg\InvalidUrlException`（继承自 `Uri\InvalidUriException`）。这些对象提供另一套解析与修改接口；`parse_url()` 仍存在，迁移时应检查解析规则和错误行为。URL 能被解析不代表可以安全访问：服务器请求还需限制协议、目的主机及重定向。

## ✅ 最佳实践

枚举用于一组有业务关系的状态；需要与数据库标量互转时 Backed Enum 很方便，但未知或旧值仍要定义迁移和失败行为。属性提供元数据，只有读取它的框架或代码才会执行对应校验。

回调语法按可读性与兼容版本选择，不把一种写法定成普遍禁令。Fiber 提供暂停与恢复原语，不自带完整调度、I/O 或重试系统；初学者先解释一个调用何时暂停、由谁恢复，再进入运行时扩展。

## ❓ 常见问题

### Q1: 枚举能继承或实例化吗？
**A**: 不能 `new`，不能继承（枚举隐式 final），但可以实现接口、使用 trait、定义常量与方法——本质是特殊的 final 类。

### Q2: 属性注解和 DocBlock 注解什么关系？
**A**: 属性注解提供反射可读的结构化元数据；DocBlock 仍用于说明参数、返回值、异常与静态分析类型。库支持的运行时声明可用属性，解释性文档仍写注释；属性并不会使所有 DocBlock 失去用途。

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

- [PHP 官方属性说明](https://www.php.net/manual/en/language.attributes.overview.php) · [构造器属性提升](https://www.php.net/manual/en/language.oop5.decon.php) · [Fiber 返回值](https://www.php.net/manual/en/fiber.getreturn.php)
- [管道运算符的 callable 契约](https://www.php.net/operators.functional) · [PHP 8.5 URI 与其他增量特性](https://www.php.net/releases/8.5/en.php)
- [本文 3 个完整案例的限定运行证据](../../shared-resources/tools/document-quality/reports/php-java-core-boundaries.md)。运行器原样提取标记代码；8.4/8.5 增量片段与异步框架集成不在这 3 项范围内。
- 📄 **[综合练习：CLI 任务管理工具](./08-first-project.md)** — 用枚举与属性完成真实项目
- 📄 **[类型系统与现代 OOP 全表](../reference/language-concepts/03-types-oop-modern.md)** — 本篇各特性的条目式权威速查
- 📄 **[PHP 8.4/8.5 增量特性](../reference/language-concepts/12-modern-php-85.md)** — 属性钩子/管道运算符/URI 扩展条目式全表
- 📄 **[关键字详解](../reference/language-concepts/01-php-keywords.md)** — `enum`/`match`/`fn` 关键字精确定义


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
