# 高级特性 — 装饰器、生成器、类型进阶与 asyncio 入门

## 先理解，再动手

装饰器改变可调用对象，生成器延迟产生值，async 协程需要运行时驱动。先分别跑一个例子，再组合，否则无法定位是哪个机制引入差异。

**本节自测**：写给返回值加前缀的装饰器，确认包装器返回了原函数处理后的结果。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

调用方应拿到新字符串；缺 return 会得到 None，与是否打印成功无关。

</details>

> **文档简介**: 跨入 Python 进阶区：理解装饰器的函数包装本质、生成器的惰性求值、泛型与 Protocol 类型进阶，以及 asyncio 并发编程的第一课
>
> **目标读者**: 已完成 ⭐ 入门路径、希望掌握 Python 框架底层机制的开发者
>
> **前置知识**: 完成[异常处理](./06-exceptions.md)，理解闭包与魔术方法基本概念

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 教程 |
| **难度** | ⭐⭐ |
| **标签** | `#装饰器` `#生成器` `#泛型` `#asyncio` |
| **更新日期** | `2026年9月` |

</details>

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

def first[T](items: Iterable[T]) -> T | None:   # PEP 695 泛型语法（3.12+）
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

## 5. 3.13/3.14 新特性速览

本模块基线为 Python 3.14。在前四节的稳定知识之上，这三年的版本值得专门记住：

**t-string 模板字符串（3.14，PEP 750）**：`t"..."` 与 f-string 同形，返回可延迟渲染的模板对象而非 `str`，由库决定如何转义插值，主打 HTML/SQL 防注入。见[字符串格式化字典](../reference/language-concepts/12-string-formatting.md)。

**类型系统增强**：

```python
# 3.13：TypeVar 可以带默认值（PEP 696），未指定时用默认类型
from typing import TypeVar

class Default: ...
T = TypeVar("T", default=Default)

# 3.13：TypeIs 收窄更直觉（PEP 742），isinstance 式的判别函数
from typing import TypeIs

def is_str_list(items: list[object]) -> TypeIs[list[str]]:
    return all(isinstance(i, str) for i in items)

# 3.14：注解改为惰性求值（PEP 649/749），前向引用不再需要引号
def create() -> "App": ...   # 旧代码里的字符串前向引用写法成为历史
```

**free-threading 现状**：no-GIL 构建在 3.13 实验引入，3.14 起转为**官方支持**的构建选项（PEP 779），但默认安装的解释器仍带 GIL，第三方生态适配持续推进中。生产选型请参考[故障排除字典的 GIL 决策表](../reference/quick-references/02-troubleshooting.md)，现阶段 asyncio / multiprocessing 的分工不变。

---

## ✅ 最佳实践

包装函数时 wraps 保留名称、文档和 wrapped 等元数据，有利于调试与工具检查，但不会自动保持全部运行行为。参数化装饰器常见嵌套工厂结构，不应只背层数而不理解每层何时执行。

生成器可作为明确的单次数据流传递，消费完不能无声地当可重复集合使用。Protocol 适合结构化接口，抽象基类也有名义约束和共享行为用途；异步程序同时检查阻塞调用是否占住事件循环。

---

## ❓ 常见问题

### Q1: 多线程、多进程、asyncio 怎么选？
**A**: I/O 并发选 asyncio；CPU 密集选 `multiprocessing`（绕过 GIL）；多线程仅适合兼容阻塞库的过渡方案。free-threading（no-GIL）构建 3.14 起官方支持但仍非默认，生态适配中，选型逻辑暂不变。GIL 细节见[常见错误排查](../reference/quick-references/02-troubleshooting.md)。

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


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
