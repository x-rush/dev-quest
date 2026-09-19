# PHP 关键字与保留字详解

## 概述

PHP 关键字（如 `class`、`function`、`enum`）是语言结构，不区分大小写（`TRUE`/`true` 等价，但规范统一小写）；保留标识符在类、函数、方法等位置有不同限制；应按当前版本的官方列表检查。部分关键字在不同上下文中语义不同（如 `static`、`list`），本条目按用途归类说明。

阅读前先会变量、数组、函数调用。本篇以 PHP 8.3 的普通语法为基础，8.4/8.5 扩展明确标注。含 `<?php` 的三个实验是完整脚本，其余代码围栏是解释局部语法的片段，需放进相应文件/类/函数上下文，不能把整篇拼成一个脚本。

### 分类索引：一个词可能出现在多个位置

| 类别 | 词 | 解决的问题 |
|---|---|---|
| 声明与组织 | `declare namespace use const function fn` | 文件行为、名称、常量和函数；use 并不加载文件 |
| 类型与对象 | `class interface trait enum extends implements abstract final readonly new clone instanceof` | 对象结构、契约、继承与复制；enum 是枚举声明语法，标识符保留规则不能简单按关键字总表推断 |
| 可见性与状态 | `public protected private static var global` | 成员访问、类级/函数局部状态、引用全局变量；var 是旧式 public 属性声明 |
| 条件与选择 | `if elseif else switch case default match` | 判断与选择；switch 弱比较、match 严格比较 |
| 循环与跳转 | `for foreach as while do break continue return goto` | 遍历、终止、跳过、返回；goto 不能跨函数跳转 |
| 替代语法结束词 | `endif endfor endforeach endwhile endswitch enddeclare` | 配对冒号形式的控制结构，常见于模板；不是新的控制算法 |
| 异常 | `try catch finally throw` | 异常传播与清理 |
| 生成器 | `yield`、`yield from` | 按需产出和委托迭代 |
| 变量与数组结构 | `array list isset empty unset` | 数组构造、解构、变量存在/空值检查与解绑；这些并非普通可调用函数 |
| 逻辑词 | `and or xor` | 逻辑运算；and/or 的优先级低于赋值，不能不加思考地代替 &&/\|\| |
| 输出与结束 | `echo print exit die` | 输出与结束执行；exit/die 的调用行为在 PHP 8.4 发生变化，见下方说明 |
| 文件执行 | `include include_once require require_once` | 在当前上下文执行另一个 PHP 文件；不是命名空间导入 |
| trait 选择 | `insteadof as` | 解决同名方法冲突、设置别名/可见性 |
| 少见语言结构 | `eval __halt_compiler` | 执行 PHP 字符串/停止编译后续源码；普通配置不要使用 eval |
| 类型名称 | `callable` 以及 `int string bool float iterable mixed never void object` 等 | 参数/返回/属性类型约束；不同位置允许的类型不同，见[类型系统](./03-types-oop-modern.md) |

