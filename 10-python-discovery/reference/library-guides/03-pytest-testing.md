# pytest 测试指南 — fixture、参数化与常用插件

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#pytest` `#fixture` `#参数化` `#测试` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

pytest 是 Python 事实标准的测试框架：`assert` 直言式断言、`fixture` 声明式夹具、按名字前缀自动发现测试。它以"函数即测试、参数即夹具"的低仪式感取代 unittest 的类模板写法，并与 FastAPI 的 `TestClient`、依赖覆盖机制天然契合。

## 📖 语法 / 签名

```python
import pytest

# 测试发现约定：test_*.py 内的 test_* 函数/方法
def test_add():
    assert add(1, 2) == 3            # 普通 assert，失败时展示表达式细节

# fixture：按名字注入的夹具；scope 控制 生命周期 function/class/module/session
@pytest.fixture
def store():
    s = Store()
    yield s                          # yield 前是准备，之后是清理
    s.close()

# 参数化：一组数据跑同一断言
@pytest.mark.parametrize(("a", "b", "expected"), [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add_many(a, b, expected):
    assert add(a, b) == expected

# 异常断言
with pytest.raises(ValueError, match="非法"):
    parse_port("-1")

# marker：跳过与预期失败
@pytest.mark.skipif(sys.version_info < (3, 14), reason="需要 3.14+")
@pytest.mark.slow                  # 自定义标记，须在 pyproject 注册
def test_something(): ...
```

命令行：`uv run pytest`（全量）、`pytest path::test_name`（定位）、`pytest -k expr`（按名过滤）、`pytest -x`（首败即停）、`pytest --lf`（只跑上次失败）。

## 💡 示例

```python
# conftest.py：无需 import 即对同目录测试可见的共享 fixture
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:       # with 确保生命周期事件触发
        yield c

# test_health.py
def test_health(client):
    assert client.get("/health").json() == {"ok": True}
```

常用插件：`pytest-cov`（覆盖率）、`pytest-asyncio`（async 测试）、`pytest-mock`（`mocker` 夹具）、`anyio`（FastAPI 自带，双后端）。

## ⚠️ 常见陷阱

| 陷阱 | 说明 |
|------|------|
| fixture 不写类型注解 | 参数注入靠名字匹配，注解缺失时报错难读 |
| 把 fixture 函数当普通测试依赖调用 | @pytest.fixture、@pytest.fixture(...) 及等价的装饰函数调用均可声明；测试通常通过参数名字请求夹具，由 pytest 管理生命周期 |
| scope 放大导致测试互相污染 | 共享连接等资源可以是 session 级，但每个测试仍需隔离或恢复数据；scope 应按资源成本与状态边界决定 |
| 测试依赖执行顺序 | 默认收集顺序不应被当成业务契约；插件、筛选和并行运行会影响执行安排 |
| 异步测试缺插件 | 裸 `async def test_` 会被跳过并警告；装 pytest-asyncio 或用 anyio 标记 |
| mock 了错误的目标路径 | patch 要打在"被使用处"的命名空间，不是"定义处"（详见 Mock 测试篇） |

<!-- full-library-explanation -->
## 从失败行为设计测试

前置知识是函数、assert 和异常。fixture 是由 pytest 管理准备与清理的资源工厂，不是测试函数参数的默认值。测试通过名字请求它，scope 决定多个测试是否共享同一个实例；扩大作用域前先确认状态如何复原。

在已安装 pytest 的项目中创建 `test_port.py`：

```python
import pytest

def parse_port(text):
    value = int(text)
    if not 1 <= value <= 65535:
        raise ValueError("port out of range")
    return value

@pytest.mark.parametrize("text, expected", [("1", 1), ("8080", 8080), ("65535", 65535)])
def test_valid_port(text, expected):
    assert parse_port(text) == expected

@pytest.mark.parametrize("text", ["0", "65536", "abc"])
def test_invalid_port(text):
    with pytest.raises(ValueError):
        parse_port(text)
```

执行 `python -m pytest test_port.py -q` 应通过 6 个用例。练习：把上界改成 `< 65535`，已有边界用例应失败；恢复实现后再通过。这样验证的是对外契约，而不是实现调用了几次 int。

## 🔗 相关条目

- 📄 **[单元测试](../../testing/01-unit-testing.md)** — fixture 的操作指南篇
- 📄 **[Mock 测试](../../testing/03-mocking-testing.md)** — monkeypatch 与 mocker 详解
- 📄 **[uv 包管理器](../framework-essentials/03-uv-package-manager.md)** — `uv add --dev pytest` 的安装侧
- 📄 **[CI/CD 流水线](../../deployment/02-ci-cd-pipelines.md)** — pytest 在流水线中的执行位


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
