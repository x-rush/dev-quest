# Web 安全：沿着一次请求建立检查边界

先修：HTTP、Cookie、SQL 参数、Server/Client Components。以“用户修改自己的文章”为主线，区分输入验证、身份认证、资源授权与输出处理。它们解决不同问题，不能用一个通用 sanitize 函数互相替代。

## 1. 数据从哪里跨越信任边界

```text
浏览器提交 → 解析与限制输入 → 验证会话 → 检查文章归属
          → 参数化写入 → 返回最少结果 → 按输出上下文展示
```

浏览器传来的 userId、角色、价格、隐藏表单字段都可被修改。会话身份必须由服务器验证得到。即使界面隐藏“删除”按钮，攻击者仍可直接调用接口。

## 2. 输入验证：把 unknown 变成业务允许的值

```ts
// lib/article-input.ts；不依赖框架的完整解析函数
export function parseArticleInput(value: unknown): { title: string } {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new Error('请求必须是对象');
  }
  const title = (value as Record<string, unknown>).title;
  if (typeof title !== 'string') throw new Error('标题必须是字符串');
  const normalized = title.trim();
  if (normalized.length < 1 || normalized.length > 120) {
    throw new Error('标题长度必须在 1 到 120 之间');
  }
  return { title: normalized };
}
```

本例返回新对象，避免把请求中额外的 ownerId、isAdmin 等字段直接展开写入数据库。length 按 UTF-16 代码单元计数，若产品要求“用户看到的字符数”，应另定义 Unicode 计数规则。JSON 解析失败、请求体大小、上传限制也要在相应层处理。

## 3. 认证之后仍要逐资源授权

以下是业务顺序示意，requireSession、数据库与实体需要项目自己的真实实现，不能复制后假装已具备认证系统：

```text
session = 验证服务器会话
input = parseArticleInput(请求数据)
更新 articles：条件为 id = articleId 且 owner_id = session.userId
若影响行数为 0：返回统一的不存在或无权限结果
返回 { id, title }，不返回会话令牌或整行内部字段
```

把归属条件放入更新语句，能避免先查归属后无条件更新带来的部分竞态。复杂角色、组织关系和状态转换可能仍需要事务与更完整的授权策略。默认拒绝未明确允许的操作，并对每次资源访问检查权限。[OWASP 授权指南](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

Server Actions 同样是服务端入口，需要验证输入与权限。服务器组件、布局和 Proxy 中的判断不能替代实际数据访问边界的检查。[Next.js 数据安全](https://nextjs.org/docs/app/guides/data-security)

## 4. SQL 参数与标识符不是一回事

```sql
-- 参数占位形式以实际驱动为准，此处展示 PostgreSQL 风格
UPDATE articles SET title = $1 WHERE id = $2 AND owner_id = $3;
```

值应通过驱动参数传入，不能拼接到 SQL 文本中。表名、列名和排序方向通常不能用值占位符替代，应从代码维护的允许列表选择。ORM 也有 raw SQL 入口，使用 ORM 并不自动消除所有注入风险。

## 5. XSS：处理规则取决于输出位置

React 的普通文本插值会转义字符串，例如 `<p>{title}</p>`。但 dangerouslySetInnerHTML、直接设置 innerHTML、动态 URL 和脚本上下文需要单独判断。

如果业务不需要富文本，就按文本展示；需要富文本时，使用维护中的 HTML 清理库并限定允许标签、属性与协议。不要靠正则删除 `<script>` 就声称防住 XSS。HTML 编码、URL 校验、SQL 参数化解决的是不同上下文。[OWASP XSS 预防](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

## 6. Cookie、CSRF 与 CORS

浏览器会自动携带满足条件的 Cookie，因此攻击者可能诱导浏览器发送用户未意图发出的写请求。使用框架或认证库提供的 CSRF 防护，并按部署拓扑校验来源、令牌与会话绑定；SameSite 可作为一层防护，不能机械当作所有业务场景的完整方案。

HttpOnly 限制脚本读取 Cookie，Secure 限制经 HTTPS 发送；它们都不等于资源授权。CORS 控制浏览器跨源读取响应，不是面向任意 HTTP 客户端的身份验证机制，也不能独自承担 CSRF 防护。[OWASP CSRF 指南](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

不要自制短随机串、未绑定会话的双提交令牌或自称恒定时间的 JavaScript 字符串比较来替代成熟机制。JWT 解码只读取内容，验证还应覆盖签名、允许算法、时间以及应用要求的 issuer/audience；权限撤销与登出需要另有设计。

## 7. 密钥、响应头和错误

秘密只留在服务端环境和受控配置中，不放 NEXT_PUBLIC_ 变量、next.config 的公开 env 配置或客户端 props。错误响应返回稳定业务信息，详细堆栈保留在受控日志；日志不记录密码、令牌与完整个人数据。

CSP 用于限制可执行内容来源，需要结合脚本、字体和第三方服务调试；复制过严配置可能直接破坏页面，加入 unsafe-inline 又会改变保护能力。按 [Next.js CSP 指南](https://nextjs.org/docs/app/guides/content-security-policy)实施并验证实际响应头。

## 8. 项目练习与验收

创建两个测试账号 A、B，各有一篇文章。验证 A 能修改自己的文章，但直接请求 B 的 ID 也不能修改；登出后重放请求应失败。再提交空标题、数组、数字标题和额外 ownerId，确认不会越过输入边界。

显示包含 `<b>标题</b>` 的普通标题时，应看到文本而不是被当作 HTML 执行。若选择支持富文本，补充允许标签与危险属性的用例。验收包括数据库最终状态与响应，不能只检查按钮是否隐藏。

本章解释实现边界与验证方法，不代表一个具体项目已经完成安全审计。后续扩展可学习上传、SSRF、速率限制、依赖更新和审计日志，每项都应绑定实际入口与测试场景。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
