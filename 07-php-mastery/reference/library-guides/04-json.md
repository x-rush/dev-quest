# JSON 编解码

> **模块**: `07-php-mastery` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

`json_encode()` 将 PHP 值序列化为 JSON 字符串，`json_decode()` 反向解析。JSON 扩展自 PHP 8.0 起内置且不可禁用。本条目行为以所用 PHP 版本的规范与运行结果为准。

## 📖 API 与常用 flags

| 函数/flag | 说明 |
|-----------|------|
| `json_encode($v, $flags, $depth)` | 失败返回 `false`（配 `JSON_THROW_ON_ERROR` 则抛异常）；默认深度 512 |
| `json_decode($json, $assoc, $depth, $flags)` | 默认返回 `stdClass`；`$assoc=true` 返回关联数组；解析失败返回 `null` |
| `JSON_THROW_ON_ERROR` | PHP 7.3 起提供，适合显式异常处理：失败抛 `JsonException`（预期消息如 "Malformed UTF-8 characters, possibly incorrectly encoded"） |
| `JSON_UNESCAPED_UNICODE` | 中文等非 ASCII 原样输出，避免编码成 Unicode 转义序列 |
| `JSON_UNESCAPED_SLASHES` | `/` 不转义 |
| `JSON_PRESERVE_ZERO_FRACTION` | `1.0` 输出 `1.0` 而非 `1`（预期），保留文本中的小数部分；JavaScript 解析后仍是 Number |
| `JSON_FORCE_OBJECT` | 空数组/索引数组输出 `{}`/对象（预期 `[1,2]` → `{"0":1,"1":2}`） |
| `JSON_BIGINT_AS_STRING`（decode） | 超过 PHP_INT_MAX 的整数解析为 string（预期 30 位整数不再丢精度） |
| `JSON_PRETTY_PRINT` | 带缩进换行，调试友好 |

对象编码规则（预期）：`private`/`protected` 属性**被跳过**，只编码 public；实现 `JsonSerializable` 接口则完全由 `jsonSerialize()` 决定输出。

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
if (!is_array($payload)) { http_response_code(400); exit('expected object'); }
$userId = is_int($payload['id'] ?? null) ? $payload['id'] : null;   // 再逐字段校验

// 对象 ↔ 数组
$o = json_decode('{"a":1,"b":{"c":2}}');    // stdClass，$o->b->c === 2（预期）
$a = json_decode('{"a":1}', true);          // ['a' => 1]
var_dump(json_decode('null'));              // NULL——合法 JSON 的 null 与"失败"不可区分（见陷阱）

// 深度限制：默认 512 层，预期超限抛 "Maximum stack depth exceeded"
json_encode($deeplyNested, JSON_THROW_ON_ERROR);   // 深度不足时 JsonException
```

## ⚠️ 常见陷阱

- ❌ **不带 `JSON_THROW_ON_ERROR` 就直接用返回值**：编码失败返回 `false`、解码失败返回 `null`，历史上是大量静默 bug 的来源（如 `json_decode($bad)['key']` 直接 TypeError 或丢数据）。
- ✅ 所有调用点固定携带 `JSON_THROW_ON_ERROR`，try/catch 收口。
- ❌ **`json_decode($str)` 后用 `=== null` 判断失败**：`"null"` 是合法 JSON，解析结果也是 `null`（预期），两者混淆。
- ✅ 先 `json_validate()`（8.3+）做纯校验，或用 `JSON_THROW_ON_ERROR` 让失败走异常路径。
- ❌ **空数组编码后端语义漂移**：`json_encode([])` 是 `[]`（列表），PHP 侧"空对象"却变成列表——预期 `new stdClass()` 才是 `{}`。
- ✅ 按字段用 stdClass 或类型明确的 DTO 表达对象；避免全局 JSON_FORCE_OBJECT 改变列表。
- ❌ **让 `json_decode` 默认返回 stdClass 再到处 `->` 取值**：属性名带连字符时需用 $obj->{'key-name'} 等显式语法访问，类型检查也弱。
- ✅ 业务代码统一 `$assoc = true` + DTO/数组校验（或用反射类如 `jsonMapper`）。
- ❌ **大整数直接编码**：超出 `PHP_INT_MAX` 的数字在 encode 阶段精度已损。
- ✅ 输入即以 string 传递，或解码时用 `JSON_BIGINT_AS_STRING`（预期保留 30 位精度）。
- ❌ **编码含私有属性的对象**：非 public 属性直接丢失（预期 `{"c":"3"}`），结构悄悄不完整。
- ✅ 实现 `JsonSerializable`，显式声明对外字段（预期 `{"pub":"yes"}`）。

<!-- full-library-explanation -->
## 解析成功不等于数据符合接口

前置是 PHP 类型与异常。JSON 顶层可以是对象、数组、数字、字符串、布尔值或 null。接口若要求对象，要先验证结构再访问 id；开启 JSON_THROW_ON_ERROR 只保证语法可解析，无法替代字段范围、权限或业务校验。json_validate 适合只验证而不需要结果的场景，马上还要 decode 时先 validate 会重复解析。

关联数组解码会丢失部分 JSON 对象与列表的区别：空对象和空数组都可能变成 []。需要严格对象契约时可先解码为 stdClass，再显式映射 DTO。PHP 能精确保存的整数也可能超过 JavaScript 的安全整数范围，所以跨端 ID 通常在契约中定义为十进制字符串。

**练习**：解析 null、[]、{}、{"id":"42"} 和 {"id":42}，分别检查顶层类型和字段类型。删除列表中间项后编码，观察不连续数字键变成 JSON 对象；使用 array_values 重新编号后应恢复列表。不要全局开 JSON_FORCE_OBJECT 修复空对象，它也会改变其他合法列表。

依据：[json_decode](https://www.php.net/manual/en/function.json-decode.php)、[json_encode](https://www.php.net/manual/en/function.json-encode.php)。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

## 🔗 相关条目

- 📄 **[PDO 数据库访问层](./03-pdo.md)** — 数据库行到 JSON 响应的管道
- 📄 **[SPL 与标准库核心扩展](./01-standard-library-spl.md)** — 内置扩展全景
- 📄 **[字符串与正则](../language-concepts/09-strings-regex.md)** — UTF-8 处理基础
- 🌐 **[php.net: JSON](https://www.php.net/manual/zh/book.json.php)** — 官方文档与常量表

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
