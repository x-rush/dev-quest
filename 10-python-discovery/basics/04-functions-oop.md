# 函数与类 — 函数、dataclass 与魔术方法入门

> **文档简介**: 系统掌握 Python 函数的参数设计、类的定义与 dataclass 数据建模，并认识魔术方法驱动的对象协议
>
> **目标读者**: 已理解变量与类型的开发者，准备进入 Python 的核心抽象层
>
> **前置知识**: 完成[变量与类型](./03-variables-types.md)，理解类型注解基本写法

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#函数` `#类` `#dataclass` `#魔术方法` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 设计位置/关键字/默认/可变参数混合的函数签名
- ✅ 定义类并实现 `__init__`、`__repr__` 等基础魔术方法
- ✅ 用 dataclass 消除样板代码建模数据
- ✅ 理解属性查找顺序，避开可变默认参数陷阱

---

## 1. 函数：参数系统的四种形态

```python
def send(
    to: str,                       # 位置参数
    subject: str,                  # 可作为关键字传入
    *,                             # * 之后的参数只能用关键字
    cc: list[str] | None = None,   # 关键字参数带默认值
    **headers: str,                # ** 收集任意关键字参数
) -> dict[str, object]:
    return {"to": to, "subject": subject, "cc": cc, "headers": headers}

msg = send("a@x.com", "hi", cc=["b@x.com"], priority="high")
```

要点：

- **`/` 与 `*`**：`/` 之前只能按位置传，`*` 之后只能按关键字传，中间两者皆可
- **默认值求值时机**：函数定义时求值**一次**，因此默认值绝不能是可变对象
- **类型注解**：参数与返回值都标注，`**headers: str` 表示值为 str 的字典

**可变默认参数陷阱**（Python 面试第一题）：

```python
def add_tag(tag: str, tags: list[str] = []):   # ❌ 所有调用共享同一个列表
    tags.append(tag)
    return tags

def add_tag(tag: str, tags: list[str] | None = None):  # ✅ 标准解法
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
```

更深入的错误案例见[常见错误排查](../reference/quick-references/02-troubleshooting.md)。

---

## 2. 类：定义你自己的类型

```python
class Bookmark:
    """书签实体：演示类的标准写法。"""

    total = 0                      # 类属性：所有实例共享

    def __init__(self, title: str, url: str) -> None:
        self.title = title         # 实例属性
        self.url = url
        Bookmark.total += 1

    def describe(self) -> str:     # 实例方法第一个参数恒为 self
        return f"[{self.title}]({self.url})"

    @classmethod
    def from_raw(cls, raw: str) -> "Bookmark":
        """工厂方法：cls 指向当前类。"""
        title, url = raw.split("|")
        return cls(title, url)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """工具函数：不接收 self/cls。"""
        return url.startswith(("http://", "https://"))


bm = Bookmark("Python", "https://python.org")
print(bm.describe())                    # [Python](https://python.org)
bm2 = Bookmark.from_raw("uv|https://astral.sh")
```

要点：

- `self` 显式写在参数里，是方法而非语法的体现
- `__init__` 只负责初始化已创建好的对象，`__new__` 才创建对象（极少自定义）
- 单下划线前缀 `self._cache` 是"内部使用"约定（无强制私有）

---

## 3. dataclass：数据建模的默认选择

纯存数据的类，用 `@dataclass` 自动生成 `__init__`/`__repr__`/`__eq__`：

```python
from dataclasses import dataclass, field

@dataclass
class Bookmark:
    title: str
    url: str
    tags: list[str] = field(default_factory=list)   # 可变默认值的正确姿势
    pinned: bool = False

bm = Bookmark("uv", "https://astral.sh")
print(bm)                # Bookmark(title='uv', url='https://astral.sh', ...)
print(bm == Bookmark("uv", "https://astral.sh"))   # True，按字段比较
```

常用变体：

