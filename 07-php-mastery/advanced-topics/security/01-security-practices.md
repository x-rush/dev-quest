# 安全实践：SQL 注入、XSS 与 CSRF 防护

> **文档简介**: 用攻击者视角审视 Laravel 应用的三类经典漏洞——SQL 注入、XSS、CSRF，给出框架内建的防线与绕过防线的危险写法
>
> **目标读者**: 需要在上线前做安全自查、或修复安全扫描告警的开发者
>
> **前置知识**: [Laravel 入门](../../frameworks/01-laravel-basics.md)、[生产级 Laravel 应用](../../projects/04-production-laravel-app.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#安全` `#SQL注入` `#XSS` `#CSRF` `#Laravel` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 说清每类漏洞的攻击原理与 Laravel 的默认防线
- ✅ 识别并改掉"绕过防线"的常见写法
- ✅ 在验证、授权、输出三层建立纵深防御

## 1. SQL 注入：绑定参数是唯一正解

原理：用户输入被拼接进 SQL 字符串时，`' OR '1'='1` 之类的载荷改变语句语义。

```php
// ❌ 危险：拼接进 ORDER BY（orderByRaw 与 whereRaw 是注入高发区）
Order::query()->orderByRaw("FIELD(status, '{$request->string('sort')}')")->get();

// ✅ 安全：原生表达式必须用绑定（? 占位由 PDO 处理，值永不进入 SQL 文本）
$sort = $request->string('sort', 'created_at');
Order::query()->orderByRaw('FIELD(status, ?)', [$sort])->get();
```

```php
// Eloquent/查询构建器的常规用法自动绑定，天然安全
Order::where('user_id', $request->integer('user_id'))->get();   // ✅

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

## 3. CSRF：Token 校验同源请求

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

- `api` 中间件组**无 session 无 CSRF**——它不用 Cookie 认证，改用 Bearer Token（请求头不会被跨站自动携带），所以不需要 CSRF 防护
- SPA 若走 Cookie 会话（Sanctum stateful），仍需先取 `/sanctum/csrf-cookie` 并保证 `SameSite=Lax/Strict`

## 4. 其他必修防线

```php
// 密码：hash 而非加密，bcrypt 自带盐
Hash::make($password);        // 存储
Hash::check($password, $hash);// 校验

// 认证延迟：登录限流防爆破
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
[ ] 全仓 grep "whereRaw|orderByRaw|selectRaw"，确认全部使用绑定参数
[ ] 全仓 grep "{!!"，每一处都能说出"谁清洗了它"
[ ] 所有写接口有 Policy 或显式权限判断
[ ] APP_DEBUG=false；/storage 目录不可列目录
[ ] 依赖升级：composer audit 通过
```

安全不是一次性的功能，而是**每次代码评审中的固定检查项**。

## 🔗 相关文档

- 📄 [Laravel 核心速查](../../reference/framework-essentials/01-laravel-essentials.md) — 验证与中间件条目
- 📄 [错误与异常](../../basics/06-error-exceptions.md) — 异常路径的安全处理
- 📄 [架构解析](../architecture/01-laravel-architecture.md) — 中间件管道在生命周期中的位置
- 📄 [生产级 Laravel 应用](../../projects/04-production-laravel-app.md) — 本清单在发布流程中的位置
