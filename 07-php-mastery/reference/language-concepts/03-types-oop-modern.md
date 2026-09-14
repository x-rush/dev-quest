# 类型系统与现代 OOP 特性全表

## 概述

本文是 PHP 8.x 类型系统（联合、交叉、DNF）与现代 OOP 特性（枚举、属性、Fibers、一等公民 callable）的条目式权威速查。每条按"定义 → 语法 → 示例 → 陷阱"组织，可任意跳入查阅。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#类型系统` `#联合类型` `#DNF` `#枚举` `#属性注解` `#Fibers` |
| **更新日期** | `2026年9月` |

## 1. 基础类型声明

### 可空类型 `?T`

**定义**: `?T` 等价于 `T|null` 的语法糖。

```php
function findUser(int $id): ?User     // 可能返回 null
function setName(?string $name): void // 可传 null
```

**陷阱**: `?T` 与 `T|null` 自 8.0 起完全等价；但 `?T` 不能与其他类型组成联合（`?int|string` 直接解析错误）。`T $x = null` 的隐式可空默认值 8.4 起弃用，必须显式写 `?T` 或 `T|null`。

### 联合类型 Union Types（8.0+）

**定义**: 参数或返回值接受多个类型之一，用 `|` 分隔。

```php
function toNumber(int|float|string $v): int|float
{
    return is_numeric($v) ? $v + 0 : 0;
}
```

**陷阱**: `int|false` 这类"返回值或哨兵"仍可写，但更推荐抛异常；`null` 必须显式出现在联合中。

### 交叉类型 Intersection Types（8.1+）

**定义**: 值必须同时满足全部类型（类/接口），用 `&` 分隔。只能用于类类型。

```php
function render(Countable&Stringable $widget): string
{
    return count($widget) . ':' . $widget;
}
```

**陷阱**: 不能包含标量类型；`A&B` 与 `A|B` 语义完全不同——交叉是"同时具备"，联合是"任选其一"。

### DNF 类型 Disjunctive Normal Form（8.2+）

**定义**: 联合与交叉的组合，形式为 `(A&B)|C`，括号内只能交叉、括号间只能联合。

```php
function process((Traversable&Countable)|ArrayAccess $data): void
{
    // 要么"可遍历且可计数"，要么"数组式访问"
}

function handle(null|(Stringable&Countable)|array $input): void   // 与 null 组合
{
}
```

**陷阱**: `A&(B|C)` 不符合 DNF，解析器会拒绝；嵌套超过一层括号也不合法。

### 类型关键字速查

| 类型 | 引入版本 | 语义 |
|------|---------|------|
| `mixed` | 8.0 | 任意值，等价于"无约束"（不等于缺省声明） |
| `void` | 7.1 | 无返回值，函数必须裸 `return` |
| `never` | 8.1 | 永不返回（抛异常/`exit`/死循环），静态分析利器 |
| `static` | 8.0（返回类型） | 返回实际调用类实例 |
| `iterable` | 7.1 | `array\|Traversable` 的别名 |
| `callable` | 5.4 | 可调用结构；类上下文中不能与闭包类型混用 |
| `true`/`false` | 8.2 | 可独立作为类型，如 `true\|false`、`false|null` |
| `object` | 7.2 | 任意对象，但无法访问具体成员 |

**陷阱**: `never` 函数必须以异常/exit 结束，写 `return` 直接报错；`callable` 参数不能用 `is_callable` 弱判定替代严格校验。

## 2. 属性可见性与只读

### readonly 属性（8.1+）

**定义**: 初始化后禁止修改的属性，只能通过构造器（或提升参数）赋值一次。

```php
final class Vector
{
    public function __construct(
        public readonly array $items = [],
    ) {}

    public function push(mixed $item): static
    {
        return new static([...$this->items, $item]);   // 修改即新对象
    }
}
```

**陷阱**: 只保证引用不可变（浅只读），数组内部、对象内部仍可变；不支持默认值与构造器传值并存。

### 动态属性废弃（8.2+）

**定义**: 未声明的属性赋值从 Deprecated 升级为废弃行为，`#[AllowDynamicProperties]` 可豁免 `stdClass` 类场景。

```php
class Legacy {}          // 8.2 起未声明属性赋值触发弃用通知
$obj = new Legacy();
// $obj->undeclared = 1;   // ⚠️ Deprecated
```

### 非对称可见性（8.4+）

**定义**: 读写权限分离声明：`public private(set)` 外部可读、仅类内可写。

```php
final class Meter
{
    public private(set) int $count = 0;      // 等效自动 getter
    public protected(set) float $avg = 0.0;  // 子类可写

    public function inc(): void
    {
        $this->count++;
    }
}
```

**陷阱**: 与 `readonly` 互斥；`new` 初始化器中的隐式初始化也算"类内写入"。

### 常量类型化（8.3+）

**定义**: 类常量可显式声明类型，子类覆盖时类型必须兼容。

```php
abstract class Config
{
    public const int TIMEOUT = 30;
    final public const string VERSION = '1.0';   // final 禁止覆盖
}
```

## 3. 枚举 Enum（8.1+）

