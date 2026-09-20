# PHP 环境运行时最小程序验证

本报告记录 [PHP 环境搭建](../../../../07-php-mastery/basics/01-environment-setup.md) 中的 `verify:php-environment-runtime` 正文。运行器从 Markdown 原样提取程序，在 `php:8.5-cli` 容器执行。

它只覆盖该 PHP CLI 的严格标量调用、JSON 编码和 mbstring 加载状态；不覆盖 Composer、Xdebug、FPM、Web 服务器、数据库或读者主机环境。

```bash
python shared-resources/tools/document-quality/verify_php_environment.py --report shared-resources/tools/document-quality/reports/php-environment-validation.json
```
