# HTTP、会话与 Cookie（原生 PHP 层）

> **模块**: `07-php-mastery` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

PHP 原生层的 HTTP 响应控制（`header()`）、Cookie 写入（`setcookie()`）与会话状态（`session_*()`）API。框架应用（Laravel 13）在这些原语之上封装，见 **[Laravel 速查](../framework-essentials/01-laravel-essentials.md)**；本条目聚焦原语语义。核心行为在 PHP 8.5.10 CLI 预期。

## 📖 header() 与 headers_sent()

```php
if (!headers_sent($file, $line)) {
    header('Content-Type: application/json; charset=utf-8');
    http_response_code(201);            // 设置状态码
    header('Location: /login', true, 302);  // 重定向：本行把前面的 201 覆盖为 302；实际响应应选择一种语义
} else {
    // 头部已发送，无法再改——$file/$line 指明输出来源
}
```

- 响应头必须在**响应头实际发送之前**设置；输出缓冲可能延迟发送（含 BOM、echo、var_dump）。预期：CLI 下输出前 `headers_sent()` 为 false，`echo` 一次后变 true。
- 输出后再调用 `setcookie()`/`session_start()` 直接返回 `false`（预期），并触发 "headers already sent" 告警。

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
// 旧签名仍可用：setcookie(name, value, expire, path, domain, secure, httponly)（预期返回 true）
// setrawcookie()：value 不做 URL 编码
```

返回值 true 表示设置操作成功，不能证明客户端已接受；发送头部失败时可返回 false，非法参数还可能抛异常。Cookie 的**读取**在下一个请求经 `$_COOKIE`，当次请求不可见。

## 📖 会话

```php
session_start();                          // 预期返回 true，状态进入 PHP_SESSION_ACTIVE
$_SESSION['uid'] = 42;

// 登录态变化 / 提权时防会话固定：换 ID 保数据（预期 ID 变化、$_SESSION 保留）
session_regenerate_id(true);

session_write_close();                    // 尽早释放会话锁（预期状态回到 PHP_SESSION_NONE）
```

| 函数/常量 | 说明 |
|-----------|------|
| `session_start()` | 启动/恢复会话；头部已发送时返回 false |
| `session_regenerate_id(bool $delete_old)` | 换发新 ID；`true` 同时删除旧会话数据——**登录成功后必调** |
| `session_status()` | `PHP_SESSION_NONE` / `PHP_SESSION_ACTIVE` / `PHP_SESSION_DISABLED` |
| `session_destroy()` | 销毁服务端会话存储；还需清空会话变量，并发送过期 Cookie，unset $_COOKIE 不会清除浏览器 Cookie |
| `session.use_strict_mode = 1` | 拒绝未初始化的会话 ID，防固定（本机默认 `0`，预期需显式开启） |

### 会话固定防护清单

1. `php.ini`：`session.use_strict_mode = 1`、`session.cookie_httponly = 1`、`session.cookie_secure = 1`、`session.cookie_samesite = Lax`。
2. 登录/权限变更时 `session_regenerate_id(true)`。
3. 会话 ID 不出现在 URL（`session.use_only_cookies = 1`）。
4. 登出时 `session_destroy()` + 清 Cookie。

## 📖 输入验证与上传处理

```php
// filter_var 验证（预期：合法返回原值，非法返回 false）
$email = filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL);

