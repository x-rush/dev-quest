# 性能剖析与优化

> **文档简介**: 用 cProfile、py-spy 与 tracemalloc 定位 Python 程序的 CPU 与内存热点，按证据而非直觉优化
>
> **目标读者**: 服务变慢但找不到瓶颈的开发者
>
> **前置知识**: [asyncio 异步并发模型](./01-async-python.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#cProfile` `#py-spy` `#tracemalloc` `#优化` |
| **更新日期** | `2026年9月` |

## 1. 方法论：先测量，再优化

> 过早优化是万恶之源——但前提是你先测量过。

流程：复现 → 剖析（找热点）→ 形成假设 → 只改一处 → 重测对比。没有剖析数据支撑的"优化"，多数是无效甚至负面的。

## 2. cProfile：函数级 CPU 剖析

```bash
uv run python -m cProfile -o out.prof -m myapp.benchmark
```

```python
# 分析结果
import pstats

stats = pstats.Stats("out.prof")
stats.sort_stats("cumulative").print_stats(15)   # 按累计时间看调用链
stats.sort_stats("tottime").print_stats(15)      # 按自身时间看真凶
```

关键字段：

- `tottime`：函数**自身**耗时（排除子调用）——排序找"真凶"
- `cumtime`：含所有子调用的累计耗时——顺调用链找入口

```python
# 代码内剖析某一段
import cProfile
import pstats

def benchmark() -> None:
    profiler = cProfile.Profile()
    profiler.enable()
    slow_function()
    profiler.disable()
    pstats.Stats(profiler).sort_stats("tottime").print_stats(10)
```

## 3. py-spy：剖析"正在运行"的进程

```bash
uv tool install py-spy

py-spy top --pid 12345                    # 实时函数热度榜
py-spy dump --pid 12345                   # 当前栈快照——立刻看出卡在哪
py-spy record -o flame.svg --pid 12345    # 火焰图
```

**生产友好**：采样式剖析，无需改代码、低开销，是排查"线上为什么卡"的第一工具。FastAPI 服务"所有请求都慢"时，`dump` 一眼可识别 `async def` 里混入的阻塞调用（该问题的原理见[asyncio 并发模型](./01-async-python.md)）。

## 4. tracemalloc：内存去哪了

```python
import tracemalloc

tracemalloc.start()
process_batch(records)                       # 被怀疑泄漏的代码
snapshot = tracemalloc.take_snapshot()
top = snapshot.statistics("lineno")[:10]     # 分配最多的 10 行
for stat in top:
    print(stat)
```

**要点**：Python 内存问题多数是"无意持有引用"——全局缓存只增不减、闭包挂住大对象、模块级 list 忘记清理。用 `snapshot2.compare_to(snapshot1, "lineno")` 对比两个时间点，增量来源一目了然。

## 5. 微基准：timeit

```python
import timeit

# 对比两种写法；number 放大次数，取多轮最小值更稳
t1 = timeit.timeit("'-'.join(str(n) for n in range(100))", number=10_000)
t2 = timeit.timeit("'-'.join(map(str, range(100)))",   number=10_000)
print(t1, t2)
```

**要点**：只用于微观对比（两种写法、两种数据结构）。系统级耗时看 cProfile/py-spy，别用 timeit 测整个请求。

## 5.5 剖析结果解读小抄

| 现象 | 典型原因 | 下一步 |
|------|---------|--------|
| `tottime` 集中在序列化函数 | 热路径手写 dict 拼接 | 换 Pydantic 模型或缓存结果 |
| `cumtime` 大头在 `socket.recv` | 等下游响应 | 加缓存或并发请求（见 01 篇） |
| py-spy 栈顶是 `time.sleep`/`recv` 出现在 `async def` | 阻塞调用混入事件循环 | 换异步库或改用 `def` 端点 |
| 内存稳定增长不回落 | 容器/全局 list 无限追加 | 用 `compare_to` 定位增量行号 |

## 6. 常见优化清单（按收益排序）

1. **算法与数据结构**：`list` 成员判断 O(n) → `set`/`dict` O(1)（数据结构见[字典](../../reference/language-concepts/03-data-structures.md)）
2. **批量 IO**：N+1 查询合并为一次 `select(Todo).where(Todo.id.in_(ids))`；HTTP 客户端复用连接池
3. **缓存**：Redis 缓存热点读（接入方式见[生态集成](../../frameworks/03-ecosystem-integration.md)）
4. **并发**：串行外部请求改 `asyncio.gather`/`TaskGroup`
5. **序列化**：Pydantic v2 的 Rust 核心已很快；别在热路径手写循环拼 dict

**反模式提醒**：在没剖析前就换"更快的库"往往白费力气——瓶颈常在数据库或网络，不在 Python 代码本身。优化后如果指标没有变化，先怀疑找错了瓶颈，见[可观测性](../../deployment/03-observability.md)建立基线。

---

## 🔗 相关文档

- 🎓 **[asyncio 异步并发模型](./01-async-python.md)** — 阻塞调用等并发问题的原理
- 📄 **[生态集成](../../frameworks/03-ecosystem-integration.md)** — N+1 查询与缓存优化对象
- 🚀 **[可观测性](../../deployment/03-observability.md)** — 生产指标与剖析工具的衔接
- 📖 **[数据结构字典](../../reference/language-concepts/03-data-structures.md)** — 优化首选方案的基础知识
- 📖 **[标准库字典](../../reference/library-guides/01-standard-library.md)** — cProfile/tracemalloc/timeit 模块速查
