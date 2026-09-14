# 控制流与推导式 — 条件、循环、推导式与 match-case

> **文档简介**: 掌握 Python 条件与循环的全部写法，重点训练推导式这一 Python 标志性表达力工具，并学会 3.10+ 的 match-case 结构化分支
>
> **目标读者**: 已掌握函数与类的开发者，想写出地道 Python 控制流的人
>
> **前置知识**: 完成[函数与类](./04-functions-oop.md)，理解可迭代对象概念

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#控制流` `#推导式` `#match-case` `#迭代` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 `if/elif/else` 与三元表达式组织分支逻辑
- ✅ 用 `for`/`while` 配合 `enumerate`、`zip` 优雅遍历
- ✅ 写出列表/字典/集合/生成器四种推导式
- ✅ 用 `match-case` 实现结构化模式匹配

---

## 1. 条件分支：Python 的真值美学

```python
score = 87

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"          # 注意 elif 而非 else if
else:
    grade = "C"

# 三元表达式：值在前，条件在后
label = "及格" if score >= 60 else "不及格"

# 链式比较，数学式写法
if 0 <= score <= 100:
    print("有效分数")
```

`match-case`（3.10+）处理多分支结构与解构：

```python
def handle(command: str) -> str:
    match command.split():
        case ["add" | "new", arg]:     # 或模式
            return f"添加 {arg}"
        case ["rm", *targets]:         # 序列解构模式
            return f"删除 {len(targets)} 项"
        case _:
            return "未知命令"
```

> ⚠️ `case _` 是通配符，**必须放最后**；匹配字面量直接写值，匹配变量会被当作捕获名——要用点号访问的常量（如 `Status.OK`）才按值匹配。

---

## 2. for 循环：迭代即遍历

Python 的 `for` 遍历**可迭代对象**，不是下标：

```python
langs = ["python", "go", "rust"]

for lang in langs:                  # 直接遍历元素
    print(lang)

for i, lang in enumerate(langs, start=1):   # 需要下标时
    print(f"{i}. {lang}")

for cn, en in zip(["一", "二"], [1, 2]):     # 并行遍历
    print(cn, en)

for k, v in {"py": 1991, "go": 2009}.items():  # 遍历字典
    print(k, v)
```

**`range` 与循环控制**：

```python
for i in range(3):          # 0, 1, 2（含头不含尾）
    ...

for i in range(10, 0, -2):  # 10, 8, 6, 4, 2
    ...

while True:                 # while 适合"不确定次数"的场景
    cmd = input("> ")
    if cmd == "quit":
        break               # 跳出循环
    if not cmd:
        continue            # 跳过本轮
    print(cmd)
```

**for-else**：循环未被 `break` 打断时执行 else，常用于搜索：

```python
for item in items:
    if item == target:
        print("找到了")
        break
else:
    print("没找到")          # 没被 break 才执行
```

> 💡 优先考虑"遍历元素"而非"遍历下标再取元素"。需要下标就用 `enumerate`，这正是 Python 惯用法与 C 风格循环的分水岭。

---

## 3. 推导式：Python 的标志表达力

推导式（comprehension）把"建列表的循环"压缩成一行，且比等价循环更快：

```python
nums = [1, 2, 3, 4, 5, 6]

# 列表推导式：[表达式 for 变量 in 可迭代 if 条件]
squares = [n * n for n in nums]                 # [1, 4, 9, 16, 25, 36]
evens = [n for n in nums if n % 2 == 0]         # [2, 4, 6]
matrix_flat = [x for row in [[1, 2], [3, 4]] for x in row]   # [1, 2, 3, 4]

# 字典推导式
len_map = {w: len(w) for w in ["py", "go"]}     # {'py': 2, 'go': 2}
rev = {v: k for k, v in len_map.items()}        # 键值互换

# 集合推导式
unique_len = {len(w) for w in ["py", "go", "rust"]}   # {2, 4}

# 生成器表达式：圆括号，惰性求值，省内存
total = sum(n * n for n in range(1_000_000))    # 不建中间列表
```

> ⚠️ 推导式超过两层 `for` 或两个 `if` 就该换回普通循环——可读性优先，一行不是目的。

> 📖 四种推导式的语法对照、条件/嵌套写法与生成器惰性语义，见 [推导式速查](../reference/language-concepts/14-comprehensions.md)。

---

## 4. 推导式实战：数据清洗三例

```python
# 例1：清洗用户输入
raw = ["  Ada ", "", "BOB", None, "cleo"]
names = [s.strip().title() for s in raw if s]        # ['Ada', 'Bob', 'Cleo']

# 例2：条件表达式做分支映射
grades = {n: ("pass" if s >= 60 else "fail") for n, s in {"a": 70, "b": 50}.items()}

# 例3：展平嵌套 JSON 字段
records = [{"tags": ["web", "api"]}, {"tags": ["db"]}]
all_tags = {t for r in records for t in r["tags"]}   # {'web', 'api', 'db'}
```

`any()`/`all()` 配生成器表达式是集合判断的地道写法：

```python
has_admin = any(u["role"] == "admin" for u in users)
all_valid = all(len(u["name"]) > 0 for u in users)
```

---

## ✅ 最佳实践

- ✅ **遍历优先 `enumerate`/`zip`/`.items()`**，禁止 `for i in range(len(lst))` 取元素
- ✅ **简单映射过滤用推导式**，复杂逻辑用循环
- ✅ **大集合聚合用生成器表达式**，避免中间列表
- ❌ **避免**：在推导式里有副作用（打印、修改外部变量）
- ❌ **避免**：嵌套推导式超过两层
- 💡 **技巧**：`for-else` + `break` 替代"搜索成功标志位"变量

---

## ❓ 常见问题

### Q1: 推导式和 `map`/`filter` 怎么选？
**A**: 新代码统一用推导式，可读性更好；`map`/`filter` 只在读老代码和已有函数可直接复用时考虑。

### Q2: `match-case` 就是 switch 吗？
**A**: 远不止——它能解构序列、映射，配合守卫 `if` 子句做结构化匹配，本质是模式匹配而非值跳转。

---

## 🎯 练习与实践

### 练习一：单词统计
1. 给定 `text = "the quick the lazy the dog"`，用推导式统计每个单词出现次数（dict 推导式 + `.split()`）
2. 用集合推导式输出出现超过一次的单词

### 练习二：重构为 match-case
1. 把下面的 if 链改写成 `match-case`（含序列解构）：

```python
if cmd == "add":
    op, *rest = args
elif cmd == "rm":
    targets = args
else:
    ...
```

2. 为 `add` 分支加守卫：`args` 为空时输出提示

**评估标准**：两个练习均用推导式/`match` 完成，单函数不超过 10 行，ruff 通过。

---

## 🔗 相关文档

- 📄 **[异常处理](./06-exceptions.md)** — 控制流之外的错误流
- 📄 **[数据结构速查](../reference/language-concepts/03-data-structures.md)** — 推导式各目标的完整语法
- 📄 **[Python 一行式速查](../reference/quick-references/01-python-cheatsheet.md)** — 推导式高频模式集
