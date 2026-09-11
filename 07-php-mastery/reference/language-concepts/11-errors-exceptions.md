# 异常体系与错误处理

## 概述

PHP 7+ 把引擎错误与用户异常统一到 `Throwable` 之下：`Error` 表达程序级错误（类型、值域），`Exception` 表达业务与运行时异常。本文收录层级结构、常用异常类、处理语法与全局钩子，属语言稳定层（Throwable 体系 7.0+）。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#异常` `#Error` `#Throwable` `#错误处理` |
| **更新日期** | `2026年9月` |

## 条目 1：Throwable 层级

📌 **定义**: 所有可抛出对象实现 `Throwable` 接口，下设两棵树：`Error`（引擎/编程错误，通常不应捕获后继续跑）与 `Exception`（可预期的业务异常）。`catch (Throwable $e)` 才能兜住一切。

📖 **语法/签名**:

```text
Throwable
├── Error
│   ├── TypeError                 类型不匹配
│   ├── ValueError                值不在合法域（8.0+）
│   ├── DivisionByZeroError       除零
│   ├── UnhandledMatchError       match 无命中且无 default（8.0+）
│   ├── ArithmeticError           数学运算越界（如 int 移位溢出）
│   └── AssertionError            assert() 失败（zend.assertions=-1 时关闭）
└── Exception
    ├── LogicException            程序逻辑错误（应修代码）
    │   ├── InvalidArgumentException
    │   ├── OutOfRangeException / DomainException / LengthException ...
    ├── RuntimeException          运行环境故障（可重试/降级）
    ├── PDOException / JsonException / RandomException(8.2+) ...
    └── 自定义异常（业务层从两棵树派生）
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

// TypeError：严格模式下类型不符
function add(int $a, int $b): int
{
    return $a + $b;
}

try {
    add('x', 1);
} catch (TypeError $e) {
    echo $e->getMessage(), PHP_EOL;   // add(): Argument #1 ($a) must be of type int, string given
}

// ValueError：类型对、值不合法（8.0+ 大量函数改抛它）
try {
    explode('', 'a,b');
} catch (ValueError $e) {
    echo '分隔符不能为空', PHP_EOL;
}

// UnhandledMatchError：match 穷尽性失守
try {
    match ('c') {
        'a' => 1, 'b' => 2,     // 没有 default，'c' 直接抛
    };
} catch (UnhandledMatchError $e) {
    echo '状态漏了 case', PHP_EOL;
}
```

⚠️ **常见陷阱**: "致命错误不能捕获"的旧结论已过时——8.x 中 `TypeError` 等都是 Throwable 可捕获，但**捕获后进程状态可能已损坏**，捕获 Error 要谨慎；内存耗尽等真正的 fatal error 依然不可捕获。

