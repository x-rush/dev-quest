# 集成测试 — TestClient 与测试数据库

> **文档简介**: 对 FastAPI 应用做请求级集成测试：TestClient / httpx AsyncClient、依赖覆盖，以及用测试数据库验证完整数据流
>
> **目标读者**: 已会单元测试、想验证 API 整体行为的开发者
>
> **前置知识**: [单元测试](./01-unit-testing.md)、[生态集成](../frameworks/03-ecosystem-integration.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#TestClient` `#httpx` `#集成测试` `#测试数据库` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 TestClient 无服务器地测试 FastAPI 端点
- ✅ 异步栈用 httpx.AsyncClient + ASGITransport
- ✅ 用 `dependency_overrides` 替换认证/数据库依赖
- ✅ 搭建独立、可重复的测试数据库

---

## 1. TestClient：最短路径

```python
from fastapi.testclient import TestClient
from main import app

import pytest

@pytest.fixture
def client():
    with TestClient(app) as active_client:
        yield active_client

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_create_todo(client):
    r = client.post("/todos", json={"title": "写集成测试"})
    assert r.status_code == 201
```

**要点**：请求走完整 ASGI 栈（中间件、依赖、异常处理器都生效），但不出网络——快且稳定。

## 2. 异步客户端：httpx.AsyncClient

```python
import pytest
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager
from main import app

pytestmark = pytest.mark.anyio

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c

async def test_redirect(client):
    r = await client.get("/abc", follow_redirects=False)
    assert r.status_code == 307
```

**要点**：异步栈（SQLAlchemy async、redis.asyncio）的端到端链路要用 `AsyncClient + ASGITransport`，确保跑在同一个事件循环里。

## 3. 依赖覆盖：替换真实实现

```python
from main import app, get_current_user

def fake_user():
    return {"name": "tester", "role": "admin"}

app.dependency_overrides[get_current_user] = fake_user
# ... 运行测试 ...
app.dependency_overrides.clear()   # 用 fixture 的 yield 后段保证清理
```

**要点**：比逐个 mock 更可靠——替换的是整个依赖函数，路由行为保持完全真实；被测代码无需任何改动，这正是依赖注入的设计回报（见[FastAPI 进阶](../frameworks/02-fastapi-advanced.md)）。

## 4. 测试数据库：独立且可重复

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager
from sqlalchemy.engine import URL

pytestmark = pytest.mark.anyio

@pytest.fixture
def anyio_backend():
    return "asyncio"
from db.orm import Base
from db.session import get_session
from main import app

TEST_DB_URL = None  # 实际 URL 在 fixture 中从 tmp_path 生成

@pytest.fixture
async def db_engine(tmp_path):
    url = URL.create("sqlite+aiosqlite", database=str(tmp_path / "test.db"))
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)   # 建表
    try:
        yield engine
    finally:
        await engine.dispose()  # 临时文件由 pytest 隔离，不对共享数据库执行 drop_all

@pytest.fixture
async def client(db_engine):
    maker = async_sessionmaker(db_engine, expire_on_commit=False)

    async def override_session():
        async with maker() as s:
            yield s

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = override_session
    try:
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as active_client:
                yield active_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)

async def test_user_flow(client):
    await client.post("/users/register",
                      json={"email": "a@b.c", "password": "secret123"})
    r = await client.post("/login",
                          json={"email": "a@b.c", "password": "secret123"})
    assert r.status_code == 200
```

**要点**：

- fixture 使用每个测试独立的临时数据库，建表后执行测试并释放引擎；应用启动逻辑也必须配置为测试环境
- 测试代码与生产代码共用同一依赖入口（`get_session`），所以才能整体替换
- 纯内存库可用 `"sqlite+aiosqlite://"` 配 `StaticPool`，更快但注意连接共享

## 5. 组织建议

- 单元测试快而多（秒级全量跑），集成测试少而全（只覆盖关键流程）
- CI 中分开 job 运行，失败定位更清晰（见[CI/CD](../deployment/02-ci-cd-pipelines.md)）
- 默认回归使用受控第三方响应；另设真实服务的契约或端到端测试时，明确环境、成本和失败分类

## ❓ 常见问题

**Q1: 集成测试要连真实 PostgreSQL 吗？**
关键方言差异（JSON 字段、事务行为）建议用 testcontainers 起真库验证；SQLite 只适合不依赖特定方言与事务语义的用例，不能保证替代目标数据库的回归。

**Q2: 测试间数据互相污染怎么办？**
每个测试走建表/删表 fixture，或每测试开启事务后回滚（`SAVEPOINT` 方案）。

---

<!-- full-library-explanation -->
## 明确测试经过哪些边界

前置是可导入的 ASGI 应用和能够被覆盖的依赖函数。TestClient 与 ASGITransport 可以在进程内执行请求，不包含真实 DNS、TLS、反向代理或网络超时。替换数据库依赖后，测试也没有验证被替换的数据库连接实现；应在报告里说明保留了哪些真实边界。

同步 TestClient 用 with 进入生命周期；HTTPX 的 ASGITransport 本身不触发 lifespan，异步场景需显式管理。下面异步片段使用 pytest-anyio 的标记机制及 asgi-lifespan，需安装 `pytest httpx asgi-lifespan`，并将 anyio_backend 固定为 asyncio；数据库片段另外需要 SQLAlchemy 和 aiosqlite。

练习连续运行用户注册流程两次，每轮从隔离数据库开始，都应得到相同结果。再让注册后的登录断言失败，确认依赖覆盖和引擎仍被释放。若只在测试成功时 clear，下一条测试可能误用上一条的身份或存储。

## 🔗 相关文档

- 🧪 **[单元测试](./01-unit-testing.md)** — fixture 与参数化的基础
- 🧪 **[Mock 测试](./03-mocking-testing.md)** — 拦截第三方 HTTP 调用
- 📄 **[生态集成](../frameworks/03-ecosystem-integration.md)** — 被替换的 get_session 依赖来源
- 🚀 **[项目：短链接服务](../projects/02-url-shortener.md)** / **[生产级应用](../projects/04-production-fastapi-app.md)** — 实战应用场景


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
