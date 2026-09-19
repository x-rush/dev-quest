# 内置函数全表（分类速查）

## 阅读准备：名字、函数与协议

前置：函数调用、列表与异常。内置名称无需 import，但可以被局部变量遮蔽；把变量命名为 list 后，list(...) 就可能不再调用内置类型。关键字如 for 参与语法解析，len 是可调用对象，math.sqrt 则来自需要导入的标准库。

读签名时注意 `/` 之前的参数只能按位置传入，`*` 后的参数只能按名字传入。比如 next(iterator, None) 合法，next(iterator, default=None) 不合法。不是所有带默认值的参数都允许关键字写法。

## 先运行一个完整的数据处理例子

保存为 `builtins_lab.py`，运行 `python builtins_lab.py`。只依赖 Python 标准运行时，本例不读取网络或个人文件。

```python
raw = [" 7 ", "2", "10"]
numbers = list(map(int, raw))
ordered = sorted(numbers)
print(numbers, ordered)
print(sum(numbers), min(numbers), max(numbers))
print(list(enumerate(ordered, start=1)))

stream = iter(ordered)
print(next(stream), next(stream), next(stream), next(stream, "结束"))
print(any([]), all([]))
print(bool("False"), bool(""))
```

预期输出：

```text
[7, 2, 10] [2, 7, 10]
19 2 10
[(1, 2), (2, 7), (3, 10)]
2 7 10 结束
False True
True False
```

<!-- core-p1-case: python-builtins-iteration -->
```python
import math

raw = [" 7 ", "2", "10"]
numbers = list(map(int, raw))
assert numbers == [7, 2, 10]
assert sorted(numbers) == [2, 7, 10]
assert list(enumerate(sorted(numbers), start=1)) == [(1, 2), (2, 7), (3, 10)]
stream = iter(numbers)
assert [next(stream), next(stream), next(stream), next(stream, "结束")] == [7, 2, 10, "结束"]
assert (any([]), all([]), bool("False"), bool("")) == (False, True, True, False)
assert math.isclose(0.1 + 0.2, 0.3)
print("builtins-iteration: map, sorted, next default, truth values, isclose")
```

这段程序直接运行本文使用的内置函数与一个标准库比较函数。它不证明每个内置函数的所有
重载；例如 `map` 的转换异常仍在消费迭代器时发生，应按输入边界单独测试。

map 逐项转换，list 消费迭代结果；sorted 创建新列表，没有修改 numbers。next 每调用一次就消耗一个元素。any 空集合没有真值证据，all 空集合没有反例，因此分别为 False 与 True。非空文本 "False" 仍是真值：bool 不解析英文布尔文本。

## 容易缺失的契约

| 调用 | 输入与输出 | 选择与边界 |
|---|---|---|
| `map(function, iterable)` | 将每项交给函数，返回迭代器 | 转换错误在消费时出现；需要复用结果时显式物化 |
| `filter(predicate, iterable)` | 保留谓词为真的项，返回迭代器 | predicate 为 None 时按真值过滤，0、空串也会被过滤 |
| `iter(callable, sentinel)` | 反复无参调用，遇到与 sentinel 相等的值停止 | 与 iter(container) 是不同重载，适合分块读取 |
| `next(iterator, default)` | 返回下一项，耗尽时返回默认值 | 无默认值则抛 StopIteration；默认值按位置传 |
| `min(items, default=...)` | 返回最小项，空迭代器可用 default | 多个位置参数形式不支持这个空集合默认值 |
| `sorted(items, key=...)` | 返回新列表，key 提取排序依据 | 不修改原列表；与 list.sort 原地修改且返回 None 区分 |
| `getattr(obj, name, default)` | 按名称读取属性，缺失时返回默认值 | 属性访问可能触发 property 逻辑，不一定只是读字典 |
| `hasattr(obj, name)` | 尝试属性访问，遇 AttributeError 返回 False | 不能据此保证属性读取没有副作用 |
| `hash(obj)` | 获得哈希整数 | 可哈希不意味着无碰撞；不能把跨进程 hash 当持久 ID |
| `type(obj)` / `type(name, bases, namespace)` | 查询类型 / 动态构造类 | 第二种是元编程入口；日常类型兼容判断多用 isinstance |
| `vars(obj)` | 返回对象的属性字典 | 没有 __dict__ 的对象可能失败；它不是所有对象的万能序列化 |
| `memoryview(buffer)` | 对缓冲区建立视图 | 不等于独立副本；释放视图与底层对象的生命周期需要协调 |

