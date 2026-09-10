# 终极项目 — 生产级 FastAPI 应用

> **文档简介**: 把前面所有知识组装成一套生产就绪的 FastAPI 工程：分层架构、JWT 认证、数据库迁移、测试、容器化与可观测性
>
> **目标读者**: 完成 ⭐/⭐⭐ 项目、准备把服务推上生产的开发者
>
> **前置知识**: 本模块 frameworks / testing / deployment 三个目录的全部 ⭐⭐ 文档

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#生产级` `#架构` `#JWT` `#Docker` `#可观测性` |
| **更新日期** | `2026年9月` |

## 🎯 生产就绪清单（本项目交付物）

- 分层：api → services → repositories → models（原理见[项目分层与领域建模](../advanced-topics/architecture/01-project-architecture.md)）
- 配置/密钥：pydantic-settings + 环境变量，无硬编码
- 认证：JWT + bcrypt 密码哈希
- 数据：SQLAlchemy 2.0 异步 + Alembic 迁移
- 质量：pytest 全绿 + ruff/mypy 通过（CI 门禁）
- 运行：Docker 多阶段构建 + structlog + Prometheus 指标

## 1. 工程结构

```text
app/
├── main.py               # 组装：lifespan、路由、中间件
├── core/
│   ├── config.py          # pydantic-settings
│   └── security.py        # JWT + 密码哈希
├── api/
│   └── routes_users.py    # 薄路由：HTTP ↔ 模型转换
├── services/
│   └── user_service.py    # 业务规则
├── repositories/
│   └── user_repo.py       # 数据访问（唯一 SQL 所在地）
├── models/
│   └── user.py            # ORM 实体
└── schemas/
    └── user.py            # Pydantic 入参/出参
tests/
alembic/
Dockerfile
pyproject.toml
uv.lock
```

**分层规则**：依赖方向单向向下，上层知道下层、下层不知道上层；业务规则只住在 service 层。

## 2. 配置与安全基座

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "dev"
    database_url: str = "sqlite+aiosqlite:///./dev.db"
    jwt_secret: str                 # 无默认值：缺失即启动失败，问题尽早暴露
    jwt_expire_minutes: int = 30

settings = Settings()               # 生产环境变量注入，详见安全实践
```

```python
# core/security.py
from datetime import UTC, datetime, timedelta
import bcrypt
import jwt
from core.config import settings

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_token(sub: str) -> str:
    now = datetime.now(UTC)
    payload = {"sub": sub, "iat": now,
               "exp": now + timedelta(minutes=settings.jwt_expire_minutes)}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
```

注入防护与密钥轮换等细则见[安全实践](../advanced-topics/security/01-security-practices.md)。

## 3. 仓储与服务层

```python
# repositories/user_repo.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))

    async def create(self, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        self.session.add(user)
        await self.session.flush()   # 拿自增 id，commit 由会话依赖统一处理
        return user
```

```python
# services/user_service.py
from fastapi import HTTPException, status
from core.security import hash_password
from repositories.user_repo import UserRepository

class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def register(self, email: str, password: str) -> None:
        if await self.repo.get_by_email(email):
            raise HTTPException(status.HTTP_409_CONFLICT, "邮箱已注册")
        if len(password) < 8:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "密码过短")
        await self.repo.create(email, hash_password(password))
```

## 4. 路由与依赖组装

```python
# api/routes_users.py
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session
from repositories.user_repo import UserRepository
from schemas.user import UserCreate
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(session: Annotated[AsyncSession, Depends(get_session)]) -> UserService:
    return UserService(UserRepository(session))   # 组合根：在此选择具体实现

@router.post("/register", status_code=201)
async def register(
    payload: UserCreate,
    svc: Annotated[UserService, Depends(get_user_service)],
) -> dict:
    await svc.register(payload.email, payload.password)
    return {"ok": True}
```

**要点**：service/repo 全部经 `Depends` 构造，测试时用 `app.dependency_overrides` 整体替换（见[集成测试](../testing/02-integration-testing.md)）。

## 5. 迁移与部署

```bash
uv run alembic revision --autogenerate -m "users"
uv run alembic upgrade head
```

```dockerfile
# 多阶段构建详解见容器化部署
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
USER nobody
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

## 6. 上线前检查清单

- [ ] ruff check / mypy / pytest 在 CI 全绿（[CI/CD](../deployment/02-ci-cd-pipelines.md)）
- [ ] structlog 结构化日志 + 请求 ID（[可观测性](../deployment/03-observability.md)）
- [ ] `/health` 健康检查 + Prometheus `/metrics`
- [ ] 密钥全部来自环境变量，`uv.lock` 已提交
- [ ] 迁移可重复执行，且有回滚方案
- [ ] 异步端点无阻塞调用（排查见[性能剖析](../advanced-topics/performance/02-profiling-optimization.md)）

---

## 🔗 相关文档

- 🎓 **[项目分层与领域建模](../advanced-topics/architecture/01-project-architecture.md)** — 第 1 节结构的原理解释
- 🎓 **[安全实践](../advanced-topics/security/01-security-practices.md)** — 第 2 节安全基座的展开
- 🚀 **[容器化部署](../deployment/01-docker-deployment.md)** / **[CI/CD](../deployment/02-ci-cd-pipelines.md)** / **[可观测性](../deployment/03-observability.md)** — 部署三部曲
- 🧪 **[集成测试](../testing/02-integration-testing.md)** — 分层架构的测试策略
- 📖 **[FastAPI 核心速查](../reference/framework-essentials/01-fastapi-essentials.md)** — 全程随查
