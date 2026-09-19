# 入门项目 — TODO REST API

## 分阶段练习与验收

**最小阶段**：先用纯函数定义标题规则，再接 FastAPI 与存储。

**验收结果**：非法请求由边界拒绝，正常创建可查回，不存在返回明确状态。

**扩展顺序**：同步与异步数据库接口不要混用，先测试再加复杂依赖。

本页是完整的内存版练习：依次保存 `schemas.py`、`store.py`、`main.py` 和 `tests/test_api.py` 即可运行。每次服务重启清空数据，多个 worker 不共享数据；它用于学习 HTTP 契约，不用于持久化部署。先通过第 6 节测试，再替换存储。

### 从书签 CLI 进入 HTTP 项目

- **前置**：完成[书签 CLI](../basics/08-first-project.md)的正常添加、非法 URL 与损坏 JSON 保留测试，再阅读[FastAPI 入门](../frameworks/01-fastapi-basics.md)的请求模型和异常处理。
- **本次产物**：按第 2 节新建独立 `todo-api` 工程，保存本页四个文件与测试结果。复用“入口校验、业务操作、存储分离”的思路；书签 JSON 文件和 CLI 的列表序号不迁入待办服务，待办使用服务生成的 ID。
- **变化要能解释**：CLI 用退出码报告失败并把书签写入文件；本页用 HTTP 状态码报告失败，并暂时只存内存。CLI 重启可查回与本页重启清空是不同阶段的约定，不能拿持久化验收替代 HTTP 验收。
- **验收步骤**：先运行第 6 节测试并确认全部通过；再手动完成“创建 → 按返回 ID 查询 → 删除 → 再查询 404”，保存状态码和响应；无效 PATCH 应返回 422 且原记录不变。关闭服务后重新启动，确认记录清空并记录这一限制。
- **失败回查**：导入失败先核对第 2 节目录和当前工作目录；422 与预期不符时回查 `schemas.py`；状态串到其他测试时回查 `clean_store`；重启丢失在本阶段属于预期，不应靠复制 CLI 文件写入代码来掩盖。
- **下一步**：完成上述检查后进入[短链接服务](./02-url-shortener.md)，先读其 Redis 配置与 lifespan，再验收存储连接、创建和跳转；JWT 与部署留到存储行为通过后。

这里列出的是学习者需在目标环境完成的桥接验收；本页既有 12 项测试的验证记录仅覆盖下方内存 API，不证明 CLI、Redis 或部署链路已通过。

> **文档简介**: 综合运用 FastAPI 基础知识，从零实现一个带完整 CRUD、过滤分页与测试的 TODO API
>
> **目标读者**: 学完 FastAPI 入门后想动手实践的开发者
>
> **前置知识**: [FastAPI 入门](../frameworks/01-fastapi-basics.md)、[单元测试](../testing/01-unit-testing.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#FastAPI` `#CRUD` `#pytest` `#入门项目` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 项目目标

- 功能：待办的增删改查 + 完成状态切换 + 过滤分页
- 质量门：`pytest` 全绿、`/docs` 可交互；正常请求与非法请求都应有可断言结果

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
from pydantic import BaseModel, ConfigDict, Field, model_validator

class TodoBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=100)
    done: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    """PATCH 语义：所有字段可选，只更新显式传入的字段。"""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_empty_or_null(cls, data):
        if isinstance(data, dict) and (not data or any(v is None for v in data.values())):
            raise ValueError("至少提供一个字段，且字段不能为 null")
        return data

class TodoRead(TodoBase):
    id: int
```

“可以省略”与“允许 null”是两回事。`exclude_unset=True` 只省略未提交的字段，无法自动拒绝显式的 `null`。这里先拒绝空对象与 null，再校验字段，否则 `{"title": null}` 会污染存储，随后在响应校验时变成服务端错误。

`mode="before"` 接收尚未转换的输入，因此先判断是否为字典，并返回原值交给后续字段校验；参见 [Pydantic 模型校验器](https://docs.pydantic.dev/latest/concepts/validators/)。

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
from fastapi import FastAPI, HTTPException, Query, Response, status
from schemas import TodoCreate, TodoRead, TodoUpdate
import store

app = FastAPI(title="TODO API")

@app.get("/todos", response_model=list[TodoRead])
async def list_todos(done: bool | None = None, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    return store.list_todos(done)[offset : offset + limit]

@app.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(payload: TodoCreate):
    return store.create(payload)

@app.get("/todos/{todo_id}", response_model=TodoRead)
async def read_todo(todo_id: int):
    todo = store.get(todo_id)
    if todo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "待办不存在")
    return todo

@app.patch("/todos/{todo_id}", response_model=TodoRead)
async def update_todo(todo_id: int, payload: TodoUpdate):
    todo = store.update(todo_id, payload)
    if todo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "待办不存在")
    return todo

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_todo(todo_id: int) -> Response:
    if not store.delete(todo_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "待办不存在")
    return Response(status_code=204)
```

此处的 `async def` 处理器只做不含 `await` 的短内存操作，在单个事件循环中不会在分配 ID 的中途切换请求。引入文件或同步数据库 I/O 后不能直接照搬：阻塞 I/O 应移至同步处理器/线程，或者换成真正的异步驱动，并交给数据库生成 ID、处理并发与事务。

## 6. 测试：tests/test_api.py

```python
from fastapi.testclient import TestClient
import pytest
from main import app
import store

@pytest.fixture(autouse=True)
def clean_store():
    store._todos.clear()   # 每个测试从空存储开始
    store._next_id = 1
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


@pytest.mark.parametrize("payload", [{}, {"title": None}, {"done": None}, {"title": "   "}, {"unknown": 1}])
def test_invalid_patch_does_not_mutate(payload):
    tid = client.post("/todos", json={"title": "保留"}).json()["id"]
    assert client.patch(f"/todos/{tid}", json=payload).status_code == 422
    assert client.get(f"/todos/{tid}").json()["title"] == "保留"


@pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1"])
def test_invalid_pagination(query):
    assert client.get(f"/todos?{query}").status_code == 422


def test_delete_has_no_body():
    tid = client.post("/todos", json={"title": "删除我"}).json()["id"]
    response = client.delete(f"/todos/{tid}")
    assert response.status_code == 204 and response.content == b""
    assert client.get(f"/todos/{tid}").status_code == 404
```

运行 `uv run python -m pytest -q`，预期 12 passed。若显示模块无法导入，确认终端位于包含 `main.py` 的项目根目录。

验证记录（2026-09-19）：从本页原样抽取四个 Python 文件，在 Python 3.12.14 与 Python 3.14 容器中均通过 12 项测试；实际依赖为 FastAPI 0.141.1、Pydantic 2.13.5、pytest 9.1.1、httpx 0.28.1。当前 Starlette 1.6.0 会报告 httpx 测试适配器与 AnyIO 别名弃用警告；测试通过不代表依赖无迁移工作，也不涵盖数据库、部署或多 worker 持久化。

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


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
