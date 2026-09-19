# 上下文管理器 — with 语句与资源生命周期

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#with` `#上下文管理器` `#contextlib` `#资源管理` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

上下文管理器是实现"进入/退出"协议的对象：`__enter__` 在进入 `with` 块时执行，`__exit__` 在 `__enter__` 成功后，正常或异常离开代码块时被调用，是资源清理（关闭文件、释放锁、回滚事务）的结构化答案。`with` 把获取与释放配对表达，减少重复的 `try/finally`；资源获取失败、清理自身失败和进程被强制终止仍需分别考虑。

## 📖 语法 / 签名

```python
# 类形式：实现两个魔术方法
class Managed:
    def __enter__(self) -> "Managed": ...
    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: object | None) -> bool | None: ...
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

<!-- full-library-explanation -->
## 进入成功，才有对应的退出

前置知识是 `try/finally` 与异常传播。`with` 的重要边界是 `__enter__` 成功返回：若获取资源时就失败，相应的 `__exit__` 不会被调用，获取操作自身要负责处理已经部分取得的资源。进入成功后，正常完成或异常离开代码块都会调用退出方法。

保存为 `managed.py` 并运行 `python managed.py`：

```python
from contextlib import contextmanager

@contextmanager
def managed():
    print("open")
    try:
        yield "resource"
    finally:
        print("close")

try:
    with managed() as value:
        print(value)
        raise ValueError("failed")
except ValueError:
    print("handled")
```

输出为 `open`、`resource`、`close`、`handled`，证明清理发生在外层处理异常之前。练习：把抛错改为正常退出，前面三行应保留，`handled` 不再出现。退出操作本身也可能失败；强制终止进程等情况不属于 Python 正常展开控制流的保证范围。

## 可运行的资源生命周期：异常传播与 ExitStack

前置知识是异常和生成器。`__exit__` 的返回值决定原异常是否继续向外传播：返回假值时传播，只有确认异常已经被处理时才返回真值。多个资源数量在运行时才确定时，`ExitStack` 按进入的反序退出；即使块内失败，也不会跳过已经登记的清理函数。

保存为 `lifecycle.py` 后运行 `python -I lifecycle.py`：

<!-- terra-fifteenth-case: python-context-lifecycle -->
```python
from contextlib import ExitStack, contextmanager

events: list[str] = []

@contextmanager
def resource(name: str):
    events.append(f"open:{name}")
    try:
        yield name
    finally:
        events.append(f"close:{name}")

try:
    with ExitStack() as stack:
        first = stack.enter_context(resource("first"))
        second = stack.enter_context(resource("second"))
        assert (first, second) == ("first", "second")
        raise ValueError("work failed")
except ValueError as error:
    events.append(f"handled:{error}")

assert events == [
    "open:first", "open:second", "close:second", "close:first", "handled:work failed"
]
print("context-lifecycle: " + " | ".join(events))
```

输出表明关闭顺序是 `second`、`first`，并且两个关闭都发生在外层 `except` 记录错误之前。若 `resource` 在 `yield` 之前失败，它尚未成为已进入的上下文，不会有它自己的 `close` 记录；应由获取代码清理已创建的局部资源。不要为了“让程序继续”让 `__exit__` 无条件返回 `True`，那会把编程错误和 I/O 失败伪装成成功。

## 🔗 相关条目

- 📄 **[异常处理教程](../../basics/06-exceptions.md)** — with 与异常体系的关系
- 📄 **[生成器与迭代器](./07-generators-iterators.md)** — `@contextmanager` 建立在生成器之上
- 📄 **[asyncio 并发](./09-asyncio-concurrency.md)** — `async with` 与 TaskGroup 的超时管理
- 📄 **[魔术方法与协议](./04-oop-protocols.md)** — `__enter__/__exit__` 所在的协议全景


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
