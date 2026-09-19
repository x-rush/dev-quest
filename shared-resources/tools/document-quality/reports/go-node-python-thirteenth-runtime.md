# Go / Node.js / Python 第十三轮正文提取运行验证

Three named complete programs, extracted unchanged from the listed P1 core/standard-library Markdown documents. A passing result covers only these contracts, not an entire page or module.

| Case | Source | Runtime | Result |
| --- | --- | --- | --- |
| `go-generics-named-type` | `01-go-backend/reference/language-concepts/09-generics.md` | `golang:1.27` | PASS |
| `node-exports-resolution` | `09-nodejs-backend/reference/language-concepts/06-esm-module-resolution.md` | `node:24-bookworm-slim` | PASS |
| `python-default-factory` | `10-python-discovery/basics/04-functions-oop.md` | `python:3.14-alpine` | PASS |

## 边界

仅验证表中的完整程序及精确标准输出：Go 命名类型与泛型约束、Node `exports` 的公开边界与相对 ESM 导入、Python 可变默认参数与 dataclass `default_factory`。不覆盖整篇文档、其他围栏、网络、数据库、框架、并发、性能或平台行为。JSON 同伴报告保留来源和提取代码哈希、镜像工具链、完整命令、标准输出/错误与退出码。
