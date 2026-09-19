# 类与继承 — MRO、super 与 __slots__

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#类` `#继承` `#MRO` `#super` `#slots` `#Mixin` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

`class` 定义可调用的类型，实例化就是调用类本身（`Dog("旺财")` → `type.__call__` → `__new__` 创建实例 + `__init__` 初始化）。继承建立"属性查找的回退链"，链的顺序由 **MRO**（Method Resolution Order，C3 线性化）唯一确定；`super()` 的含义不是"我的父类"，而是"**沿 MRO 找下一个类**"——这是多重继承与 Mixin 能正确协作的基石。魔术方法背后的协议见 [04-oop-protocols](./04-oop-protocols.md)。

## 📖 语法 / 详解

### 类定义与实例化

```python
class Animal:                        # 不写基类时隐式继承 object
    kind = "animal"                  # 类属性：所有实例共享一份

    def __init__(self, name: str):   # 初始化钩子（不是构造本身）
        self.name = name             # 实例属性：写入实例自己的存储

a = Animal("旺财")
a.name          # 实例属性
a.kind          # 类属性（实例未覆盖时回退到类）
```

### 属性查找顺序

对普通属性，可用“先实例存储，再沿类的 MRO”理解；数据描述符（如带 setter 的 property）会优先于实例字典，__getattribute__ 也可定制查找行为。`a.name = "x"` 只写实例层，不碰类；实例属性被 `del` 后回退到类属性。执行本节片段检查：`k.x = 2` 后 `k.x` 为 2 而 `K().x` 仍为 1；`del k.x` 后再读应回退到类属性 1。

### MRO：C3 线性化

```python
class A:
    def who(self): return "A"

class B(A):
    def who(self): return "B|" + super().who()

class C(A):
    def who(self): return "C|" + super().who()

class D(B, C):
    def who(self): return "D|" + super().who()

D.mro()      # 预期为 [<class D>, <class B>, <class C>, <class A>, <class 'object'>]
D().who()    # 'D|B|C|A' —— 每个类的方法恰好参与一次
```

C3 线性化保证三条不变式：**子类总排在父类之前；多父类按声明顺序；每个类只出现一次**。声明顺序冲突时类无法创建；运行下例观察 `TypeError`：

```python
class X(B, A, C): pass
# TypeError: Cannot create a consistent method resolution order (MRO) for bases A, ...
```

### super() 的真实语义

`super().method()` = 在“**当前类在 MRO 中的位置**”之后继续找 `method`——不是“直接父类”。菱形结构靠它实现每层只执行一次的协作式初始化；运行下例确认输出顺序是否为 Child → Left → Right → Base。这里的 `**kw` 必须在到达 `object.__init__` 前被某一层消费；本例为空所以可以原样传到底：

```python
class Base:
    def __init__(self, **kw):
        print("Base"); super().__init__(**kw)     # object.__init__ 兜底

class Left(Base):
    def __init__(self, **kw):
        print("Left"); super().__init__(**kw)     # 沿 MRO 走到 Right，不是 Base！

class Right(Base):
    def __init__(self, **kw):
        print("Right"); super().__init__(**kw)

class Child(Left, Right):
    def __init__(self, **kw):
        print("Child"); super().__init__(**kw)

Child()    # Child → Left → Right → Base：每个类只初始化一次
```

### 多重继承与 Mixin

Mixin 是"提供行为、不单独实例化"的小类，排在基类列表**前面**：

```python
import json

class JsonMixin:
    def to_json(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)

class User(JsonMixin):                  # 行为在前，业务基类在后
    def __init__(self, name: str):
        self.name = name

User("ada").to_json()                   # 预期 '{"name": "ada"}'
```

组合原则：Mixin 放前、业务基类在后；Mixin 之间不互相依赖；需要的状态由宿主类提供。

### __slots__

```python
class Slim:
    __slots__ = ("x", "y")              # 声明全部实例属性

s = Slim()
s.x = 1
s.z = 3                   # 预期 AttributeError：没有 z 属性且没有 __dict__
hasattr(s, "__dict__")    # False —— 不再为每个实例挂属性字典
```

收益：可减少每实例的字典开销，属性访问有时更快；具体字节数取决于 Python 版本、构建和平台，需用 `sys.getsizeof` 在目标环境测量。dataclass 一行开启：`@dataclass(slots=True)`，详见 [13-dataclasses](./13-dataclasses.md)。

### object 基类

一切类的终点。常用兜底实现：`__init__`（无参）、`__repr__`、`__eq__`（默认身份比较）、`__hash__`（默认基于身份，数值不等同于 id）、`__str__`（默认同 `__repr__`）。覆写 `__eq__` 时记得同步考虑 `__hash__`（详见 [04-oop-protocols](./04-oop-protocols.md)）。

