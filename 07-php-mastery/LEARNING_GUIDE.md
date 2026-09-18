# PHP / Laravel：理解地图与学习规划

> 前置：基本函数与数组；理解终端输入和 HTTP 输入不同。安装 PHP 后检查扩展，Composer 管 PHP 包而非替代解释器。

## 先回答一个问题

**同一个脚本在命令行与 HTTP 请求中运行，有哪些输入和生命周期差异？**

PHP 先处理输入并产生输出，Laravel 在其上提供路由、容器、ORM 与任务体系。先掌握字符串、数组、类型转换和错误，再理解框架约定；否则容易把语言行为误认为 Laravel 的魔法。

## 概念怎样连接

CLI 脚本 → 类型与数组 → 函数/类 → 异常 → Composer/自动加载 → 路由 → 数据库与测试

| 概念 | 必要解释 |
|---|---|
| 数组 | PHP array 同时承担有序映射的角色；过滤后键可能不连续，JSON 输出形状可能随之改变。 |
| 严格比较 | 未找到的 false 与下标 0 需要区分；先看函数返回契约，再决定如何判断。 |
| 请求生命周期 | 传统请求中的内存状态不应被当成持久存储；队列或常驻 worker 又有不同的对象复用边界。 |

## 从 0 到 1 的阅读顺序

以下按模块现有章节编号导航。章节中的“先理解，再动手”给出本节重点与自测；环境版本集中看[模块 README](README.md)。

1. [PHP 开发环境搭建 - PHP 8.5+ 与现代工具链](basics/01-environment-setup.md)
2. [第一个 PHP 脚本 - CLI 与 Web 双运行模式](basics/02-first-script.md)
3. [变量与类型系统 - 从动态到严格类型](basics/03-variables-types.md)
4. [函数与面向对象 - 构造器属性提升时代](basics/04-functions-oop.md)
5. [控制流程 - 从 if 到 match 表达式](basics/05-control-flow.md)
6. [错误与异常 - Throwable 的世界](basics/06-error-exceptions.md)
7. [高级特性 - 枚举、属性注解与 Fibers](basics/07-advanced-features.md)
8. [综合练习 - CLI 任务管理工具](basics/08-first-project.md)

## 三个阶段如何验收

1. 写 CLI 标题校验，正常和空白输入产生不同退出结果。
2. 用 JSON 文件保存待办，损坏 JSON 要报告错误而不是悄悄当成空列表。
3. 迁移到 Laravel API 后，测试创建、非法输入与不存在 ID；再接认证。

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

## 框架与高级主题怎么选

Laravel 为主线，Symfony 用于理解组件化选择。队列、事件和缓存放在明确需要异步处理或减少重复读取后，先解释失败重试和一致性。

## 全量参考怎么查

关键词解决“语法是什么意思”，内置函数解决“直接能调用什么”，标准库解决“导入以后能做什么”。框架 API 另列，避免把库函数误当成语言本身。以下是现有文章的完整导航，不代表每个 API 都已充分讲解；具体覆盖缺口进入审查台账。

### framework-essentials

- [Laravel 核心速查（Laravel 13）](reference/framework-essentials/01-laravel-essentials.md)
- [Symfony 核心速查（Symfony 7）](reference/framework-essentials/02-symfony-essentials.md)

### language-concepts

- [PHP 关键字与保留字详解](reference/language-concepts/01-php-keywords.md)
- [常用内置函数分类全表](reference/language-concepts/02-built-in-functions.md)
- [类型系统与现代 OOP 特性全表](reference/language-concepts/03-types-oop-modern.md)
- [控制结构全表](reference/language-concepts/04-control-flow.md)
- [数组函数与集合操作模式](reference/language-concepts/05-arrays-patterns.md)
- [生成器与迭代器](reference/language-concepts/06-generators-iterators.md)
- [命名空间与自动加载](reference/language-concepts/07-namespaces-autoloading.md)
- [反射与属性注解](reference/language-concepts/08-reflection-attributes.md)
- [字符串与正则](reference/language-concepts/09-strings-regex.md)
- [日期时间](reference/language-concepts/10-datetime.md)
- [异常体系与错误处理](reference/language-concepts/11-errors-exceptions.md)
- [PHP 8.4/8.5 增量特性](reference/language-concepts/12-modern-php-85.md)
- [弱比较与强比较全表（== / ===）](reference/language-concepts/13-weak-comparison.md)
- [值语义与引用（&）](reference/language-concepts/14-references-value-semantics.md)
- [超全局变量（Superglobals）](reference/language-concepts/15-superglobals.md)
- [运算符全表与优先级](reference/language-concepts/16-operators.md)
- [魔术方法全表（Magic Methods）](reference/language-concepts/17-magic-methods.md)
- [常量与魔术常量](reference/language-concepts/18-constants-magic-constants.md)

### library-guides

- [SPL 与标准库核心扩展](reference/library-guides/01-standard-library-spl.md)
- [Composer 生态精选](reference/library-guides/02-composer-ecosystem.md)
- [PDO 数据库访问层](reference/library-guides/03-pdo.md)
- [JSON 编解码](reference/library-guides/04-json.md)
- [文件与流 I/O](reference/library-guides/05-file-stream-io.md)
- [HTTP、会话与 Cookie（原生 PHP 层）](reference/library-guides/06-http-session-cookie.md)
- [内置扩展地图](reference/library-guides/07-extension-map.md)

### quick-references

- [现代 PHP 一行式速查](reference/quick-references/01-php-cheatsheet.md)
- [常见错误排查](reference/quick-references/02-troubleshooting.md)

## 卡住时

先判断是术语不懂、输入输出不清、代码上下文缺失，还是运行环境不同。返回[学习方法](../shared-resources/learning-guide.md)按证据排查；通用术语见[术语解释](../shared-resources/glossary.md)。
