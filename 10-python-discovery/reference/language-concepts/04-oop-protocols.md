# 魔术方法与协议 — 迭代器 / 上下文 / 描述符

## 概述

Python 的对象行为由双下划线方法（dunder methods）定义，语法结构（for/with/+）只是协议调用的糖。本条目按协议分组，给出触发场景、最小实现与陷阱。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#魔术方法` `#协议` `#迭代器` `#描述符` |
| **更新日期** | `2026年9月` |

</details>

## 协议总览

| 协议 | 核心方法 | 触发语法 |
|------|---------|---------|
| 对象创建 | `__new__` `__init__` `__del__` | `Obj(...)` |
| 表示 | `__repr__` `__str__` | `repr()` / `str()` / print |
| 比较 | `__eq__` `__lt__` `__hash__` | `==` `<` hash() |
| 容器 | `__len__` `__getitem__` `__contains__` | `len()` `x[k]` `in` |
| 迭代 | `__iter__` `__next__` | for / next() |
| 可调用 | `__call__` | `obj()` |
| 数值 | `__add__` `__mul__` 等 | `+` `*` |
| 上下文 | `__enter__` `__exit__` | with |
| 属性 | `__getattr__` `__setattr__` `__getattribute__` | `obj.attr` |
| 描述符 | `__get__` `__set__` | 类属性访问 |

---

## 1. 创建与表示

```python
class Point:
    def __init__(self, x: float, y: float) -> None:   # 初始化（对象已由 __new__ 创建）
        self.x, self.y = x, y

    def __repr__(self) -> str:                        # 调试表示，应无歧义；未定义 __str__ 时 str() 回落至此
        return f"Point({self.x!r}, {self.y!r})"
```

**陷阱**: 只实现 `__str__` 不实现 `__repr__`，容器打印时显示 `<Point object at 0x...>`——`__repr__` 优先实现。

---

## 2. 比较与哈希

```python
from dataclasses import dataclass

@dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int

print(Point(1, 2) == Point(1, 2))  # True
print(len({Point(1, 2), Point(1, 2)}))  # 1
```

**规则**：相等对象必须有相等哈希值；作为集合元素或字典键期间，参与哈希的状态不能变化。上例用整数和冻结字段保持该约束。默认可变 dataclass 通常不可哈希；`order=True` 本身不会生成可用哈希。手写 `__eq__` 遇到不支持的类型时可返回 `NotImplemented`，让对方的比较实现有机会参与。

---

## 3. 迭代器协议

**定义**: `__iter__` 返回迭代器；`__next__` 产出下一个值，耗尽抛 `StopIteration`。

```python
class Countdown:
    def __init__(self, n: int) -> None:
        self.n = n

    def __iter__(self) -> "Countdown":       # 迭代器协议入口
        return self

    def __next__(self) -> int:
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1

for x in Countdown(3): ...    # 3, 2, 1
```

**要点**:
- 只需遍历的实现用**生成器函数**（`yield`）替代整个类；迭代器一次性耗尽，`__iter__` 返回 `self` 的类被 for 两次会第二次为空
- 可迭代（`__iter__`）与迭代器（`__iter__`+`__next__`）是两个概念：list 可迭代但不是自己的迭代器

---

## 4. 容器协议

```python
class Playlist:
    def __init__(self, songs: list[str]) -> None:
        self._songs = songs

    def __len__(self) -> int:
        return len(self._songs)

    def __getitem__(self, index: int) -> str:     # 支持 p[0]、切片、甚至 for
        return self._songs[index]

    def __contains__(self, song: str) -> bool:    # 支持 in；if p: 回落 __len__（0 为假）
        return song in self._songs
```

**要点**: 按序列约定实现 `__getitem__` 可支持 for 的索引回退；切片还要求实现能够接收并处理 slice 对象；`__bool__` 缺省回落 `__len__`（0 为假）。

---

## 5. 上下文管理协议

**定义**: `__enter__` 返回值绑定给 `as` 变量；`__exit__` 保证清理，返回 True 吞异常。

```python
import time

class Timer:
    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.cost = time.perf_counter() - self.start
        return False    # 不吞异常（True 会静默，慎用）
```

简化方案：`@contextmanager` 装饰器或继承 `contextlib.AbstractContextManager`。

---

## 6. 描述符协议（property 的底层机制）

**定义**: 类属性级协议，`__get__`/`__set__`/`__delete__` 拦截属性访问。

```python
class Positive:
    def __set_name__(self, owner, name: str) -> None:   # 自动记录属性名
        self.name = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name)

    def __set__(self, obj, value: float) -> None:
        if value <= 0:
            raise ValueError(f"{self.name[1:]} 必须为正数")
        setattr(obj, self.name, value)

class Product:
    price = Positive()      # price 赋负数会抛 ValueError
```

**要点**:
- `@property` = 数据描述符的语法糖， getter/setter 场景优先用它
- 描述符定义在**类**上，拦截**实例**的属性访问；框架（ORM 字段、校验器）大量使用
- 查找顺序：数据描述符 → 实例 `__dict__` → 非数据描述符/类属性

---

## 陷阱速查表

| 陷阱 | 说明 |
|------|------|
| 只写 `__str__` | 容器/调试场景仍显示内存地址，补 `__repr__` |
| 为可变值对象强加哈希 | 不可哈希往往是正确选择；只有能保证哈希状态稳定时才设计哈希实现 |
| 迭代器被复用 | 耗尽后为空；或 `__iter__` 每次返回新迭代器 |
| `__exit__` 返回 True | 静默吞掉所有异常 |
| `__getattribute__` 递归 | 内部用 `super().__getattribute__` |

---

<!-- full-library-explanation -->
## 协议是调用约定，不是方法名的装饰

前置知识是实例、方法与异常。实现 `__len__` 后，`len(obj)` 会按语言协议调用它；实现 `__getitem__` 后，索引访问会传入整数或切片对象。方法必须满足相应契约，例如长度为非负整数，序列索引耗尽时抛出 `IndexError`，不能只定义同名方法而返回任意值。

完整实验保存为 `protocol.py`，运行 `python protocol.py`：

```python
class Playlist:
    def __init__(self, songs):
        self.songs = list(songs)
    def __len__(self):
        return len(self.songs)
    def __getitem__(self, index):
        return self.songs[index]

p = Playlist(["intro", "outro"])
print(len(p), bool(p))
print(list(p))
print(p[:1])
```

输出 `2 True`、`['intro', 'outro']`、`['intro']`。这里切片能工作，是因为方法把 `slice` 对象交给了内部列表，不是所有自定义 `__getitem__` 都天然支持切片。练习：改为只接受整数并对其他类型抛 `TypeError`，解释为什么遍历仍可工作而切片失败。

## 🔗 相关文档

- 📄 **[函数与类](../../basics/04-functions-oop.md)** — 面向对象入门教程
- 📄 **[typing 注解全表](./05-typing-annotations.md)** — Protocol：协议的静态类型表达
- 📄 **[内置函数全表](./02-built-in-functions.md)** — 协议触发表（内置函数 ↔ dunder）


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
