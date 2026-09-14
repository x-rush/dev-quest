# 魔术方法全表（Magic Methods）

> **模块**: `07-php-mastery` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

魔术方法是以 `__` 双下划线开头、由 PHP 引擎在特定时机**自动调用**的方法。命名保留给引擎，自定义方法不得使用该前缀。全部行为在 PHP 8.5.10 实测。

## 📖 触发时机总表

| 方法 | 触发时机 |
|------|---------|
| `__construct(...$args)` | `new` 实例化时（可与构造器属性提升并用） |
| `__destruct()` | 对象引用清零 / 脚本结束时（实测：`unset($a)` 立即触发，克隆出的副本在脚本结束时各自触发） |
| `__get($name)` | 读取**不可访问**（未声明/private/protected）属性时 |
| `__set($name, $value)` | 写入不可访问属性时（返回值被忽略） |
| `__isset($name)` | 对不可访问属性调用 `isset()`/`empty()` 时（实测 `empty()` 也会触发） |
| `__unset($name)` | 对不可访问属性调用 `unset()` 时 |
| `__call($name, $args)` | 调用不可访问的**实例**方法时 |
| `__callStatic($name, $args)` | 调用不可访问的**静态**方法时（必须 `public static`） |
| `__toString(): string` | 对象被当作字符串使用（echo、拼接、`(string)` 强转）时 |
| `__invoke(...$args)` | 对象被当作函数调用 `$obj(...)` 时 |
| `__clone()` | `clone` 复制完成后被调用 |
| `__debugInfo(): array` | `var_dump()`/`var_export()` 对象时，返回值替代默认属性展示 |

序列化族（本条目不展开）：`__sleep`/`__wakeup`、8.1 起推荐的 `__serialize`/`__unserialize`、`var_export` 用的 `__set_state`。属性级拦截另有 8.4 属性钩子（`get`/`set`），见 **[PHP 8.4/8.5 增量特性](./12-modern-php-85.md)**。

## 💡 示例

```php
class Entity
{
    private array $data = [];

    public function __get(string $name): mixed          // 不可访问属性读取
    {
        return $this->data[$name] ?? null;
    }

    public function __set(string $name, mixed $value): void
    {
        $this->data[$name] = $value;
    }

    public function __isset(string $name): bool          // isset()/empty() 都走这里
    {
        return isset($this->data[$name]);
    }

    public function __call(string $name, array $args): mixed   // "findByXxx" 风格转发
    {
        return "via __call($name)";
    }

    public static function __callStatic(string $name, array $args): mixed
    {
        return "via __callStatic($name)";
    }

    public function __toString(): string
    {
        return 'Entity:' . count($this->data);
    }

    public function __invoke(int $times): int            // $obj(3) 形式的调用
    {
        return $times * 2;
    }

    public function __clone(): void
    {
        // 深复制内部可变成员的标准位置
    }

    public function __debugInfo(): array                 // var_dump 视图脱敏
    {
        return ['fields' => count($this->data)];
    }
}

$e = new Entity();
$e->name = 'x';          // __set
var_dump($e->name);      // __get → 'x'
var_dump(isset($e->name));  // __isset → true
echo $e->anything();     // __call
echo Entity::anything(); // __callStatic
echo $e;                 // __toString
var_dump($e(21));        // __invoke → int(42)
var_dump($e);            // __debugInfo
```

### 8.5 clone() 批量覆盖与 __clone 的先后

```php
class Point
{
    public function __construct(public int $x, public int $y = 0) {}
    public function __clone(): void { $this->y = $this->x + 1; }
}

$q = clone(new Point(10), ['x' => 20]);
var_dump($q->x, $q->y);   // int(20), int(11)
```

实测结论：执行顺序是 **浅复制 → `__clone()` → 属性覆盖**——`__clone` 内读到的是**旧值**（x=10，算出 y=11），覆盖在之后生效（x=20）。依赖覆盖值的逻辑不能写在 `__clone` 里。

## ⚠️ 常见陷阱

- ❌ **在 `__toString` 中抛异常后假设调用方没准备**：允许抛出是 PHP 7.4 才有的行为（7.3 及之前是致命错误）；且字符串转换可能发生在错误消息、日志拼接等"无意"上下文中。
- ✅ `__toString` 保持纯净、无副作用，异常仅留给真正的失败场景（实测 `try { echo (string) $obj; } catch (RuntimeException $e)` 可正常捕获）。
- ❌ **在 `__get`/`__set` 里读写同名属性**：`$this->$name = ...` 若落到已声明属性之外会再次触发 `__set`，形成无限递归。
- ✅ 转存到独立容器（如 `$this->data[$name]`）。
- ❌ **以为 `isset($obj->prop)` 与 `empty($obj->prop)` 只查属性**：对不可访问属性都会转入 `__isset`（实测两者均触发），`empty()` 在 `__isset` 为 true 后还会经 `__get` 取值判断真值。
- ✅ 在 `__isset` 中给出与 `__get` 一致的语义。
- ❌ **`__callStatic` 声明为非 static 或非 public**：引擎不认，访问不可见静态方法直接报错。
- ✅ 固定写 `public static function __callStatic(...)`。
- ❌ **在 `__clone` 中读取 `clone($obj, [...])` 的覆盖值**：覆盖发生在 `__clone` 之后（实测）。
- ✅ 覆盖相关的派生逻辑放在克隆后的调用方，或用属性钩子。
- ❌ **用 `__call` 承载热路径**：每次调用都走转发，无法被 OPcache 内联，也比直接方法慢。
- ✅ 显式声明方法；`__call` 留给 DSL/门面场景。

## 🔗 相关条目

- 📄 **[值语义与引用](./14-references-value-semantics.md)** — clone 与对象复制的底层语义
- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — readonly/属性可见性与不可访问属性的边界
- 📄 **[PHP 8.4/8.5 增量特性](./12-modern-php-85.md)** — 属性钩子对 `__get`/`__set` 场景的替代
- 🌐 **[php.net: 魔术方法](https://www.php.net/manual/zh/language.oop5.magic.php)** — 官方说明

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
