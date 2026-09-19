# 文件与流 I/O

> **模块**: `07-php-mastery` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

PHP 文件操作分两层：`fopen` 系列的**流（stream）API** 与 `file_get_contents` 系列的**整读整写**便捷函数。流统一了文件、网络、内存的读写抽象（可用包装器由安装与配置决定，使用 stream_get_wrappers() 查询，例如：`https, ftps, compress.zlib, compress.bzip2, php, file, glob, data, http, ftp, phar, zip`）。

## 📖 fopen 模式表

| 模式 | 读 | 写 | 指针位置 | 文件不存在 | 文件已存在（预期） |
|------|----|----|----------|-----------|------------------|
| `r`  | ✔ | ✘ | 开头 | 失败 | 不动 |
| `r+` | ✔ | ✔ | 开头 | 失败 | **不截断**，覆盖写（预期 `line1` 被 `XX` 覆盖成 `XXne1`） |
| `w`  | ✘ | ✔ | 开头 | 创建 | **清空** |
| `w+` | ✔ | ✔ | 开头 | 创建 | 清空（预期配合 `rewind` 读回 `w+mode`） |
| `a`  | ✘ | ✔ | 末尾 | 创建 | 追加（预期 TAIL 接在原文后） |
| `a+` | ✔ | ✔ | 末尾（读需 `rewind`/`fseek`） | 创建 | 追加 |
| `x`  | ✘ | ✔ | 开头 | 创建（预期新建成功写入） | **失败返回 false**（预期已存在时 false） |
| `x+` | ✔ | ✔ | 开头 | 创建 | 失败返回 false |

另加 `b`（二进制，Windows 明确需要，跨平台代码一律带上）与 `t`（Windows 文本换行翻译，不建议）。

## 📖 核心函数

```php
// 逐行读
$fh = fopen('log.txt', 'rb');
while (($line = fgets($fh)) !== false) { /* trim($line) */ }
fclose($fh);

// CSV：预期引号字段 "c,x" 正确保持为单列，普通字段为字符串，空行可返回 [null]
$rows = [];
$fh = fopen('data.csv', 'rb');
while (($row = fgetcsv($fh, escape: "")) !== false) { $rows[] = $row; }
fclose($fh);

// 整读整写（flags：FILE_APPEND 追加、LOCK_EX 排它锁、FILE_USE_INCLUDE_PATH）
$all = file_get_contents('config.json');
file_put_contents('counter.txt', "1\n", FILE_APPEND | LOCK_EX);   // 预期两次调用得到两行

// 带 context 的整读（超时、代理等选项都在这里配）
$ctx = stream_context_create(['http' => ['timeout' => 5]]);
$html = file_get_contents('https://example.com', false, $ctx);
```

### 流包装器与临时流

```php
$body = file_get_contents('php://input');            // 原始请求体；可重开读取的行为与请求类型有关，不应与框架一次性消费流混为一谈
$m = fopen('php://memory', 'w+');                    // 内存流（预期写入读回 in-mem）
fwrite($m, 'in-mem'); rewind($m); echo fread($m, 64);
fclose($m);

$t = tmpfile();                                      // 自动删除的临时文件流（预期可用）
fwrite($t, 'tmp'); rewind($t);

// 流到流的拷贝（避免在 PHP 变量中保存整个文件，内部仍可能缓冲）
$src = fopen('big.bin', 'rb'); $dst = fopen('copy.bin', 'wb');
stream_copy_to_stream($src, $dst);                   // 预期返回拷贝字节数
fclose($src); fclose($dst);
```

### SplFileObject：面向对象文件迭代

```php
$sf = new SplFileObject('data.csv');
$sf->setCsvControl(",", '"', "");
$sf->setFlags(SplFileObject::READ_CSV);
foreach ($sf as $i => $row) {
    // 逐行 CSV 迭代，无需 fopen/fgetcsv 手工循环
}
```

## 💡 大文件处理模式

```php
// 1. 行式处理（峰值受最大行长度及聚合状态影响）
foreach (new SplFileObject('access.log') as $line) { /* 过滤/聚合 */ }

// 2. 定长块读（二进制、协议解析）
$fh = fopen('big.bin', 'rb');
if ($fh === false) { throw new RuntimeException('cannot open input'); }
$hash = hash_init('sha256');
try {
while (!feof($fh)) {
    $chunk = fread($fh, 64 * 1024);
    if ($chunk === false) { throw new RuntimeException('read failed'); }
    hash_update($hash, $chunk);
}
} finally { fclose($fh); }
echo hash_final($hash);

// 3. 文件对拷用 stream_copy_to_stream，禁用 file_get_contents 全量中转
```

## ⚠️ 常见陷阱

