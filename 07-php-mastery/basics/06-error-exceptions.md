# 错误与异常 - Throwable 的世界

## 先理解，再动手

Throwable 是可捕获错误与异常的共同接口。捕获后应恢复、转换或传播，不是把所有失败都变成成功返回。

**本节自测**：读取不存在文件，检查返回 false，再把失败转成明确异常由入口处理。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

并非所有函数失败都会自动抛异常；先看函数契约，避免 catch 永远等不到预期错误。

</details>

> **文档简介**: 理解 PHP 7+ 统一后的异常层次（Throwable/Error/Exception），学会自定义异常与分层捕获策略
>
> **目标读者**: 需要写出健壮错误处理逻辑的 PHP 初学者
>
> **前置知识**: 完成 [控制流程](./05-control-flow.md)，理解类的继承体系

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#异常` `#Throwable` `#错误处理` `#自定义异常` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 画出 PHP 异常层次结构并解释 Error 与 Exception 的分界
- ✅ 正确使用 try/catch/finally 与多 catch 分支
- ✅ 设计业务异常层次，替代魔法返回值
- ✅ 配置全局异常兜底与错误报告级别

## 1. 异常层次：一切皆 Throwable

PHP 7 起，引擎错误与用户异常统一到 `Throwable` 接口下：

```
Throwable (interface)
├── Error                    # 引擎/编程错误：通常不应捕获后继续运行
│   ├── TypeError            # 类型不匹配（严格模式下高发）
│   ├── ValueError           # 值合法但语义错误（如 array_pad 负长度）
│   ├── ArithmeticError      # 数学错误（位移、整除溢出）
│   │   └── DivisionByZeroError
│   ├── UnhandledMatchError  # match 无 default 且未命中
│   └── AssertionError       # assert() 失败
└── Exception                # 用户/运行时异常：业务代码的主战场
    ├── JsonException        # JSON 编解码失败
    ├── LogicException       # 逻辑错误（改代码才能修复）
    │   ├── InvalidArgumentException
    │   ├── DomainException
    │   └── OutOfRangeException
    ├── RuntimeException     # 运行时环境错误（重试可能解决）
    │   ├── PDOException
    │   └── OutOfBoundsException
    └── SPL 系（RuntimeException 分支）
        ├── RuntimeException / UnexpectedValueException 等
```

**分界原则**：

- `Error` 子类 = "代码写错了"，测试与静态分析应该拦住它，生产中一般不做捕获后继续
- `LogicException` = "调用方用错了"（参数非法、状态不允许），修复靠改调用
- `RuntimeException` = "环境出问题了"（网络失败、DB 宕机），可捕获、可重试

## 2. try / catch / finally 基本功

```php
<?php

declare(strict_types=1);

function parseInt(string $raw): int
{
    if (!ctype_digit($raw)) {
        throw new InvalidArgumentException("非数字输入: {$raw}");
    }
    return (int) $raw;
}

try {
    $count = parseInt($_GET['count'] ?? 'abc');
    echo "数量: {$count}", PHP_EOL;
} catch (InvalidArgumentException $e) {
    echo "参数错误: {$e->getMessage()}", PHP_EOL;
} catch (Throwable $e) {                    // 兜底分支放在最后
    error_log($e);                          // 记录完整堆栈
    echo '服务异常，请稍后重试', PHP_EOL;
} finally {
    echo '—— 清理工作总会执行 ——', PHP_EOL;  // 无论成败都运行
}
```

**要点**：

- `catch` 按**从具体到宽泛**的顺序排列，宽泛的 `Throwable` 只能放最后
- `finally` 在 `return`/`break` 之后依然执行，适合放资源释放
- 抛出异常时**带上上下文**（参数值、操作意图），堆栈之外的信息往往才是排查关键

## 3. 自定义异常：用类型表达业务语义

```php
<?php

declare(strict_types=1);

// 第一步：建立模块级基类，方便上游"一把抓"
abstract class OrderException extends RuntimeException
{
}

// 第二步：具体异常携带结构化上下文
final class InsufficientStockException extends OrderException
{
    public function __construct(
        public readonly string $sku,
        public readonly int $requested,
        public readonly int $available,
    ) {
        parent::__construct(
            sprintf('库存不足: %s 需要 %d, 仅剩 %d', $sku, $requested, $available)
        );
    }
}

final class OrderService
{
    /** @return array{sku: string, quantity: int, status: 'accepted'} */
    public function placeOrder(string $sku, int $qty): array
    {
        $available = 3;   // 模拟查询库存

        if ($qty > $available) {
            throw new InsufficientStockException($sku, $qty, $available);
        }
        // 校验通过后才执行实际写入；这里返回可观察结果，便于调用方决定下一步。
        return ['sku' => $sku, 'quantity' => $qty, 'status' => 'accepted'];
    }
}

// 第三步：调用方按需精捕或泛捕
$svc = new OrderService();

try {
    $svc->placeOrder('PHP-BOOK', 10);
} catch (InsufficientStockException $e) {
    // 精捕：能直接读取结构化字段
    echo "提示用户: {$e->available} 本内可购买", PHP_EOL;
} catch (OrderException $e) {
    // 泛捕：本模块全部订单异常
    echo "订单失败: {$e->getMessage()}", PHP_EOL;
}
```

