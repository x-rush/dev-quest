# FastAPI 入门 — 路由、Pydantic 模型与自动文档

## 先看框架承担哪部分职责

**FastAPI 入门**：函数参数与类型注解被框架读取，用于路由绑定和校验。Pydantic 在边界处理数据，普通 Python 函数不会因此自动变成强制类型系统。

**最小练习与预期结果**：分别提交合法、缺字段与错类型数据；观察校验响应，再测试纯业务函数的错误处理。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 用 FastAPI 从零构建一个类型安全的 REST API，掌握路由声明、Pydantic 请求/响应模型与自动生成的交互式文档
>
> **目标读者**: 已完成本模块 basics 入门路径、想用 Python 做 Web 后端的开发者
>
> **前置知识**: 类型注解（[reference 05](../reference/language-concepts/05-typing-annotations.md)）、uv 项目管理（[basics 01](../basics/01-environment-setup.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#FastAPI` `#Pydantic` `#REST` `#自动文档` |
| **更新日期** | `2026年9月` |

</details>

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

# 先保存第 2 节 main.py，再启动开发服务器（热重载）
uv run uvicorn main:app --reload
```

## 2. 第一个路由：路径参数

```python
# main.py
from fastapi import FastAPI, HTTPException, Query, status

app = FastAPI(title="待办服务", version="0.1.0")

# 演示用内存存储，后续项目会换成数据库
_TODOS: dict[int, dict] = {1: {"id": 1, "title": "学 FastAPI", "done": False}}

@app.get("/health")
def health() -> dict[str, str]:
    """健康检查端点，文档字符串会显示在 /docs 中。"""
    return {"status": "ok"}

@app.get("/todos/{todo_id}")
async def read_todo(todo_id: int) -> dict:
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
from pydantic import BaseModel, ConfigDict, Field

class TodoCreate(BaseModel):
    """创建待办的入参——自动完成校验、序列化与文档生成。"""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=100, examples=["学 FastAPI"])
    done: bool = False

class TodoRead(TodoCreate):
    """对外输出的完整模型：继承入参字段并补充 id。"""
    id: int

@app.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(payload: TodoCreate) -> TodoRead:
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

第 3、4 节代码按顺序追加到同一个 `main.py`。演示存储仅属于一个进程，重启即丢失；内存读写端点使用不含 `await` 的短 `async def`，避免线程池中的多个请求交错分配 ID。这不替代数据库事务：接入阻塞 I/O 后须改为线程池或异步驱动，并由数据库保障 ID 与并发更新。`response_model` 还会校验输出；若服务端产生错误类型，应修正实现，不能把响应校验失败包装成客户端错误。

## 4. 查询参数：列表与过滤

```python
@app.get("/todos", response_model=list[TodoRead])
async def list_todos(
    done: bool | None = None,   # 可选过滤条件：?done=true
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[TodoRead]:
    items = [TodoRead(**t) for t in _TODOS.values()]
    if done is not None:                          # 仅在显式传入时过滤
        items = [t for t in items if t.done == done]
    return items[offset : offset + limit]
```

**要点**：不属于路径的标量参数自动成为查询参数；`bool | None` 表达"可传可不传"。

用 `/docs` 验收：创建 `{"title":"学路由"}` 返回 201 与 ID；查询该 ID 返回相同标题；`{"title":"   "}`、`?limit=0`、`?offset=-1` 返回 422；未知 ID 返回 404。`int` 只检查类型，`Query` 中的上下界才阻止负索引和无界分页。完整自动化练习见 [TODO API](../projects/01-todo-api.md)。

参数声明与校验的官方说明见 [FastAPI Query 校验](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/)。

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

同步端点可通过框架的线程池运行阻塞代码，async 端点则应等待可异步的操作；随意把同步库调用放进 async 函数并不会自动变非阻塞。线程池同样有容量与排队成本，应在实际负载下观察。

输入模型只允许客户端应填写的字段，输出模型只暴露需要返回的字段，防止数据库内部属性意外泄漏。校验成功还不代表有权操作资源，用跨用户访问和非法输入验证服务端边界。

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


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
