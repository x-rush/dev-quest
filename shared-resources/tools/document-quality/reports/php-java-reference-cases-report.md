# PHP / Java P1 正文提取运行验证

范围仅为四篇没有 `runtime-evidence` 的核心页。每个案例直接提取 `reference-case` 注释紧随的完整代码围栏；JSON 保存源码哈希、工具链版本、命令、标准输出、错误输出、退出码与断言。

| Case | Document | Language | Result |
| --- | --- | --- | --- |
| `php-keyword-values` | `07-php-mastery/reference/language-concepts/01-php-keywords.md` | php | PASS |
| `php-keyword-generator` | `07-php-mastery/reference/language-concepts/01-php-keywords.md` | php | PASS |
| `php-keyword-control` | `07-php-mastery/reference/language-concepts/01-php-keywords.md` | php | PASS |
| `php-array` | `07-php-mastery/reference/language-concepts/02-built-in-functions.md` | php | PASS |
| `php-sort` | `07-php-mastery/reference/language-concepts/02-built-in-functions.md` | php | PASS |
| `php-text-json` | `07-php-mastery/reference/language-concepts/02-built-in-functions.md` | php | PASS |
| `php-date` | `07-php-mastery/reference/language-concepts/02-built-in-functions.md` | php | PASS |
| `php-file` | `07-php-mastery/reference/language-concepts/02-built-in-functions.md` | php | PASS |
| `java-flow` | `08-java-revisited/reference/language-concepts/01-java-keywords.md` | java | PASS |
| `java-record` | `08-java-revisited/reference/language-concepts/01-java-keywords.md` | java | PASS |
| `java-patterns` | `08-java-revisited/reference/language-concepts/01-java-keywords.md` | java | PASS |
| `java-resource` | `08-java-revisited/reference/language-concepts/01-java-keywords.md` | java | PASS |
| `java-text` | `08-java-revisited/reference/library-guides/01-standard-library.md` | java | PASS |
| `java-collections` | `08-java-revisited/reference/library-guides/01-standard-library.md` | java | PASS |
| `java-decimal` | `08-java-revisited/reference/library-guides/01-standard-library.md` | java | PASS |
| `java-time` | `08-java-revisited/reference/library-guides/01-standard-library.md` | java | PASS |
| `java-files` | `08-java-revisited/reference/library-guides/01-standard-library.md` | java | PASS |

只有实际执行并匹配预期输出的 `PASS` 才构成此报告的运行证据；运行环境缺少所需工具时，验证器直接失败且不会生成可计数状态。
