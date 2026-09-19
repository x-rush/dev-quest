# Python 一行式速查

## 概述

高频惯用表达的一行式片段集：每个模式一行代码 + 注释示例。按场景分组，可作 REPL 伴侣。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#速查` `#一行式` `#惯用法` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. 字符串

```python
s = "  Hello, World  "
s.strip().lower()                          # 清洗并归一化
" ".join(words)                            # 列表 → 字符串
s.replace("World", "Python")               # 替换
s.split(",")                               # 分割
f"{price:>10,.2f}"                         # 右对齐+千分位+两位小数
s.startswith(("http", "https"))            # 多前缀判断
len(text.splitlines())                    # 按 splitlines 规则计行；空文本为 0
```

## 2. 列表与字典

```python
[x for x in xs if x % 2 == 0]              # 过滤
[len(x) for x in words]                    # 映射
{v: k for k, v in d.items()}               # 键值反转
sorted(xs, key=lambda x: (-x.score, x.name))   # 多级排序（负号降序）
list(dict.fromkeys(xs))                    # 保序去重
max(xs, key=len)                           # 按规则取极值
sum(x.price for x in cart)                 # 生成器求和
list(zip(names, scores))                   # 配对
a, *rest = xs                              # 解包
```

## 3. 集合运算

```python
set(a) & set(b)                            # 交集
set(a) | set(b)                            # 并集
set(a) - set(b)                            # 差集
len(set(xs)) == len(xs)                    # 是否无重复
```

## 4. 条件与逻辑

```python
grade = "A" if s >= 90 else "B"            # 三元
value = d.get("k") or "default"            # 真值兜底（区分 0/"" 用 in 判断）
any(x > 0 for x in xs)                     # 存在判断
all(x > 0 for x in xs)                     # 全称判断
value if value is not None else fallback   # 精确 None 判断
```

## 5. 文件与路径

```python
Path("f.txt").read_text(encoding="utf-8").splitlines()    # 读行列表
Path("out.txt").write_text("\n".join(lines), encoding="utf-8")
with open("f.json", encoding="utf-8") as f: json.load(f)  # 读 JSON
with open("big.log", encoding="utf-8") as stream:
    for line in stream:
        if "ERROR" in line:
            print(line.rstrip("\n"))
```

## 6. 常用内置组合

```python
dict(Counter(words).most_common(5))        # Top-N 计数
dict(zip(keys, values))                    # 双列表 → 字典
list(itertools.chain.from_iterable(nested)) # 二维展平
list(itertools.islice(gen, 5))             # 生成器取前 N
round(sum(xs) / len(xs), 2)                # 均值
os.cpu_count()                             # CPU 核数
```

## 7. REPL 调试

```python
print(f"{var=}")                           # 变量名+值
print(*xs, sep="\n")                       # 逐行打印
repr(obj)[:200]                            # 截断调试输出
sys.version                                # 解释器版本
```

## 8. 时间与随机

```python
datetime.now(timezone.utc).isoformat()     # UTC 时间戳（ISO 格式）
int(time.time())                           # Unix 秒
random.choice(xs); random.sample(xs, 3)    # 随机取
secrets.token_hex(16)                      # 安全令牌（勿用 random）
```

---

## 使用原则

- 一行式服务于**简单转换**；两步以上逻辑写正常函数
- REPL 里先试一行式，成型后落盘
- 单次流式消费可用生成器；需要重复遍历、随机访问或固定快照时使用列表

### 可复现验收：空输入、严格配对与资源关闭

以下完整程序把速查中的几个边界放到同一处执行。它不是让所有业务都接受空输入，而是让调用者先看清 Python 的默认语义，再在业务层决定是否拒绝。

```python verify:python-cheatsheet-boundaries
from pathlib import Path
from tempfile import TemporaryDirectory

print(f"max={max([], default=None)}")

try:
    list(zip(["a"], [1, 2], strict=True))
except ValueError:
    print("zip=strict-error")

print(f"all-empty={all([])} any-empty={any([])}")

with TemporaryDirectory() as directory:
    path = Path(directory) / "sample.txt"
    path.write_text("first\nsecond\n", encoding="utf-8")
    with path.open(encoding="utf-8") as stream:
        assert next(stream) == "first\n"
    print(f"closed={stream.closed}")
```

预期输出：

```text
max=None
zip=strict-error
all-empty=True any-empty=False
closed=True
```

`zip(..., strict=True)` 的长度不匹配在迭代消费时出现，因此只创建 iterator 并不能验证输入；文件对象由 `with` 管理，即使中途抛出异常也会走关闭路径。

---

<!-- full-library-explanation -->
## 使用速查表前先补齐输入条件

这里是局部表达式集合，xs、words、Path 等名字需要调用方定义或导入，不是一份能从上到下运行的脚本。前置是了解容器与异常；陌生表达式应回到对应参考正文，先确认输入和返回值。

练习比较三组边界：`max([])` 会失败，`max([], default=None)` 返回 None；普通 zip 遇到长度不同会截断，`zip(..., strict=True)` 在消费时报告不匹配；`all([])` 为 True，而 `any([])` 为 False。它们都不是业务验证规则，是否允许空输入由你的需求决定。

一行文件生成器没有显式表达关闭时机，尤其在提前停止消费时容易保留文件。需要读大文件时用 with 持有文件，再在块内消费生成器。若只处理小文本，read_text().splitlines() 更直接，但会读取全部内容。

## 🔗 相关文档

- 📄 **[控制流与推导式](../../basics/05-control-flow.md)** — 推导式的教程讲解
- 📄 **[数据结构速查](../language-concepts/03-data-structures.md)** — 一行式背后的容器操作
- 📄 **[标准库导航](../library-guides/01-standard-library.md)** — itertools/collections 全貌


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
