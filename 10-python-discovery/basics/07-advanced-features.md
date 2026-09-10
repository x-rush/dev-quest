# 高级特性 — 装饰器、生成器、类型进阶与 asyncio 入门

> **文档简介**: 跨入 Python 进阶区：理解装饰器的函数包装本质、生成器的惰性求值、泛型与 Protocol 类型进阶，以及 asyncio 并发编程的第一课
>
> **目标读者**: 已完成 ⭐ 入门路径、希望掌握 Python 框架底层机制的开发者
>
> **前置知识**: 完成[异常处理](./06-exceptions.md)，理解闭包与魔术方法基本概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#装饰器` `#生成器` `#泛型` `#asyncio` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 编写带参数的装饰器并用 `@wraps` 保留元信息
- ✅ 区分生成器函数与生成器表达式，理解惰性求值收益
- ✅ 使用泛型、`Protocol`、`TypedDict` 表达复杂类型
- ✅ 用 `async/await` 编写并发 I/O 程序并理解事件循环模型

---

## 1. 装饰器：函数的函数

装饰器本质是"接收函数、返回新函数"的高阶函数，`@decorator` 只是 `f = decorator(f)` 的语法糖：

```python
from functools import wraps
import time

def timed(func):
    @wraps(func)                        # 保留原函数名与 docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)  # 透传所有参数
        print(f"{func.__name__} 耗时 {time.perf_counter() - start:.3f}s")
        return result
    return wrapper

@timed
def slow_sum() -> int:
    return sum(range(5_000_000))
```

`*args/**kwargs` 让包装器适配任意签名；`@wraps` 缺失会让原函数 `__name__` 变成 `"wrapper"`，破坏调试与文档。

**带参数的装饰器**多包一层：

```python
def retry(times: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == times:
                        raise
        return wrapper
    return decorator

@retry(times=3)          # 先执行 retry(3) 得到真正装饰器
def fetch(url: str) -> str: ...
```

FastAPI 的 `@app.get("/path")`、pytest 的 `@pytest.fixture` 全是装饰器——看懂本节，框架魔法就不再神秘。

---

## 2. 生成器：惰性求值的流水线

生成器函数用 `yield` 逐个产出值，调用时**不执行**函数体，只在迭代时推进：

```python
def read_lines(path: str):
    """逐行产出，内存中永远只有一行（处理 10GB 文件也不爆内存）。"""
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.strip()
```

三种创建方式：`yield` 生成器函数、生成器表达式 `(x * x for x in range(10))`、`yield from` 委托子生成器。

关键特性：

- **一次性**：耗尽后为空，需要复用就包成函数每次新建
- **惰性链**：多个生成器串联只在 `for` 消费时才逐元素推进，内存 O(1)
- `next(g)` 手动推进，耗尽抛 `StopIteration`（`for` 自动处理）

---

## 3. 类型进阶：泛型、Protocol 与 TypedDict

**泛型**：让容器/函数的类型随参数流动：

```python
from collections.abc import Iterable

def first[T](items: Iterable[T]) -> T | None:   # 3.12 新泛型语法 PEP 695
    for item in items:
        return item
    return None
```

**Protocol**：结构化子类型（鸭子类型的静态版）——不要求继承，只要"长得像"：

```python
from typing import Protocol

class Serializer(Protocol):
    def serialize(self) -> str: ...

def export(obj: Serializer) -> None:
    print(obj.serialize())

class JSONStore:                     # 没有继承 Serializer，但类型检查通过
    def serialize(self) -> str:
        return "{}"
```

**TypedDict**：给字典的形状定类型：

```python
from typing import TypedDict

class UserRow(TypedDict):
    id: int
    name: str
    admin: bool

u: UserRow = {"id": 1, "name": "ada", "admin": False}
```

运行时强校验交给 Pydantic（同形状的数据模型），见 [typing 注解全表](../reference/language-concepts/05-typing-annotations.md)。

---

## 4. asyncio 入门：单线程并发

异步解决的是 **I/O 等待浪费**：网络请求、数据库查询时 CPU 闲着，事件循环趁等待切换到其他任务。

```python
import asyncio

async def fetch(name: str, delay: float) -> str:    # async def 定义协程
    await asyncio.sleep(delay)                       # await 挂起，让出控制权
    return f"{name} 完成"

async def main() -> None:
    # 并发跑三个协程，总耗时 = 最长的那个，而非三者之和
    results = await asyncio.gather(
        fetch("A", 2.0),
        fetch("B", 1.0),
        fetch("C", 1.5),
    )
    print(results)

asyncio.run(main())   # 程序入口：启动事件循环
```

心智模型三句话：

1. `async def` 创建**协程**，直接调用它只会得到协程对象，不执行
2. `await` 是"我在等 I/O，事件循环你先干别的"的唯一让出口
3. 事件循环（event loop）单线程调度所有任务，**没有 await 就没有并发**

**同步 vs 异步对比**：

| | 同步 | 异步 |
|------|------|------|
| 三个 1s 网络请求 | ~3s | ~1s |
| 适用场景 | CPU 密集、简单脚本 | 高并发 I/O（API 网关、爬虫） |
| 代表生态 | requests | httpx.AsyncClient / FastAPI |

> ⚠️ 陷阱：协程里写同步阻塞调用（如 `time.sleep`、`requests.get`）会卡死整个事件循环。异步栈内用 `asyncio.sleep`、`httpx` 等异步对等物。

---

## ✅ 最佳实践

- ✅ **装饰器必配 `@wraps`**，参数化装饰器三层结构记牢
- ✅ **大数据流用生成器**，聚合终止函数（sum/join）配生成器表达式
- ✅ **公开 API 优先 Protocol** 而非抽象基类，耦合更低
- ❌ **避免**：把生成器对象存起来跨函数复用（一次性耗尽）；事件循环里混入阻塞调用

---

## ❓ 常见问题

### Q1: 多线程、多进程、asyncio 怎么选？
**A**: I/O 并发选 asyncio；CPU 密集选 `multiprocessing`（绕过 GIL）；多线程仅适合兼容阻塞库的过渡方案。GIL 细节见[常见错误排查](../reference/quick-references/02-troubleshooting.md)。

---

## 🎯 练习与实践

### 练习一：限速装饰器
1. 实现 `@rate_limit(per_second: float)`：两次调用间隔不足时 `time.sleep` 等待
2. 用 `@wraps` 保留元信息，`timed` 与 `rate_limit` 叠加使用验证装饰器顺序

### 练习二：并发批量请求
1. 用 `httpx.AsyncClient` 并发请求 5 个 URL（可用 `https://httpbin.org/delay/1`），对比串行与 `asyncio.gather` 版本耗时

---

## 🔗 相关文档

- 📄 **[综合项目：书签管理器](./08-first-project.md)** — 用 typer/rich 实战装饰器与 CLI
- 📄 **[typing 注解全表](../reference/language-concepts/05-typing-annotations.md)** — 泛型语法全量参考
- 📄 **[FastAPI 速查](../reference/framework-essentials/01-fastapi-essentials.md)** — asyncio 与装饰器的生产级应用
