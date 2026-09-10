# AndroidX 官方库指南

> ViewModel/Lifecycle/Room/DataStore/Navigation/WorkManager 六大官方库的字典式速查：核心 API、最小示例与陷阱

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Jetpack` `#ViewModel` `#Room` `#DataStore` `#Lifecycle` `#WorkManager` |
| **更新日期** | `2026年9月` |

---

## 1. ViewModel - 状态容器

### 定义
以配置变更（旋转等）为界的 UI 状态持有者；销毁时回调 `onCleared()`，是 `viewModelScope` 的宿主。

### 语法和示例
```kotlin
class NotesViewModel(private val repo: NoteRepository) : ViewModel() {
    val notes: StateFlow<List<Note>> = repo.observeNotes()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    override fun onCleared() { /* 最终清理 */ }
}
```

获取方式（Compose 场景）：

```kotlin
// 1. Hilt 注入（生产首选）
@HiltViewModel
class NotesViewModel @Inject constructor(repo: NoteRepository) : ViewModel()
// Compose 中：hiltViewModel()

// 2. 手写工厂（无 DI 时）
val vm: NotesViewModel = viewModel(factory = NotesViewModel.factory(repo))

// 3. 导航图级共享（同一次导航栈内共享）
val sharedVm: CartViewModel =
    backStackEntry.sharedViewModel(navController)   // 基于 navGraphViewModels 封装
```

### 陷阱
- ❌ 持有 Activity/Fragment/View/Context 引用——泄漏；需要 Application 用 `AndroidViewModel(app)`
- ❌ 暴露 `MutableStateFlow` 或 suspend 写方法给 UI——对外只读（`.asStateFlow()`）+ 事件函数
- ✅ ViewModel ≠ 数据层：纯展示转换放 UI 层，跨页面共享放 Repository

## 2. Lifecycle - 生命周期

### 定义
生命周期感知原语；Compose 场景最常用的是**生命周期感知收集**。

### 语法和示例
```kotlin
// Compose：生命周期感知收集（推荐）
val state by vm.uiState.collectAsStateWithLifecycle()

// 非组合环境（Service/Receiver）：repeatOnLifecycle 模板
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        vm.events.collect { event -> handle(event) }   // STOP 自动取消，START 自动恢复
    }
}
```

| API | 用途 |
|-----|------|
| `collectAsStateWithLifecycle()` | Compose 收集 StateFlow ⭐ |
| `repeatOnLifecycle(STARTED)` | 非 Compose 环境的安全收集 |
| `LifecycleEventObserver` | 观察具体事件（ON_RESUME 等） |

### 陷阱
`lifecycleScope.launch { flow.collect {} }` 不感知 STARTED，后台仍会收集——必须套 `repeatOnLifecycle` 或用 Compose 版 API。

## 3. Room - 持久化数据库

### 定义
SQLite 的编译期校验封装；`suspend`/`Flow` 返回类型自动获得协程与响应式支持。

### 语法和示例
```kotlin
@Entity(tableName = "notes", indices = [Index("createdAt")])
data class NoteEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val title: String,
    val content: String,
    val createdAt: Long
)

@Dao
interface NoteDao {
    @Query("SELECT * FROM notes ORDER BY createdAt DESC")
    fun observeAll(): Flow<List<NoteEntity>>          // 可观察查询

    @Query("SELECT * FROM notes WHERE id = :id")
    suspend fun byId(id: Long): NoteEntity?

    @Upsert                                            // 有则更新无则插入
    suspend fun upsert(note: NoteEntity)

    @Query("DELETE FROM notes WHERE id = :id")
    suspend fun deleteById(id: Long)
}

@Database(entities = [NoteEntity::class], version = 2, exportSchema = true)
abstract class NotesDatabase : RoomDatabase() {
    abstract fun noteDao(): NoteDao
}

// 建库（学习期）；生产交给 Hilt 提供
Room.databaseBuilder(ctx, NotesDatabase::class.java, "notes.db")
    .addMigrations(MIGRATION_1_2)
    .build()

// 手写迁移
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE notes ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0")
    }
}
```

