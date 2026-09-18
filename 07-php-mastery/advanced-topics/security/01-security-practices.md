# 安全实践：SQL 注入、XSS 与 CSRF 防护

> **文档简介**: 用攻击者视角审视 Laravel 应用的三类经典漏洞——SQL 注入、XSS、CSRF，给出框架内建的防线与绕过防线的危险写法
>
> **目标读者**: 需要在上线前做安全自查、或修复安全扫描告警的开发者
>
> **前置知识**: [Laravel 入门](../../frameworks/01-laravel-basics.md)、[生产级 Laravel 应用](../../projects/04-production-laravel-app.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#安全` `#SQL注入` `#XSS` `#CSRF` `#Laravel` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 说清每类漏洞的攻击原理与 Laravel 的默认防线
- ✅ 识别并改掉"绕过防线"的常见写法
- ✅ 在验证、授权、输出三层建立纵深防御

## 1. SQL 注入：值绑定与标识符白名单

原理：用户输入被拼接进 SQL 字符串时，`' OR '1'='1` 之类的载荷改变语句语义。

```php
// ❌ 危险：拼接进 ORDER BY（orderByRaw 与 whereRaw 是注入高发区）
Order::query()->orderByRaw("FIELD(status, '{$request->string('sort')}')")->get();

// ✅ 安全：原生表达式必须用绑定（? 占位由 PDO 处理，把值与 SQL 结构分开交给驱动处理）
$sort = $request->string('sort', 'created_at');
Order::query()->orderByRaw('FIELD(status, ?)', [$sort])->get();
```

```php
// Eloquent/查询构建器的普通值条件自动绑定以防注入，但仍需授权与字段白名单
Order::where('user_id', $request->user()->id)->get(); // 当前认证用户的订单

// 批量赋值还有第二层洞：未做字段白名单
// ❌ $request->all() 会把 is_admin 等字段一并写入
Order::create($request->all());
// ✅ 只放行验证过的字段
Order::create($request->validated());
```

框架防线：PDO 预处理 + `$fillable` 白名单 + FormRequest 验证。三层缺一不可，攻击面在"绕过任何一层"的写法上。

## 2. XSS：转义边界在模板

原理：用户输入的 `<script>` 被原样写入 HTML，在其他用户浏览器中执行。

```blade
{{-- Blade 的 {{ }} 自动调用 htmlspecialchars，默认安全 --}}
<p>{{ $post->title }}</p>

{{-- ❌ 危险：!!! 跳过转义。仅当内容经过服务端白名单清洗后才允许 --}}
{!! $post->body_html !!}
```

确实需要富文本时的最小安全实现：

```php
// composer require ezyang/htmlpurifier
$clean = (new \HTMLPurifier())->purify($request->string('body'));
// 服务端清洗后存储清洗结果，模板侧仍用 {!! !!}——清洗与信任点一一对应
```

补充纵深：`Content-Security-Policy` 响应头限制脚本来源（Nginx 或中间件层配置），使侥幸注入的脚本无法加载外域资源。

## 3. CSRF：Token 防止跨站伪造写请求

原理：受害者浏览器带着 Cookie 访问攻击者构造的跨站表单，"冒充"受害者提交写操作。

Laravel 的 `web` 中间件组自动校验 `_token` 字段（session 对比）：

```blade
{{-- ❌ 表单缺 token 直接 419 --}}
<form method="POST" action="/posts">
    @csrf   {{-- 生成 <input type="hidden" name="_token" ...> --}}
    ...
</form>
```

边界辨析（最常混淆处）：

- 默认 api 组不提供会话和 CSRF；是否需要 CSRF 防护取决于实际认证方式。仅使用显式 Authorization Bearer 凭据与启用 Cookie 会话的 API 不能一概而论
- SPA 若走 Cookie 会话（Sanctum stateful），仍需先取 `/sanctum/csrf-cookie` 并保证 `SameSite=Lax/Strict`

## 4. 其他必修防线

```php
// 密码：hash 而非加密，bcrypt 自带盐
Hash::make($password);        // 存储
Hash::check($password, $hash);// 校验

// 认证限流：定义规则后还需绑定到实际登录路由
RateLimiter::for('login', fn (Request $r) => Limit::perMinute(5)->by($r->ip()));

// 上传：白名单 + MIME 校验 + 移出可执行目录
$request->validate(['avatar' => ['image', 'mimes:jpg,png,webp', 'max:2048']]);
$path = $request->file('avatar')->store('avatars', 's3');   // 不落 public/
```

| 风险 | 默认防线 | 常见失守点 |
|------|---------|-----------|
| SQL 注入 | PDO 绑定 | `whereRaw/orderByRaw` 拼接 |
| XSS | Blade `{{ }}` 转义 | `{!! !!}` 包裹未清洗内容 |
| CSRF | web 组 token 校验 | 把写路由放进 api 组却用 Cookie 认证 |
| 越权 | Policy/Gate | 忘记 `$this->authorize()`（见[博客平台](../../projects/02-blog-platform.md)） |
| 敏感泄漏 | `.env` 不进库 | `APP_DEBUG=true` 上线、日志打请求体 |

## 5. 上线前安全自查清单

```text
[ ] 全仓搜索 whereRaw/orderByRaw/selectRaw，确认外部值绑定、动态标识符使用允许列表
[ ] 全仓 grep "{!!"，每一处都能说出"谁清洗了它"
[ ] 所有写接口有 Policy 或显式权限判断
[ ] APP_DEBUG=false；/storage 目录不可列目录
[ ] 依赖升级：composer audit 通过
```

安全不是一次性的功能，而是**每次代码评审中的固定检查项**。

<!-- full-library-explanation -->
## 从攻击输入追踪到执行边界

前置是 HTTP、数据库参数和浏览器渲染。输入验证确认形状与范围，授权确认当前主体能否访问资源，输出编码确认数据在目标上下文中不会变成代码。三者解决不同问题：合法整数订单 ID 仍可能属于别人；已验证文本进入 HTML、URL 或 JavaScript 时仍需各自的安全处理。

参数绑定处理 SQL 值，无法绑定表名、列名或 ASC/DESC。排序字段要用服务端允许列表映射；列表查询还要按当前认证主体限制范围。Blade 的 HTML 转义适用于文本和正确引用的属性，不能直接保障脚本代码、事件属性或 javascript: URL 安全。富文本清洗策略也需限定标签、属性和 URL 协议。

**练习**：用户 A 请求用户 B 的订单，预期拒绝且不泄露订单内容；把 sort 改成不允许的字段，预期校验失败；提交带脚本标签的标题，页面显示文本而不执行。对 Cookie 认证的写接口分别发送缺失、错误和正确 CSRF 凭据，在启用真实中间件的环境验证。测试通过的结论应限定在覆盖的入口和输入。

依据：[SQL 查询绑定边界](https://laravel.com/docs/13.x/queries)、[CSRF](https://laravel.com/docs/13.x/csrf)、[授权](https://laravel.com/docs/13.x/authorization)。


本轮未在本机执行 PHP 片段；文中的输出为预期值，版本相关行为请用项目运行时验证。

## 🔗 相关文档

- 📄 [Laravel 核心速查](../../reference/framework-essentials/01-laravel-essentials.md) — 验证与中间件条目
- 📄 [错误与异常](../../basics/06-error-exceptions.md) — 异常路径的安全处理
- 📄 [架构解析](../architecture/01-laravel-architecture.md) — 中间件管道在生命周期中的位置
- 📄 [生产级 Laravel 应用](../../projects/04-production-laravel-app.md) — 本清单在发布流程中的位置


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
