# iOS 安全实践：凭证、请求与隐私边界

前置：URLSession、错误处理、应用生命周期。目标是让凭证与用户内容在存储、传输、日志和账号切换时都按明确规则处理。客户端的保护不能替代服务端认证与每次资源访问的授权检查。

## 数据应放在哪里

| 数据 | 建议位置 | 需要处理的边界 |
|---|---|---|
| 访问/刷新令牌等小型秘密 | Keychain | 访问条件、过期、退出清理、读取失败 |
| 用户正文 | 数据库或应用文件 | 文件保护、备份、账号隔离、删除 |
| 普通偏好 | UserDefaults | 不作为秘密存储或可靠业务数据库 |
| 可重新获取的图片 | 缓存目录 | 容量、失效、账号切换，系统可能清除 |

## Keychain 更新：先保留旧值，再处理写入结果

先删除再添加不是原子的替换：新添加失败会丢失旧凭证。下面的封装先更新，只有不存在时才添加；并发写仍应由应用会话服务统一协调。

```swift
import Foundation
import Security

enum CredentialError: Error { case status(OSStatus), invalidData }

struct CredentialStore {
    let service: String
    private func key(_ account: String) -> [String: Any] {
        [kSecClass as String: kSecClassGenericPassword,
         kSecAttrService as String: service,
         kSecAttrAccount as String: account]
    }

    func save(_ data: Data, account: String) throws {
        let changes: [String: Any] = [
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]
        var status = SecItemUpdate(key(account) as CFDictionary, changes as CFDictionary)
        if status == errSecItemNotFound {
            let attributes = key(account).merging(changes) { _, new in new }
            status = SecItemAdd(attributes as CFDictionary, nil)
        }
        guard status == errSecSuccess else { throw CredentialError.status(status) }
    }

    func read(account: String) throws -> Data? {
        var query = key(account)
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne
        var result: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        if status == errSecItemNotFound { return nil }
        guard status == errSecSuccess else { throw CredentialError.status(status) }
        guard let data = result as? Data else { throw CredentialError.invalidData }
        return data
    }

    func delete(account: String) throws {
        let status = SecItemDelete(key(account) as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw CredentialError.status(status)
        }
    }
}
```

访问条件必须匹配产品：WhenUnlockedThisDeviceOnly 限制锁定时访问和迁移到其他设备，不自动允许后台刷新。不存在返回 nil；其他系统错误抛出，不能把设备暂时不可访问误判成“用户已退出”。本轮没有 Apple SDK，代码未经本机编译运行。API 依据：[Apple 更新与删除 Keychain 项目](https://developer.apple.com/documentation/security/updating-and-deleting-keychain-items)。

## 凭证存在不代表会话有效

读取到 token 只能说明本地有候选凭证，仍需按协议验证有效期、刷新或请求服务端确认。退出时应取消或隔离旧请求、清理该账号的缓存和凭证；旧请求晚到不得把前一个账号的数据重新写回当前界面。不能把 Keychain 在某次卸载后的残留现象当作永久存储契约。

## 网络与日志

使用 HTTPS 与系统默认信任验证，不以“调试方便”为由全局放开 ATS 或接受任意证书。确需域名例外时记录用途与移除条件。证书锁定需要同时设计证书轮换和失效恢复，不能只粘贴一段 delegate 代码。

日志记录操作名、状态码、脱敏后的错误类别和关联标识，通常没有必要记录完整 token。Logger 的 privacy 标记影响显示与收集方式，不能代替数据最小化；普通 print 也可能进入发布日志。数据库参数、深链和返回 JSON 都要按使用位置校验，客户端隐藏按钮不构成权限控制。

## 权限与隐私声明

只在功能需要时解释并申请权限；定位被拒绝仍可手动选择城市。应用与第三方 SDK 的实际收集、关联、用途应分别核对。“与用户身份关联的数据”和“用于跨应用/网站追踪的数据”是不同维度，不能画等号。隐私清单也不能替代 App Store Connect 的披露。提交前核对 [Apple App 隐私说明](https://developer.apple.com/app-store/app-privacy-details/)，规则可能调整。

## 项目练习与验收

给天气应用加入测试会话：保存合成 token，覆盖写入后读到新值；删除两次都成功；读取不存在得到 nil。测试读取失败与过期凭证分别进入正确状态。账号 A 请求未完成时切换 B，再放行 A 的响应，B 页面不得出现 A 的城市或缓存。关闭定位权限后手选城市仍可完成查询。检索发布日志，确认没有 token、正文或精确定位。

继续阅读 [URLSession](../../reference/language-concepts/15-urlsession.md)、[并发边界](../performance/02-concurrency-optimization.md)、[生产项目](../../projects/04-production-ios-app.md)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
