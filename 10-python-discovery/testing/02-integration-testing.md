# 集成测试 — TestClient 与测试数据库

> **文档简介**: 对 FastAPI 应用做请求级集成测试：TestClient / httpx AsyncClient、依赖覆盖，以及用测试数据库验证完整数据流
>
> **目标读者**: 已会单元测试、想验证 API 整体行为的开发者
>
> **前置知识**: [单元测试](./01-unit-testing.md)、[生态集成](../frameworks/03-ecosystem-integration.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#TestClient` `#httpx` `#集成测试` `#测试数据库` |
| **更新日期** | `2026年9月` |

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

client = TestClient(app)      # 基于 httpx，无需启动真实服务器

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_create_todo():
    r = client.post("/todos", json={"title": "写集成测试"})
    assert r.status_code == 201
```

**要点**：请求走完整 ASGI 栈（中间件、依赖、异常处理器都生效），但不出网络——快且稳定。

## 2. 异步客户端：httpx.AsyncClient

```python
import pytest
from httpx import ASGITransport, AsyncClient
from main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
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
from db.orm import Base
from db.session import get_session
from main import app

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"   # 绝不指向开发/生产库

@pytest.fixture
async def db_engine():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)   # 建表
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)     # 清理
    await engine.dispose()

@pytest.fixture
async def client(db_engine):
    maker = async_sessionmaker(db_engine, expire_on_commit=False)

    async def override_session():
        async with maker() as s:
            yield s

    app.dependency_overrides[get_session] = override_session
    yield
    app.dependency_overrides.clear()

async def test_user_flow(client):
    await client.post("/users/register",
                      json={"email": "a@b.c", "password": "secret123"})
    r = await client.post("/login",
                          json={"email": "a@b.c", "password": "secret123"})
    assert r.status_code == 200
```

**要点**：

- fixture 建表 → 测试 → 删表，保证每轮从干净状态开始，可重复
- 测试代码与生产代码共用同一依赖入口（`get_session`），所以才能整体替换
- 纯内存库可用 `"sqlite+aiosqlite://"` 配 `StaticPool`，更快但注意连接共享

## 5. 组织建议

- 单元测试快而多（秒级全量跑），集成测试少而全（只覆盖关键流程）
- CI 中分开 job 运行，失败定位更清晰（见[CI/CD](../deployment/02-ci-cd-pipelines.md)）
- 第三方 HTTP API 不进集成测试——用 [Mock](./03-mocking-testing.md) 拦截

## ❓ 常见问题

**Q1: 集成测试要连真实 PostgreSQL 吗？**
关键方言差异（JSON 字段、事务行为）建议用 testcontainers 起真库验证；日常回归用 SQLite 足够。

**Q2: 测试间数据互相污染怎么办？**
每个测试走建表/删表 fixture，或每测试开启事务后回滚（`SAVEPOINT` 方案）。

---

## 🔗 相关文档

- 🧪 **[单元测试](./01-unit-testing.md)** — fixture 与参数化的基础
- 🧪 **[Mock 测试](./03-mocking-testing.md)** — 拦截第三方 HTTP 调用
- 📄 **[生态集成](../frameworks/03-ecosystem-integration.md)** — 被替换的 get_session 依赖来源
- 🚀 **[项目：短链接服务](../projects/02-url-shortener.md)** / **[生产级应用](../projects/04-production-fastapi-app.md)** — 实战应用场景
