# PHP / Java 类型教程的限定验证

日期：2026-09-19。结果：5 / 5 个完整正文实验符合预期。原始命令、退出码、标准输出、标准错误、文档与案例摘要在 [php-java-types.json](php-java-types.json)。

| 文档 | 案例 | 覆盖范围 |
|---|---|---|
| [PHP 变量与类型](../../../../07-php-mastery/basics/03-variables-types.md) | `php-strict-types-boundaries` | 变量关键字名称、强转与输入验证、年龄格式/范围、严格参数、int 到 float、严格/宽松比较、查找索引 0 与 false、resource |
| 同上 | `php-weak-call-boundaries` | 弱调用方允许标量转换，仍拒绝数组 |
| [Java 变量与类型](../../../../08-java-revisited/basics/03-variables-types.md) | `java-boxing-boundaries` | char 默认值、UTF-16、装箱值比较、显式 null 与 getOrDefault、条件分支拆箱、var 后续拓宽赋值 |
| 同上 | `java-text-block-boundaries` | 公共缩进与末尾换行 |
| [Java 类与 Record](../../../../08-java-revisited/basics/04-classes-records.md) | `java-record-boundaries` | 构造不变量、列表快照、修改拒绝、null 拒绝、组件相等、可变元素浅复制 |

运行环境为已有本地镜像 `dev-quest-validation:local` 中的 PHP 8.3.6、Temurin JDK 21.0.12。PHP 示例所用能力兼容该版本；这次没有测试 PHP 8.4/8.5 或 Java 25。镜像标签可被重建，复核时需记录实际工具链版本，不能只比较标签名。

运行器 [verify_php_java_types.py](../verify_php_java_types.py) 复用 [基础参考运行器](../verify_php_java_foundations.py)：只抽取明确标记的完整代码，校验固定案例数与唯一 ID，不添加 import、不补类、不改代码。每个案例写入独立临时目录；Java 使用 `javac --release 21 -encoding UTF-8` 编译再运行，PHP 启用全部错误报告。只有退出码为 0、stderr 为空、stdout 精确匹配声明才计为通过。

在仓库根目录、有 PHP 和 JDK 21 的环境中复现：

```sh
python3 shared-resources/tools/document-quality/verify_php_java_types.py --report /tmp/php-java-types.json
```

本次使用的 PowerShell 容器命令（报告目录为仓库外已有的 `verification-lab`）：

```powershell
docker run --rm --network none --read-only --tmpfs /tmp:rw,nosuid,size=128m --cap-drop ALL --pids-limit 128 --memory 512m --cpus 2 -e PYTHONDONTWRITEBYTECODE=1 -v "${PWD}:/source:ro" -v "${PWD}/../verification-lab:/out:rw" dev-quest-validation:local python3 /source/shared-resources/tools/document-quality/verify_php_java_types.py --report /out/php-java-types-results.json
```

边界：仅证明上述命名案例在给定工具链的输出与异常检查。未将所有讲解片段拼装运行；未执行静态分析器、Java 25 灵活构造器、Lombok/Jackson 集成；未对所有 PHP 内部回调验证 strict_types 传播。正文将版本约束、值类型与签名、浅不可变和缓存扩展等契约链接到 PHP 手册与 Java 官方规范；这些来源复核与运行检查分别提供证据，不把一类证据扩大成另一类。
