# PHP 关键字与保留字详解

## 概述

PHP 关键字（如 `class`、`function`、`enum`）是语言结构，不区分大小写（`TRUE`/`true` 等价，但规范统一小写）；保留字（如 `__halt_compiler()`、软保留的 `match` 早期版本）暂不可用作类名/函数名。部分关键字在不同上下文中语义不同（如 `static`、`list`），本条目按用途归类说明。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#关键字` `#保留字` `#语法基础` |
| **更新日期** | `2026年9月` |

## 1. 结构与声明类

### declare

**定义**: 为代码块设置编译/执行指令，必须是文件或代码块的第一条语句。

**语法与示例**:
```php
declare(strict_types=1);          // 严格类型：影响本文件发起的所有调用
declare(ticks=1) { /* 信号处理 */ }
declare(encoding='UTF-8');
```

**陷阱**: `strict_types` 必须是文件第一条语句，写在 `namespace` 之后会报错；它约束"本文件调用别人"，不影响"别人调用本文件"。

### namespace / use

**定义**: 命名空间解决类/函数名冲突；`use` 导入外部名称并支持别名。

```php
namespace App\Service;

use App\Model\{User, Order};          // 组合导入（PHP 7+）
use App\Model\User as AuthUser;       // 别名解决冲突
use function App\helpers\format;      // 显式导入函数
use const App\MAX_SIZE;               // 显式导入常量
```

**陷阱**: 同名类必须起别名，否则编译错误；`use` 是编译期别名，不是 `require`。

### enum（PHP 8.1+）

**定义**: 定义枚举类型，case 为唯一实例。

```php
enum Level: int
{
    case Debug = 0;
    case Error = 1;
}
```

**陷阱**: 枚举隐式 final，不可 `new`、不可继承；backed 枚举值必须是 int 或 string 且全局唯一。

## 2. 类与 OOP 类

### class / interface / trait / extends / implements

```php
trait Loggable
{
    public function log(string $m): void { error_log($m); }
}

interface Repository
{
    public function find(int $id): ?object;
}

abstract class BaseRepository implements Repository
{
    abstract public function find(int $id): ?object;
}

final class UserRepository extends BaseRepository
{
    use Loggable;    // trait 引入一组可复用方法

    public function find(int $id): ?object { return null; }
}
```

**陷阱**: 类只能单继承 `extends`，但可 `implements` 多接口；trait 冲突需用 `insteadof`/`as` 显式消解。

### readonly（PHP 8.1+）

**定义**: 声明后属性只能在声明处（提升参数或同类内一次初始化）赋值，此后只读。

```php
final class Point
{
    public function __construct(
        public readonly float $x,
        public readonly float $y,
    ) {}
}
```

**陷阱**: `readonly` 与动态属性、8.4 非对称可见性 `(set)` 互斥；`clone with` 是修改只读对象的唯一途径（8.3+）。

### final / abstract / static / instanceof

```php
abstract class Shape
{
    abstract public function area(): float;

    public static function describe(Shape $s): string
    {
        return get_class($s) . ' 面积=' . $s->area();
    }
}

final class Square extends Shape
{
    public function __construct(public readonly float $side) {}

    public function area(): float { return $this->side ** 2; }
}

$s = new Square(3);
var_dump($s instanceof Shape);        // true：运行时类型检查
echo Shape::describe($s), PHP_EOL;
```

**陷阱**: `static::method()` 与 `self::method()` 不同——前者后期静态绑定；`instanceof` 对接口/父类都成立。

## 3. 访问控制类

### public / protected / private / private(set)（8.4）

**定义**: 可见性修饰符。8.4 非对称可见性允许读写权限分开声明。

```php
class Account
{
    public private(set) string $owner = '';   // 外部可读、仅类内可写
    public protected(set) int $attempts = 0;  // 外部可读、子类可写
}
```

**陷阱**: 与 `readonly` 不能组合；可见性是编译期约束，反射可绕过（`ReflectionProperty::setAccessible`）。

## 4. 控制流程类

### if / else / elseif / while / for / foreach / do / switch / break / continue

```php
foreach ($items as $k => $v) {
    if ($v < 0) {
        continue;    // 跳过本轮
    }
    if ($v > 100) {
        break;       // 终止循环
    }
}
```

