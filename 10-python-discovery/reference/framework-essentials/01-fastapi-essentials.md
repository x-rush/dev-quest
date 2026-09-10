# FastAPI 核心速查 — 路由 / 依赖 / Pydantic / 异步

## 概述

FastAPI 是注解驱动的现代 Web 框架：类型注解同时充当参数校验、文档生成与编辑器提示。本条目覆盖路由、参数注入、依赖系统、Pydantic 模型与异步实践的完整核心面。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#FastAPI` `#Pydantic` `#异步` `#Web` `#API` |
| **更新日期** | `2026年9月` |

## 最小应用

```python
from fastapi import FastAPI

app = FastAPI(title="书签服务")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

# 运行：uv run uvicorn main:app --reload；自动文档 /docs (Swagger) 与 /redoc
```

---

## 1. 路由与路径参数

```python
from fastapi import HTTPException, status

@app.get("/bookmarks/{bookmark_id}")
def get_bookmark(bookmark_id: int) -> dict:     # 注解 int → 自动类型转换与校验
    if bookmark_id not in DB:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="书签不存在")
    return DB[bookmark_id]
```

**要点**: 路径参数类型来自函数签名；不匹配返回 422；`status_code` 显式声明成功码（如 `@app.put(..., status_code=204)`）。

---

## 2. 查询参数与请求体

```python
from pydantic import BaseModel, Field

class BookmarkIn(BaseModel):
    url: str = Field(pattern=r"^https?://")
    title: str = Field(min_length=1, max_length=100)
    tags: list[str] = []

@app.post("/bookmarks", status_code=201)
def create(bookmark: BookmarkIn,                # 请求体：Pydantic 模型
           q: str | None = None,                # 标量参数默认是查询参数
           x_token: str = Header()) -> BookmarkIn:
    return bookmark

# 分页：offset: int = Query(0, ge=0)、limit: int = Query(20, le=100)
```

**要点**: Body 参数用 Pydantic 模型；`Query`/`Header`/`Path` 提供约束与校验元数据。

---

## 3. 依赖注入（FastAPI 的灵魂）

**定义**: `Depends` 声明"这个端点需要什么"，框架负责构造并缓存。

```python
from fastapi import Depends, HTTPException

async def get_current_user(token: str = Depends(HTTPBearer())) -> User:
    if (user := await auth.verify(token.credentials)) is None:
        raise HTTPException(status_code=401, detail="无效令牌")
    return user

def get_db():
    db = SessionLocal()
    try:
        yield db          # yield 前是准备，yield 是注入值，之后是清理
    finally:
        db.close()

@app.get("/me")
def read_me(user: User = Depends(get_current_user)):
    return user

# 依赖工厂：def pagination(offset: int = 0, limit: int = 20): ...
# 以 Page = Annotated[dict, Depends(pagination)] 在任意端点复用
```

**要点**: 依赖可嵌套（依赖树自动解析），同一请求内同依赖只执行一次；生成器依赖 = with 语义的资源生命周期管理。

---

## 4. 异步路由

```python
import httpx

@app.get("/proxy")
async def proxy(url: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:   # 真异步 I/O
        return (await client.get(url)).json()
```

**规则**:
- `def` 路由跑在线程池，`async def` 跑在事件循环——按数据库驱动的同步/异步类型选择
- `async def` 内禁止阻塞调用（`requests`/`time.sleep`）；并发批量请求用 `asyncio.gather`

---

## 5. Pydantic 响应与模型配置

```python
from pydantic import BaseModel, ConfigDict

class BookmarkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # 允许从 ORM 对象转换
    url: str
    title: str

@app.get("/bookmarks", response_model=list[BookmarkOut])
def list_all() -> list[BookmarkOut]: ...
```

**要点**: `response_model` 控制输出形状（自动过滤多余字段、生成文档）；输入/输出分离模型是标准实践。

---

## 6. 中间件、异常处理与项目组织

```python
from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse

class BusinessError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code, self.message = code, message

@app.middleware("http")                          # await 前后 = 请求前/响应后钩子
async def add_timing(request: Request, call_next):
    return await call_next(request)

@app.exception_handler(BusinessError)            # 自定义异常 → 统一 JSON 响应
async def business_handler(request: Request, exc: BusinessError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"code": exc.code, "msg": exc.message})

bookmarks = APIRouter(prefix="/bookmarks", tags=["书签"])   # main.py: include_router 挂载
@bookmarks.get("/")
def list_bookmarks(): ...
```

标准分层：`routers/`（路由）、`schemas/`（Pydantic 模型）、`dependencies.py`（依赖）、`services/`（业务）。

---

## 陷阱速查表

| 陷阱 | 说明 |
|------|------|
| `async def` 里写阻塞调用 | 冻结事件循环，全服务卡死 |
| 忘 `response_model` | 敏感字段（密码哈希）直接泄漏 |
| 依赖里吞异常 | 依赖抛 HTTPException 才会转 4xx |
| `--reload` 上生产 | 仅开发用；生产 uvicorn + gunicorn 多 worker |

---

## 🔗 相关文档

- 📄 **[typing 注解全表](../language-concepts/05-typing-annotations.md)** — Pydantic 校验的类型学基础
- 📄 **[Django 与 Flask 速查](./02-django-flask.md)** — 另两大 Web 框架对照
- 📄 **[高级特性](../../basics/07-advanced-features.md)** — asyncio 与装饰器的前置知识
