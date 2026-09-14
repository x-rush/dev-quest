# HTTP、会话与 Cookie（原生 PHP 层）

> **模块**: `07-php-mastery` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

PHP 原生层的 HTTP 响应控制（`header()`）、Cookie 写入（`setcookie()`）与会话状态（`session_*()`）API。框架应用（Laravel 13）在这些原语之上封装，见 **[Laravel 速查](../framework-essentials/01-laravel-essentials.md)**；本条目聚焦原语语义。核心行为在 PHP 8.5.10 CLI 实测。

## 📖 header() 与 headers_sent()

```php
if (!headers_sent($file, $line)) {
    header('Content-Type: application/json; charset=utf-8');
    http_response_code(201);            // 设置状态码
    header('Location: /login', true, 302);  // 重定向（response_code 与第三参二选一用法）
} else {
    // 头部已发送，无法再改——$file/$line 指明输出来源
}
```

- 头部必须在**任何输出之前**发送（含 BOM、echo、var_dump）。实测：CLI 下输出前 `headers_sent()` 为 false，`echo` 一次后变 true。
- 输出后再调用 `setcookie()`/`session_start()` 直接返回 `false`（实测），并触发 "headers already sent" 告警。

## 📖 setcookie 参数表

```php
// 现代签名（7.3+）：选项数组，语义明确，推荐
setcookie('sid', $token, [
    'expires'  => time() + 3600,    // Unix 时间戳；0 = 会话 Cookie
    'path'     => '/',
    'domain'   => 'example.com',    // 省略 = 当前主机
    'secure'   => true,             // 仅 HTTPS 传输
    'httponly' => true,             // JS 不可读（document.cookie 拿不到）
    'samesite' => 'Lax',            // Lax（默认推荐）/ Strict / None（None 必须配 secure）
]);
// 旧签名仍可用：setcookie(name, value, expire, path, domain, secure, httponly)（实测返回 true）
// setrawcookie()：value 不做 URL 编码
```

返回值：头部未发送时 `true`；已有输出后 `false`（实测）。Cookie 的**读取**在下一个请求经 `$_COOKIE`，当次请求不可见。

## 📖 会话

```php
session_start();                          // 实测返回 true，状态进入 PHP_SESSION_ACTIVE
$_SESSION['uid'] = 42;

// 登录态变化 / 提权时防会话固定：换 ID 保数据（实测 ID 变化、$_SESSION 保留）
session_regenerate_id(true);

session_write_close();                    // 尽早释放会话锁（实测状态回到 PHP_SESSION_NONE）
```

| 函数/常量 | 说明 |
|-----------|------|
| `session_start()` | 启动/恢复会话；头部已发送时返回 false |
| `session_regenerate_id(bool $delete_old)` | 换发新 ID；`true` 同时删除旧会话数据——**登录成功后必调** |
| `session_status()` | `PHP_SESSION_NONE` / `PHP_SESSION_ACTIVE` / `PHP_SESSION_DISABLED` |
| `session_destroy()` | 销毁会话存储（配合清 `$_COOKIE[session_name()]` 才完整登出） |
| `session.use_strict_mode = 1` | 拒绝未初始化的会话 ID，防固定（本机默认 `0`，实测需显式开启） |

### 会话固定防护清单

1. `php.ini`：`session.use_strict_mode = 1`、`session.cookie_httponly = 1`、`session.cookie_secure = 1`、`session.cookie_samesite = Lax`。
2. 登录/权限变更时 `session_regenerate_id(true)`。
3. 会话 ID 不出现在 URL（`session.use_only_cookies = 1`）。
4. 登出时 `session_destroy()` + 清 Cookie。

## 📖 输入验证与上传处理

```php
// filter_var 验证（实测：合法返回原值，非法返回 false）
$email = filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL);

// 上传：PHP 自动把 multipart 文件放进 $_FILES（结构见超全局条目）
if (($_FILES['avatar']['error'] ?? UPLOAD_ERR_NO_FILE) === UPLOAD_ERR_OK) {
    $tmp  = $_FILES['avatar']['tmp_name'];
    if (is_uploaded_file($tmp)                       // 确认确为 HTTP 上传产物（CLI 实测返回 false）
        && finfo_file(finfo_open(FILEINFO_MIME_TYPE), $tmp) === 'image/jpeg') {
        move_uploaded_file($tmp, $dstPath);          // 原子地移入正式目录并起服务端命名
    }
}
```

## ⚠️ 常见陷阱

- ❌ **输出后调用 `header()`/`setcookie()`/`session_start()`**：实测全部失效/返回 false，Cookie 丢失。
- ✅ 处理流程先逻辑后输出；模板渲染放最后；用 `ob_start()` 兜底缓冲。
- ❌ **`SameSite=None` 不带 `secure`**：浏览器直接拒收。
- ✅ `None` 必配 `secure => true`；拿不准就用 `Lax`。
- ❌ **把 `session_regenerate_id()` 留到"以后再做"**：会话固定攻击直接复用登录前 ID。
- ✅ 登录成功第一行就 `session_regenerate_id(true)`。
- ❌ **信任 `$_FILES['x']['name']`/`['type']`**：均为客户端可控值。
- ✅ 服务端 `finfo` 探测 MIME、随机重命名、`move_uploaded_file` 限定目录。
- ❌ **用 `move_uploaded_file` 之外的方式处理 `tmp_name`**（copy/rename）：绕过 `is_uploaded_file` 安全检查。
- ✅ 标准组合：`is_uploaded_file()` 校验 + `move_uploaded_file()` 落位。
- ❌ **写完 `$_SESSION` 长事务不关会话**：会话文件加锁，同会话请求被串行阻塞。
- ✅ 读写完成后尽早 `session_write_close()`。

## 🔗 相关条目

- 📄 **[超全局变量](../language-concepts/15-superglobals.md)** — `$_COOKIE`/`$_FILES`/`$_SESSION` 数据入口
- 📄 **[文件与流 I/O](./05-file-stream-io.md)** — 上传文件的流式读取
- 📄 **[Laravel 速查](../framework-essentials/01-laravel-essentials.md)** — 框架层 Request/Response/Session 封装
- 🌐 **[php.net: 会话](https://www.php.net/manual/zh/book.session.php)** — 安全配置项官方清单

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
