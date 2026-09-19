# Node/Python 标准库正文验证

验证日期：2026-09-19。结果：**9 / 9 个命名完整程序通过**。来源为四篇参考文档，运行器直接提取 `library-case` 标记后的原始围栏，不补 import、不包装业务代码、不使用替代实现。

| 文档 | 命名程序 | 验证范围 |
|---|---|---|
| [Node 子进程](../../../../09-nodejs-backend/reference/library-guides/04-child-process.md) | `node-child-buffer` | 参数原样传递、非零退出、maxBuffer 错误 |
| 同上 | `node-child-stream` | 同时消费 stdout/stderr，校验字节数与退出状态 |
| [Node 压缩](../../../../09-nodejs-backend/reference/library-guides/09-zlib.md) | `node-zlib-roundtrip` | gzip、zlib、裸 DEFLATE、Brotli 往返，错误格式与一次性输出上限 |
| 同上 | `node-zlib-stream-limit` | 流式解压总量恰好等于上限、超限、损坏输入 |
| [Python 函数工具与子进程](../../../../10-python-discovery/reference/library-guides/06-functools-subprocess.md) | `python-functools-cache` | 缓存命中、LRU 淘汰、不可哈希参数、可变返回值身份、缓存外复制 |
| 同上 | `python-functools-dispatch` | wraps 元信息、partial 参数覆盖、singledispatch 继承与专门注册 |
| 同上 | `python-subprocess-contract` | 字面参数、非零退出、run 超时、communicate 超时后的显式清理 |
| [Python 枚举](../../../../10-python-discovery/reference/library-guides/05-enum-module.md) | `python-enum-contract` | 成员身份、别名、名称/值查询失败、unique、IntEnum/StrEnum 互操作 |
| 同上 | `python-enum-transition` | 外部字符串转换、非法类型、合法成员的不合法转移、Flag 组合 |

运行环境为 Linux 容器中的 **Node v24.21.0** 和 **Python 3.14.7**。镜像 ID、正文/代码 SHA-256、原始程序、标准输出、标准错误和退出码均保存在 [机器证据](node-python-libraries.json)。一次性程序每次有独立容器，禁用网络、根文件系统只读、源文件只读挂载，并限制内存、CPU、进程数及运行时间。程序内部的失败反例只有匹配预期错误类型或错误码才会继续成功结束；运行器同时要求退出码 0、标准错误为空、标准输出精确匹配。

## 复现

在仓库根目录运行；需要 Python 主控解释器、Docker，以及本地已有 `node:24-bookworm-slim`、`python:3.14-alpine` 镜像。运行器使用 `--pull=never`，不会悄悄下载新版本。

```sh
python shared-resources/tools/document-quality/verify_node_python_libraries.py
```

需要复现完全相同镜像时，可把机器报告中记录的镜像 ID 作为 `--node-image` 与 `--python-image` 参数。若本机没有该 ID，应先明确获取对应镜像，再复跑；标签在未来可能指向不同版本。

提取前会检查九个案例集合是否完整、唯一；缺少、重复或标记格式错误时拒绝覆盖报告。所有哈希以 UTF-8、CRLF 规范化为 LF 计算，代码带一个结尾换行。报告只记录这次运行，修改正文后需要重跑以更新源哈希。

## 正文修正与边界

- Node 子进程：修正 fork 默认 stdio 行为，区分 shell 参数与目标程序选项、管道背压与总体内存、exit/close/kill、孤儿与僵尸进程；明确 POSIX 外部命令片段和 Windows 批处理的环境前提。
- Node 压缩：区分 zlib 与裸 DEFLATE，删除固定压缩字节数、Brotli 总更小和等级越高总更小的断言；区分流缓冲、总解压量、CPU 时间与 HTTP 分帧。
- Python 函数工具：修正“在缓存函数 return 前复制即可避免缓存污染”的错误建议；补线程安全与只执行一次的区别、缓存持有对象、bool 命中 int 分派、partial 关键字覆盖。
- Python 子进程：区分 run 与 communicate 超时的清理责任，说明 communicate 仍会缓冲输出、进程树不等于直接子进程。
- Python 枚举：修正 auto、成员身份和默认相等语义的过度概括，区分 IntEnum 与 StrEnum 的引入版本，补输入转换与状态转移两层检查。

**未覆盖**：上文未标记的局部片段、外部 ffmpeg/pandoc/Git 命令、fork IPC、Windows 批处理、平台信号与整棵进程树清理、HTTP 压缩中间件/代理、Zstd、性能基准、多线程缓存竞态、持久化订单并发以及其它 Python/Node 版本。这份报告不把整篇文档或整个模块升级为“全部运行通过”。

官方参考核对入口：[Node 24 child_process](https://nodejs.org/docs/latest-v24.x/api/child_process.html)、[Node 24 zlib](https://nodejs.org/docs/latest-v24.x/api/zlib.html)、[Python 3.14 functools](https://docs.python.org/3.14/library/functools.html)、[subprocess](https://docs.python.org/3.14/library/subprocess.html)、[enum](https://docs.python.org/3.14/library/enum.html)。
