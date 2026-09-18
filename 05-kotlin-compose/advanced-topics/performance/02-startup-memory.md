# 启动与内存优化

> **文档简介**: 剖析 Android 冷启动链路与常见内存泄漏形态：启动阶段做什么/不做什么、Baseline Profile 的收益原理、Compose 应用的泄漏高发点与排查工具
>
> **目标读者**: 应用功能完备、要达到"秒开不泄漏"生产水位的中高级学习者
>
> **前置知识**: [重组优化](01-recomposition-optimization.md)、[生态集成](../../frameworks/03-ecosystem-integration.md)、[CI/CD 与可观测性](../../deployment/03-ci-cd-observability.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 深度解释（advanced-topics） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#cold-startup` `#baseline-profile` `#memory-leak` `#profiling` |
| **更新日期** | `2026年9月` |

</details>

---

## 1️⃣ 冷启动发生了什么

```
进程创建 → Application.onCreate() → 首个 Activity
        → Compose 首帧组合/布局/绘制 → 首帧可见（"Displayed"）
```

用户感知的启动时间止于**首帧可交互**。一切优化都围绕"Displayed 之前少做事"。

**先测量**（工具操作详见[开发工具链](../../frameworks/04-devtools.md)）：

```bash
adb shell am start -W com.example.app/.MainActivity   # TotalTime 概览
adb logcat | grep Displayed                           # 系统口径的启动耗时
```

精确到方法级用 Macrobenchmark（`StartupBenchmarks` 模板），它同时能防回归——
CI 中跑法见 [CI/CD 与可观测性](../../deployment/03-ci-cd-observability.md)。

## 2️⃣ 启动期三大反模式

| 反模式 | 问题 | 对策 |
|--------|------|------|
| `Application.onCreate` 里同步初始化 DI/分析/推送 | 白屏期被拉长 | Hilt 惰性注入：依赖在首次使用时才构造 |
| 首屏组合前预加载全部数据 | 阻塞首帧 | 首帧只取首屏数据，其余延后（Room Flow 天然按需） |
| 启动页主动 `Thread.sleep`/延时跳转 | 纯浪费 | 用 splash screen API（`postSplashScreenTheme`），到点即走 |

验证手段：StrictMode（debug 构建）会直接惩罚主线程磁盘/网络操作：

```kotlin
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder().detectAll().penaltyLog().build()
            )
        }
    }
}
```

## 3️⃣ Baseline Profile：为什么能提速

默认情况下，应用代码要经历解释执行→JIT 热身才快。**Baseline Profile** 在安装/首启时
把"预标注的热路径字节码"提前 AOT 编译，首屏与滚动跳过热身期——

- 冷启动典型收益：约 20-30% 提升（Google 官方数据）
- Compose 应用尤其受益：框架代码 + 你的热路径一起预编译

生成方式：

```kotlin
// :baselineprofile 模块 + macrobenchmark 依赖
plugins { id("androidx.baselineprofile") }
```

```bash
./gradlew :app:generateBaselineProfile    # 真机/模拟器上自动跑典型路径并生成 profile
```

随 AAB 上传后 Play 自动分发。**每次大版本 UI 结构变化后重新生成**，否则热路径过期。

## 4️⃣ Compose 应用的高发内存问题

### 问题 1：remember 持有 Activity/Context

```kotlin
@Composable
fun Banner() {
    // ❌ 长生命周期对象（如单例缓存）持有 Activity context → 整棵 Activity 泄漏
    // Cache.put("banner", LocalContext.current)
}
```

需要 context 做初始化时，只提取所需对象（`LayoutInflater`、`Resources`）或用
`LocalContext.current.applicationContext`。

### 问题 2：离开屏幕后仍在收集 Flow

```kotlin
// ❌ 用不受生命周期约束的方式收集：屏幕离开仍在跑
// ✅ UI 层订阅用 lifecycle 感知版本，后台自动停
val state by viewModel.uiState.collectAsStateWithLifecycle()
```

（两种 `collectAsState*` 的差异见 [Compose 状态 API 详解](../../reference/language-concepts/04-compose-state-api.md)。）

### 问题 3：DisposableEffect 忘记注销

```kotlin
DisposableEffect(lifecycleOwner) {
    val observer = LifecycleEventObserver { _, _ -> /* ... */ }
    lifecycleOwner.lifecycle.addObserver(observer)
    onDispose {
        lifecycleOwner.lifecycle.removeObserver(observer)   // 忘了这行 = 监听器泄漏
    }
}
```

### 问题 4：图片全尺寸加载

列表大图一律走 Coil/Glide：按组件尺寸请求、内存缓存自动管理、生命周期感知取消——
自写 BitmapFactory + remember 是泄漏与 OOM 双料来源。

## 5️⃣ 排查工具链

| 工具 | 用途 |
|------|------|
| LeakCanary（debug 依赖） | 泄漏自动捕获 + 引用链报告，零成本接入 |
| Android Studio Memory Profiler | 堆快照对比：反复进出页面看 Activity/Bitmap 是否累积 |
| StrictMode | 违规操作实时日志 |
| Macrobenchmark + Perfetto | 启动/滚动的系统级追踪，防回归基线 |

排查节奏：**LeakCanary 常驻日常 → Profiler 复现确认 → 修复后用快照对比验证归零**。

## 🎨 最佳实践

先区分冷启动、温启动和恢复，固定设备与操作后记录启动耗时和内存。把非首屏必要的初始化延后可能改善首屏，但要验证用户进入相关功能时仍有加载与失败反馈。

监听器或资源的生命周期应明确结束；生命周期感知的 UI 收集可以在后台停止收集，但上游任务是否停止还取决于其共享策略。缓存会延长对象持有时间，新增缓存后观察内存是否回落。不要引用没有本项目测量依据的“低端设备慢 5–10 倍”。

## 🔗 相关文档

- 📖 概念字典：[Compose 状态 API 详解](../../reference/language-concepts/04-compose-state-api.md) ｜ [协程与 Flow API 全表](../../reference/language-concepts/03-coroutines-flow-api.md)
- 📖 操作指南：[开发工具链](../../frameworks/04-devtools.md) ｜ [CI/CD 与可观测性](../../deployment/03-ci-cd-observability.md)
- 🎓 延伸解释：[重组优化](01-recomposition-optimization.md) ｜ [应用架构](../architecture/01-app-architecture.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
