# Django 与 Flask 核心对比速查

## 概述

Django 是"全家桶"（ORM/模板/Admin/认证内置），Flask 是"微内核"（路由+模板，其余自由组装）。本条目并排呈现两者的核心机制与选型判断。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Django` `#Flask` `#Web` `#ORM` `#对比` |
| **更新日期** | `2026年9月` |

</details>

## 选型一分钟

| 维度 | Django | Flask | FastAPI |
|------|--------|-------|---------|
| 定位 | 全栈框架 | 微框架 | API 框架 |
| ORM | 内置 | 无（常用 SQLAlchemy） | 无（任意） |
| 异步 | 部分支持（ASGI） | WSGI 为主 | 原生 |
| 适合 | 内容型网站、Admin 后台 | 小服务、灵活组合 | API 服务、高并发 I/O |

---

## 1. Django：最小应用

```bash
uv run django-admin startproject config .
uv run python manage.py startapp bookmarks
uv run python manage.py runserver
```

**模型（ORM）**：

```python
from django.db import models

class Bookmark(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
```

**视图与路由**：

```python
# views.py
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse

def bookmark_list(request):
    items = Bookmark.objects.all()[:50]
    return render(request, "bookmarks/list.html", {"items": items})

def bookmark_json(request, pk: int):
    bm = get_object_or_404(Bookmark, pk=pk)      # 404 化的错误处理
    return JsonResponse({"url": bm.url, "title": bm.title})

# config/urls.py
from django.urls import path
urlpatterns = [
    path("bookmarks/", bookmark_list),
    path("bookmarks/<int:pk>/", bookmark_json),
]
```

**ORM 常用查询**：

```python
Bookmark.objects.filter(tags__name="web").distinct()
Bookmark.objects.filter(title__icontains="python")     # 大小写不敏感包含
Bookmark.objects.count()
Bookmark.objects.select_related("owner").prefetch_related("tags")  # 预加载防 N+1

# 迁移三连
# python manage.py makemigrations / migrate / createsuperuser
```

**要点**: Django 5.x 默认 ASGI 兼容；Admin 后台只需注册模型（`admin.site.register(Bookmark)`）即得增删改查界面。

---

## 2. Flask：最小应用

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/bookmarks")
def list_bookmarks():
    tag = request.args.get("tag")              # 查询参数
    return jsonify([b.to_dict() for b in store.all(tag=tag)])

@app.post("/bookmarks")
def create_bookmark():
    data = request.get_json()                  # 请求体
    saved = store.add(data["url"], data.get("title", ""))
    return jsonify(saved), 201

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "not found"}), 404

# 运行：flask --app main run --debug
```

**蓝图（Blueprint）拆分**：

```python
from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api")

@api.get("/health")
def health(): ...

# main.py 注册
app.register_blueprint(api)
```

**要点**: Flask 用装饰器注册路由，请求上下文中的 request 以及应用上下文中的 g 是上下文本地代理，现代实现基于 contextvars；不能把它们当成普通全局对象或任意跨线程传递；扩展生态按需引入（`flask-sqlalchemy`、`flask-login`）。

---

## 3. 两者的请求处理对照

| 任务 | Django | Flask |
|------|--------|-------|
| 路径参数 | `path("<int:pk>/")` + 位置传参 | `@app.get("/b/<int:pk>")` |
| 查询参数 | `request.GET.get("q")` | `request.args.get("q")` |
| 请求体 | 表单用 request.POST；JSON 读取 request.body 后解析，或使用 DRF 的请求解析与 serializer | request.get_json() 解析 JSON，业务字段另行验证 |
| 返回 JSON | `JsonResponse` | `jsonify` |
| 模板 | `render(request, "x.html", ctx)` | `render_template("x.html", **ctx)` |
| 表单 | `django.forms` 全家桶 | 手动或 `flask-wtf` |
| 认证 | 内置（session + Admin） | `flask-login` 扩展 |

---

## 4. 陷阱速查表

**Django**:
- 改模型忘 `makemigrations`/`migrate`，报"no such column"
- QuerySet 通常惰性求值，同一已求值实例可复用缓存；重新构造查询、切片或 iterator 等行为需分别检查
- N+1 查询：外键遍历配 `select_related`（外键）/`prefetch_related`（多对多）
- `settings.DEBUG = True` 不能上生产（错误页泄漏源码）

**Flask**:
- 生产模式禁用 `--debug`（调试器可执行任意代码）
- 循环导入：把 `db = SQLAlchemy()` 抽到独立 `extensions.py`
- 请求上下文对象（`request`）在视图外访问抛 `RuntimeError`

---

<!-- full-library-explanation -->
## 先比较同一个任务，再比较框架名称

前置知识是 HTTP 请求、函数路由和数据库表。选择框架时，先写出要交付的功能：若需要用户、管理后台、表单和数据库迁移，Django 提供较多统一机制；若希望自行组装一个小服务，Flask 的较小核心给出更大选择空间，但相关集成也由项目负责。

练习只做“按 ID 读取书签”，输入存在和不存在的 ID，分别验收 JSON 200 与 JSON 404。再加“标题必填”的创建操作，比较数据校验、错误格式、事务和测试放在哪里。框架大小不能替代这些行为的定义。

Django 文中的模型与视图是局部片段：需要把应用加入 INSTALLED_APPS、导入模型和视图、创建模板并执行迁移；涉及 owner/tags 的查询还需要定义相应关联字段。Flask 的 store 也需要单独实现，不能将两个片段都称为可直接启动的完整应用。

查询优化时观察真实 SQL 次数：同一个已求值 QuerySet 通常复用结果缓存，重新构造的 QuerySet 或特定求值方式可能再次查询；“重复循环一定重复查询”不能作为判断依据。[Django 查询说明](https://docs.djangoproject.com/en/stable/topics/db/queries/)解释了缓存边界。

## 🔗 相关文档

- 📄 **[FastAPI 核心速查](./01-fastapi-essentials.md)** — API 场景的现代首选
- 📄 **[标准库导航](../library-guides/01-standard-library.md)** — 框架之下共用的基础能力
- 📄 **[typing 注解全表](../language-concepts/05-typing-annotations.md)** — 三框架共同依赖的类型系统


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
