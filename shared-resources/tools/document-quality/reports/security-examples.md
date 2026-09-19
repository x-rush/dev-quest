# 安全实践正文复核与运行边界

本轮复核五个后端模块的安全专题，重点检查认证、输入、对象授权和失败路径是否互相混淆。正文修改不等于整个框架的安全验收；以下将实际执行与仍需集成测试的内容分开记录。

## 实际修正

| 正文 | 原问题 | 当前处理 |
|---|---|---|
| [Go 安全](../../../../01-go-backend/advanced-topics/security/01-security-best-practices.md) | JWT 解析失败后解引用 token；未限定算法、发行方、受众、必需 exp；中间件闭包复用 DTO | 先处理错误与 nil，再读取 claims；服务端固定验证策略；每请求独立 DTO、正文大小、未知字段、连续 JSON 与对象授权示例 |
| [PHP 安全](../../../../07-php-mastery/advanced-topics/security/01-security-practices.md) | 排序列与 SQL 值混淆；把 validated 当作赋值/授权保证；CSRF 与上传条件不清 | 动态列允许列表、服务端所有者、PDO 绑定与原子 owner 条件；补真实 CSRF 中间件和存储权限验收 |
| [Java 安全](../../../../08-java-revisited/advanced-topics/security/01-security-practices.md) | 默认 decoder 被宣称验证 aud；链外 URL 未兜底；无状态被等同于无 CSRF；默认 principal 被当成业务对象 | 显式组合 issuer/时间与 exp/sub/aud 验证器、默认拒绝兜底、按浏览器凭据判断 CSRF、scope 与对象权限分离 |
| [Node 安全](../../../../09-nodejs-backend/advanced-topics/security/01-security-practices.md) | 普通对象索引允许原型链属性；校验 exp 不等于必需 exp；文件 ID 被当成全部防线 | 使用自有属性允许列表、声明类型/存在性检查；分别验证 ID、存在性、对象归属并说明文件系统边界 |
| [Python 安全](../../../../10-python-discovery/advanced-topics/security/01-security-practices.md) | bcrypt 未说明字节上限；配置仅声明类未实例化；JWT 必需声明不完整 | 统一 UTF-8 字节策略、SecretStr 与实例化、明确 required claims、SQL 绑定和 owner 条件实验 |

## 已执行的正文完整程序

结果见 [security-examples.json](security-examples.json)，由 [验证器](../verify_security_examples.py) 直接抽取对应 `security-check` 标识下的完整围栏，不补 import 或伪造框架 API。

| 程序 | 断言范围 | 结果 |
|---|---|---|
| Go 输入与对象权限 | 5 种请求正文 + 跨用户修改 | 6 个检查通过 |
| PHP PDO SQLite | 注入作为值、跨用户拒绝且数据不变、本人修改成功 | 3 个检查通过 |
| Node 文件与排序 | 本人/别人/不存在文件、路径穿越、原型属性、合法排序 | 6 个检查通过 |
| Python SQLite | 注入作为值、跨用户拒绝且数据不变、本人修改成功 | 3 个检查通过 |

共 4 个程序、18 个明确检查。每个程序都要求退出码为 0、标准输出完全匹配、标准错误为空。JSON 保存文档与代码 SHA-256、源行、运行时版本、镜像 ID、命令和实际输出；正文改变后应重新执行，不能挪用旧哈希证明新文档。

## 重现

需要 Python 3 与 Docker，预先准备 `golang:1`、`php:8.5-cli-alpine`、`node:24-bookworm-slim`、`python:3.14-alpine` 镜像。仓库根目录执行：

```bash
python shared-resources/tools/document-quality/verify_security_examples.py --report shared-resources/tools/document-quality/reports/security-examples.json
```

标签可能移动，因此运行器先记录镜像 ID，再使用该 ID 执行。复验特定历史环境时，应保留对应镜像或使用可信注册表中的相同摘要。容器无网络，根文件系统与正文挂载只读，临时编译目录可写，有 CPU、内存与进程数量限制。不读取生产凭据，不启动公网服务。

## 未被这些程序证明的部分

Go JWT 库、Spring Security 自定义 decoder、Laravel/Blade/Sanctum、Hono/jsonwebtoken、FastAPI/PyJWT、bcrypt/Pydantic 的集成片段分别需要真实依赖、过滤器/中间件与业务工程测试。它们的关键契约已依据正文中的官方资料修正，但不能因为同一文件的标准库程序通过就计为运行验证通过。

文件磁盘竞态、真实身份提供方、刷新/撤销时效、浏览器 CSRF、上传存储权限、反向代理信任和部署配置仍需文中验收矩阵。漏洞扫描零结果也不是这些业务边界的验证证据。
