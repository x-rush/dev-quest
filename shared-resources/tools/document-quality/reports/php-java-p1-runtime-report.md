# PHP / Java P1 正文提取运行验证

范围只包括九个带命名标记的完整代码围栏：覆盖 PHP/Java 的关键字、内置 API/函数和标准库，以及 Java 的第一个程序、枚举语义和接口语义。控制流程页已有独立证据，未重新计入；无标记的教学片段也不计入。

| Case | Category | Document | Runner | Result |
| --- | --- | --- | --- | --- |
| `php-keyword-values` | keyword | `07-php-mastery/reference/language-concepts/01-php-keywords.md` | php:8.5-cli-alpine container | PASS |
| `php-array` | built-in functions | `07-php-mastery/reference/language-concepts/02-built-in-functions.md` | php:8.5-cli-alpine container | PASS |
| `php-spl-core` | standard library | `07-php-mastery/reference/library-guides/01-standard-library-spl.md` | php:8.5-cli-alpine container | PASS |
| `java-flow` | keyword | `08-java-revisited/reference/language-concepts/01-java-keywords.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-first-program-classic` | first program | `08-java-revisited/basics/02-first-program.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-enum-stable-code` | enum semantics | `08-java-revisited/reference/language-concepts/08-enums.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-interface-default-resolution` | interface semantics | `08-java-revisited/reference/language-concepts/10-interface-semantics.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-java-lang-contract` | built-in APIs (java.lang) | `08-java-revisited/reference/library-guides/03-java-lang.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-text` | standard library | `08-java-revisited/reference/library-guides/01-standard-library.md` | eclipse-temurin:21-jdk-noble container | PASS |

JSON 记录从正文提取的源码 SHA-256、完整命令、stdout/stderr、退出码与断言结果；它不是全库覆盖率报告。
