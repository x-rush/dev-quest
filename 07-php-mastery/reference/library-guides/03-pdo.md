# PDO 数据库访问层

## PDO 解决连接与执行，不替你决定业务原子性

前置：SQL 查询、参数与异常。预处理把 SQL 结构和数据参数分开：用户提供标题作为绑定值，而不是拼接进 SQL 文本。表名或排序方向通常不能用普通值占位符替代，需要明确白名单选择。

以转移积分为例：扣 A 与加 B 应放在同一事务里，两步之间失败需要回滚。只分别执行两条成功过的 SQL，不能证明组合操作正确。开启事务后还要保证异常分支释放事务状态，后续连接才不会带着未结束的事务继续使用。

自测：给第二步制造失败，重新查询两边余额，总额与原值都应保持。再用一个含引号的普通姓名作为参数，仍应保存为数据；不要为了测试注入而连接真实业务库。

> **模块**: `07-php-mastery` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

PDO（PHP Data Objects）是 PHP 内置的数据库**访问抽象层**：统一的连接、预处理语句、事务与取回接口，驱动覆盖 MySQL/PostgreSQL/SQLite 等。它抽象 API，不抽象 SQL 方言。请使用项目锁定的 PHP 与驱动版本运行示例确认行为。

## 📖 连接与 DSN

```php
// MySQL
$pdo = new PDO('mysql:host=localhost;dbname=app;charset=utf8mb4', $user, $pass, [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,   // 关闭模拟预处理，交给服务端
]);
// PostgreSQL
$pdo = new PDO('pgsql:host=localhost;port=5432;dbname=app', $user, $pass);
// SQLite
$pdo = new PDO('sqlite:' . __DIR__ . '/app.sqlite');
```

错误模式（php.net 官方）：**PHP 8.0.0 起 PDO 默认错误模式即 `PDO::ERRMODE_EXCEPTION`**；8.0 之前默认是 `ERRMODE_SILENT`。请在目标驱动中用 `getAttribute(PDO::ATTR_ERRMODE)` 和错误 SQL 确认行为；连接失败则无论何种模式都抛 `PDOException`。

## 📖 预处理语句：prepare / execute / bind

```php
$stmt = $pdo->prepare('INSERT INTO users (name, age) VALUES (:n, :a)');

// bindValue：按值绑定，立即拷贝
$name = 'alice';
$stmt->bindValue(':n', $name, PDO::PARAM_STR);

// bindParam：按引用绑定，execute 时才读取变量
$stmt->bindParam(':a', $age, PDO::PARAM_INT);
$age = 99;                      // 预期 execute 插入 99，而不是绑定时的旧值；请在目标驱动确认
$stmt->execute();

// 更常用：execute 参数数组一次性绑定（全部按值）
$pdo->prepare('INSERT INTO users (name, age) VALUES (?, ?)')
    ->execute(['bob', 25]);
```

| API | 语义 | 选型 |
|-----|------|------|
| `bindValue($name, $value, $type)` | 按值，立即拷贝 | 常量值、循环内重用语句时绑定不同字面量 |
| `bindParam($name, &$var, $type)` | 按引用，execute 时读取 | 存储过程 OUT 参数、变量后续还会变化 |
| `execute(?array $params)` | 数组按值绑定 | 最常用；不能混用 `?` 与命名占位符 |

## 📖 取回模式

```php
$stmt = $pdo->query('SELECT id, name, age FROM users');
$row = $stmt->fetch(PDO::FETCH_ASSOC);      // 预期形如 ['id' => 1, 'name' => 'alice', 'age' => 99]；字段类型受驱动配置影响
$row = $stmt->fetch(PDO::FETCH_OBJ);        // stdClass 实例，$row->name
$obj = $stmt->fetchObject(User::class);     // 映射到指定类（属性同名赋值）
$ids = $pdo->query('SELECT id FROM users')->fetchAll(PDO::FETCH_COLUMN);  // 单列数组
$count = $pdo->query('SELECT COUNT(*) FROM users')->fetchColumn();
echo $pdo->lastInsertId();                  // 最近一行自增主键（MySQL 用序列名参数；PgSQL 注意返回 string）
```

## 📖 事务

