# KSP 代码生成配置指南

> KSP（Kotlin Symbol Processing）的字典式速查：与 kapt 的关系、版本与插件声明、ksp(...) 依赖写法、Room/Hilt 等库的接入、常见配置错误

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#KSP` `#代码生成` `#Room` `#构建配置` |
| **更新日期** | `2026年9月` |

---

## 1. 定义：KSP 是什么、与 kapt 什么关系

**KSP**（Kotlin Symbol Processing）是 Kotlin 编译期的注解处理框架：编译时扫描 `@Entity`、`@Database` 这类注解，生成实现代码（Room 的 DAO 实现等），**不进运行时**。

| 维度 | KSP（首选） | kapt（维护模式） |
|------|-------------|------------------|
| 原理 | 直接解析 Kotlin 源码（KSP2 基于 Analysis API） | 先生成 Java stub，再走 javac 注解处理 |
| 速度 | 官方宣称最高约 2 倍于 kapt | 两轮编译，慢 |
| Kotlin 2.x 支持 | 一等公民 | 仍可用但不再演进 |
| 版本号 | **独立版本号**（如 2.3.x），与 Kotlin 版本解耦 | 随 Kotlin 版本走 |

结论：**新项目一律 KSP；旧项目从 kapt 迁移时把 kapt 依赖删干净**，不能双处理器并存。

## 2. 版本与插件声明（libs.versions.toml）

```toml
# gradle/libs.versions.toml（版本以官方最新稳定版为准，基线见模块 README）
[versions]
kotlin = "2.4.20"
ksp = "2.3.11"            # ⭐ KSP 独立版本号，升级 Kotlin 后无需强改

[plugins]
ksp = { id = "com.google.devtools.ksp", version.ref = "ksp" }
```

```kotlin
// 根 build.gradle.kts：声明不应用
plugins {
    alias(libs.plugins.ksp) apply false
}

// 模块 build.gradle.kts：应用
plugins {
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.ksp)          // ⭐ 用到 ksp(...) 的模块必须应用插件
}
```

## 3. 依赖写法：implementation vs ksp(...)

```kotlin
dependencies {
    // Room：运行时走 implementation，编译器走 ksp
    implementation(libs.androidx.room.runtime)
    implementation(libs.androidx.room.ktx)
    ksp(libs.androidx.room.compiler)                 // ⭐ 处理器专用配置

    // 需要传参时用 ksp 扩展块
    ksp {
        // arg("room.schemaLocation", "$projectDir/schemas")
        // Room 更推荐官方 Gradle 插件的 DSL（见下）
    }
}

// Room 推荐写法：androidx.room 官方插件管理 schema 导出
plugins { alias(libs.plugins.room) }
room { schemaDirectory("$projectDir/schemas") }
```

| 配置 | 放什么 |
|------|--------|
| `implementation(...)` | 运行时库（room-runtime、room-ktx） |
| `ksp(...)` | 编译期处理器（room-compiler、hilt-compiler） |
| `ksp { arg(key, value) }` | 向处理器传参 |

## 4. 哪些库走 KSP

| 库 | KSP 接入 | 说明 |
|----|----------|------|
| **Room** | `ksp(androidx.room:room-compiler)` | 本模块主力场景，见 [basics/08](../../basics/08-first-project.md) |
| **Hilt / Dagger** | `ksp(hilt-android-compiler)` 等 | Dagger 2.48+ 起支持 KSP |
| **Moshi**（codegen） | `ksp(moshi-kotlin-codegen)` | 手写适配器的替代 |
| **Glide** | `ksp(glide-compiler)` | `@GlideModule` 生成 |
| ⚠️ **Kotlinx Serialization** | **不走 KSP** | 它是 **Kotlin 编译器插件** `org.jetbrains.kotlin.plugin.serialization`，只需在 plugins 里 alias 应用，**不添加任何 ksp/processor 依赖** |

> 常见误区：以为"所有注解库都要 ksp(...)"。**先查该库文档用哪种机制**——Kotlin 编译器插件（serialization）、Gradle 插件（room DSL）、还是 KSP 处理器（Room/Hilt）。混淆三者是配置报错的主因。

## 5. 常见配置错误

### 5.1 KSP 与 Kotlin 版本不匹配
Sync 失败："KSP version is not compatible with the Kotlin version" → 升级 KSP 插件到与当前 Kotlin 兼容的最新稳定版。完整排查见 [故障排除 #11](../quick-references/02-troubleshooting.md)。

### 5.2 处理器写成了 implementation(...)
```kotlin
implementation(libs.androidx.room.compiler)   // ❌ 处理器进了运行时 classpath，编译期不生成代码
ksp(libs.androidx.room.compiler)              // ✅ 注册为 KSP 处理器
```
症状：编译通过，**运行期**才报"没有 DAO 实现"。

### 5.3 模块忘记应用 ksp 插件
依赖写了 `ksp(...)` 但模块 plugins 没有 `alias(libs.plugins.ksp)` → Gradle 报"无法解析 ksp 配置"。

### 5.4 kapt 残留与 ksp 并存
从 kapt 迁移后同时保留 `kapt(room-compiler)` 与 `ksp(room-compiler)` → 重复生成/冲突。迁移时逐模块删净 `kapt(...)` 与 kapt 插件。

### 5.5 Room schema 目录未配置
没配 `room { schemaDirectory(...) }`（或 `arg("room.schemaLocation", ...)`）→ 无 schema 导出，日后无法写迁移测试。

---

## 相关文档

- 📄 **[第一个项目 - Compose + Room 笔记应用](../../basics/08-first-project.md)** - Room + KSP 完整配置实战
- 📄 **[生态集成四件套](../../frameworks/03-ecosystem-integration.md)** - Room/Hilt/Retrofit 组合中的 ksp 用法
- 📄 **[AndroidX 官方库指南](./01-androidx-libraries.md)** - Room 三件套与迁移
- 📄 **[常见错误与故障排除](../quick-references/02-troubleshooting.md)** - KSP 版本不匹配等构建期症状
- 📖 **[KSP 官方文档](https://kotlinlang.org/docs/ksp-overview.html)** - 快速开始与 Gradle 配置细节
