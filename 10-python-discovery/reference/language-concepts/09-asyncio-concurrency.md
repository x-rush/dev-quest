# asyncio 并发 — 事件循环、协程与任务

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#asyncio` `#事件循环` `#协程` `#TaskGroup` `#并发` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

asyncio 是标准库的异步 I/O 框架：单线程中的**事件循环**在任务遇到可挂起的 `await` 时调度其他就绪任务。可同时存活多少协程受每个任务持有的内存、套接字/文件描述符、队列长度、下游服务限额和取消是否及时响应影响；应先限制并发数，再在目标负载下测量。它主要减少 **I/O 等待期间的空转**，不能让 CPU 密集 Python 代码在同一事件循环线程中并行执行。

## 📖 语法 / 签名

```python
import asyncio

async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)          # 等待期间可调度其他任务
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

    # 将一个同步等待放在线程中，避免在事件循环线程调用 time.sleep
    import time
    await asyncio.to_thread(time.sleep, 0.01)

asyncio.run(main())     # 程序入口：创建事件循环并运行 main
```

核心对象速查：`async def`（协程函数）→ 调用得**协程对象**（不执行）；`create_task`（把协程包成 Task 立即调度）；`await`（挂起等待可等待对象）；`async for` / `async with`（异步迭代器/上下文管理器）。

## 💡 示例

```python
import asyncio
import httpx

async def fetch_all(urls: list[str]) -> list[str]:
    """并发发起请求；只有各请求能并行等待且没有排队/限流时，总耗时才接近最慢的一项。"""
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(client.get(u)) for u in urls]
    return [t.result().text for t in tasks]
```

心智模型三句话：

1. `async def` 创建协程，直接调用只得到协程对象，**不执行**
2. `await` 表达等待可等待对象，是否实际挂起取决于其状态；async for/async with 也可能包含等待
3. 同一事件循环线程中的同步长计算会阻碍其他任务推进；线程、进程和原生扩展具有不同的并发机制

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

退出 `async with` 的语义（实测）：要么全部完成；要么任一失败 → **立即取消同组其余任务** → 收集所有异常 → 抛 `ExceptionGroup`。结构上保证离开 with 块后没有任务逃逸。与 `gather(return_exceptions=True)` 的分工：前者约束子任务的生命周期，后者收集各项结果。TaskGroup 不提供事务原子性，不会回滚已完成的外部操作。

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

选型：`asyncio.timeout` 管"一段代码"的总预算（持有对象可 `reschedule()` 调整截止时间）；`wait_for` 管"单个 awaitable"。两者都通过取消实现超时控制，但不是强制终止：timeout 取消当前任务并在退出上下文时转换相应异常；wait_for 取消等待对象并等待其取消完成。若任务阻塞循环或抑制取消，实际耗时可能超过给定超时。

## ⚠️ 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 协程内写阻塞调用 | `time.sleep`、`requests.get` 冻结整个事件循环；用 `asyncio.sleep`、`httpx`、`asyncio.to_thread` |
| 忘记 await 协程 | `fetch(...)` 裸调用只创建对象并触发 RuntimeWarning，函数体不执行 |
| 悬空任务 | `create_task` 后不保存引用可能被垃圾回收；TaskGroup 成组持有最安全 |
| TaskGroup 内一个失败全组取消 | 是特性也是约束：需要"互不拖累"时改用 gather（配 `return_exceptions=True`） |
| 在已有事件循环内再次 asyncio.run | 普通脚本可用 asyncio.run；已有循环中通常直接 await，入口方式取决于运行环境 |
| 在事件循环线程直接执行阻塞数据库调用 | 使用异步驱动或明确的线程隔离，并确认连接对象的线程使用约束 |

<!-- full-library-explanation -->
## 调度并不等于事务

前置知识是同步调用、异常和资源清理。协程对象代表尚未完成的计算；任务让事件循环跟踪和推进它。`await` 只有在等待对象需要挂起时才让出执行机会，等待一个已经就绪的结果不必切换任务。

下面的完整实验要求 Python 3.11+，保存为 `tasks.py` 后运行：

```python
import asyncio

async def main():
    records = []
    ready = asyncio.Event()

    async def writer():
        records.append("written")
        ready.set()
        await asyncio.sleep(60)

    async def failing():
        await ready.wait()
        raise ValueError("failed")

    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(writer())
            group.create_task(failing())
    except* ValueError:
        print("group failed")
    print(records)

asyncio.run(main())
```

输出为 `group failed` 与 `['written']`，不会等待 60 秒：异常触发组内取消，但取消没有撤销已经发生的列表修改。练习：把写入换成发送邮件，说明为什么不能依靠 TaskGroup 实现业务回滚。答案是外部副作用需要自己的事务、幂等或补偿协议。

## 🔗 相关条目

- 📄 **[高级特性教程](../../basics/07-advanced-features.md)** — asyncio 入门第一课
- 📄 **[asyncio 深度专题](../../advanced-topics/performance/01-async-python.md)** — 事件循环与任务管理的解释篇
- 📄 **[上下文管理器](./08-context-managers.md)** — `async with` 是同一协议的异步版
- 📄 **[FastAPI 核心速查](../framework-essentials/01-fastapi-essentials.md)** — 异步路由的生产级形态


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
