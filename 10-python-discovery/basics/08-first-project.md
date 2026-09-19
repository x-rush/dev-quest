# 综合项目 — 命令行书签管理器（typer + rich）

## 先理解，再动手

书签工具把输入解析、业务函数和文件存储连接起来。先用小 JSON 文件走通，再用 typer/rich 改善交互。

**本节自测**：新增两个 URL，重启查询，模拟损坏文件与重复 URL。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

持久化与重复策略可解释；显示漂亮表格不代表数据保存正确。

</details>

> **文档简介**: 综合运用函数、类与异常，从零构建一个命令行书签管理器：typer 定义命令、rich 美化输出、JSON 持久化、dataclass 建模、异常体系兜底
>
> **目标读者**: 已完成 basics 01–06 的学习者，需要一个收束型的实战项目
>
> **前置知识**: 能运行脚本，理解 [函数与类](./04-functions-oop.md)、控制流和 [异常处理](./06-exceptions.md)；先补读 [高级特性](./07-advanced-features.md) 中的装饰器，理解 `@app.command()` 注册命令即可。生成器、异步与泛型不作为本项目开工条件。

本课产物是带 `bm` 入口的 Python 工程和 JSON 书签文件。按正文建立工程并 `uv sync` 后，先用 `uv run bm --help` 验证入口安装成功，再按使用示例将 `BM_STORE` 指向父目录已存在的专用测试文件。新增 URL 后启动新进程列表，应能读回；重复新增应退出 1；将测试文件写成 `{` 后列表也应退出 1，且文件仍保留 `{`。保留这三种结果，再运行本页的临时目录测试。

若入口不存在，回查本页 `pyproject.toml` 与 `uv sync`；解释器或依赖找不到，回 [环境搭建](./01-environment-setup.md)；保存后读不回，核对两次进程的 `BM_STORE`，并回查存储层；错误被吞掉则回 [异常处理](./06-exceptions.md)。通过后按 [学习规划](../LEARNING_GUIDE.md) 进入 [Todo API](../projects/01-todo-api.md)，比较命令参数校验与 HTTP 请求校验。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#实战项目` `#typer` `#rich` `#CLI` `#JSON` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本项目后，你将能够：

- ✅ 用 typer 构建多命令 CLI，用 rich 输出表格与彩色提示
- ✅ 用 dataclass + JSON 完成数据的建模与持久化
- ✅ 组织"模型—存储—命令"三层结构的小型项目

---

## 1. 项目设计

**功能需求**：

| 命令 | 行为 |
|------|------|
| `bm add <url> --title 标题 --tag 标签` | 添加书签，URL 去重 |
| `bm list [--tag 标签]` | 表格展示，可按标签过滤 |
| `bm find 关键词` | 标题/URL 模糊搜索（基础练习实现） |
| `bm rm <序号>` | 删除指定书签 |

**技术选型**：typer（基于类型注解的 CLI 框架）+ rich（表格输出）+ 标准库 `json`/`pathlib`。直接使用的包都显式声明为依赖。

**目录结构**：

```
bm/
├── pyproject.toml
└── bm/
    ├── __init__.py
    ├── models.py      # 数据模型（dataclass）
    ├── storage.py     # 存储层（JSON 读写 + 异常）
    └── cli.py         # 命令入口（typer）
```

初始化：

```bash
uv init --python 3.14 bm
cd bm
uv add typer rich
```

按上图创建 `bm/` 目录和空的 `bm/__init__.py`。下面采用根目录包布局；若初始化工具生成了 `src/bm/`，把本页三个文件放入该目录，并相应使用工具生成的构建配置，勿同时保留两个 `bm` 包。这里的完整配置使用根目录布局：在 `pyproject.toml` 中保留已有 `[project]`，补充/替换下面三张表（同名表不能重复）：

```toml
[project.scripts]
bm = "bm.cli:app"

[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["bm"]
```

