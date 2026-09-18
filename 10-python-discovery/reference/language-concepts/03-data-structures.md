# 数据结构速查 — list / dict / set / tuple

## 概述

四大内置容器按"可变性 × 有序性 × 是否去重"分工。选型口诀：**有序序列用 list，键值映射用 dict，去重与成员判断用 set，不可变记录用 tuple**。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#数据结构` `#list` `#dict` `#set` `#tuple` |
| **更新日期** | `2026年9月` |

</details>

## 特性对照表

| 类型 | 可变 | 有序 | 去重 | 字面量 | 典型用途 |
|------|------|------|------|--------|---------|
| `list` | ✅ | ✅ | ❌ | `[1, 2]` | 队列、集合收集 |
| `tuple` | ❌ | ✅ | ❌ | `(1, 2)` | 固定记录、dict 键 |
| `dict` | ✅ | ✅（插入序） | 键去重 | `{"a": 1}` | 映射、JSON |
| `set` | ✅ | ❌ | ✅ | `{1, 2}` | 去重、交并差 |
| `frozenset` | ❌ | ❌ | ✅ | `frozenset()` | 可哈希集合 |

---

## 1. list — 核心操作

```python
nums = [3, 1, 4, 1, 5]

nums.append(9)            # 尾部追加，摊还 O(1)；个别扩容会复制元素
nums.insert(0, 7)         # 指定位置插入 O(n)
nums.extend([2, 6])       # 合并（或 nums += [...]）
nums.remove(4)            # 按值删（首个），不存在抛 ValueError
nums.pop()                # 弹尾 O(1)；pop(0) 弹头 O(n)
nums.index(5)             # 查下标
nums.count(1)             # 计数
nums.sort(key=abs, reverse=True)   # 原地排序
sorted(nums)              # 返回新列表
nums.reverse()            # 原地反转

# 切片 [起:止:步] —— 含头不含尾，均为新对象
nums[1:3]      # 下标 1、2
nums[:3]       # 前 3 个
nums[::2]      # 隔一个取一个
nums[::-1]     # 反转副本
copy = nums[:] # 浅拷贝
```

### 切片详解 — 负索引、step、越界与 slice 对象

`seq[起:止:步]` 三参数均可省略，规则：**含头不含尾**、下标可为负（`-1` 是末尾，本机 3.14.7 实测）：

```python
s = [0, 1, 2, 3, 4, 5]
s[2:4]      # [2, 3]              含头不含尾
s[-3:]      # [3, 4, 5]           负下标从尾部倒数
s[::2]      # [0, 2, 4]           step=2 隔一个取一个
s[::-1]     # [5, 4, 3, 2, 1, 0]  step=-1 反转副本
s[1:100]    # [1, 2, 3, 4, 5]     越界不报错，取到哪算哪
s[10:]      # []                  完全越界得空序列
```

**越界不报错**是切片与下标访问的本质区别：`s[100]` 抛 `IndexError`，而切片先按 `slice.indices(len())` 收缩到合法范围（实测 `slice(-2, None).indices(6)` → `(4, 6, 1)`）——这是"先切后处理"惯用法安全的根源。

**浅拷贝**：`b = a[:]` 与 `b = a.copy()` 都只复制最外层容器，嵌套对象仍共享（完整演示见第 5 节）。需要复制内层对象时可考虑 `copy.deepcopy(a)`，但自定义复制协议及文件、锁等资源需要另外处理，不能把它理解为任意对象都能复制成独立资源。

**slice 对象与自定义类**：`a[1:3]` 只是 `a[slice(1, 3)]` 的语法糖（内置 [`slice`](./02-built-in-functions.md) 生成）。自定义类想支持切片，在 `__getitem__` 里判断参数类型；`slice.indices(len)` 负责把负数与 step 换算成绝对下标（实测）：

```python
class Window:
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self.data))
            return [self.data[i] for i in range(start, stop, step)]
        return self.data[key]

w = Window("abcdef")
w[1:4]      # ['b', 'c', 'd']
w[-2:]      # ['e', 'f']
w[::2]      # ['a', 'c', 'e']
```

**陷阱**: `+` 拼接列表每次都建新对象，循环内累积用 `append`/`extend`；切片是浅拷贝，嵌套列表的内部对象仍共享。

---

## 2. dict — 核心操作

```python
user = {"name": "ada", "age": 36}

user["email"] = "a@x.io"       # 增/改
user.get("phone", "未填")       # 安全读取，键不存在给默认值
user.setdefault("tags", []).append("dev")   # 不存在才设默认值
del user["age"]                # 删除（不存在抛 KeyError）
user.pop("email", None)        # 弹出并返回，可给默认值

"name" in user                 # 成员判断（只查键）

# 遍历三件套
for key in user: ...                   # 默认遍历键
for k, v in user.items(): ...          # 键值对
for v in user.values(): ...

# 合并（3.9+）
merged = defaults | overrides          # 右侧优先
defaults.update(overrides)             # 原地合并

# 推导式
squares = {n: n * n for n in range(5)}
```

