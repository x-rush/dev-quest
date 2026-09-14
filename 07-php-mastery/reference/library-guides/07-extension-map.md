# 内置扩展地图

> **模块**: `07-php-mastery` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

PHP 发行包自带的扩展速查地图：按用途分组，每个扩展一行"一句话职责 + 官方文档链接"。本机（PHP 8.5.10，asdf 安装）`php -m` 全量核对；个别扩展（如 gd/intl/pcntl）在发行包中默认关闭，编译/ini 启用后可用。

## 📖 字符串与文本

| 扩展 | 一句话职责 |
|------|-----------|
| [pcre](https://www.php.net/manual/zh/book.pcre.php) | Perl 兼容正则（preg_* 函数族） |
| [mbstring](https://www.php.net/manual/zh/book.mbstring.php) | 多字节字符串（UTF-8 长度/截断/编码转换） |
| [iconv](https://www.php.net/manual/zh/book.iconv.php) | 字符集间转换 |
| [ctype](https://www.php.net/manual/zh/book.ctype.php) | 字符类型快速判定（is 数字/字母/空白…） |
| [gettext](https://www.php.net/manual/zh/book.gettext.php) | 传统 i18n 翻译机制 |

## 📖 日期与数字

| 扩展 | 一句话职责 |
|------|-----------|
| [date](https://www.php.net/manual/zh/book.datetime.php) | DateTime/DateInterval/时区，日期时间核心 |
| [calendar](https://www.php.net/manual/zh/book.calendar.php) | 历法换算（儒略日等历法换算） |
| [BCMath](https://www.php.net/manual/zh/book.bc.php) | 任意精度十进制运算（金额计算基础） |
| [gmp](https://www.php.net/manual/zh/book.gmp.php) | 任意精度整数运算（密码学/大数） |

## 📖 数据格式与编码

| 扩展 | 一句话职责 |
|------|-----------|
| [json](https://www.php.net/manual/zh/book.json.php) | JSON 编解码（8.0 起内置不可禁用，详见 JSON 条目） |
| [dom](https://www.php.net/manual/zh/book.dom.php) / [SimpleXML](https://www.php.net/manual/zh/book.simplexml.php) / [xmlreader](https://www.php.net/manual/zh/book.xmlreader.php) / [xmlwriter](https://www.php.net/manual/zh/book.xmlwriter.php) / [xml](https://www.php.net/manual/zh/book.xml.php) / [libxml](https://www.php.net/manual/zh/book.libxml.php) | XML 全家桶：DOM 树 / 简易遍历 / 流式读 / 流式写 / SAX / 底层库 |
| [lexbor](https://www.php.net/manual/zh/book.dom.php) | HTML5 解析器库（Lexbor，随核心捆绑，本机 2.7.0） |
| [intl](https://www.php.net/manual/zh/book.intl.php) | ICU 国际化（本地化格式、翻译、音译） |

## 📖 图像与文件类型

| 扩展 | 一句话职责 |
|------|-----------|
| [gd](https://www.php.net/manual/zh/book.image.php) | 图像生成与处理（缩放、水印、验证码） |
| [exif](https://www.php.net/manual/zh/book.exif.php) | 读取图像 EXIF 元数据 |
| [fileinfo](https://www.php.net/manual/zh/book.fileinfo.php) | 内容探测 MIME/编码（finfo_*，上传校验必备） |

## 📖 密码、哈希与随机

| 扩展 | 一句话职责 |
|------|-----------|
| [hash](https://www.php.net/manual/zh/book.hash.php) | 哈希摘要与 HMAC（password_hash 底层之一） |
| [password hash](https://www.php.net/manual/zh/book.password.php) | 密码散列 API（password_hash/password_verify，标准库函数） |
| [openssl](https://www.php.net/manual/zh/book.openssl.php) | TLS、证书、非对称加解密 |
| [sodium](https://www.php.net/manual/zh/book.sodium.php) | 现代密码学库（libsodium，7.2 起随核心） |
| [random](https://www.php.net/manual/zh/book.random.php) | 8.2+ 独立随机数扩展（Random\Randomizer、加密安全引擎） |

## 📖 压缩与归档

| 扩展 | 一句话职责 |
|------|-----------|
| [zlib](https://www.php.net/manual/zh/book.zlib.php) | gzip/deflate 压缩与 `compress.zlib://` 流 |
| [bz2](https://www.php.net/manual/zh/book.bzip2.php) | bzip2 压缩 |
| [zip](https://www.php.net/manual/zh/book.zip.php) | Zip 归档读写（ZipArchive） |
| [Phar](https://www.php.net/manual/zh/book.phar.php) | PHP 归档包（单文件应用/依赖打包） |

## 📖 网络与通信

| 扩展 | 一句话职责 |
|------|-----------|
| [curl](https://www.php.net/manual/zh/book.curl.php) | HTTP/HTTPS 等协议客户端（见下方最小用法） |
| [sockets](https://www.php.net/manual/zh/book.sockets.php) | 原生 BSD socket 编程 |
| [ftp](https://www.php.net/manual/zh/book.ftp.php) | FTP 客户端 |

### curl 最小用法（GET / POST）

```php
// GET
$ch = curl_init('https://httpbin.org/get');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,                       // 返回字符串而非直接输出
    CURLOPT_TIMEOUT        => 5,
]);
$body = curl_exec($ch);                                   // 失败返回 false
curl_close($ch);

// POST JSON
$ch = curl_init('https://httpbin.org/post');
curl_setopt_array($ch, [
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => json_encode(['name' => 'php']),
    CURLOPT_HTTPHEADER     => ['Content-Type: application/json'],
    CURLOPT_RETURNTRANSFER => true,
]);
$body = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);        // HTTP 状态码
curl_close($ch);
```

## 📖 数据库

| 扩展 | 一句话职责 |
|------|-----------|
| [PDO](https://www.php.net/manual/zh/book.pdo.php) + [pdo_mysql](https://www.php.net/manual/zh/ref.pdo-mysql.php) / [pdo_pgsql](https://www.php.net/manual/zh/ref.pdo-pgsql.php) / [pdo_sqlite](https://www.php.net/manual/zh/ref.pdo-sqlite.php) | 统一数据库抽象层与各驱动（详见 PDO 条目） |
| [mysqli](https://www.php.net/manual/zh/book.mysqli.php) | MySQL 专用改进版扩展（同步/异步 API） |
| [mysqlnd](https://www.php.net/manual/zh/book.mysqlinfo.php) | MySQL 原生驱动库（mysqli/PDO MySQL 共用底层） |
| [sqlite3](https://www.php.net/manual/zh/book.sqlite3.php) | SQLite 的面向对象直连接口 |
| [dba](https://www.php.net/manual/zh/book.dba.php) | 键值型 dbm 文件抽象 |

## 📖 进程、系统与运行时

| 扩展 | 一句话职责 |
|------|-----------|
| [pcntl](https://www.php.net/manual/zh/book.pcntl.php) | 进程控制（fork、信号，CLI 专用） |
| [posix](https://www.php.net/manual/zh/book.posix.php) | POSIX 系统接口（UID/PID/终端） |
| [shmop](https://www.php.net/manual/zh/book.shmop.php) / [sysvmsg](https://www.php.net/manual/zh/book.sem.php) / [sysvsem](https://www.php.net/manual/zh/book.sem.php) / [sysvshm](https://www.php.net/manual/zh/book.sem.php) | System V 共享内存/消息队列/信号量族 |
| [readline](https://www.php.net/manual/zh/book.readline.php) | 交互式命令行输入（REPL 工具基础） |
| [FFI](https://www.php.net/manual/zh/book.ffi.php) | 调用 C 库与数据结构（7.4+ 实验，生产慎用） |
| [tokenizer](https://www.php.net/manual/zh/book.tokenizer.php) | PHP 源码词法分析（静态分析工具基础） |
| [filter](https://www.php.net/manual/zh/book.filter.php) | 输入验证与净化（filter_var/filter_input） |
| [uri](https://www.php.net/manual/zh/book.uri.php) | WHATWG URL 标准解析（8.5 新增，`Uri\WhatWg\Url` 类） |
| [Reflection](https://www.php.net/manual/zh/book.reflection.php) | 类/函数/属性的运行时反射 |
| [SPL](https://www.php.net/manual/zh/book.spl.php) | 数据结构、迭代器、SplAutoload（详见 SPL 条目） |
| [Zend OPcache](https://www.php.net/manual/zh/book.opcache.php) | 字节码缓存 + JIT（生产环境必开） |

## ⚠️ 常见陷阱

- ❌ **假设所有扩展默认启用**：gd、intl、pcntl、sodium 等在发行包中常需显式启用。
- ✅ 部署前 `php -m` 核对（本条目各扩展均经本机核对存在）。
- ❌ **用 BCMath 处理浮点科学计算**：BCMath 是十进制字符串运算，不做超越函数。
- ✅ 金额用 BCMath/整数分，科学计算用高精度专用库。
- ❌ **密码用 `hash('md5', ...)`**：速度过快，不利抗暴力破解。
- ✅ `password_hash()` / `password_verify()`（bcrypt/argon2）。
- ❌ **生产环境关闭 OPcache**：每次请求重新编译全部文件，性能损失数倍。
- ✅ `opcache.enable=1` 并合理设置内存与校验策略（FPM 下 `validate_timestamps` 按发布节奏权衡）。

## 🔗 相关条目

- 📄 **[PDO 数据库访问层](./03-pdo.md)** — 数据库族扩展详解
- 📄 **[JSON 编解码](./04-json.md)** — json 扩展详解
- 📄 **[SPL 与标准库核心扩展](./01-standard-library-spl.md)** — SPL 与 mbstring/PCRE 详解
- 🌐 **[php.net: 扩展列表](https://www.php.net/manual/zh/extensions.php)** — 官方全部扩展索引

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
