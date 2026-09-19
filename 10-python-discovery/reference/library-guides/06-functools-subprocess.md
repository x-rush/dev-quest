# functools 与 subprocess — 函数工具与子进程

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#functools` `#subprocess` `#lru_cache` `#partial` `#wraps` `#singledispatch` `#shell注入` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

functools 是"函数层面的胶水"：记忆化缓存（`cache`/`lru_cache`）、偏函数（`partial`）、装饰器元信息保全（`wraps`）、按类型分派（`singledispatch`）、折叠（`reduce`）。subprocess 提供外部进程的输入、输出、退出码和生命周期管理。一次性任务通常从 run() 开始；参数列表配合默认 shell=False 可以避免 shell 语法解释，但还要验证目标程序自身的选项。

## 📖 语法 / 详解

### functools 速览

| API | 一句话 | 关键点 |
|-----|--------|--------|
| `@lru_cache(maxsize=128)` | LRU 记忆化 | 参数必须可哈希（dict 参数不可哈希）；`maxsize=None` 即无界 |
| `@cache` | 无界缓存（3.9+ 简写） | 等价 `lru_cache(maxsize=None)`，注意内存 |
| `partial(func, *a, **kw)` | 固定部分参数 | `partial(int, base=2)("101")` → 5 |
| `reduce(fn, it, init)` | 折叠 | 少用：`sum`/`"".join` 更清晰 |
| `@wraps(func)` | 装饰器保元数据 | 保留 `__name__`/`__doc__`/`__wrapped__` |
| `@singledispatch` | 按第一参数类型分派 | 注解或 `.register(int)` 注册 |

记忆化与 unhashable 陷阱（行为说明；完整命名案例见文末）：

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

fib(40)                 # 此输入下每个 n 只首次计算；不能将缓存等同于恒定耗时
fib.cache_info()        # CacheInfo(hits=..., misses=41, maxsize=128, currsize=41)
fib({"a": 1})           # TypeError: unhashable type: 'dict'
```

`@wraps` 前后对比：

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

`singledispatch` 按类型分派：

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

### 缓存与其它函数工具的边界

lru_cache/cache 线程安全表示内部缓存结构保持一致，不保证多个并发首次请求只执行一次函数。它们会持有参数和结果引用；缓存实例方法还会持有 self。不要直接缓存协程、生成器或每次都应创建新可变对象的函数。缓存参数必须可哈希，tuple 内若包含 list 仍不可哈希；转换为 tuple 也不能解决依赖外部状态的过期问题。

cached_property 把首次计算结果保存在实例属性，删除该属性后可重新计算，通常需要实例 __dict__。Python 3.12 起没有旧版内部锁；需要只执行一次的并发场景应自行同步。partial 的关键字默认值可在调用时覆盖；Python 3.14 的 Placeholder 可预留位置参数，但学习项目若兼容 3.12 不应无条件使用它。singledispatch 根据首参数的运行时类型及继承关系选择实现；bool 是 int 的子类，也会命中 int 注册。类型注解本身不负责输入校验。

### subprocess：run 首选

```python
import subprocess
import sys

