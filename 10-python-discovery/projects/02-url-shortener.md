# 进阶项目 — 短链接服务

> **文档简介**: 构建带 Redis 存储与点击统计的短链接服务，练习异步编程、原子计数与 lifespan 资源管理
>
> **目标读者**: 完成 TODO API 后想接触真实存储与并发计数的开发者
>
> **前置知识**: [生态集成（Redis）](../frameworks/03-ecosystem-integration.md)、[FastAPI 进阶](../frameworks/02-fastapi-advanced.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Redis` `#FastAPI` `#异步` `#统计` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

- `POST /urls`：长链接换短码（同一长链幂等复用）
- `GET /{code}`：307 跳转并原子计数
- `GET /urls/{code}/stats`：点击统计查询
- Redis 持久化，重启不丢数据

## 1. 接口设计

| 方法 | 路径 | 请求 | 响应 |
|------|------|------|------|
| POST | `/urls` | `{"url": "https://..."}` | 201 + `{"code", "short_url"}` |
| GET | `/{code}` | — | 307 跳转到长链 |
| GET | `/urls/{code}/stats` | — | 200 + `{"clicks", "target"}` |

## 2. 初始化与配置

```bash
uv init --app url-shortener && cd url-shortener
uv add fastapi "uvicorn[standard]" redis pydantic-settings
uv add --dev pytest httpx
# 本地起 Redis：docker run -d -p 6379:6379 redis:7-alpine
```

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    base_url: str = "http://localhost:8000"

settings = Settings()
```

## 3. 短码生成

```python
# shortener.py
import secrets

ALPHABET = "23456789abcdefghjkmnpqrstuvwxyz"   # 去掉 0/o/1/l 等易混淆字符

def make_code(length: int = 7) -> str:
    """随机短码；7 位 31 进制约 275 亿组合，碰撞概率极低。"""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
```

**要点**：用 `secrets` 而非 `random`——短码对外可见，需防猜测（安全原则见[安全实践](../advanced-topics/security/01-security-practices.md)）。

## 4. 应用与 lifespan

```python
# main.py
import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from config import settings
from shortener import make_code

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.from_url(settings.redis_url, decode_responses=True)
    yield
    await app.state.redis.aclose()

app = FastAPI(title="短链接服务", lifespan=lifespan)
```

## 5. 创建短链接

```python
class UrlCreate(BaseModel):
    url: HttpUrl        # Pydantic 直接校验合法 URL，非法请求 422

@app.post("/urls", status_code=status.HTTP_201_CREATED)
async def create_short_url(payload: UrlCreate, request: Request) -> dict:
    r: redis.Redis = request.app.state.redis
    # 幂等：同一长链命中反向索引则复用已有短码
    code = await r.get(f"rev:{payload.url}")
    if code is None:
        code = make_code()
        await r.set(f"url:{code}", str(payload.url))     # code -> 长链
        await r.set(f"rev:{payload.url}", code)          # 长链 -> code
        await r.set(f"count:{code}", 0)
    return {"code": code, "short_url": f"{settings.base_url}/{code}"}
```

## 6. 跳转与原子计数

```python
@app.get("/{code}")
async def redirect(code: str, request: Request) -> RedirectResponse:
    r = request.app.state.redis
    target = await r.get(f"url:{code}")
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "短码不存在")
    await r.incr(f"count:{code}")   # INCR 原子操作，并发下不丢计数
    return RedirectResponse(target, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@app.get("/urls/{code}/stats")
async def stats(code: str, request: Request) -> dict:
    r = request.app.state.redis
    target = await r.get(f"url:{code}")
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "短码不存在")
    clicks = int(await r.get(f"count:{code}") or 0)
    return {"code": code, "target": target, "clicks": clicks}
```

**要点**：

- 307 保持原请求方法；跳转场景也可权衡 301（可被浏览器缓存、可能丢统计）与 302
- 计数必须用 Redis `INCR`，"读-加-写"在并发下会丢数据（并发模型见[asyncio 并发](../advanced-topics/performance/01-async-python.md)）

## 7. 验证

```bash
uv run uvicorn main:app --reload

# 创建
curl -s -X POST localhost:8000/urls -H 'content-type: application/json' \
  -d '{"url": "https://docs.python.org/3.12/"}'
# 跳转（-i 看 307 与 Location 头）
curl -s -i localhost:8000/<code>
# 统计（clicks 随跳转增长）
curl -s localhost:8000/urls/<code>/stats
```

集成测试写法（TestClient + 依赖覆盖）见[集成测试](../testing/02-integration-testing.md)。

## 8. 扩展练习

- 短码过期：`SETEX` 替代 `set`，支持自定义别名（需校验唯一性）
- 每日统计：Hash 记 `count:{code}:{yyyymmdd}`，支持趋势图
- 速率限制：`INCR` + `EXPIRE` 实现每 IP 限流

---

## 🔗 相关文档

- 📄 **[生态集成](../frameworks/03-ecosystem-integration.md)** — Redis/SQLAlchemy 集成模式
- 🧪 **[集成测试](../testing/02-integration-testing.md)** — 本项目的测试方案
- 🚀 **[项目：数据处理管道](./03-data-pipeline.md)** — 下一关：定时任务与数据校验
- 📖 **[生态库速查](../reference/library-guides/02-ecosystem-libs.md)** — Redis 命令与 API 字典
- 🎓 **[asyncio 异步并发模型](../advanced-topics/performance/01-async-python.md)** — 本项目异步代码的底层原理
