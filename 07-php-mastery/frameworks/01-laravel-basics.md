# Laravel 入门：路由、控制器与 Blade 模板

> **文档简介**: 从零创建 Laravel 11 项目，掌握路由定义、资源控制器、Blade 模板渲染与完整请求生命周期
>
> **目标读者**: 已学完 PHP 基础、第一次接触 Laravel 的开发者
>
> **前置知识**: [面向对象基础](../basics/04-functions-oop.md)、[环境搭建](../basics/01-environment-setup.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#Laravel` `#路由` `#控制器` `#Blade` `#请求生命周期` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 创建 Laravel 11 项目并理解目录职责
- ✅ 编写路由与控制器，返回视图与 JSON
- ✅ 用 Blade 模板组织页面布局与组件
- ✅ 说清一次 HTTP 请求在 Laravel 内部的流转过程

## 1. 创建项目

```bash
# 创建全新 Laravel 11 项目（要求 PHP >= 8.2，本模块基线为 8.3）
composer create-project laravel/laravel blog-app
cd blog-app

# 启动开发服务器（http://localhost:8000）
php artisan serve
```

关键目录速览：

| 目录 | 职责 |
|------|------|
| `routes/` | 路由定义（web.php 面向页面，api.php 面向接口） |
| `app/Http/Controllers/` | 控制器：组织请求处理逻辑 |
| `resources/views/` | Blade 模板 |
| `app/Models/` | Eloquent 模型 |
| `config/` | 框架配置 |

## 2. 路由：URI 到动作的映射

```php
// routes/web.php
use App\Http\Controllers\PostController;
use Illuminate\Support\Facades\Route;

// 闭包路由：适合简单页面
Route::get('/', fn () => view('home'))->name('home');

// 带参数 + 约束：{id} 必须是数字
Route::get('/posts/{id}', fn (string $id) => "文章 {$id}")
    ->whereNumber('id')
    ->name('posts.show');

// 控制器路由（生产环境必须用控制器类，路由缓存不支持闭包）
Route::get('/posts', [PostController::class, 'index'])->name('posts.index');

// RESTful 资源路由：一次注册 7 个动作
Route::resource('posts', PostController::class);
```

路由命名后可用 `route('posts.show', ['id' => 1])` 生成 URL，避免硬编码。

## 3. 控制器：请求的组织者

```bash
# 生成资源控制器（含 index/store/show/update/destroy 骨架）
php artisan make:controller PostController --resource
```

```php
// app/Http/Controllers/PostController.php
namespace App\Http\Controllers;

use App\Models\Post;
use Illuminate\Http\Request;
use Illuminate\Http\Response;

final class PostController extends Controller
{
    // 列表页：渲染 Blade 视图
    public function index(): Response
    {
        return response()->view('posts.index', [
            'posts' => Post::latest()->paginate(10),
        ]);
    }

    // 创建接口：先验证，再落库（永不信任用户输入）
    public function store(Request $request): Response
    {
        $validated = $request->validate([
            'title' => ['required', 'string', 'max:120'],
            'body'  => ['required', 'string'],
        ]);

        $post = Post::create($validated);

        return response()->json($post, Response::HTTP_CREATED);
    }
}
```

依赖（如 `Request`）通过类型提示自动注入——这是服务容器的基本用法，原理见[架构解析](../advanced-topics/architecture/01-laravel-architecture.md)。

## 4. Blade 模板

Blade 是 Laravel 的模板引擎：原样输出 HTML，`{{ }}` 内的表达式**自动转义**（防 XSS）。

```blade
{{-- resources/views/layouts/app.blade.php：布局 --}}
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <title>@yield('title', 'Blog')</title>
</head>
<body>
    @if (auth()->check())
        <p>欢迎，{{ auth()->user()->name }}</p>
    @endif

    <main>
        @yield('content')
    </main>
</body>
</html>
```

```blade
{{-- resources/views/posts/index.blade.php --}}
@extends('layouts.app')

@section('title', '文章列表')

@section('content')
    @forelse ($posts as $post)
        <article>
            <h2>{{ $post->title }}</h2>
            {{-- 原始输出需显式信任：仅用于你完全掌控的内容 --}}
            <p>{!! $post->summary_html !!}</p>
        </article>
    @empty
        <p>暂无文章</p>
    @endforelse

    {{ $posts->links() }} {{-- 分页组件 --}}
@endsection
```

也可用匿名组件（`php artisan make:component Alert`）替代 `@include`，逻辑进类、模板进视图，复用性更好。

## 5. 请求生命周期

一次请求的完整流转：

```text
HTTP 请求
  → public/index.php（唯一入口）
  → 加载 composer 自动加载与 bootstrap/app.php
  → HTTP Kernel：按顺序执行全局中间件（会话、CSRF、加密等）
  → 路由匹配 → 路由中间件组（web / api）
  → 控制器动作 → 返回 Response
  → 中间件后置管道（逐层回溯）
  → 发送响应给客户端
```

理解这条管道的两个意义：①中间件是横切关注点（认证、日志、限流）的正确挂载点；②`api` 组无会话无 CSRF，`web` 组有——决定了两类路由的安全模型（见[安全实践](../advanced-topics/security/01-security-practices.md)）。

## ❓ 常见问题

**Q: 路由定义了却返回 404？**
A: 先 `php artisan route:list` 确认路由已注册；若用了 `route:cache`，闭包路由会直接报错，缓存前必须全部改为控制器类。

**Q: Blade 页面显示旧内容？**
A: `php artisan view:clear` 清理编译后的模板缓存。

## 🔗 相关文档

- 📄 [Laravel 核心速查](../reference/framework-essentials/01-laravel-essentials.md) — 路由/Eloquent/Artisan 条目式参考
- 📄 [类型系统与现代 OOP](../reference/language-concepts/03-types-oop-modern.md) — 控制器中 readonly、枚举等语法细节
- 📄 [Laravel 进阶：Eloquent 与队列](./02-laravel-advanced.md) — 本文的进阶篇
- 📄 [综合练习：CLI 任务管理工具](../basics/08-first-project.md) — Laravel 之前的纯 PHP 项目体验
