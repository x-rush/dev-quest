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
