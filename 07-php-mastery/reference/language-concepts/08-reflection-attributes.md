# 反射与属性注解

## 概述

反射（Reflection）让程序在运行时检视类/方法/参数/类型的结构，是容器自动装配、序列化器、验证器等框架设施的地基；属性注解（Attributes，8.0+）是可被反射读取的语言级元数据。两者合起来构成"声明式 PHP"的闭环。属语言稳定层。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#反射` `#Reflection` `#属性注解` `#Attributes` |
| **更新日期** | `2026年9月` |

</details>

## 条目 1：ReflectionClass 与成员检视

📌 **定义**: `ReflectionClass` 报告类的完整结构：常量、属性、方法、接口/父类、是否 abstract/final/enum 等。

📖 **语法/签名**: `new ReflectionClass(object|class-string $objectOrClass)`

💡 **示例**:

```php
<?php

declare(strict_types=1);

$ref = new ReflectionClass(App\Model\Order::class);

$ref->getName();                 // 完整类名
$ref->isFinal();                 // 是否 final
$ref->getInterfaces();           // ReflectionClass[]：实现的接口
$ref->getParentClass();          // ReflectionClass|false，无父类返回 false
$ref->getProperties();           // ReflectionProperty[]
$ref->getMethods();              // ReflectionMethod[]
$ref->getConstructor();          // ?ReflectionMethod（构造器）
$ref->isInstance($obj);          // 类型判断
(new ReflectionClass($obj))->getShortName();   // 对象也能反射；短名如 Order
```

⚠️ **常见陷阱**: 传不存在的类名直接抛 `ReflectionException`（可先用 `class_exists($c, false)` 判）；反射能绕过可见性读取私有成员（`setAccessible` 自 8.1 起默认已无需调用），生产代码慎用。