🔗 **相关条目**: [try/catch/finally 与异常链](#条目-2trycatchfinally-与异常链)、[教程：错误与异常](../../basics/06-error-exceptions.md)

## 条目 2：try/catch/finally 与异常链

📌 **定义**: `try` 包裹风险代码，`catch` 按子类优先顺序匹配（可多个类型用 `|` 联合捕获），`finally` 无条件执行（清理资源）；构造新异常时把原异常传入 `$previous` 参数保留因果链。

📖 **语法/签名**:

```php
try {
    // ...
} catch (SpecificException | AnotherException $e) {   // 联合捕获（7.1+）
} catch (Throwable $e) {                                // 父类兜底放最后
} finally {
    // 无论是否抛出都执行（含 catch 中 return/throw 的情况）
}
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

final class PaymentFailed extends RuntimeException
{
}

function charge(int $cents): void
{
    try {
        if ($cents <= 0) {
            throw new InvalidArgumentException('amount must be positive');
        }
        throw new RuntimeException('gateway timeout');
    } catch (RuntimeException $e) {
        // ✅ 关键：previous 保留根因，日志里能看到完整链条
        throw new PaymentFailed('支付失败', 0, $e);
    } finally {
        echo '连接已释放', PHP_EOL;      // 抛出前也执行
    }
}

try {
    charge(-5);
} catch (PaymentFailed $e) {
    echo $e->getMessage(), PHP_EOL;
    echo $e->getPrevious()?->getMessage(), PHP_EOL;   // amount must be positive
}
```

⚠️ **常见陷阱**: 重抛时丢掉 `$previous` 是日志排障的头号灾难；`finally` 里再抛异常会**顶替**原异常；catch 顺序从具体到宽泛，`catch (Exception)` 放前面会让后面的具体 catch 变死代码。

🔗 **相关条目**: [自定义异常体系](#条目-3自定义异常体系)

## 条目 3：自定义异常体系

📌 **定义**: 按业务域建立异常层级，继承 `LogicException`（调用方编程错误）或 `RuntimeException`（环境/外部故障），让调用方按"异常类型"而非"错误字符串"分流处理。

📖 **语法/签名**:

```text
LogicException 系      = 程序写错了（应修代码，不该在运行期"处理"）
RuntimeException 系    = 运行环境问题（可重试/降级/告警）
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

namespace App\Exception;

// 业务域异常基类：统一携带领域错误码
abstract class OrderException extends \RuntimeException
{
    abstract public function errorCode(): string;
}

final class InsufficientStock extends OrderException
{
    public function errorCode(): string
    {
        return 'ORDER_STOCK_SHORT';
    }
}

// 调用方按类型分流（而不是解析 message）
try {
    // placeOrder(...);
} catch (OrderException $e) {
    http_response_code(409);
    echo json_encode(['code' => $e->errorCode(), 'msg' => $e->getMessage()]);
}
```

⚠️ **常见陷阱**: 不要为"每种错误一个类"爆炸式建类——先分"可重试/不可重试"两轴；异常的 `message` 给人看、`code/errorCode` 给机器看，别混。

🔗 **相关条目**: [Throwable 层级](#条目-1throwable-层级)

## 条目 4：全局钩子与错误等级

📌 **定义**: `set_error_handler` 把 warning/notice 等转为可处理对象（通常转抛 `ErrorException`），`set_exception_handler` 兜底未捕获异常；`error_reporting` 控制哪些等级进入处理器。

📖 **语法/签名**:

```php
set_error_handler(?callable $handler, int $levels = E_ALL): ?callable
// handler(int $errno, string $errstr, string $file, int $line): bool
set_exception_handler(?callable $handler): ?callable
restore_error_handler(): void / restore_exception_handler(): void
error_reporting(int $level = ?): int     // E_ALL & ~E_DEPRECATED 等
get_error_handler(): ?callable           // 8.5 新增
get_exception_handler(): ?callable       // 8.5 新增
```

💡 **示例**:

```php
<?php

declare(strict_types=1);

// 把"警告/通知"升格为异常——让意外显式化（框架入口的标配）
set_error_handler(function (int $errno, string $errstr, string $file, int $line): bool {
    if (! (error_reporting() & $errno)) {
        return false;                       // 被 @ 抑制的，交还原生逻辑
    }
    throw new ErrorException($errstr, 0, $errno, $file, $line);
});

// 未捕获异常的最终防线：记日志 + 返回 500
set_exception_handler(function (Throwable $e): void {
    error_log($e->__toString());
    http_response_code(500);
    echo json_encode(['error' => 'internal']);
});
```

⚠️ **常见陷阱**: 设置 error handler 后 `@` 抑制符仍会触发 handler（用 `error_reporting()` 检查位掩码再 return false）；8.5 起可用 `get_error_handler()`/`get_exception_handler()` 检查是否已有钩子，避免测试环境互相覆盖；生产 `display_errors` 必须关闭。

🔗 **相关条目**: [Throwable 层级](#条目-1throwable-层级)、[故障排除](../quick-references/02-troubleshooting.md)

## 条目 5：异常使用准则

📌 **定义**: 异常是"异常控制流"，不是返回码替代品：**可预期的分支用返回值/可空类型，破坏性偏差才抛异常**；库抛具体异常、应用层统一转 HTTP 响应。

📖 **语法/签名**: 无新 API；准则条目。

💡 **示例**:

```php
<?php

declare(strict_types=1);

// ✅ 可预期：查不到返回 null，调用方分支处理
function findUser(int $id): ?array
{
    return null;
}

// ✅ 不可预期/违反契约：直接抛
function withdraw(int $balance, int $amount): int
{
    if ($amount > $balance) {
        throw new \DomainException('余额不足');    // 违反业务不变量
    }
    return $balance - $amount;
}

// ❌ 反例：用异常做普通流程控制（等价 goto，且栈展开昂贵）
// try { findUser($id); } catch (NotFound) { 注册新用户(); }
```

⚠️ **常见陷阱**: 循环体内 try/catch 抛接异常有可测开销；空 `catch {}` 吞异常等于埋雷，至少记日志；`assert()` 不是校验工具（生产可被 zend.assertions 关闭）。

🔗 **相关条目**: [自定义异常体系](#条目-3自定义异常体系)、[错误与异常教程](../../basics/06-error-exceptions.md)

## 相关文档

- 📄 **[错误与异常（教程）](../../basics/06-error-exceptions.md)** — 渐进式讲解入口
- 📄 **[控制流程](./04-control-flow.md)** — match 穷尽性与 UnhandledMatchError 的关系
- 📄 **[生产级 Laravel 应用](../../projects/04-production-laravel-app.md)** — 框架层统一异常渲染实践

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
