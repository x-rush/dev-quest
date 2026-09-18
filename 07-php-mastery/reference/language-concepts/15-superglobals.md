# 超全局变量（Superglobals）

> **模块**: `07-php-mastery` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

超全局变量是 PHP 在**全部作用域**内自动可用的内置数组（函数/方法内无需 `global`）。它们是 HTTP 请求与运行环境的数据入口，同时也是不可信输入的集合——区分客户端字段、服务器配置和应用维护状态；客户端输入必须验证，环境信息还可能包含敏感配置。`register_globals`（把请求参数直接注入普通变量）已在 PHP 5.4 移除，现代 PHP 只通过这些数组访问请求数据。

## 📖 各超全局一览

| 变量 | 内容 | 关键点 |
|------|------|--------|
| `$_GET` | URL 查询参数 | 顺序无关；数组语法 `?ids[]=1` |
| `$_POST` | 请求体表单字段 | 仅 `application/x-www-form-urlencoded` 与 `multipart/form-data` 会填充；JSON 体要用 `php://input` |
| `$_REQUEST` | `$_GET` + `$_POST` + `$_COOKIE` 的合并 | 合并顺序由 `request_order` ini 决定（默认 GP，Cookie 不进）；来源不明，不建议使用 |
| `$_SERVER` | 服务器与执行环境信息 | 常用键见下表；`HTTP_*` 前缀键来自请求头，**可伪造** |
| `$_FILES` | 上传文件信息 | 见下 |
| `$_COOKIE` | 请求携带的 Cookie | 客户端可控 |
| `$_SESSION` | 会话数据 | 通常在成功启动会话后可用；启动前可能未定义，自动会话配置也会改变时机 |
| `$_ENV` | 环境变量 | 是否填充取决于 `variables_order` 含 `E` |
| `$GLOBALS` | 全局作用域所有变量的引用集合 | PHP 8.1 起**整体赋值/整体 unset 是编译错误**（预期："\$GLOBALS can only be modified using the \$GLOBALS[\$name] = \$value syntax"），元素级读写仍可用 |

### $_SERVER 常用键

| 键 | 含义 |
|----|------|
| `PHP_SELF` | 当前脚本路径（相对文档根，可被 PATH_INFO 注入，输出时需 `htmlspecialchars`） |
| `REQUEST_METHOD` | GET/POST/PUT… |
| `QUERY_STRING` | 原始查询串 |
| `DOCUMENT_ROOT` / `SCRIPT_NAME` / `SCRIPT_FILENAME` | 文档根 / 相对路径 / 绝对路径 |
| `HTTP_HOST` / `HTTP_USER_AGENT` / `HTTP_REFERER` | 请求头 Host / UA / Referer（全部可伪造） |
| `REMOTE_ADDR` | 客户端 IP（经代理时是代理 IP；代理头可能映射到 HTTP_X_FORWARDED_FOR；只能依据已配置的可信代理解释） |
| `REQUEST_TIME` / `REQUEST_TIME_FLOAT` | 请求开始时间戳（float 版含微秒） |
| `argv` / `argc` | CLI 参数（CLI 预期 $_SERVER 还会混入环境变量） |

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
$email = filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL);   // 预期合法返回字符串、非法返回 false
$page  = filter_var($_GET['page'] ?? '1', FILTER_VALIDATE_INT,
          ['options' => ['min_range' => 1, 'max_range' => 100]]);    // 预期越界返回 false

// 从请求上下文取（读取原始 SAPI 输入，不一定反映代码对 $_GET 的后续修改；CLI/无输入上下文返回 null——预期）
$id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);

// 原始请求体（JSON API 场景，$_POST 拿不到）
$body = file_get_contents('php://input');
if ($body === false) { throw new RuntimeException('读取请求体失败'); }
$payload = json_decode($body, true, 512, JSON_THROW_ON_ERROR); // 请求入口另设大小限制

// 输出转义是另一道防线：验证 ≠ 转义
echo htmlspecialchars($_GET['q'] ?? '', ENT_QUOTES, 'UTF-8');
```

## ⚠️ 常见陷阱

- ❌ **信任 `$_SERVER['HTTP_*']`、`$_FILES['x']['type']`、`$_FILES['x']['name']`**：全部由客户端控制。
- ✅ MIME 用 finfo 对临时文件内容进行服务端探测，结果仍需结合允许类型与文件解析验证；存储名用 `bin2hex(random_bytes(8))` 自行生成。
- ❌ **用 `$_REQUEST` 图省事**：来源混合、顺序随 `request_order` 变化，Cookie 也能覆盖同名参数。
- ✅ 按语义选 `$_GET` / `$_POST`。
- ❌ **JSON 请求读 `$_POST`**：非表单 Content-Type 时它是空数组（预期 `$_GET/$_POST/$_REQUEST/$_FILES/$_COOKIE` 在无请求上下文均为 `[]`）。
- ✅ 读 `php://input` 再 `json_decode`。
- ❌ **函数内写 `$GLOBALS = [...]` 批量改**：8.1 起编译错误。
- ✅ 逐元素 `$GLOBALS['key'] = ...`，或更优：通过参数与返回值传递状态。
- ❌ **`$_SESSION` 在 `session_start()` 前读写**：尚未建立会话存储关联，不能依赖未定义变量的读写实现持久化。

<!-- full-library-explanation -->
## 请求参数先检查形状，再检查值

前置是数组、类型判断和 HTTP。`?page=1` 通常得到字符串，而 `?page[]=1` 得到数组；不能假设所有查询参数都能直接传给接收 string 的函数。框架的 Request 对象通常封装这些入口，但仍需要同样的形状与范围验证。

```php
<?php
$raw = $_GET['page'] ?? '1';
if (!is_string($raw)) {
    http_response_code(400);
    exit('page must be a string');
}
$page = filter_var($raw, FILTER_VALIDATE_INT,
    ['options' => ['min_range' => 1, 'max_range' => 100]]);
if ($page === false) {
    http_response_code(400);
    exit('invalid page');
}
echo $page;
```

**练习**：分别请求无 page、page=2、page=0、page[]=2，预期只有前两种成功。上传还要先检查 error、大小和实际内容，不能只修改扩展名；文件名由服务端生成，文件所有权由业务授权决定。$_SESSION 通常保存在服务端，但其中若放入未经验证的输入也不会自动变可信；$_ENV 可能含密钥，不应整包输出诊断。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

## 🔗 相关条目

- 📄 **[HTTP、会话与 Cookie](../library-guides/06-http-session-cookie.md)** — setcookie/session 的正确用法与会话固定防护
- 📄 **[文件与流 I/O](../library-guides/05-file-stream-io.md)** — `php://input` 与流包装器
- 📄 **[弱比较与强比较](./13-weak-comparison.md)** — 处理请求数据时规避 `==`
- 🌐 **[php.net: 预定义变量](https://www.php.net/manual/zh/reserved.variables.php)** — 全部超全局的官方说明

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