// 上传：PHP 自动把 multipart 文件放进 $_FILES（结构见超全局条目）
if (($_FILES['avatar']['error'] ?? UPLOAD_ERR_NO_FILE) === UPLOAD_ERR_OK) {
    $tmp  = $_FILES['avatar']['tmp_name'];
    if (is_uploaded_file($tmp)                       // 确认确为 HTTP 上传产物（CLI 预期返回 false）
        && finfo_file(finfo_open(FILEINFO_MIME_TYPE), $tmp) === 'image/jpeg') {
        move_uploaded_file($tmp, $dstPath);          // 检查返回值，并使用预先生成的服务端路径；不保证跨文件系统原子移动
    }
}
```

## ⚠️ 常见陷阱

- ❌ **输出后调用 `header()`/`setcookie()`/`session_start()`**：预期全部失效/返回 false，Cookie 丢失。
- ✅ 处理流程先逻辑后输出；模板渲染放最后；用 `ob_start()` 兜底缓冲。
- ❌ **`SameSite=None` 不带 `secure`**：浏览器直接拒收。
- ✅ `None` 必配 `secure => true`；拿不准就用 `Lax`。
- ❌ **把 `session_regenerate_id()` 留到"以后再做"**：会话固定攻击直接复用登录前 ID。
- ✅ 认证成功并建立登录态时轮换会话 ID，同时处理并发请求与旧会话失效。
- ❌ **信任 `$_FILES['x']['name']`/`['type']`**：均为客户端可控值。
- ✅ 服务端 `finfo` 探测 MIME、随机重命名、`move_uploaded_file` 限定目录。
- ❌ **用 `move_uploaded_file` 之外的方式处理 `tmp_name`**（copy/rename）：绕过 `is_uploaded_file` 安全检查。
- ✅ 标准组合：`is_uploaded_file()` 校验 + `move_uploaded_file()` 落位。
- ❌ **写完 `$_SESSION` 长事务不关会话**：会话文件加锁，同会话请求被串行阻塞。
- ✅ 读写完成后尽早 `session_write_close()`。

<!-- full-library-explanation -->
## 把一次请求拆成三个可观察阶段

前置是 HTTP 请求与响应、数组和会话状态。浏览器发送旧 Cookie，服务器验证会话并构造响应，浏览器收到 Set-Cookie 后决定是否保存；setcookie 返回 true 只说明 PHP 接受了设置操作，不能证明浏览器接受。HttpOnly 阻止脚本读取 Cookie，不阻止浏览器自动携带它，也不能代替 CSRF 防护。

session_write_close 后再修改当前进程的 $_SESSION，不会自动保存这次修改。锁的行为由会话存储实现决定；默认文件会话常把同一会话的并发请求串行化。再生成 ID 时立即删除旧数据可能与并发请求竞争，应按应用的会话轮换方案处理过渡与失效，不能只看单次调用返回值。

**练习**：在本地 HTTP 服务中发出 Cookie，利用浏览器网络面板检查 Set-Cookie，再检查下一次请求是否有 Cookie。分别测试 HTTPS、Path 不匹配和过期时间，解释“PHP 返回 true 但浏览器没带回来”的原因。退出登录后再次请求受保护接口，应得到未认证响应，不能只以页面跳转判断退出成功。

依据：[会话安全](https://www.php.net/manual/en/features.session.security.management.php)、[setcookie](https://www.php.net/manual/en/function.setcookie.php)。HTTP 行为应通过真实 Web SAPI 验证，CLI 不能验证浏览器收发。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

## 完整实验：隔离目录中的会话写入与关闭

下面是可独立运行的 CLI 程序。它只验证文件会话存储中的启动、写入和 `session_write_close()`；不验证 HTTP 响应头、浏览器 Cookie、上传来源或并发锁行为。临时目录由程序创建并在结束时清除。

<!-- terra-eighteenth-case: php-session-write-close -->
```php
<?php
declare(strict_types=1);

$directory = sys_get_temp_dir() . '/php-session-demo-' . bin2hex(random_bytes(4));
mkdir($directory, 0700);
ini_set('session.save_path', $directory);
session_id('eighteenth-demo');
session_start();
$_SESSION['uid'] = 42;
session_write_close();

$file = $directory . '/sess_eighteenth-demo';
echo session_status() === PHP_SESSION_NONE ? "closed\n" : "open\n";
echo str_contains((string) file_get_contents($file), 'uid|i:42;') ? "stored\n" : "missing\n";
unlink($file);
rmdir($directory);
```

预期输出为 `closed` 与 `stored`。该程序把会话存储限制在独立目录，避免读取或修改应用的默认会话目录；实际 Web 请求的 Cookie 发送与安全属性仍须在对应 SAPI 和浏览器中验证。

## 🔗 相关条目

- 📄 **[超全局变量](../language-concepts/15-superglobals.md)** — `$_COOKIE`/`$_FILES`/`$_SESSION` 数据入口
- 📄 **[文件与流 I/O](./05-file-stream-io.md)** — 上传文件的流式读取
- 📄 **[Laravel 速查](../framework-essentials/01-laravel-essentials.md)** — 框架层 Request/Response/Session 封装
- 🌐 **[php.net: 会话](https://www.php.net/manual/zh/book.session.php)** — 安全配置项官方清单

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
