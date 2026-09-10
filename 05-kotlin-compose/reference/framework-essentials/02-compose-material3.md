# Material 3 主题系统速查

> MaterialTheme 三要素（colorScheme/typography/shapes）、动态取色与暗色主题的字典式速查：定义 → 语法 → 示例 → 陷阱

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#Material3` `#主题` `#colorScheme` `#Typography` `#暗色模式` |
| **更新日期** | `2026年9月` |

---

## 1. MaterialTheme - 主题入口

### 定义
Material 3 的主题组合函数，向下提供 `colorScheme`/`typography`/`shapes` 三个读取入口（通过 CompositionLocal）。

### 语法和示例
```kotlin
@Composable
fun QuickNotesTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Dynamic color 在 Android 12+ 可用
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S ->
            if (darkTheme) dynamicDarkColorScheme(LocalContext.current)
            else dynamicLightColorScheme(LocalContext.current)
        darkTheme -> DarkColors
        else -> LightColors
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        shapes = AppShapes,
        content = content
    )
}

// 使用
val primary = MaterialTheme.colorScheme.primary
val titleStyle = MaterialTheme.typography.titleLarge
```

### 陷阱
预览/测试中不会自动套用主题——Preview 函数要手动包一层 `AppTheme { }`。

## 2. ColorScheme - 颜色角色

### 定义
M3 不再是"几个颜色"，而是**语义角色**系统：每种颜色成对出现（前景 onXxx + 背景 xxx），保证对比度可计算。

### 角色全表

| 角色 | 用途 | 配对前景 |
|------|------|----------|
| `primary` | 品牌主色：主按钮、强调 | `onPrimary` |
| `onPrimary` | 叠在 primary 上的内容色 | — |
| `primaryContainer` | 主色浅底（选中态、徽标底） | `onPrimaryContainer` |
| `secondary` | 次强调（次要按钮、筛选片） | `onSecondary` |
| `secondaryContainer` | 次强调浅底 | `onSecondaryContainer` |
| `tertiary` | 第三强调（对比性点缀） | `onTertiary` |
| `surface` | 卡片、面板底色 | `onSurface` |
| `surfaceVariant` | 次级面板（列表项底、输入框底） | `onSurfaceVariant` |
| `background` | 页面底色 | `onBackground` |
| `error` | 错误态 | `onError` |
| `outline` | 描边、分隔 | — |

### 语法和示例
```kotlin
private val LightColors = lightColorScheme(
    primary = Color(0xFF1565C0),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFD3E4FF),
    onPrimaryContainer = Color(0xFF001B3F),
    secondary = Color(0xFF565F71),
    background = Color(0xFFF8F9FF),
    surface = Color(0xFFF8F9FF),
    error = Color(0xFFBA1A1A)
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFFA8C8FF),
    onPrimary = Color(0xFF00306B),
    background = Color(0xFF111318)
)
```

### 陷阱
- **禁止硬编码颜色** `Color(0xFF...)` 直接用于组件——暗色模式下立即翻车；一律 `MaterialTheme.colorScheme.xxx`
- 不要拿 `primary` 当大面积背景又用默认内容色，前景配对应始终成对（`primary` + `onPrimary`）

## 3. Typography - 排版刻度

### 定义
M3 定义 15 个文字样式（5 组 × 3 号），以"角色"引用而非具体字号。

| 组 | Large | Medium | Small | 典型用途 |
|----|-------|--------|-------|----------|
| `display` | 57sp | 45 | 36 | 超大数字/庆祝页 |
| `headline` | 32sp | 28 | 24 | 大标题 |
| `title` | 22sp | 16 | 14 | 卡片标题、AppBar |
| `body` | 16sp | 14 | 12 | 正文 |
| `label` | 14sp | 12 | 11 | 按钮、标签、辅助文字 |

### 语法和示例
```kotlin
val Typography = Typography(
    titleLarge = TextStyle(
        fontWeight = FontWeight.SemiBold,
        fontSize = 22.sp,
        lineHeight = 28.sp
    ),
    bodyMedium = TextStyle(
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.25.sp
    )
)

Text("标题", style = MaterialTheme.typography.titleLarge)
Text("正文", style = MaterialTheme.typography.bodyMedium)
```

### 陷阱
`fontSize` 硬编码会绕开排版刻度；局部微调请基于主题样式复制修改：`style = MaterialTheme.typography.bodyMedium.copy(color = Color.Gray)`。

## 4. Shapes - 形状刻度

### 定义
五档圆角刻度，组件按"体量"取用。

| 档位 | 默认圆角 | 典型组件 |
|------|----------|----------|
| `extraSmall` | 4dp | Chip、SnackBar |
| `small` | 8dp | TextField |
| `medium` | 12dp | Card |
| `large` | 16dp | FAB、Dialog |
| `extraLarge` | 28dp | BottomSheet |

```kotlin
val AppShapes = Shapes(
    small = RoundedCornerShape(8.dp),
    medium = RoundedCornerShape(12.dp),
    large = RoundedCornerShape(16.dp)
)

Surface(shape = MaterialTheme.shapes.medium) { /* ... */ }
```

## 5. 动态取色（Dynamic Color）

### 定义
Android 12+ 从用户壁纸提取调色板，自动生成 ColorScheme，是 M3 的标志性能力。

### 语法和示例
```kotlin
val colorScheme = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
} else {
    if (darkTheme) DarkColors else LightColors          // 低版本回退自定义品牌色
}
```

### 陷阱
- 动态色下你的品牌色会被覆盖——品牌感强的产品应提供关闭开关（`dynamicColor: Boolean = false`）
- 动态色只覆盖 colorScheme，字体与形状仍由你定义

## 6. 暗色主题要点

### 最佳实践
- ✅ 跟随系统：`isSystemInDarkTheme()` 作为默认，让用户系统设置生效
- ✅ 所有组件颜色取自 colorScheme，暗色模式零额外代码
- ✅ 暗色下用"降饱和的亮色变体"做 primary，避免刺眼（如 `0xFF1565C0` → `0xFFA8C8FF`）
- ❌ 不要在暗色模式叠纯黑 `Color.Black` 背景 + 纯白文字（对比过强）；M3 暗色 surface 是深灰蓝（约 `0xFF111318`）

### 状态栏/系统栏
```kotlin
// 使用 enableEdgeToEdge()（androidx.activity）后，系统栏自动跟随主题
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()                              // 放在 super.onCreate 之前
        super.onCreate(savedInstanceState)
        setContent { QuickNotesTheme { App() } }
    }
}
```

---

## 快速选型

| 需求 | 做法 |
|------|------|
| 自定义品牌主题 | `lightColorScheme`/`darkColorScheme` + `MaterialTheme` |
| 支持壁纸取色 | `dynamicLight/DarkColorScheme` + API 31 判断 |
| 局部覆盖主题 | 嵌套 `MaterialTheme(colorScheme = ...)`（如登录页换肤） |
| 读当前主题色 | `MaterialTheme.colorScheme.primary` |
| 判断暗色模式 | `isSystemInDarkTheme()` |

---

## 相关文档

- 📄 **[Compose 核心组件速查](./01-compose-essentials.md)** - 组件如何消费主题角色
- 📄 **[第一个项目：笔记应用](../../basics/08-first-project.md)** - 给实战项目套自定义主题
- 📖 **[Material 3 官方主题文档](https://developer.android.com/develop/ui/compose/designsystems/material3)** - 权威指南
- 📖 **[Material Theme Builder](https://m3.material.io/theme-builder)** - 在线生成 colorScheme 代码