上表是常用重载的简写，不冒充每个函数的完整签名。以下分类正文加上本表覆盖官方内置函数索引中的名称；异常类与内置常量另有各自分类，不能用 dir(builtins) 的总数充当函数数量。

## 小练习：预测失败发生在哪一步

执行 `converted = map(int, ["1", "bad"])` 时通常还没触发转换错误；执行 `list(converted)` 消费到 "bad" 时才抛 ValueError。请改成逐项 try/except，只保留合法整数，同时记录非法项。

验收：输入 `["1", "bad", "3"]` 得到合法数 `[1, 3]` 与一条非法项记录；不能捕获错误后直接返回空列表而丢掉合法结果。这检查的是惰性消费与错误边界，不是记住 map 的拼写。

## 概述

Python 内置函数共 70 余个，无需导入即可使用。本表按用途分类，每个条目给出签名、示例与陷阱。可用 `dir(builtins)` 列出全部名字。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#内置函数` `#速查` `#标准库` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. 类型与转换

| 函数 | 作用 |
|------|------|
| `int(x, base=10)` | 转 int；`int("ff", 16)` → 255 |
| `float(x)` | 转 float；`float("nan")` → nan |
| `str(obj)` | 转 str，调 `__str__` |
| `repr(obj)` | 调试表示，调 `__repr__` |
| `bool(x)` | 按真值规则转 bool |
| `bytes(s, "utf-8")` | 编码为字节串 |
| `list(iterable)` / `tuple(it)` / `set(it)` / `dict(...)` | 构建容器 |
| `frozenset(it)` | 不可变集合，可作 dict 键 |
| `complex(re, im)` | 复数 |
| `ord(c)` / `chr(n)` | 字符 ↔ 码点 |
| `bin(n)` / `hex(n)` / `oct(n)` | 进制字符串：`bin(5)` → `'0b101'`、`hex(255)` → `'0xff'`、`oct(8)` → `'0o10'` |
| `ascii(obj)` | 同 `repr` 但非 ASCII 字符转义：`ascii("café")` → `"'caf\xe9'"` |
| `bytearray(b"ab")` | 可变字节串：支持原地增改（`ba[0] = 65` → `bytearray(b'Ab')`） |
| `memoryview(obj)` | 零拷贝缓冲区视图；视图存活期间原对象禁止扩缩容（实测抛 `BufferError`），`mv.release()` 或 with 释放 |
| `slice(start, stop, step)` | 切片对象：`a[1:3]` 即 `a[slice(1, 3)]`，详见[数据结构速查](./03-data-structures.md) |

**陷阱**: `int("4.5")` 抛 `ValueError`（不像 JavaScript）；`int(float("4.9"))` 是截断为 4。

---

## 2. 数值与数学

```python
abs(-3.5)                    # 3.5
round(2.675, 2)              # 2.67：2.675 的二进制浮点近似影响十进制舍入
divmod(17, 5)                # (3, 2) 商与余数一次返回
pow(2, 10, 100)              # 24 三参数取模幂
sum(nums, start=0)           # 求和，可给初始值
min(nums, key=abs)           # 极值可带 key 函数
max(users, key=lambda u: u.score)
```

**陷阱**: 浮点比较用 `==` 不可靠，用 `math.isclose(a, b)`。

---

## 3. 迭代与聚合

```python
len(seq)                     # 调 __len__
range(10, 0, -1)             # 惰性整数序列
enumerate(items, start=1)    # 附带下标
zip(a, b, strict=True)       # 并行迭代；strict 长度不等即报错（3.10+）
reversed(seq)                # 反向迭代器
sorted(it, key=..., reverse=True)   # 返回新列表
any(pred(x) for x in it)     # 存在真值
all(pred(x) for x in it)     # 全部为真
next(it, None)       # 手动推进迭代器，可给默认值
iter(obj)                    # 获取迭代器
aiter(ait) / anext(ait, None)   # 异步版 iter/next（3.10+）：需 await，如 await anext(ait)
```

**陷阱**: `zip` 默认长度不齐时**静默截断**，要求严格对齐传 `strict=True`。

---

## 4. 对象内省

```python
type(obj)                    # 精确类型
isinstance(obj, (int, float))   # 类型判断（含子类）
issubclass(Child, Parent)
hasattr(obj, "name") / getattr(obj, "name", default) / setattr(obj, "name", v)
callable(obj)                # 是否可调用
id(obj)                      # 身份（CPython 中即内存地址）
hash(obj)                    # 哈希值；可哈希才能作 dict 键
dir(obj)                     # 属性列表
vars(obj)                    # 实例 __dict__
object()                     # 万类之根：<object object ...>；无 __dict__，不能动态加属性（实测 AttributeError）
delattr(obj, "name")         # 删除属性，等价 del obj.name
```

