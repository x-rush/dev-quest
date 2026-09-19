# 变量与类型 — 动态类型、基本类型与 f-string

## 先理解，再动手

赋值把名字绑定到对象，两个名字可以指向同一个列表。不可变值的重新绑定与可变对象的原地修改需要分开理解。

**本节自测**：a=[1]，b=a；修改 b，再令 b 指向新列表，观察 a。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

append 会影响共享列表；重新绑定 b 不会把 a 一起改成新列表。

</details>

> **文档简介**: 掌握 Python 动态类型模型与六种常见基础类型，学会用类型注解约束变量、用 f-string 格式化输出
>
> **目标读者**: 已能运行脚本、想理解 Python 数据模型的开发者
>
> **前置知识**: 完成[第一个脚本](./02-first-script.md)，理解变量赋值与函数定义

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#动态类型` `#基本类型` `#f-string` `#类型注解` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 解释 Python "变量是标签，不是盒子"的对象模型
- ✅ 熟练使用 int/float/str/bool/None/bytes 及其常用操作
- ✅ 用 f-string 完成格式化、对齐与表达式插值
- ✅ 为变量与函数补充类型注解，避免 `Optional` 旧写法

---

## 1. 变量：贴在对象上的标签

Python 变量没有类型，**对象**才有。赋值是把名字绑定到对象：

```python
x = 42        # 名字 x 指向 int 对象 42
x = "hello"   # 现在 x 指向 str 对象 —— 完全合法
```

与 Go/Java 的区别：`int x = 42` 把盒子填成整数，之后只能装整数；而 Python 的 `x` 只是一个可反复改贴的标签。

```python
a = [1, 2, 3]
b = a          # b 与 a 指向同一个列表
b.append(4)
print(a)       # [1, 2, 3, 4] —— 同一对象被两个名字观察
```

> ⚠️ 这是 Python 新手第一大陷阱：赋值复制的是**引用**。需要独立副本时用 `b = a.copy()` 或 `b = list(a)`。

动态类型的代价是错误晚发现，所以现代 Python 靠**类型注解**找回编译期体验（见第 4 节）。

---

## 2. 六种常见基础类型

| 类型 | 示例 | 可变 | 说明 |
|------|------|------|------|
| `int` | `42`, `0x2A`, `1_000_000` | 否 | 任意精度，不会溢出 |
| `float` | `3.14`, `1e-3` | 否 | 双精度浮点，注意精度误差 |
| `str` | `"hello"`, `'单引号'` | 否 | Unicode 字符串，不可变 |
| `bool` | `True`, `False` | 否 | 是 `int` 的子类（`True == 1`） |
| `None` | `None` | — | 空值唯一实例，判等用 `is` |
| `bytes` | `b"\x00\xff"` | 否 | 字节序列，处理二进制数据 |

**不可变（immutable）** 意味着任何"修改"操作都返回新对象：

```python
s = "python"
s.upper()        # 返回 'PYTHON'，s 本身不变
s = s.upper()    # 必须重新绑定才"改变" s

print(10 / 3)    # 3.3333333333333335 真除法，永远得 float
print(10 // 3)   # 3 整除
print(10 % 3)    # 1 取余
print(2 ** 100)  # 1267650600228229401496703205376 大整数无上限
```

浮点精度是 IEEE 754 的固有行为：`0.1 + 0.2 == 0.3` 结果为 `False`。金额计算用 `decimal.Decimal`，科学计算用 `float`。

---

## 3. f-string：现代格式化的唯一答案

Python 3.12 起 f-string 支持嵌套引号与多行表达式，日常输出仍是首选的字符串插值方案：

```python
name, price, qty = "机械键盘", 399.5, 2

# 基本插值：{表达式}
print(f"{name} 单价 {price} 元")

# 表达式直接计算
print(f"合计 {price * qty:.2f} 元")       # 合计 799.00 元

# 对齐与填充：{值:填充符 对齐 宽度}
print(f"|{name:<10}|")      # 左对齐，宽 10
print(f"|{price:>10.1f}|")  # 右对齐，宽 10，保留 1 位小数
print(f"|{name:*^10}|")     # 居中，* 填充

# 调试三件套：= 语法输出表达式本身
print(f"{price=}, {qty=}")  # price=399.5, qty=2

# 千分位与百分号
print(f"{1234567:,}")     # 1,234,567
print(f"{0.856:.1%}")     # 85.6%
```

多行 f-string 与嵌套引号（3.12 新能力）：

```python
data = {"user": {"name": "ada"}}
print(f"用户名: {data["user"]["name"]}")  # 3.12 起允许内部再用双引号
```

**3.14 新增 t-string（PEP 750）**：`t"..."` 语法与 f-string 同形，但返回的不是 `str`，而是可延迟处理的模板对象——渲染交给库决定，适合 HTML 转义、SQL 参数化等防注入场景：

