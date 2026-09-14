# asyncio 并发 — 事件循环、协程与任务

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#asyncio` `#事件循环` `#协程` `#TaskGroup` `#并发` |
| **更新日期** | `2026年9月` |

## 📌 定义

asyncio 是标准库的异步 I/O 框架：单线程内由**事件循环**调度成千上万个协程，协程在 `await` 处主动让出控制权，等待 I/O 期间去执行其他任务。它解决的是 **I/O 等待浪费**，不是 CPU 密集问题（那交给 `multiprocessing`）。

## 📖 语法 / 签名

```python
import asyncio

async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)          # 唯一让出口：await
    return f"{name} 完成"

async def main() -> None:
    # 结构化并发：TaskGroup 退出时保证子任务全部完成或抛出（成组取消）
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fetch("A", 2.0))
        t2 = tg.create_task(fetch("B", 1.0))
    print(t1.result(), t2.result())

    # 并发收集结果：gather 适合"全要结果"的场景
    results = await asyncio.gather(fetch("A", 2.0), fetch("B", 1.0))

    # 超时：timeout 到点取消内部任务并抛 TimeoutError
    async with asyncio.timeout(5):
        await fetch("C", 1.5)

    # CPU/阻塞调用丢给线程或进程池，不卡事件循环
    await asyncio.to_thread(blocking_io_func)

asyncio.run(main())     # 程序入口：创建事件循环并运行 main
```

核心对象速查：`async def`（协程函数）→ 调用得**协程对象**（不执行）；`create_task`（把协程包成 Task 立即调度）；`await`（挂起等待可等待对象）；`async for` / `async with`（异步迭代器/上下文管理器）。

## 💡 示例

```python
import asyncio
import httpx

async def fetch_all(urls: list[str]) -> list[str]:
    """并发请求全部 URL，总耗时 ≈ 最慢的一个，而非之和。"""
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(client.get(u)) for u in urls]
    return [t.result().text for t in tasks]
```

心智模型三句话：

1. `async def` 创建协程，直接调用只得到协程对象，**不执行**
2. `await` 是"我在等 I/O，事件循环你先干别的"的唯一让出口
3. 事件循环单线程调度所有任务，**没有 await 就没有并发**

## 🧭 编排三件套：gather、TaskGroup 与超时

### gather 与 return_exceptions

```python
async def job(i: int) -> int:
    await asyncio.sleep(0.01 * (3 - i))
    if i == 2:
        raise ValueError("boom")
    return i

results = await asyncio.gather(job(0), job(1))
# [0, 1] —— 结果顺序与传参一致，与完成先后无关（实测）

results = await asyncio.gather(job(0), job(2), job(1), return_exceptions=True)
# [0, ValueError('boom'), 1] —— 异常作为占位结果返回（实测类型 ['int', 'ValueError', 'int']）
```

默认 `return_exceptions=False`：第一个异常立即向上抛，**其余任务不会被取消**、继续在后台运行（实测：抛错后 job(0) 仍完成）——抛出后记得 await 或取消它们，别留悬空任务。

### TaskGroup（3.11+ 结构化并发）

```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(job(0))
        tg.create_task(job(2))
        tg.create_task(job(1))
except* ValueError as eg:            # 3.11+ except*：捕获 ExceptionGroup
    print(len(eg.exceptions))        # 1 —— 全部失败打包在组里（实测）
```

退出 `async with` 的语义（实测）：要么全部完成；要么任一失败 → **立即取消同组其余任务** → 收集所有异常 → 抛 `ExceptionGroup`。结构上保证离开 with 块后没有任务逃逸。与 `gather(return_exceptions=True)` 的分工：前者是"一损俱损"的原子性，后者是"互不拖累"的结果收集。

### 超时：asyncio.timeout vs wait_for

```python
async def slow():
    await asyncio.sleep(0.5)
    return "done"

# 3.11+ 首选：上下文管理器，块内所有 await 共享同一截止时间，可嵌套
try:
    async with asyncio.timeout(0.05):
        await slow()
except TimeoutError:                 # 3.11+ 起 asyncio.TimeoutError 就是内置 TimeoutError（实测 is 为 True）
    ...

# 旧式：只包一个 awaitable
await asyncio.wait_for(slow(), timeout=0.05)   # 同样抛 TimeoutError（实测）
```

选型：`asyncio.timeout` 管"一段代码"的总预算（持有对象可 `reschedule()` 调整截止时间）；`wait_for` 管"单个 awaitable"。两者到点都会**先取消被包的工作**再抛 `TimeoutError`（实测：内部协程收到 CancelledError）。

## ⚠️ 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 协程内写阻塞调用 | `time.sleep`、`requests.get` 冻结整个事件循环；用 `asyncio.sleep`、`httpx`、`asyncio.to_thread` |
| 忘记 await 协程 | `fetch(...)` 裸调用只创建对象并触发 RuntimeWarning，函数体不执行 |
| 悬空任务 | `create_task` 后不保存引用可能被垃圾回收；TaskGroup 成组持有最安全 |
| TaskGroup 内一个失败全组取消 | 是特性也是约束：需要"互不拖累"时改用 gather（配 `return_exceptions=True`） |
| 在非 async 环境调 async 函数 | 必须经 `asyncio.run(...)` 进入事件循环 |
| 混用同步 ORM/驱动 | 数据库操作必须用异步驱动（如 aiosqlite/asyncpg），否则阻塞循环 |

## 🔗 相关条目

- 📄 **[高级特性教程](../../basics/07-advanced-features.md)** — asyncio 入门第一课
- 📄 **[asyncio 深度专题](../../advanced-topics/performance/01-async-python.md)** — 事件循环与任务管理的解释篇
- 📄 **[上下文管理器](./08-context-managers.md)** — `async with` 是同一协议的异步版
- 📄 **[FastAPI 核心速查](../framework-essentials/01-fastapi-essentials.md)** — 异步路由的生产级形态
