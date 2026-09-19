# PHP / Java P1 正文提取运行验证

范围只包括六个带命名标记的完整代码围栏：每种语言各覆盖关键字、内置 API/函数和标准库一篇。控制流程页已有独立证据，未重新计入；无标记的教学片段也不计入。

| Case | Category | Document | Runner | Result |
| --- | --- | --- | --- | --- |
| `php-keyword-values` | keyword | `07-php-mastery/reference/language-concepts/01-php-keywords.md` | local php | PASS |
| `php-array` | built-in functions | `07-php-mastery/reference/language-concepts/02-built-in-functions.md` | local php | PASS |
| `php-spl-core` | standard library | `07-php-mastery/reference/library-guides/01-standard-library-spl.md` | local php | PASS |
| `java-flow` | keyword | `08-java-revisited/reference/language-concepts/01-java-keywords.md` | local JDK | PASS |
| `java-java-lang-contract` | built-in APIs (java.lang) | `08-java-revisited/reference/library-guides/03-java-lang.md` | local JDK | PASS |
| `java-text` | standard library | `08-java-revisited/reference/library-guides/01-standard-library.md` | local JDK | PASS |

JSON 记录从正文提取的源码 SHA-256、完整命令、stdout/stderr、退出码与断言结果；它不是全库覆盖率报告。
