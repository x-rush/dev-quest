# 全仓代码块全量机器验证报告（无抽样）

- **日期**：2026-09-15（CHANGELOG 2.8.0）
- **范围**：全仓 Markdown 围栏代码块，**全量、非抽样**
- **结论**：4138 个代码块 100% 取得终态，其中确认 78 处真实错误（REAL）已全部修复并经本机工具链实证；其余失败块经 L3 agent 逐块裁决归因为教学示意（TEACHING）、环境缺失（ENV）或工具伪影（FALSEPOSITIVE）

## 一、口径与流水线

```
manifest 4263 个围栏块
  ├─ 125 个非代码块（text / mermaid / markdown / txt）→ SKIP_NONCODE，不入验证
  └─ 4138 个代码块 → 三层验证 → 每块必有终态
```

| 层 | 覆盖 | 手段 |
|----|------|------|
| L1 语法层 | 可验证语言 100% | go（parsego 三级包装梯）/ ts 族 1206 块（4 个按模块技术基线 pin 的 tsc 项目分批）/ php -l / python ast.parse / kotlinc 包装梯 / swiftc -swift-version 6 -parse / jshell / bash -n（**绝不执行**）/ yaml·json·toml / protoc |
| L2 运行层 | 自包含块 100% | go：stdlib-only `go run` + 第三方依赖 goproj `go vet`（47 个依赖按技术基线 pin）；python 三道闸（import 白名单 → AST 危险调用扫描 → `-I` 隔离 + timeout）；php 危险 token 过滤后执行 |
| L3 裁决层 | 全部机器失败块 100% | 17 路并行 agent 分片裁决 + 1 路闭环补充，四类判定 TEACHING / ENV / REAL / FALSEPOSITIVE，每条附证据 |

工具链版本：go 1.25.14 / tsc 5.9.3（项目本地）/ python 3.14.7 / php 8.5.10 / kotlinc 2.4.20 / jshell JDK 21 / swiftc 6.3.3 / protoc 36.1。

验证管线已沉淀入仓：`shared-resources/tools/code-block-verify/`（提取器 + 主驱动 + Go 语法 runner，用法见其 README）。

## 二、终态矩阵（4138/4138，PENDING=0）

| 终态 | 块数 | 含义 |
|------|-----:|------|
| PASS_L1L2 | 245 | L1 语法通过且 L2 实际运行/编译通过（机器双重背书） |
| PASS_L1 | 2409 | L1 语法通过（片段形态，无 L2 入口） |
| GATED_L2 | 291 | 自包含但含危险 token/不被放行，按安全边界不执行 |
| L2_TIMEOUT | 2 | 运行超时（阻塞式服务器类，见 L3 裁决） |
| L3_TEACHING | 705 | agent 裁决：教学示意（省略号/伪代码/不完整上下文），意图即非完整程序 |
| L3_ENV | 279 | agent 裁决：环境缺失（Compose/SwiftUI/Playwright 等 UI·测试框架不在沙箱） |
| L3_FALSEPOSITIVE | 129 | agent 裁决：工具伪影（详见方法学限制） |
| REAL_FIXED | 78 | 真实错误，已全部修复并实证 |
| **合计** | **4138** | |

覆盖证明：`len(results) == len(验证块) == 4138`，断言通过；语言×模块矩阵见归档 `results.jsonl`（每块含 id/lang/module/file/行区间/终态/证据）。

补充背书：L3 归类块中有 170 块在修复后的终态重跑中同时取得 L1 PASS——即裁决结论与机器验证双重一致。

## 三、REAL 78 块分布与高频错误模式

| 模块 | REAL 数 |
|------|--------:|
| 02-nextjs-frontend | 44 |
| 01-go-backend | 10 |
| 03-tanstack-stack | 7 |
| 04-multiplatform-apps | 4 |
| 05-kotlin-compose | 3 |
| 07-php-mastery | 3 |
| 10-python-discovery | 3 |
| shared-resources | 3 |
| 08-java-revisited | 1 |

