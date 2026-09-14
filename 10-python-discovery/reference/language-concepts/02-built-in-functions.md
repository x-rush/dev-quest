# 内置函数全表（分类速查）

## 概述

Python 内置函数共 70 余个，无需导入即可使用。本表按用途分类，每个条目给出签名、示例与陷阱。可用 `dir(builtins)` 列出全部名字。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#内置函数` `#速查` `#标准库` |
| **更新日期** | `2026年9月` |

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
| `bytearray(b"ab")` | 可变字节串：支持原地增改（`ba[0] = 65` → `b'Abc'`） |
| `memoryview(obj)` | 零拷贝缓冲区视图；视图存活期间原对象禁止扩缩容（实测抛 `BufferError`），`mv.release()` 或 with 释放 |
| `slice(start, stop, step)` | 切片对象：`a[1:3]` 即 `a[slice(1, 3)]`，详见[数据结构速查](./03-data-structures.md) |

**陷阱**: `int("4.5")` 抛 `ValueError`（不像 JavaScript）；`int(float("4.9"))` 是截断为 4。

---

## 2. 数值与数学

```python
abs(-3.5)                    # 3.5
round(2.675, 2)              # 2.67 —— 银行家舍入（.5 取偶），非四舍五入
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
next(it, default=None)       # 手动推进迭代器，可给默认值
iter(obj)                    # 获取迭代器
aiter(ait) / anext(ait, default=None)   # 异步版 iter/next（3.10+）：需 await，如 await anext(ait)
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

**陷阱**: `type(x) == int` 不认子类，判断类型统一用 `isinstance`。

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

**陷阱**: `input` 返回字符串，`int(input())` 在非数字输入时抛异常；`open` 不写 `encoding` 在 Windows 上默认 GBK，跨平台文件必乱码。

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
counts = {w: words.count(w) for w in set(words)}

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
| `open` 缺 encoding | Windows 默认非 UTF-8 |
| `isinstance` vs `type` | 判断类型用前者 |
| 可变对象做默认值 | 与内置无关但最高频，见[排查手册](../quick-references/02-troubleshooting.md) |

---

## 🔗 相关文档

- 📄 **[Python 关键字详解](./01-python-keywords.md)** — 与内置函数相对的保留字
- 📄 **[数据结构速查](./03-data-structures.md)** — 容器类型的完整操作面
- 📄 **[标准库导航](../library-guides/01-standard-library.md)** — 需要导入的能力清单