**定义**: 封闭的值集合，case 是单例；Backed 枚举绑定 int/string 标量值。

```php
enum HttpMethod: string implements HasLabel
{
    case Get  = 'GET';
    case Post = 'POST';

    public function label(): string   // 枚举可含方法、常量、实现接口
    {
        return match ($this) {
            self::Get  => '查询',
            self::Post => '创建',
        };
    }

    public static function fromHeader(string $raw): static
    {
        return static::from(strtoupper($raw));   // 非法值抛 ValueError
    }
}

// 内置方法
HttpMethod::cases();                        // 全部 case 数组
HttpMethod::from('POST');                   // 静态解析，失败抛异常
HttpMethod::tryFrom('PUT');                 // 失败返回 null
HttpMethod::Post->value;                    // 'POST'
HttpMethod::Post->name;                     // 'Post'
```

**陷阱**: 枚举隐式 final、无构造器、不可序列化为任意对象；`serialize`/`var_export` 对枚举有专门格式，反序列化非法值抛异常。

## 4. 属性注解 Attributes（8.0+）

**定义**: 语言级结构化元数据，`#[Attr(...)]` 标注在类/方法/属性/参数/函数上，经反射实例化。

```php
#[Attribute(Attribute::TARGET_METHOD | Attribute::IS_REPEATABLE)]
final class Route
{
    public function __construct(
        public readonly string $path,
        public readonly array $methods = ['GET'],
    ) {}
}

final class HomeController
{
    #[Route('/health', ['GET', 'HEAD'])]
    public function health(): array
    {
        return ['ok' => true];
    }
}

// 框架侧读取
$ref = new ReflectionMethod(HomeController::class, 'health');
foreach ($ref->getAttributes(Route::class) as $attr) {
    $route = $attr->newInstance();   // 触发构造器校验
}
```

**陷阱**: `newInstance()` 才会执行构造器校验，`getArguments()` 不校验；目标不匹配（如方法上用了 `TARGET_CLASS`）仅在实例化时报错。

## 5. 一等公民 Callable 语法（8.1+）

**定义**: `Foo::method(...)` 创建绑定闭包（Closure），替代字符串/数组回调。

```php
$fn  = strlen(...);          // 全局函数
$fn2 = str_repeat(...);
$fn3 = Foo::bar(...);        // 静态方法
$fn4 = $obj->bar(...);       // 实例方法（绑定 $obj）

echo $fn('abc'), PHP_EOL;    // 3
```

**陷阱**: 该语法创建的是 `Closure` 实例（`$fn instanceof Closure` 为 true）；构造器不能用 `...` 引用，需要工厂方法或 `fn() => new Foo(...)`。

## 6. Fibers（8.1+）

**定义**: 可挂起/恢复的完整调用栈执行单元，异步库的底层原语。

```php
$fiber = new Fiber(function (): int {
    $value = Fiber::suspend('paused');   // 挂起，向外交出控制权
    return $value + 1;
});

$mid = $fiber->start();          // 返回 suspend() 交出的值：'paused'
$end = $fiber->resume(41);       // 41 注入挂起点 $value；fiber return 42，但 resume() 返回 NULL
var_dump($mid, $end, $fiber->getReturn());   // string(6) "paused"、NULL、int(42)
```

| API | 语义 |
|-----|------|
| `new Fiber(callable)` | 创建（不执行） |
| `start(...$args)` | 首次执行，参数传入 Fiber 函数；只能调用一次 |
| `resume(mixed $value)` | 从挂起点恢复，该值成为 fiber 内 `suspend` 的返回值；方法本身返回 fiber 下一次 suspend 交出的值（未再挂起则 NULL） |
| `throw(Throwable $e)` | 恢复但在挂起点抛出异常 |
| `Fiber::suspend(mixed $value)` | Fiber 内挂起，值返回给 start/resume |
| `getReturn()` | 取 fiber 的 return 值，仅 `isTerminated()` 后可调（提前调用抛 Error） |
| `isStarted/isSuspended/isRunning/isTerminated` | 状态查询 |

**陷阱**: Fiber 不是线程/进程，无并行；在挂起状态销毁 Fiber 会导致后续 resume 抛 `FiberError`；阻塞 I/O 依旧阻塞整个进程。

## 7. 其他现代 OOP 要点

- **`::class` 常量对对象可用（8.0）**：`$obj::class` 获取运行时类名
- **构造器内嵌 `new` 初始化器（8.1）**：`public Logger $log = new NullLogger();` 属性默认值可为 new 表达式（不能引用其他属性）
- **抽象方法的可见性**：接口方法天然外部可见；抽象类中 `abstract protected` 常见，`abstract private` 不合法
- **`enum` + `readonly` + DNF** 是 8.3 代码库主流的领域建模组合拳

## 相关文档

- 📄 **[PHP 关键字详解](./01-php-keywords.md)** — `enum`/`readonly` 等关键字本身
- 📄 **[数组操作模式](./05-arrays-patterns.md)** — 一等公民 callable 与集合操作结合
- 📄 **[教程：高级特性](../../basics/07-advanced-features.md)** — 本表各特性的渐进式讲解
