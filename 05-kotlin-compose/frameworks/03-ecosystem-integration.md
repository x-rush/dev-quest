# 生态集成 - Room + Hilt + Retrofit + ViewModel 完整链路

> **文档简介**: 一次性打通现代 Android 四件套——Room 本地存储、Hilt 依赖注入、Retrofit 网络层与 ViewModel 状态管理，形成可复用的项目骨架
>
> **目标读者**: 已掌握 Compose 基础与协程、准备搭建真实应用架构的中级学习者
>
> **前置知识**: [Compose 进阶](02-compose-advanced.md)、[协程与 Flow 基础](../basics/07-coroutines-flow-basics.md)、[第一个项目](../basics/08-first-project.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（frameworks） |
| **难度** | ⭐⭐ |
| **标签** | `#room` `#hilt` `#retrofit` `#viewmodel` `#repository` |
| **更新日期** | `2026年9月` |

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

### ✅ 推荐

- DTO / Entity / Domain 三套模型各司其职，边界处显式映射
- 所有依赖经 Hilt 注入，测试时可整体替换为 Fake（见[单元测试](../testing/01-unit-testing.md)）
- `StateFlow` + `collectAsStateWithLifecycle`，后台自动停止收集省电

### ❌ 避免陷阱

- UI 直接调用 Retrofit 或全局单例——破坏可测试性，也违背单向数据流（原理见[应用架构](../advanced-topics/architecture/01-app-architecture.md)）
- 在 `Application` 中同步初始化数据库/网络，拖慢冷启动（对策见[启动与内存优化](../advanced-topics/performance/02-startup-memory.md)）
- 忘记 `ksp` 编译器依赖，Room/Hilt 编译期不生成代码，运行期才报错

## 🔗 相关文档

- 📖 概念字典：[AndroidX 官方库指南](../reference/library-guides/01-androidx-libraries.md) ｜ [第三方库指南](../reference/library-guides/02-third-party-libs.md) ｜ [协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md)
- 📖 前置教程：[第一个项目 - Compose + Room 笔记应用](../basics/08-first-project.md)
- 🚀 后续学习：[入门项目：笔记应用](../projects/01-notes-app.md) ｜ [进阶项目：新闻阅读器](../projects/03-news-reader.md)
