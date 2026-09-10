# 单元测试 — pytest 与 fixture

> **文档简介**: 用 pytest 建立单元测试工作流：断言、fixture 上下文管理、参数化、标记分层与覆盖率
>
> **目标读者**: 想为 Python 代码建立测试习惯的开发者
>
> **前置知识**: [开发工具链](../frameworks/04-devtools.md)（uv 工作流）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#pytest` `#fixture` `#参数化` `#覆盖率` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 编写并运行 pytest 测试，读懂失败报告
- ✅ 用 fixture 管理测试前后置与共享状态
- ✅ 用 `parametrize` 覆盖多组输入
- ✅ 用 marker 分层测试，用 coverage 统计覆盖

---

## 1. 安装与第一个测试

```bash
uv add --dev pytest pytest-cov
```

```python
# pkg/price.py
def apply_discount(price: float, percent: int) -> float:
    """按百分比打折，percent 取值 0-100。"""
    if not 0 <= percent <= 100:
        raise ValueError("percent 必须在 0-100")
    return round(price * (100 - percent) / 100, 2)
```

```python
# tests/test_price.py
import pytest
from pkg.price import apply_discount

def test_normal_discount():
    assert apply_discount(100, 20) == 80.0

def test_invalid_percent():
    with pytest.raises(ValueError, match="0-100"):   # 同时校验异常消息
        apply_discount(100, 150)
```

```bash
uv run pytest -q      # 全量运行；-v 看明细，-k name 按名过滤
```

**要点**：文件与函数以 `test_` 开头即被发现；普通 `assert` 即可，失败时 pytest 自动展开左右值差异，无需记忆 `assertXxx` API。

## 2. fixture：共享的测试上下文

```python
# tests/conftest.py —— 同目录及子目录的测试自动可见
import pytest
from store import Cart

@pytest.fixture
def empty_cart():
    return Cart()

@pytest.fixture
def cart_with_item(empty_cart):
    """fixture 可以依赖其他 fixture，构成装配树。"""
    empty_cart.add("apple", price=3.5, qty=2)
    return empty_cart

@pytest.fixture(autouse=True)
def reset_registry():
    yield                       # yield 前：准备
    Cart._registry.clear()      # yield 后：清理（等价 setup/teardown）
```

```python
# tests/test_cart.py —— 函数参数即注入，不用 import fixture
def test_total(cart_with_item):
    assert cart_with_item.total() == 7.0
```

**要点**：

- fixture 默认每个测试新建一份（`scope="module"` 等可改变作用域，慎用避免状态串扰）
- `conftest.py` 是 fixture 的公共存放点，测试文件不写 import

## 3. 参数化：一份逻辑多组数据

```python
@pytest.mark.parametrize(
    ("price", "percent", "expected"),
    [
        (100, 0, 100.0),      # 下边界
        (100, 100, 0.0),      # 上边界
        (9.99, 10, 8.99),     # 精度
    ],
)
def test_apply_discount(price, percent, expected):
    assert apply_discount(price, percent) == expected
```

**要点**：每个参数组独立运行、独立报告失败；边界值优先于随机值。

## 4. 标记与覆盖率

```python
@pytest.mark.slow               # 自定义标记
def test_big_export(): ...
```

```toml
# pyproject.toml —— 自定义 marker 需注册，否则告警
[tool.pytest.ini_options]
markers = ["slow: 耗时用例"]
addopts = "-q"
```

```bash
uv run pytest -m "not slow"                # 跳过慢测试
uv run pytest --cov=pkg --cov-report=term  # 覆盖率报告
```

**要点**：覆盖率是"发现没测到的地方"的探测器，别为 100% 的数字写无意义断言。

## ✅ 最佳实践

- 测试名描述行为：`test_expired_token_returns_401`，而非 `test_3`
- 单元测试不碰网络/数据库——外部依赖交给 [Mock 测试](./03-mocking-testing.md)
- 每修一个 bug，先写复现测试再修复，让回归永久留下
- 测试代码同样过 ruff（CI 门禁见[CI/CD](../deployment/02-ci-cd-pipelines.md)）

## ❓ 常见问题

**Q1: fixture 和普通辅助函数怎么选？**
需要"准备 + 清理"或被多个测试注入时用 fixture；纯计算转换用普通函数即可。

**Q2: 测试之间如何保证隔离？**
autouse fixture 重置全局状态 + 每测试新建夹具实例；永远不要依赖测试执行顺序。

---

## 🔗 相关文档

- 🧪 **[集成测试](./02-integration-testing.md)** — 下一层：请求级与数据库级验证
- 🧪 **[Mock 测试](./03-mocking-testing.md)** — 隔离外部依赖
- 🚀 **[项目：TODO API](../projects/01-todo-api.md)** — 本篇知识的实战落地
- 📄 **[开发工具链](../frameworks/04-devtools.md)** — pytest 安装与 uv 工作流
- 📖 **[故障排除](../reference/quick-references/02-troubleshooting.md)** — 测试环境问题速查