官方的[关键字表](https://www.php.net/manual/en/reserved.keywords.php)与[其他保留字](https://www.php.net/manual/en/reserved.other-reserved-words.php)分开列出，类型名、字面值与关键字不可简单混为同一组。`__FILE__`、`__DIR__`、`__LINE__`、`__CLASS__`、`__METHOD__`、`__FUNCTION__`、`__NAMESPACE__`、`__TRAIT__` 是编译位置相关的魔术常量，PHP 8.4 的属性钩子还有 `__PROPERTY__`。

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
`declare(strict_types=1);` 放在 PHP 开始标签后的第一条语句。它改变本文件发起的标量参数调用及本文件函数返回值的类型检查规则，内部函数发起的回调调用等另有规则；它不是“全部数据都严格”的开关。`ticks` 涉及 tick 回调，`encoding` 依赖 Zend 多字节配置；普通入门脚本无需照抄这两个指令。

**陷阱**: `strict_types` 必须是文件第一条语句，写在 `namespace` 之后会报错。用户函数参数是否允许标量转换由调用方决定；函数返回值规则由定义方文件决定。这两个方向不能合并成一句“只影响调用别人”。

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

**陷阱**: readonly 属性必须声明类型；PHP 8.4 可与非对称可见性组合，默认写入可见性为 protected(set)。PHP 8.5 的 `clone($object, ['property' => $value])` 可在克隆副本上覆盖属性，并遵守可见性；“clone with”是特性的称呼，不是可直接写入程序的语法。PHP 8.3 引入的是 `__clone` 方法内对 readonly 属性的再初始化。见[官方克隆说明](https://www.php.net/manual/en/language.oop5.cloning.php)。

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

**陷阱**: `goto` 不能跨函数，也不能跳入循环/switch；可以跳出当前循环。`yield from` 转发键值，其表达式值可以接收被委托生成器的 return 值，不代表所有可迭代对象都有 return 值。

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
    // 正常控制流离开 try/catch 时清理；进程终止等不保证执行
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

## 三个完整实验：从术语回到程序行为

三个实验是彼此独立的完整脚本：每次单独保存为 `keyword-lab.php`（或改用不同文件名），再运行 `php keyword-lab.php`。不要把三个围栏拼进同一文件，否则会重复声明函数。第一个实验同时观察严格标量输入、箭头函数按值捕获、普通闭包按引用捕获以及 match 严格比较。

<!-- reference-case: {"id":"php-keyword-values","stdout":"strict rejected\n6\n10\nstring\n"} -->
```php
<?php
declare(strict_types=1);
function increment(int $value): int { return $value + 1; }
try {
    increment('12');
} catch (TypeError $error) {
    echo 'strict rejected', PHP_EOL;
}
$factor = 3;
$snapshot = fn(int $value): int => $value * $factor;
$live = function (int $value) use (&$factor): int { return $value * $factor; };
$factor = 5;
echo $snapshot(2), PHP_EOL;
echo $live(2), PHP_EOL;
echo match ('1') { 1 => 'integer', '1' => 'string' }, PHP_EOL;
```

输出依次是 strict rejected、6、10、string。练习：去掉 strict_types 声明再运行，字符串 `'12'` 可被转换为 int；改成数组输入则两个模式都拒绝。捕获对象时“按值”复制的是对象标识，并不深拷贝对象内容。

第二个实验区分“同一进程内保留变量”与“持久化”。生成器调用先返回可迭代对象，foreach 消费时才逐步执行函数体。

<!-- reference-case: {"id":"php-keyword-generator","stdout":"1,2,3\n0:4\n1:5\n9:6\n"} -->
```php
<?php
declare(strict_types=1);
function counter(): int {
    static $value = 0;
    return ++$value;
}
function numbers(): Generator {
    yield 4;
    yield 5;
    yield from [9 => 6];
}
echo counter(), ',', counter(), ',', counter(), PHP_EOL;
foreach (numbers() as $key => $value) {
    echo $key, ':', $value, PHP_EOL;
}
```

输出 1,2,3 后依次为 0:4、1:5、9:6。再次启动脚本，计数仍从 1 开始；生成器的委托键 9 不会自动重新编号。普通请求模型与常驻工作进程的生命周期不同，不要用 static 计数当数据库编号。

第三个实验解释 and 的优先级，并在 catch 和 finally 中观察异常路径。

<!-- reference-case: {"id":"php-keyword-control","stdout":"bool(true)\nbool(false)\ncaught\ncleaned\n"} -->
```php
<?php
declare(strict_types=1);
$first = true and false;
$second = (true and false);
var_dump($first, $second);
try {
    throw new RuntimeException('failure');
} catch (RuntimeException $error) {
    echo 'caught', PHP_EOL;
} finally {
    echo 'cleaned', PHP_EOL;
}
```

第一行等价于先赋值 true 再参与 and 运算，所以 first 为 true；括号内先算逻辑结果，second 为 false。PHP 8.4 起 exit/die 具有函数调用语义、遵循相应类型规则；exit 仍会结束执行，不能当作业务函数的普通 return，且它不会执行普通 finally 清理路径。参见 [exit 手册](https://www.php.net/manual/en/function.exit.php)。

`include` 找不到文件会产生警告并返回 false；`require` 失败会产生 Error。二者都可能执行文件中的语句，应使用固定可信路径，通常以 `__DIR__` 为基准。类加载优先遵循 Composer 自动加载规则，use 名称别名不承担加载责任。echo 是输出结构，print 是返回 1 的表达式；也不能把 echo 当作普通回调函数传给 array_map。

验收：能够解释三个实验的每一行输出，并说明返回值、变量重赋值、闭包捕获、进程生命周期四种不同边界。之后进入[CLI 任务项目](../../basics/08-first-project.md)，再把这些语言机制组合为程序。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
