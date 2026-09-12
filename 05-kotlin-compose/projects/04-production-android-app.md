# 精通项目 - 生产级 Android 应用

> **文档简介**: 以发布一个真实应用为终点的集成指南：多模块架构、错误体系、离线优先、发布加固、可观测性，把前面所有项目经验收敛为工程能力
>
> **目标读者**: 已完成三个递进项目、准备把应用推向真实用户的进阶学习者
>
> **前置知识**: [新闻阅读器](03-news-reader.md)、[应用架构](../advanced-topics/architecture/01-app-architecture.md)，建议同步阅读 testing/ 与 deployment/ 全部文档

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（projects） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#multi-module` `#error-handling` `#offline-first` `#release` `#observability` |
| **更新日期** | `2026年9月` |

---

## 🎯 "生产级"的定义

一个应用达到生产级，意味着以下六件事全部成立：

1. **架构可演进**：分层清晰、依赖单向，新功能不改旧代码
2. **失败是常态**：网络/存储/权限失败都有明确 UI 与恢复路径
3. **离线可用**：缓存优先，弱网体验不崩塌
4. **质量可度量**：核心逻辑有测试拦截（[单元测试](../testing/01-unit-testing.md)）
5. **发布可重复**：签名/混淆/渠道全部脚本化（[发布构建](../deployment/01-release-build.md)）
6. **线上可观测**：崩溃与 ANR 主动上报（[CI/CD 与可观测性](../deployment/03-ci-cd-observability.md)）

## 1️⃣ 多模块结构

```
app/                    # 壳工程：导航 + Application + 主题
core/
├── network/            # Retrofit/序列化，无业务知识
├── database/           # Room，无业务知识
├── designsystem/       # 主题 + 基础组件（全部无状态）
└── common/             # Result 封装、调度器接口
feature/
├── home/               # 每个 feature 自带 ViewModel + Compose 界面 + 依赖接口
└── detail/
```

规则：**feature 依赖 core 的抽象，绝不横向依赖 feature**；app 只做组装。
一个人起步时可先做"包分层"（packages，结构同上），收益（编译隔离、边界清晰）到位后再拆 Gradle 模块。

## 2️⃣ 错误体系：Result + 领域异常

```kotlin
// 统一的领域错误：UI 只认识这三类（继承 Exception，才能 throw / 放入 Result.failure）
sealed interface AppError {
    data class Network(override val cause: Throwable) : AppError, Exception(cause)
    data class Storage(override val cause: Throwable) : AppError, Exception(cause)
    data class Unexpected(override val cause: Throwable) : AppError, Exception(cause)
}

// Repository 边界处统一转译，向上只暴露 Result
// 注意：取消放行不能写进 recoverCatching 的 transform——它内部用 runCatching 包裹 lambda，
// 里面的 throw 会被捕获为 Result.failure 而不是传播；必须先取 exceptionOrNull 检查放行
suspend fun <T> runCatchingApp(block: suspend () -> T): Result<T> {
    val result = runCatching { block() }
    val e = result.exceptionOrNull() ?: return result
    // runCatching 会把取消也捕获为 failure——先放行 CancellationException，协程才能正常取消
    if (e is kotlinx.coroutines.CancellationException) throw e
    return when (e) {
        is IOException     -> Result.failure(AppError.Network(e))
        is SQLiteException -> Result.failure(AppError.Storage(e))
        else               -> Result.failure(AppError.Unexpected(e))
    }
}

// ViewModel：错误 → UiState 的单一出口
data class FeedUiState(
    val items: List<Article> = emptyList(),
    val banner: AppError? = null,        // 非阻断错误横幅（缓存内容仍展示）
)

fun refresh() = viewModelScope.launch {
    runCatchingApp { repository.refresh() }
        .onFailure { e -> _uiState.update { it.copy(banner = e as? AppError) } }
        .onSuccess { _uiState.update { it.copy(banner = null) } }
}
```

要点：**区分"阻断错误"（整屏错误态）与"非阻断错误"（横幅 + 旧数据）**，这是离线优先体验的关键。

## 3️⃣ 离线优先

- Room 为唯一事实来源，UI 只订阅 Room Flow（分页版模式详见[新闻阅读器](03-news-reader.md)）
- 网络失败不抛到 UI 层阻断，降级为横幅提示
- 关键写操作走"本地先提交 + 后台同步"：简单场景用 WorkManager 排队重试
- 缓存要有"新鲜度"概念：`updatedAt` 超过阈值静默刷新，不给用户转圈

## 4️⃣ 发布就绪

| 检查项 | 文档 |
|--------|------|
| 签名配置入仓（不含密钥） | [发布构建](../deployment/01-release-build.md) |
| R8 混淆 + 反射库 keep 规则 | [发布构建](../deployment/01-release-build.md) |
| 版本号策略（versionCode 单调递增） | [发布构建](../deployment/01-release-build.md) |
| Play 分轨发布与灰度 | [Play Store 上架](../deployment/02-play-store-release.md) |

```kotlin
// build.gradle.kts：release 常客
android {
    buildTypes {
        debug { applicationIdSuffix = ".debug" }   // 与线上包名隔离，可并存安装
        release {
            isMinifyEnabled = true
            isShrinkResources = true
        }
    }
}
```

## 5️⃣ 质量门禁

- **单元测试**：ViewModel 状态机 + Repository，Fake 注入（[单元测试](../testing/01-unit-testing.md)）
- **UI 测试**：核心路径（登录、下单、发帖）各至少 1 条（[Compose UI 测试](../testing/02-ui-testing.md)）
- **CI 门禁**：PR 必须通过 `test + lint` 才可合并（[CI/CD](../deployment/03-ci-cd-observability.md)）
- **性能预算**：冷启动 < 2s、列表滚动无卡顿（[启动与内存](../advanced-topics/performance/02-startup-memory.md)、[重组优化](../advanced-topics/performance/01-recomposition-optimization.md)）
- **安全基线**：密钥不进仓、敏感屏防截屏（[安全实践](../advanced-topics/security/01-security-practices.md)）

## 6️⃣ 上线后

- Crashlytics 自定义 key（版本/功能开关）定位崩溃面
- Android Vitals 关注 ANR 率与启动耗时
- 每个版本记录 CHANGELOG，问题回滚依赖分轨发布

## 🎨 实施路线图

| 阶段 | 产出 | 验收 |
|------|------|------|
| 1. 骨架 | 多模块 + DI + 主题 | 新起一个 feature 不超过 30 分钟 |
| 2. 核心 | 首个 feature 全链路 | [架构原则](../advanced-topics/architecture/01-app-architecture.md) 全部满足 |
| 3. 质量 | 测试金字塔 + CI | 合并前测试全绿 |
| 4. 发布 | 签名 AAB + 分轨 | 灰度 10% 崩溃率无异常 |
| 5. 运营 | Crashlytics + Vitals | 崩溃 24h 内可定位 |

## 🔗 相关文档

- 📖 深度解释：[应用架构与 UDF](../advanced-topics/architecture/01-app-architecture.md) ｜ [安全实践](../advanced-topics/security/01-security-practices.md)
- 🧪 测试：[单元测试](../testing/01-unit-testing.md) ｜ [UI 测试](../testing/02-ui-testing.md) ｜ [集成与端到端](../testing/03-integration-e2e-testing.md)
- 🚀 发布：[发布构建](../deployment/01-release-build.md) ｜ [Play Store 上架](../deployment/02-play-store-release.md) ｜ [CI/CD 与可观测性](../deployment/03-ci-cd-observability.md)
