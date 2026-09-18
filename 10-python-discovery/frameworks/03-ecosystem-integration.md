# 生态集成 — SQLAlchemy 2.0、数据库与 Redis

## 先看框架承担哪部分职责

**SQLAlchemy 与 Redis**：Session 表达一段数据库工作，事务负责提交边界；同步与异步 API 要与执行模型匹配。缓存的数据不自动参加 SQL 事务。

**最小练习与预期结果**：模拟提交失败并回滚，再重新查询；缓存不可用时按既定策略处理，避免留下半成功状态。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 把 FastAPI 连上真实存储：SQLAlchemy 2.0 异步 ORM 访问数据库、Redis 做缓存与计数、pydantic-settings 管配置、Alembic 管迁移
>
> **目标读者**: 需要给 API 接入数据库与缓存的开发者
>
> **前置知识**: [FastAPI 进阶（yield 依赖）](./02-fastapi-advanced.md)、异步基础（[basics 07](../basics/07-advanced-features.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#SQLAlchemy` `#Redis` `#Alembic` `#pydantic-settings` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 配置 SQLAlchemy 2.0 异步引擎与会话工厂
- ✅ 用 `Mapped` / `mapped_column` 声明 ORM 模型
- ✅ 以 yield 依赖注入会话，自动提交/回滚
- ✅ 用 `redis.asyncio` 实现缓存与原子计数
- ✅ 用 pydantic-settings 集中管理连接配置，用 Alembic 管表结构

---

## 1. 安装依赖

```bash
uv add sqlalchemy aiosqlite redis pydantic-settings   # SQLite 起步
uv add asyncpg                                        # 生产 PostgreSQL 时加装
```

## 2. 配置：pydantic-settings

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./app.db"
    redis_url: str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env"}   # 环境变量优先于默认值，.env 只进本地

settings = Settings()
```

**要点**：连接串等敏感配置从环境变量注入（密钥管理细则见[安全实践](../advanced-topics/security/01-security-practices.md)）。

## 3. SQLAlchemy 2.0：声明 ORM 模型

```python
# db/orm.py
from datetime import datetime
from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

**要点**：2.0 风格用 `Mapped[类型]` 注解声明列，类型即模式；字段级语法见[生态库速查](../reference/library-guides/02-ecosystem-libs.md)。

## 4. 引擎与会话依赖

```python
# db/session.py
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    """yield 依赖：请求开始拿会话，结束时按成败提交或回滚。"""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**要点**：会话粒度 = 请求粒度，一个请求一个会话，由依赖自动清理（生命周期机制见[FastAPI 进阶](./02-fastapi-advanced.md)）。

## 5. 路由中使用会话

```python
from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from db.session import get_session
from db.orm import Todo
from schemas import TodoCreate, TodoRead

SessionDep = Annotated[AsyncSession, Depends(get_session)]
router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("", response_model=list[TodoRead])
async def list_todos(session: SessionDep) -> list[TodoRead]:
    rows = await session.scalars(select(Todo).order_by(Todo.id))
    return list(rows)

@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(payload: TodoCreate, session: SessionDep) -> TodoRead:
    todo = Todo(**payload.model_dump())
    session.add(todo)
    await session.flush()      # 送出 INSERT 以拿到自增 id（commit 由依赖统一做）
    return todo
```

**要点**：

- SQL 一律用 `select()` 表达式构造，参数自动绑定，杜绝 SQL 注入（原理见[安全实践](../advanced-topics/security/01-security-practices.md)）
- `scalars()` 返回 ORM 对象流；`await session.get(Todo, id)` 按主键取单条

## 6. 表结构管理：建表与 Alembic

```python
# 开发期快速建表（生产改用迁移）
async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

```bash
uv add --dev alembic
uv run alembic init -t async migrations          # 异步模板
# 编辑 migrations/env.py：target_metadata 指向 Base.metadata
uv run alembic revision --autogenerate -m "add todos"
uv run alembic upgrade head
```

## 7. Redis：缓存与计数

```python
# core/redis.py
import redis.asyncio as redis
from core.config import settings

def create_redis() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)
```

```python
# 连接池挂到 app.state（lifespan 见 FastAPI 进阶第 5 节）

# 用法一：缓存旁路
@app.get("/stats")
async def stats(request: Request) -> dict:
    r = request.app.state.redis
    cached = await r.get("stats:hits")             # 先查缓存
    if cached is None:
        cached = await compute_hits()              # 未命中回源计算
        await r.set("stats:hits", cached, ex=60)   # 60 秒过期
    return {"hits": int(cached)}

# 用法二：原子计数（并发安全）
await r.incr(f"url:abc123:clicks")
```

**要点**：`decode_responses=True` 让值直接是 `str`；INCR 是原子操作，计数场景禁用"读-加-写"。

## ✅ 最佳实践

列表查询先约定分页方式和上限，offset 与游标各有适用场景，不能无条件强制同一种。遇到 N+1 时记录实际 SQL 与访问关系，选择 selectinload、join 等加载策略并比较结果数量和查询成本。

迁移记录随代码管理，验证空库创建和旧版本数据升级。upgrade head 再运行通常不应重复应用已记录迁移，但这不等于每条迁移 SQL 天然可随意重放；失败恢复需要具体方案。

## ❓ 常见问题

**Q1: 为什么要 `expire_on_commit=False`？**
默认提交后访问属性会再次查询；关闭后对象保持可用，适配"提交后还要序列化返回"的 Web 场景。

**Q2: 测试时怎么替换数据库？**
测试用独立 SQLite 文件/内存库 + `app.dependency_overrides[get_session]`，见[集成测试](../testing/02-integration-testing.md)。

---

## 🔗 相关文档

- 📖 **[生态库速查](../reference/library-guides/02-ecosystem-libs.md)** — SQLAlchemy/Redis API 字典
- 📄 **[FastAPI 进阶](./02-fastapi-advanced.md)** — yield 依赖与 lifespan 机制
- 🚀 **[项目：短链接服务](../projects/02-url-shortener.md)** — Redis 实战
- 🧪 **[集成测试](../testing/02-integration-testing.md)** — 测试数据库与依赖覆盖
- 🎓 **[asyncio 异步并发模型](../advanced-topics/performance/01-async-python.md)** — 异步栈底层原理
- 🚀 **[容器化部署](../deployment/01-docker-deployment.md)** — Compose 编排数据库与缓存


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
