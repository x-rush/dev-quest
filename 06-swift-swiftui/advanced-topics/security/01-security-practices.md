# iOS 安全实践深度解析 — Keychain、传输安全与隐私合规

> **文档简介**: 系统梳理 iOS 客户端安全：敏感数据的 Keychain 存储、ATS 传输安全、权限最小化、日志脱敏，以及它们与 App Store 审核的对应关系
>
> **目标读者**: 已完成生产级应用改造、要建立安全基线的中高级学习者
>
> **前置知识**: [frameworks/03-ecosystem-integration.md](../../frameworks/03-ecosystem-integration.md)（网络与持久化链路）、[library-guides/01-foundation-and-stdlib.md](../../reference/library-guides/01-foundation-and-stdlib.md)（Foundation 数据类型）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `06-swift-swiftui` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#Keychain` `#ATS` `#隐私合规` `#安全基线` `#数据保护` |
| **更新日期** | `2026年9月` |

## 🔍 一、威胁模型：先明确防什么

个人级 iOS 应用的现实威胁按优先级排序：

1. **数据落库泄露**：UserDefaults 明文存 token，备份/越狱后直接可读
2. **传输被窃听**：ATS 例外配置放开了明文 HTTP
3. **日志泄密**：Release 构建打印 token、定位到控制台
4. **权限滥用**：索要了用不到的权限，审核与用户双重不信任

安全设计不是"加密一切"，而是**按数据密级匹配存储与传输手段**：

| 数据密级 | 例子 | 存储位置 |
|----------|------|---------|
| 凭证类 | token、密码、刷新令牌 | Keychain |
| 用户内容 | 笔记、打卡记录 | SwiftData（文件级保护由系统提供） |
| 偏好设置 | 主题、排序方式 | UserDefaults / @AppStorage |
| 缓存 | 天气快照、图片 | 沙盒 Cache 目录（系统可清除） |

## 🔍 二、Keychain：凭证的唯一正确归宿

### 2.1 最小可用的 Keychain 封装

```swift
import Security
import Foundation

enum KeychainError: Error { case unhandled(OSStatus) }

struct KeychainStore {
    let service: String                      // App 命名空间，如 "com.yourname.habittracker"

    func save(_ data: Data, account: String) throws {
        // 先删后加：幂等写入
        try? delete(account: account)

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: data,
            // 关键属性：解锁后 + 本设备才可访问（不随备份到其他设备）
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
        ]
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw KeychainError.unhandled(status) }
    }

    func read(account: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        return status == errSecSuccess ? result as? Data : nil
    }

    func delete(account: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.unhandled(status)
        }
    }
}

// 用法：token 只进 Keychain，绝不进 UserDefaults
let store = KeychainStore(service: "com.yourname.habittracker")
try store.save(Data("synthetic-token-value".utf8), account: "accessToken")
```

### 2.2 为什么 UserDefaults 不行

`UserDefaults` 是明文 plist，**iTunes 备份、文件共享、越狱设备**三种途径都能直接读出。判断口诀：这个数据泄露后能否被冒用？能 → Keychain。

### 2.3 SwiftUI 侧的会话状态

```swift
@MainActor
@Observable
final class SessionModel {
    private let keychain = KeychainStore(service: "com.yourname.habittracker")

    private(set) var isAuthenticated = false

    func restoreSession() {
        isAuthenticated = keychain.read(account: "accessToken") != nil
    }

    func signOut() throws {
        try keychain.delete(account: "accessToken")   // 退出必须清凭证
        isAuthenticated = false
    }
}
```

## 🔍 三、传输安全：ATS 的正确姿势

**App Transport Security 默认强制 HTTPS（TLS 1.2+）**。正确顺序是：

1. 所有 API 域名上 HTTPS（现代服务默认满足，零配置）
2. **禁止**为图省事全局关闭 ATS（`NSAllowsArbitraryLoads`）——审核会要求理由，且是安全倒退
3. 个别老系统确需例外时，**按域名精细化声明**：

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>legacy.example.com</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key> <true/>
            <key>NSIncludesSubdomains</key> <true/>
        </dict>
    </dict>
