# PHP / Java P1 正文提取运行验证

范围只包括十五个带命名标记的完整代码围栏：覆盖 PHP 的第一个脚本、关键字、内置 API/函数、标准库、PDO 事务绑定、异常链和 PCRE 返回值，以及 Java 的第一个程序、现代特性、枚举语义、接口语义和速查边界。控制流程页已有独立证据，未重新计入；无标记的教学片段也不计入。

| Case | Category | Document | Runner | Result |
| --- | --- | --- | --- | --- |
| `php-first-script-cli-contract` | first PHP script | `07-php-mastery/basics/02-first-script.md` | php:8.5-cli-alpine container | PASS |
| `php-keyword-values` | keyword | `07-php-mastery/reference/language-concepts/01-php-keywords.md` | php:8.5-cli-alpine container | PASS |
| `php-array` | built-in functions | `07-php-mastery/reference/language-concepts/02-built-in-functions.md` | php:8.5-cli-alpine container | PASS |
| `php-spl-core` | standard library | `07-php-mastery/reference/library-guides/01-standard-library-spl.md` | php:8.5-cli-alpine container | PASS |
| `php-pdo-bind-and-rollback` | PDO transaction and binding | `07-php-mastery/reference/library-guides/03-pdo.md` | php:8.5-cli-alpine container | PASS |
| `php-exception-chain-finally` | exception chain and finally | `07-php-mastery/reference/language-concepts/11-errors-exceptions.md` | php:8.5-cli-alpine container | PASS |
| `php-pcre-three-states` | PCRE result states | `07-php-mastery/reference/language-concepts/09-strings-regex.md` | php:8.5-cli-alpine container | PASS |
| `java-flow` | keyword | `08-java-revisited/reference/language-concepts/01-java-keywords.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-first-program-classic` | first program | `08-java-revisited/basics/02-first-program.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-enum-stable-code` | enum semantics | `08-java-revisited/reference/language-concepts/08-enums.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-interface-default-resolution` | interface semantics | `08-java-revisited/reference/language-concepts/10-interface-semantics.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-modern-features-jdk21` | modern Java features | `08-java-revisited/basics/07-modern-features.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-cheatsheet-boundaries` | quick-reference boundaries | `08-java-revisited/reference/quick-references/01-java-cheatsheet.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-java-lang-contract` | built-in APIs (java.lang) | `08-java-revisited/reference/library-guides/03-java-lang.md` | eclipse-temurin:21-jdk-noble container | PASS |
| `java-text` | standard library | `08-java-revisited/reference/library-guides/01-standard-library.md` | eclipse-temurin:21-jdk-noble container | PASS |

JSON 记录从正文提取的源码 SHA-256、完整命令、stdout/stderr、退出码与断言结果；它不是全库覆盖率报告。
