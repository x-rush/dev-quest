# FastAPI 进阶 — 依赖注入、后台任务与中间件

> **文档简介**: 掌握 FastAPI 的三大进阶机制——依赖注入系统、后台任务与中间件，写出可组合、可测试的服务端代码
>
> **目标读者**: 已能编写基础路由，准备构建多模块服务的开发者
>
> **前置知识**: [FastAPI 入门](./01-fastapi-basics.md)、函数与闭包（[basics 04](../basics/04-functions-oop.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#FastAPI` `#依赖注入` `#中间件` `#后台任务` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 `Depends` 组合可复用的依赖链
- ✅ 用 yield 依赖实现"请求前准备 / 请求后清理"
- ✅ 用 `BackgroundTasks` 处理响应后的轻量异步工作
- ✅ 编写自定义中间件与 lifespan 应用生命周期

---

## 1. 依赖注入：Depends 与 Annotated

```python
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status

app = FastAPI()

# 依赖就是普通函数：签名声明它需要什么
def pagination(limit: int = 20, offset: int = 0) -> tuple[int, int]:
    return limit, offset

PageParams = Annotated[tuple[int, int], Depends(pagination)]

def get_current_user(token: str) -> dict:
    # 真实项目在此校验 JWT；演示直接查表
    users = {"alice": {"name": "Alice", "role": "admin"}}
    if token not in users:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "无效令牌")
    return users[token]

CurrentUser = Annotated[dict, Depends(get_current_user)]

@app.get("/items")
def list_items(user: CurrentUser, page: PageParams) -> dict:
    limit, offset = page
    return {"user": user["name"], "limit": limit, "offset": offset}
```

**要点**：

- 依赖可以嵌套：`get_current_user` 内部还能 `Depends` 别的函数，形成依赖树
- 依赖有缓存：同一请求内同一依赖只执行一次
- `Annotated` 写法把依赖声明收敛为类型别名，端点签名更干净（推荐风格）
- 依赖在测试中可整体替换（见[Mock 测试](../testing/03-mocking-testing.md)）

## 2. yield 依赖：准备与清理

```python
# 典型场景：数据库会话——请求结束后无论成败都关闭
async def get_session():
    async with SessionLocal() as session:   # yield 之前：准备（创建会话）
        yield session                        # 把会话交给端点使用
    # yield 之后：清理（在响应完成后执行）

# 在依赖里接住异常可做事务回滚
async def get_session_with_rollback():
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

**要点**：

- `yield` 前是"准备"、之后是"清理"，相当于每请求维度的 try/finally
- 完整数据库会话版见[生态集成](./03-ecosystem-integration.md)

## 3. 后台任务 BackgroundTasks

```python
import logging
from fastapi import BackgroundTasks, status

logger = logging.getLogger(__name__)

def send_welcome_email(to: str) -> None:
    logger.info("给 %s 发送欢迎邮件", to)   # 模拟耗时 IO

@app.post("/signup", status_code=status.HTTP_202_ACCEPTED)
def signup(email: str, background_tasks: BackgroundTasks) -> dict:
    background_tasks.add_task(send_welcome_email, email)
    # 响应立即返回，邮件在响应发送完成后执行
    return {"queued": True}
```

**要点**：

- 适合"轻量、可容忍丢失"的任务（发通知、写审计日志）
- 需要可靠投递/重试时请用任务队列（Celery/ARQ），不要滥用 BackgroundTasks
- 参数在 `add_task(函数, *args)` 中依次传入

## 4. 中间件

```python
import time
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

# CORS：前后端分离必备（白名单最小化，见安全实践）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)      # 放行到路由
    elapsed = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{elapsed:.4f}"
    return response
```

**要点**：

- `@app.middleware("http")` 包装每个请求：进入前 / 放行后两段逻辑
- 中间件里可读写 headers、用 `request.state` 向端点传递数据

## 5. Lifespan：应用级启动/关闭

```python
from contextlib import asynccontextmanager
import redis.asyncio as redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.from_url("redis://localhost:6379/0")  # 启动：建连接池
    yield
    await app.state.redis.aclose()                                # 关闭：释放

app = FastAPI(lifespan=lifespan)
```

**要点**：连接池、缓存预热等全局资源放 lifespan，别用模块级副作用创建。

## ✅ 最佳实践

- 业务逻辑别写进端点：用依赖注入服务函数，保持端点薄（架构原理见[项目分层与领域建模](../advanced-topics/architecture/01-project-architecture.md)）
- 全局异常处理器只兜底未知异常，业务错误统一走 `HTTPException`
- 中间件保持轻量：重逻辑交给依赖，避免每个请求的额外开销

## ❓ 常见问题

**Q1: 依赖和中间件有什么区别？**
依赖面向"这次请求需要什么资源"（可组合、可测试、有缓存）；中间件面向"所有请求的横切关注点"（日志、CORS、计时）。

**Q2: BackgroundTasks 任务失败会重试吗？**
不会。任务随进程存活，进程重启即丢失——重要任务请上消息队列。

---

## 🔗 相关文档

- 📖 **[FastAPI 核心速查](../reference/framework-essentials/01-fastapi-essentials.md)** — 依赖系统的字典级完整参考
- 📄 **[FastAPI 入门](./01-fastapi-basics.md)** — 路由与 Pydantic 模型基础
- 📄 **[生态集成](./03-ecosystem-integration.md)** — yield 依赖管理数据库会话的完整实现
- 📄 **[Mock 测试](../testing/03-mocking-testing.md)** — 依赖替换在测试中的应用
- 🎓 **[项目分层与领域建模](../advanced-topics/architecture/01-project-architecture.md)** — 依赖注入的架构价值
- 🚀 **[生产级 FastAPI 应用](../projects/04-production-fastapi-app.md)** — 本篇机制的综合落地
