# FastAPI 入门 — 路由、Pydantic 模型与自动文档

> **文档简介**: 用 FastAPI 从零构建一个类型安全的 REST API，掌握路由声明、Pydantic 请求/响应模型与自动生成的交互式文档
>
> **目标读者**: 已完成本模块 basics 入门路径、想用 Python 做 Web 后端的开发者
>
> **前置知识**: 类型注解（[reference 05](../reference/language-concepts/05-typing-annotations.md)）、uv 项目管理（[basics 01](../basics/01-environment-setup.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#FastAPI` `#Pydantic` `#REST` `#自动文档` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 uv 初始化 FastAPI 项目并启动开发服务器
- ✅ 声明路径参数、查询参数并理解自动校验行为
- ✅ 用 Pydantic 模型定义请求体与响应体
- ✅ 使用 `/docs` 与 `/redoc` 自动文档调试 API
- ✅ 用 `HTTPException` 返回规范的错误响应

---

## 1. 项目初始化

```bash
# 创建应用骨架并安装依赖
uv init --app todo-api && cd todo-api
uv add fastapi "uvicorn[standard]"

# 启动开发服务器（热重载）
uv run uvicorn main:app --reload
```

## 2. 第一个路由：路径参数

```python
# main.py
from fastapi import FastAPI, HTTPException, status

app = FastAPI(title="待办服务", version="0.1.0")

# 演示用内存存储，后续项目会换成数据库
_TODOS: dict[int, dict] = {1: {"id": 1, "title": "学 FastAPI", "done": False}}

@app.get("/health")
def health() -> dict[str, str]:
    """健康检查端点，文档字符串会显示在 /docs 中。"""
    return {"status": "ok"}

@app.get("/todos/{todo_id}")
def read_todo(todo_id: int) -> dict:
    # 注解 int 让 FastAPI 自动做类型转换；请求 /todos/abc 会得到 422
    if todo_id not in _TODOS:
        # 规范错误出口：状态码 + 人类可读的 detail
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="待办不存在")
    return _TODOS[todo_id]
```

**要点**：

- 函数签名即校验规则——路径参数注解为 `int`，非数字请求直接返回 422
- `HTTPException` 是 FastAPI 推荐的业务错误出口（异常机制基础见 [basics 06](../basics/06-exceptions.md)）
- 所有语法细节可随时查 [FastAPI 核心速查字典](../reference/framework-essentials/01-fastapi-essentials.md)

## 3. Pydantic 模型：请求体与响应体

```python
from pydantic import BaseModel, Field

class TodoCreate(BaseModel):
    """创建待办的入参——自动完成校验、序列化与文档生成。"""
    title: str = Field(min_length=1, max_length=100, examples=["学 FastAPI"])
    done: bool = False

class TodoRead(TodoCreate):
    """对外输出的完整模型：继承入参字段并补充 id。"""
    id: int

@app.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate) -> TodoRead:
    # payload 已经过 Pydantic 校验：title 保证是 1-100 字符
    new_id = max(_TODOS, default=0) + 1
    todo = TodoRead(id=new_id, **payload.model_dump())
    _TODOS[new_id] = todo.model_dump()
    return todo
```

**要点**：

- 请求体模型通过参数注解声明，无需手动解析 JSON
- `response_model` 起到"出口过滤"作用：多余字段不会泄露给客户端
- Pydantic v2 使用 `model_dump()`，替代 v1 的 `dict()`

## 4. 查询参数：列表与过滤

```python
@app.get("/todos", response_model=list[TodoRead])
def list_todos(
    done: bool | None = None,   # 可选过滤条件：?done=true
    limit: int = 10,            # 分页大小
    offset: int = 0,            # 分页偏移
) -> list[TodoRead]:
    items = [TodoRead(**t) for t in _TODOS.values()]
    if done is not None:                          # 仅在显式传入时过滤
        items = [t for t in items if t.done == done]
    return items[offset : offset + limit]
```

**要点**：不属于路径的标量参数自动成为查询参数；`bool | None` 表达"可传可不传"。

## 5. 自动文档：/docs 与 /redoc

| 地址 | 用途 |
|------|------|
| `http://127.0.0.1:8000/docs` | Swagger UI，可在页面里直接发请求调试 |
| `http://127.0.0.1:8000/redoc` | ReDoc 风格阅读版 |
| `http://127.0.0.1:8000/openapi.json` | 机器可读的 OpenAPI 3 规范 |

- 文档由**类型注解 + Pydantic 模型 + 文档字符串**自动生成，无需手写
- 在 `FastAPI(title=..., version=...)` 中维护元信息；示例值用 `Field(examples=[...])`
- 前后端协作时可直接把 `openapi.json` 交给客户端代码生成器

## ✅ 最佳实践

- **同步端点用 `def`**：FastAPI 会放进线程池，兼容阻塞库；`async def` 里不要混用阻塞调用（深入见[异步并发模型](../advanced-topics/performance/01-async-python.md)）
- 入参/出参模型分开设（`TodoCreate` / `TodoRead`），避免字段随意外泄
- 状态码用 `status` 常量而非魔法数字

## ❓ 常见问题

**Q1: 请求一直返回 422？**
请求体/参数与模型声明不符。查看 `/docs` 中自动生成的 Schema，与实际发送的 JSON 对照排查。

**Q2: `def` 和 `async def` 端点怎么选？**
用同步库（多数传统数据库驱动）就用 `def`；全异步栈（asyncpg、redis.asyncio、httpx.AsyncClient）才用 `async def`。

---

## 🔗 相关文档

- 📖 **[FastAPI 核心速查](../reference/framework-essentials/01-fastapi-essentials.md)** — 本篇所有概念的字典级完整参考
- 📖 **[类型注解](../reference/language-concepts/05-typing-annotations.md)** — 理解 Pydantic/FastAPI 校验的地基
- 📄 **[FastAPI 进阶](./02-fastapi-advanced.md)** — 依赖注入、后台任务与中间件
- 🚀 **[入门项目：TODO REST API](../projects/01-todo-api.md)** — 用本篇知识完成完整小项目
- 📄 **[环境搭建](../basics/01-environment-setup.md)** — uv 与现代工具链基础
- 📖 **[语法速查](../reference/quick-references/01-python-cheatsheet.md)** — 写示例时随查随用
