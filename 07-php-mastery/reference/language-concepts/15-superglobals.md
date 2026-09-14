# 超全局变量（Superglobals）

> **模块**: `07-php-mastery` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

超全局变量是 PHP 在**全部作用域**内自动可用的内置数组（函数/方法内无需 `global`）。它们是 HTTP 请求与运行环境的数据入口，同时也是不可信输入的集合——**一律视为用户数据**。`register_globals`（把请求参数直接注入普通变量）已在 PHP 5.4 移除，现代 PHP 只通过这些数组访问请求数据。

## 📖 各超全局一览

| 变量 | 内容 | 关键点 |
|------|------|--------|
| `$_GET` | URL 查询参数 | 顺序无关；数组语法 `?ids[]=1` |
| `$_POST` | 请求体表单字段 | 仅 `application/x-www-form-urlencoded` 与 `multipart/form-data` 会填充；JSON 体要用 `php://input` |
| `$_REQUEST` | `$_GET` + `$_POST` + `$_COOKIE` 的合并 | 合并顺序由 `request_order` ini 决定（默认 GP，Cookie 不进）；来源不明，不建议使用 |
| `$_SERVER` | 服务器与执行环境信息 | 常用键见下表；`HTTP_*` 前缀键来自请求头，**可伪造** |
| `$_FILES` | 上传文件信息 | 见下 |
| `$_COOKIE` | 请求携带的 Cookie | 客户端可控 |
| `$_SESSION` | 会话数据 | `session_start()` 之前是 `null`，之后才是数组（实测） |
| `$_ENV` | 环境变量 | 是否填充取决于 `variables_order` 含 `E` |
| `$GLOBALS` | 全局作用域所有变量的引用集合 | PHP 8.1 起**整体赋值/整体 unset 是编译错误**（实测："\$GLOBALS can only be modified using the \$GLOBALS[\$name] = \$value syntax"），元素级读写仍可用 |

### $_SERVER 常用键

| 键 | 含义 |
|----|------|
| `PHP_SELF` | 当前脚本路径（相对文档根，可被 PATH_INFO 注入，输出时需 `htmlspecialchars`） |
| `REQUEST_METHOD` | GET/POST/PUT… |
| `QUERY_STRING` | 原始查询串 |
| `DOCUMENT_ROOT` / `SCRIPT_NAME` / `SCRIPT_FILENAME` | 文档根 / 相对路径 / 绝对路径 |
| `HTTP_HOST` / `HTTP_USER_AGENT` / `HTTP_REFERER` | 请求头 Host / UA / Referer（全部可伪造） |
| `REMOTE_ADDR` | 客户端 IP（经代理时是代理 IP；`X-Forwarded-For` 不在 $_SERVER 标准键内且可伪造） |
| `REQUEST_TIME` / `REQUEST_TIME_FLOAT` | 请求开始时间戳（float 版含微秒） |
| `argv` / `argc` | CLI 参数（CLI 实测 $_SERVER 还会混入环境变量） |

### $_FILES 上传数组结构

```php
// 表单 <input type="file" name="avatar"> 上传后：
$_FILES['avatar'] = [
    'name'     => 'photo.jpg',        // 客户端原始文件名——不可信，勿直接用作存储名
    'type'     => 'image/jpeg',       // 客户端声明的 MIME——不可信
    'size'     => 204800,             // 字节数
    'tmp_name' => '/tmp/phpA1b2C3',   // 服务端临时文件
    'error'    => UPLOAD_ERR_OK,      // 0=成功，其余见 UPLOAD_ERR_* 常量
];
// 多文件字段 name="files[]" 时得到嵌套数组
```

## 💡 示例：输入过滤与验证

```php
// 验证（FILTER_VALIDATE_* 失败返回 false，而非抛异常）
$email = filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL);   // 实测合法返回字符串、非法返回 false
$page  = filter_var($_GET['page'] ?? '1', FILTER_VALIDATE_INT,
          ['options' => ['min_range' => 1, 'max_range' => 100]]);    // 实测越界返回 false

// 从请求上下文取（与 $_GET 等价但可配合 INPUT_POST 等；CLI/无输入上下文返回 null——实测）
$id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);

// 原始请求体（JSON API 场景，$_POST 拿不到）
$payload = json_decode(file_get_contents('php://input'), true);

// 输出转义是另一道防线：验证 ≠ 转义
echo htmlspecialchars($_GET['q'] ?? '', ENT_QUOTES, 'UTF-8');
```

## ⚠️ 常见陷阱

- ❌ **信任 `$_SERVER['HTTP_*']`、`$_FILES['x']['type']`、`$_FILES['x']['name']`**：全部由客户端控制。
- ✅ MIME 用 `finfo_file($tmp_name)` 服务端探测；存储名用 `bin2hex(random_bytes(8))` 自行生成。
- ❌ **用 `$_REQUEST` 图省事**：来源混合、顺序随 `request_order` 变化，Cookie 也能覆盖同名参数。
- ✅ 按语义选 `$_GET` / `$_POST`。
- ❌ **JSON 请求读 `$_POST`**：非表单 Content-Type 时它是空数组（实测 `$_GET/$_POST/$_REQUEST/$_FILES/$_COOKIE` 在无请求上下文均为 `[]`）。
- ✅ 读 `php://input` 再 `json_decode`。
- ❌ **函数内写 `$GLOBALS = [...]` 批量改**：8.1 起编译错误。
- ✅ 逐元素 `$GLOBALS['key'] = ...`，或更优：通过参数与返回值传递状态。
- ❌ **`$_SESSION` 在 `session_start()` 前读写**：此时它是 `null`，写入不持久化。

## 🔗 相关条目

- 📄 **[HTTP、会话与 Cookie](../library-guides/06-http-session-cookie.md)** — setcookie/session 的正确用法与会话固定防护
- 📄 **[文件与流 I/O](../library-guides/05-file-stream-io.md)** — `php://input` 与流包装器
- 📄 **[弱比较与强比较](./13-weak-comparison.md)** — 处理请求数据时规避 `==`
- 🌐 **[php.net: 预定义变量](https://www.php.net/manual/zh/reserved.variables.php)** — 全部超全局的官方说明

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
