# 单元测试 - JUnit + MockK + 协程测试

> **文档简介**: 为 ViewModel 与 Repository 编写快速稳定的 JVM 单元测试：JUnit 骨架、MockK 替身、kotlinx-coroutines-test 驱动协程与 Flow
>
> **目标读者**: 已能写出 ViewModel/Repository、开始关注代码质量的进阶学习者
>
> **前置知识**: [生态集成](../frameworks/03-ecosystem-integration.md)、[协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（testing） |
| **难度** | ⭐⭐ |
| **标签** | `#junit` `#mockk` `#coroutines-test` `#turbine` |
| **更新日期** | `2026年9月` |

</details>

---

## 1️⃣ 依赖与运行环境

```kotlin
dependencies {
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.mockk:mockk:1.13.x")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test")
    testImplementation("app.cash.turbine:turbine")          // Flow 断言利器
}
```

这些测试跑在 JVM 上（`./gradlew testDebugUnitTest`），毫秒级反馈，是[测试金字塔](03-integration-e2e-testing.md)的地基。

## 2️⃣ 核心：测试调度器控制虚拟时间

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class NotesViewModelTest {

    // 每个测试独立的 TestDispatcher：协程不会真正并发，advanceUntilIdle 才推进
    private val testDispatcher = StandardTestDispatcher()

    @Before fun setUp() { Dispatchers.setMain(testDispatcher) }
    @After  fun tearDown() { Dispatchers.resetMain() }

    @Test
    fun `搜索词变化后 列表按新关键词刷新`() = runTest {
        val dao = FakeNoteDao()
        val viewModel = NotesViewModel(dao)

        viewModel.onQueryChange("kotlin")
        advanceUntilIdle()                       // 推进虚拟时间：防抖、Flow 全部结算

        val state = viewModel.uiState.value
        assertEquals(1, state.notes.size)
        assertEquals("kotlin", state.query)
    }
}
```

- `Dispatchers.setMain`：ViewModel 内的 `viewModelScope` 默认用 Main 调度器，测试必须替换；
- `advanceUntilIdle()`：一次性跑完所有挂起的协程任务，测试不 sleep、不等待；
- `runTest` 内的 `delay(60_000)` 会被虚拟时间立即跳过——防抖/超时逻辑秒测。

## 3️⃣ MockK：替身的两种用法

```kotlin
// 用法 A：真实协程行为复杂时，mock 掉协程 API
@Test
fun `加载失败时 UiState 进入 Error`() = runTest {
    val api = mockk<WeatherApi> {
        coEvery { currentWeather(any(), any()) } throws IOException("断网")
    }
    val location = mockk<FusedLocationProviderClient>()   // Android 类无法实例化，直接 mock
    val viewModel = WeatherViewModel(api, location)

    viewModel.load()
    advanceUntilIdle()

    assertTrue(viewModel.uiState.value is WeatherUiState.Error)
}
```

```kotlin
// 用法 B：手写 Fake（优先）——更接近真实行为，复用率高
class FakeNoteDao : NoteDao {
    private val store = mutableMapOf<Long, NoteEntity>()
    override fun observeNotes(query: String) = flow {
        emit(store.values.filter { it.title.contains(query) })
    }
    override suspend fun upsert(note: NoteEntity) { store[note.id] = note }
    override suspend fun deleteById(id: Long) { store.remove(id) }
}
```

选型：**协程/挂起函数的边界 → MockK `coEvery`；数据源本体 → 手写 Fake**。
验证交互细节（"是否被调用过一次"）用 `coVerify { }`。

## 4️⃣ Turbine：把 Flow 断言写成时间线

```kotlin
@Test
fun `UiState 依次经历 Loading 与 Success`() = runTest {
    val api = mockk<WeatherApi> {
        coEvery { currentWeather(any(), any()) } coAnswers {
            delay(1_000)                                  // 虚拟时间下立即被跳过
            WeatherResponse(WeatherResponse.CurrentWeather(25.0, 3.0))
        }
    }
    val viewModel = WeatherViewModel(api, mockk())

    viewModel.uiState.test {                              // Turbine
        viewModel.load()
        assertEquals(WeatherUiState.Loading, awaitItem())
        val success = awaitItem() as WeatherUiState.Success
        assertEquals(25.0, success.temperature)
        cancelAndIgnoreRemainingEvents()
    }
}
```

## 5️⃣ 命名与结构约定

- 测试名用反引号长句：`删除笔记后 列表不再包含该项`——失败信息即文档；
- 结构 Given / When / Then 三段式，每段空行分隔；
- 一个测试只验证一个行为；共享夹具放 `@Before`，不共享可变状态。

## 🎨 最佳实践

ViewModel 测试观察公开状态如何从初始变为加载、成功或失败，再验证重复触发和取消。依赖 WhileSubscribed 的流需要活跃收集者才能推动相应上游；测试应明确启动和清理收集，而不只读取初值。

协程测试调度器可控制它管理的延时，但不会自动加速所有真实线程或外部 I/O。用可控时钟和依赖验证防抖、重试，不把每个等待都替换成无限 advanceUntilIdle。断言用户可见状态，避免绑定私有实现。

## 🔗 相关文档

- 📖 概念字典：[协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md) ｜ [第三方库指南](../reference/library-guides/02-third-party-libs.md)
- 🧪 同级指南：[Compose UI 测试](02-ui-testing.md) ｜ [集成与端到端测试](03-integration-e2e-testing.md)
- 🚀 实战应用：[天气应用的状态机测试](../projects/02-weather-app.md) ｜ [生产级应用的质量门禁](../projects/04-production-android-app.md)


<!-- acceptance-exercise -->
## 练习与验收：让协程测试控制时间而不是等待运气

选择带 debounce 的搜索逻辑，用测试调度器连续输入两个词，推进虚拟时间后只应提交最终词；再模拟服务失败，状态应进入可重试分支。预期测试不依赖真实 delay 等待，取消后不再提交旧结果。验收时去掉 debounce 或取消检查，应有对应断言失败；虚拟时间只控制使用该调度器的工作，不会自动推进所有外部线程。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
