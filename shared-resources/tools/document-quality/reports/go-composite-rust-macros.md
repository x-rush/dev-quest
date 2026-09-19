# Go 复合类型与 Rust 宏的正文验证

2026-09-19，Linux x86_64；Go 1.27.1、Rust 1.98.1 / edition 2024。直接抽取两篇正文的命名围栏，不补 import、main 或依赖，不拼接未标记片段。结果 **10 / 10 通过**：8 个程序运行符合正文输出、2 个反例按预期编译失败。

| 来源 | 案例 | 覆盖的契约 |
|---|---|---|
| [Go 复合类型](../../../../01-go-backend/basics/04-composite-types.md) | `go-composite-alias` | append 复用存储、限制容量后的分离、struct 内部切片浅拷贝 |
| 同上 | `go-composite-empty` | nil 与空切片、copy 长度与重叠、nil map 读取、comma-ok、map 共享与键排序 |
| 同上 | `go-composite-panic` | nil map 写入、接口中不可比较值、map 动态键的三种 panic |
| 同上 | `go-composite-remove` | 新列表删除、原列表独立、负索引与越界、单元素与 nil 输入 |
| [Rust 宏系统](../../../../11-rust-cross-platform/reference/language-concepts/05-macros.md) | `rust-macro-max` | 生成 item、单元素与尾逗号、输入求值次数 |
| 同上 | `rust-macro-hygiene`、`rust-macro-derive` | 递归求和、局部变量卫生、内置 derive 生成的 trait 行为 |
| 同上 | `rust-macro-edition` | edition 2024 expr 与 expr_2021 的首臂匹配、pat 与 pat_param |
| 同上 | `rust-macro-move`、`rust-macro-cfg` | E0382：宏展开不豁免移动；E0425：cfg! 不删除未选分支 |

## 重现

[验证器](../verify_go_composite_rust_macros.py)要求恰好 4 个 Go、6 个 Rust 命名案例。Go 使用 `go build -race`；Rust 使用 `rustc --edition 2024 --error-format=json`。运行案例要求退出 0、stderr 为空、stdout 与正文紧随案例的 text 围栏逐字一致；编译反例要求非零退出且结构化诊断包含指定错误码。

已有本地工具镜像时，在仓库根目录执行：

```powershell
docker run --rm --network none --read-only `
  --tmpfs /tmp:rw,exec,nosuid,size=1536m `
  --cap-drop ALL --pids-limit 256 --memory 2g --cpus 2 `
  -e GOCACHE=/tmp/go-cache -e HOME=/tmp `
  -v "${PWD}:/source:ro" `
  -v "${PWD}/shared-resources/tools/document-quality/reports:/reports:rw" `
  dev-quest-validation:local `
  python3 /source/shared-resources/tools/document-quality/verify_go_composite_rust_macros.py `
  --report /reports/go-composite-rust-macros.json
```

该镜像是已有本地环境，不是公开镜像发布物。其他机器可准备 Linux、Python 3.10+、Go 1.27.1、Rust 1.98.1 和 race 构建所需 C 编译器，在隔离环境运行同一脚本。程序仅使用标准库，不下载第三方包。

[原始 JSON 证据](go-composite-rust-macros.json)记录来源路径/行号、规范化正文 SHA-256、代码 SHA-256、完整命令、工具链、构建诊断与运行输出。正文修改后应重新执行以更新哈希，不能沿用旧结果证明新内容。

## 本轮修正

- Go：切片、map、指针字段的外层复制不等于深拷贝；append 无论扩容与否都不更新别的切片变量长度；copy 看长度而非容量；map 顺序不保证每次不同；指针大小依平台；同类型 struct 字段换序不一定触发编译错误。
- Go：补足比较的静态/动态边界，修复原组合示例缺失 package 与 import，增加可独立运行的删除练习。
- Rust：匹配器表补 `expr_2021` 与 `pat_param`，修正 stmt 尾分号、重复分隔符、follow-set 与 local ambiguity 混淆。
- Rust：修正“递归终止臂必须先写”“递归没有明确限制”“ident 捕获关键字便可任意使用”等解释；区分内置 derive 展示与第三方过程宏实现测试；以实际程序证明输入求值次数、edition 首臂选择与 cfg! 分支检查。

## 边界

只对表中命名案例作运行结论，正文其他短片段、过程宏实现、跨 crate 导出、递归深度极限及练习变体未纳入本脚本。Go panic 案例只确认发生 panic，未锁定平台可能变化的消息。Rust 编译成功时允许编译器警告，原始记录保留这些诊断；运行 stderr 仍必须为空。race 通过不证明所有并发调度，本文程序也没有宣称做过并发 map 集成测试。未进行性能或内存分配基准。

语义复核依据：[Go 语言规范](https://go.dev/ref/spec)、[Rust 声明宏规则](https://doc.rust-lang.org/reference/macros-by-example.html)。实际版本和行为证据以本报告 JSON 中的命令结果为准。