### 陷阱
- 编译器用 **KSP**（`ksp(libs.androidx.room.compiler)`），KAPT 已是旧方案且显著更慢
- Entity 结构变化必须升 version + 提供迁移（或开发期 `fallbackToDestructiveMigration()` 重建——会丢数据）
- `Flow` 查询在主线程收集即可；`suspend` 写入自动切 IO——无需自己包 `withContext`

## 4. DataStore - 键值与 Proto 存储

### 定义
替代 SharedPreferences 的异步、事务性存储；Preferences DataStore 存键值对，Proto DataStore 存类型安全对象。

### 语法和示例
```kotlin
// 顶层声明（全应用唯一）
val Context.settingsStore by preferencesDataStore(name = "settings")

class SettingsRepository(private val context: Context) {
    private val SORT_KEY = stringPreferencesKey("sort_order")     // key 需常量化

    val sortOrder: Flow<String> = context.settingsStore.data
        .map { it[SORT_KEY] ?: "created" }                         // 默认值

    suspend fun setSortOrder(value: String) {
        context.settingsStore.edit { it[SORT_KEY] = value }        // 事务性写入
    }
}
```

### 与 SharedPreferences 对比

| 维度 | DataStore | SharedPreferences |
|------|-----------|-------------------|
| API | 全异步 Flow/suspend | 同步阻塞 |
| 一致性 | 事务性 | 无 |
| 错误处理 | 显式（IOException 可捕获） | 静默失败 |

### 陷阱
- `preferencesDataStore` 属性只能声明一次（同名 store 重复声明抛异常）
- 读到的是 `Flow`——收集才开始读；写入必须 suspend（或 `runBlocking` 仅限无 UI 场景）

## 5. Navigation Compose - 导航

### 定义
单 Activity 应用的页面栈管理；核心是 NavController + NavHost + 路由（字符串或 2.8+ 的类型安全 `@Serializable` 路由）。

### 语法和示例
```kotlin
// 类型安全路由（2.8+，配合 kotlinx.serialization）
@Serializable data object NotesRoute
@Serializable data class NoteDetailRoute(val id: Long)

NavHost(navController, startDestination = NotesRoute) {
    composable<NotesRoute> {
        NotesScreen(onOpen = { id -> navController.navigate(NoteDetailRoute(id)) })
    }
    composable<NoteDetailRoute> { entry ->
        val route = entry.toRoute<NoteDetailRoute>()       // 类型安全取参
        NoteDetailScreen(route.id)
    }
}
```

> 📖 字符串路由、返回栈选项、底部导航的完整教程见 [Navigation Compose 入门](../../basics/06-navigation.md)。

## 6. WorkManager - 后台任务

### 定义
可延迟、可约束（网络/充电）、保证执行的后台任务调度；重启后任务恢复。

### 语法和示例
```kotlin
class SyncWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result =
        try { repo.sync(); Result.success() }
        catch (e: IOException) { Result.retry() }          // 指数退避重试
}

val request = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 10, TimeUnit.SECONDS)
    .build()

WorkManager.getInstance(context).enqueue(request)
```

### 陷阱
需要**精确时间执行**的任务（闹钟）不归它管（用 AlarmManager）；短时即时任务直接用协程即可，别为一切上 WorkManager。

---

## 选型速查

| 数据类型 | 存储 |
|----------|------|
| 结构化记录（可查询/排序） | Room |
| 用户设置/开关/Token | DataStore |
| 页面状态（跨旋转） | ViewModel |
| UI 瞬时状态 | remember/rememberSaveable |
| 磁盘大文件 | File + MediaStore |
| 必达后台任务 | WorkManager |

---

## 相关文档

- 📄 **[协程与 Flow API 全表](../language-concepts/03-coroutines-flow-api.md)** - Room Flow/stateIn 的底层机制
- 📄 **[第三方库指南](./02-third-party-libs.md)** - Hilt/Retrofit/Coil 等
- 📄 **[第一个项目：笔记应用](../../basics/08-first-project.md)** - Room+ViewModel 的完整落地
- 📖 **[Jetpack 官方文档](https://developer.android.com/jetpack)** - 全库总览
