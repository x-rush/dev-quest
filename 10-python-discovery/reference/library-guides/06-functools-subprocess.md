# functools 与 subprocess — 函数工具与子进程

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#functools` `#subprocess` `#lru_cache` `#partial` `#wraps` `#singledispatch` `#shell注入` |
| **更新日期** | `2026年9月` |

## 📌 定义

functools 是"函数层面的胶水"：记忆化缓存（`cache`/`lru_cache`）、偏函数（`partial`）、装饰器元信息保全（`wraps`）、按类型分派（`singledispatch`）、折叠（`reduce`）。subprocess 是"调外部命令的正解"：`run()` 一站式 API——参数列表不经 shell 解析、可控捕获输出、可控超时，全面替代 `os.system`。

## 📖 语法 / 详解

### functools 速览

| API | 一句话 | 关键点 |
|-----|--------|--------|
| `@lru_cache(maxsize=128)` | LRU 记忆化 | 参数必须可哈希（实测 dict 参数抛 TypeError）；`maxsize=None` 即无界 |
| `@cache` | 无界缓存（3.9+ 简写） | 等价 `lru_cache(maxsize=None)`，注意内存 |
| `partial(func, *a, **kw)` | 固定部分参数 | `partial(int, base=2)("101")` → 5（实测） |
| `reduce(fn, it, init)` | 折叠 | 少用：`sum`/`"".join` 更清晰 |
| `@wraps(func)` | 装饰器保元数据 | 保留 `__name__`/`__doc__`/`__wrapped__`（实测） |
| `@singledispatch` | 按第一参数类型分派 | 注解或 `.register(int)` 注册 |

记忆化与 unhashable 陷阱（本机 3.14.7 实测）：

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

fib(40)                 # 秒回：O(2^n) → O(n)
fib.cache_info()        # CacheInfo(hits=..., misses=41, maxsize=128, currsize=41)
fib({"a": 1})           # TypeError: unhashable type: 'dict'（实测）
```

`@wraps` 前后对比（实测）：

```python
from functools import wraps

def bare(f):
    def wrapper(*a, **k): return f(*a, **k)
    return wrapper

@bare
def docme(): "doc"
docme.__name__, docme.__doc__        # ('wrapper', None) —— 元信息丢了

def proper(f):
    @wraps(f)
    def wrapper(*a, **k): return f(*a, **k)
    return wrapper

@proper
def docme2(): "doc"
docme2.__name__, docme2.__doc__      # ('docme2', 'doc')
docme2.__wrapped__.__name__          # 'docme2' —— __wrapped__ 指向原函数
```

`singledispatch` 按类型分派（实测）：

```python
from functools import singledispatch

@singledispatch
def render(x):
    return f"object: {x!r}"          # 兜底实现

@render.register
def _(x: int):                       # 用注解注册
    return f"int: {x}"

@render.register(str)                # 显式注册
def _(x):
    return f"str: {x}"

render(1)      # 'int: 1'
render("a")    # 'str: a'
render(1.5)    # 'object: 1.5' —— 未注册类型回落兜底
```

### subprocess：run 首选

```python
import subprocess

r = subprocess.run(
    ["ls", "-la"],          # 列表形式：参数不经 shell 解析
    capture_output=True,    # 捕获 stdout/stderr
    text=True,              # 文本模式（默认 bytes）
    check=True,             # 非零退出码抛 CalledProcessError
    timeout=10,             # 超时杀进程并抛 TimeoutExpired
)
r.stdout, r.returncode
```

关键行为（本机 3.14.7 实测）：

- `run(["echo", "hello"], capture_output=True, text=True)` → `returncode 0`、`stdout 'hello\n'`
- `run(["false"], check=True)` → `CalledProcessError`（returncode 1）
- `run(["sleep", "1"], timeout=0.3)` → `TimeoutExpired`

`Popen` 何时用：需要**与进程交互**（边写边读、串管道、长驻托管）才下到 `Popen` + `communicate()`；一次性拿结果用 `run`：

```python
p = subprocess.Popen(["echo", "popen"], stdout=subprocess.PIPE, text=True)
out, _ = p.communicate()     # 'popen\n'
p.returncode                 # 0（实测）
```

### shell=True 的注入风险

```python
subprocess.run(f"echo {user_input}", shell=True)   # ❌ user_input="x; rm -rf ~" 直接执行
subprocess.run(["echo", user_input])               # ✅ 参数原样传递，无解析
```

`shell=True` 只在命令本身是受信静态字符串（如 `ps aux | grep python` 管道）时使用；含用户输入一律列表参数 + 默认 `shell=False`。

## 💡 示例

组合拳：`lru_cache` 给慢查询加缓存，`subprocess.run` 安全地查 git 版本（实测输出 `d9def1d`）：

```python
from functools import lru_cache
import subprocess

@lru_cache(maxsize=1)
def git_version(repo: str) -> str:
    r = subprocess.run(
        ["git", "-C", repo, "describe", "--tags", "--always"],
        capture_output=True, text=True, check=True, timeout=5,
    )
    return r.stdout.strip()

git_version("/path/to/repo")     # 'd9def1d' —— 失败抛 CalledProcessError，超时抛 TimeoutExpired
```

## ⚠️ 常见陷阱

- ❌ **lru_cache 直接吃 dict/list 参数**：`TypeError: unhashable type`（实测）。
  ✅ 收参转 tuple；或把参数拆成标量；自定义对象保证 `__hash__` 稳定。
- ❌ **缓存可变返回值**：调用方原地 `append` 会污染缓存，下一个"命中"拿到脏数据。
  ✅ 返回 tuple/str 等不可变类型，或返回前拷贝并在文档标注。
- ❌ **装饰器忘 `@wraps`**：`__name__` 变 'wrapper'、`__doc__` 丢失（实测）。
  ✅ wrapper 首行 `@wraps(func)`，详见 [06-decorators](../language-concepts/06-decorators.md)。
- ❌ **`shell=True` + f-string 拼用户输入**：命令注入。
  ✅ 列表参数 + 默认 `shell=False`。
- ❌ **`check=False`（默认）时当成功处理**：非零退出静默，下游解析空 stdout。
  ✅ "失败即异常"场景一律 `check=True`；需要区分错误码时才手工查 `returncode`。
- ❌ **忘 timeout**：外部命令卡死拖垮调用方。
  ✅ 给有界超时并处理 `TimeoutExpired`（配合重试策略）。

## 🔗 相关条目

- 📄 **[装饰器](../language-concepts/06-decorators.md)** — `@wraps` 的完整展开
- 📄 **[os 与 sys](./04-os-sys.md)** — `os.system` 与 subprocess 的分工边界
- 📄 **[asyncio 并发](../language-concepts/09-asyncio-concurrency.md)** — 异步版子进程走 `asyncio.create_subprocess_exec`
- 📄 **[标准库导航](./01-standard-library.md)** — 标准库场景地图
- 🌐 **[官方文档：functools](https://docs.python.org/3/library/functools.html)** · **[subprocess](https://docs.python.org/3/library/subprocess.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