🔗 **相关条目**: [方法与参数反射](#条目-2reflectionmethod-与-reflectionparameter)

## 条目 2：ReflectionMethod 与 ReflectionParameter

📌 **定义**: 方法级与参数级反射：签名、参数类型、默认值、可否为 null——依赖注入容器"看签名造对象"的全部依据。

📖 **语法/签名**:

```php
new ReflectionMethod(class-string|object $class, string $method)
new ReflectionFunction(Closure|string $fn)
$method->getParameters(): ReflectionParameter[]
$param->getType(): ?ReflectionType
$param->isDefaultValueAvailable(): bool
$param->getDefaultValue(): mixed
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

// 模拟容器的核心：解析构造器依赖链
function build(string $class, array $chain = []): object
{
    if (in_array($class, $chain, true)) {
        throw new LogicException('循环依赖: ' . implode(' -> ', [...$chain, $class]));
    }
    $ref = new ReflectionClass($class);
    if (!$ref->isInstantiable()) {
        throw new LogicException("需要为接口或抽象类配置实现: {$class}");
    }
    $args = [];
    foreach ($ref->getConstructor()?->getParameters() ?? [] as $param) {
        if ($param->isDefaultValueAvailable()) {
            $args[] = $param->getDefaultValue();
            continue;
        }
        $type = $param->getType();
        if (!$type instanceof ReflectionNamedType || $type->isBuiltin() || $param->isVariadic()) {
            throw new LogicException("不支持自动解析参数: {$param->getName()}");
        }
        $name = $type->getName();
        if ($name === 'self' || $name === 'parent') {
            throw new LogicException('教学容器不解析相对类型，请显式配置工厂');
        }
        $args[] = build($name, [...$chain, $class]);
    }
    return $ref->newInstanceArgs($args);
}
```

⚠️ **常见陷阱**: `getType() 可能返回 null、ReflectionNamedType、ReflectionUnionType 或 ReflectionIntersectionType，取 `getName()` 前必须先 `instanceof ReflectionNamedType`；内置类型（int 等）不能当依赖装配。

🔗 **相关条目**: [类型反射](#条目-4类型反射reflectiontype)

## 条目 3：属性注解的读取

📌 **定义**: `getAttributes()` 返回 `ReflectionAttribute[]`；`newInstance()` 才会实例化注解类并执行构造器校验——这是"声明元数据"与"运行时消费"的连接点。

📖 **语法/签名**:

```php
$ref->getAttributes(): ReflectionAttribute[]                 // 全部
$ref->getAttributes(Route::class): ReflectionAttribute[]     // 按类过滤
$attr->getName(): string
$attr->getArguments(): array        // ⚠️ 不校验
$attr->newInstance(): object        // 校验目标与参数后实例化
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

#[Attribute(Attribute::TARGET_METHOD | Attribute::IS_REPEATABLE)]
final class Route
{
    public function __construct(
        public readonly string $path,
        public readonly array $methods = ['GET'],
    ) {}
}

final class HealthController
{
    #[Route('/health')]
    #[Route('/ping', ['GET', 'HEAD'])]
    public function check(): array
    {
        return ['ok' => true];
    }
}

// 框架侧：扫描方法注解注册路由
$method = new ReflectionMethod(HealthController::class, 'check');
foreach ($method->getAttributes(Route::class) as $attr) {
    $route = $attr->newInstance();        // 每条 #[Route] 一个实例
    echo $route->path, PHP_EOL;           // /health、/ping
}
```

⚠️ **常见陷阱**: `getArguments()` 只回原始数组不校验；注解目标不匹配（如把 `TARGET_CLASS` 的注解标在方法上）要到 `newInstance()` 才报错；注解参数必须是常量表达式（8.5 起允许一等公民 callable 引用如 `trim(...)` 与 **static 闭包**，仅 `fn` 箭头函数不允许，见 [8.4/8.5 增量特性](./12-modern-php-85.md) 条目 7）。

🔗 **相关条目**: [ReflectionClass](#条目-1reflectionclass-与成员检视)、[教程：属性注解](../../basics/07-advanced-features.md)

## 条目 4：类型反射（ReflectionType）

📌 **定义**: 参数/属性/返回值的类型声明经 `getType()` 暴露为三种对象：单类型、联合（`|`）、交叉（`&`），配合 `allowsNull()` 完成精确类型推断。

📖 **语法/签名**:

```php
$type->allowsNull(): bool                       // ?T / 显式 null
$named->getName(): string                       // 类名或内置类型名
ReflectionNamedType|ReflectionUnionType|ReflectionIntersectionType
// 联合 getTypes() 的成员在 DNF 类型中还可能包含 ReflectionIntersectionType
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

function parse(string|int|null $raw): void {}

$param = new ReflectionParameter('parse', 0);   // 也可从方法反射拿
$type = $param->getType();

var_dump($type->allowsNull());                  // true
foreach ($type->getTypes() as $t) {             // 联合类型逐个看
    echo $t->getName(), PHP_EOL;                // string int null
}
```

⚠️ **常见陷阱**: `?T` 与 `T|null` 完全等价，反射均为 `ReflectionNamedType`（`allowsNull()` 为 true）；只有非空成员不少于两个的联合（如 `int|string|null`）才是 `ReflectionUnionType`；`static` 返回类型经 `getName()` 得 `'static'`，需按调用类解析。

🔗 **相关条目**: [类型系统全表](./03-types-oop-modern.md)、[方法与参数反射](#条目-2reflectionmethod-与-reflectionparameter)

## 条目 5：使用原则

📌 **定义**: 反射昂贵且破坏封装，可优先在启动或构建期缓存稳定扫描结果，再根据实际性能决定请求路径是否需要进一步优化：框架在启动时把注解/签名扫描结果编译成普通数组/闭包，请求路径直接用编译产物。

📖 **语法/签名**: 无新 API；原则条目。

💡 **示例**:

```php
<?php

declare(strict_types=1);

// ❌ 反例：每个请求反射扫路由（每次 newInstance + 遍历，拖垮性能）

// ✅ 正例：启动期编译一次
$routes = [];
foreach (['App\\Http\\Controller\\HomeController'] as $class) {
    foreach ((new ReflectionClass($class))->getMethods() as $method) {
        foreach ($method->getAttributes(Route::class) as $attr) {
            $route = $attr->newInstance();
            foreach ($route->methods as $verb) {
                $key = strtoupper($verb) . " " . $route->path;
                if (isset($routes[$key])) { throw new LogicException("重复路由: {$key}"); }
                $routes[$key] = [$class, $method->getName()];
            }
        }
    }
}
file_put_contents(
    __DIR__ . '/runtime/routes.php',
    '<?php return ' . var_export($routes, true) . ';',
);
// 运行期：require routes.php，纯数组查表，零反射
```

⚠️ **常见陷阱**: 重复扫描可能带来开销，应结合缓存失效与实际剖析评估；用反射调私有方法做测试是坏味道，说明设计该改。

🔗 **相关条目**: [属性注解的读取](#条目-3属性注解的读取)

## 相关文档

- 📄 **[类型系统与现代 OOP](./03-types-oop-modern.md)** — Attributes 与类型声明条目
- 📄 **[Laravel 核心速查](../framework-essentials/01-laravel-essentials.md)** — 容器自动装配的应用侧视角
- 📄 **[Laravel 架构解析](../../advanced-topics/architecture/01-laravel-architecture.md)** — "反射构造依赖链"如何被容器使用

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team


<!-- full-library-explanation -->
## 反射只能读取结构，不能猜出业务配置

前置是构造器、联合类型和接口。看到参数 MailerInterface，并不能推断应实例化 SMTP、测试替身还是外部 API 实现；看到 string $host，也不能知道配置来自哪里。真正容器还需要绑定表、生命周期、工厂与错误报告。本页 build 仅演示具体类的递归构造，并显式拒绝不支持的情况，不是生产 DI 容器。

读取 Attribute 的描述不等于执行它；newInstance 会调用属性类构造器，构造器可以抛异常或产生副作用。只扫描可信代码中的元数据，定义重复路由、重复标记和无效参数的处理规则。缓存结果时要明确何时失效，否则代码更新后旧路由仍可能生效。

**练习**：建立无参类、依赖具体类的类、需要接口的类和循环依赖类，让 build 前两种成功、后两种给出清晰失败。再定义一个构造时递增计数器的 Attribute，对比 getAttributes 与 newInstance，确认行为何时发生。性能优化应基于剖析结果，不能把每次反射都直接定性为事故。

## 正文提取验证：重复属性的反射实例化

下面的单文件程序从方法读取两个重复的 `Route` 属性，再逐个 `newInstance()`。它验证元数据先被读取、随后按声明参数构造属性对象的最小路径。

<!-- terra-twentytwo-case: php-reflection-repeatable-route -->
```php
<?php

declare(strict_types=1);

#[Attribute(Attribute::TARGET_METHOD | Attribute::IS_REPEATABLE)]
final class Route
{
    /** @param list<string> $methods */
    public function __construct(public string $path, public array $methods = ['GET']) {}
}

final class HealthController
{
    #[Route('/health')]
    #[Route('/ping', ['GET', 'HEAD'])]
    public function check(): void {}
}

$method = new ReflectionMethod(HealthController::class, 'check');
foreach ($method->getAttributes(Route::class) as $attribute) {
    $route = $attribute->newInstance();
    echo $route->path, ':', implode(',', $route->methods), PHP_EOL;
}
```

预期输出是 `/health:GET` 与 `/ping:GET,HEAD`。验证不涉及路由分发、HTTP 请求或容器扫描。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
