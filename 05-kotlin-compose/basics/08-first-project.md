# 第一个项目 - Compose + Room 笔记应用

> **文档简介**: 综合运用本模块所学，从零构建一个完整的本地笔记应用：Compose 界面 + ViewModel + StateFlow + Room 持久化，走通现代 Android 分层架构
>
> **目标读者**: 已完成 01-07 全部课程的学习者，准备把知识点串成完整应用
>
> **前置知识**: [协程与 Flow 基础](./07-coroutines-flow-basics.md)；[Navigation Compose](./06-navigation.md)（可选扩展用）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#实战项目` `#Room` `#StateFlow` `#ViewModel` `#笔记应用` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

- ✅ 独立搭建 UI → ViewModel → Repository → Room 四层数据通路
- ✅ 掌握 Room 的 Entity/Dao/Database 三件套与 KSP 集成
- ✅ 实现列表展示、新增、删除的完整增删查流程
- ✅ 体验"改数据库 = 界面自动更新"的响应式架构

## 📋 目录

- [项目目标](#项目目标)
- [架构总览](#架构总览)
- [第一步：数据层](#第一步数据层)
- [第二步：Repository](#第二步repository)
- [第三步：ViewModel](#第三步viewmodel)
- [第四步：Compose 界面](#第四步compose-界面)
- [运行验证](#运行验证)
- [进阶挑战](#进阶挑战)

---

## 🎯 项目目标

构建 **QuickNotes**：一个本地笔记应用。

**功能清单**：
1. 笔记列表（按创建时间倒序）
2. 点击 FAB 弹出对话框新增笔记（标题 + 内容）
3. 每条笔记可点按钮删除
4. 数据持久化在 Room 数据库，重启应用不丢

**技术栈**: Kotlin + Compose (Material 3) + ViewModel + StateFlow + Room + Coroutines。

---

## 🏗️ 架构总览

```text
┌─────────────────┐
│  Compose UI     │  NotesScreen：收集状态 + 上抛事件
└───────┬─────────┘
        │ StateFlow ↓（状态下行）  事件 ↑（onAddNote 回调）
┌───────┴─────────┐
│  NotesViewModel │  持有 UI 状态，viewModelScope 执行写入
└───────┬─────────┘
┌───────┴─────────┐
│  NoteRepository │  数据源的门面（本期只有 Room，日后可加网络）
└───────┬─────────┘
┌───────┴─────────┐
│  Room Database  │  NoteEntity / NoteDao
└─────────────────┘
```

数据流是双向单向的：**状态向下**（Room → Flow → StateFlow → Compose），**事件向上**（点击 → ViewModel → Repository → Room）。

---

## 🗄️ 第一步：数据层

### 1. 添加 Room 依赖（KSP）

`libs.versions.toml`（版本以官方最新稳定版为准）：

```toml
[plugins]
ksp = { id = "com.google.devtools.ksp", version = "2.2.20-2.0.4" }
room = { id = "androidx.room", version = "2.8.4" }

[libraries]
androidx-room-runtime = { group = "androidx.room", name = "room-runtime" }
androidx-room-ktx = { group = "androidx.room", name = "room-ktx" }
androidx-room-compiler = { group = "androidx.room", name = "room-compiler" }
```

`app/build.gradle.kts`：

```kotlin
plugins {
    alias(libs.plugins.ksp)
    alias(libs.plugins.room)
}

room { schemaDirectory("$projectDir/schemas") }   // 导出 schema 便于日后迁移

dependencies {
    implementation(libs.androidx.room.runtime)
    implementation(libs.androidx.room.ktx)
    ksp(libs.androidx.room.compiler)
}
```

### 2. Entity 与 Dao

```kotlin
@Entity(tableName = "notes")
data class NoteEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val title: String,
    val content: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Dao
interface NoteDao {
    // 返回 Flow：表一旦变化自动重新发射（响应式的关键）
    @Query("SELECT * FROM notes ORDER BY createdAt DESC")
    fun observeAll(): Flow<List<NoteEntity>>

    @Insert
    suspend fun insert(note: NoteEntity)

    @Delete
    suspend fun delete(note: NoteEntity)
}
```

### 3. Database 与单例入口

```kotlin
@Database(entities = [NoteEntity::class], version = 1)
abstract class NotesDatabase : RoomDatabase() {
    abstract fun noteDao(): NoteDao

    companion object {
        @Volatile private var INSTANCE: NotesDatabase? = null

        fun get(context: Context): NotesDatabase =
            INSTANCE ?: synchronized(this) {
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    NotesDatabase::class.java,
                    "notes.db"
                ).build().also { INSTANCE = it }
            }
    }
}
```

> ⚠️ 学习期用 companion object 单例即可；生产项目应交给 Hilt 管理（见[三方库指南](../reference/library-guides/02-third-party-libs.md)）。

---

## 📦 第二步：Repository

隔离 UI 与数据源，并做领域模型转换（保持 import 边界干净）：

```kotlin
// 面向 UI 的领域模型（与 Entity 解耦）
data class Note(val id: Long, val title: String, val content: String)

class NoteRepository(private val dao: NoteDao) {

    fun observeNotes(): Flow<List<Note>> =
        dao.observeAll().map { list ->
            list.map { Note(it.id, it.title, it.content) }
        }

    suspend fun addNote(title: String, content: String) =
        dao.insert(NoteEntity(title = title, content = content))

    suspend fun deleteNote(note: Note) =
        dao.delete(NoteEntity(id = note.id, title = note.title, content = note.content))

    companion object {
        fun from(context: Context) = NoteRepository(NotesDatabase.get(context).noteDao())
    }
}
```

---

## 🧠 第三步：ViewModel

```kotlin
class NotesViewModel(private val repository: NoteRepository) : ViewModel() {

    val notes: StateFlow<List<Note>> = repository.observeNotes()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = emptyList()
        )

    fun addNote(title: String, content: String) {
        if (title.isBlank()) return                      // 输入校验留在 ViewModel
        viewModelScope.launch { repository.addNote(title.trim(), content) }
    }

    fun deleteNote(note: Note) {
        viewModelScope.launch { repository.deleteNote(note) }
    }
}
```

> 💡 注意 `NotesViewModel(repository)` 需要参数，默认 `viewModel()` 工厂创建不了。学习期可用 `viewModel(factory = ...)` 自定义工厂，或直接引入 Hilt 的 `@HiltViewModel`（推荐，见[三方库指南](../reference/library-guides/02-third-party-libs.md)）。

---

## 🖼️ 第四步：Compose 界面

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotesScreen(viewModel: NotesViewModel) {
    val notes by viewModel.notes.collectAsStateWithLifecycle()
    NotesContent(notes = notes, onAdd = viewModel::addNote, onDelete = viewModel::deleteNote)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotesContent(
    notes: List<Note>,
    onAdd: (title: String, content: String) -> Unit,
    onDelete: (Note) -> Unit
) {
    var showDialog by rememberSaveable { mutableStateOf(false) }

    Scaffold(
        topBar = { TopAppBar(title = { Text("QuickNotes") }) },
        floatingActionButton = {
            FloatingActionButton(onClick = { showDialog = true }) {
                Icon(Icons.Default.Add, contentDescription = "新增笔记")
            }
        }
    ) { padding ->
        if (notes.isEmpty()) {
            Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                Text("还没有笔记，点右下角 + 创建一条吧")
            }
        } else {
            LazyColumn(
                modifier = Modifier.padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(notes, key = { it.id }) { note ->
                    NoteCard(note = note, onDelete = { onDelete(note) })
                }
            }
        }
    }

    if (showDialog) {
        AddNoteDialog(
            onConfirm = { title, content ->
                onAdd(title, content)
                showDialog = false
            },
            onDismiss = { showDialog = false }
        )
    }
}

@Composable
fun NoteCard(note: Note, onDelete: () -> Unit) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp)) {
            Text(note.title, style = MaterialTheme.typography.titleMedium)
            Spacer(Modifier.height(4.dp))
            Text(note.content, style = MaterialTheme.typography.bodyMedium, maxLines = 3)
            TextButton(onClick = onDelete, modifier = Modifier.align(Alignment.End)) {
                Text("删除")
            }
        }
    }
}

@Composable
fun AddNoteDialog(onConfirm: (String, String) -> Unit, onDismiss: () -> Unit) {
    var title by rememberSaveable { mutableStateOf("") }
    var content by rememberSaveable { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("新建笔记") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = title, onValueChange = { title = it }, label = { Text("标题") })
                OutlinedTextField(value = content, onValueChange = { content = it }, label = { Text("内容") })
            }
        },
        confirmButton = {
            TextButton(onClick = { onConfirm(title, content) }, enabled = title.isNotBlank()) {
                Text("保存")
            }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("取消") } }
    )
}
```

---

## ✅ 运行验证

1. `Run ▶️` 部署到模拟器，看到空态提示
2. 点 FAB → 输入标题内容 → 保存 → 列表立即出现新笔记（无需手动刷新，Room Flow 自动驱动）
3. 点"删除"→ 条目消失
4. **杀掉应用重新打开** → 笔记仍在（持久化生效）

任何一步不符合预期，先查 Logcat 中 Room/数据库相关报错，再对照[故障排除速查](../reference/quick-references/02-troubleshooting.md)。

---

## 🚀 进阶挑战

- [ ] **编辑功能**: 新增 `detail/{noteId}` 页面（Navigation），进入后可修改并保存
- [ ] **搜索**: 顶部搜索框 → ViewModel 中对 `query` 做 `debounce` + `flatMapLatest` 过滤
- [ ] **滑动删除**: 用 `SwipeToDismissBox` 替换删除按钮
- [ ] **依赖注入**: 引入 Hilt，用 `@HiltViewModel` + `@Inject` 消灭手写工厂
- [ ] **设置持久化**: 用 DataStore 记住"列表排序方式"（见[官方库指南](../reference/library-guides/01-androidx-libraries.md)）
- [ ] **单元测试**: 为 ViewModel 编写 JUnit 测试（配合 Turbine 验证 StateFlow）

---

## 🔗 相关文档

- 📄 **[AndroidX 官方库指南](../reference/library-guides/01-androidx-libraries.md)** - Room/DataStore 深入用法
- 📄 **[协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md)** - stateIn/WhileSubscribed 原理
- 📄 **[Material 3 主题系统](../reference/framework-essentials/02-compose-material3.md)** - 给应用换上自定义主题
- 📖 **[Room 官方指南](https://developer.android.com/training/data-storage/room)** - 完整 Room 文档
