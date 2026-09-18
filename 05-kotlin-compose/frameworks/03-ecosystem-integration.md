# 生态集成 - Room + Hilt + Retrofit + ViewModel 完整链路

## 先看框架承担哪部分职责

**Android 数据链路**：网络与数据库提供数据，Repository 协调来源，ViewModel 暴露页面状态，UI 发送事件。Hilt 负责装配对象，不负责数据一致性。

**最小练习与预期结果**：新增一条本地笔记并从 Flow 观察更新；再模拟网络失败，说明当前界面显示本地数据还是错误。

具体 API 与安装版本以[模块基线](../README.md)和本篇官方来源为准。先完成这条数据路径，再展开后面的高级配置；框架名称变化后，输入边界、状态归属和失败处理仍是需要理解的机制。

> **文档简介**: 一次性打通现代 Android 四件套——Room 本地存储、Hilt 依赖注入、Retrofit 网络层与 ViewModel 状态管理，形成可复用的项目骨架
>
> **目标读者**: 已掌握 Compose 基础与协程、准备搭建真实应用架构的中级学习者
>
> **前置知识**: [Compose 进阶](02-compose-advanced.md)、[协程与 Flow 基础](../basics/07-coroutines-flow-basics.md)、[第一个项目](../basics/08-first-project.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（frameworks） |
| **难度** | ⭐⭐ |
| **标签** | `#room` `#hilt` `#retrofit` `#viewmodel` `#repository` |
| **更新日期** | `2026年9月` |

</details>

---

## 🗺️ 集成蓝图

```
Compose UI ──事件──▶ ViewModel ──调用──▶ Repository ──▶ Retrofit(远程)
   ▲                                        │
   └──────StateFlow ◀── Flow ◀── Room(本地) ◀┘
```

核心原则：**Room 是唯一事实来源**。Repository 先写 Room，Room 的 Flow 自动驱动 UI；
网络只负责"补充数据"，UI 永远不直接依赖 Retrofit。各库定位与选型见
[AndroidX 官方库指南](../reference/library-guides/01-androidx-libraries.md) 与
[第三方库指南](../reference/library-guides/02-third-party-libs.md)。

## 1️⃣ 数据层：Room 实体与 DAO

```kotlin
@Entity(tableName = "articles")
data class ArticleEntity(
    @PrimaryKey val id: Long,
    val title: String,
    val summary: String,
    val updatedAt: Long,
)

@Dao
interface ArticleDao {
    // UI 直接观察这张表：任何写入自动推流
    @Query("SELECT * FROM articles ORDER BY updatedAt DESC")
    fun observeAll(): Flow<List<ArticleEntity>>

    @Upsert
    suspend fun upsertAll(articles: List<ArticleEntity>)

    @Query("DELETE FROM articles")
    suspend fun clear()
}

@Database(entities = [ArticleEntity::class], version = 1, exportSchema = true)
abstract class AppDatabase : RoomDatabase() {
    abstract fun articleDao(): ArticleDao
}
```

## 2️⃣ 网络层：Retrofit 接口

```kotlin
interface ArticleApi {
    @GET("v1/articles")
    suspend fun fetchArticles(@Query("page") page: Int): List<ArticleDto>
}

// DTO 与 Entity 分离，映射写在同文件的扩展函数中
fun ArticleDto.toEntity() = ArticleEntity(id, title, summary, updatedAt)
```

依赖（Gradle Kotlin DSL，版本统一走 version catalog）：

```kotlin
dependencies {
    implementation("androidx.room:room-runtime")
    implementation("androidx.room:room-ktx")
    ksp("androidx.room:room-compiler")            // KSP 编译期生成实现
    implementation("com.squareup.retrofit2:retrofit")
    implementation("com.squareup.retrofit2:converter-kotlinx-serialization")
    implementation("androidx.hilt:hilt-navigation-compose")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose")
}
```

## 3️⃣ Repository：合并远程与本地

```kotlin
class ArticleRepository @Inject constructor(
    private val api: ArticleApi,
    private val dao: ArticleDao,
) {
    val articles: Flow<List<Article>> =
        dao.observeAll().map { list -> list.map { it.toDomain() } }

    // 先落库，再让 UI 经由 Flow 收流；失败向上抛出，由 ViewModel 统一转状态
    suspend fun refresh() {
        val remote = api.fetchArticles(page = 1)
        dao.upsertAll(remote.map { it.toEntity() })
    }
}
```

## 4️⃣ Hilt：把所有线接起来

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db").build()

    @Provides @Singleton
    fun provideArticleApi(): ArticleApi = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build()
        .create(ArticleApi::class.java)

    @Provides @Singleton
    fun provideRepository(api: ArticleApi, db: AppDatabase) =
        ArticleRepository(api, db.articleDao())
}
```

应用入口与 Activity 各加一行注解：`@HiltAndroidApp`、`@AndroidEntryPoint`。

## 5️⃣ ViewModel：状态收敛为单一 UiState

```kotlin
data class ArticleUiState(
    val loading: Boolean = false,
    val items: List<Article> = emptyList(),
    val error: String? = null,
)

@HiltViewModel
class ArticleViewModel @Inject constructor(
    private val repository: ArticleRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(ArticleUiState(loading = true))
    val uiState: StateFlow<ArticleUiState> = _uiState.asStateFlow()

    init {
        // 订阅数据库流 → 合并进 UiState
        viewModelScope.launch {
            repository.articles.collect { items ->
                _uiState.update { it.copy(items = items, loading = false) }
            }
        }
        refresh()
    }

    fun refresh() = viewModelScope.launch {
        _uiState.update { it.copy(loading = true) }
        runCatching { repository.refresh() }
            .onFailure { e ->
                if (e is kotlinx.coroutines.CancellationException) throw e  // 取消异常必须放行
                _uiState.update { it.copy(loading = false, error = e.message) }
            }
            .onSuccess { _uiState.update { it.copy(loading = false, error = null) } }
    }
}
```

## 6️⃣ UI 层：hiltViewModel + collectAsStateWithLifecycle

```kotlin
@Composable
fun ArticleScreen(viewModel: ArticleViewModel = hiltViewModel()) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    when {
        state.loading -> CircularProgressIndicator()
        state.error != null -> ErrorRetry(text = state.error!!, onRetry = viewModel::refresh)
        else -> LazyColumn {
            items(state.items, key = { it.id }) { article ->
                ArticleRow(article)
            }
        }
    }
}
```

## 🎨 最佳实践

网络 DTO、数据库 Entity 与业务模型用于隔离不同契约；当字段与生命周期确实不同再拆分，简单程序不必机械复制三份相同数据。构造参数即可表达依赖，Hilt 在对象图增长后帮助组装，不意味着所有依赖只能经它传递。

UI 从可观察状态读取结果，服务层负责数据协调。按生命周期收集不自动停止所有上游工作，应同时核对 StateFlow 的共享策略。代码生成配置缺失可能直接导致构建失败，先检查构建诊断和生成源码，不能笼统断言只在运行时暴露。

## 🔗 相关文档

- 📖 概念字典：[AndroidX 官方库指南](../reference/library-guides/01-androidx-libraries.md) ｜ [第三方库指南](../reference/library-guides/02-third-party-libs.md) ｜ [协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md)
- 📖 前置教程：[第一个项目 - Compose + Room 笔记应用](../basics/08-first-project.md)
- 🚀 后续学习：[入门项目：笔记应用](../projects/01-notes-app.md) ｜ [进阶项目：新闻阅读器](../projects/03-news-reader.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
