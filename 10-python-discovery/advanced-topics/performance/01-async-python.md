# asyncio 异步并发模型

> **文档简介**: 理解事件循环、协程与任务的真实执行模型，搞清楚 FastAPI 里 `def` 与 `async def` 的选择，以及何时该放弃异步
>
> **目标读者**: 用过 async/await 但说不清并发语义的开发者
>
> **前置知识**: [高级特性（异步基础）](../../basics/07-advanced-features.md)、[FastAPI 进阶](../../frameworks/02-fastapi-advanced.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#asyncio` `#并发` `#事件循环` `#FastAPI` |
| **更新日期** | `2026年9月` |

</details>

## 1. 并发三模型对比

| 模型 | 适合 | 不适合 | 调度单位 |
|------|------|--------|---------|
| asyncio | 大量 IO 等待（网络/磁盘） | CPU 密集 | 协程（单线程） |
| threading | 阻塞库的轻量并发 | 高频切换、GIL 限制 | 线程 |
| multiprocessing | CPU 密集 | 数据共享复杂 | 进程 |

asyncio 的本质：**单线程内协作式调度**——协程在 `await` 处主动让出控制权，事件循环趁等待间隙去跑别的协程。没有抢占，全是配合。

## 2. await 到底发生了什么

```python
import asyncio

async def fetch(name: str, delay: float) -> str:
    print(f"{name} 开始")
    await asyncio.sleep(delay)   # 让出控制权：事件循环转去跑其他协程
    print(f"{name} 完成")
    return name

async def main() -> None:
    # 串行写法：总耗时 3 秒
    # await fetch("a", 1); await fetch("b", 1); await fetch("c", 1)

    # 并发写法：总耗时 1 秒——三个协程在 await 处交替执行
    results = await asyncio.gather(fetch("a", 1), fetch("b", 1), fetch("c", 1))
    print(results)

asyncio.run(main())
```

**要点**：

- await 等待可等待对象，并不限于 I/O；在同一事件循环线程里，不挂起的同步代码不会与另一协程交错，但跨 await 的业务不变量仍可能需要锁或事务
- 对比学习：`gather` 之于协程，约等于 `Promise.all`（JS）与 `errgroup`（Go）的组合

## 3. 任务管理：TaskGroup（3.11+ 推荐）

```python
async def main() -> None:
    async with asyncio.TaskGroup() as tg:      # 结构化并发
        t1 = tg.create_task(fetch("a", 1))
        t2 = tg.create_task(fetch("b", 2))
    # 离开 with 时全部任务已完成；任一失败会取消其余任务并抛 ExceptionGroup
    print(t1.result(), t2.result())
```

限制并发量用 `Semaphore`：

```python
sem = asyncio.Semaphore(10)                    # 最多 10 个并发请求

async def bounded_fetch(url: str) -> str:
    async with sem:
        return await fetch(url, 0.1)
```

**要点**：TaskGroup 保证任务不泄漏；裸用 `create_task` 后忘记 await 容易产生"悬空任务"警告。完整超时用 `asyncio.timeout(5)` 包裹（3.11+）。

## 4. FastAPI：def 与 async def 的真相

```python
@app.get("/a")
def sync_endpoint():                      # FastAPI 自动丢进线程池执行
    time.sleep(1)                         # 阻塞库安全：不会卡事件循环
    return {}

@app.get("/b")
async def async_endpoint():
    await async_client.get("https://example.com")   # 异步栈：等 IO 时服务别人
    return {}
```

**红线**：`async def` 里调用阻塞函数（`time.sleep`、同步 DB 驱动、`requests`）会**卡住整个事件循环**，该事件循环上的其他任务会延迟；其他 worker 或线程仍可能工作。

选型口诀：

- 全异步库（httpx.AsyncClient、asyncpg、redis.asyncio、SQLAlchemy async）→ `async def`
- 只有同步库 → 用 `def`，让线程池兜底

## 5. CPU 密集怎么办

```python
import asyncio

async def crunch_numbers(data: bytes) -> int:
    loop = asyncio.get_running_loop()
    # 丢给线程/进程池：绕开事件循环，重计算用进程池绕开 GIL
    return await loop.run_in_executor(None, blocking_hash, data)  # None 使用默认线程池，并非进程池
```

**要点**：事件循环只解决 IO 并发。run_in_executor(None, ...) 使用默认线程池；进程池需要显式传入 ProcessPoolExecutor。原生扩展是否释放 GIL、数据传输成本及运行环境会影响选择，上例的 blocking_hash 由调用方提供。

## 6. 实战核对清单

- [ ] 每个外部调用都有超时（`asyncio.timeout(5)` / httpx `timeout=`）
- [ ] 并发请求有 `Semaphore` 上限，防打爆下游
- [ ] 无 `async def` 内的阻塞调用（用 py-spy 抓栈可发现，见[性能剖析](./02-profiling-optimization.md)）
- [ ] 共享可变状态最小化——单线程模型里仍有 `await` 交错
- [ ] 分层架构中明确哪些方法需要 await；上层编排也可以是异步方法（与[项目分层](../architecture/01-project-architecture.md)协同）

---

<!-- full-library-explanation -->
## 用交错顺序解释丢失更新

前置是 await 与共享对象。即使只有一个事件循环线程，业务动作跨越 await 时也可能被其他任务插入：任务 A 读取余额 10 后等待，任务 B 同样读取 10，二者各写回 9，结果只扣了一次。锁应保护整个需要一致性的操作，而不是只保护赋值那一行。

练习创建两个任务，各执行“读计数 → await asyncio.sleep(0) → 写回计数加一”。从 0 开始，刻意构造相同读取值时最终可能是 1。改为在同一个 asyncio.Lock 内完成整段后，应为 2。再解释为什么单进程锁不能保护多个 worker 的数据库余额：不同进程没有共享这把锁，需要数据库或其他跨进程协调机制。

并发上限也要区分活跃操作数和排队任务数。Semaphore 限制进入临界区的数量，但一次创建百万任务仍可能耗尽内存；大量输入应配合有界队列、分批读取或固定数量的工作任务。

## 🔗 相关文档

- 📄 **[高级特性](../../basics/07-advanced-features.md)** — async/await 语法入门
- 📄 **[生态集成](../../frameworks/03-ecosystem-integration.md)** — 异步数据库与 Redis 的接入方式
- 🎓 **[性能剖析与优化](./02-profiling-optimization.md)** — 本篇"红线问题"的定位工具
- 🚀 **[项目：短链接服务](../../projects/02-url-shortener.md)** — 异步 Redis 实战
- 📖 **[标准库字典](../../reference/library-guides/01-standard-library.md)** — asyncio 模块速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
