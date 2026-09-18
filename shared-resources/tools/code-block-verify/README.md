# 教学知识库的代码与文档验证

验证的目标是让每个代码块都有可解释的状态，不是让每个教学片段独立运行成功。任何 PASS 都只能说明记录的检查通过，不能代替内容审查或真实框架集成测试。

## 日常自动检查

`.github/workflows/verify.yml` 在推送 main 和 PR 时只运行快速文档完整性检查：本地文件链接、GitHub 风格章节锚点、代码围栏闭合。三个步骤独立执行，某一步失败不会跳过其余检查，报告上传到 `document-integrity` artifact。

全仓多语言检查改为 Actions 页面手动触发 `verify`。默认只检查 L1；`execute_examples` 明确选中才执行符合规则的 L2 和 Java JShell。代码检查与文档检查是独立 job。手动检查仍保留真实失败退出码，不使用 continue-on-error 掩盖失败。

手动全量 job 使用 PHP 8.5，并在开始验证前检查主次版本，避免 Ubuntu 24.04 默认 PHP 8.3 误报新语法；通过 [setup-php 的官方项目说明](https://github.com/shivammathur/setup-php#tada-php-support)指定版本。Rust 使用 runner 当前工具链并显式安装 `rustfmt` 组件，然后检查其可执行版本；只有 rustup 代理存在不代表组件可用。组件管理依据 [Rustup 文档](https://rust-lang.github.io/rustup/concepts/components.html)。这些依赖安装只在手动全量 job 执行，日常快速门禁不安装多语言环境。

Python 检查器使用 3.14，与 Python 模块的语法基线一致，避免旧解释器把 t-string、类型参数默认值等新语法判为错误。

周报 `baseline-weekly.yml` 继续报告外链和版本漂移，不代表自动批准技术版本升级。

## 代码块的维护约定

1. **完整可运行示例**：写出文件名、工具版本、依赖安装、命令与预期输出。涉及服务时说明启动和清理方法。
2. **局部片段**：正文明确它接在哪个完整示例中，哪些变量或服务由上文提供。用准确围栏标记语言，JSX 应使用 tsx/jsx。
3. **故意错误的反例**：正文写清“预期失败”、触发原因与应出现的错误，再给正确版本。失败不是可以无理由豁免的依据。
4. **平台或环境依赖**：缺少 Android/iOS SDK、数据库、浏览器或框架依赖时记作未验证。语法通过不能当作框架可运行。
5. **伪代码与终端输出**：明确标注，不把真实代码改成 text 以绕过检查。

新例外必须按具体文件、完整内容哈希、教学目的、预期错误和复核依据记录。当前 `adjudicated-fails.jsonl` 是历史仅含短哈希的名单，缺少这些信息；暂时保持原有兼容性，但报告会显式显示 `legacy_hash_exception`。本次没有批量增补名单，历史名单也不能视作内容质量证明。

## 本地与隔离环境运行

```bash
python shared-resources/tools/code-block-verify/extract_blocks.py .
python shared-resources/tools/code-block-verify/verify.py --strict
python shared-resources/tools/code-block-verify/prefilter.py
```

默认不会运行文章中的 Python/PHP/Go/Rust 程序。旧 Java L1 使用 JShell，实际上会执行代码，所以现在只有显式 `--execute` 才启用，否则记录 NOT_VERIFIED。L2 的导入白名单/危险词过滤不是安全沙箱：必须使用不挂载凭证的临时容器或专用临时 CI runner；本地工作站不要启用。编译器本身仍需要合理的资源和时间限制。

```bash
# 仅限可丢弃的隔离环境
python shared-resources/tools/code-block-verify/verify.py --strict --execute
# 有针对性的诊断，不应被报告成全量验证
python shared-resources/tools/code-block-verify/verify.py --langs python,json --sample 3
```

Go 语法工具仅依赖标准库，无需 go.mod/go.sum：

```bash
mkdir -p /tmp/dq-verify/parsego
go build -o /tmp/dq-verify/parsego/parsego shared-resources/tools/code-block-verify/parsego/main.go
python shared-resources/tools/code-block-verify/test_parsego.py /tmp/dq-verify/parsego/parsego
python -m unittest discover -s shared-resources/tools/code-block-verify -p 'test_verifier.py'
```

`DQ_WORK` 可覆盖默认 `/tmp/dq-verify`。安装在 PATH 的 `tsc` 被直接调用，避免 npx 在验证途中隐式下载。TS 脚手架复制到工作目录，不修改仓库内脚手架。当前脚手架使用 stubs，语义诊断保留在报告中；原有 strict 兼容策略只把 TS1xxx 语法错误作为门禁，不能据此宣称完整 TypeScript 类型检查通过。Kotlin、Swift 缺少工具时保留未验证状态。

TypeScript 批次使用 `--moduleDetection force`，使每个围栏拥有独立作用域；一个示例的 `const c` 不会改变另一个示例中 `c` 的类型。顶层 await 因此按模块片段检查，读者实际运行时仍须使用 ES 模块环境。批次中出现无法归属代码块的编译器配置错误时，未报局部诊断的块也标为 `ERROR_TOOL`，不推断为通过。

## 报告与退出状态

手动 CI 的 `code-verification` artifact 包含：

- `manifest.jsonl` 与索引：全部提取的代码/非代码块、源路径、行号和内容。
- `results.jsonl`：每块 L1/L2 原始状态、完整内容 SHA-256、分类及历史例外标记。
- `commands.jsonl`：命令、工作目录、退出码、完整 stdout/stderr（不截断）。逐条落盘，长任务中断时仍保留已完成的证据。Go/TS 批处理命令通过生成的 block ID 关联；Python AST、JSON/YAML/TOML 等是进程内解析。
- `summary.json`：工具版本、覆盖数量、是否启用执行。
- `report.md`：全部检查项与所有待审诊断，不再只显示前 50 项。
- `run.log`：运行过程。如果摘要不存在，说明本轮没有完成，不能视为成功。

`PASS_CHECKED_SCOPE` 只表示相应范围通过；`NOT_VERIFIED` 表示缺环境/未执行；`NEEDS_REVIEW` 表示错误、超时、工具失败或漏检。GATED 是未运行，不是通过。`prefilter.py` 的教学/环境分类只是排查建议，不是自动裁决。预期失败和片段必须人工核实，不能仅凭“syntax error”或省略号自动放行。

完整报告保留真实 FAIL；`--strict` 沿用历史短哈希兼容规则，但新失败、工具异常和超时会失败退出。编译器非零退出且没有可归属的诊断时标为 ERROR_TOOL，不能把整个批次当 PASS。

## 维护检查器

调整编译器、提取规则或例外规则时，先运行检查器测试，再选定小样本验证，最后全量扫描。不要根据“CI 变绿”反推所有内容正确。报告有错时先修检查器，不为检查器误判篡改教学内容。没有平台环境的剩余项应保留清单和复验命令。

`test_pipeline.py` 面向具备 `python3` 的 Linux 或 Git Bash 环境，每个子进程限时 30 秒；Windows 上不要依赖可能指向 WSL 的同名 `bash` 隐式运行。
