# 生成器与迭代器 — 迭代协议与惰性求值

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#生成器` `#迭代器` `#yield` `#惰性求值` `#itertools` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

**迭代器**是实现了迭代协议的对象：`__iter__` 返回自身，`__next__` 产出下一个值，耗尽时抛 `StopIteration`。**生成器**是迭代器的便捷工厂：函数体含 `yield` 即为生成器函数，调用它不执行函数体，只在迭代时逐段推进。逐行处理可避免一次读入整个文件，但内存仍取决于最长记录、读取缓冲和下游是否保存结果。

## 📖 语法 / 签名

```python
# 生成器函数
def gen():
    yield value            # 产出一个值并暂停
    yield from inner()     # 委托子生成器（含异常传播）

# 生成器表达式：与列表推导式同形，用圆括号
squares = (x * x for x in range(10))

# 手动推进
g = gen()
next(g)        # 产出值；耗尽抛 StopIteration（for 自动处理）

# 自定义迭代器类（生成器覆盖不了的显式状态场景）
class Countdown:
    def __init__(self, n: int): self.n = n
    def __iter__(self): return self
    def __next__(self):
        if self.n <= 0: raise StopIteration
        self.n -= 1
        return self.n + 1
```

配套工具：`iter(obj)` 取迭代器（可迭代 vs 迭代器的分界）、`enumerate`/`zip(strict=)` 并行迭代、`itertools`（`chain`、`islice`、`groupby`、`pairwise` 等惰性组合件）。

## 💡 示例

```python
import itertools

def read_lines(path: str):
    """逐行产出；内存取决于行长度、缓冲和调用方保留的数据。"""
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.strip()

# 局部片段：先准备 app.log；消费时逐元素推进，不保存全部行
errors = (line for line in read_lines("app.log") if "ERROR" in line)
first_three = list(itertools.islice(errors, 3))

# 聚合终止函数直接消费生成器
total = sum(x * x for x in range(1_000_000))
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 生成器一次性耗尽 | 耗尽后再迭代得到空值；复用就包成函数每次新建 |
| `len()` 不可用 | 生成器无长度，需要长度先 `list()`（付出内存代价） |
| 混淆可迭代与迭代器 | `list` 是可迭代对象但不是迭代器；`iter(list)` 才是 |
| 生成器内吞异常 | 迭代中途抛出的异常会终止生成器，`finally` 仍会执行 |
| `yield from` 忘记返回值 | 子生成器的 `return x` 体现在 `StopIteration.value`，需 `result = yield from` 接收 |

<!-- full-library-explanation -->
## 一次性消费与资源关闭

前置知识是 `for`、函数和文件读取。可迭代对象负责提供迭代器；迭代器保存“读到哪里”的状态。生成器把这个状态保存为暂停的函数执行现场，因此不会在每次循环时自动回到起点。

保存为 `iteration.py` 并运行 `python iteration.py`：

```python
def numbers():
    print("started")
    yield 10
    yield 20

g = numbers()
print("created")
print(next(g))
print(list(g))
print(list(g))
```

输出依次为 `created`、`started`、`10`、`[20]`、`[]`。创建时尚未运行函数体；`next` 消费第一项，第一次 `list` 消费剩余项，第二次得到空列表。

练习：用两次 `list(numbers())` 替换最后两行，每次应分别得到 `[10, 20]`，因为创建了两个新迭代器。再思考文件生成器只消费三行就停止的情况：生成器内部的 `with` 可能仍暂停着，调用方应显式关闭生成器或在调用方持有文件上下文，不能把循环 `break` 当成资源已经关闭。

## 🔗 相关条目

- 📄 **[高级特性教程](../../basics/07-advanced-features.md)** — 生成器的教程视角
- 📄 **[数据结构速查](./03-data-structures.md)** — 可迭代容器全操作
- 📄 **[上下文管理器](./08-context-managers.md)** — 资源清理与惰性读取常配合出现
- 📄 **[asyncio 并发](./09-asyncio-concurrency.md)** — 异步迭代器是同一协议的异步版


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
