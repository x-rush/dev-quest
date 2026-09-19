# 第一个项目 - Compose + Room 笔记应用

## 先理解，再动手

Room 保存数据，ViewModel 组织页面状态，Composable 显示和发事件。三层用一条新增笔记流程连接，先别引入同步服务。

**本节自测**：新增、查询、删除各做一次，关闭并重新启动应用。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

查询反映保存结果，删除确实持久化；空标题失败不能留下半条记录。

</details>

> **文档简介**: 综合运用本模块所学，从零构建一个完整的本地笔记应用：Compose 界面 + ViewModel + StateFlow + Room 持久化，走通现代 Android 分层架构
>
> **目标读者**: 已完成 01-07 全部课程的学习者，准备把知识点串成完整应用
>
> **前置知识**: [协程与 Flow 基础](./07-coroutines-flow-basics.md)；[Navigation Compose](./06-navigation.md)（可选扩展用）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#实战项目` `#Room` `#StateFlow` `#ViewModel` `#笔记应用` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

- ✅ 独立搭建 UI → ViewModel → Repository → Room 四层数据通路
- ✅ 掌握 Room 的 Entity/Dao/Database 三件套与 KSP 集成
- ✅ 实现列表展示、新增、删除的完整增删查流程
- ✅ 体验"改数据库 = 界面自动更新"的响应式架构

## 📋 目录

