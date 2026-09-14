# 常量与魔术常量

> **模块**: `07-php-mastery` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

常量是脚本周期内不可重定义的命名值；魔术常量是以 `__` 开头、由引擎在编译期按**所在位置**填充的只读信息。本条目覆盖 `const` vs `define()`、类常量与魔术常量，行为在 PHP 8.5.10 实测。

## 📖 const vs define()

| 维度 | `const` | `define()` |
|------|---------|-----------|
| 生效时机 | **编译期**（先于代码运行） | **运行时**（执行到才定义） |
| 定义位置 | 顶层、类/接口/枚举内 | 任意函数/条件分支内 |
| 表达式支持 | 常量标量表达式（算术、拼接、`**` 等）+ 数组（实测 `const APP = ["v" => 1, "computed" => 2 ** 10];` 可用） | 数组（PHP 7.0+，实测可用）；值可为任意表达式，在执行时求值 |
| 条件定义 | 不可以 | 可以（`if (!defined(...)) define(...)`） |
| 第三参大小写不敏感 | — | 已废弃：PHP 8.0 起不再支持，传入 `true` 触发警告 "Argument #3 (\$case_insensitive) is ignored since declaration of case-insensitive constants is no longer supported"（实测返回 true 但被忽略） |

## 📖 类常量

```php
abstract class Config
{
    private const SECRET = 's';             // PHP 7.1+ 可见性修饰
    public const int TIMEOUT = 30;          // PHP 8.3+ 类型化类常量（类型不符在编译期报错）
    final public const string VERSION = '1.0';  // final 禁止子类覆盖
}

var_dump(Config::TIMEOUT);                  // int(30)
var_dump(Config::SECRET);                   // Error: Cannot access private constant Config::SECRET（实测）
```

- 子类覆盖时必须保持类型兼容（8.3 类型化常量的协变/不变规则）。
- 枚举 case 本质是枚举常量的特殊形态，见 **[类型系统与现代 OOP](./03-types-oop-modern.md)**。

## 📖 魔术常量

| 常量 | 值 |
|------|-----|
| `__LINE__` | 当前行号 |
| `__FILE__` | 完整路径与文件名 |
| `__DIR__` | 文件所在目录（不含尾斜杠，等价 `dirname(__FILE__)`） |
| `__FUNCTION__` | 函数名。**类方法内不含类名**（实测返回 `m`）；普通命名空间函数返回含命名空间全名（实测 `Demo\f`）；闭包中返回 `{closure:文件:行}` 形式 |
| `__CLASS__` | 类名（含命名空间）。**在普通函数中为空字符串**（实测）；trait 中是使用它的类名 |
| `__METHOD__` | 类方法返回 `类名::方法名`（实测 `Demo\C::m`）；普通函数等于 `__FUNCTION__` |
| `__NAMESPACE__` | 当前命名空间名 |
| `__TRAIT__` | 当前 trait 名 |
| `::class` | 类全名。PHP 8.0 起可作用于对象：`$obj::class` 返回运行时类名（实测） |

## 💡 示例

```php
namespace Demo;

class C
{
    const ME = __CLASS__;
    public function m(): array
    {
        return [__METHOD__, __FUNCTION__];   // ['Demo\C::m', 'm']
    }
}

define('APP_NAME', 'dev-quest');            // 运行时常量（含数组值也支持）
var_dump(constant('APP_NAME'));             // 动态取常量
var_dump(constant('\Demo\C::ME'));          // 动态取类常量（实测可用）

$name = 'BAR';
var_dump(C2::{$name});                      // 8.3+ 动态类常量获取（实测 'bv'）
var_dump((new C())::class);                 // 'Demo\C'
```

## ⚠️ 常见陷阱

- ❌ **在函数/条件块里用 `const`**：编译期语义不允许。
- ✅ 动态/条件定义场景用 `define()`。
- ❌ **依赖 `define()` 第三个参数做大小写兼容**：8.0 起被忽略并触发警告（实测），大小写敏感是唯一行为。
- ✅ 统一常量命名约定（全大写 + 下划线）。
- ❌ **在普通函数里写 `__CLASS__` 期望拿到调用者类**：实测为空字符串。
- ✅ 需要运行时类名时通过对象：`$obj::class` 或 `static::class`。
- ❌ **`__METHOD__` 当作"完整限定方法"用于静态晚期绑定场景**：它返回的是**定义处**的类名，经子类调用也不会变成子类名。
- ✅ 需要运行时类用 `static::class`。
- ❌ **把魔术常量当变量拼接 `"$__DIR__"`**：魔术常量不能插值。
- ✅ 直接使用或 `sprintf('%s/file.php', __DIR__)`。
- ❌ **用 `constant()` 取不存在的常量**：抛 `Error`。
- ✅ 先 `defined($name)` 判断，或 try/catch。

## 🔗 相关条目

- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — 类型化类常量与枚举常量
- 📄 **[命名空间与自动加载](./07-namespaces-autoloading.md)** — `::class` 与全限定名解析
- 📄 **[运算符全表](./16-operators.md)** — 常量表达式中可用的运算符
- 🌐 **[php.net: 常量](https://www.php.net/manual/zh/language.constants.php)** / **[魔术常量](https://www.php.net/manual/zh/language.constants.magic.php)** — 官方说明

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
