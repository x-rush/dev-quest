# 集成与端到端测试

> **文档简介**: 超越单组件：Hilt 注入下打通 Room + 网络（MockWebServer）的集成测试，以及跨页面用户旅程的端到端测试思路
>
> **目标读者**: 单元与 UI 测试已就位、要验证"整条链路真的能跑"的进阶学习者
>
> **前置知识**: [单元测试](01-unit-testing.md)、[Compose UI 测试](02-ui-testing.md)、[生态集成](../frameworks/03-ecosystem-integration.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（testing） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#hilt-test` `#mockwebserver` `#room-in-memory` `#e2e` |
| **更新日期** | `2026年9月` |

</details>

---

## 🧭 测试金字塔中的定位

```
      ／ E2E（跨页面旅程，少量）      ＼   慢、脆、真实
    ／  集成（Repository/页面+依赖）    ＼  中速、关键链路
  ／    单元（ViewModel/逻辑，大量）      ＼ 快、稳定（01 篇）
```

集成与 E2E 用真实组件组合（真 Room + 假 HTTP），只把**边界**替换掉：数据库用内存版，服务器用 MockWebServer。

## 1️⃣ Hilt 测试环境搭建

```kotlin
// build.gradle.kts
androidTestImplementation("com.google.dagger:hilt-android-testing")
kspAndroidTest("com.google.dagger:hilt-android-compiler")
```

```kotlin
@HiltAndroidTest
class NewsIntegrationTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeRule = createAndroidComposeRule<TestActivity>()   // @AndroidEntryPoint 的空壳 Activity

    @Inject lateinit var repository: ArticleRepository           // 注入真实依赖
}
```

## 2️⃣ 替换边界：内存数据库 + 假服务器

```kotlin
@Module
@TestInstallIn(components = [SingletonComponent::class], replaces = [AppModule::class])
object TestAppModule {

    @Provides @Singleton
    fun provideDb(@ApplicationContext context: Context): AppDatabase =
        Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()            // 仅测试环境
            .build()

    @Provides @Singleton
    fun provideApi(server: MockWebServer): ArticleApi =
        retrofit(server.url("/")).create(ArticleApi::class.java)
}

class NewsRepositoryIntegrationTest {

    val server = MockWebServer()
    @Before fun setUp() { server.start() }
    @After fun tearDown() { server.shutdown() }

    @Test
    fun `刷新成功后 数据库出现文章`() = runTest {
        server.enqueue(
            MockResponse().setBody("""{"articles":[{"id":1,"title":"测试新闻","hasMore":false}]}""")
        )
        // repository.refresh() → Retrofit → MockWebServer → Room 全链路
        repository.refresh()
        val items = repository.articles.first()
        assertEquals("测试新闻", items.first().title)
    }

    @Test
    fun `服务器 500 时 返回失败且缓存不丢`() = runTest {
        repository.refresh()                              // 先塞入缓存
        server.enqueue(MockResponse().setResponseCode(500))
        assertFailsWith<Exception> { repository.refresh() }
        assertEquals(1, repository.articles.first().size) // 缓存仍在：离线优先的底线
    }
}
```

要点：**JSON 放 body 字符串即文档**——响应结构变更时测试会先红；DB 断言直接查注入的 Room，不经过 UI。

## 3️⃣ 端到端：用户旅程级测试

E2E 测的是"用户能否完成一件事"，跨页面、跨组件：

```kotlin
@HiltAndroidTest
class NoteJourneyTest {

    @get:Rule val hiltRule = HiltAndroidRule(this)
    @get:Rule val rule = createAndroidComposeRule<MainActivity>()

    @Before fun setUp() = hiltRule.inject()

    @Test
    fun `新建笔记后 出现在列表并支持搜索`() {
        // ① 列表页 → 新建
        rule.onNodeWithContentDescription("新建笔记").performClick()
        // ② 编辑页输入并保存（真实 Room 内存库）
        rule.onNodeWithText("标题").performTextInput("Compose 指南")
        rule.onNodeWithText("保存").performClick()
        // ③ 回到列表，断言可见
        rule.waitUntil { rule.onAllNodesWithText("Compose 指南").fetchSemanticsNodes().isNotEmpty() }
        // ④ 走搜索链路
        rule.onNodeWithText("搜索标题").performTextInput("Compose")
        rule.onNodeWithText("Compose 指南").assertIsDisplayed()
    }
}
```

E2E 实践要点：

- **少而关键**：每个核心旅程一条（注册→发帖→删除），其余交给金字塔下层；
- Hilt 注入的 `@TestInstallIn` 保证 E2E 也不碰真网络/真盘；
- Compose 测试自动同步重组与 Idling，无需手写 IdlingResource；
- 需要多设备矩阵/系统权限（相机、定位）时，考虑 Play Console 的预发布报告或云真机——
  发布前的自动化检查见 [CI/CD 与可观测性](../deployment/03-ci-cd-observability.md)。

## 4️⃣ 运行与分级命令

```bash
./gradlew testDebugUnitTest            # JVM 单元测试（每次提交）
./gradlew connectedDebugAndroidTest    # 仪器测试：集成 + E2E（PR 门禁/夜间）
./gradlew connectedDebugAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.class=com.example.NewsRepositoryIntegrationTest
```

## 🎨 最佳实践

集成测试保留本次要验证的协作链，例如 Repository 与真实 DAO，网络则可由受控服务返回成功或错误数据。每条测试建立可预测状态并清理资源，允许单独或换序运行。

断言应覆盖最终数据及失败影响。请求次数在“防止重复提交”等契约中有意义，其余场景不必绑定实现细节。E2E 选择跨层风险高的少数旅程；数据库细节和业务组合优先在反馈更快的层验证。

## 🔗 相关文档

- 📖 概念字典：[AndroidX 官方库指南](../reference/library-guides/01-androidx-libraries.md) ｜ [常见错误与故障排除](../reference/quick-references/02-troubleshooting.md)
- 🧪 同级指南：[单元测试](01-unit-testing.md) ｜ [Compose UI 测试](02-ui-testing.md)
- 🚀 实战应用：[天气应用的 MockWebServer 先行](../projects/02-weather-app.md) ｜ [生产级应用的质量门禁](../projects/04-production-android-app.md)


<!-- acceptance-exercise -->
## 练习与验收：验证数据库与页面之间的真实边界

在独立测试库中创建记录，通过页面修改后重新查询数据库，确认持久化值改变；再以旧 schema 测试库启动升级流程，检查记录数和关键字段。预期测试失败时仍清理本轮资源。验收再测试进程重建后的页面恢复；只重组一次或旋转屏幕，不能替代真正的进程重建与磁盘恢复验证。

以上是在个人或隔离测试环境中的练习，不是本轮已执行记录；实际运行范围见仓库文档质量报告。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
