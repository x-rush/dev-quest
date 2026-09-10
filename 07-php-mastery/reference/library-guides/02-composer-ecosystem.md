# Composer 生态精选

## 概述

现代 PHP = 语言 + Composer 生态。本文精选每个领域的事实标准包：HTTP（Guzzle）、日志（Monolog）、测试（PHPUnit/Pest）、静态分析（PHPStan/Psalm）与质量工具，含最小上手代码与选型建议。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Composer` `#PSR-4` `#Guzzle` `#Monolog` `#PHPUnit` `#Pest` `#PHPStan` |
| **更新日期** | `2026年9月` |

## 1. Composer 工作流要点

```bash
composer require guzzlehttp/guzzle          # 加生产依赖
composer require --dev phpunit/phpunit      # 加开发依赖
composer install                            # 严格按 lock 安装（CI/生产）
composer update                             # 升级并改写 lock（维护者行为）
composer why-not guzzlehttp/guzzle 8.0      # 依赖冲突诊断
composer why psr/log                        # 谁依赖了某包
composer outdated                           # 可升级清单
composer dump-autoload -o                   # 优化 classmap
```

```json
{
  "require": { "php": ">=8.3" },
  "autoload": {
    "psr-4": { "App\\": "src/" },
    "files": ["src/helpers.php"]
  },
  "autoload-dev": { "psr-4": { "App\\Tests\\": "tests/" } },
  "scripts": {
    "analyse": "phpstan analyse src --level=8",
    "test": "pest"
  }
}
```

**陷阱**: `files` 自动加载每次请求都执行，只放无副作用函数；`composer update` 不带包名会全量升级，CI 中一律 `install`。

## 2. Guzzle — HTTP 客户端

**定义**: 事实标准的 HTTP 客户端，基于 PSR-7/18，支持同步/异步与中间件。

```php
use GuzzleHttp\Client;

$client = new Client([
    'base_uri' => 'https://api.example.com',
    'timeout'  => 5.0,
]);

// 同步 GET
$resp = $client->get('/users/1', ['headers' => ['Accept' => 'application/json']]);
$data = json_decode((string) $resp->getBody(), true, 512, JSON_THROW_ON_ERROR);

// 异步并发（配合 Promise）
$promises = [
    'a' => $client->getAsync('/a'),
    'b' => $client->getAsync('/b'),
];
$results = \GuzzleHttp\Promise\Utils::settle($promises)->wait();
```

**陷阱**: 生产代码面向 `Psr\Http\Client\ClientInterface` 注入而非直接 `new Client`，便于测试替换；未设 `timeout` 默认 0（无限等待），必须显式配置。

## 3. Monolog — 日志

**定义**: PSR-3 标准实现，Handler/Formatter/Processor 三层组合。

```php
use Monolog\Logger;
use Monolog\Handler\StreamHandler;
use Monolog\Handler\RotatingFileHandler;

$log = new Logger('app');
$log->pushHandler(new RotatingFileHandler(__DIR__ . '/logs/app.log', 14, Logger::INFO));
$log->pushHandler(new StreamHandler('php://stderr', Logger::ERROR));   // 错误另投 stderr

$log->info('订单创建', ['order_id' => '3f9c2e10', 'amount' => 99.0]);
$log->error('支付超时', ['trace' => $e->getTraceAsString()]);
```

**陷阱**: 日志上下文必须是 `array`（第二参），字符串拼接会丢结构化能力；Laravel/Symfony 项目日志已内置 Monolog，写 `Log::info()` / `$logger->info()` 即可，勿重复初始化。

## 4. PHPUnit 与 Pest — 测试双雄

### PHPUnit（传统主流）

```php
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\TestCase;

final class MoneyTest extends TestCase
{
    #[Test]
    public function 加法产生新实例(): void
    {
        $a = Money::of(100);
        $b = $a->add(Money::of(50));

        $this->assertSame(150, $b->cents);
        $this->assertNotSame($a, $b);          // 不可变性验证
    }
}
```

