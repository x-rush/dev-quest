# 文件与流 I/O

> **模块**: `07-php-mastery` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

PHP 文件操作分两层：`fopen` 系列的**流（stream）API** 与 `file_get_contents` 系列的**整读整写**便捷函数。流统一了文件、网络、内存的读写抽象（PHP 8.5 本机实测可用包装器：`https, ftps, compress.zlib, compress.bzip2, php, file, glob, data, http, ftp, phar, zip`）。

## 📖 fopen 模式表

| 模式 | 读 | 写 | 指针位置 | 文件不存在 | 文件已存在（实测） |
|------|----|----|----------|-----------|------------------|
| `r`  | ✔ | ✘ | 开头 | 失败 | 不动 |
| `r+` | ✔ | ✔ | 开头 | 失败 | **不截断**，覆盖写（实测 `line1` 被 `XX` 覆盖成 `XXne1`） |
| `w`  | ✘ | ✔ | 开头 | 创建 | **清空** |
| `w+` | ✔ | ✔ | 开头 | 创建 | 清空（实测配合 `rewind` 读回 `w+mode`） |
| `a`  | ✘ | ✔ | 末尾 | 创建 | 追加（实测 TAIL 接在原文后） |
| `a+` | ✔ | ✔ | 末尾（读需 `rewind`/`fseek`） | 创建 | 追加 |
| `x`  | ✘ | ✔ | 开头 | 创建（实测新建成功写入） | **失败返回 false**（实测已存在时 false） |
| `x+` | ✔ | ✔ | 开头 | 创建 | 失败返回 false |

另加 `b`（二进制，Windows 明确需要，跨平台代码一律带上）与 `t`（Windows 文本换行翻译，不建议）。

## 📖 核心函数

```php
// 逐行读
$fh = fopen('log.txt', 'rb');
while (($line = fgets($fh)) !== false) { /* trim($line) */ }
fclose($fh);

// CSV：实测引号字段 "c,x" 正确保持为单列，返回值始终是 string 数组
$rows = [];
$fh = fopen('data.csv', 'rb');
while (($row = fgetcsv($fh)) !== false) { $rows[] = $row; }
fclose($fh);

// 整读整写（flags：FILE_APPEND 追加、LOCK_EX 排它锁、FILE_USE_INCLUDE_PATH）
$all = file_get_contents('config.json');
file_put_contents('counter.txt', "1\n", FILE_APPEND | LOCK_EX);   // 实测两次调用得到两行

// 带 context 的整读（超时、代理等选项都在这里配）
$ctx = stream_context_create(['http' => ['timeout' => 5]]);
$html = file_get_contents('https://example.com', false, $ctx);
```

### 流包装器与临时流

```php
$body = file_get_contents('php://input');            // 原始请求体（JSON API 必备，只读一次）
$m = fopen('php://memory', 'w+');                    // 内存流（实测写入读回 in-mem）
fwrite($m, 'in-mem'); rewind($m); echo fread($m, 64);
fclose($m);

$t = tmpfile();                                      // 自动删除的临时文件流（实测可用）
fwrite($t, 'tmp'); rewind($t);

// 流到流的拷贝（大文件不经过 PHP 内存）
$src = fopen('big.bin', 'rb'); $dst = fopen('copy.bin', 'wb');
stream_copy_to_stream($src, $dst);                   // 实测返回拷贝字节数
fclose($src); fclose($dst);
```

### SplFileObject：面向对象文件迭代

```php
$sf = new SplFileObject('data.csv');
$sf->setFlags(SplFileObject::READ_CSV);
foreach ($sf as $i => $row) {
    // 逐行 CSV 迭代，无需 fopen/fgetcsv 手工循环
}
```

## 💡 大文件处理模式

```php
// 1. 行式流式处理（内存恒定）
foreach (new SplFileObject('access.log') as $line) { /* 过滤/聚合 */ }

// 2. 定长块读（二进制、协议解析）
$fh = fopen('big.bin', 'rb');
while (!feof($fh)) {
    $chunk = fread($fh, 64 * 1024);
    hash_update($ctx, $chunk);
}
fclose($fh);

// 3. 文件对拷用 stream_copy_to_stream，禁用 file_get_contents 全量中转
```

## ⚠️ 常见陷阱

- ❌ **`fopen($f, 'w')` 当"打开"用**：`w` 无条件清空已有文件（实测）。
- ✅ 读改写用 `r+`/`a`；确要重建才用 `w`。
- ❌ **`fgetcsv` 结果当数字用**：返回值全部是 string（实测 `["1","2","3"]`）。
- ✅ 显式 `(int)`/类型校验。
- ❌ **SplFileObject CSV 迭代不处理末尾空行**：实测末尾空行产出 `[null]` 行。
- ✅ 循环内 `if ($row === [null]) continue;`。
- ❌ **`while (!feof($f)) { $line = fgets($f); }`**：`fgets` 返回 `false` 后 `feof` 才为真，最后会混入一个 false 值。
- ✅ `while (($line = fgets($f)) !== false)`。
- ❌ **整读用户上传/超大文件**：`file_get_contents` 一次性载入内存。
- ✅ 行式/块式流处理或 `stream_copy_to_stream`。
- ❌ **写文件不加锁**：并发请求交错写坏内容。
- ✅ `flock($fh, LOCK_EX)` 或 `file_put_contents(..., LOCK_EX)`。

## 🔗 相关条目

- 📄 **[HTTP、会话与 Cookie](./06-http-session-cookie.md)** — 上传文件的接收与暂存
- 📄 **[JSON 编解码](./04-json.md)** — `php://input` 之后的解码
- 📄 **[SPL 与标准库核心扩展](./01-standard-library-spl.md)** — DirectoryIterator 与文件系统迭代器族
- 🌐 **[php.net: 流](https://www.php.net/manual/zh/book.stream.php)** — 包装器与 context 全表

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
