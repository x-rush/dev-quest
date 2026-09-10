# 魔术方法与协议 — 迭代器 / 上下文 / 描述符

## 概述

Python 的对象行为由双下划线方法（dunder methods）定义，语法结构（for/with/+）只是协议调用的糖。本条目按协议分组，给出触发场景、最小实现与陷阱。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#魔术方法` `#协议` `#迭代器` `#描述符` |
| **更新日期** | `2026年9月` |

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
class Point:
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:        # 定义了才可放入 set/dict 键
        return hash((self.x, self.y))

    def __lt__(self, other: "Point") -> bool:   # 使 sorted() 可用
        return (self.x, self.y) < (other.x, other.y)
```

**规则**: `__eq__` 与 `__hash__` 必须一致——相等的对象哈希必须相等；定义 `__eq__` 后默认 `__hash__` 被置 None（不可哈希），需要时必须同时实现。用 `@dataclass(order=True, eq=True)` 可自动生成。

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

**要点**: 只实现 `__getitem__` 就能 for 遍历与切片（回落机制）；`__bool__` 缺省回落 `__len__`（0 为假）。

---

## 5. 上下文管理协议

**定义**: `__enter__` 返回值绑定给 `as` 变量；`__exit__` 保证清理，返回 True 吞异常。

```python
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
| 定义 `__eq__` 忘 `__hash__` | 对象进 set/dict 键即 TypeError |
| 迭代器被复用 | 耗尽后为空；或 `__iter__` 每次返回新迭代器 |
| `__exit__` 返回 True | 静默吞掉所有异常 |
| `__getattribute__` 递归 | 内部用 `super().__getattribute__` |

---

## 🔗 相关文档

- 📄 **[函数与类](../../basics/04-functions-oop.md)** — 面向对象入门教程
- 📄 **[typing 注解全表](./05-typing-annotations.md)** — Protocol：协议的静态类型表达
- 📄 **[内置函数全表](./02-built-in-functions.md)** — 协议触发表（内置函数 ↔ dunder）
