# 推导式 — 列表 / 字典 / 集合 / 生成器表达式

## 概述

推导式（comprehension）把"建容器的循环"压缩为一行表达式，语义固定：**先 for 取值，后 if 过滤，最左输出表达式**。比等价循环更快，也是 Python 标志性的表达力工具。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#推导式` `#comprehension` `#生成器` `#表达式` |
| **更新日期** | `2026年9月` |

## 四种形态对照

| 形态 | 语法 | 产物 | 求值 |
|------|------|------|------|
| 列表推导式 | `[x for x in it]` | `list` | 立即 |
| 字典推导式 | `{k: v for k, v in it}` | `dict` | 立即 |
| 集合推导式 | `{x for x in it}` | `set`（去重） | 立即 |
| 生成器表达式 | `(x for x in it)` | 生成器 | **惰性** |

---

## 1. 四种语法与示例

```python
nums = [1, 2, 3, 4, 5, 6]

squares = [n * n for n in nums]                  # [1, 4, 9, 16, 25, 36]
evens   = [n for n in nums if n % 2 == 0]        # 过滤：[2, 4, 6]

len_map = {w: len(w) for w in ["py", "go"]}      # {'py': 2, 'go': 2}
rev     = {v: k for k, v in len_map.items()}     # 键值互换

unique  = {len(w) for w in ["py", "go", "rust"]} # {2, 4}

total   = sum(n * n for n in range(1_000_000))   # 生成器表达式，无中间列表
```

**陷阱**: 生成器表达式作函数唯一实参时可省括号（`sum(n for n in ...)`）；一旦还有别的参数必须显式包一层 `sum((n for n in ...), 0)`。

---

## 2. 条件与分支的三个位置

```python
# if 在末尾 = 过滤（不满足的元素直接丢弃）
kept = [v for v in [1, 2, 0, 3] if v]            # [1, 2, 3]

# if/else 在输出表达式 = 变换（每个元素都产出）
marks = ["及格" if s >= 60 else "补考" for s in [70, 50]]

# 海象运算符：一次计算、两处使用（3.8+）
doubled = [y for x in [1, 2, 3] if (y := x * 2) > 2]   # [4, 6]
```

**陷阱**: `if` 位置不能带 `else`（那是过滤）；`else` 必须贴着输出表达式——`[x if c for ...]` 是语法错误。

---

## 3. 嵌套与展平

```python
matrix = [[1, 2], [3, 4]]
flat = [x for row in matrix for x in row]        # [1, 2, 3, 4]：for 顺序同嵌套顺序

records = [{"tags": ["web", "api"]}, {"tags": ["db"]}]
all_tags = {t for r in records for t in r["tags"]}  # {'web', 'api', 'db'}
```

**陷阱**: 多个 `for` 的书写顺序=嵌套从外到内，但读起来像"从左到右展平"；超过两层 `for` 或两个 `if` 应改回普通循环——可读性优先，一行不是目的。

---

## 4. 生成器表达式的惰性语义

```python
g = (x * x for x in range(5))
next(g)            # 0：逐个产出
list(g)            # [1, 4, 9, 16]：续上一次的位置
list(g)            # []：已耗尽，生成器只能消费一次

has_admin = any(u["role"] == "admin" for u in users)   # any/all 短路，可能不遍历完
```

**陷阱**: 生成器**单次消费**——`sum(g)` 之后再 `list(g)` 得到空列表；需要多次遍历就老实建列表。列表推导式的循环变量不泄漏到外层作用域（Python 3），生成器表达式同理。

---

## 🔗 相关文档

- 📄 **[控制流与推导式](../../basics/05-control-flow.md)** — 推导式实战教程（数据清洗三例）
- 📄 **[数据结构速查](./03-data-structures.md)** — 产物容器的完整操作
- 📄 **[生成器与迭代器](./07-generators-iterators.md)** — `yield` 函数与迭代协议的深入条目