```python
title = "<script>攻击</script>"
template = t"<h1>{title}</h1>"   # 模板对象，不会立即拼接
# 由渲染库（如 html 支持库）决定如何转义 title 后再输出
```

入门阶段记住"f-string 直接出字符串、t-string 出模板对象"即可，详见[字符串格式化字典](../reference/language-concepts/12-string-formatting.md)。

旧写法 `%` 与 `str.format()` 只需能读懂，新代码一律 f-string（需要防注入的模板渲染交给 t-string 生态）。

---

## 4. 类型注解：给动态类型上保险

注解**不影响运行时**，但编辑器、mypy/pyright、FastAPI 都依赖它：

```python
# 变量注解（多在复杂初始化处使用）
count: int = 0
tags: list[str] = []
config: dict[str, str] = {}

# 函数注解是刚需
def repeat(text: str, times: int = 2) -> str:
    return text * times

# 可能为空 → 管道联合类型（3.10+ 标准写法）
def find_user(uid: int) -> str | None:
    ...
```

类型演进对照（旧代码里会遇到，新代码用右列）：

| 旧写法（3.8 及以前） | 3.10+ 写法（3.12 仍推荐） |
|------|------|
| `Optional[str]` | `str \| None` |
| `Union[int, str]` | `int \| str` |
| `List[str]` | `list[str]` |
| `Dict[str, int]` | `dict[str, int]` |
| `Type[X]` | `type[X]` |

> 💡 注解是"承诺"而非"强制"：`def f(x: int)` 传字符串不会在运行时报错，需靠 `uvx mypy .` 或 Pylance 静态检查兜底。

---

## 5. 类型转换与真值判断

```python
int("42"), float("3.5"), str(99), bool("")   # 显式转换
int("4A")          # ValueError —— 转换失败抛异常而非返回垃圾值

# 真值测试：以下都为 False
falsy = [0, 0.0, "", [], {}, set(), None, False]
```

习惯写法是利用真值语义，而不是与空值硬比较：

```python
items: list[str] = []
if items:            # 推荐：非空列表即真
    print("有数据")

name: str | None = None
if name:             # 同时排除 None 和 ""
    print(name.strip())
```

---

## ✅ 最佳实践

类型注解描述预期契约，运行时仍可收到不符合约定的值。判断“缺失”用 is None，判断“为空”可用相应长度或真值；0、空串与 None 不能因都为假就无条件视为同一业务情况。

浮点近似比较要设置符合场景的相对或绝对容差，精确可表示值与特定协议也可能需要精确比较。f-string、format 和日志的延迟格式化各有用途，不必统一禁用。练习分别输入 None、0 和空串，确认不会误用默认值。

---

## ❓ 常见问题

### Q1: 为什么 `b = a` 之后改 `b`，`a` 也变了？
**A**: `a`、`b` 是同一对象的两个标签（第 1 节）。可变对象（list/dict/set）共享引用；int/str 等不可变对象"看似复制"是因为修改只能产生新对象。

### Q2: 注解错了运行时为什么没报错？
**A**: 注解默认只存进 `__annotations__`，解释器不校验。运行时强校验交给 Pydantic（见 [typing 注解全表](../reference/language-concepts/05-typing-annotations.md)）。

---

## 🎯 练习与实践

### 正文验证：绑定、不可变值与格式化

下面程序是本页关键对象模型与 f-string 规则的独立版本。验证脚本会直接提取这个 Markdown 代码块，用隔离的 Python 容器执行；它不覆盖类型检查器、第三方库或本页其他示例。

```python verify:python-bindings-formatting
a = [1]
b = a
b.append(2)
assert a == [1, 2]

b = [9]
assert a == [1, 2] and b == [9]

name, price, qty = 'keyboard', 399.5, 2
assert f'{price * qty:.2f}' == '799.00'
assert f'{name:*>10}' == '**keyboard'
assert 0.1 + 0.2 != 0.3
print('python-bindings: alias, rebinding, f-string, float')
```

### 练习一：类型观察
1. 在 REPL 中依次执行 `type(1)`、`type(True)`、`isinstance(True, int)`，解释输出
2. 构造 `a = [1, 2]`，用三种方式创建独立副本并逐一验证

### 练习二：格式化报告
1. 给定 `items = [("键盘", 399.5, 2), ("鼠标", 129, 5)]`
2. 用 f-string 输出右对齐的三列表格，金额保留两位、千分位
3. 合计行用 `=` 调试语法打印各变量

**评估标准**：输出形如 `| 键盘 | 399.50 | 2 |`，且 `uvx mypy` 对练习代码零报错。

---

## 🔗 相关文档

- 📄 **[函数与类](./04-functions-oop.md)** — 把类型注解扩展到面向对象设计
- 📄 **[数据结构速查](../reference/language-concepts/03-data-structures.md)** — list/dict/set/tuple 全操作
- 📄 **[typing 注解全表](../reference/language-concepts/05-typing-annotations.md)** — 泛型、Protocol、TypedDict 进阶


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