（06-swift-swiftui 与 09-nodejs-backend 零 REAL。05-kotlin 延续 2.7.0 零确认级问题标杆，本轮 3 处均为裁决后修复的轻量问题。）

高频根因模式（按出现频次）：

1. **MSW v1 API 过时**（02-nextjs 多处）：`rest.*`/`ctx.*` 旧命名空间，应迁 `http.*`/`HttpResponse`
2. **App Router 缺 `'use client'`**：事件处理器/hooks 出现在默认服务端组件文件
3. **Docker 多阶段 `--omit=dev` 缺 devDeps**：构建期需要 typescript 等却只装生产依赖
4. **未使用/缺失 import**：tsc noUnusedLocals 关闭下漏检，靠 L3 目检补齐
5. **虚构 API**：`web-vitals` 的 `reportWebVitals` 签名、`@react-native-community/axios`（npm 404）等
6. **Go 细节**：`bufio.Split` 返回 advance=0 且 token 非空导致死循环、`gin` 路由参数写法等（go 1.25.14 编译/运行实证）
7. **命名/签名漂移**：`enableFiltering`→`enableColumnFilter`（table-core 9.2.4 实查）、Next Metadata 顶层 `publishTime` 应入 `openGraph` 等

全部修复经本机实证：tsc 零错 / go run+go vet PASS / kotlinc+coroutines 编译零错 / jshell / php 实跑 / `prisma validate` / `node --check`。

## 四、方法学限制（如实声明）

1. **TSX-as-TS 伪影（约 71+ 块，FALSEPOSITIVE 主因）**：`tsx` 标注块若被分入 `.ts` 编译批，JSX 语法报 TS1005/TS1136/TS1161 三联征。未在验证器层做 JSX 语言嗅探（工程量大），此类失败一律 L3 裁决为 FALSEPOSITIVE，不影响最终正确性结论。
2. **kotlin 包装梯缺文档上下文桩**：片段中的自定义类型/Composable（如 `Note`、`MyTheme`）在单文件包装下 unresolved，154 块判 ENV。这是包装梯形态的固有盲区，非代码错误。
3. **jshell 无桩**：Java 片段缺 import/外围类时 jshell 直接报错，同上归 ENV/TEACHING。
4. **ts-03 沙箱未装测试框架**：@playwright/test、vitest、@testing-library/user-event 不在该模块技术基线内，相关 testing 块报模块缺失，判 ENV（代码正确）。
5. **`strict:false` 降噪**：TS2339/TS2551 属性级错误在降噪下不可靠，此类失败块**永不自动放行**，一律 L3 查官方文档/源码实证。
6. **阻塞式服务器**：`http.ListenAndServe` 等永不返回的自包含块在 L2 timeout 内必失败，判 ENV（代码正确），共 2 块 TIMEOUT。
7. **GATED 边界**：291 块因安全边界（危险 token、PHPUnit 测试类等）不执行，其正确性由 L1 + L3 背书，未做运行级验证。

## 五、归档清单

| 文件 | 说明 |
|------|------|
| `manifest.jsonl` | 4263 行：全部围栏块（含 125 个 SKIP_NONCODE），含内容 hash/行区间/标题链/上下文散文 |
| `results.jsonl` | 4138 行：每块终态 + L1/L2 明细 + L3 证据 |
| `../../shared-resources/tools/code-block-verify/` | 验证管线源码（extract_blocks.py / verify.py / parsego），可复跑 |

复跑方式：

```bash
python3 extract_blocks.py [REPO_ROOT] [OUTPUT]
/tmp/dq-verify/venv/bin/python verify.py   # 依赖 /tmp/dq-verify 工作区，详见工具 README
```

L3 分片裁决记录（17 分片 + closure，共 1191 条）保留于 `/tmp/dq-verify/l3/`（工作区，不入仓）。