**陷阱**: `switch` 是弱比较 `==` 且会穿透（忘写 `break`）；新代码用 `match`（严格比较、表达式、无穿透）。

### match（8.0+）

**定义**: 表达式形式的分支选择，返回值、严格比较、未命中抛 `UnhandledMatchError`。

```php
$dir = match ($code) {
    1, 2  => 'up',
    3     => 'down',
    default => '?',
};
```

**陷阱**: 分支只能是单个表达式；故意省 `default` 换穷尽性检查时，未列举值会直接抛异常。

### return / yield / goto

**定义**: `return` 返回并终止；`yield` 在 Generator 中产出值并暂停；`goto` 无条件跳转（限同一文件/上下文）。

```php
function gen(): Generator
{
    yield 'a' => 1;      // 键值均可产出
    yield from [2, 3];   // 委托另一个可迭代
}
```

**陷阱**: `goto` 只能跳出不能跳入循环/函数，现代代码基本不用；`yield from` 会透传返回值。

## 5. 函数与变量类

### function / fn / return / use

```php
$factor = 3;
$triple = fn(int $n): int => $n * $factor;   // 箭头函数：自动按值捕获
$multi = function (int $n) use (&$factor): int {   // 闭包：显式捕获，& 按引用
    return $n * $factor;
};
```

**陷阱**: `use` 在命名空间与闭包两个语境含义不同；箭头函数捕获是"定义时"的值快照。

### new / clone / unset / isset / empty / list / global / static / var

```php
$a = new DateTimeImmutable();
$b = clone $a;                       // 浅拷贝，__clone 可定制
unset($a);                           // 销毁变量（数组中删除键同理）
var_dump(isset($b), empty($c));      // isset: 已设置且非 null；empty: 弱判定空值

[$x, $y] = [1, 2];                   // list 解构（可写成 [] 形式）
['name' => $name] = ['name' => 'Ada'];
```

**陷阱**: `isset` 对嵌套属性短路安全，`empty('0')` 为 true 易踩坑；`clone` 是浅拷贝，嵌套对象仍共享引用。

### static 的第二身份

```php
function counter(): int
{
    static $n = 0;    // 静态局部变量：跨调用保留
    return ++$n;
}
```

**陷阱**: `static $n` 初始化表达式不能包含非常量（8.1 起放宽部分场景）；对象属性不可用 `static` 声明。

## 6. 异常与流程类

### try / catch / finally / throw

```php
try {
    throw new RuntimeException('boom');
} catch (RuntimeException | LogicException $e) {   // 多类型联合捕获
    echo $e->getMessage();
} finally {
    // 无论成败执行
}
```

**陷阱**: catch 顺序从具体到宽泛；`throw` 在 PHP 8.0 起是表达式（可用在 `??`、三元、`||` 中）。

## 7. 其他常用字面保留字

| 关键字 | 用途 | 备注 |
|--------|------|------|
| `const` | 编译期常量（类内/文件顶层） | 8.3 起支持类型化 `const int X = 1` |
| `as` | `use ... as 别名`、trait 冲突消解 | — |
| `insteadof` | trait 同名方法取舍 | trait 冲突必用 |
| `callable` / `iterable` / `mixed` / `never` / `void` | 类型关键字 | 详见 [类型系统全表](./03-types-oop-modern.md) |
| `instanceof` | 运行时类型判断 | 接受类名/接口名表达式 |
| `__halt_compiler()` | 终止编译器（打包器用） | 其后内容被原样忽略 |

## 陷阱速查

- **大小写**：关键字不区分大小写，但 `TRUE`/`False` 风格不符合 PSR-12，统一小写
- **类名保留**：`enum`、`match` 等曾是软保留字，8.0/8.1 后完全保留——旧代码若以其为类名需改名
- **`list()` vs `[]`**：解构推荐 `[]` 形式；`list` 在 `foreach (… as list(…))` 中已随 PHP 7.1 支持 `[]` 而淡出

## 相关文档

- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — 类型关键字（联合/交叉/DNF/never 等）权威条目
- 📄 **[控制结构全表](./04-control-flow.md)** — `match`/`if`/循环的完整语法
- 📄 **[综合练习：CLI 任务管理工具](../../basics/08-first-project.md)** — 在真实项目中运用关键字
