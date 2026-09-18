# SPL 与标准库核心扩展

## 概述

SPL（Standard PHP Library）随 PHP 内核发布，提供数据结构、迭代器、异常与文件处理工具；本文同时覆盖 `ArrayAccess`/`Countable`/`Iterator` 等核心接口与常用内置扩展（mbstring、JSON、PCRE）。全部内容无需 Composer 安装。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#SPL` `#标准库` `#迭代器` `#数据结构` `#扩展` |
| **更新日期** | `2026年9月` |

</details>

## 1. SPL 数据结构

### SplStack / SplQueue

**定义**: 双向链表实现的栈与队列，性能优于 `array_shift`（后者 O(n)）。

```php
$stack = new SplStack();
$stack->push('a');
$stack->push('b');
$stack->push('c');
echo $stack->pop(), PHP_EOL;      // c：后进先出
echo $stack->top(), PHP_EOL;      // b：窥视不移除

$queue = new SplQueue();
$queue->enqueue('task-1');
$queue->enqueue('task-2');
echo $queue->dequeue(), PHP_EOL;  // task-1：先进先出
```

### SplFixedArray

**定义**: 定长数值索引数组，内存表现取决于元素类型、数量和 PHP 版本，键固定 0..n-1。

```php
$arr = new SplFixedArray(3);
$arr[0] = 'x';
$arr[2] = 'z';
echo $arr->getSize(), PHP_EOL;    // 3
$arr->setSize(5);                 // 扩容

// 与普通数组互转
$plain = $arr->toArray();
$fixed = SplFixedArray::fromArray([1, 2, 3]);
```

**陷阱**: 不支持字符串键——字符串键映射用普通数组；对象身份映射可用 `SplObjectStorage`；扩容是复制操作，频繁 resize 失去性能意义。

### SplObjectStorage

**定义**: 以对象为键的集合/映射，天然防重复对象。

```php
$attached = new SplObjectStorage();

$loggerA = new ArrayObject();
$attached[$loggerA] = 'debug 级';     // 对象 → 数据
$attached->attach(new ArrayObject()); // 仅作集合成员

var_dump($attached->contains($loggerA));   // true：同一实例才相等
$attached->detach($loggerA);
```

**陷阱**: 匹配按对象标识（===）而非属性相等；两个"内容一样"的对象互不相等。

## 2. SPL 迭代器

### ArrayIterator 与 IteratorAggregate

```php
use IteratorAggregate;
use Traversable;

final class Cart implements IteratorAggregate
{
    /** @var list<string> */
    private array $items = [];

    public function add(string $item): void
    {
        $this->items[] = $item;
    }

    public function getIterator(): Traversable
    {
        return new ArrayIterator($this->items);   // 使对象可 foreach
    }
}

$cart = new Cart();
$cart->add('php');
$cart->add('go');

foreach ($cart as $item) {          // 无需暴露内部数组
    echo $item, PHP_EOL;
}
```

### 常用迭代器组合

| 迭代器 | 用途 | 示例 |
|--------|------|------|
| `ArrayIterator` | 包装数组供 foreach | `new ArrayIterator($arr)` |
| `RecursiveIteratorIterator` | 摊平多维结构 | 遍历目录树/嵌套数组 |
| `DirectoryIterator` / `FilesystemIterator` | 目录遍历 | `new DirectoryIterator('.')` |
| `LimitIterator` | 分页式截取 | `new LimitIterator($it, 10, 5)` |
| `CallbackFilterIterator` | 回调过滤 | 延迟求值的 filter |
| `InfiniteIterator` | 循环迭代 | 轮询场景 |

```php
// 递归遍历目录（替代手写递归函数）
$files = new RecursiveIteratorIterator(
    new RecursiveDirectoryIterator('src/', FilesystemIterator::SKIP_DOTS)
);

foreach ($files as $file) {
    if ($file->isFile() && $file->getExtension() === 'php') {
        echo $file->getPathname(), PHP_EOL;
    }
}
```

**陷阱**: 迭代器可以延迟取值，但具体实现也可能提前加载；遍历期间修改底层集合的行为取决于实现；需要快照时先 `iterator_to_array($it)`。

## 3. 核心接口（让类"像"内置类型）

```php
use ArrayAccess;
use Countable;
use Stringable;

final class Bag implements ArrayAccess, Countable, Stringable
{
    private array $data = [];

    // ArrayAccess：$bag['k'] 语法
    public function offsetExists(mixed $offset): bool { return isset($this->data[$offset]); }
    public function offsetGet(mixed $offset): mixed { return $this->data[$offset]; }
    public function offsetSet(mixed $offset, mixed $value): void {
        if ($offset === null) { $this->data[] = $value; }
        else { $this->data[$offset] = $value; }
    }
    public function offsetUnset(mixed $offset): void { unset($this->data[$offset]); }

    // Countable：count($bag)
    public function count(): int { return count($this->data); }

    // Stringable：(string) $bag
    public function __toString(): string
    {
        return json_encode($this->data, JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
    }
}

$bag = new Bag();
$bag['name'] = 'Ada';
echo count($bag), (string) $bag, PHP_EOL;
```