**命名规范**：异常类名以 `Exception` 结尾，语义具体（`PaymentTimeoutException` 优于 `OrderFailException`）。

## 4. 异常链与异常包装

底层异常向上抛时，用链保留原始现场：

```php
<?php

declare(strict_types=1);

final class UserRepository
{
    public function find(int $id): array
    {
        try {
            return $this->query($id);   // 可能抛 PDOException
        } catch (PDOException $e) {
            // 包装为领域异常，同时用 $e 保留原异常为 previous
            throw new RuntimeException("查询用户 {$id} 失败", 0, $e);
        }
    }

    private function query(int $id): array
    {
        throw new PDOException('connection refused');   // 模拟底层错误
    }
}

try {
    (new UserRepository())->find(42);
} catch (RuntimeException $e) {
    echo $e->getMessage(), PHP_EOL;                            // 查询用户 42 失败
    echo '原因: ' . ($e->getPrevious()?->getMessage() ?? ''), PHP_EOL;  // connection refused
}
```

> ⚠️ **不要"吞异常"**：空 `catch {}` 或只 `echo` 后继续，会让故障失去唯一现场。必须重新抛出或记录后处理。

## 5. 全局兜底与错误报告配置

```php
<?php

declare(strict_types=1);

// CLI / 入口脚本的最后防线：未被捕获的异常统一处理
set_exception_handler(function (Throwable $e): void {
    error_log("[UNCAUGHT] {$e}");        // 完整记录
    fwrite(STDERR, '系统繁忙，请联系管理员' . PHP_EOL);
    exit(1);                             // 非零退出码方便脚本编排判断
});

// 把 Warning/Notice 也转成异常（现代框架默认如此）
set_error_handler(function (int $no, string $msg, string $file, int $line): bool {
    throw new ErrorException($msg, 0, $no, $file, $line);
});

// php.ini 开发环境推荐
// error_reporting = E_ALL
// display_errors = On
// 生产环境：display_errors = Off，log_errors = On
```

Laravel/Symfony 项目中以上机制已由框架接管，直接写业务异常层次即可（见 [`../reference/framework-essentials/01-laravel-essentials.md`](../reference/framework-essentials/01-laravel-essentials.md)）。

## ✅ 最佳实践

异常分类应服务调用方决策，例如非法输入可提示修改，存储失败可能需要重试；只有存在共同处理需求时才建立异常基类，不必每个模块都先搭继承树。

捕获后明确恢复、转换或继续传播，未知错误在边界记录经过脱敏的上下文，客户端得到稳定消息。finally 用于清理，避免 return 覆盖原结果。正常“没有找到”是返回值还是异常由接口契约决定，不能只按性能口号选择。

以“导入一行用户数据”为例：缺邮箱是可解释的输入错误，数据库不可用是基础设施错误。前者让调用方修改这一行，后者应终止或进入明确的重试流程；不要把两种失败都返回空数组，让调用方误以为导入成功。

**最小练习与验收：** 给同一导入函数传有效数据、缺邮箱的数据，再用测试存储主动抛异常。记录成功数、失败行号和稳定错误类别，确认存储异常没有被吞掉。只有能证明操作可安全重试时才重试写入；超时后是否已写入未知，应通过唯一键/幂等设计核实。日志保留关联 ID 和异常原因，对外响应不包含数据库密码或完整堆栈。

## ❓ 常见问题

### Q1: `try` 块里 `return` 了，`finally` 还执行吗？
**A**: 执行。`finally` 在方法真正返回前运行；若 `finally` 中也 `return`，会**覆盖** try 中的返回值——避免这样写。

### Q2: `@file_get_contents()` 抑制错误可行吗？
**A**: 不可行。`@` 只压掉 Warning 不解决失败，且 8.0 起许多失败改为抛异常。应显式 `try/catch` 或检查返回值 `false`。

### Q3: `Error` 和 `Exception` 该分别捕获吗？
**A**: 组件边界处通常只捕获自己定义的业务异常；进程顶层的兜底 handler 才捕获 `Throwable`，让 Error 直接崩出并记录。

## 🎯 练习与实践

### 基础练习
- [ ] 实现 `divide(int $a, int $b): float`，除零时抛 `DivisionByZeroError` 或自定义异常，并写调用方捕获
- [ ] 为第 4 节异常链示例增加第三层包装（Repository → Service → Controller），逐层打印 `getPrevious()`
- [ ] 用 `set_exception_handler` 写一个把未捕获异常输出为 JSON 的 CLI 兜底

### 进阶挑战
- [ ] 设计"重试三次仍失败才抛出"的装饰器函数，用 `RuntimeException` 表达最终失败，保留每次失败的原因
- [ ] 对照第 1 节层次图，逐一触发 `TypeError`、`ValueError`、`UnhandledMatchError`、`DivisionByZeroError`，记录各自触发条件

---

## 🔗 相关文档

- 📄 **[高级特性](./07-advanced-features.md)** — 下一节：枚举、属性注解与 Fibers
- 📄 **[常见错误排查](../reference/quick-references/02-troubleshooting.md)** — 异常报错速查
- 📄 **[Laravel 核心](../reference/framework-essentials/01-laravel-essentials.md)** — 框架如何接管异常渲染


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
