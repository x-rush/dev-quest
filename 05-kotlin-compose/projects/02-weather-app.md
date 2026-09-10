# 进阶项目 - 天气应用（网络 + 定位）

> **文档简介**: 构建"定位 → 请求天气 API → 渲染"的天气应用，掌握网络栈、运行时权限与异步状态机的完整协作
>
> **目标读者**: 完成[入门项目](01-notes-app.md)、想掌握网络与系统能力集成的进阶学习者
>
> **前置知识**: [生态集成](../frameworks/03-ecosystem-integration.md)、[Compose 进阶](../frameworks/02-compose-advanced.md)、协程与 Flow 基础

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 操作指南（projects） |
| **难度** | ⭐⭐ |
| **标签** | `#retrofit` `#location` `#runtime-permission` `#sealed-state` |
| **更新日期** | `2026年9月` |

---

## 🎯 项目目标

- ✅ Retrofit 请求公开天气 API（本文用 Open-Meteo，无需 API Key）
- ✅ Google Play Services 定位（FusedLocationProviderClient）
- ✅ Compose 中优雅地请求**运行时权限**
- ✅ 用密封接口建模加载/成功/失败/无权限四态，杜绝非法状态组合

## 1️⃣ 网络层：API 与模型

```kotlin
// Open-Meteo 响应（节选），kotlinx-serialization 解析
@Serializable
data class WeatherResponse(
    val current: CurrentWeather,
) {
    @Serializable
    data class CurrentWeather(val temperature: Double, val windSpeed: Double)
}

interface WeatherApi {
    @GET("v1/forecast")
    suspend fun currentWeather(
        @Query("latitude") lat: Double,
        @Query("longitude") lon: Double,
        @Query("current") fields: String = "temperature,wind_speed",
    ): WeatherResponse
}
```

## 2️⃣ 定位：权限先行

```kotlin
@Composable
fun LocationGate(
    onLocationReady: (Double, Double) -> Unit,   // 事件向上
) {
    val context = LocalContext.current
    var granted by remember { mutableStateOf(false) }

    // 声明式请求权限：授权结果也是状态
    val launcher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted = it }

    LaunchedEffect(Unit) {
        val fine = Manifest.permission.ACCESS_FINE_LOCATION
        if (ContextCompat.checkSelfPermission(context, fine) == PackageManager.PERMISSION_GRANTED) {
            granted = true
        } else {
            launcher.launch(fine)
        }
    }

    when {
        granted -> FetchLocation(onLocationReady = onLocationReady)   // 有权限才进入定位
        else -> PermissionHint(onRequest = { launcher.launch(Manifest.permission.ACCESS_FINE_LOCATION) })
    }
}
```

```kotlin
// 定位实现：fused provider 只取一次位置
@SuppressLint("MissingPermission")   // 权限已由上游 UI 把关
suspend fun fetchLocation(
    client: FusedLocationProviderClient,
): Pair<Double, Double> = suspendCancellableCoroutine { cont ->
    client.getCurrentLocation(Priority.PRIORITY_BALANCED_POWER_ACCURACY, null)
        .addOnSuccessListener { loc ->
            if (loc != null) cont.resume(loc.latitude to loc.longitude)
            else cont.resumeWithException(IllegalStateException("定位失败"))
        }
        .addOnFailureListener { e -> cont.resumeWithException(e) }
}
```

## 3️⃣ ViewModel：密封状态机

```kotlin
sealed interface WeatherUiState {
    data object Loading : WeatherUiState
    data class Success(val temperature: Double, val windSpeed: Double) : WeatherUiState
    data class Error(val message: String) : WeatherUiState
    data object NoPermission : WeatherUiState
}

@HiltViewModel
class WeatherViewModel @Inject constructor(
    private val api: WeatherApi,
    private val locationClient: FusedLocationProviderClient,
) : ViewModel() {

    private val _uiState = MutableStateFlow<WeatherUiState>(WeatherUiState.Loading)
    val uiState = _uiState.asStateFlow()

    fun load() = viewModelScope.launch {
        _uiState.value = WeatherUiState.Loading
        runCatching {
            val (lat, lon) = fetchLocation(locationClient)
            api.currentWeather(lat = lat, lon = lon)
        }.fold(
            onSuccess = { r ->
                _uiState.value = WeatherUiState.Success(r.current.temperature, r.current.windSpeed)
            },
            onFailure = { e ->
                _uiState.value = WeatherUiState.Error(e.message ?: "未知错误")
            },
        )
    }

    fun onPermissionDenied() { _uiState.value = WeatherUiState.NoPermission }
}
```

> 为什么用密封接口而不是四个布尔位？——非法组合（同时 loading+error）在类型层面就不可能存在。

## 4️⃣ UI：按状态渲染

```kotlin
@Composable
fun WeatherScreen(viewModel: WeatherViewModel = hiltViewModel()) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    Column(Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        when (val s = state) {
            WeatherUiState.Loading -> CircularProgressIndicator()
            WeatherUiState.NoPermission -> {
                Text("需要定位权限才能获取天气")
                Button(onClick = { /* 引导到系统设置 */ }) { Text("去开启") }
            }
            is WeatherUiState.Error -> ErrorRetry(s.message, onRetry = viewModel::load)
            is WeatherUiState.Success -> {
                // 动画数字：状态变化自带过渡（动画详见 Compose 进阶）
                AnimatedContent(targetState = s.temperature, label = "temp") { t ->
                    Text("${t.toInt()}°C", style = MaterialTheme.typography.displayLarge)
                }
            }
        }
    }
}
```

## 5️⃣ 实施步骤

1. 配置 Retrofit + kotlinx-serialization（复用[生态集成](../frameworks/03-ecosystem-integration.md)骨架）
2. 用 MockWebServer 先跑通 API 解析，不依赖真网络（见[集成测试](../testing/03-integration-e2e-testing.md)）
3. 接入定位与权限流，验证拒绝授权路径
4. 实现 WeatherViewModel 四态机，配 [Turbine 单元测试](../testing/01-unit-testing.md)
5. 补 UI 与错误重试，真机验收断网/拒绝权限/成功三条路径

## 🎨 验收清单

- [ ] 拒绝权限 → 显示引导，不崩溃
- [ ] 断网 → Error 态可重试
- [ ] 旋转屏幕不重复请求（状态在 ViewModel）
- [ ] 权限相关字符串在 Manifest 声明齐全

## 🔗 相关文档

- 📖 概念字典：[协程与 Flow API 全表](../reference/language-concepts/03-coroutines-flow-api.md) ｜ [第三方库指南](../reference/library-guides/02-third-party-libs.md)
- 📖 前置教程：[页面导航](../basics/06-navigation.md) ｜ [协程与 Flow 基础](../basics/07-coroutines-flow-basics.md)
- 🚀 进阶项目：[新闻阅读器：分页 + 缓存](03-news-reader.md) ｜ 精通挑战：[生产级 Android 应用](04-production-android-app.md)