```php
try {
    $pdo->beginTransaction();
    $pdo->prepare('UPDATE accounts SET balance = balance - ? WHERE id = ?')
        ->execute([100, 1]);
    if ($pdo->query('SELECT balance FROM accounts WHERE id = 1')->fetchColumn() < 0) {
        throw new RuntimeException('余额不足');
    }
    $pdo->commit();
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();                   // 回滚后应检查 inTransaction() 为 false，并验证前序写入未保留
    }
    throw $e;
}
```

### 可复现验收：绑定值与回滚是否真的生效

以下案例用内存 SQLite 验证两件独立的事：参数中的单引号仍作为数据保存；事务中第二步失败后，第一步写入也不会留下。SQLite 适合验证 PDO API 契约，不代表 MySQL/PostgreSQL 的隔离级别、锁、序列或驱动类型转换已经验证。

<!-- runtime-evidence: {"id":"php-pdo-bind-and-rollback","stdout":"name=Ada's task\nrows-after-rollback=1\n"} -->
```php
<?php

declare(strict_types=1);

$pdo = new PDO('sqlite::memory:', null, null, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);
$pdo->exec('CREATE TABLE tasks (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)');

$insert = $pdo->prepare('INSERT INTO tasks (name) VALUES (:name)');
$insert->execute(['name' => "Ada's task"]);
echo 'name=', $pdo->query('SELECT name FROM tasks')->fetchColumn(), PHP_EOL;

try {
    $pdo->beginTransaction();
    $insert->execute(['name' => 'first inside transaction']);
    $insert->execute(['name' => 'first inside transaction']); // UNIQUE 约束失败
    $pdo->commit();
} catch (Throwable) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
}

echo 'rows-after-rollback=', $pdo->query('SELECT COUNT(*) FROM tasks')->fetchColumn(), PHP_EOL;
```

预期输出：

```text
name=Ada's task
rows-after-rollback=1
```

## 📖 注入防护要点

- **只有"参数化"是防护**：`prepare` + 占位符绑定，让值永远不参与 SQL 解析。
- 表名/列名/排序方向无法参数化——用白名单映射（`$sortMap = ['name' => 'name', 'age' => 'age'];`）。
- `quote()` 只是转义字符串；其返回形式受驱动影响，远不如预处理可靠，遗留代码再考虑。
- 关闭模拟预处理（`ATTR_EMULATE_PREPARES => false`）避免多语句注入与本地类型处理差异。
- LIKE 通配符（`%`/`_`）不是注入但需转义业务语义。

## ⚠️ 常见陷阱

- ❌ **`rowCount()` 判断 SELECT 行数**：多数驱动对 SELECT 返回 0 或无意义值；在实际目标驱动上验证后再选择计数查询或逐行读取策略。
- ✅ 用 `COUNT(*)` 或直接遍历结果。
- ❌ **`lastInsertId()` 当 int 用**：不同驱动可能返回 `string`。
- ✅ 显式 `(int)` 转换。
- ❌ **依赖 8.0 前的"静默失败"习惯**：`$pdo->exec($bad)` 在 8.0+ 抛异常而非返回 false——从旧版本升级的代码要补 try/catch。
- ✅ 统一 `ERRMODE_EXCEPTION`（默认已开启），错误处理集中在 catch。
- ❌ **循环内 `bindValue` 后不重新 `execute`**：绑定不会自动执行。
- ✅ `bindValue` 与 `execute()` 成对出现；循环内优先 `bindParam` 或数组 execute。
- ❌ **`fetchAll()` 吃下大结果集**：内存直接撑爆。
- ✅ `fetch()` + while 循环，或设 `ATTR_MAX_COLUMN_LEN`/游标策略（MySQL 可开缓冲查询权衡）。

## 🔗 相关条目

- 📄 **[SPL 与标准库核心扩展](./01-standard-library-spl.md)** — 同为内置扩展的迭代器体系
- 📄 **[JSON 编解码](./04-json.md)** — API 层与 PDO 结果的序列化衔接
- 📄 **[Laravel 速查](../framework-essentials/01-laravel-essentials.md)** — Eloquent/查询构造器对 PDO 的封装
- 🌐 **[php.net: PDO](https://www.php.net/manual/zh/book.pdo.php)** / **[错误与错误处理](https://www.php.net/manual/zh/pdo.error-handling.php)** — 官方文档

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
