# CI/CD 与可观测性任务指南 — Xcode Cloud、MetricKit 与崩溃监控

> **文档简介**: 建立无人值守的构建发布流水线（Xcode Cloud）与线上质量监控（MetricKit 指标采集、崩溃上报），让"发版"变成按钮而不是仪式
>
> **目标读者**: 已上架或即将上架、要把发布与运维自动化的中高级学习者
>
> **前置知识**: [02-app-store-release.md](./02-app-store-release.md)（熟悉 App Store Connect）、[frameworks/04-devtools.md](../frameworks/04-devtools.md)（Xcode 构建体系）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#XcodeCloud` `#CI-CD` `#MetricKit` `#崩溃上报` `#可观测性` |
| **更新日期** | `2026年9月` |

## 🎯 本指南解决什么问题

个人开发者最缺的不是代码能力，而是**发布纪律**：手动打包会漏步骤、线上崩溃没人报、性能劣化没感知。本指南用三件事补齐：Xcode Cloud 自动构建分发 → MetricKit 采集系统级指标 → 崩溃日志自动符号化上报。

## 🛠️ 任务一：Xcode Cloud 流水线

### 1.1 基础工作流

Xcode 内置入口：Report Navigator → Cloud → 创建工作流。推荐的最小流水线：

```text
触发：main 分支有新提交
  → 1. Test（iOS 26 模拟器跑单元测试）      ← 失败即停
  → 2. Archive（Release 构建）
  → 3. Distribute → TestFlight（内部组）
```

### 1.2 版本号自动化（脚本动作）

工作流里添加 Post-build 脚本，把 Build 号绑到 CI 构建次数：

```bash
#!/bin/sh
# ci_scripts/ci_post_xcodebuild.sh — Xcode Cloud 约定脚本目录
# 用 Xcode Cloud 构建号回写 CFBundleVersion，保证每次上传唯一
agvtool new-version -all "$CI_BUILD_NUMBER" || true
```

脚本放在仓库根的 `ci_scripts/ci_post_xcodebuild.sh`，加执行权限（`chmod +x`）。

### 1.3 分支策略与工作流组合

