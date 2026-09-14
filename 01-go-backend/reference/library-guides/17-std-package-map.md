# Go 标准库全包地图

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

Go 1.25 标准库的**按用途分组全包地图**：每包一行"一句话职责 + 官方文档链接"。当你知道要做什么但不知道用哪个包时，从这里开始检索；已在本目录单独成篇的包，链接直接指向本目录条目。

**阅读约定**：包名 + 一句话职责；`📖` 标记 = 本字典有专篇详解。链接统一指向 `pkg.go.dev`。

## 📖 分组地图

### 入口与进程管理

- **[flag](https://pkg.go.dev/flag)** 📖 [本字典 16 篇](./16-flag.md) — 命令行参数的声明式解析
- **[os](https://pkg.go.dev/os)** 📖 [本字典 11 篇](./11-os.md) — 进程环境、文件系统、信号的系统调用大门
- **[os/exec](https://pkg.go.dev/os/exec)** — 执行外部命令并接管其 stdio
- **[os/signal](https://pkg.go.dev/os/signal)** — 把 Unix 信号转成 channel 通知
- **[os/user](https://pkg.go.dev/os/user)** — 查询当前/指定系统用户与组
- **[plugin](https://pkg.go.dev/plugin)** — 加载 Go 编译的共享库插件（平台支持有限，慎用）
- **[runtime](https://pkg.go.dev/runtime)** — 与 Go 运行时交互（GOMAXPROCS、GC 钩子、栈信息）
- **[runtime/debug](https://pkg.go.dev/runtime/debug)** — 运行时调试开关与 panic 堆栈读取
- **[syscall](https://pkg.go.dev/syscall)** — 底层系统调用原语（优先用 os 系列包装）
- **[unsafe](https://pkg.go.dev/unsafe)** — 绕过类型系统的底层操作（标准库中唯一不保证兼容的包）

### 语言与基础数据结构

- **[builtin](https://pkg.go.dev/builtin)** — 预声明类型/常量/函数的文档视图（无需 import）
- **[cmp](https://pkg.go.dev/cmp)** — `Compare/Less` 泛型比较器与 NaN 处理
- **[errors](https://pkg.go.dev/errors)** 📖 [本字典 9 篇](./09-errors.md) — 错误包装、判断与合并
- **[iter](https://pkg.go.dev/iter)** — 迭代器协议 `Seq/Seq2`（1.23+）
- **[maps](https://pkg.go.dev/maps)** 📖 [本字典 13 篇](./13-slices-maps.md) — map 的泛型工具（克隆/键值迭代/删选）
- **[reflect](https://pkg.go.dev/reflect)** — 运行时反射（序列化框架/依赖注入的底层）
- **[slices](https://pkg.go.dev/slices)** 📖 [本字典 13 篇](./13-slices-maps.md) — 切片的泛型工具（排序/查找/克隆/增删）
- **[sort](https://pkg.go.dev/sort)** — 预泛型时代的排序（新代码优先 slices）
- **[strconv](https://pkg.go.dev/strconv)** 📖 [本字典 14 篇](./14-strconv.md) — 字符串与基本类型的高性能互转
- **[strings](https://pkg.go.dev/strings)** — 字符串操作全家桶（查找/替换/分割/Builder）
- **[unique](https://pkg.go.dev/unique)** — 值驻留（interning），句柄化去重（1.23+）
- **[unicode](https://pkg.go.dev/unicode)** / **[unicode/utf8](https://pkg.go.dev/unicode/utf8)** — Unicode 分类与 UTF-8 编解码
- **[weak](https://pkg.go.dev/weak)** — 弱引用指针，配合运行时缓存清理（1.24+）

### IO 与流处理

- **[bufio](https://pkg.go.dev/bufio)** 📖 [本字典 10 篇](./10-io-bufio.md) — 读写缓冲层与 Scanner 分词
- **[bytes](https://pkg.go.dev/bytes)** — []byte 的 Reader/Buffer/操作函数（io 的内存流实现）
- **[io](https://pkg.go.dev/io)** 📖 [本字典 10 篇](./10-io-bufio.md) — Reader/Writer 接口宇宙与工具函数
- **[io/fs](https://pkg.go.dev/io/fs)** — 文件系统的抽象接口（embed/zip/内存 FS 统一模型）
- **[path](https://pkg.go.dev/path)** — 正斜杠路径操作（URL 内部路径）
- **[path/filepath](https://pkg.go.dev/path/filepath)** — 平台相关文件路径（Join/Walk/Glob）
- **[text/scanner](https://pkg.go.dev/text/scanner)** — Go 风格词法扫描器
- **[text/tabwriter](https://pkg.go.dev/text/tabwriter)** — 制表符对齐表格输出
- **[fmt](https://pkg.go.dev/fmt)** — 格式化 I/O（%v/%w/动词全家桶）
- **[embed](https://pkg.go.dev/embed)** — 编译期把静态文件嵌入二进制

### 数据格式与编码

- **[encoding/json](https://pkg.go.dev/encoding/json)** 📖 [本字典 4 篇](./04-encoding-json.md) — JSON 编解码与 struct tag
- **[encoding/csv](https://pkg.go.dev/encoding/csv)** — CSV 读写（Reader/Writer 流式）
- **[encoding/xml](https://pkg.go.dev/encoding/xml)** — XML 编解码
- **[encoding/gob](https://pkg.go.dev/encoding/gob)** — Go 自有的二进制序列化（RPC/本地缓存）
- **[encoding/base64](https://pkg.go.dev/encoding/base64)** / **[encoding/base32](https://pkg.go.dev/encoding/base32)** — Base 编码
- **[encoding/binary](https://pkg.go.dev/encoding/binary)** — 定长二进制与字节序转换
- **[encoding/hex](https://pkg.go.dev/encoding/hex)** — 十六进制编解码
- **[encoding/pem](https://pkg.go.dev/encoding/pem)** — PEM 证书/密钥文本块
- **[encoding/asn1](https://pkg.go.dev/encoding/asn1)** — ASN.1 DER（X.509 内部用）
- **[text/template](https://pkg.go.dev/text/template)** / **[html/template](https://pkg.go.dev/html/template)** — 模板引擎（html 版自动转义）
- **[mime](https://pkg.go.dev/mime)** / **[mime/multipart](https://pkg.go.dev/mime/multipart)** / **[mime/quotedprintable](https://pkg.go.dev/mime/quotedprintable)** — MIME 类型表与邮件/表单格式
- **[net/url](https://pkg.go.dev/net/url)** — URL 解析、构造与 query 编码
- **[net/mail](https://pkg.go.dev/net/mail)** — 邮件地址解析与消息头
- **[archive/tar](https://pkg.go.dev/archive/tar)** / **[archive/zip](https://pkg.go.dev/archive/zip)** — 归档读写
- **[compress/gzip](https://pkg.go.dev/compress/gzip)** / **[compress/flate](https://pkg.go.dev/compress/flate)** / **[compress/zlib](https://pkg.go.dev/compress/zlib)** / **[compress/bzip2](https://pkg.go.dev/compress/bzip2)**（只读）/ **[compress/lzw](https://pkg.go.dev/compress/lzw)** — 压缩算法

### 时间与并发

- **[time](https://pkg.go.dev/time)** 📖 [本字典 8 篇](./08-time.md) — 时间点、时长、定时器与时区
- **[time/tzdata](https://pkg.go.dev/time/tzdata)** — 内嵌 IANA 时区库（交叉编译兜底）
- **[context](https://pkg.go.dev/context)** 📖 [本字典 5 篇](./05-context.md) — 跨 API 的取消/截止/请求级数据
- **[sync](https://pkg.go.dev/sync)** 📖 [本字典 6 篇](./06-sync.md) — Mutex/WaitGroup/Once/Cond 同步原语
- **[sync/atomic](https://pkg.go.dev/sync/atomic)** — 原子操作（Add/Load/Store/CAS/Value）

### 数学与随机

- **[math](https://pkg.go.dev/math)** — 浮点数学函数与特殊值（NaN/Inf）
- **[math/bits](https://pkg.go.dev/math/bits)** — 位操作（计数/反转/前导零）
- **[math/cmplx](https://pkg.go.dev/math/cmplx)** — 复数函数
- **[math/rand](https://pkg.go.dev/math/rand)** — 随机数（旧 API，自动播种）
- **[math/rand/v2](https://pkg.go.dev/math/rand/v2)** — 随机数新 API（更快的算法与更清晰的接口）

### 数据库

- **[database/sql](https://pkg.go.dev/database/sql)** 📖 [本字典 7 篇](./07-database-sql.md) — SQL 连接池与统一查询接口
- **[database/sql/driver](https://pkg.go.dev/database/sql/driver)** — 驱动作者实现的接口契约

### 网络与 RPC

- **[net](https://pkg.go.dev/net)** — TCP/UDP/Unix socket 与 DNS
- **[net/http](https://pkg.go.dev/net/http)** 📖 [本字典 3 篇](./03-net-http.md) — HTTP 服务端/客户端/路由
- **[net/http/httptest](https://pkg.go.dev/net/http/httptest)** — HTTP 测试服务器与响应记录器
- **[net/http/httputil](https://pkg.go.dev/net/http/httputil)** — 反向代理（ReverseProxy）与转储工具
- **[net/http/pprof](https://pkg.go.dev/net/http/pprof)** — 以 HTTP 端点暴露性能剖析
- **[net/netip](https://pkg.go.dev/net/netip)** — 高性能 IP 地址/前缀类型（替代 net.IP）
- **[net/rpc](https://pkg.go.dev/net/rpc)** — Go 原生 RPC（配合 gob）
- **[net/smtp](https://pkg.go.dev/net/smtp)** — SMTP 客户端（发邮件）
- **[net/textproto](https://pkg.go.dev/net/textproto)** — 文本协议（HTTP/SMTP 共用的行式读写）

### 哈希与加密

- **[crypto](https://pkg.go.dev/crypto)** — 加密原语的公共类型与常量
- **[crypto/aes](https://pkg.go.dev/crypto/aes)** / **[crypto/cipher](https://pkg.go.dev/crypto/cipher)** — AES 与分组密码模式（GCM 等）
- **[crypto/ecdh](https://pkg.go.dev/crypto/ecdh)** — ECDH 密钥交换
- **[crypto/ecdsa](https://pkg.go.dev/crypto/ecdsa)** / **[crypto/ed25519](https://pkg.go.dev/crypto/ed25519)** / **[crypto/rsa](https://pkg.go.dev/crypto/rsa)** — 签名算法
- **[crypto/hmac](https://pkg.go.dev/crypto/hmac)** — HMAC 消息认证
- **[crypto/md5](https://pkg.go.dev/crypto/md5)** / **[crypto/sha1](https://pkg.go.dev/crypto/sha1)** / **[crypto/sha256](https://pkg.go.dev/crypto/sha256)** / **[crypto/sha512](https://pkg.go.dev/crypto/sha512)** / **[crypto/sha3](https://pkg.go.dev/crypto/sha3)** — 摘要算法（md5/sha1 仅限兼容场景）
- **[crypto/pbkdf2](https://pkg.go.dev/crypto/pbkdf2)** — 口令基密钥派生（1.24+）
- **[crypto/mlkem](https://pkg.go.dev/crypto/mlkem)** — 后量子 ML-KEM 密钥封装（1.24+）
- **[crypto/rand](https://pkg.go.dev/crypto/rand)** — 密码学安全随机数（token/密钥生成必用）
- **[crypto/subtle](https://pkg.go.dev/crypto/subtle)** — 常数时间比较（防时序攻击）
- **[crypto/tls](https://pkg.go.dev/crypto/tls)** — TLS 协议实现
- **[crypto/x509](https://pkg.go.dev/crypto/x509)** — X.509 证书解析/校验/生成
- **[hash](https://pkg.go.dev/hash)** — 哈希接口；**[hash/adler32](https://pkg.go.dev/hash/adler32)** / **[hash/crc32](https://pkg.go.dev/hash/crc32)** / **[hash/crc64](https://pkg.go.dev/hash/crc64)** / **[hash/fnv](https://pkg.go.dev/hash/fnv)** / **[hash/maphash](https://pkg.go.dev/hash/maphash)** — 校验和与非加密哈希

### 日志与可观测

- **[log](https://pkg.go.dev/log)** — 经典文本日志（slog 兼容桥可接管其输出）
- **[log/slog](https://pkg.go.dev/log/slog)** 📖 [本字典 15 篇](./15-log-slog.md) — 结构化日志
- **[expvar](https://pkg.go.dev/expvar)** — 进程内公共变量的 JSON 暴露端点
- **[runtime/metrics](https://pkg.go.dev/runtime/metrics)** — 运行时指标读取（GC/内存/调度）
- **[runtime/pprof](https://pkg.go.dev/runtime/pprof)** — CPU/内存/阻塞剖析采样
- **[runtime/trace](https://pkg.go.dev/runtime/trace)** — 执行轨迹跟踪（go tool trace 可视化）

### 测试

- **[testing](https://pkg.go.dev/testing)** 📖 [本字典 12 篇](./12-testing.md) — 单元/基准/模糊测试框架
- **[testing/fstest](https://pkg.go.dev/testing/fstest)** — io/fs 实现的符合性测试与内存 FS
- **[testing/iotest](https://pkg.go.dev/testing/iotest)** — 故障注入 Reader（ErrReader/超时）
- **[testing/slogtest](https://pkg.go.dev/testing/slogtest)** — 验证自定义 slog Handler 符合规范
- **[testing/synctest](https://pkg.go.dev/testing/synctest)** — 并发代码的虚拟时间气泡测试（1.25 稳定）

### 图像与容器结构

- **[image](https://pkg.go.dev/image)** / **[image/color](https://pkg.go.dev/image/color)** / **[image/draw](https://pkg.go.dev/image/draw)** / **[image/gif](https://pkg.go.dev/image/gif)** / **[image/jpeg](https://pkg.go.dev/image/jpeg)** / **[image/png](https://pkg.go.dev/image/png)** — 图像类型与编解码
- **[container/heap](https://pkg.go.dev/container/heap)** / **[container/list](https://pkg.go.dev/container/list)** / **[container/ring](https://pkg.go.dev/container/ring)** — 堆/双向链表/环形链表
- **[index/suffixarray](https://pkg.go.dev/index/suffixarray)** — 后缀数组全文搜索

### Go 代码工具（元编程）

- **[go/ast](https://pkg.go.dev/go/ast)** / **[go/token](https://pkg.go.dev/go/token)** — 语法树表示
- **[go/parser](https://pkg.go.dev/go/parser)** / **[go/printer](https://pkg.go.dev/go/printer)** / **[go/format](https://pkg.go.dev/go/format)** — 解析与打印/格式化 Go 源码
- **[go/types](https://pkg.go.dev/go/types)** — 类型检查器
- **[go/doc](https://pkg.go.dev/go/doc)** / **[go/build](https://pkg.go.dev/go/build)** / **[go/constant](https://pkg.go.dev/go/constant)** — 文档提取/构建约束/常量算术

## 💡 选型速判

- "把 X 变成 Y" → 先查 strconv/encoding/*，再考虑 fmt
- "读文件/网络流" → io + bufio 组合，永远面向接口
- "等一组 goroutine / 保护一个 map" → sync；"传数据给另一 goroutine" → channel
- "超时/取消" → context 一条路走到底
- "CLI 解析" → flag（复杂子命令再评估第三方 cobra）
- "日志" → log/slog，别再引入第三方日志库

## ⚠️ 常见陷阱

- ❌ **错误做法**：用 `io/ioutil`、`sort`、`math/rand` 老包写新代码。
- ✅ **正确做法**：ioutil 已废弃（io/os 有等价物）、排序用 slices、随机用 math/rand/v2；遇到旧包先查是否已有现代替代。
- ❌ **错误做法**：引入第三方库解决标准库已覆盖的需求（uuid、结构化日志、JSON）。
- ✅ **正确做法**：先查本地图——crypto/rand 生成 token、slog 记日志、encoding/json 处理 JSON；标准库没有再引第三方（如 pgx、zap）。
- ❌ **错误做法**：把 crypto/md5/crypto/rand 等加密包当普通哈希用。
- ✅ **正确做法**：校验和用 hash/crc32 系；任何涉及安全的摘要/随机只用 crypto/* 且按文档组合。

## 🔗 相关条目

- 📄 **[net/http](./03-net-http.md)** / **[encoding/json](./04-encoding-json.md)** / **[context](./05-context.md)** / **[sync](./06-sync.md)** / **[database/sql](./07-database-sql.md)** - 本目录各专篇
- 📄 **[time](./08-time.md)** / **[errors](./09-errors.md)** / **[io/bufio](./10-io-bufio.md)** / **[os](./11-os.md)** / **[testing](./12-testing.md)** - 本目录各专篇
- 📄 **[slices/maps](./13-slices-maps.md)** / **[strconv](./14-strconv.md)** / **[log/slog](./15-log-slog.md)** / **[flag](./16-flag.md)** - 本目录各专篇
- 🌐 **[Go 标准库总目录](https://pkg.go.dev/std)** - 官方全包列表（权威来源）

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
