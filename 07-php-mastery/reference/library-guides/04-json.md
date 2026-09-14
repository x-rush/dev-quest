# JSON 编解码

> **模块**: `07-php-mastery` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

`json_encode()` 将 PHP 值序列化为 JSON 字符串，`json_decode()` 反向解析。JSON 扩展自 PHP 8.0 起内置且不可禁用。本条目行为在 PHP 8.5.10 实测。

## 📖 API 与常用 flags

| 函数/flag | 说明 |
|-----------|------|
| `json_encode($v, $flags, $depth)` | 失败返回 `false`（配 `JSON_THROW_ON_ERROR` 则抛异常）；默认深度 512 |
| `json_decode($json, $assoc, $depth, $flags)` | 默认返回 `stdClass`；`$assoc=true` 返回关联数组；解析失败返回 `null` |
| `JSON_THROW_ON_ERROR` | 8.0+ 推荐必带：失败抛 `JsonException`（实测消息如 "Malformed UTF-8 characters, possibly incorrectly encoded"） |
| `JSON_UNESCAPED_UNICODE` | 中文等非 ASCII 原样输出（实测 `{"名":"字"}` 而非 `名`） |
| `JSON_UNESCAPED_SLASHES` | `/` 不转义 |
| `JSON_PRESERVE_ZERO_FRACTION` | `1.0` 输出 `1.0` 而非 `1`（实测），前端类型不漂移 |
| `JSON_FORCE_OBJECT` | 空数组/索引数组输出 `{}`/对象（实测 `[1,2]` → `{"0":1,"1":2}`） |
| `JSON_BIGINT_AS_STRING`（decode） | 超过 PHP_INT_MAX 的整数解析为 string（实测 30 位整数不再丢精度） |
| `JSON_PRETTY_PRINT` | 带缩进换行，调试友好 |

对象编码规则（实测）：`private`/`protected` 属性**被跳过**，只编码 public；实现 `JsonSerializable` 接口则完全由 `jsonSerialize()` 决定输出。

## 💡 示例

```php
// 推荐的 API 响应模式
function jsonResponse(mixed $data): never
{
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(
        $data,
        JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE | JSON_PRESERVE_ZERO_FRACTION
    );
    exit;
}

// 推荐的解析模式：显式异常 + 类型约束
try {
    $payload = json_decode(file_get_contents('php://input'), true, 512, JSON_THROW_ON_ERROR);
} catch (JsonException $e) {
    http_response_code(400);
    exit(json_encode(['error' => 'invalid json']));
}
$userId = is_int($payload['id'] ?? null) ? $payload['id'] : null;   // 再逐字段校验

// 对象 ↔ 数组
$o = json_decode('{"a":1,"b":{"c":2}}');    // stdClass，$o->b->c === 2（实测）
$a = json_decode('{"a":1}', true);          // ['a' => 1]
var_dump(json_decode('null'));              // NULL——合法 JSON 的 null 与"失败"不可区分（见陷阱）

// 深度限制：默认 512 层，实测超限抛 "Maximum stack depth exceeded"
json_encode($deeplyNested, JSON_THROW_ON_ERROR);   // 深度不足时 JsonException
```

## ⚠️ 常见陷阱

- ❌ **不带 `JSON_THROW_ON_ERROR` 就直接用返回值**：编码失败返回 `false`、解码失败返回 `null`，历史上是大量静默 bug 的来源（如 `json_decode($bad)['key']` 直接 TypeError 或丢数据）。
- ✅ 所有调用点固定携带 `JSON_THROW_ON_ERROR`，try/catch 收口。
- ❌ **`json_decode($str)` 后用 `=== null` 判断失败**：`"null"` 是合法 JSON，解析结果也是 `null`（实测），两者混淆。
- ✅ 先 `json_validate()`（8.3+）做纯校验，或用 `JSON_THROW_ON_ERROR` 让失败走异常路径。
- ❌ **空数组编码后端语义漂移**：`json_encode([])` 是 `[]`（列表），PHP 侧"空对象"却变成列表——实测 `new stdClass()` 才是 `{}`。
- ✅ 依赖 `JSON_FORCE_OBJECT` 或类型明确的 DTO。
- ❌ **让 `json_decode` 默认返回 stdClass 再到处 `->` 取值**：属性名带连字符/保留字无法访问，类型检查也弱。
- ✅ 业务代码统一 `$assoc = true` + DTO/数组校验（或用反射类如 `jsonMapper`）。
- ❌ **大整数直接编码**：超出 `PHP_INT_MAX` 的数字在 encode 阶段精度已损。
- ✅ 输入即以 string 传递，或解码时用 `JSON_BIGINT_AS_STRING`（实测保留 30 位精度）。
- ❌ **编码含私有属性的对象**：非 public 属性直接丢失（实测 `{"c":"3"}`），结构悄悄不完整。
- ✅ 实现 `JsonSerializable`，显式声明对外字段（实测 `{"pub":"yes"}`）。

## 🔗 相关条目

- 📄 **[PDO 数据库访问层](./03-pdo.md)** — 数据库行到 JSON 响应的管道
- 📄 **[SPL 与标准库核心扩展](./01-standard-library-spl.md)** — 内置扩展全景
- 📄 **[字符串与正则](../language-concepts/09-strings-regex.md)** — UTF-8 处理基础
- 🌐 **[php.net: JSON](https://www.php.net/manual/zh/book.json.php)** — 官方文档与常量表

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
