# PHP、Java、Python 第十轮：正文提取验证

验证器直接从三篇 Markdown 正文抽取具名围栏代码，在临时目录追加断言并运行；临时文件会删除，不依赖 `verification-lab` 产物。

| 语言 | 页面 | 提取案例 | 状态 |
|---|---|---|---|
| PHP | `07-php-mastery/reference/language-concepts/09-strings-regex.md` | PCRE example fence containing preg_replace_callback | PASS |
| Java | `08-java-revisited/reference/library-guides/07-java-text-and-time-format.md` | complete FormatDemo fence | PASS |
| Python | `10-python-discovery/basics/04-functions-oop.md` | dataclass example fence | PASS |

## 执行环境与范围

- 通过 `dev-quest-validation:local` 容器执行：PHP 8.3.6、OpenJDK 21.0.12、Python 3.12.3。
- 每个 PASS 仅覆盖表中具名的源代码围栏及其追加断言，不表示整页或外部框架已验证。
- JSON 报告保留实际退出码和标准输出/错误输出。
