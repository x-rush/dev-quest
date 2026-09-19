# PHP 与 Java 基础参考验证

验证对象是下列四篇参考中显式标记的完整程序，代码原样提取，不补 import、不生成缺失变量、不替换真实 API。标记中的预期标准输出与实际运行结果逐字比较；非零退出码或任何标准错误输出都使该案例失败。

| 文档 | 完整程序 | 结果 |
|---|---:|---:|
| [PHP 关键词](../../../../07-php-mastery/reference/language-concepts/01-php-keywords.md) | 3 | 3 通过 |
| [PHP 内置函数](../../../../07-php-mastery/reference/language-concepts/02-built-in-functions.md) | 5 | 5 通过 |
| [Java 关键词](../../../../08-java-revisited/reference/language-concepts/01-java-keywords.md) | 4 | 4 通过 |
| [Java 标准库](../../../../08-java-revisited/reference/library-guides/01-standard-library.md) | 5 | 5 通过 |

总计 **17 / 17 通过**。本地运行环境为 PHP 8.3.6、OpenJDK Temurin 21.0.12，Java 使用 `javac --release 21 -encoding UTF-8` 编译。文档提及的 PHP 8.4/8.5 和 Java 22/25 特性为官方资料核对范围，没有混入这套基线运行案例。

运行记录：[机器报告](php-java-foundations.json)，包含运行时版本、源文档和案例哈希、编译/执行命令、标准输出和错误输出。哈希描述报告生成时的工作树字节；Git 换行归一化后应重新运行而不是仅用文件哈希推断语义差异。

## 复现

需要 Python 3、PHP CLI 和 JDK 21。仓库根目录运行：

```bash
python3 shared-resources/tools/document-quality/verify_php_java_foundations.py --report /tmp/php-java-foundations.json
```

只有一种语言环境时增加 `--language php` 或 `--language java`；这会缩小范围，不能当作两种语言都通过。运行器会检查标记案例数量，防止遗漏标记导致静默减少验证。

本地验证使用现有 `dev-quest-validation:local` 镜像，无网络、只读根文件系统、只读仓库挂载，临时编译/文件实验在受限 tmpfs 内完成。临时目录输出由运行器捕获后删除。

## 验证边界

PHP 关键词中其余局部语法片段已明确标为片段；本报告不将其列为完整脚本。可选 PHP 扩展、PHP 新版特性实测、Java 新版特性、HTTP 外网请求、框架依赖、数据库与部署不属于这 17 个离线案例。文档的语义说明引用 PHP 手册与 JLS/JDK API；通过这些实验也不等于对整个 PHP/Java 模块作出无错误证明。