r = subprocess.run(
    [sys.executable, "--version"],          # 列表形式：参数不经 shell 解析
    capture_output=True,    # 捕获 stdout/stderr
    text=True,              # 文本模式（默认 bytes）
    check=True,             # 非零退出码抛 CalledProcessError
    timeout=10,             # 超时杀进程并抛 TimeoutExpired
)
r.stdout, r.returncode
```

以下命令片段要求 POSIX 命令环境，不适合直接复制到 Windows；文末完整实验统一调用 sys.executable：

- `run(["echo", "hello"], capture_output=True, text=True)` → `returncode 0`、`stdout 'hello\n'`
- `run(["false"], check=True)` → `CalledProcessError`（returncode 1）
- `run(["sleep", "1"], timeout=0.3)` → `TimeoutExpired`

`Popen` 何时用：需要**与进程交互**（边写边读、串管道、长驻托管）才下到 `Popen`；输出有界时可用 `communicate()`；一次性拿结果用 `run`：

```python
import subprocess
import sys
p = subprocess.Popen([sys.executable, "-c", "print('popen')"], stdout=subprocess.PIPE, text=True)
out, _ = p.communicate()     # 'popen\n'
p.returncode                 # 0
```

communicate() 会把捕获输出保存在内存，它不是流式转发 API。数据很大时考虑重定向文件或并发消费管道，不要只 wait() 而无人读取 stdout/stderr。run(timeout=...) 超时会终止并等待直接子进程；Popen.communicate(timeout=...) 超时不会自动杀进程，需要显式 kill 后再次 communicate 回收，且两者都不能保证自动清理孙进程。进程创建阶段也不一定能被超时及时打断。

### shell=True 的注入风险

```python
subprocess.run(f"echo {user_input}", shell=True)   # ❌ user_input="x; rm -rf ~" 直接执行
subprocess.run(["echo", user_input])               # ✅ 参数原样传递，无解析
```

只有确实需要 shell 语法时才考虑 shell=True，并处理相应平台的引用规则。普通可执行程序优先使用参数列表和 shell=False；仍要防止目标程序自身的选项注入，不能把列表参数称为一切场景都安全。

## 💡 示例

局部组合示例：查询仓库版本，并缓存同一路径的结果。仓库变化后必须调用 git_version.cache_clear() 或移除缓存，否则会返回旧版本；调用前将占位路径换成实际仓库：

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

- ❌ **lru_cache 直接吃 dict/list 参数**：`TypeError: unhashable type`。
  ✅ 收参转 tuple；或把参数拆成标量；自定义对象保证 `__hash__` 稳定。
- ❌ **缓存可变返回值**：调用方原地 `append` 会污染缓存，下一个"命中"拿到脏数据。
  ✅ 返回 tuple/str 等不可变类型。若需要可变副本，在缓存函数外的非缓存包装函数中复制；在被缓存函数内部 return 前复制，仍只执行一次，后续命中仍返回同一对象。
- ❌ **装饰器忘 `@wraps`**：`__name__` 变 'wrapper'、`__doc__` 丢失。
  ✅ 在 wrapper 定义前添加 `@wraps(func)`，详见 [06-decorators](../language-concepts/06-decorators.md)。
- ❌ **`shell=True` + f-string 拼用户输入**：命令注入。
  ✅ 列表参数 + 默认 `shell=False`。
- ❌ **`check=False`（默认）时当成功处理**：非零退出静默，下游解析空 stdout。
  ✅ "失败即异常"场景一律 `check=True`；需要区分错误码时才手工查 `returncode`。
- ❌ **忘 timeout**：外部命令卡死拖垮调用方。
  ✅ 给有界超时并处理 `TimeoutExpired`（配合重试策略）。

<!-- full-library-explanation -->
## 缓存依赖输入，子进程依赖协议

前置知识是函数参数、对象可变性和进程退出码。缓存把输入映射到先前结果，只有结果在缓存有效期间仍适用才有价值。给“查询当前 Git 提交”加无期限缓存，会在仓库改变后返回旧结果；需要明确清除时机，不能只考虑第一次运行快不快。

完整且跨平台的小实验保存为 `child.py`：

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-c", "import sys; print(sys.argv[1])", "a b; c"],
    capture_output=True, text=True, check=True, timeout=5,
)
print(result.stdout.strip())
print(result.returncode)
```

输出 `a b; c` 和 `0`，空格与分号是一个普通参数的内容，没有被 shell 当作命令。练习：让子进程执行 `sys.exit(2)`，check=True 时应抛 CalledProcessError；改为 False 时应检查 returncode，不能把“没有异常”误当成执行成功。

参数列表减少 shell 注入风险，但不替你验证目标程序的参数语义；例如用户提供的 `--delete` 仍可能被程序当成选项。还要限制允许执行的程序及参数，Windows 批处理文件等特殊入口应按平台规则另外评估。

## 可复现验证：缓存身份、分派与进程失败

下面三个完整程序保存为 `.py` 执行，使用 Python 3.12+ 标准库，不需要 Git 仓库、外部命令或第三方包。上文的短片段用于查语法；只有下列命名案例绑定本页运行报告。

### 缓存命中返回的是同一个对象

<!-- library-case: python-functools-cache -->
```python
from functools import lru_cache

calls = 0

@lru_cache(maxsize=2)
def square(n):
    global calls
    calls += 1
    return n * n

assert square(3) == square(3) == 9
assert calls == 1
assert square.cache_info().hits == 1
square(4)
square(5)
assert square.cache_info().currsize == 2
square(3)  # 3 是最久未使用的键，已被淘汰
assert calls == 4
try:
    square([])
except TypeError:
    pass
else:
    raise AssertionError('unhashable input was accepted')
square.cache_clear()
assert square.cache_info().currsize == 0

@lru_cache(maxsize=1)
def cached_titles():
    return ['learn']

first = cached_titles()
first.append('changed')
assert cached_titles() is first
assert cached_titles() == ['learn', 'changed']

def fresh_titles():
    return cached_titles().copy()  # 复制必须发生在缓存边界之外

copy = fresh_titles()
copy.append('local')
assert fresh_titles() == ['learn', 'changed']
print('functools-cache: hit, eviction, invalid key, shared result, copy')
```