执行 `uv sync` 安装当前工程与入口，然后运行 `uv run bm --help`。入口脚本必须随工程安装，仅在文件中声明 `[project.scripts]` 不等于已经安装；参见 [uv 工程配置](https://docs.astral.sh/uv/concepts/projects/config/)。

---

## 2. 数据模型层 `models.py`

```python
"""书签数据模型。"""
from dataclasses import dataclass, field

@dataclass
class Bookmark:
    url: str
    title: str
    tags: list[str] = field(default_factory=list)

    def matches(self, keyword: str) -> bool:
        """大小写不敏感的模糊匹配。"""
        kw = keyword.lower()
        return kw in self.title.lower() or kw in self.url.lower()
```

> 回顾：`field(default_factory=list)` 规避可变默认参数陷阱（见[函数与类](./04-functions-oop.md)第 3 节）。

---

## 3. 存储层 `storage.py`

```python
"""JSON 文件存储 + 模块异常体系。"""
import json
import os
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile
from .models import Bookmark

STORE_PATH = Path(os.environ.get("BM_STORE", str(Path.home() / ".bm.json")))

class StoreError(Exception):
    """存储层异常基类。"""


def load() -> list[Bookmark]:
    try:
        raw = json.loads(STORE_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("根节点必须为数组")
        for item in raw:
            if not isinstance(item, dict) or set(item) != {"url", "title", "tags"}:
                raise ValueError("书签字段不完整")
            if not isinstance(item["url"], str) or not isinstance(item["title"], str):
                raise ValueError("URL 与标题必须为字符串")
            if not isinstance(item["tags"], list) or not all(isinstance(t, str) for t in item["tags"]):
                raise ValueError("标签必须为字符串数组")
        return [Bookmark(**item) for item in raw]
    except FileNotFoundError:
        return []                          # 首次使用，空库
    except (ValueError, TypeError, UnicodeError) as e:
        raise StoreError(f"书签文件损坏: {STORE_PATH}") from e
    except OSError as e:
        raise StoreError(f"无法读取: {STORE_PATH}") from e


def save(bookmarks: list[Bookmark]) -> None:
    data = [asdict(b) for b in bookmarks]
    temp_path = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=STORE_PATH.parent,
                                prefix=".bm-", delete=False) as file:
            temp_path = Path(file.name)
            file.write(json.dumps(data, ensure_ascii=False, indent=2))
        temp_path.replace(STORE_PATH)
    except OSError as e:
        raise StoreError(f"无法保存: {STORE_PATH}") from e
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
```

dataclass 的注解不会在运行时检查 JSON 字段类型，因此加载时显式校验，损坏文件保持原样。保存先写同目录临时文件，完整写完再替换，降低中途写入导致原文件截断的风险；这不提供并发写入保护或断电耐久保证。本练习一次只运行一个写入进程，多进程需要文件锁或数据库事务。`BM_STORE` 可指定测试文件，其父目录须先存在。

---

## 4. 命令层 `cli.py`

```python
"""typer 命令入口。"""
import typer
from functools import wraps
from urllib.parse import urlsplit
from rich.console import Console
from rich.table import Table
from . import storage
from .models import Bookmark

app = typer.Typer(help="命令行书签管理器")
console = Console(markup=False)


def guard_store(func):
    """在 CLI 边界把存储异常转成非零退出码，保留内部异常链供调试。"""
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except storage.StoreError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
    return wrapped

@app.command()
@guard_store
def add(url: str, title: str = "",
        tag: list[str] = typer.Option(None, "--tag", "-t")) -> None:
    """添加书签（URL 重复则拒绝）。"""
    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        raise typer.BadParameter("URL 格式错误") from exc
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise typer.BadParameter("URL 必须以 http:// 或 https:// 开头并包含主机")
    bookmarks = storage.load()
    if any(b.url == url for b in bookmarks):
        typer.echo(f"已存在: {url}", err=True)
        raise typer.Exit(code=1)
    bookmarks.append(Bookmark(url=url, title=title or url, tags=tag or []))
    storage.save(bookmarks)
    console.print(f"已添加 {title or url}")


@app.command("list")
@guard_store
def list_bookmarks(tag: str | None = typer.Option(None, "--tag", "-t")) -> None:
    """列出书签，可按标签过滤。"""
    bookmarks = [(i, b) for i, b in enumerate(storage.load(), start=1) if tag is None or tag in b.tags]
    table = Table(title=f"书签 ({len(bookmarks)} 条)")
    table.add_column("序号", justify="right")
    table.add_column("标题")
    table.add_column("URL", style="cyan")
    for i, b in bookmarks:
        table.add_row(str(i), b.title, b.url)
    console.print(table)


@app.command()
@guard_store
def rm(index: int) -> None:
    """按 list 显示的序号删除。"""
    bookmarks = storage.load()
    if not 1 <= index <= len(bookmarks):
        raise typer.BadParameter(f"序号超范围: {index}")
    try:
        removed = bookmarks.pop(index - 1)
    except IndexError as e:
        raise typer.BadParameter(f"序号超范围: {index}") from e
    storage.save(bookmarks)
    console.print(f"已删除 {removed.title}")
```

typer 的魔法：**函数签名即 CLI 接口**——类型注解决定参数解析方式，docstring 即 `--help` 文案，`typer.Option` 定制选项名。这正是[高级特性](./07-advanced-features.md)装饰器知识的落地。

---

## 5. 运行与验证

```bash
uv run bm add https://docs.python.org --title "Python 文档" --tag 官方
uv run bm list                    # rich 表格输出；数据落在 ~/.bm.json
uv run bm add https://docs.python.org --title x  # 失败并退出 1
```

Bash 中下一条命令用 `echo $?` 读取退出码，PowerShell 用 `$LASTEXITCODE`；不要用 `&&` 连接，因为它会跳过失败后的检查。再添加一个不同 URL，分别标记不同标签，过滤后显示的序号仍是原列表序号，`rm` 才不会误删；删除会使后续序号前移，每次删除前重新列表。`rm 0`、负数与越界值必须失败，文件内容不变。

将 `BM_STORE` 指向临时目录文件，验证“新增 → 启动新进程列表 → 重复新增失败 → 筛选 → 删除 → 再列表”；然后向文件写入 `{`，运行列表应退出 1 并报告损坏，文件不能被覆盖成空列表。删除数据文件后再列表应显示空库。这个区别解释了为什么只有 `FileNotFoundError` 可以当作首次使用。

### 用隔离文件自动验收

执行 `uv add --dev pytest`，保存为 `tests/test_cli.py`，再运行 `uv run python -m pytest -q`，预期 10 passed。每个测试只操作临时目录；不接触默认的个人书签文件。

验证记录（2026-09-19）：正文的三个模块与下方测试原样抽取后，在 Python 3.12.14 和 Python 3.14 容器中均为 10 passed，使用 Typer 0.27.2、Rich 15.0.0、pytest 9.1.1。验证覆盖命令行为与临时文件读写；`uv` 安装/入口脚本生成、跨进程竞争和断电恢复不在本轮运行证据范围内。

```python
import pytest
from typer.testing import CliRunner
from bm.cli import app
from bm import storage

runner = CliRunner()

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "STORE_PATH", tmp_path / "data.json")

def test_add_reload_duplicate():
    assert runner.invoke(app, ["add", "https://a.test", "--title", "A"]).exit_code == 0
    assert storage.load()[0].title == "A"
    before = storage.STORE_PATH.read_bytes()
    assert runner.invoke(app, ["add", "https://a.test"]).exit_code == 1
    assert storage.STORE_PATH.read_bytes() == before

def test_filter_preserves_index():
    runner.invoke(app, ["add", "https://a.test", "--tag", "a"])
    runner.invoke(app, ["add", "https://b.test", "--tag", "b"])
    result = runner.invoke(app, ["list", "--tag", "b"])
    assert result.exit_code == 0 and "2" in result.stdout
    assert runner.invoke(app, ["rm", "2"]).exit_code == 0
    assert [b.url for b in storage.load()] == ["https://a.test"]

@pytest.mark.parametrize("index", ["0", "-1", "2"])
def test_invalid_index_preserves_data(index):
    runner.invoke(app, ["add", "https://a.test"])
    before = storage.STORE_PATH.read_bytes()
    assert runner.invoke(app, ["rm", index]).exit_code != 0
    assert storage.STORE_PATH.read_bytes() == before

@pytest.mark.parametrize("raw", ["{", "{}", '[{"url":1,"title":"a","tags":[]}]',
                                '[{"url":"a","title":"b","tags":"bad"}]'])
def test_corruption_preserved(raw):
    storage.STORE_PATH.write_text(raw, encoding="utf-8")
    assert runner.invoke(app, ["list"]).exit_code == 1
    assert storage.STORE_PATH.read_text(encoding="utf-8") == raw

def test_missing_and_invalid_url():
    assert storage.load() == []
    assert runner.invoke(app, ["add", "javascript:alert(1)"]).exit_code != 0
    assert not storage.STORE_PATH.exists()
```

---

## ✅ 最佳实践

命令入口解析输入，业务函数决定哪些操作允许，存储层负责持久化和错误传播；这些责任可以先在少量文件中表达，不必按目录数衡量架构。数据路径由配置或参数提供，测试使用临时路径，避免修改用户真实文件。

人类提示与机器输出分开，成功和失败退出码明确。用损坏 JSON、不存在目录和重复记录测试失败后的文件状态，再验证重新启动能读取成功保存的数据。

---

## 🎯 练习与实践

### 基础练习
- [ ] 实现 `bm find 关键词`：复用 `Bookmark.matches()` 做模糊搜索
- [ ] 补齐 `bm export`（JSON→CSV）与 `bm list` 的添加日期列

### 进阶挑战
- [ ] 把存储层改成 `Storage` 协议（`typing.Protocol`），提供 JSON 与 SQLite 两个实现
- [ ] 为 CLI 编写 pytest 集成测试：`typer.testing.CliRunner` 调用各命令

**提示**：挑战项分别对应 [typing 注解全表](../reference/language-concepts/05-typing-annotations.md)与[标准库导航](../reference/library-guides/01-standard-library.md)的知识点。

---

## 🔗 相关文档

- 📄 **[环境搭建](./01-environment-setup.md)** — 本项目的 uv 工作流来源
- 📄 **[生态库精选](../reference/library-guides/02-ecosystem-libs.md)** — typer/rich 完整能力速查
- 📄 **[FastAPI 速查](../reference/framework-essentials/01-fastapi-essentials.md)** — 相同哲学的 Web 框架进阶


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
