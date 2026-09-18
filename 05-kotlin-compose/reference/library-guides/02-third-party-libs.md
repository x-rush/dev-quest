# 第三方库指南

> **阅读准备**：Gradle 依赖、协程、HTTP 与 JSON；先能用系统能力完成小功能，再比较库提供的额外价值。

> Hilt/Retrofit/OkHttp/Coil/Ktor 五大生态库的字典式速查：核心注解与 API、最小集成示例与陷阱

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Hilt` `#Retrofit` `#OkHttp` `#Coil` `#Ktor` `#依赖注入` `#网络` |
| **更新日期** | `2026年9月` |

> 版本一律通过 `gradle/libs.versions.toml` 统一管理，本文不锁具体版本号，安装时以各库官方最新稳定版为准。

---

## 1. Hilt - 依赖注入

### 定义
基于 Dagger 的 Android 官方 DI 方案：编译期生成注入代码，用注解声明"谁能被注入、从哪提供"。

### 核心注解

| 注解 | 位置 | 作用 |
|------|------|------|
| `@HiltAndroidApp` | Application | 启动 DI 容器 |
| `@AndroidEntryPoint` | Activity/Fragment 等 | 声明注入点 |
| `@Inject` | 构造器/字段 | 标记"需要被注入/可被提供" |
| `@Module` + `@InstallIn` | 模块类 | 声明提供方式 |
| `@Provides` / `@Binds` | 模块方法 | 接口→实现绑定 |
| `@HiltViewModel` | ViewModel | ViewModel 注入 + Compose 获取 |
| `@Qualifier`（如 `@Named`） | 注解类 | 区分同类型多实例 |

### 语法和示例
```kotlin
@HiltAndroidApp
class App : Application()

@Module
@InstallIn(SingletonComponent::class)          // 单例级别容器
object DataModule {
    @Provides @Singleton
    fun provideDatabase(@ApplicationContext ctx: Context): NotesDatabase =
        Room.databaseBuilder(ctx, NotesDatabase::class.java, "notes.db").build()

    @Provides
    fun provideNoteDao(db: NotesDatabase): NoteDao = db.noteDao()
}

@HiltViewModel
class NotesViewModel @Inject constructor(
    private val repo: NoteRepository           // 构造注入，无需手写工厂
) : ViewModel()

// Compose 中获取
@Composable
fun NotesScreen(viewModel: NotesViewModel = hiltViewModel()) { /* ... */ }
```

### 陷阱
- `@Singleton` 的作用域必须与 `@InstallIn` 容器匹配（SingletonComponent 配 `@Singleton`）
- 接口绑定用 `@Binds`（抽象模块 + 抽象函数），对象构建用 `@Provides`
- 漏加 `@AndroidEntryPoint` 会在运行时崩溃，且报错信息不直观

## 2. Retrofit - 声明式 HTTP 客户端

### 定义
把 REST API 描述成 Kotlin 接口，注解映射路径与参数；`suspend` 函数自动走协程。

### 语法和示例
```kotlin
interface NotesApi {
    @GET("notes")
    suspend fun list(@Query("page") page: Int = 1): List<NoteDto>

    @GET("notes/{id}")
    suspend fun byId(@Path("id") id: Long): NoteDto

    @POST("notes")
    suspend fun create(@Body body: CreateNoteRequest): NoteDto
}

// 构建（通常放 Hilt Module）
@Provides @Singleton
fun provideApi(client: OkHttpClient, json: Json): NotesApi =
    Retrofit.Builder()
        .baseUrl("https://api.example.com/v1/")     // 必须以 / 结尾
        .client(client)
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build()
        .create(NotesApi::class.java)
```

### 错误处理
```kotlin
viewModelScope.launch {
    try {
        val notes = api.list()                       // 非 2xx 抛 HttpException
    } catch (e: HttpException) {
        _uiState.value = UiState.Error("服务端错误 ${e.code()}")
    } catch (e: IOException) {
        _uiState.value = UiState.Error("网络不可用")
    }
}
// 需要"读错误响应体"时，把返回类型改为 Response<NoteDto> 手动判 isSuccessful
```

### 陷阱
- baseUrl 忘写结尾 `/`、路径多写开头 `/` 都会拼接成错误 URL
- DTO 与领域模型分离：`NoteDto` 只在数据层流转，Repository 转成 `Note` 给上层

## 3. OkHttp - HTTP 引擎

### 定义
Retrofit 底层的 HTTP 客户端：连接池、拦截器、日志、超时都配置在这里。

### 语法和示例
```kotlin
@Provides @Singleton
fun provideOkHttp(): OkHttpClient = OkHttpClient.Builder()
    .connectTimeout(10, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .addInterceptor { chain ->                       // 应用拦截器：加公共头
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer ${TokenStore.current}")
            .build()
        chain.proceed(request)
    }
    .addInterceptor(HttpLoggingInterceptor().apply { // 仅 debug 构建加日志
        redactHeader("Authorization")
        level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BASIC else HttpLoggingInterceptor.Level.NONE
    })
    .build()
```

