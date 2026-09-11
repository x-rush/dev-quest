# 装饰器 — 函数包装与元编程入口

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#装饰器` `#高阶函数` `#functools` `#元编程` |
| **更新日期** | `2026年9月` |

## 📌 定义

装饰器是"接收函数（或类）、返回新对象"的可调用物，`@decorator` 只是 `f = decorator(f)` 的语法糖。它把横切逻辑（计时、重试、缓存、注册路由）从业务代码中剥离，是理解 FastAPI 路由注册、pytest fixture 等框架魔法的基础。

## 📖 语法 / 签名

```python
def decorator(func):
    def wrapper(*args, **kwargs):   # *args/**kwargs 适配任意签名
        ...                         # 前置逻辑
        result = func(*args, **kwargs)
        ...                         # 后置逻辑
        return result
    return wrapper

@decorator
def target(): ...
# 等价于：target = decorator(target)
```

三类常用形态：

- **无参装饰器**：如上，单层包装
- **带参装饰器**：再包一层工厂 `def deco(arg): def decorator(func): ...`
- **类装饰器**：实现 `__call__` 的类实例，或直接装饰类本身

标准库工具：`functools.wraps`（保留元信息）、`functools.cache` / `lru_cache`（记忆化）、`functools.singledispatch`（按类型分派）。

## 💡 示例

```python
from functools import wraps
import time

def timed(func):
    @wraps(func)                       # 缺失会让 __name__ 变成 "wrapper"
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时 {time.perf_counter() - start:.3f}s")
        return result
    return wrapper

@timed
def slow_sum() -> int:
    return sum(range(5_000_000))

# 带参数的装饰器：三层结构
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

@retry(times=3)          # 先执行 retry(3) 得到真正的装饰器
def fetch(url: str) -> str: ...
```

框架视角：`@app.get("/path")` 是带参装饰器——注册路由并返回原函数；`@pytest.fixture` 把函数注册为 fixture 工厂。

## ⚠️ 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 忘写 `@wraps` | 原函数 `__name__`/`__doc__` 被覆盖，破坏调试与文档 |
| 装饰器顺序敏感 | `@a` 上 `@b` 下等价于 `a(b(f))`，最靠近函数的最先生效 |
| 带参装饰器少包一层 | `@retry(3)` 与 `@retry` 的调用时机完全不同，注意括号 |
| 包装器忘返回结果 | 吞掉 `func` 的返回值，调用方拿到 `None` |
| 对异步函数用同步包装 | `async def` 需配 `async def wrapper` + `await`，同步包装器会破坏协程 |

## 🔗 相关条目

- 📄 **[高级特性教程](../../basics/07-advanced-features.md)** — 装饰器的教程视角
- 📄 **[生成器与迭代器](./07-generators-iterators.md)** — 同属函数进阶主题
- 📄 **[FastAPI 核心速查](../framework-essentials/01-fastapi-essentials.md)** — 路由装饰器的生产级用法
- 📄 **[生态库精选](../library-guides/02-ecosystem-libs.md)** — tenacity 等装饰器型库
