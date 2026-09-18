# enum — 枚举类型

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#enum` `#枚举` `#IntEnum` `#StrEnum` `#常量` `#状态机` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

enum 用"有限的、命名的常量集合"替代裸字符串与魔法数字：`OrderState.SHIPPED` 可读、可被 IDE 重构、拼错在定义处就报错。成员是**单例**，普通 Enum 的默认相等语义基于成员身份，可用 == 比较成员——`Color.RED == 1` 为 `False`（实测），这是特性：防止枚举与裸值混用。状态、方向等有限集合可以使用枚举；开放字符串集合或简单布尔开关未必需要单独建枚举。

## 📖 语法 / 详解

### 定义与成员

```python
from enum import Enum, auto

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = auto()          # 接续上一成员：3
```

成员三要素：`Color.RED.name` → `'RED'`，`Color.RED.value` → `1`，身份全局唯一。

### 成员访问与比较

```python
Color.RED is Color(1)        # True：按值反查（实测）
Color["RED"] is Color.RED    # True：按名查（实测）
Color.RED == 1               # False：与裸值比较永假（实测）
Color.RED is Color.RED       # True：身份比较
Color.RED in Color           # True：成员判断（实测）
{Color.RED: "stop"}[Color.RED]   # 可哈希，可作字典键
list(Color)                  # [Color.RED, Color.GREEN, Color.BLUE] 按定义序遍历
```

### 混入型：IntEnum / StrEnum（3.11+）

```python
from enum import IntEnum, StrEnum

class Level(IntEnum):
    LOW = 1
    HIGH = 2

Level.HIGH > Level.LOW       # True：可与 int 比较、排序（实测）
int(Level.HIGH)              # 2

class Format(StrEnum):
    TEXT = "text"

str(Format.TEXT)             # 'text'：f"{Format.TEXT}" 直接插值（实测）
```

`IntEnum` 适合持久化/协议编码，`StrEnum` 适合替代字符串常量（header 名、状态标签）。普通 Enum 与 int/str **不**互通——这是防误用的特性，需要互操作时才选混入型。

### 别名、@unique 与 @verify

```python
class Loose(Enum):
    A = 1
    B = 1            # 不报错：B 成为 A 的别名（实测 Loose.B is Loose.A，遍历只出 1 个）

from enum import unique, verify, UNIQUE, CONTINUOUS

@unique
class Strict(Enum):
    A = 1
    B = 1            # ValueError: duplicate values found in <enum 'Strict'>: B -> A（实测）
```

`@unique` 等价于 `@verify(UNIQUE)`；`CONTINUOUS` 检查整数成员值是否连续，不限于 auto 生成的值。别名机制本身合法——可用于给旧名起文档化新名。

### 枚举方法与属性

成员 value 可以是元组，配合自定义 `__init__` 拆成属性（官方 Planet 模式，实测）：

```python
class Planet(Enum):
    MERCURY = (3.303e+23, 2.4397e6)
    EARTH = (5.976e+24, 6.37814e6)

    def __init__(self, mass, radius):    # 每个成员的 value 元组拆入 __init__
        self.mass = mass
        self.radius = radius

    def surface_gravity(self):
        G = 6.67300E-11
        return G * self.mass / (self.radius ** 2)

round(Planet.EARTH.surface_gravity(), 1)   # 9.8
```

### 函数式 API

```python
Status = Enum("Status", "OK FAIL")                        # 空格分隔名（实测）
HttpStatus = Enum("HttpStatus", [("OK", 200), ("NOT_FOUND", 404)])   # 名值对（实测）
```

适合配置驱动、动态生成；常规代码用 class 语法更可读。

## 💡 示例

订单状态机：StrEnum + auto()（值自动取小写成员名，实测 `['pending', 'shipped']`）：

```python
from enum import StrEnum, auto

class OrderState(StrEnum):
    PENDING = auto()      # 值 = 'pending'
    SHIPPED = auto()      # 值 = 'shipped'

def ship_action(state: OrderState) -> str:
    if state is OrderState.PENDING:      # 身份比较
        return "立即发货"
    return "查看物流"

ship_action(OrderState.PENDING)          # '立即发货'
f"state={OrderState.SHIPPED}"            # 'state=shipped' —— JSON/日志友好（实测）
```

## ⚠️ 常见陷阱

- ❌ **用字符串比较写状态分支**：`if status == "pending"` 拼错无警告、无补全。
  ✅ `if status is OrderState.PENDING`；外部输入先调用 OrderState(value) 并处理 ValueError；函数注解本身不会挡住非法值。
- ❌ **期待 `Color.RED == 1` 为 True**：普通 Enum 与裸值永不相等（实测 False）。
  ✅ 需要 int 互操作用 `IntEnum`，或显式取 `.value`。
- ❌ **重复 value 当两个成员用**：第二个静默变成别名（实测）。
  ✅ 加 `@unique` 强制唯一；确实要别名时写注释说明新旧名关系。
- ❌ **动态名/值查询不设防**：`Color["PURPLE"]` 抛 KeyError、`Color(99)` 抛 ValueError（实测）。
  ✅ 先查 `"PURPLE" in Color.__members__` 或用 try/except 包住反查。
- ❌ **在业务代码里用 `range(len(...))` 遍历成员**：绕开枚举抽象。
  ✅ 直接 `for member in Color` 或 `list(Color)`，按定义序迭代。

<!-- full-library-explanation -->
## 在输入边界把字符串转换为枚举

前置知识是类、比较和异常。枚举让合法状态有明确名字，但不会自动限制一个普通函数的实际参数。来自 JSON 的字符串需要显式转换，再进入只处理枚举的业务函数。

完整实验保存为 `states.py`，Python 3.11+ 运行：

```python
from enum import StrEnum

class State(StrEnum):
    PENDING = "pending"
    SHIPPED = "shipped"

print(State("pending") is State.PENDING)
print(State.PENDING == "pending")
try:
    State("unknown")
except ValueError:
    print("invalid state")
```

输出 `True`、`True`、`invalid state`。StrEnum 故意保留字符串互操作性，因此不能套用“枚举永远不等于裸值”的说法。

练习：即使 pending 与 shipped 都是合法成员，从 shipped 再次发货是否合理？枚举只限制状态集合，状态转移还需要业务规则，重复发货的幂等处理也需要单独设计。

## 🔗 相关条目

- 📄 **[dataclass 数据类](../language-concepts/13-dataclasses.md)** — 枚举字段 + frozen 数据模型的常见组合
- 📄 **[类型注解全表](../language-concepts/05-typing-annotations.md)** — `Literal` 与 Enum 的分工对比
- 📄 **[标准库导航](./01-standard-library.md)** — 标准库场景地图
- 🌐 **[官方文档：enum](https://docs.python.org/3/library/enum.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
