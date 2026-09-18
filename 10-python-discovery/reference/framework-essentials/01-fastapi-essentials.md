# FastAPI 核心速查 — 路由 / 依赖 / Pydantic / 异步

## 概述

FastAPI 是注解驱动的现代 Web 框架：类型注解同时充当参数校验、文档生成与编辑器提示。本条目覆盖路由、参数注入、依赖系统、Pydantic 模型与异步实践的完整核心面。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#FastAPI` `#Pydantic` `#异步` `#Web` `#API` |
| **更新日期** | `2026年9月` |

</details>

后续各节默认是独立的局部片段：DB、User、auth、SessionLocal 等应用对象须由项目提供，不可直接串成一个文件执行。文末提供无这些依赖的完整请求实验。

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
from fastapi import Header, Query
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
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
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

**要点**: 依赖可嵌套（依赖树自动解析），同一请求内相同依赖通常复用缓存；use_cache=False 等配置会改变行为；生成器依赖 = with 语义的资源生命周期管理。

---

## 4. 异步路由

```python
import httpx

@app.get("/proxy")
async def proxy() -> dict:
    # 教学固定上游，避免把任意用户 URL 变成服务器请求目标。
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get("https://api.github.com/repos/fastapi/fastapi")
        response.raise_for_status()
        return response.json()
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
| 直接返回含敏感字段的对象 | 返回注解或 response_model 可约束输出，也可显式构造响应；必须验证敏感字段确实被排除 |
| 依赖里吞异常 | 只捕获能够处理的错误；HTTPException 或配置的异常处理器都可决定响应，其他异常通常成为服务端错误 |
| 把开发启动方式直接用于部署 | reload 用于开发；生产进程数与进程管理方式按部署环境选择，不要求固定搭配某个管理器 |

---

<!-- full-library-explanation -->
## 可独立运行的请求校验实验

前置知识是 HTTP 路径、JSON 和 Python 注解。请求进入 FastAPI 后先匹配路由，再解析参数和模型，随后执行处理器；输出模型负责描述响应形状。业务权限与持久化并不会因为声明了类型而自动完成。

安装 FastAPI、httpx 和 pytest 后，将下列完整实验保存为 `test_fastapi_boundary.py`，执行 `python -m pytest test_fastapi_boundary.py -q`。无需启动网络端口。

```python
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI()

class Item(BaseModel):
    title: str = Field(min_length=1, max_length=30)

@app.post("/items", response_model=Item, status_code=201)
def create(item: Item):
    if not item.title.strip():
        raise HTTPException(status_code=422, detail="blank title")
    return Item(title=item.title.strip())

def test_valid():
    with TestClient(app) as client:
        response = client.post("/items", json={"title": " learn "})
        assert response.status_code == 201
        assert response.json() == {"title": "learn"}

def test_invalid():
    with TestClient(app) as client:
        assert client.post("/items", json={"title": ""}).status_code == 422
        assert client.post("/items", json={"title": "   "}).status_code == 422
```

预期 2 个测试通过。空字符串被字段约束拒绝，纯空白由业务规则拒绝，正常输入被清理后返回。练习：增加独立读取端点后再称为“创建并保存”；目前这里只演示验证和响应，没有持久化，不应把 201 理解为数据库已写入。

## 🔗 相关文档

- 📄 **[typing 注解全表](../language-concepts/05-typing-annotations.md)** — Pydantic 校验的类型学基础
- 📄 **[Django 与 Flask 速查](./02-django-flask.md)** — 另两大 Web 框架对照
- 📄 **[高级特性](../../basics/07-advanced-features.md)** — asyncio 与装饰器的前置知识


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
