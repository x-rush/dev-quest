# CI/CD 与可观测性 - GitHub Actions + Firebase Crashlytics

> **文档简介**: 用 GitHub Actions 自动化 Android 构建测试与签名发布，接入 Firebase Crashlytics 实现线上崩溃与 ANR 的主动监控
>
> **目标读者**: 已会手动出包（见[发布构建](01-release-build.md)）、想把"人肉发布"变成流水线的进阶学习者
>
> **前置知识**: [发布构建](01-release-build.md)、[Play Store 上架流程](02-play-store-release.md)、[集成与端到端测试](../testing/03-integration-e2e-testing.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（deployment） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#github-actions` `#crashlytics` `#vitals` `#release-automation` |
| **更新日期** | `2026年9月` |

</details>

---

## 1️⃣ GitHub Actions：PR 门禁 + 签名构建

`.github/workflows/android.yml`：

```yaml
name: Android CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - uses: gradle/actions/setup-gradle@v4   # 缓存 Gradle，加速后续构建

      - name: 单元测试 + Lint（PR 门禁）
        run: ./gradlew testDebugUnitTest lintDebug

      - name: 还原签名密钥（push 才执行）
        if: github.event_name == 'push'
        env:
          KEYSTORE_BASE64: ${{ secrets.UPLOAD_KEYSTORE_BASE64 }}
          KEYSTORE_PROPS: ${{ secrets.KEYSTORE_PROPERTIES }}
        run: |
          echo "$KEYSTORE_BASE64" | base64 -d > upload-keystore.jks
          echo "$KEYSTORE_PROPS" > keystore.properties   # 与本地同名，构建脚本零改动

      - name: 签名 AAB
        if: github.event_name == 'push'
        run: ./gradlew bundleProdRelease

      - uses: actions/upload-artifact@v4
        if: github.event_name == 'push'
        with:
          name: release-aab
          path: app/build/outputs/bundle/prodRelease/*.aab
```

要点：

- 密钥走 **Actions Secrets**（Base64 编码的 jks + properties 文本），与 [发布构建](01-release-build.md)
  的本地文件名对齐后，脚本无需分支判断；
- PR 上只跑 `test + lint`，push 才出签名包——门禁要快，发布要稳；
- 仪器测试（`connectedDebugAndroidTest`）需要模拟器环境：可用 `reactivecircus/android-emulator-runner`
  起 KVM 模拟器，或接入云真机服务后作为 push 级门禁；
- 进阶：`r0adkll/upload-google-play` 等 Action 或 Fastlane 可直接把 AAB 推上内部/封闭轨道，
  与 [Play 分轨发布](02-play-store-release.md) 打通全自动。

## 2️⃣ Crashlytics：崩溃主动上报

**接入**（Firebase Console 创建项目后）：

```kotlin
// 根 build.gradle.kts：插件
plugins {
    id("com.google.gms.google-services") version "4.4.x" apply false
    id("com.google.firebase.crashlytics") version "3.0.x" apply false
}

// app/build.gradle.kts
plugins {
    id("com.google.gms.google-services")
    id("com.google.firebase.crashlytics")
}
android {
    buildTypes {
        release {
            configure<CrashlyticsExtension> {
                mappingFileUploadEnabled = true   // 上传混淆映射，堆栈自动还原
            }
        }
    }
}
dependencies {
    implementation(platform("com.google.firebase:firebase-bom:33.x.x"))
    implementation("com.google.firebase:firebase-crashlytics")
    implementation("com.google.firebase:firebase-analytics")
}
```

`google-services.json` 放 app/ 目录——它只含公开标识符，可以入仓；CI 缺它时生成占位文件即可编译。

**使用层次**：

```kotlin
// ① 自动捕获：未处理崩溃默认上报，映射还原
// ② 已捕获异常：记录但不中断
try { riskyOperation() } catch (e: Exception) {
    FirebaseCrashlytics.getInstance().recordException(e)
}

// ③ 自定义上下文：定位"哪个版本/哪条路径"出的问题
FirebaseCrashlytics.getInstance().apply {
    setCustomKey("feature", "weather")           // 与功能模块对齐
    setCustomKey("api_endpoint", "/v1/forecast")
    log("刷新失败，进入重试")
}
```

## 3️⃣ Release Health：以指标驱动灰度决策

Crashlytics Dashboard 关注三个数：

| 指标 | 含义 | 健康线 |
|------|------|--------|
| 无崩溃用户率 | crash-free users | > 99.5% |
| 无崩溃会话率 | crash-free sessions | > 99.7% |
| ANR 率 | 主线程阻塞（Vitals 同步可见） | < 0.47%（Play 政策线） |

结合 [Play 灰度](02-play-store-release.md)：灰度 10% 观察 24-48h，
无崩溃率异常再放量；异常则**暂停 rollout**（已升级用户不受影响）并发布修复版本。

## 4️⃣ 可观测性分层

- **崩溃层**：Crashlytics（本文）——非致命异常也记录，别只等 crash
- **性能层**：Firebase Performance 监控启动耗时/网络请求（与 [启动优化](../advanced-topics/performance/02-startup-memory.md) 互相验证）
- **行为层**：Analytics 关键事件（首启/核心转化），驱动产品决策
- **系统层**：Play Console Vitals（ANR、电池、权限拒绝），面向商店政策的官方口径

## 🎨 最佳实践

每次发布将源码提交、构建编号、签名产物和混淆映射关联归档。先制造一个受控异常，验证平台能把堆栈还原到该版本的源代码，再认为崩溃采集已经可用。

日志和自定义字段提供定位线索，但避免用户秘密与无界高基数字段。非致命错误也值得观察，其严重性由对业务的影响判断，不能一概视为即将崩溃。流水线限制签名凭据访问；灰度发现问题时按预先定义的暂停和修复方案执行。

## 🔗 相关文档

- 📖 前置步骤：[发布构建](01-release-build.md) ｜ [Play Store 上架流程](02-play-store-release.md)
- 🧪 质量门禁：[集成与端到端测试](../testing/03-integration-e2e-testing.md)
- 🚀 深度优化：[启动与内存优化](../advanced-topics/performance/02-startup-memory.md) ｜ [生产级 Android 应用](../projects/04-production-android-app.md)


<!-- acceptance-exercise -->
## 练习与验收：建立提交、构建与崩溃的对应关系

在测试分支先制造一个失败单元测试，预期流水线拦截发布。恢复后构建测试发行包，用受控方式触发合成错误，确认错误平台能关联版本与反混淆映射。验收包含新进程启动、一次核心操作和敏感日志检查；上传 mapping 文件不代表它与用户实际安装的包一致，必须按构建标识匹配。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
