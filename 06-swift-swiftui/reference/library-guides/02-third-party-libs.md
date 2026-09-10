# 常用第三方库速查

> **文档简介**: Swift 生态主流三方库的选型表与用法示例：网络、图片、UI 工具、代码质量与依赖管理（SPM 为主）
>
> **目标读者**: 准备为项目引入三方库、需要对比选型的学习者
>
> **前置知识**: [01-foundation-and-stdlib.md](./01-foundation-and-stdlib.md)（Foundation 基础类型）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#三方库` `#SPM` `#Alamofire` `#Kingfisher` `#SwiftLint` |
| **更新日期** | `2026年9月` |

---

## 0. 依赖管理：Swift Package Manager

**定义**: Apple 官方包管理器，Xcode 内建支持，iOS 生态事实标准（CocoaPods 已进入维护期）。

```bash
# 命令行（Xcode 项目内也推荐先用 SPM CLI 验证）
swift package init --type executable
swift package add-dependency  # 实际编辑 Package.swift
swift package resolve
swift build && swift test
```

Xcode 中添加：**File > Add Package Dependencies…** → 粘贴仓库 URL → 选版本规则（推荐 **Up to Next Major**）。

---

## 1. 网络

### 1.1 Alamofire

**定位**: 语法糖化的 URLSession。链式请求、上传下载、拦截器、重试。

```swift
import Alamofire

AF.request("https://api.example.com/users/1")
    .validate()
    .responseDecodable(of: User.self) { response in
        switch response.result {
        case .success(let user): print(user.name)
        case .failure(let e): print(e)
        }
    }
```

### 1.2 什么时候不需要它

现代项目多数场景直接用 URLSession async API（见 [basics/07-concurrency-async-await.md](../../basics/07-concurrency-async-await.md)），只有需要复杂上传进度、证书校验、重试策略时再引入 Alamofire。

---

## 2. 图片加载

### 2.1 Kingfisher

**定位**: 网络图片下载 + 磁盘/内存缓存 + 占位与过渡动画。

```swift
import Kingfisher

KFImage(url)
    .placeholder { ProgressView() }
    .fade(duration: 0.25)
    .resizable()
    .aspectRatio(contentMode: .fill)
    .frame(width: 80, height: 80)
    .clipShape(Circle())
```

### 2.2 对比

| 库 | SwiftUI 支持 | 特点 |
|----|--------------|------|
| Kingfisher | ✅ KFImage | 老牌、功能全、社区大 |
| Nuke | ✅ LazyImage | 性能极致、API 更现代 |
| AsyncImage（系统） | ✅ 内建 | 无缓存；小项目够用 |

> 💡 选型顺序：先试系统 `AsyncImage`；需要缓存与复杂加载态再上 Kingfisher/Nuke。

---

## 3. UI 与工具

### 3.1 SwiftUI 补强

| 库 | 用途 |
|----|------|
| [SwiftUI Charts](https://developer.apple.com/documentation/charts)（系统） | 声明式图表 |
| [SnapshotTesting](https://github.com/pointfreeco/swift-snapshot-testing) | 截图测试视图 |
| [Lottie iOS](https://github.com/airbnb/lottie-ios) | AE 动画播放 |

### 3.2 工具库

**SwiftGen** 构建期生成类型安全的资源访问代码（`Color(asset: .accentPrimary)` 替代字符串）；**KeychainAccess** 封装 Keychain 读写样板代码。

| 库 | 替代的手写代码 |
|----|----------------|
| [KeychainAccess](https://github.com/kishikawakatsumi/KeychainAccess) | Security 框架样板 |
| [swift-composable-architecture](https://github.com/pointfreeco/swift-composable-architecture) | 完整状态管理架构（TCA） |
| [Cache](https://github.com/hyperoslo/Cache) | 通用混合缓存 |
| [DGCharts](https://github.com/danielgindi/Charts) | 复杂图表（UIKit 系） |

---

## 4. 代码质量

### 4.1 SwiftLint

**定位**: 风格与静态检查，500+ 规则。

```bash
brew install swiftlint
```

```yaml
# .swiftlint.yml 示例
disabled_rules:
  - trailing_whitespace
opt_in_rules:
  - empty_count
  - closure_spacing
line_length:
  warning: 120
  error: 200
excluded:
  - .build
  - DerivedData
```

```bash
swiftlint                    # 全量检查
swiftlint --fix              # 自动修复
```

Xcode 集成：Build Phases > New Run Script > `if command -v swiftlint >/dev/null; then swiftlint; fi`

### 4.2 SwiftFormat

```bash
brew install swiftformat
swiftformat . --swiftversion 6.0
```

与 SwiftLint 分工：**SwiftFormat 管格式**（缩进、换行、排序），**SwiftLint 管规则**（复杂度、强制约束）。

---

## 5. 选型原则

| 场景 | 建议 |
|------|------|
| 系统已有等价 API | 优先系统（AsyncImage、Charts、UserDefaults） |
| 单一职责小库 | 优于大而全框架 |
| 长期不维护 + 简单功能 | 复制源码优于依赖（SPM vendor） |
| 敏感合规（隐私清单） | 检查库是否提供 PrivacyInfo.xcprivacy |

**评估清单**：最近提交时间、Swift 6 兼容声明、issue 响应速度、License（MIT/Apache 优先）。

## ⚠️ 高频陷阱速查

- **版本规则选 Exact**：失去安全修复；Up to Next Major 平衡稳定性与更新
- **混用 CocoaPods 与 SPM**：同一依赖两条路径解析，冲突难排查；新项目统一 SPM
- **库内强缓存 URLProtocol**：调试时"改了 API 没反应"，先清 Kingfisher 缓存 `KingfisherManager.shared.cache.clearMemoryCache()`

## 相关文档

- 📄 [01-foundation-and-stdlib.md](./01-foundation-and-stdlib.md) — 系统网络与基础类型
- 📄 [01-swiftui-essentials.md](../framework-essentials/01-swiftui-essentials.md) — 原生 UI 速查
- 📄 [02-troubleshooting.md](../quick-references/02-troubleshooting.md) — 依赖冲突排查
