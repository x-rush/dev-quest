# dataclass 数据类 — field / frozen / order / slots

## 概述

`@dataclass` 自动生成 `__init__`/`__repr__`/`__eq__`，是纯数据建模的默认选择（教程见 [函数与类](../../basics/04-functions-oop.md)）。本条目覆盖字段级控制 `field()`、装饰器参数与序列化工具。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#dataclass` `#field` `#frozen` `#slots` `#建模` |
| **更新日期** | `2026年9月` |

## 装饰器参数总表

| 参数 | 默认 | 作用 |
|------|------|------|
| `frozen=True` | `False` | 实例不可变：赋值抛 `FrozenInstanceError`；获得 `__hash__`，可入 set/dict 键 |
| `order=True` | `False` | 生成 `__lt__`/`__le__`/`__gt__`/`__ge__`，按字段声明顺序比较，可直接 `sorted()` |
| `slots=True` | `False` | 生成 `__slots__`：省内存、属性访问更快、禁止动态新增属性 |
| `kw_only=True` | `False` | 全部字段仅限关键字传参（多布尔参数的函数签名防呆） |
| `init`/`repr`/`eq` | `True` | 对应魔术方法的生成开关 |

---

## 1. 基本用法与默认值

```python
from dataclasses import dataclass, field

@dataclass
class Bookmark:
    title: str
    url: str
    tags: list[str] = field(default_factory=list)   # 可变默认值的唯一正确姿势
    pinned: bool = False

bm = Bookmark("uv", "https://astral.sh")
print(bm)                 # Bookmark(title='uv', url='https://astral.sh', tags=[], pinned=False)
print(bm == Bookmark("uv", "https://astral.sh"))   # True：eq 按字段逐个比较
```

**陷阱**: `tags: list[str] = []` 直接写可变字面量会在类定义时抛 `ValueError: mutable default ... use default_factory`；不可变默认值（str/int/bool/None）才允许直接写 `=`。

---

## 2. field() 参数全表

```python
@dataclass
class Doc:
    id: int = field(compare=True)                 # 参与 == 与排序（默认即 True）
    body: str = field(default="", repr=False)     # 不进 repr：敏感/超大字段
    seq: int = field(default=0, init=False)       # 不进 __init__，类内计算
    uuid: str = field(default_factory=lambda: uuid4().hex)  # 每实例独立求值
    label: str = field(default="", metadata={"json": "label_name"})  # 自定义元数据
```

| 参数 | 作用 |
|------|------|
| `default` | 不可变默认值 |
| `default_factory` | 零参工厂：`list`/`dict`/`set`/lambda，每实例新建 |
| `repr=False` | 该字段不出现在 `__repr__` |
| `compare=False` | 该字段不参与 `__eq__` 与排序 |
| `init=False` | 不进 `__init__` 签名 |
| `metadata` | 任意只读映射，供序列化库读取 |

---

## 3. frozen：不可变与哈希

```python
@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
p.x = 9            # FrozenInstanceError
hash(p)            # 可哈希：可入 set、作 dict 键
{p, Point(1, 2)}   # 值相等的实例去重为 1 个
```

**陷阱**: `frozen=True` 只是拦截 `__setattr__`，字段若持有可变对象（如 `list`），其内容仍可被原地修改——需要深度不可变时字段用 tuple/frozenset。

---

## 4. order 与 slots

```python
@dataclass(order=True)
class Task:
    priority: int                      # 首字段即主排序键
    title: str = field(compare=False)  # 比较时忽略

sorted([Task(2, "b"), Task(1, "a")])   # [Task(1, 'a'), Task(2, 'b')]

@dataclass(slots=True)
class Slim:
    x: int = 0

s = Slim()
s.y = 1            # AttributeError：slots 禁止动态属性
```

**陷阱**: `slots=True` 会重建类，`frozen` 的 `__setattr__` 需同时声明（`@dataclass(frozen=True, slots=True)`）；slots 类不再有 `__dict__`，依赖它的代码（如 `vars(obj)`）会失效。

---

## 5. 序列化与复制工具

```python
from dataclasses import asdict, astuple, replace, fields

asdict(bm)              # 递归转 dict（嵌套 dataclass/list 一起转）
astuple(bm)             # 递归转 tuple
replace(bm, title="rx") # 拷贝并替换指定字段，原对象不动
fields(Doc)             # (Field, ...) 内省字段定义
```

> 💡 **与 Pydantic 分工**：dataclass 管"程序内部数据"，Pydantic v2 管"边界校验"（API 输入/配置），见 [FastAPI 速查](../framework-essentials/01-fastapi-essentials.md)。二者模型互转可用 `TypeAdapter` 或 `dataclasses.asdict` 过桥。

---

## 🔗 相关文档

- 📄 **[函数与类](../../basics/04-functions-oop.md)** — dataclass 入门教程与建模练习
- 📄 **[魔术方法与协议](./04-oop-protocols.md)** — 自动生成的 `__init__`/`__repr__`/`__eq__` 背后的协议
- 📄 **[类型注解全表](./05-typing-annotations.md)** — 字段注解的进阶写法