| 分支 | 触发动作 | 目的地 |
|------|---------|--------|
| feature/* | 只跑测试 | 无分发 |
| main | 测试 + Archive | TestFlight 内部组 |
| release/* | 测试 + Archive | TestFlight 外部组 / 提审 |

提审 App Store 用 Xcode Cloud 的 "Submit for Review" 动作，过审发布方式（手动/自动）沿用 App Store Connect 配置。

## 🛠️ 任务二：MetricKit 采集系统级指标

MetricKit 是苹果官方的**系统级遥测**：卡顿（hang）、耗电、磁盘写入、崩溃摘要，每天随系统诊断包送达。

```swift
import MetricKit

final class MetricsSubscriber: NSObject, MXMetricManagerSubscriber {
    static let shared = MetricsSubscriber()

    func start() {
        MXMetricManager.shared.add(self)          // App 启动时订阅
    }

    // 日度/周度性能指标包
    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            if let launch = payload.applicationLaunchMetrics {
                record("启动耗时直方图", launch.histogrammedTimeToFirstDraw)
            }
            if let scroll = payload.applicationScrollHitchTimeRatioMetrics {
                record("滚动卡顿比", scroll.scrollHitchTimeRatio)
            }
        }
        // 把 payload JSON 归档/上报到自己的后端
    }

    // 诊断包：卡顿与崩溃堆栈
    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            for crash in payload.crashDiagnostics ?? [] {
                record("崩溃", crash.callStackTree)   // 关键：堆栈树
            }
            for hang in payload.hangDiagnostics ?? [] {
                record("卡顿超时", hang.callStackTree)
            }
        }
    }

    private func record(_ label: String, _ data: Any) {
        // 最小实现：写日志文件；生产实现：异步上报后端
        print("📊 \(label)")
    }
}
```

**解读要点**：`scrollHitchTimeRatio` 低于 5ms/s 属良好；启动看 P90 分位而不是均值。指标劣化的代码级排查见 [01-rendering-performance.md](../advanced-topics/performance/01-rendering-performance.md)。

## 🛠️ 任务三：崩溃上报与符号化

### 路线选择

| 路线 | 成本 | 适合 |
|------|------|------|
| TestFlight / App Store Connect 崩溃面板 | 零接入 | 个人开发者起步 ✅ |
| MetricKit + 自建后端 | 需后端 | 想要原始数据 |
| 第三方 SDK（如 Firebase Crashlytics） | 接入 SDK | 团队协作、聚合告警 |

### 接入 Crashlytics 的最小步骤

```text
1. Firebase Console 创建项目，下载 GoogleService-Info.plist
2. SPM 添加 Firebase iOS SDK，勾选 FirebaseCrashlytics
3. App 启动时 FirebaseApp.configure()
4. dSYM 上传配置：Debug Information Format → DWARF with dSYM File（Release）
5. 构建脚本中调用 Crashlytics 的 upload-symbols 完成自动上传
```

**符号化是崩溃可读的前提**：保留每次 Release 的 dSYM（Xcode Cloud 自动归档，可从构建详情页下载），否则堆栈只有内存地址。

## 🛠️ 任务四：建立"指标 → 行动"闭环

```text
每周一次例行检查：
1. Xcode Cloud 构建成功率 < 90%？ → 修复 flaky 测试
2. 崩溃 Top 3 变化？ → 对齐到版本号，高崩溃版本优先热修
3. 卡顿比 / 启动 P90 劣化 > 10%？ → 建 perf 工单，Instruments 复现
4. TestFlight 反馈关键词归类 → 转化为下个迭代的需求
```

## ✅ 最佳实践

- ✅ 流水线从第一天就跑测试，**没有测试支撑的 CI 只是打包机器**
- ✅ dSYM 与版本一一归档，崩溃符号化不过夜
- ✅ 指标看趋势不看单点，周同比比日波动有意义

## ❌ 避免陷阱

- ❌ 把密钥、签名文件提交进仓库——用 Xcode Cloud 的环境变量与托管签名
- ❌ 上报逻辑同步执行阻塞主线程——遥测必须异步、可丢失
- ❌ 只接 SDK 不看面板——告警阈值不设，等于没接

## ❓ 常见问题

**Q1: Xcode Cloud 免费额度够用吗？** 个人开发者账号含每月固定构建时长，个人项目通常足够，超额再考虑计费或迁移 GitHub Actions（配合 `xcodebuild` 命令行）。

**Q2: MetricKit 数据延迟多久？** 性能指标按日送达，诊断包可能滞后 1-2 天，不能当实时告警用。

**Q3: 测试在 CI 上偶发失败？** 先隔离出复现用例，常见为时序问题——检查 `waitForExistence` 使用是否彻底（见 [02-ui-testing.md](../testing/02-ui-testing.md)）。

## 🎯 练习

- [ ] 为仓库建 main → TestFlight 的 Xcode Cloud 工作流，含测试关卡
- [ ] 接入 MetricsSubscriber，连续一周收集启动耗时并画出 P50/P90 趋势
- [ ] 制造一个故意崩溃，验证 TestFlight 崩溃面板与 dSYM 符号化链路

## 相关文档

- 📄 [02-app-store-release.md](./02-app-store-release.md) — 上游：App Store 上架流程
- 📄 [04-devtools.md](../frameworks/04-devtools.md) — 本地侧工具链（Instruments/调试器）
- 📄 [01-rendering-performance.md](../advanced-topics/performance/01-rendering-performance.md) — 指标劣化后的优化方法论
- 📄 [03-integration-testing.md](../testing/03-integration-testing.md) — 让 CI 测试关卡更扎实的集成测试