**陷阱**: 遍历时增删键抛 `RuntimeError`——先复制 `list(user.items())` 再改；Python 3.7+ 保证插入序，别依赖它做业务排序。

**进阶容器**（`collections` 模块）：

```python
from collections import Counter, defaultdict, deque

Counter("abracadabra").most_common(2)  # [('a', 5), ('b', 2)]
groups = defaultdict(list)             # 缺键自动建默认值
groups["a"].append(1)
dq = deque([1, 2, 3], maxlen=5)        # 双端队列，两端 O(1)
```

详见[标准库导航](../library-guides/01-standard-library.md)。

---

## 3. set — 去重与集合运算

```python
a = {1, 2, 3}
b = {3, 4, 5}

a | b        # 并 {1, 2, 3, 4, 5}
a & b        # 交 {3}
a - b        # 差 {1, 2}
a ^ b        # 对称差 {1, 2, 4, 5}

a.add(6); a.discard(99)    # discard 不存在不报错（remove 会报）
x in a                     # 平均 O(1)；依赖哈希分布及相等比较成本

unique = set(["a", "b", "a"])      # 一行去重
```

**陷阱**: 空 set 必须写 `set()`，`{}` 是空 dict；set 元素必须可哈希；列表转成元组后，内部元素仍须全部可哈希。

---

## 4. tuple — 不可变记录

```python
point = (3, 5)
x, y = point                 # 解包
first, *rest = [1, 2, 3, 4]  # 星号收集
a, b = b, a                  # 交换变量

def min_max(nums) -> tuple[int, int]:
    return min(nums), max(nums)      # 多返回值本质是 tuple

nested = {point: "原点附近"}          # tuple 可作 dict 键
```

**陷阱**: 单元素元组必须带逗号 `(1,)`，`(1)` 只是 int；具名场景用 `typing.NamedTuple` 或 dataclass 提升可读性。

---

## 5. 可变性与共享引用（最大陷阱区）

```python
a = [[1, 2], [3, 4]]
b = a[:]                # 浅拷贝
b[0].append(99)
print(a[0])             # [1, 2, 99] —— 内层列表仍共享！

import copy
c = copy.deepcopy(a)    # 此处由整数和列表构成，嵌套列表会复制
```

判空、判存、判等的惯用法：

```python
items = [1, 2]
mapping = {"name": "Ada"}
key = "name"
a = [1, 2]
b = a.copy()

if items:                       # 非空
    print("列表有内容")
if key in mapping:              # 键存在
    print(mapping[key])         # Ada
if a == b:                      # 值相等
    print("内容相等")
if a is b:                      # 同一对象；不限于单例，但不能代替值比较
    print("引用同一对象")         # 本例不会执行：copy 创建了新列表
```

---

## 陷阱速查表

| 陷阱 | 正确做法 |
|------|---------|
| `list.pop(0)` 高频调用 | 用 `collections.deque` |
| 遍历 dict 时增删键 | 遍历 `list(d.items())` 副本 |
| 浅拷贝以为安全 | 嵌套结构用 `copy.deepcopy` |
| `set()` 写成 `{}` | 空集合只能是 `set()` |
| dict 键用 list | 元组或 frozenset 的内部元素也必须可哈希 |
| `(1)` 当元组 | 单元素加逗号 `(1,)` |

---

<!-- full-library-explanation -->
## 从数据的关系选择容器

前置知识是赋值、循环和函数调用。容器选择先回答“元素如何被找到”：按位置找用序列，按标识查值用映射，判断是否出现过用集合。`dict` 保存插入顺序，但重新给旧键赋值不会让它自动按值排序；`set` 不提供可依赖的显示顺序。

下面是完整小实验，保存为 `containers.py` 后运行 `python containers.py`：

```python
rows = [["read"], ["write"]]
shallow = rows.copy()
shallow[0].append("test")
print(rows[0])
record = (rows[0],)
record[0].append("review")
print(record[0])
try:
    hash(record)
except TypeError:
    print("contains an unhashable list")
```

输出依次为 `['read', 'test']`、`['read', 'test', 'review']` 和 `contains an unhashable list`。列表副本共享内部列表，元组固定的是元素引用的位置，不会把内部列表冻结。因此“元组不可变”不能推出“任意元组都能作字典键”。

练习：把 `rows.copy()` 换成 `[row.copy() for row in rows]`。第一行输出应变为 `['read']`，因为现在每个内层列表也被复制；继续增加第三层嵌套时，说明这一写法为什么又不能保证所有层都独立。

## 🔗 相关文档

- 📄 **[变量与类型](../../basics/03-variables-types.md)** — 可变/不可变模型的教程讲解
- 📄 **[内置函数全表](./02-built-in-functions.md)** — 作用于容器的内置函数
- 📄 **[标准库导航](../library-guides/01-standard-library.md)** — collections/itertools 扩展


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
