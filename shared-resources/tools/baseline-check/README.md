# baseline-check 基线版本漂移检查

解析全仓各模块 README「技术基线」区块，批量比对 registry 最新版本，输出漂移报告。配套季度"基线对齐 ritual"使用（与 code-block-verify 管线复跑同为时效维护步骤）。

## 用法

```bash
python3 baseline_check.py [--json OUT.json]
```

- 报告打印 stdout，Markdown 副本写 `/tmp/baseline-check-<ISO日期>.md`
- 建议设置 `GITHUB_TOKEN` 环境变量：GitHub API 匿名限额 60 次/小时，带 token 提高到 5000 次/小时
- 依赖：python3（标准库）+ go/npm 在 PATH（可选，用于 go proxy / npm registry 查询）

## 解析策略

1. 提取每个模块 README `## 技术基线` 区块的表格行（名称 + 版本 token + 行内来源 URL）
2. 包身份解析优先用行内 URL：`pkg.go.dev` → go proxy、`github.com/*/releases` → GitHub API、`npmjs.com/package` → `npm view`、`pypi.org` → PyPI JSON API、`crates.io` → crates API、`go.dev/dl` → 官方版本 JSON
3. 无 URL 行按名称回退表（脚本内 `FALLBACK`，含 Google Maven / 平台人工项）
4. 状态判定（pinned 与 latest 前缀比对）：
   - `OK` 一致
   - `DRIFT_MAJOR` 主版本落后 —— 需评估是否升级基线并核对破坏性变更
   - `DRIFT_MINOR` 次版本落后 —— 常规基线刷新
   - `UNKNOWN` 查询失败（网络/限额），重跑即可
   - `NOTE` 非版本行或无通用 registry 的平台工具链（Xcode/Android Studio/targetSdk 等，人工核实）

## 局限（如实声明）

- 一行混写两个工具（如"Maven / Gradle"）只取首个版本号比对，Gradle 需人工看
- Java/GraalVM/KSP 版本号格式特殊（LTS 策略 / 版本跟随 JDK / `<kotlin>-<ksp>` 拼接），固定转人工
- GitHub release tag 语义依赖上游规范（已兼容 `swift-6.4.0-RELEASE`/`php-8.5.10`/`jdk-*` 等前缀）
- Google Maven 过滤 `-alpha/-beta/-rc/-dev` 预发布取最新稳定版

## 2026-09-16 首跑结论（10 模块 46 行基线）

漂移 5 处：**02-nextjs TypeScript 5.x → 实际 7.0（主版本级）**、01-go Go 1.25 → 1.27.1（官方支持窗口外）、04-rn React 19.2 → 19.3、05-kotlin Compose BOM 2026.08 → 2026.09、06-swift Swift 6.3 → 6.4.0（待 swift.org Linux 工具链确认）。其余 23 行 OK、10 行 NOTE（人工）、8 行当时限额未查完（第 2 轮已证 Spring 全家桶 7.x/Hibernate 7.4/JUnit 6 均为最新）。漂移处置不在本工具范围，由基线对齐 ritual 决策。

**2026-09-16 漂移处置结果**：TS 7.0.2（npm/GitHub Releases 实核，Go 原生编译器 GA）与 Go 1.27.1（go.dev/dl 实核）已升级基线并同步散文引用；Compose BOM 2026.09.00（Google Maven 实核）、Swift 6.4.0（swift.org API 实核，Linux 工具链可用）已升级基线，模块正文注明"内容基于 6.3 编写仍成立"；04-rn React 判定为**依赖锁版本**（随 Expo SDK 57/RN 0.86 锁 19.2.3），不改版本、加注解待 SDK 58 一并刷新。