### Pest（现代优雅层）

```php
// tests/Unit/MoneyTest.php —— Pest 语法，底层仍是 PHPUnit
it('adds amounts immutably', function (): void {
    $a = Money::of(100);
    $b = $a->add(Money::of(50));

    expect($b->cents)->toBe(150)
        ->and($a->cents)->toBe(100);       // 链式断言
});

it('rejects negative amounts', function (): void {
    Money::of(-1);
})->throws(InvalidArgumentException::class);
```

```bash
vendor/bin/phpunit --testdox      # PHPUnit 运行
vendor/bin/pest --coverage        # Pest 运行（需 xdebug/pcov）
```

**陷阱**: Pest 是 PHPUnit 的语法层，混用两种风格时统一以 Pest 为主；断言失败信息依赖严格比较（`assertSame` vs `assertEquals` 差异是高频错因）。

## 5. PHPStan 与 Psalm — 静态分析

**定义**: 在不运行代码的情况下推导类型并报错，PHP 的"编译期检查"。

```php
/** @return array<string, list<int>> */
function groupScores(array $rows): array
{
    $out = [];
    foreach ($rows as $row) {
        $out[$row['name']][] = $row['score'];   // PHPStan level 6+ 会校验此结构
    }
    return $out;
}
```

```bash
composer require --dev phpstan/phpstan
vendor/bin/phpstan analyse src --level=max

composer require --dev vimeo/psalm
vendor/bin/psalm --init            # 生成配置后运行
```

**要点**：

- 等级 0-9（max），存量项目从 5 起步渐进收紧，新增代码用 `level: max` 基线隔离旧债
- `@template`/`@covariant` 等 DocBlock 泛型是表达集合类型的唯一方式
- Laravel/Symfony 官方提供扩展包（`phpstan/laravel-extension`、`phpstan/phpstan-symfony`）补全框架魔法方法的类型

**陷阱**: `--generate-baseline` 生成的基线文件必须进版本库并定期清零；Psalm 与 PHPStan 注解 95% 兼容，团队二选一，不要混用输出。

## 6. 其他值得记住的标准件

| 包 | 领域 | 一句话定位 |
|----|------|-----------|
| `symfony/console` | CLI | 命令、参数解析、彩色输出，Laravel Artisan 的底座 |
| `vlucas/phpdotenv` | 配置 | `.env` 加载，框架均已内置 |
| `nikic/php-parser` | AST | 静态工具与重构脚本的基石 |
| `ramsey/uuid` | 标识 | RFC 4122 UUID 生成（含 UUIDv7） |
| `brick/math` | 数值 | 任意精度大数，金额计算首选 |
| `carbonphp/carbon` | 日期 | DateTime 的流畅封装（Laravel 内置） |
| `fakerphp/faker` | 测试数据 | 合成数据生成器，Pest/PHPUnit 通用 |
| `friendsofphp/php-cs-fixer` | 风格 | 按 PSR-12 与自定义规则自动修格式 |

```bash
composer require symfony/console ramsey/uuid brick/math
composer require --dev friendsofphp/php-cs-fixer fakerphp/faker
```

## 陷阱速查

- **平台依赖**：`composer.json` 中 `"ext-mbstring": "*"` 声明扩展需求，CI 才能提前失败
- **语义化版本**：`^8.3` 允许 8.x 不允许 9.0；安全升级看 `composer outdated --direct`
- **私有包**：`repositories` 配 VCS 源或 Satis 镜像；`auth.json` 不进版本库

## 相关文档

- 📄 **[SPL 与标准库](./01-standard-library-spl.md)** — 无需 Composer 的内置能力
- 📄 **[教程：环境搭建](../../basics/01-environment-setup.md)** — Composer 安装与锁文件原则
- 📄 **[教程：CLI 任务管理工具](../../basics/08-first-project.md)** — PSR-4 实战
