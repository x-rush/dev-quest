# PDO 数据库访问层

> **模块**: `07-php-mastery` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

PDO（PHP Data Objects）是 PHP 内置的数据库**访问抽象层**：统一的连接、预处理语句、事务与取回接口，驱动覆盖 MySQL/PostgreSQL/SQLite 等。它抽象 API，不抽象 SQL 方言。本条目示例在 PHP 8.5.10 + pdo_sqlite 实测。

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

错误模式（php.net 官方）：**PHP 8.0.0 起 PDO 默认错误模式即 `PDO::ERRMODE_EXCEPTION`**（实测 8.5 中 `getAttribute(PDO::ATTR_ERRMODE) === 2`，坏 SQL 直接抛 `PDOException`）；8.0 之前默认是 `ERRMODE_SILENT`。连接失败则无论何种模式都抛 `PDOException`。

## 📖 预处理语句：prepare / execute / bind

```php
$stmt = $pdo->prepare('INSERT INTO users (name, age) VALUES (:n, :a)');

// bindValue：按值绑定，立即拷贝
$name = 'alice';
$stmt->bindValue(':n', $name, PDO::PARAM_STR);

// bindParam：按引用绑定，execute 时才读取变量
$stmt->bindParam(':a', $age, PDO::PARAM_INT);
$age = 99;                      // 实测：execute 插入的是 99，不是绑定时的旧值
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
$row = $stmt->fetch(PDO::FETCH_ASSOC);      // ['id' => 1, 'name' => 'alice', 'age' => 99]，实测原生类型
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
        $pdo->rollBack();                   // 实测：中途坏 SQL 异常后回滚，inTransaction() 为 false
    }
    throw $e;
}
```

## 📖 注入防护要点

- **只有"参数化"是防护**：`prepare` + 占位符绑定，让值永远不参与 SQL 解析。
- 表名/列名/排序方向无法参数化——用白名单映射（`$sortMap = ['name' => 'name', 'age' => 'age'];`）。
- `quote()` 只是转义字符串（实测 `'o''reilly'`），远不如预处理可靠，遗留代码再考虑。
- 关闭模拟预处理（`ATTR_EMULATE_PREPARES => false`）避免多语句注入与本地类型处理差异。
- LIKE 通配符（`%`/`_`）不是注入但需转义业务语义。

## ⚠️ 常见陷阱

- ❌ **`rowCount()` 判断 SELECT 行数**：多数驱动对 SELECT 返回 0 或无意义值（实测 sqlite SELECT 后 `rowCount() === 0`）。
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
