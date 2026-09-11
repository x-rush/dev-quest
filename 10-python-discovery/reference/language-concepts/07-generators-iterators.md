# 生成器与迭代器 — 迭代协议与惰性求值

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#生成器` `#迭代器` `#yield` `#惰性求值` `#itertools` |
| **更新日期** | `2026年9月` |

## 📌 定义

**迭代器**是实现了迭代协议的对象：`__iter__` 返回自身，`__next__` 产出下一个值，耗尽时抛 `StopIteration`。**生成器**是迭代器的便捷工厂：函数体含 `yield` 即为生成器函数，调用它不执行函数体，只在迭代时逐段推进。惰性求值让"处理 10GB 文件"只需一行数据的内存。

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
def read_lines(path: str):
    """逐行产出，内存中永远只有一行。"""
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.strip()

# 惰性链：串联多个生成器，for 消费时才逐元素推进，内存 O(1)
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

## 🔗 相关条目

- 📄 **[高级特性教程](../../basics/07-advanced-features.md)** — 生成器的教程视角
- 📄 **[数据结构速查](./03-data-structures.md)** — 可迭代容器全操作
- 📄 **[上下文管理器](./08-context-managers.md)** — 资源清理与惰性读取常配合出现
- 📄 **[asyncio 并发](./09-asyncio-concurrency.md)** — 异步迭代器是同一协议的异步版
