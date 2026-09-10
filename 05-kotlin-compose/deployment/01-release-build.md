# 发布构建 - 签名、混淆与多渠道

> **文档简介**: 配置生产级 Gradle Kotlin DSL 发布流水线：签名密钥管理、R8 混淆与资源收缩、构建类型与渠道变体、AAB 产物输出
>
> **目标读者**: 应用功能完成、准备产出可上架安装包的进阶学习者
>
> **前置知识**: [生产级应用](../projects/04-production-android-app.md)、Gradle Kotlin DSL 基本操作（速查见[一行式速查表](../reference/quick-references/01-kotlin-compose-cheatsheet.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（deployment） |
| **难度** | ⭐⭐ |
| **标签** | `#signing` `#r8` `#product-flavors` `#aab` `#gradle-kotlin-dsl` |
| **更新日期** | `2026年9月` |

---

## 1️⃣ 签名：密钥不进仓库

先生成上传密钥（Play App Signing 模式下，上传密钥由你保管，发布签名由 Google 托管）：

```bash
keytool -genkey -v -keystore upload-keystore.jks \
  -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

密钥与口令放在 `keystore.properties`（已加入 `.gitignore`）：

```properties
storeFile=/home/user/keys/upload-keystore.jks
storePassword=REDACTED
keyAlias=upload
keyPassword=REDACTED
```

`app/build.gradle.kts` 读取并配置签名（**配置入仓、密钥不进仓**）：

```kotlin
import java.util.Properties

val keystoreProps = Properties().apply {
    val f = rootProject.file("keystore.properties")
    if (f.exists()) f.inputStream().use { load(it) }
}

android {
    signingConfigs {
        create("upload") {
            storeFile = keystoreProps["storeFile"]?.let { file(it) }
            storePassword = keystoreProps["storePassword"] as String?
            keyAlias = keystoreProps["keyAlias"] as String?
            keyPassword = keystoreProps["keyPassword"] as String?
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("upload")
            // …混淆配置见下一节
        }
    }
}
```

CI 环境中密钥以 secret 注入（Base64 解码），见 [CI/CD 与可观测性](03-ci-cd-observability.md)。

## 2️⃣ R8 混淆与资源收缩

```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true          // 开启 R8：混淆 + 树摇
            isShrinkResources = true        // 移除未引用资源
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }
}
```

Compose/Room/Hilt 主流库自带 consumer rules，通常**只需为反射框架补规则**。
以 kotlinx-serialization 为例（`proguard-rules.pro`）：

```proguard
# kotlinx-serialization：保留序列化器生成的类与字段名
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keepclassmembers class kotlinx.serialization.json.** { *** Companion; }
-keepclasseswithmembers class ** {
    kotlinx.serialization.KSerializer serializer(...);
}
```

验证方式：混淆后完整跑一遍[端到端测试](../testing/03-integration-e2e-testing.md)，
再真机冒烟——`ClassNotFoundException` 就是缺 keep 规则的信号（速查见[故障排除](../reference/quick-references/02-troubleshooting.md)）。

## 3️⃣ 构建类型与渠道变体

```kotlin
android {
    flavorDimensions += "environment"
    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
            versionNameSuffix = "-dev"
            // 开发渠道：指向测试服务器，日志全开
        }
        create("prod") {
            dimension = "environment"
            // 生产渠道：正式服务器
        }
    }
}
```

常用命令：

```bash
./gradlew bundleProdRelease          # 产出 .aab（Play 上架格式）
./gradlew assembleDevDebug           # 日常开发安装包
./gradlew bundleProdRelease --scan   # 构建耗时分析
```

**为什么是 AAB 不是 APK**：AAB 由 Play 按设备下发拆分（ABI/密度/语言），包体显著更小；
本地真机直装调试用 APK 即可。

## 4️⃣ 版本号策略

```kotlin
android {
    defaultConfig {
        versionCode = 42               // 单调递增，Play 用来判定升级
        versionName = "1.2.0"          // 语义化版本：大改.功能.修复
    }
}
```

- 每次发版 `versionCode +1`，回滚版本也必须更高；
- 版本号演进可脚本化（读 git tag 或属性文件），避免手工漏改；
- debug 构建加 `applicationIdSuffix = ".debug"`，与线上版并存互不干扰。

## 5️⃣ 发布前检查清单

- [ ] `keystore.properties` 与 `*.jks` 均在 `.gitignore`
- [ ] release 混淆构建通过全部[仪器测试](../testing/03-integration-e2e-testing.md)
- [ ] `versionCode` 递增、`versionName` 语义正确
- [ ] `bundleProdRelease` 产物可在真机安装启动
- [ ] 权限清单与实际使用一致（多余权限在审核中扣分，见[安全实践](../advanced-topics/security/01-security-practices.md)）

## 🔗 相关文档

- 📖 概念字典：[AndroidX 官方库指南](../reference/library-guides/01-androidx-libraries.md) ｜ [常见错误与故障排除](../reference/quick-references/02-troubleshooting.md)
- 🚀 后续步骤：[Play Store 上架流程](02-play-store-release.md) ｜ [CI/CD 与可观测性](03-ci-cd-observability.md)
- 🧪 质量前提：[集成与端到端测试](../testing/03-integration-e2e-testing.md)
