# 入门项目 — TODO REST API

> **文档简介**: 综合运用 FastAPI 基础知识，从零实现一个带完整 CRUD、过滤分页与测试的 TODO API
>
> **目标读者**: 学完 FastAPI 入门后想动手实践的开发者
>
> **前置知识**: [FastAPI 入门](../frameworks/01-fastapi-basics.md)、[单元测试](../testing/01-unit-testing.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#FastAPI` `#CRUD` `#pytest` `#入门项目` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

- 功能：待办的增删改查 + 完成状态切换 + 过滤分页
- 质量门：`ruff check` 通过、`pytest` 全绿、`/docs` 可交互

## 1. 需求与接口设计

| 方法 | 路径 | 说明 | 成功码 |
|------|------|------|--------|
| GET | `/todos` | 列表（`?done=&limit=&offset=`） | 200 |
| POST | `/todos` | 创建 | 201 |
| GET | `/todos/{id}` | 详情 | 200 |
| PATCH | `/todos/{id}` | 部分更新 | 200 |
| DELETE | `/todos/{id}` | 删除 | 204 |

## 2. 项目初始化

```bash
uv init --app todo-api && cd todo-api
uv add fastapi "uvicorn[standard]"
uv add --dev pytest httpx
```

## 3. 数据模型：schemas.py

```python
from pydantic import BaseModel, Field

class TodoBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    """PATCH 语义：所有字段可选，只更新显式传入的字段。"""
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None

class TodoRead(TodoBase):
    id: int
```

## 4. 存储层：store.py

```python
"""内存存储：接口按 CRUD 组织，日后可替换为数据库实现。"""
from schemas import TodoCreate, TodoUpdate

_todos: dict[int, dict] = {}
_next_id = 1

def list_todos(done: bool | None = None) -> list[dict]:
    items = list(_todos.values())
    if done is not None:
        items = [t for t in items if t["done"] is done]
    return items

def create(payload: TodoCreate) -> dict:
    global _next_id
    todo = {"id": _next_id, **payload.model_dump()}
    _todos[_next_id] = todo
    _next_id += 1
    return todo

def get(todo_id: int) -> dict | None:
    return _todos.get(todo_id)

def update(todo_id: int, payload: TodoUpdate) -> dict | None:
    todo = _todos.get(todo_id)
    if todo is None:
        return None
    todo.update(payload.model_dump(exclude_unset=True))  # 只取显式传入的字段
    return todo

def delete(todo_id: int) -> bool:
    return _todos.pop(todo_id, None) is not None
```

## 5. 路由层：main.py

```python
from fastapi import FastAPI, HTTPException, status
from schemas import TodoCreate, TodoRead, TodoUpdate
import store

app = FastAPI(title="TODO API")

@app.get("/todos", response_model=list[TodoRead])
def list_todos(done: bool | None = None, limit: int = 50, offset: int = 0):
    return store.list_todos(done)[offset : offset + limit]

@app.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate):
    return store.create(payload)

@app.get("/todos/{todo_id}", response_model=TodoRead)
def read_todo(todo_id: int):
    todo = store.get(todo_id)
    if todo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "待办不存在")
    return todo

@app.patch("/todos/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, payload: TodoUpdate):
    todo = store.update(todo_id, payload)
    if todo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "待办不存在")
    return todo

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int) -> None:
    if not store.delete(todo_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "待办不存在")
```

## 6. 测试：tests/test_api.py

```python
from fastapi.testclient import TestClient
import pytest
from main import app
import store

@pytest.fixture(autouse=True)
def clean_store():
    store._todos.clear()   # 每个测试从空存储开始
    yield

client = TestClient(app)

def test_create_and_read():
    r = client.post("/todos", json={"title": "写测试"})
    assert r.status_code == 201
    todo_id = r.json()["id"]
    assert client.get(f"/todos/{todo_id}").json()["title"] == "写测试"

def test_patch_partial():
    tid = client.post("/todos", json={"title": "A"}).json()["id"]
    r = client.patch(f"/todos/{tid}", json={"done": True})
    assert r.json()["done"] is True and r.json()["title"] == "A"

def test_delete_404():
    assert client.delete("/todos/999").status_code == 404
```

运行 `uv run pytest -q`，预期 3 passed。

## 7. 运行与验证

```bash
uv run uvicorn main:app --reload
# 打开 http://127.0.0.1:8000/docs 手动过一遍五个接口
```

## 8. 扩展练习

- 用 SQLAlchemy 2.0 异步引擎替换内存存储（参照[生态集成](../frameworks/03-ecosystem-integration.md)）
- 加 JWT 认证，按用户隔离数据（参照[安全实践](../advanced-topics/security/01-security-practices.md)）
- Docker 化部署（[容器化](../deployment/01-docker-deployment.md)）

---

## 🔗 相关文档

- 📄 **[FastAPI 入门](../frameworks/01-fastapi-basics.md)** — 本项目用到的全部框架知识
- 🧪 **[单元测试](../testing/01-unit-testing.md)** — 第 6 节测试代码的原理详解
- 🚀 **[项目：短链接服务](./02-url-shortener.md)** — 下一关：引入 Redis 与异步
- 📖 **[FastAPI 核心速查](../reference/framework-essentials/01-fastapi-essentials.md)** — 卡住时查字典
- 📖 **[第一个项目教程](../basics/08-first-project.md)** — basics 侧的入门项目
