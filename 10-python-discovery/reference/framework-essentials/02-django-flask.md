# Django 与 Flask 核心对比速查

## 概述

Django 是"全家桶"（ORM/模板/Admin/认证内置），Flask 是"微内核"（路由+模板，其余自由组装）。本条目并排呈现两者的核心机制与选型判断。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Django` `#Flask` `#Web` `#ORM` `#对比` |
| **更新日期** | `2026年9月` |

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

**要点**: Flask 用装饰器注册路由，请求上下文（`request`/`g`）是线程本地代理；扩展生态按需引入（`flask-sqlalchemy`、`flask-login`）。

---

## 3. 两者的请求处理对照

| 任务 | Django | Flask |
|------|--------|-------|
| 路径参数 | `path("<int:pk>/")` + 位置传参 | `@app.get("/b/<int:pk>")` |
| 查询参数 | `request.GET.get("q")` | `request.args.get("q")` |
| 请求体 | `request.POST` / DRF `serializer` | `request.get_json()` |
| 返回 JSON | `JsonResponse` | `jsonify` |
| 模板 | `render(request, "x.html", ctx)` | `render_template("x.html", **ctx)` |
| 表单 | `django.forms` 全家桶 | 手动或 `flask-wtf` |
| 认证 | 内置（session + Admin） | `flask-login` 扩展 |

---

## 4. 陷阱速查表

**Django**:
- 改模型忘 `makemigrations`/`migrate`，报"no such column"
- `filter()` 返回 QuerySet 是惰性的，循环外重复遍历会重复查询——用 `list(qs)` 物化
- N+1 查询：外键遍历配 `select_related`（外键）/`prefetch_related`（多对多）
- `settings.DEBUG = True` 不能上生产（错误页泄漏源码）

**Flask**:
- 生产模式禁用 `--debug`（调试器可执行任意代码）
- 循环导入：把 `db = SQLAlchemy()` 抽到独立 `extensions.py`
- 请求上下文对象（`request`）在视图外访问抛 `RuntimeError`

---

## 🔗 相关文档

- 📄 **[FastAPI 核心速查](./01-fastapi-essentials.md)** — API 场景的现代首选
- 📄 **[标准库导航](../library-guides/01-standard-library.md)** — 框架之下共用的基础能力
- 📄 **[typing 注解全表](../language-concepts/05-typing-annotations.md)** — 三框架共同依赖的类型系统