## 💡 示例

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return "..."

class Dog(Animal):
    def speak(self) -> str:                    # 重写
        return f"汪({self.name})"

    def fetch(self) -> str:                    # 扩展
        return f"{self.name} 捡回来了"

dog = Dog("旺财")
dog.speak()                  # '汪(旺财)'
dog.fetch()                  # '旺财 捡回来了'
isinstance(dog, Animal)      # True
[c.__name__ for c in Dog.mro()]   # ['Dog', 'Animal', 'object']
```

## ⚠️ 常见陷阱

- ❌ **子类重写 `__init__` 忘调 `super().__init__()`**：基类负责的字段全部缺失。
  ✅ 若基类契约需要初始化，应在合适位置调用 super 并按约定传参；不必把“首行”当成语言规则。
- ❌ **可变类属性当“实例默认值”**：`class C: items = []`，一个实例 `append` 后全体实例都会看到同一列表；运行小片段确认共享行为。
  ✅ 实例状态放 `__init__`：`self.items = []`；类属性只放真常量与配置。
- ❌ **把 super() 当"直接父类"手动指定**：`super(B, self).method()` 跳层只在明确意图时使用，乱用会漏初始化。
  ✅ 默认零参 `super()`，交给 MRO 协作分发。
- ❌ **只给继承链上某一层声明 `__slots__`**：子类没声明就仍有 `__dict__`，省内存效果失效；`vars(obj)` 等依赖 `__dict__` 的代码对 slots 实例直接报错。
  ✅ 整条继承链都声明 `__slots__`（纯继承层写 `__slots__ = ()`）。
- ❌ **Mixin 里塞业务状态或构造依赖**：宿主类被隐式绑架，继承顺序一换就崩。
  ✅ Mixin 只依赖文档声明的接口；需要约定属性存在时用注解表达。

<!-- full-library-explanation -->
## 沿调用链检查协作，而不是背继承图

前置知识是实例方法与函数覆盖。阅读多重继承时，先打印 `type(obj).__mro__`，再沿每个 `super()` 继续寻找方法。一个类如果直接调用固定父类，或没有继续调用 super，协作链就可能提前结束。

用上文 A/B/C/D 示例，在文件末尾添加 `print(D().who())`，输出应为 `D|B|C|A`。练习：将 B 的实现改为直接 `return "B|" + A.who(self)`，输出将变成 `D|B|A`，C 被跳过。这说明 super 的价值在于遵守实际实例的解析顺序，而不是缩写某个父类名。

继承用于表达可替换的行为关系；若只是希望借用一个功能，也可让实例持有另一个对象并调用它。比如业务服务持有存储对象，测试时替换存储实现，比让业务服务继承数据库客户端更容易明确职责。

<!-- node-python-p1-next-case: python-class-mro-slots -->
下面是可直接运行的最小验证，保存为 `class-contracts.py` 后执行 `python class-contracts.py`。它覆盖菱形 MRO 中的协作式 `super()`，并确认 `__slots__` 禁止未声明属性；不会验证所有继承、描述符或序列化场景。

```python
class A:
    def who(self):
        return "A"

class B(A):
    def who(self):
        return "B|" + super().who()

class C(A):
    def who(self):
        return "C|" + super().who()

class D(B, C):
    def who(self):
        return "D|" + super().who()

class Slim:
    __slots__ = ("x",)

slim = Slim()
slim.x = 1
try:
    slim.extra = 2
except AttributeError:
    blocked = True
else:
    blocked = False

assert [cls.__name__ for cls in D.__mro__] == ["D", "B", "C", "A", "object"]
assert D().who() == "D|B|C|A"
assert blocked and not hasattr(slim, "__dict__")
print("class-contracts: D|B|C|A; slots block undeclared attributes")
```

## 🔗 相关条目

- 📄 **[魔术方法与协议](./04-oop-protocols.md)** — `__init__`/`__eq__`/`__hash__` 等协议全表
- 📄 **[dataclass 数据类](./13-dataclasses.md)** — `slots=True`、`order=True` 的声明式替代
- 📄 **[闭包与作用域](./15-closures-and-scope.md)** — 方法也是函数：self 同样遵循作用域规则
- 📄 **[函数参数全形态](./17-functions-parameters.md)** — `__init__` 的签名设计与仅关键字防呆
- 🌐 **[官方文档：Classes 教程](https://docs.python.org/3/tutorial/classes.html)** — 类、继承与作用域的权威讲解

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
