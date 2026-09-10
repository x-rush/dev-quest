# Mock 测试 — 隔离外部依赖

> **文档简介**: 用 monkeypatch、pytest-mock 与 AsyncMock 隔离外部服务，让测试只验证自己的逻辑——快、稳、无副作用
>
> **目标读者**: 被慢测试或不稳定测试困扰的开发者
>
> **前置知识**: [单元测试](./01-unit-testing.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#monkeypatch` `#mock` `#pytest-mock` `#respx` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 判断什么该 mock、什么不该 mock
- ✅ 用 monkeypatch 替换环境变量与模块属性
- ✅ 用 pytest-mock 的 mocker 验证交互
- ✅ 用 AsyncMock 处理异步依赖，用 respx 拦截 httpx

---

## 1. 什么该 Mock

| 依赖 | 建议 |
|------|------|
| 纯函数 / 数据结构 | 不 mock，直接测 |
| 数据库（自有） | 测试库真连（见[集成测试](./02-integration-testing.md)） |
| 第三方 HTTP API | mock（respx） |
| 时间、随机、环境变量 | mock（monkeypatch） |
| 发邮件 / 短信等副作用 | mock |

**原则**：mock 你不拥有的边界；mock 自己写的实现等于没测。

## 2. monkeypatch：pytest 内置

```python
# 被测代码 notify.py
import os
import httpx

def send_alert(message: str) -> bool:
    webhook = os.environ["ALERT_WEBHOOK"]              # 外部配置
    resp = httpx.post(webhook, json={"text": message})
    return resp.is_success
```

```python
# tests/test_notify.py
import httpx
from notify import send_alert

def test_send_alert_uses_env(monkeypatch):
    monkeypatch.setenv("ALERT_WEBHOOK", "http://hook.test/x")

    def fake_post(url, **kwargs):                      # 替换模块属性
        assert url == "http://hook.test/x"
        return httpx.Response(200)

    monkeypatch.setattr("notify.httpx.post", fake_post)
    assert send_alert("磁盘告警") is True
# 测试结束自动还原，无需手写 finally
```

**要点**：`monkeypatch.setattr` 的目标写成 `"模块.路径.属性"` 字符串最不易错；fixture 参数注入，测试结束自动撤销一切替换。

## 3. pytest-mock：mocker 更顺手

```bash
uv add --dev pytest-mock
```

```python
# 被测代码 user_service.py 中：注册成功后调用 send_welcome_email(email)

def test_register_sends_welcome(mocker):
    send = mocker.patch("user_service.send_welcome_email")   # 自动还原
    user_service.register("a@b.c", "secret123")
    send.assert_called_once_with("a@b.c")                    # 验证交互
```

**要点**：

- patch 路径必须是**被测模块引用它的位置**（`user_service.send_welcome_email`），不是定义处
- `assert_called_once_with` 验证"交互"，比只看返回值更完整

## 4. 异步 Mock：AsyncMock

```python
from unittest.mock import AsyncMock
import pytest

@pytest.fixture
def fake_redis():
    r = AsyncMock()
    r.get.return_value = "100"     # await r.get(...) -> "100"
    return r

async def test_stats(fake_redis):
    assert int(await fake_redis.get("count:abc")) == 100
```

**要点**：异步函数必须用 `AsyncMock`；对普通 `MagicMock` 做 await 会直接报错——这本身就是一种保护，防止忘了标记异步。

## 5. respx：拦截 httpx 请求

```bash
uv add --dev respx
```

```python
import httpx
import respx

@respx.mock
async def test_fetch_exchange_rate():
    respx.get("https://api.fx.test/rate").respond(json={"rate": 7.2})
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.fx.test/rate")
    assert r.json()["rate"] == 7.2
```

**要点**：可以进一步用 `respx.get(...).mock(return_value=httpx.Response(500))` 模拟失败路径——重试逻辑只有靠 mock 失败才能测到。

## ✅ 最佳实践

- 先验证交互（`assert_called_once_with`），再验证返回值被正确使用
- Mock 返回值要贴近真实形状，否则测试通过、线上报错
- FastAPI 里优先考虑 `app.dependency_overrides`——它替换整层依赖，比 patch 更贴近真实行为（见[集成测试](./02-integration-testing.md)）
- 不确定是否该 mock 时问一句：这个依赖会让测试变慢、不稳定或有真实副作用吗？

## ❓ 常见问题

**Q1: patch 之后测试通过但线上失败？**
常见原因是 mock 返回形状与真实 API 不符。用真实响应快照做 mock 数据，并在 CI 里定期跑少量"真连"冒烟测试。

**Q2: monkeypatch 和 mocker 用哪个？**
`monkeypatch` 适合环境变量与简单属性替换；`mocker`（pytest-mock）适合创建带交互验证的 Mock 对象。两者都会自动还原。

---

## 🔗 相关文档

- 🧪 **[单元测试](./01-unit-testing.md)** — fixture 与参数化基础
- 🧪 **[集成测试](./02-integration-testing.md)** — 依赖覆盖与测试数据库
- 📄 **[FastAPI 进阶](../frameworks/02-fastapi-advanced.md)** — 依赖注入：可替换性的设计来源
- 📖 **[故障排除](../reference/quick-references/02-troubleshooting.md)** — 常见 mock 报错速查
- 🚀 **[项目：短链接服务](../projects/02-url-shortener.md)** — AsyncMock 模拟 Redis 的实战对象