</dict>
```

**证书锁定（可选进阶）**：金融/账号类 App 在 `URLSessionDelegate` 中校验服务器证书公钥，防中间人；普通内容类 App 依赖系统信任链即可。

## 🔍 四、隐私合规：权限与数据声明的技术实现

### 4.1 权限最小化三原则

- **触发时申请**：进入定位页才申请定位，启动时连环弹窗是审核 5.1.1 高频拒因
- **声明即使用**：`Info.plist` 的用途文案（`NSLocationWhenInUseUsageDescription` 等）必须与真实行为一致
- **可降级运行**：拒绝权限后功能给出替代路径（手动输入城市替代自动定位），而不是死等

```swift
// 降级示例：拒绝定位 → 提供手动城市输入入口
switch manager.authorizationStatus {
case .authorizedWhenInUse, .authorizedAlways:
    manager.requestLocation()
case .denied, .restricted:
    ManualCityPicker()          // 降级 UI，而非空白报错
case .notDetermined:
    PermissionPrompt()
@unknown default:
    EmptyView()
}
```

### 4.2 数据声明与代码行为对账

App Store Connect 的"隐私营养标签"逐项核对清单：

- [ ] 第三方 SDK（如 Crashlytics）收集了什么？在标签中如实勾选
- [ ] `URLSession` 请求体里带了哪些用户数据？设备标识符算"标识符"类
- [ ] 分析数据是否与身份关联？关联与否对应标签中"用于追踪"的差别

### 4.3 日志脱敏

```swift
import os

private let logger = Logger(subsystem: "com.yourname.habittracker", category: "network")

// os.Logger 输出：静态字符串明文可见，动态参数默认仅限本机调试可见
logger.info("请求完成, 状态: \(statusCode)")            // ✅ 状态码可打印
logger.info("token: \(token, privacy: .private)")      // ✅ 显式标记私密
// ❌ print("token=\(token)")——Release 可能残留且明文
```

## ✅ 安全基线检查清单

- [ ] 全仓搜索 `UserDefaults.set`，确认没有 token/密码级数据
- [ ] 全仓搜索 `print(`，Release 路径无敏感输出（统一走 os.Logger）
- [ ] `NSAllowsArbitraryLoads` 不存在或仅在 Debug Scheme
- [ ] 退出登录清理 Keychain 与本地缓存
- [ ] 隐私标签与代码实际行为一致（逐项对账）

## ❌ 常见误区

- ❌ "客户端加密 = 安全"——密钥在客户端必然可提取，客户端加密只提高成本不改变模型
- ❌ Keychain 数据 iCloud 同步一定更好——`kSecAttrSynchronizable` 会离开设备，凭证类慎用
- ❌ 权限申请越早越好——启动时批量弹权限既伤转化又触发审核关注

## 🎯 实践检验

- [ ] 把天气/笔记 Demo 中的假想 token 从 UserDefaults 迁移到 Keychain，验证卸载重装后 Keychain 数据仍在（系统行为）
- [ ] 用 `nscurl --ats-diagnostics https://你的API域名` 验证 ATS 全通过
- [ ] 做一次"权限对账表"：App 申请的每个权限 × 使用场景 × Info.plist 文案 × 降级方案

## 相关文档

- 📄 [04-production-ios-app.md](../../projects/04-production-ios-app.md) — 安全基线并入生产化清单
- 📄 [02-app-store-release.md](../../deployment/02-app-store-release.md) — 隐私标签与审核条款示
- 📄 [03-ecosystem-integration.md](../../frameworks/03-ecosystem-integration.md) — 被保护的数据链路本身
- 📄 [01-foundation-and-stdlib.md](../../reference/library-guides/01-foundation-and-stdlib.md) — Data/URL 等基础类型速查
