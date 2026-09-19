# Go / Node.js / Python 第十五轮正文提取运行验证

Three named, complete P1 core/standard-library Markdown programs extracted byte-for-byte from their marked fences. A pass verifies only the listed output contracts.

| Case | Source | Runtime | Result |
| --- | --- | --- | --- |
| `go-control-flow-contract` | `01-go-backend/basics/06-control-structures.md` | `golang:1.27` | PASS |
| `node-buffer-view-and-bounds` | `09-nodejs-backend/reference/library-guides/05-buffer.md` | `node:24-bookworm-slim` | PASS |
| `python-context-lifecycle` | `10-python-discovery/reference/language-concepts/08-context-managers.md` | `python:3.14-alpine` | PASS |

## 边界

只验证表中的完整程序和精确标准输出：Go 的 continue、switch 与循环停止边界；Node Buffer 的共享视图、复制和长度校验；Python ExitStack 的反序清理及异常传播。不覆盖整篇文档、其他围栏、网络、数据库、框架、并发、性能或平台行为。JSON 同伴报告保留每个来源和提取代码的 SHA-256、镜像工具链、完整命令、标准输出/错误与退出码。
