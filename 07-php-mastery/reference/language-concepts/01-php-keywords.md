# PHP 关键字与保留字详解

## 概述

PHP 关键字（如 `class`、`function`、`enum`）是语言结构，不区分大小写（`TRUE`/`true` 等价，但规范统一小写）；保留标识符在类、函数、方法等位置有不同限制；应按当前版本的官方列表检查。部分关键字在不同上下文中语义不同（如 `static`、`list`），本条目按用途归类说明。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#关键字` `#保留字` `#语法基础` |
| **更新日期** | `2026年9月` |

</details>

## 1. 结构与声明类

### declare

**定义**: 为代码块或文件设置指令；strict_types 等指令有文件位置限制，不能推广为所有 declare 都必须在首行。

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

**陷阱**: 枚举隐式 final，不可 `new`、不可继承；backed 枚举统一使用 int 或 string，值必须在该枚举内唯一。

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

**定义**: readonly 属性在允许的写入作用域内初始化后不能再次修改，具体作用域与克隆规则随版本演进。

```php
final class Point
{
    public function __construct(
        public readonly float $x,
        public readonly float $y,
    ) {}
}
```

**陷阱**: readonly 属性必须声明类型；PHP 8.4 可与非对称可见性组合，默认写入可见性为 protected(set)；`clone with`（8.5+，RFC clone_with_v2）是批量覆盖 readonly 对象的途径——8.3 引入的只是 `__clone` 方法内对 readonly 属性的再初始化。

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

**陷阱**: PHP 8.4 可与 readonly 组合；可见性也在运行时检查。反射有专门访问语义，不能把可见性当作进程内安全隔离。

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

**陷阱**: PHP 8.3 起静态局部变量可用动态初始化表达式；类可声明 static 属性，它属于类而不是每个实例。

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
| `const` | 编译期常量（类内/文件顶层） | 8.3 起类常量支持类型声明；文件顶层 const 不使用同样的类型化语法 |
| `as` | `use ... as 别名`、trait 冲突消解 | — |
| `insteadof` | trait 同名方法取舍 | trait 冲突必用 |
| `callable` / `iterable` / `mixed` / `never` / `void` | 类型关键字 | 详见 [类型系统全表](./03-types-oop-modern.md) |
| `instanceof` | 运行时类型判断 | 接受类名/接口名表达式 |
| `__halt_compiler()` | 终止编译器（打包器用） | 其后内容被原样忽略 |

## 陷阱速查

- **大小写**：关键字不区分大小写，但 `TRUE`/`False` 风格不符合 PSR-12，统一小写
- **类名保留**：不要把“有关键字用途”与“所有标识符位置都禁用”混同；类名、方法名等按当前版本规则分别核对
- **`list()` vs `[]`**：解构推荐 `[]` 形式；`list` 在 `foreach (… as list(…))` 中已随 PHP 7.1 支持 `[]` 而淡出

## 相关文档

- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — 类型关键字（联合/交叉/DNF/never 等）权威条目
- 📄 **[控制结构全表](./04-control-flow.md)** — `match`/`if`/循环的完整语法
- 📄 **[综合练习：CLI 任务管理工具](../../basics/08-first-project.md)** — 在真实项目中运用关键字


<!-- full-library-explanation -->
## 同一个词要放回语法位置理解

前置是变量、函数与类。use 在文件顶部建立名称别名，在类体组合 trait，在匿名函数后声明捕获变量；三者不互相替代。static 可以声明类级属性或方法，也可以让函数局部变量在多次调用间保留，还能表达后期静态绑定。速查时先识别位置，再判断语义。

strict_types 主要约束标量参数与返回类型的转换规则，不会自动验证数组结构、HTTP 输入或数据库记录。调用方文件是否启用严格模式会影响用户函数参数的标量转换，int 传入 float 等规则还有例外；不能把它当成全局“所有值都完全严格”的开关。

**练习**：在两个文件中定义接收 int 的函数，分别从严格与非严格文件传入字符串 '12'，观察差异；再传入数组，两者都不应将它当成合法整数。把一个静态局部计数器调用三次，预期依次得到 1、2、3；重新启动 CLI 进程后从 1 开始，不能据此实现跨请求的持久编号。

关键字清单与标识符限制应查 [PHP 保留字](https://www.php.net/manual/en/reserved.php)；版本相关属性规则参见 [属性文档](https://www.php.net/manual/en/language.oop5.properties.php)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
