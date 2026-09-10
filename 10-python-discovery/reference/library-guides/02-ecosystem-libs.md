# 生态库精选 — requests / httpx / pandas / pydantic / typer / rich

## 概述

Python 第三方生态是它统治多领域的核心原因。本条目精选六个高频库，按"HTTP 客户端 / 数据处理 / 数据校验 / 命令行体验"分组，给出选型与核心 API。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#requests` `#httpx` `#pandas` `#pydantic` `#typer` `#rich` |
| **更新日期** | `2026年9月` |

---

## 1. HTTP 客户端：requests vs httpx

**选型**：脚本/同步代码用 requests（事实标准、生态兼容）；异步或需要 HTTP/2 用 httpx（API 与 requests 几乎一致，可双模式）。

```python
import requests

resp = requests.get("https://api.github.com/users/python", timeout=10)
resp.raise_for_status()            # 4xx/5xx 抛异常，务必调用
data = resp.json()

requests.post(url, json={"k": "v"}, headers={"X-Token": "t"})
```

```python
import httpx, asyncio

async def fetch_all(urls: list[str]) -> list[dict]:
    async with httpx.AsyncClient(timeout=10) as client:
        rs = await asyncio.gather(*(client.get(u) for u in urls))
        return [r.json() for r in rs]
```

**陷阱**: 两个库都不默认超时（**必须显式 `timeout=`**）；`raise_for_status()` 忘调则 404 也当成功解析；生产重试交给 `tenacity` 或 httpx 传输层。

---

## 2. pandas — 表格数据处理

```python
import pandas as pd

df = pd.read_csv("sales.csv")                 # 读表格
df.head(); df.info(); df.describe()           # 三板斧探查

df[df["amount"] > 100]                        # 布尔筛选
df.groupby("region")["amount"].sum()          # 分组聚合
df.sort_values("amount", ascending=False)
df["date"] = pd.to_datetime(df["date"])       # 类型转换
df = df.dropna(subset=["amount"])             # 缺失值
df.merge(users, on="uid", how="left")         # 类 SQL join
df.to_parquet("out.parquet")                  # 列式输出
```

**陷阱**: 链式赋值 `df[a][b] = x` 触发 SettingWithCopyWarning，用 `.loc[mask, col] = x`；逐行 `iterrows` 慢百倍，能用向量化就不用循环。

> 数据科学纵深（NumPy/Matplotlib/scikit-learn）属模块 advanced-topics 规划范畴，此处仅导航。

---

## 3. pydantic — 运行时数据校验

```python
from pydantic import BaseModel, Field

class Settings(BaseModel):
    host: str = "localhost"
    port: int = Field(default=8000, ge=1, le=65535)
    debug: bool = False

cfg = Settings.model_validate_json('{"host": "0.0.0.0", "port": 9000}')
cfg.port                      # 9000，非法值抛 ValidationError（含全部字段错误）
```

**要点**: 校验失败一次报出**所有**字段错误；`model_validate`/`model_dump`/`model_dump_json` 是 v2 核心三角；与 FastAPI 无缝集成（详见 [FastAPI 速查](../framework-essentials/01-fastapi-essentials.md)）。

---

## 4. typer — 类型注解式 CLI

```python
import typer

app = typer.Typer()

@app.command()
def greet(
    name: str,
    shout: bool = typer.Option(False, "--shout", "-s"),
) -> None:
    """向某人问好。"""
    msg = f"Hello, {name}!"
    print(msg.upper() if shout else msg)

if __name__ == "__main__":
    app()
```

```bash
uv run greet.py ada --shout       # HELLO, ADA!
uv run greet.py --help            # 自动生成帮助（来自 docstring 与注解）
```

**要点**: 函数签名即 CLI；多命令用 `@app.callback()` 组织子命令组；完整实战见[综合项目](../../basics/08-first-project.md)。

---

## 5. rich — 终端美化

```python
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

console.print("[bold red]错误[/]: 文件不存在")     # 标记语法着色
console.print_exception()                        # 带语法高亮的异常栈

table = Table(title="模块状态")
table.add_column("模块"); table.add_column("进度", justify="right")
table.add_row("10-python", "8/8")
console.print(table)

for step in track(range(100), description="处理中:"):
    ...
```

**要点**: rich 是 typer 的底层依赖（`typer[all]` 已含）；日志美化用 `rich.logging.RichHandler`；Jupyter 中表格自动渲染。

---

## 6. 其余高频生态速览

| 库 | 一句话 | 典型场景 |
|------|--------|---------|
| `pyyaml` / `tomllib` | 配置解析 | tomllib 3.11+ 内置读 TOML |
| `sqlalchemy 2.x` | ORM 标杆 | 类型化查询 `select(User).where(...)` |
| `pytest` | 测试框架 | `assert` 直写 + fixture 体系 |
| `openpyxl` | Excel 读写 | 报表自动化 |
| `beautifulsoup4` / `lxml` | HTML 解析 | 配 requests 做轻量爬取 |
| `python-dotenv` | .env 加载 | 本地密钥不入库 |
| `tenacity` | 重试装饰器 | `@retry(wait=wait_exponential())` |
| `loguru` | 开箱日志 | 比 logging 简单的多用途场景 |
| `ruff` / `mypy` | 质量工具 | 格式化与静态检查（见 [环境搭建](../../basics/01-environment-setup.md)） |

---

## 选型速查表

| 需求 | 首选 | 备选 |
|------|------|------|
| 同步 HTTP | requests | httpx |
| 异步 HTTP | httpx | aiohttp |
| 表格分析 | pandas | polars（更快） |
| 数据校验 | pydantic v2 | msgspec（更快） |
| CLI | typer | argparse（零依赖） |
| 终端输出 | rich | — |
| 重试 | tenacity | 手写装饰器（见[高级特性](../../basics/07-advanced-features.md)） |

---

## 🔗 相关文档

- 📄 **[标准库导航](./01-standard-library.md)** — 免安装的基础能力
- 📄 **[FastAPI 核心速查](../framework-essentials/01-fastapi-essentials.md)** — pydantic 的最大舞台
- 📄 **[综合项目：书签管理器](../../basics/08-first-project.md)** — typer/rich 完整实战