- ❌ **`fopen($f, 'w')` 当"打开"用**：`w` 无条件清空已有文件（预期）。
- ✅ 原位读改写可用 r+；只追加用 a；还需考虑锁、截断旧尾部和失败恢复；确要重建才用 `w`。
- ❌ **`fgetcsv` 结果当数字用**：普通字段通常为 string（如 `["1","2","3"]`），空行是 [null]。
- ✅ 显式 `(int)`/类型校验。
- ❌ **SplFileObject CSV 迭代不处理末尾空行**：预期末尾空行产出 `[null]` 行。
- ✅ 循环内 `if ($row === [null]) continue;`。
- ❌ **`while (!feof($f)) { $line = fgets($f); }`**：`fgets` 返回 `false` 后 `feof` 才为真，最后会混入一个 false 值。
- ✅ `while (($line = fgets($f)) !== false)`。
- ❌ **整读用户上传/超大文件**：`file_get_contents` 一次性载入内存。
- ✅ 行式/块式流处理或 `stream_copy_to_stream`。
- ❌ **写文件不加锁**：并发请求交错写坏内容。
- ✅ `flock($fh, LOCK_EX)` 或 `file_put_contents(..., LOCK_EX)`。

## 正文提取验证：字节完整写入与锁内读改写

下面是本页唯一用于自动运行验证的完整脚本。它在系统临时目录创建自己的文件，先用循环处理 `fwrite` 的部分写入契约，再在同一把排他锁内完成读取、递增和截断回写。`LOCK_EX` 只协调遵守相同协议的进程；此例验证的是单进程中锁覆盖整个读改写临界区这一必要结构，不声称替代多进程压力测试。

<!-- body-runtime-case: {"id":"php-file-stream-full-write-and-locked-update","stdout":"bytes=6\ncontent=abc123\ncounter=42\n"} -->
```php
<?php

declare(strict_types=1);

function writeAll($stream, string $bytes): void
{
    $offset = 0;
    while ($offset < strlen($bytes)) {
        $written = fwrite($stream, substr($bytes, $offset));
        if ($written === false || $written === 0) {
            throw new RuntimeException('write failed');
        }
        $offset += $written;
    }
}

$path = tempnam(sys_get_temp_dir(), 'php-io-');
if ($path === false) {
    throw new RuntimeException('cannot create temp file');
}

try {
    $stream = fopen($path, 'c+b');
    if ($stream === false) {
        throw new RuntimeException('cannot open temp file');
    }
    try {
        writeAll($stream, 'abc123');
        rewind($stream);
        $content = stream_get_contents($stream);
        if ($content === false) {
            throw new RuntimeException('cannot read temp file');
        }
        echo 'bytes=', strlen($content), PHP_EOL;
        echo 'content=', $content, PHP_EOL;

        if (!flock($stream, LOCK_EX)) {
            throw new RuntimeException('cannot lock temp file');
        }
        try {
            rewind($stream);
            $current = stream_get_contents($stream);
            if ($current === false || !ctype_digit($current)) {
                $current = '41';
            }
            rewind($stream);
            if (!ftruncate($stream, 0)) {
                throw new RuntimeException('cannot truncate temp file');
            }
            writeAll($stream, (string) ((int) $current + 1));
            fflush($stream);
        } finally {
            flock($stream, LOCK_UN);
        }

        rewind($stream);
        echo 'counter=', stream_get_contents($stream), PHP_EOL;
    } finally {
        fclose($stream);
    }
} finally {
    unlink($path);
}
```

预期输出证明首段字节被完整读回，并证明覆盖写先截断了旧内容；若省略 `ftruncate`，较长旧内容的尾部会残留。`tempnam` 仅使示例可重复运行，生产代码仍须为目标目录、权限和替换策略制定自己的约束。

<!-- full-library-explanation -->
## 文件处理要同时考虑资源和并发

前置是异常与循环。打开流可能返回 false，并伴随警告；读取失败和到达 EOF 也要区分。取得资源后用 try/finally 关闭，异常路径同样需要释放。fwrite 可能只写入部分字节，处理协议或大块数据时应根据返回长度继续写，不能把一次调用当成完整写入保证。

锁只约束遵守同一锁协议的访问者。计数器的“读取→加一→写回”需要把整个过程放在锁内，仅给最后写入加 LOCK_EX 仍会丢更新。发布完整配置可写入同目录临时文件、检查写入成功，再替换目标；原子替换和断电持久性不是同一个保证，且需确认目标平台文件系统行为。

**练习**：用两个进程同时递增练习文件，比较只锁写入与锁整个读改写的结果。再用含逗号、引号、空行与多行字段的 CSV 验证解析，明确是否跳过 [null]；每行仍要校验列数和数值格式。流式读取只有在单条记录和下游缓冲有界时才能控制峰值内存。

依据：[fgetcsv](https://www.php.net/fgetcsv)、[文件锁](https://www.php.net/manual/en/function.flock.php)。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

## 🔗 相关条目

- 📄 **[HTTP、会话与 Cookie](./06-http-session-cookie.md)** — 上传文件的接收与暂存
- 📄 **[JSON 编解码](./04-json.md)** — `php://input` 之后的解码
- 📄 **[SPL 与标准库核心扩展](./01-standard-library-spl.md)** — DirectoryIterator 与文件系统迭代器族
- 🌐 **[php.net: 流](https://www.php.net/manual/zh/book.stream.php)** — 包装器与 context 全表

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