输出为 `functools-cache: hit, eviction, invalid key, shared result, copy`。它解释了为什么“函数里面先 copy 再 return”不能解决缓存返回值污染：命中缓存时函数根本不执行。业务中优先缓存不可变数据；嵌套可变结构还要考虑浅拷贝不足的问题。

### 元信息、偏函数与类型分派

<!-- library-case: python-functools-dispatch -->
```python
from functools import partial, singledispatch, wraps

def traced(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)
    return wrapper

@traced
def greet(name):
    """Create a greeting."""
    return f'hello {name}'

assert greet('Ada') == 'hello Ada'
assert greet.__name__ == 'greet'
assert greet.__doc__ == 'Create a greeting.'
assert greet.__wrapped__('Ada') == 'hello Ada'
binary = partial(int, base=2)
assert binary('101') == 5
assert binary('11', base=10) == 11  # 调用处可覆盖预先绑定的关键字

@singledispatch
def kind(value):
    return 'object'

@kind.register(int)
def _(value):
    return 'integer'

assert kind(1) == kind(True) == 'integer'
assert kind('1') == 'object'

@kind.register(bool)
def _(value):
    return 'boolean'

assert kind(True) == 'boolean'
assert kind(1) == 'integer'
print('functools-dispatch: metadata, override, inheritance, specialization')
```

输出为 `functools-dispatch: metadata, override, inheritance, specialization`。wraps 保留接口元信息，不会自动改变包装函数的实际参数处理；singledispatch 处理运行时类型，不是按字符串内容或任意参数列表选择实现。

### 直接子进程的参数、退出码与两种超时

<!-- library-case: python-subprocess-contract -->
```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, '-c', 'import sys; print(sys.argv[1])', 'a b; c'],
    capture_output=True, text=True, encoding='utf-8', check=True, timeout=5,
)
assert result.stdout == 'a b; c\n'
assert result.stderr == '' and result.returncode == 0

try:
    subprocess.run(
        [sys.executable, '-c', "import sys; sys.stderr.write('invalid'); sys.exit(2)"],
        capture_output=True, text=True, check=True, timeout=5,
    )
except subprocess.CalledProcessError as error:
    assert error.returncode == 2 and error.stderr == 'invalid'
else:
    raise AssertionError('nonzero exit was accepted')

try:
    subprocess.run([sys.executable, '-c', 'import time; time.sleep(10)'], timeout=0.5)
except subprocess.TimeoutExpired:
    pass  # run 已终止并等待这个直接子进程
else:
    raise AssertionError('expected timeout')

with subprocess.Popen(
    [sys.executable, '-c', 'import time; time.sleep(10)'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
) as process:
    try:
        process.communicate(timeout=0.5)
    except subprocess.TimeoutExpired:
        process.kill()       # communicate 超时不会替我们终止它
        process.communicate()  # 完成管道读取并等待回收
    else:
        raise AssertionError('expected communicate timeout')
    assert process.returncode is not None
print('subprocess: literal, nonzero, run timeout, communicate cleanup')
```

输出为 `subprocess: literal, nonzero, run timeout, communicate cleanup`。这里只启动一个直接子进程，没有进程树、网络或长时间输出；不能据此保证 shell 孙进程和平台信号处理已被验证。超时异常的输出字段可能是 bytes，即使开启 text 模式也不能盲目按 str 处理。

练习：给缓存添加“输入还依赖当前配置”的场景，明确何时 cache_clear；把子进程改为退出码 0 但输出非法数据，验证调用方仍要做产物校验。命名证据与复现命令见 [Node/Python 标准库验证](../../../shared-resources/tools/document-quality/reports/node-python-libraries.md)。

## 🔗 相关条目

- 📄 **[装饰器](../language-concepts/06-decorators.md)** — `@wraps` 的完整展开
- 📄 **[os 与 sys](./04-os-sys.md)** — `os.system` 与 subprocess 的分工边界
- 📄 **[asyncio 并发](../language-concepts/09-asyncio-concurrency.md)** — 异步版子进程走 `asyncio.create_subprocess_exec`
- 📄 **[标准库导航](./01-standard-library.md)** — 标准库场景地图
- 🌐 **[官方文档：functools](https://docs.python.org/3/library/functools.html)** · **[subprocess](https://docs.python.org/3/library/subprocess.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