类定义期四件套（实测行为）：

```python
class Temperature:
    def __init__(self, celsius=0.0):
        self._c = celsius

    @property
    def c(self): return self._c                      # 读：t.c
    @c.setter
    def c(self, v): self._c = v                      # 写：t.c = 30

    @classmethod
    def from_f(cls, f): return cls((f - 32) * 5 / 9) # 备选构造器：Temperature.from_f(212).c → 100.0

    @staticmethod
    def describe(): return "摄氏温度封装"               # 无 self/cls 的相关函数

class Kelvin(Temperature):
    def __init__(self, k):
        super().__init__(k - 273.15)                 # super()：调父类实现（实测 373.15 → 100.0）
```

继承、MRO 与 `super()` 的完整展开见[类与继承](./16-classes-and-inheritance.md)。

**陷阱**: `type(x) == int` 不认子类，需要接受子类时用 `isinstance`；只接受精确类型时可用 `type(x) is int`，例如排除作为 int 子类的 bool。

---

## 5. 作用域与执行

```python
globals() / locals()         # 名字空间字典
eval("1 + 2")                # 执行表达式 —— 慎用
exec("x = 1")                # 执行语句 —— 更慎用
compile(src, "<s>", "eval")
__import__("math")           # import 语句的底层接口；动态导入场景见[模块与导入系统](./11-modules-imports.md)
```

**陷阱**: `eval`/`exec` 处理外部输入等于任意代码执行漏洞，业务代码禁用。

---

## 6. 输入输出与调试

```python
print(*values, sep=", ", end="\n", file=sys.stdout, flush=False)
input(prompt)                # 返回 str，永远不带类型转换
help(obj)                    # 交互式文档
breakpoint()                 # 进入调试器（默认 pdb；由 PYTHONBREAKPOINT / sys.breakpointhook 控制）
open(path, mode="r", encoding="utf-8")   # 文件，一律显式 encoding
format(value, spec)          # 等价 f-string 的 format 规格
```

**陷阱**: `input` 返回字符串，`int(input())` 在非数字输入时抛异常；文本模式的默认编码受 Python 版本、UTF-8 模式和系统区域设置影响；双方约定 UTF-8 时显式写 `encoding="utf-8"`，二进制模式不传 encoding。

---

## 7. 属性与协议触发表

| 内置函数 | 实际调用的魔术方法 |
|------|------|
| `len(x)` | `__len__` |
| `iter(x)` / for 循环 | `__iter__` / `__getitem__` |
| `next(it)` | `__next__` |
| `x[a]` | `__getitem__` |
| `str(x)` | `__str__`（缺省回落 `__repr__`） |
| `repr(x)` | `__repr__` |
| `bool(x)` / if 判断 | `__bool__`（缺省回落 `__len__`） |
| `with x as f` | `__enter__` / `__exit__` |

理解此表等于理解 Python 的协议驱动设计，详见[魔术方法与协议](./04-oop-protocols.md)。

---

## 8. 高频组合模式

```python
# 计数统计（无 Counter 时）
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1

# 优雅排序
ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

# 分组索引
by_dept: dict[str, list] = {}
for emp in employees:
    by_dept.setdefault(emp.dept, []).append(emp)

# 批量转换
nums = list(map(int, raw_strings))    # 等价 [int(s) for s in raw_strings]
```

---

## 陷阱速查表

| 陷阱 | 说明 |
|------|------|
| `round` 银行家舍入 | `round(0.5) == 0`，精确舍入用 `decimal` |
| `zip` 静默截断 | 加 `strict=True` |
| `open` 缺 encoding | 默认值依赖解释器与环境，文本交换应明确编码 |
| `isinstance` vs `type` | 判断类型用前者 |
| 可变对象做默认值 | 与内置无关但最高频，见[排查手册](../quick-references/02-troubleshooting.md) |

---

## 🔗 相关文档

- 📄 **[Python 关键字详解](./01-python-keywords.md)** — 与内置函数相对的保留字
- 📄 **[数据结构速查](./03-data-structures.md)** — 容器类型的完整操作面
- 📄 **[标准库导航](../library-guides/01-standard-library.md)** — 需要导入的能力清单


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)

本轮语义核对来源：[Python 内置函数签名](https://docs.python.org/3/library/functions.html)（2026-09-18；不等同于本地完整工程运行验证）。