### 陷阱
日志拦截器打印 BODY 会泄露敏感信息——用 `BuildConfig.DEBUG` 控制；认证 Token 过期刷新通常放 `Authenticator` 而非手动重试。

## 4. Coil - 图片加载

### 定义
Kotlin-first、协程原生的图片库，与 Compose 无缝集成；Glide 的现代替代。

### 语法和示例
```kotlin
// 依赖：io.coil-kt.coil3:coil-compose + io.coil-kt.coil3:coil-network-okhttp

AsyncImage(
    model = ImageRequest.Builder(LocalContext.current)
        .data(note.coverUrl)
        .crossfade(true)
        .build(),
    contentDescription = "笔记封面",
    placeholder = painterResource(R.drawable.placeholder),
    error = painterResource(R.drawable.error),
    contentScale = ContentScale.Crop,
    modifier = Modifier.fillMaxWidth().height(160.dp).clip(RoundedCornerShape(12.dp))
)

// 命令式：拿到 ImageRequest 结果（如取 bitmap）
val context = LocalContext.current
LaunchedEffect(url) {
    val loader = context.imageLoader
    val result = loader.execute(ImageRequest.Builder(context).data(url).build())
}
```

### 陷阱
- LazyColumn 中滚动错图 → 先查条目身份、请求模型、内容版本和缓存键；手工固定缓存键可能反而复用旧图
- `contentDescription` 为 null 仅限装饰图；有含义的图必须描述（无障碍）

## 5. Ktor Client - 多平台 HTTP

### 定义
Kotlin 官方 HTTP 客户端，KMP（Android/iOS/桌面）项目首选；纯 Android 单端通常 Retrofit 更省事。

### 语法和示例
```kotlin
val client = HttpClient(CIO) {
    expectSuccess = true // 非成功响应抛出异常；调用方分类处理                     // 引擎可换 OkHttp/Android
    install(ContentNegotiation) {
        json(Json { ignoreUnknownKeys = true })
    }
    install(HttpTimeout) { requestTimeoutMillis = 15_000 }
}

suspend fun fetchNotes(): List<NoteDto> =
    client.get("https://api.example.com/v1/notes").body()
```

### 与 Retrofit 对比

| 维度 | Retrofit | Ktor Client |
|------|----------|-------------|
| 心智模型 | 注解 + 接口 | 构建 + 扩展插件 |
| 平台 | Android/JVM | KMP 全平台 |
| 序列化 | Converter（kotlinx/moshi/gson） | 内置 ContentNegotiation |
| 生态 | Android 事实标准 | KMP 事实标准 |

---

## 生态选型速查

| 需求 | 首选 |
|------|------|
| 依赖注入 | Hilt（KMP 用 Koin） |
| REST 网络请求 | Retrofit + kotlinx.serialization |
| 网络底层/拦截 | OkHttp |
| 图片加载 | Coil |
| 图片加载（View 体系/老项目） | Glide |
| 跨平台 HTTP | Ktor Client |
| JSON 解析 | kotlinx.serialization |

---

## 相关文档

- 📄 **[AndroidX 官方库指南](./01-androidx-libraries.md)** - ViewModel/Room/DataStore 等
- 📄 **[协程与 Flow API 全表](../language-concepts/03-coroutines-flow-api.md)** - suspend 网络请求的调度机制
- 📄 **[Kotlin 语法基础](../../basics/03-kotlin-syntax-essentials.md)** - 读懂数据类 DTO 的语言基础
- 📖 **[Hilt 官方文档](https://developer.android.com/training/dependency-injection/hilt-android)** - 完整指南
- 📖 **[Retrofit 官网](https://square.github.io/retrofit/)** - API 参考


<!-- full-library-explanation -->
## 为什么需要接口与可替换实现

Repository 依赖 NotesApi 接口后，测试可以提供固定成功、超时和格式错误响应，而不用真的访问网络。Hilt 负责构建依赖图，不验证远端数据；Retrofit 负责 HTTP 映射，不决定重试一次写操作是否安全；Coil 管理图片请求，不知道业务上的用户身份。

HTTP 401、429、500、连接失败与 JSON 解析失败应分别处理。刷新 token 时限制重试次数，避免多个请求同时刷新；写操作若可能在服务端已成功，要用业务幂等键或查询状态消除重复提交风险。

练习：给笔记列表替换一个 fake API，依次返回空列表、两条记录、错误。验收：每种状态都有可解释界面；生产构建不输出请求体、token 和个人资料。debug 日志同样可能泄露真实数据，不能把 DEBUG 当作安全保证。

选依赖时看目标平台、维护状态、兼容版本与替换成本；“最新稳定版”必须与整个工程兼容，不应把每个依赖独立升级到最大版本号。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
