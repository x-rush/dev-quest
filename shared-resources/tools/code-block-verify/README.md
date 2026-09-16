# code-block-verify 全仓代码块机器验证管线

对全仓 Markdown 围栏代码块做**全量（非抽样）**三层验证：L1 语法层 → L2 运行/编译层 → L3 agent 裁决（由审计流程人工/agent 执行，不在本目录脚本范围内）。

## 组件

| 文件 | 用途 |
|------|------|
| `extract_blocks.py` | 提取器：扫描全仓 `.md` 围栏代码块（手写状态机，支持嵌套围栏/`~` 围栏/未闭合兜底），输出 `manifest.jsonl` + `manifest.jsonl.index.json` |
| `verify.py` | 主驱动：读 manifest，按语言分发 L1/L2 验证，输出 `results.jsonl` |
| `prefilter.py` | L3 预分流：读 results+manifest，产出失败块分类工作清单 `l3_worklist.jsonl`（likely-teaching / likely-env / force-deep / needs-review；TS2339/TS2551 永不自动放行） |
| `parsego/main.go` | Go 语法 runner（`go/parser` 三级包装梯：原样 → 补 `package p` → 包进 `func _s(){}`），编译后供 verify.py 调用 |

> `manifest.jsonl` / `results.jsonl` / `l3_worklist.jsonl` 为运行产物，不入仓（见 `.gitignore`）；2.8.0 全量验证的快照归档于 `refactor-archives/completed/code-block-verification/`。

## 环境依赖

- 本机工具链：go / node+tsc / python3 / php / kotlinc / swiftc（完整路径）/ jshell (JDK 21) / rustc + rustfmt / protoc
- `/tmp/dq-verify/` 下（验证工作区，不入仓）：
  - `parsego/parsego` — 由 `parsego/main.go` 编译（`go build -o parsego .`）
  - `ts-02/ ts-03/ ts-04/ ts-09/` — 四个 tsc 项目，依赖版本按各模块 README 技术基线 pin（02-nextjs / 03-tanstack / 04-rn / 09-nodejs + 其余模块），`tsconfig`：`strict:false + skipLibCheck + jsx:react-jsx + moduleResolution:bundler`，include `src/**`，`stubs.d.ts` 提供 `@/*` 通配
  - `goproj/` — go.mod + 全量第三方依赖（`go get` 按技术基线），供含第三方 import 的自包含块 `go vet` 编译级验证
  - `venv/` — pyyaml（yaml 解析）

## 用法

```bash
# 1. 提取
python3 extract_blocks.py [REPO_ROOT] [OUTPUT_JSONL]

# 2. 编译 parsego（首次）
cd parsego && go build -o /tmp/dq-verify/parsego/parsego .

# 3. 样本试跑 / 全量批跑
/tmp/dq-verify/venv/bin/python verify.py --langs tsx --sample 20
/tmp/dq-verify/venv/bin/python verify.py
```

`--langs` 逗号分隔过滤语言；`--sample N` 每语言抽 N 块（结果写 `results.jsonl.sample`，不污染全量结果）。

## 层级与安全边界

- **L1 语法层**（可验证语言 100%）：go（parsego 包装梯）/ ts 族（tsc 分项目分批）/ php（`php -l`，无 `<?php` 补前缀）/ python（`ast.parse`）/ kotlin（kotlinc 包装梯：import 保留+其余包进 `fun _s(){}`）/ swift（`swiftc -swift-version 6 -parse`，对齐仓库 Swift 6 基线，不做 sema）/ java（jshell stdin，剥 package 行）/ rust（rustfmt 解析校验 + `fn main` 包装梯；纯语法层不 type-check，编译失败演示块不误报）/ bash（**仅 `bash -n`，绝不执行**）/ yaml / json（首行 `//` 注释惯例容忍：纯解析失败时按 jsonc 剥注释重试）/ jsonc（剥注释）/ toml / protobuf（protoc）
- **L2 运行层**（自包含块）：
  - go：`has_package && has_func_main`；stdlib-only `go run`（timeout 15s），第三方 import 走 goproj 子目录 `go vet`
  - python 三道闸：import 白名单 → AST 禁 eval/exec/open 等危险调用与危险模块 → `-I` 隔离 + PYTHONSAFEPATH=1 + timeout 10s + 临时 cwd
  - php：完整脚本（含 `<?php`）且无危险 token（exec/system/unlink/include 等）且非 PHPUnit 测试类才执行
  - rust：有 `fn main` 且 use/attribute 仅引用 std 系与编译器内置（`use`/`#[crate::…]`/`extern crate` 三路探测第三方）→ `rustc --edition 2024` 编译 + 运行（timeout 10s）；编译失败演示块会 FAIL，按文档标注裁决
- **不可执行即 GATED**；无验证器的语言（dockerfile/nginx/blade 等）标 `SKIP_NOTOOL` 交 L3 目检
- TS 方法学限制：`strict:false` 降噪下属性级错误（TS2339/TS2551）不可靠，此类失败块**永不自动放行**，一律 L3 深查

## 终态枚举

`PASS`（L1）/ L2 附加：`PASS` / `TIMEOUT` / `FAIL` / `GATED` / `SKIP_NOTOOL`；L3 裁决终态由审计报告归档（TEACHING / ENV / REAL / FALSEPOSITIVE）。