- [项目目标](#-项目目标)
- [架构总览](#️-架构总览)
- [第一步：数据层](#️-第一步数据层)
- [第二步：Repository](#-第二步repository)
- [第三步：ViewModel](#-第三步viewmodel)
- [第四步：Compose 界面](#️-第四步compose-界面)
- [运行验证](#-运行验证)
- [进阶挑战](#-进阶挑战)

---

## 🎯 项目目标

构建 **QuickNotes**：一个本地笔记应用。

### 开工检查与交付物

本模块提供文档和代码片段，不附带已配置好的 QuickNotes 工程。先完成[第一个 Compose 应用](./02-first-compose-app.md)，在 Android Studio 创建自己的空 Compose 工程并成功显示模板页面；保留生成的 Gradle Wrapper、版本目录和应用包名。需要能解释 `suspend`、`Flow` 和 `viewModelScope` 的用途，不清楚时先完成[协程与 Flow](./07-coroutines-flow-basics.md)。

首次实现按本文顺序完成数据层到 UI，随后接入“运行验证”中的 `MainActivity` 与 import；仅粘贴 Entity/Dao 不会出现界面。Room 的 KSP 配置不清楚时先查[KSP 配置指南](../reference/library-guides/03-ksp-configuration.md)。

交付自己的工程源文件、Gradle Wrapper、`gradle/libs.versions.toml`、导出的 Room schema，以及一份验收记录。记录要分别列出构建结果、设备型号/系统、新增 A/B 后删除 B 再重启的结果、空白标题结果、旋转时草稿结果；未执行项写“未验证”。构建成功后仍需完成文末设备验收。通过后进入[本地笔记应用](../projects/01-notes-app.md)，继续实现编辑与搜索。

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

数据流遵循单向数据流：**状态向下**（Room → Flow → StateFlow → Compose），**事件向上**（点击 → ViewModel → Repository → Room）。事件会触发新的状态，而不是由 UI 直接修改数据库中的状态。

---

## 🗄️ 第一步：数据层

### 1. 添加 Room 依赖（KSP）

`gradle/libs.versions.toml`（在你新建的工程中编辑；以下是待构建验证的教学配置，本仓库没有可直接复用的已验证 Android 工程锁文件。不要因为“最新稳定版”就单独升级某一个插件或库）：

将下面条目合并到已有同名节，不要重复创建 `[plugins]` 或 `[libraries]`。本例 Room 2.8 系列要求 `minSdk >= 23`；Room 插件版本不会替库声明版本，三个库必须显式使用同一个版本。先保留 Android Studio 空 Compose 工程已有的 AGP、Kotlin、Compose、Activity 和 Lifecycle 版本。本文尚无 Android 构建证据，不能把以下配置称为“已验证兼容组合”。

```toml
[versions]
room = "2.8.5"

[plugins]
ksp = { id = "com.google.devtools.ksp", version = "2.3.11" }   # KSP 独立版本号，与 Kotlin 版本解耦
room = { id = "androidx.room", version.ref = "room" }

[libraries]
androidx-room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
androidx-room-ktx = { group = "androidx.room", name = "room-ktx", version.ref = "room" }
androidx-room-compiler = { group = "androidx.room", name = "room-compiler", version.ref = "room" }
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
    @Query("SELECT * FROM notes ORDER BY createdAt DESC, id DESC")
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

此处单例持有 `applicationContext`，不持有 Activity。Hilt 是管理较复杂对象图的一种选择；手写组合入口本身不意味着不能用于生产。需要测试时，把 Repository 的依赖显式传入。

---

## 📦 第二步：Repository

隔离 UI 与数据源，并做领域模型转换（保持 import 边界干净）：

```kotlin
// 面向 UI 的领域模型（与 Entity 解耦）
data class Note(val id: Long, val title: String, val content: String)

data class NoteDraft(val title: String, val content: String)

fun validateNote(title: String, content: String): NoteDraft {
    val normalized = title.trim()
    require(normalized.isNotEmpty()) { "标题不能为空" }
    require(normalized.length <= 120) { "标题最多 120 个 UTF-16 单元" }
    require(content.length <= 10_000) { "内容最多 10000 个 UTF-16 单元" }
    return NoteDraft(normalized, content)
}

class NoteRepository(private val dao: NoteDao) {

    fun observeNotes(): Flow<List<Note>> =
        dao.observeAll().map { list ->
            list.map { Note(it.id, it.title, it.content) }
        }

    suspend fun addNote(title: String, content: String) {
        val draft = validateNote(title, content)
        dao.insert(NoteEntity(title = draft.title, content = draft.content))
    }

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
data class NotesUiState(
    val notes: List<Note> = emptyList(),
    val loading: Boolean = true,
    val error: String? = null
)

data class NoteFormState(
    val visible: Boolean = false,
    val title: String = "",
    val content: String = "",
    val busy: Boolean = false,
    val error: String? = null
)

class NotesViewModel(private val repository: NoteRepository) : ViewModel() {

    val notes: StateFlow<NotesUiState> = repository.observeNotes()
        .map { NotesUiState(notes = it, loading = false) }
        .catch { cause ->
            if (cause is CancellationException) throw cause
            Log.e("QuickNotes", "Read failed", cause)
            emit(NotesUiState(loading = false, error = "读取失败，请重启应用后重试"))
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = NotesUiState()
        )

    private val _form = MutableStateFlow(NoteFormState())
    val form: StateFlow<NoteFormState> = _form.asStateFlow()

    fun openForm() { if (!_form.value.busy) _form.value = NoteFormState(visible = true) }
    fun dismissForm() { if (!_form.value.busy) _form.value = NoteFormState() }
    fun editTitle(value: String) {
        if (!_form.value.busy) _form.value = _form.value.copy(title = value, error = null)
    }
    fun editContent(value: String) {
        if (!_form.value.busy) _form.value = _form.value.copy(content = value, error = null)
    }

    fun addNote() {
        val draft = _form.value
        if (draft.busy) return
        try {
            validateNote(draft.title, draft.content)
        } catch (invalid: IllegalArgumentException) {
            _form.value = draft.copy(error = invalid.message)
            return
        }
        _form.value = draft.copy(busy = true, error = null)
        viewModelScope.launch {
            try {
                repository.addNote(draft.title, draft.content)
                _form.value = NoteFormState() // 只有写入返回成功才清空并关闭
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (cause: Exception) {
                Log.e("QuickNotes", "Insert failed", cause)
                _form.value = draft.copy(error = "保存失败，输入已保留，请重试")
            }
        }
    }

    fun deleteNote(note: Note) {
        if (_form.value.busy) return
        _form.value = _form.value.copy(busy = true, error = null)
        viewModelScope.launch {
            try {
                repository.deleteNote(note)
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (cause: Exception) {
                Log.e("QuickNotes", "Delete failed", cause)
                _form.value = _form.value.copy(error = "删除失败，数据库中的记录未确认删除")
            } finally {
                _form.value = _form.value.copy(busy = false)
            }
        }
    }
}
```

表单也由 ViewModel 持有，因此旋转屏幕后能重新收集同一个草稿与保存状态。它不保证进程被系统杀死后恢复未保存的草稿；需要该能力再引入 `SavedStateHandle`。所有 UI 方法从主线程调用，先同步设置 `busy`，再发起写入，避免快速双击发出两个保存请求。失败显示具体操作，取消继续向上传播。生产日志应使用统一脱敏策略，本例不打印标题或内容。

---

## 🖼️ 第四步：Compose 界面

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotesScreen(viewModel: NotesViewModel) {
    val state by viewModel.notes.collectAsStateWithLifecycle()
    val form by viewModel.form.collectAsStateWithLifecycle()

    Scaffold(
        topBar = { TopAppBar(title = { Text("QuickNotes") }) },
        floatingActionButton = {
            FloatingActionButton(onClick = viewModel::openForm) {
                Text("新增")
            }
        }
    ) { padding ->
        if (state.loading || state.error != null || state.notes.isEmpty()) {
            Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                Text(state.error ?: if (state.loading) "正在读取" else "还没有笔记，点新增创建一条")
            }
        } else {
            LazyColumn(
                modifier = Modifier.padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (!form.visible && form.error != null) {
                    item { Text(form.error.orEmpty(), color = MaterialTheme.colorScheme.error) }
                }
                items(state.notes, key = { it.id }) { note ->
                    NoteCard(note = note, enabled = !form.busy,
                        onDelete = { viewModel.deleteNote(note) })
                }
            }
        }
    }

    if (form.visible) {
        AddNoteDialog(
            form = form,
            onTitle = viewModel::editTitle,
            onContent = viewModel::editContent,
            onConfirm = viewModel::addNote,
            onDismiss = viewModel::dismissForm
        )
    }
}

@Composable
fun NoteCard(note: Note, enabled: Boolean, onDelete: () -> Unit) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp)) {
            Text(note.title, style = MaterialTheme.typography.titleMedium)
            Spacer(Modifier.height(4.dp))
            Text(note.content, style = MaterialTheme.typography.bodyMedium, maxLines = 3)
            TextButton(onClick = onDelete, enabled = enabled, modifier = Modifier.align(Alignment.End)) {
                Text("删除")
            }
        }
    }
}

@Composable
fun AddNoteDialog(
    form: NoteFormState,
    onTitle: (String) -> Unit,
    onContent: (String) -> Unit,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("新建笔记") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = form.title, onValueChange = onTitle,
                    enabled = !form.busy, label = { Text("标题") })
                OutlinedTextField(value = form.content, onValueChange = onContent,
                    enabled = !form.busy, label = { Text("内容") })
                form.error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
            }
        },
        confirmButton = {
            TextButton(onClick = onConfirm, enabled = !form.busy && form.title.isNotBlank()) {
                Text(if (form.busy) "保存中" else "保存")
            }
        },
        dismissButton = { TextButton(onClick = onDismiss, enabled = !form.busy) { Text("取消") } }
    )
}
```

---

## ✅ 运行验证

### 先把入口和 import 接齐

上述数据层、Repository、ViewModel、界面 Kotlin 块可放入同一个 `MainActivity.kt`，使用项目原有 `package`。文件顶部需要以下 import；保留模板 Activity 的 manifest 注册。Gradle 还必须声明 `androidx.lifecycle:lifecycle-runtime-compose`、`lifecycle-viewmodel-compose`、`lifecycle-viewmodel-ktx`，三者使用工程已有的同一个 Lifecycle 版本；Compose Material 3、UI、Foundation 使用工程已有 Compose BOM，不能凭 import 自动得到依赖。

```kotlin
import android.content.Context
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.room.*
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private val factory by lazy {
        val repository = NoteRepository.from(applicationContext)
        viewModelFactory { initializer { NotesViewModel(repository) } }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                val model: NotesViewModel = viewModel(factory = factory)
                NotesScreen(model)
            }
        }
    }
}
```

`stateIn` 的初始空列表并不证明数据库里没有数据，因此我们用 `loading` 区分“尚未读完”与“查询确实为空”。读取错误也不能显示为“还没有笔记”。本教学版读取失败显示重启提示，后续练习再实现显式重试；Room 表变化可能触发重新查询，而非保证只对本次结果变化发射，见[异步查询说明](https://developer.android.com/training/data-storage/room/async-queries)。版本与 minSdk 条件见 [Room 发行说明](https://developer.android.com/jetpack/androidx/releases/room)。

### 设备验收（尚无通过记录）

1. `Run ▶️` 部署到模拟器，看到空态提示
2. 点 FAB → 输入标题内容 → 保存 → 列表立即出现新笔记（无需手动刷新，Room Flow 自动驱动）
3. 点"删除"→ 条目消失
4. 新增 A、B，删除 B，杀掉应用重新打开 → A 仍在、B 不在；这同时检查新增与删除持久化
5. 保存期间快速双击 → 只有一条记录；旋转屏幕后草稿/忙碌状态仍存在
6. 输入空白标题或超过限制的内容 → 明确提示、对话框保留、数据库不变
7. 注入会抛出存储异常的 Repository/DAO 测试替身 → 保存错误可见，输入不丢失，取消异常不被吞掉

先执行 `./gradlew :app:assembleDebug`，再在模拟器/设备执行上表。当前环境没有 Android SDK 构建与设备结果，纯 JVM 输入规则通过不能替代 Room KSP 生成、Lifecycle 收集或 UI 验证。

### 不依赖设备的领域规则验收

把上文的 `NoteDraft` 与 `validateNote` 原样复制到 `Rules.kt`，再添加下列入口：

```kotlin
fun main() {
    check(validateNote("  hello  ", " body ") == NoteDraft("hello", " body "))
    check(validateNote("a".repeat(120), "b".repeat(10_000)).title.length == 120)
    for ((title, body) in listOf("  " to "ok", "a".repeat(121) to "", "ok" to "b".repeat(10_001))) {
        check(runCatching { validateNote(title, body) }.exceptionOrNull() is IllegalArgumentException)
    }
    println("Kotlin note rules passed")
}
```

运行 `kotlinc Rules.kt -include-runtime -d rules.jar`、`java -jar rules.jar`。验证器直接抽取正文领域声明和此入口，不补写假 Room API；证据见[基础与项目核心逻辑报告](../../shared-resources/tools/document-quality/reports/kotlin-swift-core-validation.md)。

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
- 📄 **[KSP 代码生成配置指南](../reference/library-guides/03-ksp-configuration.md)** - ksp 插件声明、ksp(...) 依赖写法与常见配置错误
- 📄 **[协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md)** - stateIn/WhileSubscribed 原理
- 📄 **[Material 3 主题系统](../reference/framework-essentials/02-compose-material3.md)** - 给应用换上自定义主题
- 📖 **[Room 官方指南](https://developer.android.com/training/data-storage/room)** - 完整 Room 文档


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