| 装饰器 | 作用 |
|------|------|
| `@dataclass(frozen=True)` | 实例不可变，可哈希、可作 dict 键 |
| `@dataclass(order=True)` | 生成 `<`、`>=` 等比较方法 |
| `@dataclass(slots=True)` | 启用 `__slots__`，省内存、禁止动态属性 |

> 💡 与 Pydantic 模型的分工：dataclass 管"程序内部数据"，Pydantic 管"边界校验"（API 输入/配置文件），见 [FastAPI 速查](../reference/framework-essentials/01-fastapi-essentials.md)。

---

## 4. 魔术方法：协议驱动的世界

Python 对象行为由双下划线"魔术方法"定义，框架和内置语法都在调用它们：

```python
class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y

    def __repr__(self) -> str:            # repr(v) / REPL 显示
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other: "Vector") -> "Vector":   # v1 + v2
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other: object) -> bool:          # v1 == v2
        return isinstance(other, Vector) and (self.x, self.y) == (other.x, other.y)

    def __len__(self) -> int:             # len(v)
        return 2

    def __getitem__(self, i: int) -> float:           # v[0]，顺带获得可迭代性
        return (self.x, self.y)[i]
```

`v1 + v2` 并非语法糖的偶然：解释器将其翻译为 `v1.__add__(v2)`。完整协议目录见[魔术方法与协议](../reference/language-concepts/04-oop-protocols.md)。

**入门必会的五个**：

| 魔术方法 | 触发场景 |
|------|------|
| `__init__` | 实例初始化 |
| `__repr__` | 调试显示（建议总是实现） |
| `__eq__` | `==` 比较 |
| `__len__` / `__bool__` | `len()` / `if obj:` |
| `__getitem__` | 下标访问与 for 遍历 |

---

继承用"单继承 + 组合"：子类在 `__init__` 中以 `super().__init__(title, url)` 复用父类初始化；需要鸭子类型灵活性时改用 `typing.Protocol`（见 [typing 注解全表](../reference/language-concepts/05-typing-annotations.md)）。

---

## ✅ 最佳实践

- ✅ **数据类一律 dataclass**，手写 `__init__` 仅在行为复杂时
- ✅ **可变默认值用 `field(default_factory=list)`** 或 `None` 哨兵
- ✅ **总实现 `__repr__`**（dataclass 自动生成），调试效率翻倍
- ❌ **避免**：写 Java 式 getter/setter——Python 用 `@property` 或直接暴露属性
- 💡 **技巧**：`dataclasses.asdict(bm)` 一键转字典，配合 json 序列化

---

## ❓ 常见问题

### Q1: `@staticmethod` 和模块级函数怎么选？
**A**: 与类有概念关联但不用实例/类状态的工具放 `@staticmethod`；否则直接写模块级函数，Python 不强制一切皆方法。

---

## 🎯 练习与实践

### 练习一：参数设计
1. 编写 `create_user(name: str, /, email: str, *, role: str = "member") -> dict`，分别用位置、关键字混合方式调用验证 `/` 与 `*` 的限制

### 练习二：建模购物车
1. 用 `@dataclass` 实现 `Item(name: str, price: float, qty: int)`
2. 实现 `Cart` 类：`add(item)`、`total() -> float`、魔术方法 `__len__`
3. 让 `Cart` 支持 `for item in cart`（`__getitem__` 或 `__iter__`）

**评估标准**：`uv run python -c "from cart import Cart; c = Cart(); print(len(c))"` 正常输出，且 ruff/mypy 无告警。

---

## 🔗 相关文档

- 📄 **[控制流与推导式](./05-control-flow.md)** — 让自定义类型融入 for 循环世界
- 📄 **[魔术方法与协议](../reference/language-concepts/04-oop-protocols.md)** — 迭代器/上下文/描述符全协议
- 📄 **[内置函数全表](../reference/language-concepts/02-built-in-functions.md)** — `isinstance`、`len` 等如何触发协议
