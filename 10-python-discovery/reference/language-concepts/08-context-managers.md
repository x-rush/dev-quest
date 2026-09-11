# 上下文管理器 — with 语句与资源生命周期

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#with` `#上下文管理器` `#contextlib` `#资源管理` |
| **更新日期** | `2026年9月` |

## 📌 定义

上下文管理器是实现"进入/退出"协议的对象：`__enter__` 在进入 `with` 块时执行，`__exit__` 在离开时**无论正常还是异常**都执行，是资源清理（关闭文件、释放锁、回滚事务）的结构化答案。`with` 保证清理代码只写一次且必然执行，替代散落各处的 `try/finally`。

## 📖 语法 / 签名

```python
# 类形式：实现两个魔术方法
class Managed:
    def __enter__(self) -> "Managed": ...
    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: object | None) -> bool: ...
        # 返回 True 表示异常已处理并吞掉；返回 None/False 继续向外抛

# 函数形式：contextlib.contextmanager 装饰生成器
from contextlib import contextmanager

@contextmanager
def managed():
    resource = acquire()
    try:
        yield resource          # yield 前是 __enter__，之后是 __exit__
    finally:
        release(resource)

# 使用
with managed() as m:
    ...                          # 异常也会触发 finally 清理

# 异步版：async with（协议为 __aenter__/__aexit__）
async with session.get(url) as resp: ...
```

contextlib 工具箱：`contextmanager`（生成器工厂）、`closing(obj)`（退出时调 `close`）、`suppress(*exc)`（吞指定异常）、`ExitStack`（动态管理不定数量的资源）、`chdir(path)`（临时切目录）。

## 💡 示例

```python
from contextlib import suppress, ExitStack, closing

# 文件：离开块自动 close，异常也不泄漏句柄
with open("data.txt", encoding="utf-8") as f:
    text = f.read()

# 多个资源一行声明
with open(src) as fin, open(dst, "w") as fout:
    fout.write(fin.read())

# 只在特定异常时静默跳过（比 try/except pass 意图更清晰）
with suppress(FileNotFoundError):
    cfg = read_config()

# 运行时才确定数量的资源
with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]
    ...
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 |
|------|------|
| `__exit__` 返回 True 吞掉一切异常 | 只在真正处理了异常时返回 True，默认返回 None |
| 手写 `__enter__/__exit__` 却漏 try/finally | 函数式 `@contextmanager` + `finally` 更不易错 |
| `@contextmanager` 忘写 try/finally | 异常路径不会清理资源，yield 必须包进 try |
| 生成器对象当资源用完不关 | 文件生成器退出前文件仍打开，配合 `with closing(...)` |
| 混用同步资源与 async with | 同步 `__exit__` 对象不能进 `async with`，反之亦然 |

## 🔗 相关条目

- 📄 **[异常处理教程](../../basics/06-exceptions.md)** — with 与异常体系的关系
- 📄 **[生成器与迭代器](./07-generators-iterators.md)** — `@contextmanager` 建立在生成器之上
- 📄 **[asyncio 并发](./09-asyncio-concurrency.md)** — `async with` 与 TaskGroup 的超时管理
- 📄 **[魔术方法与协议](./04-oop-protocols.md)** — `__enter__/__exit__` 所在的协议全景
