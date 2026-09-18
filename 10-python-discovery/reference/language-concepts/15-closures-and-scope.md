# 闭包与作用域 — LEGB、global/nonlocal、late binding

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#闭包` `#LEGB` `#nonlocal` `#late-binding` `#作用域` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

闭包是"记住定义时所在名字空间"的内层函数：`inner` 引用了外层函数的局部变量 `x`，即使 `outer` 已经返回，`x` 仍存活在 `inner.__closure__` 里。作用域规则（LEGB）决定名字查找顺序：**L**ocal（当前函数）→ **E**nclosing（外层函数）→ **G**lobal（模块级）→ **B**uilt-in（内置）。理解闭包是理解装饰器（[06-decorators](./06-decorators.md)）的前提。

## 📖 语法 / 详解

### LEGB 查找顺序

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        return x          # L 层命中即停，E/G/B 不再查找
    return inner()

outer()                   # 'local'
```

查找在第一层命中即停；四层都没有 → `NameError`。内置名也可被遮蔽：函数内写 `len = lambda s: -1` 后，该函数里 `len("abc")` 返回 `-1`（局部遮蔽内建）。

### 赋值决定归属：global / nonlocal

函数内的**赋值**让名字在编译期就被定为局部变量，只有读取才按 LEGB 回退：

```python
count = 0

def broken():
    count = count + 1     # UnboundLocalError：赋值使 count 变成局部名

def bump():
    global count          # 声明：这次赋值写的是模块级 count
    count += 1

def make_counter():
    n = 0
    def inc():
        nonlocal n        # 声明：n 绑定到外层函数的 n
        n += 1
        return n
    return inc
```

`global` 命中模块级名字，`nonlocal` 命中最近的**外层函数**名字（不查模块级）。

### 自由变量与 __closure__

```python
def outer():
    x = 10
    def inner(): return x
    return inner

f = outer()
f.__closure__                       # (<cell at 0x...: int object at 0x...>,)
f.__closure__[0].cell_contents      # 10 —— 自由变量的当前值
```

闭包持有的不是值的副本，而是**变量所在的 cell**：函数体执行时才读取 cell 的当前内容。没有自由变量的函数 `__closure__` 为 `None`。

### late binding 陷阱（本机 3.14.7 实测）

循环里创建闭包时，所有闭包引用同一个循环变量，调用时才取值——拿到的是**循环结束后的值**：

```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]                    # [2, 2, 2] —— 不是 [0, 1, 2]！
funcs[0].__closure__[0].cell_contents   # 2：读到的都是循环结束后的 i
```

三种修复：

```python
# 1. 默认参数：在定义那一刻求值（见 17-functions-parameters）
funcs = [lambda i=i: i for i in range(3)]       # [0, 1, 2]

# 2. 工厂函数：每次调用产生独立 cell
funcs = [(lambda i: lambda: i)(i) for i in range(3)]   # [0, 1, 2]

# 3. functools.partial：注册回调时固定参数
from functools import partial
callbacks = [partial(print, i) for i in range(3)]      # 各自持有自己的 i
```

### 与装饰器的关系

常见函数装饰器会接收原函数并返回包装闭包，但装饰器也可以返回其他对象或由可调用实例实现。对包装闭包这种写法：`wrapper` 闭包持有 `func`、以及带参装饰器外层的 `arg` 等自由变量，闭包的生存期 = wrapper 的生存期。完整展开见 [06-decorators](./06-decorators.md)。

## 💡 示例

```python
def make_counter(start: int = 0):
    n = start                       # 被闭包捕获的自由变量
    def inc(step: int = 1) -> int:
        nonlocal n                  # 声明写的是外层 n，不是新建局部
        n += step
        return n
    return inc

c = make_counter()
c()        # 1
c(9)       # 10
d = make_counter(100)               # 独立状态，互不干扰
d()        # 101
```

闭包给"带状态的小函数"提供了比全局变量、类实例更轻的载体；状态需要多个方法共享时再升级为类（[16-classes-and-inheritance](./16-classes-and-inheritance.md)）。

## ⚠️ 常见陷阱

- ❌ **循环里建 lambda 期待立即绑定**：`[lambda: i for i in range(3)]` 全部返回 2——闭包捕获变量而非值（实测）。
  ✅ 默认参数 `lambda i=i: i`（定义时求值一次）、工厂函数或 `functools.partial`。
- ❌ **函数内给全局名赋值不加 global**：`count += 1` 触发 `UnboundLocalError`，因为赋值让名字变局部。
  ✅ 需要 rebind 模块级名字时显式 `global count`；只读引用不需要声明。
- ❌ **跨函数改外层变量不加 nonlocal**：`n += 1` 同理被当局部变量，`UnboundLocalError`。
  ✅ 声明 `nonlocal n`；注意 `nonlocal` 找不到外层函数变量时编译报 SyntaxError，它也不命中模块级名字。
- **可变容器与 nonlocal 表达不同动作**：`state["n"] += 1` 修改对象内容，`nonlocal n; n += 1` 重新绑定外层名字。两者都可用于闭包状态，按数据形状与可读性选择，不必把容器写法当成错误。
- ❌ **注册事件回调时直接引用循环变量**（GUI/异步回调的经典翻车点，与 late binding 同源）。
  ✅ 回调注册用 `functools.partial(handler, item)` 在注册时固定参数。

<!-- full-library-explanation -->
## 用两个计数器观察绑定的寿命

前置知识是函数可以作为返回值。闭包不是把所有外层变量拍成快照，而是保留所需绑定。`nonlocal` 用于重新绑定外层名字；对已引用的列表调用 `append` 没有重新绑定名字，因此不要求 `nonlocal`。

将上面的 `make_counter` 定义保存到 `counter.py`，追加：

```python
left = make_counter()
right = make_counter(10)
print(left(), left(), right(), left())
```

运行 `python counter.py`，输出 `1 2 11 3`。同一闭包多次调用共享状态，不同工厂调用建立不同状态。

练习：解释 `lambda i=i: i` 为什么解决循环回调问题，却不能隔离 `i` 引用的可变列表。答案是默认参数保存当时的对象引用，不自动复制对象；需要独立数据时，在注册时明确构造副本。不要把绑定时机与对象可变性混为一谈。

## 🔗 相关条目

- 📄 **[装饰器](./06-decorators.md)** — 闭包最重要的应用场景
- 📄 **[函数参数全形态](./17-functions-parameters.md)** — 默认参数求值时机是 late binding 的解药之一
- 📄 **[Python 关键字详解](./01-python-keywords.md)** — `global`/`nonlocal` 关键字本身
- 📄 **[asyncio 并发](./09-asyncio-concurrency.md)** — 协程与任务同样依赖名字查找与闭包语义
- 🌐 **[官方文档：Python Scopes and Namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
