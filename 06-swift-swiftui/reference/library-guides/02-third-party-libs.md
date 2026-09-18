# 常用第三方库速查

> **文档简介**: Swift 生态主流三方库的选型表与用法示例：网络、图片、UI 工具、代码质量与依赖管理（SPM 为主）
>
> **目标读者**: 准备为项目引入三方库、需要对比选型的学习者
>
> **前置知识**: [01-foundation-and-stdlib.md](./01-foundation-and-stdlib.md)（Foundation 基础类型）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#三方库` `#SPM` `#Alamofire` `#Kingfisher` `#SwiftLint` |
| **更新日期** | `2026年9月` |

</details>

---

## 0. 依赖管理：Swift Package Manager

**定义**: Apple 官方包管理器，Xcode 内建支持，iOS 生态事实标准（CocoaPods 已进入维护期）。

```bash
# 以下用于新建独立 Swift package；不要直接在已有 Xcode 应用根目录初始化
swift package init --type executable
# 编辑 Package.swift 的 dependencies 与 target dependencies 后解析
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
| Nuke | ✅ LazyImage | 提供图片加载管线与缓存控制，需按自己的场景测量 |
| AsyncImage（系统） | ✅ 内建 | 系统异步图片视图；不提供专用图片库同等的显式缓存管理接口 |

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

**定位**: 风格与静态规则检查；以所用版本的规则清单为准。

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
| 长期不维护 + 简单功能 | 评估替换或受控维护分支；复制源码仍需保留许可证并承担修复责任 |
| 敏感合规（隐私清单） | 检查库是否提供 PrivacyInfo.xcprivacy |

**评估清单**：最近提交时间、Swift 6 兼容声明、issue 响应速度、License（MIT/Apache 优先）。

## ⚠️ 高频陷阱速查

- **固定版本后不维护**：Exact 并非错误，但必须主动跟踪并验证修复；范围版本也要审查升级
- **混用 CocoaPods 与 SPM**：同一依赖两条路径解析，冲突难排查；新项目统一 SPM
- **图片仍显示旧内容**：区分内存、磁盘与 HTTP 缓存；只有内存缓存才由下面调用清除： `KingfisherManager.shared.cache.clearMemoryCache()`

## 相关文档

- 📄 [01-foundation-and-stdlib.md](./01-foundation-and-stdlib.md) — 系统网络与基础类型
- 📄 [01-swiftui-essentials.md](../framework-essentials/01-swiftui-essentials.md) — 原生 UI 速查
- 📄 [02-troubleshooting.md](../quick-references/02-troubleshooting.md) — 依赖冲突排查


<!-- full-library-explanation -->
## 用一个可撤回的小实验决定是否引库

先写下系统 API 缺少的能力。例如图片页需要可配置磁盘缓存、解码缩小和取消，分别用系统 AsyncImage 与候选库完成同一个滚动列表，再比较请求次数、峰值内存与实现复杂度。不要用“性能极致”“社区大”替代测试条件。

应用提交 Package.resolved 以记录解析结果；版本范围决定允许升级到哪里，锁文件决定本次实际使用什么。固定版本可以提高复现性，但需要主动审查更新；允许同一大版本更新也不保证每次没有行为变化。记录依赖版本、最低系统、许可证、迁移说明与替代路径。

练习：为图片加载建立自己的小 View 封装，仅让该文件依赖 Kingfisher；使用同样输入切换到系统实现。验收包括图片 404、无网、快速滚动、相同 URL 内容更新与退出账号清理，清内存缓存不能同时证明磁盘缓存和 HTTP 缓存都已清理。

选型核对入口：[Kingfisher](https://github.com/onevcat/Kingfisher)、[Nuke](https://github.com/kean/Nuke)、[Alamofire](https://github.com/Alamofire/Alamofire)、[SwiftLint](https://github.com/realm/SwiftLint)。本页不承诺固定规则数量或库永不过时；学习 HTTP、缓存、取消与测试边界能帮助替换工具。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
