# PHP 数组/生成器与 Java Stream/IO 的限定验证

日期：2026-09-19。结果：12 / 12 个直接抽取的完整正文程序符合声明输出。原始命令、版本、退出码、stdout、stderr、文档摘要与案例摘要见 [php-java-pipelines.json](php-java-pipelines.json)。

| 文档 | 命名案例 | 运行证据覆盖 |
|---|---|---|
| [PHP 数组操作](../../../../07-php-mastery/reference/language-concepts/05-arrays-patterns.md) | `php-array-paid-pipeline` | 按整数分过滤/映射/归约已支付金额 |
| 同上 | `php-array-key-contracts` | 过滤保留键、列表 JSON、null 精确过滤、map 单/多数组键、并集与 merge、非严格差集、重复 ID 拒绝 |
| 同上 | `php-array-object-and-sort` | 回调修改共享对象、多级排序、asort 保留键 |
| [PHP 生成器](../../../../07-php-mastery/reference/language-concepts/06-generators-iterators.md) | `php-generator-resource-lifetime` | 创建惰性、break 后保留状态、最后引用释放触发 finally、未启动函数体不清理 |
| 同上 | `php-generator-delegation-return` | yield from 重复键、保留/丢弃键模式、正常返回、未完成与异常结束时 getReturn 失败 |
| 同上 | `php-generator-take-demand` | 取零项不启动上游、取三项恰好推进三次 |
| [Java Stream 与 Optional](../../../../08-java-revisited/reference/language-concepts/03-streams-optional.md) | `java-stream-collection-contracts` | toList 不可修改但元素可变、null 允许/拒绝、显式可修改收集、重复键拒绝及合并 |
| 同上 | `java-optional-fallbacks` | 默认值求值时机、map 与 flatMap 的 null 差异、空值异常、Optional.stream |
| 同上 | `java-stream-lifecycle` | 空流量词、并行求和、已消费流复用失败、Files.lines 关闭回调 |
| [Java IO](../../../../08-java-revisited/reference/library-guides/04-java-io.md) | `java-io-text-roundtrip` | 字节读取、UTF-8 文本、末尾无换行、EOF 与临时文件清理 |
| 同上 | `java-io-short-read-decoder` | 每次最多两个字节的短读取、按 n 写入、损坏 UTF-8 明确拒绝 |
| 同上 | `java-io-writer-failure` | PrintWriter 隐藏底层 IOException 后 checkError 可见、关闭传递 |

环境为现有 `dev-quest-validation:local` 镜像的 PHP 8.3.6 和 Temurin JDK 21.0.12。Java 用 `javac --release 21 -encoding UTF-8` 编译，再以 `java Main` 运行；PHP 启用全部错误报告。两个版本号以 JSON 内实际命令输出为准，不能把可变镜像标签当作固定工具链证明。

[本批运行器](../verify_php_java_pipelines.py) 复用[严格正文运行器](../verify_php_java_foundations.py)，要求四篇分别有 3 个标记程序，并校验案例 ID 唯一。不补 import、不添加类/函数、不替换数据；每例放在独立临时目录。只有退出码为 0、stderr 为空、stdout 精确匹配才计入通过；异常行为在正文程序中显式捕获并输出。

在仓库根目录复现（需 Python、PHP 与 JDK 21）：

```sh
python3 shared-resources/tools/document-quality/verify_php_java_pipelines.py --report /tmp/php-java-pipelines.json
```

本次 PowerShell 隔离命令，输出目录为仓库外已有的 `verification-lab`：

```powershell
docker run --rm --network none --read-only --tmpfs /tmp:rw,nosuid,size=128m --cap-drop ALL --pids-limit 128 --memory 512m --cpus 2 -e PYTHONDONTWRITEBYTECODE=1 -v "${PWD}:/source:ro" -v "${PWD}/../verification-lab:/out:rw" dev-quest-validation:local python3 /source/shared-resources/tools/document-quality/verify_php_java_pipelines.py --report /out/php-java-pipelines.json
```

正文同时按官方资料修正了以下契约：Collectors.toList 与 Stream.toList 不等价、count 返回 long、teeing 是同一输入的双下游收集、Optional 主要用于返回值而非语法禁止字段、数组回调可能修改共享对象、array_diff 按字符串比较、生成器异常结束并不能取正常返回值、普通对象可 foreach 但不因此满足 iterable。

未覆盖：所有速查片段的独立运行、PHP 8.4 的 array_find/any/all、PHP 8.5、Java 25、实际磁盘写满/设备故障、网络流、并行流性能与线程池调度、Java 对象序列化兼容迁移、远程分页或数据库框架。PrintWriter 失败使用确定性的故障 Writer；它验证错误传播契约，不等于完整存储故障测试。以上 12 个程序的结果不代表四篇所有 API 已穷尽验证。
