# 标准库导航 — collections / itertools / pathlib / json / logging 等

## 概述

Python "自带电池"：大量日常需求无需第三方包。本条目按场景导航最值得掌握的标准库模块，每个给出最小可用示例。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#标准库` `#collections` `#itertools` `#pathlib` `#json` `#logging` |
| **更新日期** | `2026年9月` |

---

## 1. collections — 容器扩展

```python
from collections import Counter, defaultdict, deque, namedtuple

# Counter：计数器
Counter("abracadabra").most_common(3)      # [('a', 5), ('b', 2), ('r', 2)]
Counter(words) - Counter(banned)           # 支持集合运算

# defaultdict：缺键自动初始化
groups: defaultdict[str, list] = defaultdict(list)
groups["dev"].append("ada")                # 无需先判断键存在

# deque：双端队列（两端 O(1)）
history = deque(maxlen=100)                # 滑动窗口神器
history.append(x); history.popleft()

# namedtuple：轻量记录
Point = namedtuple("Point", ["x", "y"]); p = Point(1, 2)
```

**陷阱**: `defaultdict` 读取不存在的键会**写入**默认值，只读场景用 `dict.get(k, default)`。

> 🌐 官方文档：[collections — 容器数据类型](https://docs.python.org/3/library/collections.html)

---

## 2. itertools — 迭代 algebra

```python
from itertools import chain, groupby, islice, product, combinations, count

chain([1, 2], [3, 4])              # 拼接可迭代：1 2 3 4
islice(gen, 10)                    # 切片迭代器（生成器不支持 [0:10]）
groupby(sorted(items, key=k), k)   # 分组（必须先按同 key 排序！）
product("AB", repeat=2)            # 笛卡尔积
combinations([1, 2, 3], 2)         # 组合；count(n, step) 无限计数器配 islice
```

**陷阱**: `groupby` 只对**相邻**相同元素分组，忘记先 `sorted(key=...)` 是头号错误。

> 🌐 官方文档：[itertools — 迭代函数库](https://docs.python.org/3/library/itertools.html)

---

## 3. pathlib — 面向对象路径

```python
from pathlib import Path

config = Path.home() / ".config" / "app.toml"   # / 拼路径，跨平台

config.exists()                  # 存在判断
config.parent / config.suffix    # 父目录/后缀等属性
config.read_text(encoding="utf-8")     # 一行读文件
config.write_text("hello", encoding="utf-8")   # 一行写文件

Path("data").glob("*.csv")             # 模式匹配，惰性生成器；rglob 递归
Path("out").mkdir(parents=True, exist_ok=True)
```

**要点**: 全面替代 `os.path` 字符串拼接；小文件直接 `read_text`/`write_text`，大文件仍用 `open` 流式处理。

> 🌐 官方文档：[pathlib — 面向对象的文件系统路径](https://docs.python.org/3/library/pathlib.html)

---

## 4. json — 序列化标准

```python
import json

text = json.dumps(obj, ensure_ascii=False, indent=2, default=str)
obj = json.loads(text)                     # 文件版用 json.load(f)
```

**陷阱**: `datetime`/`Decimal`/自定义类默认不可序列化——`default=str` 兜底或转字符串；`ensure_ascii=False` 才能保存中文原貌；`json.dump`（文件）与 `json.dumps`（字符串）一字之差。

> 🌐 官方文档：[json — JSON 编解码器](https://docs.python.org/3/library/json.html)

---

## 5. logging — 生产日志

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

log.info("处理 %d 条记录", n)          # 惰性格式化，优于 f-string
try:
    risky()
except Exception:
    log.exception("处理失败")          # 自动带完整栈
```

**要点**: 库代码只 `getLogger(__name__)`，不 `basicConfig`（配置权归应用）；`log.exception` 只能在 except 块内用。

> 🌐 官方文档：[logging — 日志工具](https://docs.python.org/3/library/logging.html)

---

## 6. re — 正则表达式

```python
import re

m = re.search(r"(\d{4})-(\d{2})", "2026-09-10")
m.group(1)                        # '2026'，分组捕获
re.findall(r"\w+", "hello world") # ['hello', 'world']
re.sub(r"\s+", " ", text)         # 替换
pattern = re.compile(r"^\w+$")    # 高频使用先编译
```

**陷阱**: `match` 只锚定开头，全文匹配用 `fullmatch`；贪婪量词 `.*` 常吃过头，用 `.*?` 惰性。

> 🌐 官方文档：[re — 正则表达式操作](https://docs.python.org/3/library/re.html)

---

## 7. datetime / time — 时间处理

```python
from datetime import datetime, date, timezone, timedelta

now = datetime.now(timezone.utc)          # 永远用带时区的 aware 时间
iso = now.isoformat()                     # '2026-09-10T08:30:00+00:00'
parsed = datetime.fromisoformat(iso)      # 对称解析
tomorrow = now + timedelta(days=1)
date.today().strftime("%Y-%m-%d")
```

**陷阱**: `datetime.now()`（无参）返回**本地时间 naive 对象**，存储/传输一律 `timezone.utc`；naive 与 aware 比较抛 TypeError。

> 🌐 官方文档：[datetime — 日期与时间类型](https://docs.python.org/3/library/datetime.html)

---

## 8. 其他必知模块速览

| 模块 | 一句话 | 代表 API | 官方链接 |
|------|--------|---------|----------|
| `os` / `sys` | 系统接口与解释器 | `os.environ`、`sys.argv`、`sys.exit` | [os](https://docs.python.org/3/library/os.html) · [sys](https://docs.python.org/3/library/sys.html) |
| `subprocess` | 调外部命令 | `subprocess.run(["ls", "-la"], capture_output=True, check=True)` | [subprocess](https://docs.python.org/3/library/subprocess.html) |
| `argparse` | CLI 解析基线 | 能读懂即可，新项目用 typer | [argparse](https://docs.python.org/3/library/argparse.html) |
| `typing` | 类型工具 | 见 [typing 全表](../language-concepts/05-typing-annotations.md) | [typing](https://docs.python.org/3/library/typing.html) |
| `functools` | 函数工具 | `@wraps`、`@lru_cache`、`partial` | [functools](https://docs.python.org/3/library/functools.html) |
| `dataclasses` | 数据类 | `@dataclass`、`field`、`asdict` | [dataclasses](https://docs.python.org/3/library/dataclasses.html) |
| `contextlib` | 上下文工具 | `@contextmanager`、`suppress` | [contextlib](https://docs.python.org/3/library/contextlib.html) |
| `sqlite3` | 内置数据库 | `sqlite3.connect("app.db")` | [sqlite3](https://docs.python.org/3/library/sqlite3.html) |
| `unittest.mock` | 测试替身 | 新项目用 `pytest` + `mocker` | [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) |
| `random` / `secrets` | 随机数 | 随机值用 `random`，安全用途（令牌）必须 `secrets` | [random](https://docs.python.org/3/library/random.html) · [secrets](https://docs.python.org/3/library/secrets.html) |
| `csv` | 表格文本 | `csv.DictReader(f)` | [csv](https://docs.python.org/3/library/csv.html) |
| `hashlib` / `shutil` | 摘要 / 文件操作 | `shutil.copytree`、`hashlib.sha256` | [hashlib](https://docs.python.org/3/library/hashlib.html) · [shutil](https://docs.python.org/3/library/shutil.html) |

`functools.lru_cache` 一行加缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def fetch_user(uid: int) -> dict: ...
```

> 🧭 深入专篇：[os 与 sys](./04-os-sys.md) · [enum](./05-enum-module.md) · [functools 与 subprocess](./06-functools-subprocess.md)

---

## 🔗 相关文档

- 📄 **[生态库精选](./02-ecosystem-libs.md)** — 标准库之外的能力补充
- 📄 **[内置函数全表](../language-concepts/02-built-in-functions.md)** — 免导入的内建能力
- 📄 **[数据结构速查](../language-concepts/03-data-structures.md)** — collections 的原生基础