**陷阱**: 实现了 `Stringable` 的对象与字符串比较时仍按对象处理；`offsetGet` 对不存在键的抛错行为由实现者决定（内建数组默认 Warning）。

## 4. SPL 异常体系

**定义**: SPL 在 `RuntimeException`/`LogicException` 下预定义了一组语义化异常，直接复用可减少自定义类。

| 异常 | 语义 | 典型场景 |
|------|------|---------|
| `BadMethodCallException` | 方法不存在/参数不匹配 | 魔法转发的兜底 |
| `OutOfBoundsException` | 索引越界 | 集合按序号取值 |
| `OutOfRangeException` | 逻辑上的范围非法 | 页码超出总页数 |
| `UnexpectedValueException` | 值不符合预期 | 反序列化字段校验 |
| `RuntimeException` | 环境性运行失败 | I/O、外部服务 |

**陷阱**: `OutOfBoundsException`（运行时）与 `OutOfRangeException`（逻辑）分属两棵树，语义区分是"改数据能解决"vs"改代码才能解决"。

## 5. 常用内置扩展要点

### mbstring（多字节字符串）

```php
mb_strlen('现代PHP');                    // 5（按字符）
mb_substr('现代PHP', 2, 2);              // 'PH'
mb_strtolower('HELLO');
mb_detect_encoding($raw, ['UTF-8', 'GBK'], true);
mb_convert_encoding($raw, 'UTF-8', 'GBK');
```

### PCRE（正则）

```php
preg_match('/^v(\d+)\./', 'v8.3.0', $m);   // $m[1] = '8'，返回 0/1
preg_match_all('/\d+/', 'a1b22c333', $all);
preg_replace('/\s+/', ' ', $text);
preg_split('/[,;]/', 'a,b;c');
```

**陷阱**: PHP 正则必须带定界符 `/.../`；失败返回 `false`（如回溯限制爆掉）而非空结果——严格判断用 `=== false`；处理用户输入记得评估回溯风险（ReDoS）。

### JSON / Hash / Random

```php
json_encode($v, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE | JSON_PRESERVE_ZERO_FRACTION);
json_decode($raw, true, 512, JSON_THROW_ON_ERROR);

hash('sha256', $data);
hash_hmac('sha256', $payload, $secret);
password_hash('secret', PASSWORD_BCRYPT);      // 密码专用（自带盐与成本因子）
password_verify('secret', $hash);

random_bytes(16);                               // 密码学安全随机
bin2hex(random_bytes(8));                       // 16 位随机 hex
```

**陷阱**: `md5`/`sha1` 不适合密码存储，一律 `password_hash`；`json_decode` 默认静默返回 `null`，解析外部输入必须 `JSON_THROW_ON_ERROR`。

## 相关文档

- 📄 **[常用内置函数分类全表](../language-concepts/02-built-in-functions.md)** — 函数级速查
- 📄 **[Composer 生态精选](./02-composer-ecosystem.md)** — SPL 之外的三方标准库
- 📄 **[类型系统与现代 OOP](../language-concepts/03-types-oop-modern.md)** — Countable 等接口在交叉类型中的应用


<!-- full-library-explanation -->
## 从集合的行为选择工具

前置是数组、对象身份与 foreach。队列强调先进先出，栈强调后进先出；选择它们首先是让操作意图明确，性能还需按数据规模测量。SplObjectStorage 持有对象的强引用，对象即使离开其他作用域也不会因此释放；若缓存不应延长对象生命，研究 WeakMap 的语义。

IteratorAggregate 每次可以返回新的迭代器，而生成器对象具有自己的当前位置。需要重复遍历时要明确返回的是新游标还是共享游标。iterator_to_array 默认保留键，重复键可能覆盖旧值；希望保留每个值应显式传 false。

**练习**：用两个属性相同的新对象作为 SplObjectStorage 的键，预期 count 为 2；把同一个实例放入两次，预期为 1。再让生成器两次 yield 相同键，比较 iterator_to_array 的第二参数为 true/false 的结果。解释“去重”到底按键、值还是对象身份进行。

扩展随 PHP 分发不等于部署已启用。mbstring 等需要在实际 CLI/FPM 环境分别确认，使用 extension_loaded 和 Composer ext-* 平台依赖声明。依据：[SPL](https://www.php.net/manual/en/book.spl.php)。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
